# Nani AI voice plush — Documentation

| | |
|---|---|
| **Project** | Nani: an ESP32-S3 voice plush toy connected to the Tutor Grandma web app |
| **Context** | Hardware add-on for a buildathon (Tutor Grandma web app by Hrishikesh Hundekari) |
| **Repository** | `nani-ai-voice-plush` |
| **Doc-set version** | 1.0 |
| **Last updated** | 2026-11-22 |
| **Status** | Working breadboard prototype, end to end |

## Start here

| If you want to… | Read |
|---|---|
| **Rebuild it from zero** (no electronics or audio background needed) | [Tutorial](tutorial/README.md) |
| Understand how it works | [02 — Architecture](02-architecture.md) |
| Wire it, flash it, run it | [03 — Hardware](03-hardware.md) → [07 — Runbook](07-operations-runbook.md) |
| Know what is measured and what is broken | [06 — Results](06-results.md) · [10 — Known issues](10-known-issues-roadmap.md) |

## Full document map

| # | Document | Type | Contents |
|---|---|---|---|
| 01 | [Overview](01-overview.md) | Explanation | Problem, objectives with status, scope, deliverables, constraints |
| 02 | [Architecture](02-architecture.md) | Explanation | Context, building blocks, runtime flows, wire protocol, deployment |
| 03 | [Hardware](03-hardware.md) | Reference | Parts list, pin map, wiring, power, assembly notes |
| 04 | [Firmware](04-firmware.md) | Reference | `nani-full` state machine, audio path, voice detection, settings |
| 05 | [Laptop brain](05-laptop-brain.md) | Reference | `nani_brain.py`: website mode, mirror, auto-find, offline mode |
| 06 | [Results](06-results.md) | Report | Every measured number with its source; experiments that failed |
| 07 | [Operations runbook](07-operations-runbook.md) | How-to | Setup, flashing, running, test sketches, troubleshooting |
| 08 | [Testing & quality](08-testing-quality.md) | Reference | Test layers, latest test output, coverage gaps |
| 09 | [Project history](09-project-history.md) | Record | Timeline and the why behind each phase |
| 10 | [Known issues & roadmap](10-known-issues-roadmap.md) | Record | Severity-ranked issues, next steps |
| — | [Glossary](glossary.md) | Reference | Every term used, in plain words |
| — | [References](references.md) | Reference | Datasheets, libraries, what each supports |
| — | [ADRs](adr/README.md) | Record | One file per significant decision, with evidence |
| — | [Tutorial](tutorial/README.md) | Tutorial | From-zero rebuild with runnable mini code |
| — | [Evidence](evidence/) | Raw data | Test output, compile logs, live session log, measurements |

## Component-level documentation (kept next to the code)

| File | Covers |
|---|---|
| [`firmware/nani-full/nani-full.ino`](../firmware/nani-full/nani-full.ino) (header comment) | Board settings, pins, modes, Serial commands |
| [`brain/nani_brain.py`](../brain/nani_brain.py) (docstring) | Modes, command-line options, wire protocol |
| [`brain/make_voice.py`](../brain/make_voice.py) (docstring) | Turning a sentence into a voice clip header |
| [`tests/run_tests.py`](../tests/run_tests.py) | What each automated check proves |

## Documentation conventions

- **Every number cites its source**: a file in [`evidence/`](evidence/) or a test.
- **Failures are documented** as carefully as what worked (see [06 — Results](06-results.md)).
- **Decisions live in ADRs** with the evidence that settled them.
- **Diagrams are Mermaid** (render on GitHub). Links are relative.
- **Update the docs in the same commit** as the code they describe.
