# ADR-0007: Edge-triggered latching switch; start asleep

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | `switchPressed()`, `toggleNani()` in [nani-full.ino](../../firmware/nani-full/nani-full.ino) |

## Context
The available on/off switch is a self-locking push switch: its button sits at a different height when
locked and unlocked. The builder wanted every press to mean the same thing.

## Decision
Read GPIO 2 with the internal pull-up and react to the **change** (debounced 40 ms), not the level: every
press toggles awake ↔ asleep. The position at power-up is only remembered, and Nani starts asleep.
`w` in the Serial Monitor does the same.

## Alternatives considered
| Option | Why not |
|---|---|
| Use the switch to cut power | the toy would reboot and rejoin Wi-Fi every time (slow) |
| Level-triggered (down = on) | depends on which way the switch was left |
| Wake word | needs a trained model |

## Evidence
The builder confirmed on the hardware that every press toggles Nani.

## Consequences
The ESP32 stays powered and connected, so waking is instant. A press during an answer acts after it (K9).
