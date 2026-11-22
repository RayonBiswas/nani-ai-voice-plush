"""Checks the mini Nani by independent routes. Run:  python test_mini.py"""
import cmath
import math
import socket
import struct
import threading
import time

from ch01_sound import RATE, fake_microphone
from ch02_voice_detect import detect_speech
from ch03_speaker_filter import gain_db, highpass_coefficients
from ch04_link import recv_msg
from ch05_mini_brain import bridge, fake_website, toy

ok_all = True


def check(name, ok, detail):
    global ok_all
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# Ch02: we KNOW the fake speech is 1.00 s to 2.00 s
s, e = detect_speech(fake_microphone())
check("voice detection", abs(s / RATE - 1.0) < 0.1 and abs(e / RATE - 2.0) < 0.15,
      f"found {s / RATE:.2f}-{e / RATE:.2f} s, truth 1.00-2.00 s")

# Ch03: the filter measured in time vs. the textbook formula |H(e^jw)|
b0, b1, b2, a1, a2 = highpass_coefficients()
for hz in (200, 1000):
    z = cmath.exp(1j * 2 * math.pi * hz / RATE)
    formula = 20 * math.log10(abs((b0 + b1 / z + b2 / z ** 2) / (1 + a1 / z + a2 / z ** 2)))
    measured = gain_db(hz)
    check(f"filter at {hz} Hz", abs(measured - formula) < 0.3, f"measured {measured:.1f} dB, formula {formula:.1f} dB")

# Ch04: a message that arrives in 3 separate pieces must still be read whole
a, b = socket.socketpair()
raw = b"ANS1" + struct.pack("<I", 13) + b"Shabaash beta"
threading.Thread(target=lambda: [a.sendall(raw[i:i + 7]) or time.sleep(0.05) for i in range(0, len(raw), 7)]).start()
tag, data = recv_msg(b)
check("link reads split messages", (tag, data) == (b"ANS1", b"Shabaash beta"), f"{tag!r} {data!r}")

# Ch05: the first sentence must be 'played' BEFORE the website sends the last one (no batching)
toy_end, bridge_end = socket.socketpair()
log, t0 = [], time.time()
player = threading.Thread(target=toy, args=(toy_end, log, t0)); player.start()
bridge(fake_website(["one", "two", "three"], gap=0.5), bridge_end); player.join()
first_play = float([l for l in log if "RPL1" in l][0].split()[0])
check("sentences stream, not batch", first_play < 1.0, f"first audio at {first_play:.1f} s, last sentence sent at 1.5 s")

print("ALL PASS" if ok_all else "SOME FAILED")
