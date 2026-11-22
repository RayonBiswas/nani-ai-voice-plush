"""Draws the tutorial figures from the mini code. Run:  python figures.py  (writes ../img/*.png)

Style: one data series per chart in the reference palette's slot-1 blue, recessive grid and axes,
reference lines in secondary ink with direct labels (no legend needed for a single series).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ch01_sound import FRAME, RATE, fake_microphone, rms
from ch02_voice_detect import MIN_START_RMS, START_FACTOR, detect_speech
from ch03_speaker_filter import highpass_coefficients

IMG = Path(__file__).resolve().parent.parent / "img"
BLUE, INK, INK2, GRID, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def style(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=10)
    ax.set_xlabel(xlabel, color=INK2); ax.set_ylabel(ylabel, color=INK2)
    ax.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2)


def filter_figure():
    b0, b1, b2, a1, a2 = highpass_coefficients()
    f = np.logspace(np.log10(50), np.log10(7900), 400)
    z = np.exp(1j * 2 * np.pi * f / RATE)
    db = 20 * np.log10(np.abs((b0 + b1 / z + b2 / z ** 2) / (1 + a1 / z + a2 / z ** 2)))
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150, facecolor=SURFACE)
    ax.semilogx(f, db, color=BLUE, linewidth=2)
    ax.axvline(400, color=INK2, linewidth=1, linestyle="--")
    ax.annotate("400 Hz: −3 dB", xy=(400, -3), xytext=(430, -22), color=INK2, fontsize=9)
    ax.annotate("speech clarity lives here\n(1–4 kHz): untouched", xy=(2000, 0), xytext=(1150, -14),
                color=INK2, fontsize=9)
    ax.annotate("low notes the small\nspeaker can't play: cut", xy=(100, -24), xytext=(55, -9),
                color=INK2, fontsize=9)
    ax.set_ylim(-45, 5); ax.set_xticks([50, 100, 200, 400, 1000, 2000, 4000])
    ax.set_xticklabels(["50", "100", "200", "400", "1k", "2k", "4k"])
    style(ax, "Bass-cut filter: how loud each note comes out", "frequency (Hz)", "gain (dB)")
    fig.tight_layout(); fig.savefig(IMG / "filter-response.png"); plt.close(fig)


def vad_figure():
    mic = fake_microphone()
    levels = [rms(mic[i:i + FRAME]) for i in range(0, len(mic) - FRAME + 1, FRAME)]
    t = np.arange(len(levels)) * FRAME / RATE
    noise = np.mean(levels[:25])
    start_line = max(noise * START_FACTOR, MIN_START_RMS)
    s, e = detect_speech(mic)
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150, facecolor=SURFACE)
    ax.axvspan(s / RATE, e / RATE, color="#cde2fb", linewidth=0)
    ax.plot(t, levels, color=BLUE, linewidth=2)
    ax.axhline(start_line, color=INK2, linewidth=1, linestyle="--")
    ax.text(0.03, start_line + 60, f"start line = max(4 × room noise, 300) = {start_line:.0f}", color=INK2, fontsize=9)
    ax.text(s / RATE + 0.03, 3050, "recorded: 1.00–2.00 s", color=INK2, fontsize=9)
    ax.text(2.05, 900, "0.7 s of quiet\n→ stop", color=INK2, fontsize=9)
    ax.set_ylim(0, 3300)
    style(ax, "Voice detection: loudness of each 20 ms frame", "time (s)", "loudness (RMS)")
    fig.tight_layout(); fig.savefig(IMG / "voice-detection.png"); plt.close(fig)


if __name__ == "__main__":
    IMG.mkdir(exist_ok=True)
    filter_figure(); vad_figure()
    print("wrote", sorted(p.name for p in IMG.glob("*.png")))
