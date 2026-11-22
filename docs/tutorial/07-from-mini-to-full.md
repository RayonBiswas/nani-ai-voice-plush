# 7 — From mini to full

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners moving on to the real project |
| **Last updated** | 2026-11-22 |

## Mini → full mapping

| Mini file | Real file | What the real one adds |
|---|---|---|
| `ch01_sound.py` | `nani-full.ino`: `micStart()`, `micFrame()` | I2S driver, 32-bit words → 16-bit samples |
| `ch02_voice_detect.py` | `nani-full.ino`: `listenTick()`, `startRecording()` | pre-roll, minimum speech length, trimming, PSRAM buffer, eye colours |
| `ch03_speaker_filter.py` | `nani-full.ino`: `hpf()`, `playMono()`; `brain/make_voice.py`: `bass_cut()`, `compress()` | volume control, amp sleep pin, filter reset, speech compression, voice clips in flash |
| `ch04_link.py` | `nani-full.ino`: `writeMsg()`, `readExact()`; `nani_brain.py`: `send_msg()`, `recv_exact()` | timeouts, toy as TCP server, auto-find (`find_toy()`) |
| `ch05_mini_brain.py` | `nani_brain.py`: `site_turn_stream()`, `main()`; `nani-full.ino`: `askBrain()` | real HTTPS to `/api/turn`, MP3 decoding, filler, error messages, website mirror |
| `test_mini.py` | `tests/run_tests.py` | fake website over real HTTP, fake toy on the network, real speech for compression |

## Build the real toy, in order

1. Read [03 — Hardware](../03-hardware.md) and wire the mic → run `mic-test`.
2. Wire the amp and speaker → run `speaker-test` (try `z`, `m`, `n`, `p`).
3. Wire the switch (GPIO 2).
4. Follow [07 — Runbook](../07-operations-runbook.md): `secrets.h`, upload `nani-full`, run
   `start-nani.bat`, press the switch.

## Why the mini results differ from the real ones

| Mini | Real | Why |
|---|---|---|
| speech found at exactly 1.00–2.00 s | real speech has soft starts and pauses | real voices aren't a clean 300 Hz note |
| first sentence at 0.5 s | first words 3.4–3.8 s | a real AI needs time to hear and think; MP3 decoding adds ~0.4 s |
| no crackle | crackle above volume 0.60 | a real 40 mm speaker has physical limits |

## Exercises (easiest first)

1. Change `END_SILENCE_MS` to 300 and re-run chapter 2. What happens to slow speakers? Why is 700 a compromise?
2. Set `CUTOFF_HZ = 1000` in chapter 3. Which notes still come through? Would speech still be clear?
3. Add a `SAY1` tag to chapter 5 for "website speech" and make the toy print it differently.
4. In chapter 5, make `fake_website()` send a `{"t": "fallback"}` with no sentences, and make the bridge
   send an apology instead (the real bridge says "Sorry beta, Nani cannot reach her brain right now").
5. Hardware: connect the amp's GAIN pin to GND (+3 dB) and find the new highest clean volume with `speaker-test`.
6. Hard: make the ESP32 call the website directly (HTTPS + MP3 decoding), removing the laptop. This is
   roadmap item R6 in [10 — Known issues](../10-known-issues-roadmap.md).
