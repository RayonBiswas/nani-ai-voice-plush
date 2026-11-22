"""Chapter 05: the bridge. Forward each answer sentence to the toy the moment it arrives.

Mini version of site_turn_stream() + the main loop in brain/nani_brain.py and askBrain() in
nani-full.ino. The website is faked: it streams one JSON line per event, like /api/turn
(heard, then one "say" per sentence with base64 audio, then done). The real website sends MP3;
the fake sends raw 16-bit audio so this runs without ffmpeg.
Run:  python ch05_mini_brain.py
"""
import base64
import json
import socket
import threading
import time

import numpy as np

from ch01_sound import RATE, tone
from ch04_link import recv_msg, send_msg


def fake_website(sentences, gap=0.5):
    """Yields NDJSON lines with a delay, like the website thinking between sentences."""
    yield json.dumps({"t": "heard", "text": "what colour is a banana"})
    for i, text in enumerate(sentences):
        time.sleep(gap)
        audio = tone(500 + 100 * i, 0.3).astype("<i2").tobytes()
        yield json.dumps({"t": "say", "text": text, "audio": base64.b64encode(audio).decode()})
    yield json.dumps({"t": "done"})


def bridge(lines, to_toy):
    """Read the website stream line by line and pass every piece on straight away."""
    for line in lines:
        ev = json.loads(line)
        if ev["t"] == "heard":
            send_msg(to_toy, b"HRD1", ev["text"].encode())
        elif ev["t"] == "say":
            send_msg(to_toy, b"ANS1", ev["text"].encode())
            send_msg(to_toy, b"RPL1", base64.b64decode(ev["audio"]))
        elif ev["t"] == "done":
            break
    send_msg(to_toy, b"END1", b"")


def toy(from_bridge, log, t0):
    """The toy: print text, 'play' each audio piece as soon as it arrives, stop at END1."""
    while True:
        tag, data = recv_msg(from_bridge)
        at = time.time() - t0
        if tag in (b"HRD1", b"ANS1"):
            log.append(f"{at:4.1f} s  {tag.decode()}  {data.decode()}")
        elif tag == b"RPL1":
            n = len(np.frombuffer(data, "<i2"))
            log.append(f"{at:4.1f} s  RPL1  play {n / RATE:.1f} s of audio")
        elif tag == b"END1":
            log.append(f"{at:4.1f} s  END1  answer finished")
            return


if __name__ == "__main__":
    toy_end, bridge_end = socket.socketpair()
    log, t0 = [], time.time()
    player = threading.Thread(target=toy, args=(toy_end, log, t0))
    player.start()
    bridge(fake_website(["Banana is yellow, beta!", "Yellow like the sun.", "What else is yellow?"]),
           bridge_end)
    player.join()
    print("\n".join(log))
