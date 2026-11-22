"""Chapter 03: protecting a small speaker with a bass-cut (high-pass) filter.

Mini version of hpfSetup()/hpf() in firmware/nani-full/nani-full.ino and bass_cut() in
brain/make_voice.py: a 2nd-order "biquad" high-pass at 400 Hz (RBJ Audio EQ Cookbook).
Run:  python ch03_speaker_filter.py
"""
import math

import numpy as np

from ch01_sound import RATE, tone

CUTOFF_HZ = 400.0


def highpass_coefficients(cutoff=CUTOFF_HZ, rate=RATE, q=0.7071):
    """The 5 numbers that define the filter (same formula as the firmware)."""
    w0 = 2 * math.pi * cutoff / rate
    alpha = math.sin(w0) / (2 * q)
    c = math.cos(w0)
    a0 = 1 + alpha
    b0, b1, b2 = (1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0
    a1, a2 = -2 * c / a0, (1 - alpha) / a0
    return b0, b1, b2, a1, a2


def bass_cut(samples):
    """Run the filter sample by sample, exactly like the ESP32 does in hpf()."""
    b0, b1, b2, a1, a2 = highpass_coefficients()
    x1 = x2 = y1 = y2 = 0.0
    out = np.empty(len(samples))
    for i, x in enumerate(samples):
        y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y
        out[i] = y
    return out


def gain_db(hz):
    """How much the filter changes a note's loudness, in decibels (0 = unchanged)."""
    x = tone(hz, 1.0)
    y = bass_cut(x)
    half = len(x) // 2                       # skip the first half while the filter settles
    return 20 * math.log10(np.abs(y[half:]).max() / np.abs(x[half:]).max())


if __name__ == "__main__":
    for hz in (100, 200, 400, 1000, 3000):
        print(f"{hz:5d} Hz: {gain_db(hz):6.1f} dB")
