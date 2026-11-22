# ADR-0002: Toy is a thin client; a laptop bridge does the heavy work

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | [02 — Architecture](../02-architecture.md), [05 — Laptop brain](../05-laptop-brain.md) |

## Context
Speech recognition, an LLM and natural speech synthesis do not fit on an ESP32. The website's answer
audio is MP3, which the ESP32 would have to decode.

## Decision
The ESP32 only records, plays, detects voice and shows its state. A Python bridge on the laptop handles
HTTPS, MP3 decoding, resampling and audio treatment. The **toy is the TCP server** (port 3333) and the
laptop connects to it, so the toy never needs the laptop's address; the laptop finds the toy by scanning
its network.

## Alternatives considered
| Option | Why not (for now) |
|---|---|
| ESP32 calls the website directly | needs HTTPS + MP3 decoding + streaming JSON on the ESP32; more risk under time pressure. On the roadmap (R6) |
| Toy as TCP client of the laptop | the toy would need the laptop's IP, which changes |
| mDNS `nani.local` | did not resolve on this Windows laptop; replaced by scanning |

## Evidence
`find_toy()` finds the toy in 1.2–2.5 s ([test output](../evidence/test-output.txt)); the toy's address
changed from `.87` to `.187` during testing and auto-find kept working.

## Consequences
The toy depends on a laptop being on (known issue K1). All audio processing can be changed in Python
without re-flashing.
