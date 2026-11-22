"""Chapter 02: knowing when the child starts and stops talking (voice activity detection).

Mini version of listenTick() / startRecording() in firmware/nani-full/nani-full.ino.
Same rules: learn the room's noise, start at 4x the noise, stop after 0.7 s below 2.5x.
Run:  python ch02_voice_detect.py
"""
import numpy as np

from ch01_sound import FRAME, RATE, fake_microphone, rms

START_FACTOR = 4.0        # speech = this many times louder than the room
STOP_FACTOR = 2.5         # quieter than this counts as silence
MIN_START_RMS = 300.0     # never trigger on anything quieter than this
END_SILENCE_MS = 700      # this much silence = the child has finished
FRAME_MS = 20


def detect_speech(samples):
    """Return (start_sample, end_sample) of the first utterance, or None."""
    frames = [samples[i:i + FRAME] for i in range(0, len(samples) - FRAME + 1, FRAME)]
    noise = np.mean([rms(f) for f in frames[:25]])          # first 0.5 s = room noise
    recording, start, silence_ms = False, 0, 0
    for n, f in enumerate(frames):
        level = rms(f)
        if not recording:
            if level > max(noise * START_FACTOR, MIN_START_RMS):
                recording, start, silence_ms = True, n, 0
            else:
                noise = 0.95 * noise + 0.05 * level          # slowly follow the room
        else:
            if level > max(noise * STOP_FACTOR, MIN_START_RMS * 0.6):
                silence_ms = 0
            else:
                silence_ms += FRAME_MS
            if silence_ms >= END_SILENCE_MS:
                end = n + 1 - END_SILENCE_MS // FRAME_MS      # back up to where speech ended
                return start * FRAME, end * FRAME
    return None


if __name__ == "__main__":
    s, e = detect_speech(fake_microphone())
    print(f"speech found from {s / RATE:.2f} s to {e / RATE:.2f} s (real speech: 1.00 s to 2.00 s)")
