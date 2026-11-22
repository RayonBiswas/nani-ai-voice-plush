# ADR-0003: Reuse the website's `/api/turn` instead of a second AI

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | `site_turn_stream()` in [nani_brain.py](../../brain/nani_brain.py) |

## Context
A first laptop brain (Whisper + Ollama qwen3 + Windows Zira) worked, but it was a *different* Nani: no
memory of Aarav, an English voice, 13.1 s per answer. Reading the website's public page code showed its
toy page posts audio to `/api/turn` and gets back `heard` and `say` (text + base64 audio) events.

## Decision
The bridge posts the toy's speech to `/api/turn` exactly like the website's toy page does, and forwards
the answer audio. `--offline` keeps the laptop-only brain as a fallback.

## Alternatives considered
| Option | Why not |
|---|---|
| Laptop-only AI | a second Nani with no shared memory; slower; English voice |
| Ask the owner for a new device API first | right long term (K6) but slower than reusing the existing endpoint |

## Evidence
One test turn: 7.2 s, *"Aarav beta, banana pila hota hai! Yellow!…"* in Nani's own voice
([M7](../evidence/development-measurements.md)). Live: 4/5 Hindi/Hinglish turns answered, with memory
("Tera lion wala din yaad hai") ([live log](../evidence/live-session-2026-11-21.txt)). Used with the web
app owner's knowledge; it uses his live service and API credits.

## Consequences
Same personality, memory and voice on the web and in the toy. The protocol is not a documented API and
may change (K6).
