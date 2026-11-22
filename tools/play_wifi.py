"""Play the ESP32's mic on the laptop speaker, over Wi-Fi.

The laptop must be on the same Wi-Fi as the ESP32 (mic-wifi.ino).
Run:   python play_wifi.py                      (tries nani.local)
       python play_wifi.py --host 192.168.1.42  (IP printed in the Arduino Serial Monitor)
       python play_wifi.py --save               (also saves a .wav in Wispr\\recordings)
Stop:  Ctrl+C
"""
import argparse
import socket
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

HEADER = bytes([0xA5, 0x5A, 0x4D, 0x43])
RATE = 16000
FRAME = 320
PACKET = len(HEADER) + FRAME * 2
PREBUFFER = int(RATE * 0.2) * 2          # 200 ms cushion against Wi-Fi hiccups (bytes)
OUT_DIR = Path(__file__).resolve().parent.parent / "recordings"


class Player:
    """Holds received audio and feeds the sound card at a steady rate."""

    def __init__(self, gain):
        self.gain = gain
        self.buf = bytearray()
        self.lock = threading.Lock()
        self.started = False
        self.underruns = 0

    def add(self, samples: np.ndarray):
        loud = np.clip(samples.astype(np.float32) * self.gain, -32768, 32767).astype("<i2")
        with self.lock:
            self.buf += loud.tobytes()
            if len(self.buf) > RATE * 2:          # more than 1 s behind: drop the oldest
                del self.buf[: len(self.buf) - PREBUFFER]

    def callback(self, outdata, frames, _time, _status):
        need = frames * 2
        with self.lock:
            if not self.started and len(self.buf) >= PREBUFFER:
                self.started = True
            if self.started and len(self.buf) >= need:
                outdata[:] = self.buf[:need]
                del self.buf[:need]
                return
            if self.started:
                self.underruns += 1
                self.started = False             # refill the cushion before playing again
        outdata[:] = b"\x00" * need


def parse(buf: bytearray):
    """Remove complete packets from buf, return their samples (or None)."""
    out = []
    while True:
        j = buf.find(HEADER)
        if j < 0:
            del buf[: max(0, len(buf) - 3)]
            break
        if j > 0:
            del buf[:j]
        if len(buf) < PACKET:
            break
        out.append(np.frombuffer(bytes(buf[4:PACKET]), dtype="<i2"))
        del buf[:PACKET]
    return np.concatenate(out) if out else None


def main():
    ap = argparse.ArgumentParser(description="Play the ESP32 mic over Wi-Fi")
    ap.add_argument("--host", default="nani.local", help="ESP32 IP or name (default nani.local)")
    ap.add_argument("--port", type=int, default=3333)
    ap.add_argument("--gain", type=float, default=1.0, help="volume boost (default 1)")
    ap.add_argument("--save", action="store_true", help="also save everything to a .wav file")
    ap.add_argument("--mute", action="store_true", help="don't play, just receive (and save)")
    ap.add_argument("--seconds", type=float, default=0, help="stop after this many seconds (0 = run until Ctrl+C)")
    args = ap.parse_args()

    player = Player(args.gain)
    saved = []
    stream = None
    if not args.mute:
        stream = sd.RawOutputStream(samplerate=RATE, channels=1, dtype="int16",
                                    blocksize=FRAME, callback=player.callback)
        stream.start()

    t_start = time.time()
    try:
        while True:
            print(f"Connecting to {args.host}:{args.port} ...")
            try:
                sock = socket.create_connection((args.host, args.port), timeout=5)
            except OSError as e:
                print(f"  can't connect ({e}). Is the ESP32 on, on the same Wi-Fi, and is the IP right? Retrying in 2 s")
                time.sleep(2)
                continue
            sock.settimeout(3)
            print("Connected. Speak into the mic. Ctrl+C to stop.")
            buf = bytearray()
            got, last = 0, time.time()
            try:
                while True:
                    data = sock.recv(4096)
                    if not data:
                        raise ConnectionError("ESP32 closed the connection")
                    buf += data
                    samples = parse(buf)
                    if samples is not None:
                        got += samples.size // FRAME
                        if not args.mute:
                            player.add(samples)
                        if args.save:
                            saved.append(samples)
                    if time.time() - last >= 1:
                        print(f"\r  {got:3d} packets/s (want 50)   dropouts so far: {player.underruns}   ",
                              end="", flush=True)
                        got, last = 0, time.time()
                    if args.seconds and time.time() - t_start >= args.seconds:
                        raise KeyboardInterrupt
            except (OSError, ConnectionError) as e:
                print(f"\n  connection lost ({e}), reconnecting...")
            finally:
                sock.close()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if stream:
            stream.stop()
            stream.close()
        if args.save and saved:
            x = np.concatenate(saved).astype(np.float32)
            x -= x.mean()
            if np.abs(x).max() > 0:
                x *= min(29000 / np.abs(x).max(), 20.0)
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            path = OUT_DIR / time.strftime("wifi_%Y%m%d_%H%M%S.wav")
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(RATE)
                w.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes())
            print(f"Saved {x.size / RATE:.1f} s to {path}")


if __name__ == "__main__":
    main()
