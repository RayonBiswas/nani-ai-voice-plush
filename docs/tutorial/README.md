# Build your own talking Nani: a from-zero tutorial

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners: basic programming, no electronics or audio background |
| **Last updated** | 2026-11-22 |

## What you'll build

A plush toy that listens to a child, sends what they said to an AI over Wi-Fi, and speaks the answer.
You first build a **mini Nani in plain Python** that runs on any laptop without hardware, so every idea
is clear and testable. Then each chapter shows how the **real** project does the same thing on an
ESP32-S3 with a mic and a speaker.

## Chapters

| # | Chapter | You build | Time |
|---|---|---|---|
| 0 | [The big picture](00-the-big-picture.md) | nothing yet: the story of the toy | 10 min |
| 1 | [Setup: sound is a list of numbers](01-setup.md) | `ch01_sound.py` | 20 min |
| 2 | [Hearing: when does the child speak?](02-hearing.md) | `ch02_voice_detect.py` + the mic | 45 min |
| 3 | [Speaking: a small speaker that doesn't crackle](03-speaking.md) | `ch03_speaker_filter.py` + the speaker | 45 min |
| 4 | [Talking over Wi-Fi](04-talking-over-wifi.md) | `ch04_link.py` | 30 min |
| 5 | [The bridge: fast answers](05-the-bridge.md) | `ch05_mini_brain.py` | 40 min |
| 6 | [Measure honestly](06-measure-honestly.md) | `test_mini.py` | 20 min |
| 7 | [From mini to full](07-from-mini-to-full.md) | the real project | 30 min+ |

## Prerequisites

- Python 3.10+ and `pip install numpy matplotlib` (matplotlib only for the figures).
- For the hardware parts: the parts in [03 — Hardware](../03-hardware.md) and the Arduino IDE.

## Conventions

- Code blocks are copied **verbatim** from [`code/`](code/). Run them from that folder:
  `cd docs/tutorial/code`.
- **✅ Check** blocks show the output recorded when this tutorial was written. Yours should match
  (timings may differ by a few hundredths of a second).
- 💡 = the idea in plain words · ⚠️ = a common mistake and its symptom.
