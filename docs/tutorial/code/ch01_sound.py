"""Chapter 01: sound is a list of numbers.

Mini version of the audio format used everywhere on the toy (nani-full.ino: RATE, FRAME).
Run:  python ch01_sound.py
"""
import numpy as np

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


def fake_microphone(seed=1):
    """What the mic hears: 1 s of quiet room, 1 s of 'speech', 1 s of quiet room.
    Speech is faked as a 300 Hz note that wobbles in loudness like syllables."""
    rng = np.random.default_rng(seed)
    room = lambda s: rng.normal(0, 60, int(RATE * s))            # soft background noise
    t = np.arange(RATE) / RATE
    syllables = 0.6 + 0.4 * np.sin(2 * np.pi * 4 * t)              # 4 "syllables" per second
    speech = np.sin(2 * np.pi * 300 * t) * 4000 * syllables + rng.normal(0, 60, RATE)
    return np.concatenate([room(1.0), speech, room(1.0)])


if __name__ == "__main__":
    mic = fake_microphone()
    print(f"{len(mic)} samples = {len(mic) / RATE:.1f} s of audio")
    print(f"first 5 samples: {np.round(mic[:5]).astype(int).tolist()}")
    print(f"loudness of the quiet room : {rms(mic[:FRAME]):7.1f}")
    print(f"loudness while 'speaking'  : {rms(mic[RATE:RATE + FRAME]):7.1f}")
