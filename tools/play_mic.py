"""Play the ESP32's mic on the laptop speaker.

Run:   python play_mic.py --port COM6
Stop:  Ctrl+C

On start this sends 'A' to put the ESP32 in AUDIO mode, and 'T' on exit so the
Arduino Serial Monitor shows the text level readout again.
The ESP32 (mic-to-laptop.ino) sends packets over USB: header A5 5A 4D 43, then
320 samples of 16-bit little-endian mono audio at 16 kHz (20 ms per packet).
"""
import argparse
import sys
import time

import numpy as np
import serial
import sounddevice as sd

HEADER = bytes([0xA5, 0x5A, 0x4D, 0x43])
RATE = 16000
FRAME = 320
PACKET = len(HEADER) + FRAME * 2


def main():
    ap = argparse.ArgumentParser(description="Play the ESP32 mic on this laptop")
    ap.add_argument("--port", default="COM6", help="ESP32 serial port (default COM6)")
    ap.add_argument("--gain", type=float, default=4.0, help="volume boost (default 4)")
    args = ap.parse_args()

    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = args.port, 115200, 1
    ser.dtr = False  # keep both lines low so opening the port doesn't reset the ESP32
    ser.rts = False
    try:
        ser.open()
    except serial.SerialException as e:
        sys.exit(f"Can't open {args.port}: {e}\nClose the Arduino Serial Monitor if it's open.")
    ser.write(b"A")  # switch the ESP32 from TEXT mode to AUDIO mode

    print(f"Listening on {args.port}. Speak into the mic. Ctrl+C to stop.")
    buf = bytearray()
    packets, last_print, loudest = 0, time.time(), 0

    with sd.RawOutputStream(samplerate=RATE, channels=1, dtype="int16",
                            blocksize=FRAME, latency="low") as out:
        try:
            while True:
                buf += ser.read(ser.in_waiting or 1)
                while True:
                    i = buf.find(HEADER)
                    if i < 0:
                        if len(buf) > 3:  # keep a partial header, drop the rest
                            text = bytes(buf[:-3]).decode("ascii", "ignore").strip()
                            if text:
                                print("ESP32:", text)
                            del buf[:-3]
                        break
                    if i > 0:  # text the ESP32 printed before the audio started
                        text = bytes(buf[:i]).decode("ascii", "ignore").strip()
                        if text:
                            print("ESP32:", text)
                        del buf[:i]
                    if len(buf) < PACKET:
                        break
                    samples = np.frombuffer(bytes(buf[4:PACKET]), dtype="<i2")
                    del buf[:PACKET]
                    loud = np.clip(samples.astype(np.float32) * args.gain, -32768, 32767)
                    out.write(loud.astype(np.int16).tobytes())
                    packets += 1
                    loudest = max(loudest, int(np.abs(loud).max()))

                if time.time() - last_print >= 1:
                    bars = "#" * min(40, loudest // 800)
                    print(f"\r{packets:3d} packets/s  level {loudest:5d} |{bars:<40}|", end="", flush=True)
                    packets, loudest, last_print = 0, 0, time.time()
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            try:
                ser.write(b"T")  # back to TEXT mode for the Arduino Serial Monitor
            except serial.SerialException:
                pass
            ser.close()


if __name__ == "__main__":
    main()
