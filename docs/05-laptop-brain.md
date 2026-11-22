# 05 — Laptop brain (`brain/nani_brain.py`)

| | |
|---|---|
| **Document type** | Reference |
| **Audience** | Developers running or changing the bridge |
| **Last updated** | 2026-11-22 |

The bridge between the toy and the Tutor Grandma website. Started by double-clicking
[`start-nani.bat`](../start-nani.bat), which restarts it if it ever exits.

## 1. Command line

| Option | Default | Meaning |
|---|---|---|
| `--host` | `auto` | toy IP; `auto` tries every address of the laptop's network for port 3333 |
| `--port` | `3333` | toy's TCP port |
| `--site` | `https://tutor-grandma.vercel.app` | website whose `/api/turn` answers |
| `--offline` | off | ignore the website; use Whisper + Ollama + Zira on the laptop |
| `--no-mirror` | off | don't forward the website's own speech (reminders, songs) |
| `--show` | off | show the hidden stage page window (debugging the mirror) |
| `--llm` | `qwen3` | Ollama model for `--offline` |
| `--whisper` | `small.en` | speech model for `--offline` (`small` = Hindi too, downloads ~480 MB once) |

## 2. Website mode (default)

### Answering the child — `site_turn_stream()`
1. Wrap the toy's PCM in a WAV file (`to_wav_bytes`).
2. `POST {site}/api/turn` as multipart: `audio=turn.wav`, `sessionId` (random UUID per run),
   `board={"spell":null,"showing":null}`, `lastEvent=null`, `clockOffsetMs=0`.
   These are the same fields the website's own toy page sends.
3. Read the reply **as it arrives**: `iter_content(chunk_size=None)` + split on newlines.
   (`iter_lines()` was tried first; it waits to fill a 512-byte buffer and held every event back
   until the next one arrived, see [M8](evidence/development-measurements.md).)
4. For each `say` event: base64 → MP3 → `ffmpeg` → 16 kHz mono → `for_speaker()` (bass cut +
   compression) → send `ANS1` + `RPL1` to the toy straight away.
5. `fallback` with no audio (e.g. `slow_brain`) or any error → the toy says
   "Sorry beta, Nani cannot reach her brain right now. Try again?".
6. Always finish with `END1`.

Console output per turn:
```
Aarav: Apple कौन से color का होता है?   [heard at 1.9 s]
Nani : Apple laal, hara,   [piece 1 at 3.5 s, 2.5 s long]
Nani : ya peela ho sakta hai, beta!   [piece 2 at 3.9 s, 2.4 s long]
Nani : Tera favourite kaunsa colour hai?   [piece 3 at 4.3 s, 2.4 s long]
       (answer complete in 8.9 s)
```
([live session log](evidence/live-session-2026-11-21.txt))

### Website speech on the toy — `stage_mirror()`
The website's reminders are fired by its **stage page in a browser**, not by a server. So the bridge
opens that page itself:

1. Playwright launches the installed **Microsoft Edge**, headless, with `--mute-audio` and a fake
   microphone.
2. An init script (`HOOK_JS`) wraps `AudioBufferSourceNode.prototype.start`: every sound the page
   starts is copied (mono float32 + its sample rate, honouring offset/duration) to Python via
   `expose_binding("__naniToToy")`.
3. The page is woken by clicking "Tap to wake Nani" (unlocks its audio).
4. Copies go into a queue. The main loop sends them as `SAY1` + `RPL1` + `END1` **only while no
   conversation is running** (`select()` with a 0.2 s timeout). Sounds shorter than 0.2 s are dropped.
5. The queue is emptied on every (re)connection, so old reminders are not replayed.

⚠️ Run only **one** stage page (close other stage tabs), otherwise reminders fire and are logged twice.

### Finding the toy — `find_toy()`
Learns the laptop's own address, then tries `x.x.x.1 … x.x.x.254` on port 3333 with 64 threads and
a 0.6 s timeout. Measured: 1.2–2.5 s ([test output](evidence/test-output.txt)). It survives the router
giving the toy a new address (it changed from `.87` to `.187` during testing).

## 3. Offline mode (`--offline`)

| Step | Tool | Notes |
|---|---|---|
| Hear | faster-whisper `small.en`, CPU int8 | English only unless `--whisper small` |
| Think | Ollama `qwen3`, `think: false`, ≤ 80 tokens, last 8 messages | started automatically (`ollama serve`) if not running |
| Speak | Windows "Microsoft Zira" via `System.Speech`, then bass cut + compression | English voice |

Nani's offline persona prompt: warm Indian grandmother, 1–2 short sentences under 30 words,
simple English, may say "beta", no emojis or lists, and *"you are a toy: you cannot see, show,
move or fetch anything"* (added after the model offered to "show" a banana).

Measured: 13.1 s from question to full answer on this CPU-only laptop ([M6](evidence/development-measurements.md)).

## 4. `make_voice.py` — voice clips for the firmware

```powershell
python brain/make_voice.py "Good night Aarav!"                       # greeting -> nani_voice.h
python brain/make_voice.py "Hmm, let me think!" --name FILLER        # -> nani_filler.h
python brain/make_voice.py "Wait beta, I am waking up!" --name OFFLINE --speed 1
```
Pipeline: Windows Zira TTS (16 kHz) → trim silence (keep 50 ms) → 400 Hz bass cut → compression
(threshold −26 dB, ratio 4:1, 5 ms attack, 80 ms release) → soften the top 0.5 % of peaks →
peak 28000 → C array. The greeting is written to `firmware/nani-full/` and
`firmware/tests/speaker-test/`; other clips only to `nani-full`. A preview WAV goes to `recordings/`.
Then re-upload the sketch.

## 5. Tools for the test sketches (`tools/`)

| Script | Pairs with | Does |
|---|---|---|
| `play_mic.py --port COM7` | `mic-to-laptop` | plays the toy's mic on the laptop speaker (sends `A` to switch the sketch to audio mode) |
| `record_wav.py --seconds 5` | `mic-to-laptop` | saves the mic to `recordings/rec_<time>.wav` |
| `play_wifi.py --host <ip> [--save]` | `mic-wifi` | plays the mic over Wi-Fi, 200 ms jitter buffer |
