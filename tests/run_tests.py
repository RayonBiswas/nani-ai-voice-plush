"""Automated checks for the laptop side. No hardware and no live website needed:
the website and the toy are both faked on this laptop.

Run:  python tests/run_tests.py
Each test prints PASS/FAIL with the measured numbers; exit code 0 = all passed.
"""
import base64
import json
import queue
import socket
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "brain"))
import make_voice  # noqa: E402
import nani_brain as nb  # noqa: E402

RATE = 16000
results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def tone(hz, secs=1.0, amp=3000.0, rate=RATE):
    return (np.sin(2 * np.pi * hz * np.arange(int(rate * secs)) / rate) * amp)


def gain_db(hz):
    x = tone(hz, 2.0)
    y = make_voice.bass_cut(x)
    return 20 * np.log10(np.abs(y[RATE:]).max() / np.abs(x[RATE:]).max())


# 1. Speaker protection filter: cuts bass, keeps speech
def test_bass_cut():
    g200, g400, g1k, g3k = gain_db(200), gain_db(400), gain_db(1000), gain_db(3000)
    check("400 Hz bass cut", g200 < -10 and -4 < g400 < -2 and abs(g1k) < 0.5 and abs(g3k) < 0.5,
          f"200 Hz {g200:.1f} dB, 400 Hz {g400:.1f} dB, 1 kHz {g1k:.1f} dB, 3 kHz {g3k:.1f} dB")


# 2. Compressor: louder SPEECH at the same peak (tuned for speech; on beeping pure tones it
#    lowers loudness instead, see docs/10-known-issues-roadmap.md). Needs the Windows Zira voice.
def test_compress():
    import tempfile, wave
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "v.wav"
        make_voice.synthesize("Hello Aarav! I am Nani. Did you drink water today?", "Zira", -1, p)
        with wave.open(str(p)) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64)
    plain = np.clip(make_voice.bass_cut(a * 28000 / np.abs(a).max()), -32768, 32767)
    y = make_voice.compress(make_voice.bass_cut(a)) * 28000
    gain = make_voice.speech_rms_db(y) - make_voice.speech_rms_db(plain)
    check("compressor on real speech", np.abs(y).max() <= 28001 and gain > 5,
          f"peak {np.abs(y).max():.0f} (limit 28000), speech loudness +{gain:.1f} dB")


# 3. Toy link messages: tag + little-endian length + data
def test_protocol():
    a, b = socket.socketpair()
    nb.send_msg(a, b"ANS1", "Shabaash beta".encode())
    tag = nb.recv_exact(b, 4); n = struct.unpack("<I", nb.recv_exact(b, 4))[0]; data = nb.recv_exact(b, n)
    a.close(); b.close()
    check("link message framing", tag == b"ANS1" and data == b"Shabaash beta", f"{tag!r} {n} bytes {data!r}")


# 4. Website answer streamed sentence by sentence (fake website + fake toy)
def test_streaming():
    import subprocess, tempfile
    clips = []
    for hz in (500, 700, 900):                               # three "sentences" as mp3
        with tempfile.TemporaryDirectory() as d:
            w = Path(d) / "s.wav"
            import wave
            with wave.open(str(w), "wb") as f:
                f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
                f.writeframes(tone(hz, 1.0, 8000).astype("<i2").tobytes())
            clips.append(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(w), "-f", "mp3", "pipe:1"],
                                        capture_output=True, check=True).stdout)

    class FakeSite(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200); self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Transfer-Encoding", "chunked"); self.end_headers()

            def out(ev):
                b = (json.dumps(ev) + "\n").encode()
                self.wfile.write(b"%x\r\n" % len(b) + b + b"\r\n"); self.wfile.flush()
            time.sleep(0.5); out({"t": "heard", "text": "what colour is a banana"})
            for i, mp3 in enumerate(clips):
                time.sleep(1.0); out({"t": "say", "i": i, "text": f"sentence {i + 1}", "cues": [],
                                      "audio": base64.b64encode(mp3).decode()})
            out({"t": "done", "ms": 3500}); self.wfile.write(b"0\r\n\r\n"); self.wfile.flush()

        def log_message(self, *a):
            pass

    site = HTTPServer(("127.0.0.1", 0), FakeSite)
    threading.Thread(target=site.serve_forever, daemon=True).start()
    t0, arrivals = time.time(), []
    for ev in nb.site_turn_stream(f"http://127.0.0.1:{site.server_port}", "test", tone(300, 1.0).astype("<i2")):
        arrivals.append((ev[0], round(time.time() - t0, 1)))
    site.shutdown()
    says = [t for k, t in arrivals if k == "say"]
    heard = [t for k, t in arrivals if k == "heard"]
    sent = [1.5, 2.5, 3.5]
    lags = [round(r - s, 1) for r, s in zip(says, sent)]
    gaps = [round(b - a, 1) for a, b in zip(says, says[1:])]
    # Streaming, not batching: sentences arrive spread out ~1 s apart like they were sent, and the first one
    # arrives before the website even sends the last (3.5 s). An absolute time limit was flaky: a busy laptop
    # adds a constant 0.3-0.8 s at the start of the request (seen 2026-11-22), which is not batching.
    ok = len(says) == 3 and bool(heard) and says[0] < sent[-1] and all(g >= 0.6 for g in gaps)
    check("sentence-by-sentence streaming", ok,
          f"website sends heard 0.5 s, sentences {sent} s -> received heard {heard}, sentences {says} "
          f"(lag {lags} s, gaps {gaps} s)")


# 5. Finding the toy on the network
def test_find_toy():
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 0)); srv.listen(16); port = srv.getsockname()[1]

    def accept():
        while True:
            try:
                c, _ = srv.accept(); c.close()
            except OSError:
                return
    threading.Thread(target=accept, daemon=True).start()
    t0 = time.time(); ip = nb.find_toy(port); dt = time.time() - t0
    srv.close()
    check("find toy on Wi-Fi", ip is not None and dt < 10, f"found {ip} in {dt:.1f} s")


# 6. Website speech forwarded to the toy: SAY1, RPL1, END1 (and tiny clicks skipped)
def test_website_speech():
    q = queue.Queue()
    t = (0.5 * np.sin(2 * np.pi * 800 * np.arange(48000) / 48000)).astype("<f4")
    q.put({"sr": 48000, "data": base64.b64encode(t.tobytes()).decode()})
    q.put({"sr": 48000, "data": base64.b64encode(t[:1000].tobytes()).decode()})
    a, b = socket.socketpair()
    sent = nb.send_website_speech(a, q); a.close()
    data = b""
    while (d := b.recv(65536)):
        data += d
    tags, i = [], 0
    while i < len(data):
        n = struct.unpack("<I", data[i + 4:i + 8])[0]; tags.append((data[i:i + 4].decode(), n)); i += 8 + n
    ok = sent == 1 and [x[0] for x in tags] == ["SAY1", "RPL1", "END1"] and tags[1][1] == 32000
    check("website speech to toy", ok, f"messages {tags} (1.0 s at 48 kHz -> 32000 bytes at 16 kHz)")


if __name__ == "__main__":
    for test in (test_bass_cut, test_compress, test_protocol, test_streaming, test_find_toy, test_website_speech):
        try:
            test()
        except Exception as e:
            check(test.__name__, False, f"{type(e).__name__}: {e}")
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)
