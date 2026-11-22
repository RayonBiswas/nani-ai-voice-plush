"""Record the ESP32's mic into a .wav file you can play on the laptop.

Needs mic-to-laptop.ino on the ESP32, and the Arduino Serial Monitor CLOSED.

Run:   python record_wav.py                 (5 seconds, saved in Wispr\\recordings)
       python record_wav.py --seconds 10    (longer)
Then double-click the .wav file it prints to hear it.
"""
import argparse
import time
import wave
from pathlib import Path

import numpy as np
import serial

HEADER = bytes([0xA5, 0x5A, 0x4D, 0x43])
RATE = 16000
FRAME = 320
PACKET = len(HEADER) + FRAME * 2
OUT_DIR = Path(__file__).resolve().parent.parent / "recordings"


def parse_packets(buf: bytes) -> np.ndarray:
    """Pull every complete audio packet out of the raw serial bytes."""
    chunks, i = [], 0
    while True:
        j = buf.find(HEADER, i)
        if j < 0 or j + PACKET > len(buf):
            break
        chunks.append(np.frombuffer(buf[j + 4:j + PACKET], dtype="<i2"))
        i = j + PACKET
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.int16)


def save_wav(samples: np.ndarray, path: Path, normalize: bool = True) -> int:
    """Save 16 kHz mono 16-bit WAV. Returns the peak level written."""
    x = samples.astype(np.float32)
    x -= x.mean() if x.size else 0
    if normalize and x.size and np.abs(x).max() > 0:
        x *= min(29000 / np.abs(x).max(), 20.0)  # make quiet recordings audible, max 20x boost
    out = np.clip(x, -32768, 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(out.tobytes())
    return int(np.abs(out).max()) if out.size else 0


def main():
    ap = argparse.ArgumentParser(description="Record the ESP32 mic to a .wav file")
    ap.add_argument("--port", default="COM7")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--out", help="output file (default: recordings/rec_<time>.wav)")
    ap.add_argument("--raw", action="store_true", help="don't boost the volume")
    args = ap.parse_args()

    s = serial.Serial()
    s.port, s.baudrate, s.timeout = args.port, 115200, 0.2
    s.dtr = False
    s.rts = False
    try:
        s.open()
    except serial.SerialException as e:
        raise SystemExit(f"Can't open {args.port}: {e}\nClose the Arduino Serial Monitor first.")

    s.write(b"A")          # ESP32: switch to audio streaming
    time.sleep(0.3)
    s.reset_input_buffer()
    print(f"Recording {args.seconds:.0f} s... speak now!")
    buf = bytearray()
    t0 = time.time()
    while time.time() - t0 < args.seconds:
        buf += s.read(8192)
    s.write(b"T")          # back to text mode for the Arduino Serial Monitor
    s.close()

    samples = parse_packets(bytes(buf))
    if samples.size == 0:
        raise SystemExit("No audio received. Is mic-to-laptop.ino flashed on the ESP32?")
    path = Path(args.out) if args.out else OUT_DIR / time.strftime("rec_%Y%m%d_%H%M%S.wav")
    peak = save_wav(samples, path, normalize=not args.raw)
    print(f"Saved {samples.size / RATE:.1f} s of audio (peak {peak}) to:\n  {path}")
    print("Double-click that file to play it.")


if __name__ == "__main__":
    main()
