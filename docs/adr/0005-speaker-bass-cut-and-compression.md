# ADR-0005: 400 Hz bass cut + speech compression + 1000 µF capacitor

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | `hpf()` in the firmware; `bass_cut()`, `compress()` in [make_voice.py](../../brain/make_voice.py) |

## Context
The speaker "hissed". Step-by-step tests showed it was overdrive of the 40 mm speaker, worst on low notes
(262 Hz crackled, 523 Hz clean), not noise in the file, power or wiring.

## Decision
- Every sound goes through a 2nd-order 400 Hz high-pass on the ESP32 (and the same filter on the laptop).
- Speech clips and answers are compressed (−26 dB threshold, 4:1, then the top 0.5 % of peaks softened),
  so they sound louder at the same peak.
- A 1000 µF capacitor across the amp's VIN/GND.
- Default volume 0.60, maximum 0.80.

## Alternatives considered
| Option | Why not |
|---|---|
| Just turn the volume down to 0.10 | clean but far too quiet |
| 280 Hz bass cut | clean only up to 0.25 |
| Soften the top 2 % of peaks | +9.0 dB, but sounds harsh |

## Evidence
Clean volume 0.10 → 0.25 (280 Hz) → 0.30+ (400 Hz) → 0.60+ (with the capacitor)
([M4](../evidence/development-measurements.md)). Compression +7.9 dB / +8.0 dB on speech
([M5](../evidence/development-measurements.md), [test output](../evidence/test-output.txt)).
Filter: 200 Hz −12.3 dB, 1 kHz −0.3 dB.

## Consequences
Voices sound slightly thinner ("phone-like") but clear. The 40 mm speaker remains the volume limit (K2).
