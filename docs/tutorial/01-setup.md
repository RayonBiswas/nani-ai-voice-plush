# 1 — Setup: sound is a list of numbers

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners |
| **Last updated** | 2026-11-22 |

**You will build:** [`code/ch01_sound.py`](code/ch01_sound.py) · **Full version:** the audio constants
(`RATE`, `FRAME`) in [`nani-full.ino`](../../firmware/nani-full/nani-full.ino)

## Install

```powershell
pip install numpy matplotlib
cd docs/tutorial/code
```

## 💡 Idea

A microphone measures air pressure many times per second. Each measurement is one number, called a
**sample**. Our toy takes **16 000 samples per second** (the *sample rate*, 16 kHz), each a whole number
between −32768 and 32767. So **one second of sound = a list of 16 000 numbers**. Silence is numbers near 0;
loud sound swings far from 0.

To ask "how loud is it right now?", we look at a short block, 20 ms = 320 samples (a **frame**), and
compute its **RMS** (root mean square): square every number, average them, take the square root. It's the
"typical size" of the swings.

## The code

```python
RATE = 16000          # samples per second (the toy uses 16 kHz)
FRAME = 320           # 20 ms of audio = 320 samples


def tone(hz, seconds, loudness=3000.0):
    """A pure note: a sine wave. Each sample is one number between -32768 and 32767."""
    t = np.arange(int(RATE * seconds)) / RATE
    return np.sin(2 * np.pi * hz * t) * loudness


def rms(samples):
    """'How loud' a block of samples is (root mean square), with the average (DC) removed."""
    x = samples - np.mean(samples)
    return float(np.sqrt(np.mean(x ** 2)))
```

- `hz` is the pitch: 300 Hz = a low voice, 1000 Hz = a whistle.
- We subtract the mean first because real mics often add a constant offset ("DC"), which isn't sound.

`fake_microphone()` builds 3 seconds of test audio: quiet room, then one second of "speech" (a 300 Hz note
that wobbles 4 times per second like syllables), then quiet again. We know exactly where the speech is,
which lets us check the next chapter's code.

## Try it

```powershell
python ch01_sound.py
```

## ✅ Check

```
48000 samples = 3.0 s of audio
first 5 samples: [64, 43, 28, 34, 87]
loudness of the quiet room :    57.9
loudness while 'speaking'  :  1981.6
```
Speech is about 34× louder than the room. That gap is what the toy uses to notice speech.

## ⚠️ Common mistakes

| Symptom | Cause |
|---|---|
| RMS is large even in silence | forgot to remove the mean (DC offset) |
| A "1 second" tone lasts 0.5 s when played | the player assumed a different sample rate (e.g. 32 kHz) |

## In the full project

The ESP32 reads the mic over **I2S** (a 3-wire digital audio link). The mic sends 32-bit words; the
firmware keeps the useful top bits with `word >> 14` to get 16-bit samples (`micFrame()`).

Next: [2 — Hearing](02-hearing.md).
