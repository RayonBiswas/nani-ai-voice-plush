# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Dates ISO 8601. Versions before 1.0.0 are
milestones derived from the build history ([docs/09-project-history.md](docs/09-project-history.md));
the repository starts at 1.0.0.

## [Unreleased]
### Planned
- LED eyes on GPIO 9–14, speaker enclosure, fitting into the plush (see [roadmap](docs/10-known-issues-roadmap.md)).

## [1.0.0] — 2026-11-22 — First public version
### Added
- Clean repository: `firmware/`, `brain/`, `tools/`, `tests/`, `docs/`.
- Automated laptop-side tests (`tests/run_tests.py`, 6 checks).
- Full documentation, 8 ADRs, beginner tutorial, evidence logs, demo video.
### Changed
- Wi-Fi moved from the sketch into a git-ignored `secrets.h` (`secrets.example.h` provided).
- Default volume 0.60 (clean with a 1000 µF capacitor), maximum 0.80.
### Removed
- Unused play-back fallback (`speakReply()`) and old stream parser (`parse_turn_stream()`).

## [0.5.0] — 2026-11-21 — One-switch system
### Added
- Edge-triggered latching on/off switch on GPIO 2; Nani starts asleep.
- Website speech (reminders, songs) mirrored from the stage page to the toy.
- Auto-find of the toy on the Wi-Fi; `start-nani.bat`; website mode on by default.
- "Wait beta, I am waking up!" when no bridge is connected.

## [0.4.0] — 2026-11-21 — Fast answers
### Added
- Instant "Hmm, let me think!" filler; sentence-by-sentence playback; `[time]` logs.
### Fixed
- Each streamed sentence was held back until the next one (`iter_lines()` buffering).

## [0.3.0] — 2026-11-21 — Nani answers
### Added
- Offline laptop brain (Whisper + Ollama + Zira), then website mode via `/api/turn`.
### Fixed
- Toy could not join `sra_5G` (5 GHz); uses the 2.4 GHz network.

## [0.2.0] — 2026-11-21 — Clean speaker
### Added
- Spoken sentences from flash (`make_voice.py`), 400 Hz bass cut, speech compression.
### Fixed
- "Static" traced to speaker overdrive; clean volume raised from 0.10.

## [0.1.0] — 2026-11-20 — Hearing
### Added
- Parts list, `mic-test`, USB and Wi-Fi mic streaming to the laptop, WAV recording.
### Fixed
- USB mic packets cut short (zero-timeout writes into a small buffer).
