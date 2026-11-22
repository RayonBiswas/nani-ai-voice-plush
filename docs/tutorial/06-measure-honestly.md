# 6 — Measure honestly

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners |
| **Last updated** | 2026-11-22 |

**You will build:** [`code/test_mini.py`](code/test_mini.py) · **Full version:**
[`tests/run_tests.py`](../../tests/run_tests.py)

## 💡 Idea

"It sounded fine" is not a measurement. A good check proves the code right by a **different route** than
the code itself:

| What we check | Independent route |
|---|---|
| Voice detection | the fake mic's speech is *known* to be 1.00–2.00 s |
| The filter | the time-domain result must match the textbook frequency formula |
| The link | a message deliberately split into 3 pieces must still be read whole |
| Streaming | the first sentence must play before the website even sends the last one |

## The code (excerpt)

```python
# Ch02: we KNOW the fake speech is 1.00 s to 2.00 s
s, e = detect_speech(fake_microphone())
check("voice detection", abs(s / RATE - 1.0) < 0.1 and abs(e / RATE - 2.0) < 0.15,
      f"found {s / RATE:.2f}-{e / RATE:.2f} s, truth 1.00-2.00 s")
```

## Try it

```powershell
python test_mini.py
```

## ✅ Check

```
[PASS] voice detection: found 1.00-2.00 s, truth 1.00-2.00 s
[PASS] filter at 200 Hz: measured -12.3 dB, formula -12.3 dB
[PASS] filter at 1000 Hz: measured -0.3 dB, formula -0.1 dB
[PASS] link reads split messages: b'ANS1' b'Shabaash beta'
[PASS] sentences stream, not batch: first audio at 0.5 s, last sentence sent at 1.5 s
ALL PASS
```
At 1000 Hz the measured −0.3 dB differs from the formula's −0.1 dB because measuring the peak of a sampled
wave slightly underestimates it. The test allows 0.3 dB for that.

## Be honest about failures too

When the real project's tests first ran, two failed. Neither was a code bug; both were wrong tests:
- the compressor was tested on a beeping tone instead of speech (it's tuned for speech);
- the streaming pass mark ignored the 0.4 s ffmpeg needs per sentence.

Both are written up in [08 — Testing](../08-testing-quality.md#4-two-test-failures-that-taught-something),
and the compressor's real limitation is logged as a known issue. Writing down what *didn't* work is part of
measuring honestly.

## For the hardware

Listening tests count as measurements if you write down the setup and the result. The volume investigation
recorded every step: 0.10 clean → 0.25 with a 280 Hz cut → 0.30 with 400 Hz → 0.60 with the capacitor
([M4](../evidence/development-measurements.md)).

Next: [7 — From mini to full](07-from-mini-to-full.md).
