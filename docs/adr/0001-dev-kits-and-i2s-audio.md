# ADR-0001: Dev kits + I2S mic + MAX98357A, no custom PCB

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-20 |
| **Related** | [03 — Hardware](../03-hardware.md) |

## Context
A buildathon timeline (days), a toy that must fit in a plush, and a team new to audio hardware.

## Decision
ESP32-S3-DevKitC-1 N16R8 + I2S MEMS mic (ICS-43434 / INMP441) + MAX98357A I2S amp + 3 W 4 Ω
speaker, on breadboard then perfboard. All audio stays digital until the amp.

## Alternatives considered
| Option | Why not |
|---|---|
| Custom PCB | 1–2 weeks fabrication + shipping to India; too slow |
| Analog mic + ESP32 ADC | noisy; I2S mics give clean digital audio |
| Plain ESP32 (no S3) | less RAM; the N16R8's 8 MB PSRAM holds 8 s recordings and 15 s answers |
| All-in-one ESP32-S3 voice board | a teammate's idea; kept as an option, discrete modules chosen for availability and repairability |
| Phone hidden in the plush | works with no code changes, but not a real device |

## Evidence
All five sketches build for this board ([compile log](../evidence/firmware-compile.txt)); the mic test
and the live run work on this hardware ([live log](../evidence/live-session-2026-11-21.txt)).

## Consequences
Modules are easy to swap and re-flash. A PCB is still an option for a later, smaller toy.
