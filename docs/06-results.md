# 06 — Results

| | |
|---|---|
| **Document type** | Report |
| **Audience** | Judges, reviewers |
| **Last updated** | 2026-11-22 |

Every number here is copied from a file in [`evidence/`](evidence/). Listening results ("clean",
"crackles") are the builder's ears on the real 40 mm speaker, not a meter.

## 1. End-to-end on the hardware

Five real turns on 21 Nov 2026, toy on a power bank, bridge in website mode
(source: [live-session-2026-11-21.txt](evidence/live-session-2026-11-21.txt)).

| Child said | Heard by website at | First sentence at | Answer complete | Result |
|---|---|---|---|---|
| "Tuesday के बाद क्या आता है?" | 1.4 s | 3.6 s | 15.1 s | ✅ 5 sentences |
| *(a roar / laugh, no words)* | 1.4 s | 3.4 s | 13.3 s | ✅ "Shabaash, Aarav! Sher ka roar…" |
| "Hello नानी, Tuesday के बाद…" | 1.9 s | — | 10.7 s | ❌ website `slow_brain` fallback at 8.7 s |
| "नानी, Tuesday के बाद क्या आता है?" | 1.6 s | 3.8 s | 15.5 s | ✅ |
| "Apple कौन से color का होता है?" | 1.9 s | 3.5 s | 8.9 s | ✅ 3 sentences |

- Times are measured from when the speech reached the laptop. Before that come the 0.7 s silence
  wait and a few tens of ms of Wi-Fi transfer; during the wait the toy plays its 1.5 s "Hmm" filler.
- **First words in 3.4–3.8 s** in all four successful turns; **4/5 turns answered**. The one failure
  was the website giving up (its own 8 s limit), which the toy reported out loud.
- The website remembered context ("Tera lion wala din yaad hai, 14 Nov ko!"): the toy really gets
  the same Nani as the web app.

## 2. Latency work

| Step | Change | Effect | Source |
|---|---|---|---|
| Offline brain | Whisper + qwen3 + Zira on CPU | 13.1 s to a full answer | [M6](evidence/development-measurements.md) |
| Website brain, whole answer | `/api/turn`, wait for all of it | 7.2 s | [M7](evidence/development-measurements.md) |
| + streaming, first try | forward sentences with `iter_lines()` | each sentence ~2 s late (held until the next) | [M8](evidence/development-measurements.md) |
| + streaming, fixed | `iter_content(None)` | each sentence 0.3–0.4 s after the website sends it | [M8](evidence/development-measurements.md), [test](evidence/test-output.txt) |
| + filler | "Hmm, let me think!" from flash right after sending | no silent wait | firmware |
| + shorter end-of-speech wait | 900 → 700 ms | −0.2 s | firmware |

## 3. Sound quality: the "static" investigation

| Hypothesis | Test | Result | Source |
|---|---|---|---|
| The voice file itself is noisy | measure quiet parts of the generated sentence | −90 dBFS: clean | [M2](evidence/development-measurements.md) |
| Power / ground noise | `z`: amp on, sending pure zeros | silent: not power | [M2](evidence/development-measurements.md) |
| Signal wiring | 1 kHz tone `3` | clean: wiring fine | [M2](evidence/development-measurements.md) |
| **Speaker overdrive** | same sentence at 0.10 instead of 0.30 | **clean: cause found** | [M2](evidence/development-measurements.md) |
| Which frequencies | melody in 3 octaves; 250 Hz tone | 262 Hz and 250 Hz crackle, 523 Hz+ clean | [M2](evidence/development-measurements.md) |

## 4. Speaker volume

| Setup | Loudest clean volume | Source |
|---|---|---|
| no filter | 0.10 | [M4](evidence/development-measurements.md) |
| 280 Hz bass cut | 0.25 (0.30 crackles) | [M4](evidence/development-measurements.md) |
| 400 Hz bass cut | ≥ 0.30 (the limit at the time) | [M4](evidence/development-measurements.md) |
| 400 Hz + 1000 µF capacitor | **≥ 0.60** (the limit at the time) | [M4](evidence/development-measurements.md) |

The builder still found 0.60 too quiet for a room. 0.80 is the full digital level (+2.5 dB), so more
volume now needs hardware: GAIN pin (+3 / +6 dB), a speaker box, or a bigger speaker
([10 — Known issues](10-known-issues-roadmap.md)).

Bass-cut filter response (measured by `tests/run_tests.py`): 200 Hz −12.3 dB, 400 Hz −3.0 dB,
1 kHz −0.3 dB, 3 kHz −0.1 dB ([test output](evidence/test-output.txt)).

## 5. Loudness boost (compression)

| Variant | Loudness gain at the same peak | Source |
|---|---|---|
| gentle compressor only | +2.4 dB | [M5](evidence/development-measurements.md) |
| + soften top 0.1 % of peaks | +6.8 dB | [M5](evidence/development-measurements.md) |
| **+ soften top 0.5 % (chosen)** | **+7.7 dB**; +8.0 dB in the automated test | [M5](evidence/development-measurements.md), [test](evidence/test-output.txt) |
| + soften top 2 % | +9.0 dB, rejected: starts to sound harsh | [M5](evidence/development-measurements.md) |

## 6. Firmware build and checks

| Check | Result | Source |
|---|---|---|
| 5 sketches compile (core 3.3.11) | all exit 0; nani-full 93 % flash | [firmware-compile.txt](evidence/firmware-compile.txt) |
| Automated laptop-side tests | 6/6 pass | [test-output.txt](evidence/test-output.txt) |
| USB mic stream integrity | 209/209 packets exactly 644 bytes after the fix (was ~262-byte fragments) | [M1](evidence/development-measurements.md) |
| Website audio hook | test tone captured, 48 kHz → 16 kHz, pitch 1000 Hz | [M9](evidence/development-measurements.md) |

## 7. Limitations of these results

- Five live turns is a small sample; latency depends on the website and the Wi-Fi.
- Volume and crackle are judged by ear, on one speaker, on a breadboard (no enclosure).
- The website mirror was proven with an injected tone; a scheduled reminder playing on the toy was
  not observed during testing (none was due).
- Offline-mode latency was measured once, with a fake toy.
