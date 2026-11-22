# 08 — Testing & quality

| | |
|---|---|
| **Document type** | Reference |
| **Audience** | Developers, reviewers |
| **Last updated** | 2026-11-22 |

## 1. Test layers

| Layer | What it guards | How to run |
|---|---|---|
| Firmware compiles | all 5 sketches build with core 3.3.11 | Arduino IDE *Verify*, or `arduino-cli compile` ([log](evidence/firmware-compile.txt)) |
| Laptop automated tests | filter, compression, link protocol, sentence streaming, auto-find, website speech forwarding | `python tests/run_tests.py` |
| Hardware checks | mic, speaker, mic→laptop, Wi-Fi, each on its own | sketches in `firmware/tests/` ([runbook §5](07-operations-runbook.md#5-hardware-checks-one-part-at-a-time)) |
| End to end | toy ↔ bridge ↔ website with real speech | live run ([log](evidence/live-session-2026-11-21.txt)) |

## 2. Latest automated test output (verbatim)

From [`evidence/test-output.txt`](evidence/test-output.txt), 2026-11-22:
```
[PASS] 400 Hz bass cut: 200 Hz -12.3 dB, 400 Hz -3.0 dB, 1 kHz -0.3 dB, 3 kHz -0.1 dB
[PASS] compressor on real speech: peak 28000 (limit 28000), speech loudness +8.0 dB
[PASS] link message framing: b'ANS1' 13 bytes b'Shabaash beta'
[PASS] sentence-by-sentence streaming: website sends heard 0.5 s, sentences [1.5, 2.5, 3.5] s -> received heard [1.0], sentences [2.2, 3.2, 4.1] (lag [0.7, 0.7, 0.6] s, gaps [1.0, 0.9] s)
[PASS] find toy on Wi-Fi: found 192.168.1.7 in 1.2 s
Website -> toy: 1.0 s of Nani's website speech
[PASS] website speech to toy: messages [('SAY1', 7), ('RPL1', 32000), ('END1', 0)] (1.0 s at 48 kHz -> 32000 bytes at 16 kHz)

6/6 passed
```

## 3. What each test proves

| Test | Independent check |
|---|---|
| `test_bass_cut` | runs a pure tone through the same filter as the firmware and measures the gain at 200 Hz, 400 Hz, 1 kHz, 3 kHz |
| `test_compress` | real Zira speech: peak stays ≤ 28000 while speech loudness rises > 5 dB |
| `test_protocol` | sends a message over a socket pair and reads it back byte for byte |
| `test_streaming` | a fake website sends 3 MP3 sentences 1 s apart over chunked HTTP; they must arrive spread out (≥ 0.6 s apart) and the first before the last is even sent (not batched) |
| `test_find_toy` | a fake toy listens on the laptop's network address; `find_toy()` must find it |
| `test_website_speech` | a 1 s 48 kHz float tone in the mirror queue must become `SAY1`, a 32000-byte `RPL1`, `END1`; a 20 ms click must be skipped |

## 4. Two test failures that taught something

| First result | What it really showed | Fix |
|---|---|---|
| compressor −2.5 dB on a beeping tone | the compressor is tuned for speech; on pure tone bursts it lowers loudness | test now uses real speech (+8.0 dB); limitation logged as [K7](10-known-issues-roadmap.md) |
| streaming "fail": sentences at 2.0/3.0/4.0 s | each sentence arrives 0.4–0.5 s after sending (ffmpeg decode), still before the next one; the threshold was wrong, not the code | the test checks the lag per sentence instead of an absolute time |
| streaming flaky (22 Nov, later): passed, then failed with heard at 1.0 s | a busy laptop adds a constant 0.3–0.8 s at the start of the request; sentences were still ~1 s apart | the test now checks the gaps between sentences and that the first arrives before the last is sent |

## 5. Debugging method used

Every hardware problem was handled the same way: **measure, form one hypothesis, change one thing**.
Examples: the broken USB packets ([M1](evidence/development-measurements.md)) were found by counting
bytes between packet headers; the speaker "static" ([M2](evidence/development-measurements.md)) was
narrowed down with a digital-silence test before touching any wiring.

## 6. Coverage gaps

- No automated test runs on the ESP32 itself (voice detection, `askBrain()` parsing are checked only by live use).
- No test of a real scheduled website reminder reaching the toy.
- `--offline` mode has no automated test (needs Ollama + model download).
- `test_compress` needs the Windows Zira voice, so it can't run on Linux/macOS CI.
- No continuous integration yet; tests are run by hand.
