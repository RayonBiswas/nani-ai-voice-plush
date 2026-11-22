# ADR-0004: Instant filler + play the answer sentence by sentence

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-21 |
| **Related** | `askBrain()` in [nani-full.ino](../../firmware/nani-full/nani-full.ino), `site_turn_stream()` |

## Context
Waiting ~7 s in silence for the whole answer felt broken. The website already streams its answer as
separate sentences.

## Decision
1. The toy plays "Hmm, let me think!" from flash the moment it sends the speech.
2. The bridge forwards each sentence (`ANS1` + `RPL1`) as soon as it arrives; the toy plays them in
   order and finishes on `END1`.
3. The stream is read with `iter_content(chunk_size=None)`.
4. End-of-speech wait cut from 900 to 700 ms.

## Alternatives considered
| Option | Why not |
|---|---|
| Wait for the whole answer | 7.2 s of silence |
| `requests` `iter_lines()` | buffers 512 bytes, so it held each event until the next arrived |

## Evidence
With `iter_lines()` the first sentence reached the toy 2.4 s after the website sent it; with
`iter_content(None)`, 0.4 s ([M8](../evidence/development-measurements.md),
[test output](../evidence/test-output.txt)). Live: first words 3.4–3.8 s after the speech reached the
laptop ([live log](../evidence/live-session-2026-11-21.txt)).

## Consequences
The amp stays on across sentences (no clicks). Long answers start fast but can still last 15 s.
