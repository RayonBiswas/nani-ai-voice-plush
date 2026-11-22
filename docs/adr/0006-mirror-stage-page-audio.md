# ADR-0006: Website speech on the toy by mirroring the stage page's audio

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | `stage_mirror()`, `HOOK_JS` in [nani_brain.py](../../brain/nani_brain.py) |

## Context
The website's reminders, calls and songs are fired by its **stage page in a browser**: it reads the
schedule from the database and plays audio through one Web Audio player. No server pushes that audio.

## Decision
The bridge opens the stage page in a hidden, muted Microsoft Edge (Playwright), wraps
`AudioBufferSourceNode.prototype.start` to copy every sound to Python, and sends it to the toy as
`SAY1` + `RPL1` + `END1` when no conversation is running.

## Alternatives considered
| Option | Why not |
|---|---|
| Re-implement the website's scheduler in Python | duplicates logic that would drift from the website |
| Ask the owner for a push channel for devices | best long term; not available in time |
| Listen to the website's realtime channel | it carries schedule changes, not the audio itself |

## Evidence
On the real stage page an injected 1 kHz tone was captured and converted 48 kHz → 16 kHz with the right
pitch ([M9](../evidence/development-measurements.md)); forwarding is covered by `test_website_speech`
([test output](../evidence/test-output.txt)). A real scheduled reminder on the toy is not yet observed (K4).

## Consequences
Anything the website says plays on the toy with the website's own timing. Only one stage page should be
open, or reminders fire twice.
