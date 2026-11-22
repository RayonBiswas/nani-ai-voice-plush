# Glossary

| | |
|---|---|
| **Document type** | Reference |
| **Audience** | Everyone, especially beginners |
| **Last updated** | 2026-11-22 |

| Term | Meaning in this project |
|---|---|
| **Amp (MAX98357A)** | Small board that turns digital audio from the ESP32 into enough power to move the speaker |
| **Bass cut / high-pass filter** | Removes low notes (below 400 Hz here) that a small speaker can't play cleanly |
| **Biquad** | A 2nd-order digital filter: 5 numbers that turn each input sample into an output sample |
| **Bridge / brain** | `nani_brain.py` on the laptop: connects the toy to the website |
| **Compression (audio)** | Making quiet parts of speech louder and loud parts quieter, so the whole voice can be raised without crackling |
| **dB / dBFS** | Decibels: a loudness ratio. +6 dB ≈ twice the amplitude. dBFS = relative to the loudest possible digital value (0 dBFS) |
| **Debounce** | Ignoring the fast on/off flicker a mechanical switch makes for a few milliseconds when pressed |
| **Edge-triggered** | Reacting when a signal *changes*, not to its current level |
| **ESP32-S3** | The Wi-Fi microcontroller that runs the toy's firmware |
| **Filler** | "Hmm, let me think!": played instantly so the child doesn't wait in silence |
| **Firmware** | The program running on the ESP32 (`nani-full.ino`) |
| **Frame** | 20 ms of audio = 320 samples at 16 kHz |
| **I2S** | A 3-wire digital audio connection (bit clock, word select, data) between chips |
| **INMP441 / ICS-43434** | Tiny digital (I2S) microphones |
| **Latching switch** | Press once, it stays down; press again, it pops up |
| **Mirror** | The bridge keeps the website's stage page open (hidden) and copies its sounds to the toy |
| **Noise floor** | How loud the room is when nobody speaks; voice detection compares against it |
| **NDJSON** | Newline-delimited JSON: one JSON object per line, sent as a stream |
| **Overdrive** | Pushing a speaker past what it can move: sounds like crackle or hiss |
| **PCM** | Raw audio: a list of numbers (samples), here 16-bit signed |
| **Pre-roll** | The last 300 ms before speech was detected, kept so the first word isn't cut |
| **PSRAM** | Extra RAM on the N16R8 module (8 MB), used for recordings and answers |
| **RMS** | Root mean square: the average "loudness" of a block of samples |
| **Sample rate** | Samples per second; 16 000 Hz on the toy, 48 000 Hz in the browser |
| **Stage page** | The website page (`/stage`) where Nani talks and reminders are fired |
| **TCP** | Reliable connection over Wi-Fi; the toy listens on port 3333 |
| **TTS** | Text-to-speech, e.g. the Windows "Zira" voice |
| **`/api/turn`** | The website's endpoint: takes the child's speech, returns what it heard and Nani's answer with audio |
| **Voice activity detection (VAD)** | Deciding when someone starts and stops speaking |
| **Whisper** | Speech-to-text model (used in `--offline` mode) |
