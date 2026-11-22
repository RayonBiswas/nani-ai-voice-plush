# 01 — Overview

| | |
|---|---|
| **Document type** | Explanation |
| **Audience** | Judges, reviewers, new contributors |
| **Last updated** | 2026-11-22 |

## 1. Executive summary

**Tutor Grandma** is a web app where "Nani", an AI grandmother, talks with a small child (the demo
child is "Aarav") in Hindi, English and Hinglish, reminds him to drink water, tells bedtime stories,
and keeps a shared memory that parents can steer by chat. This project gives Nani a **body**: a plush
toy built around an ESP32-S3 that the child can press, talk to, and hear answer.

| Headline | Value | Source |
|---|---|---|
| Works end to end on hardware | Hindi/Hinglish question → website answer in Nani's voice from the toy | [live session log](evidence/live-session-2026-11-21.txt) |
| Time until Nani starts answering | 3.4–3.8 s after the speech reaches the laptop (plus an instant "Hmm" filler) | [live session log](evidence/live-session-2026-11-21.txt) |
| Clean speaker volume | 0.60 (was 0.10 before the fixes) | [M4](evidence/development-measurements.md) |
| Speech loudness boost at the same peak | +8.0 dB | [test output](evidence/test-output.txt) |
| Automated checks | 6/6 pass, 5/5 sketches compile | [test output](evidence/test-output.txt), [compile log](evidence/firmware-compile.txt) |

**Main insight:** the toy itself should stay simple. The ESP32 only listens, plays and shows its state.
A small laptop bridge does the heavy work by reusing the web app's own backend, so the toy gets
exactly the same Nani (memory, voice, agents) with no second "brain" to keep in sync.

## 2. Problem statement

The senior's request in the team chat (19 Nov 2026):

> "How would you build the soft toy hardware … in sync with the agentic software side.
> Also I want a list of all components whenever you pitch your idea."

The web app only had a browser "Tap to talk" stage. A real child needs a physical toy: no screen,
one button, a voice that comes from the toy, and reminders that reach the child even when nobody is
looking at the website.

## 3. Objectives

| ID | Objective | Status |
|---|---|---|
| O1 | Components list (BOM) with costs | **Done**: [03 — Hardware](03-hardware.md) |
| O2 | Mic that reliably hears a child's voice | **Done**: mic test + live use |
| O3 | Speaker that is loud enough and clean | **Done** (0.60 clean); louder needs an enclosure, see [10](10-known-issues-roadmap.md) |
| O4 | Toy answers with the web app's Nani (same memory and voice) | **Done**: [ADR-0003](adr/0003-reuse-website-api-turn.md) |
| O5 | Answer latency that feels natural | **Done**: filler + sentence streaming ([ADR-0004](adr/0004-filler-and-sentence-streaming.md)) |
| O6 | Website reminders play on the toy | **Done** (mechanism tested; a live reminder on the toy not yet observed) |
| O7 | One-switch operation, no typing | **Done**: switch + auto-find + `start-nani.bat` |
| O8 | LED eyes show the mode | **In progress**: code done, LEDs not yet moved to GPIO 9–14 |
| O9 | Fit everything inside a plush | **Planned** |
| O10 | Toy works without a laptop | **Planned**, see roadmap |

## 4. Scope

**In scope:** toy hardware, ESP32 firmware, the laptop bridge, hardware test sketches, documentation.

**Out of scope:**
- The web app itself (agents, memory, voices, `/api/turn`): owned by the senior; used as-is.
- A custom PCB: dev kits on perfboard are faster for a buildathon (a PCB takes 1–2 weeks to arrive in India).
- Wake word ("Hey Nani"): needs custom model training; the switch + voice detection is enough for now.

## 5. Deliverables

| Deliverable | Location |
|---|---|
| Toy firmware | [`firmware/nani-full/`](../firmware/nani-full/nani-full.ino) |
| Hardware test sketches | [`firmware/tests/`](../firmware/tests/) |
| Laptop bridge | [`brain/nani_brain.py`](../brain/nani_brain.py), [`start-nani.bat`](../start-nani.bat) |
| Voice clip generator | [`brain/make_voice.py`](../brain/make_voice.py) |
| Automated tests | [`tests/run_tests.py`](../tests/run_tests.py) |
| Parts list and wiring | [03 — Hardware](03-hardware.md) |
| Demo videos | end-to-end conversations: [56 s](media/demo-conversation-56s.mp4), [35 s](media/demo-conversation-35s.mp4), [26 s](media/demo-conversation-26s.mp4); first sound test: [18 s](media/demo-2026-11-21.mp4) |
| Build photos | [top](media/prototype-in-box-top.jpg), [wide](media/prototype-in-box-wide.jpg) |

## 6. Constraints and deliberate choices

| Constraint | Choice | ADR |
|---|---|---|
| ESP32 can't run speech recognition or an LLM | Laptop bridge does the heavy lifting | [ADR-0002](adr/0002-laptop-bridge-architecture.md) |
| One Nani, not two | Reuse the website's `/api/turn` instead of a separate AI | [ADR-0003](adr/0003-reuse-website-api-turn.md) |
| Answers take ~7 s on the website | Instant filler + play sentence by sentence | [ADR-0004](adr/0004-filler-and-sentence-streaming.md) |
| Small speaker crackles | 400 Hz bass cut + compression + capacitor | [ADR-0005](adr/0005-speaker-bass-cut-and-compression.md) |
| Reminders are fired by the website's browser page | Mirror the stage page's audio | [ADR-0006](adr/0006-mirror-stage-page-audio.md) |
| ESP32-S3 joins only 2.4 GHz Wi-Fi | Documented; `secrets.h` holds the network | [07 — Runbook](07-operations-runbook.md) |
