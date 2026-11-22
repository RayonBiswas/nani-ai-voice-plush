# 07 — Operations runbook

| | |
|---|---|
| **Document type** | How-to |
| **Audience** | Anyone setting up or demoing the toy |
| **Last updated** | 2026-11-22 |

## 1. One-time setup: laptop

```powershell
git clone https://github.com/RayonBiswas/nani-ai-voice-plush.git
cd nani-ai-voice-plush
pip install -r requirements.txt
ffmpeg -version          # must print a version; install from https://ffmpeg.org if not
```
Microsoft Edge or Google Chrome must be installed (the website mirror uses it); otherwise run
`python -m playwright install chromium` once.

**macOS:** `brew install ffmpeg`, `python3 -m pip install -r requirements.txt`, `chmod +x start-nani.sh`.
The fallback voice uses macOS `say` instead of the Windows Zira voice. The macOS path is written but not yet
tested on a real Mac (known issue K16).
Success signal: `pip` finishes without errors.

## 2. One-time setup: Arduino IDE

1. Install Arduino IDE 2.x and the **esp32 by Espressif** board package (3.x) from Boards Manager.
2. Tools menu, every time you upload:

| Setting | Value |
|---|---|
| Board | ESP32S3 Dev Module |
| USB CDC On Boot | **Enabled** (else the Serial Monitor shows nothing; the sketch refuses to compile) |
| PSRAM | **OPI PSRAM** (N16R8) |
| Port | the COM port of the board (e.g. COM7) |

## 3. Flash the toy

```powershell
copy firmware\nani-full\secrets.example.h firmware\nani-full\secrets.h
notepad firmware\nani-full\secrets.h      # put a 2.4 GHz Wi-Fi name and password
```
Open `firmware/nani-full/nani-full.ino` → **Upload**. ~1–2 min the first time.
Serial Monitor at **115200** should show:
```
======== NANI FULL TEST ========
Mic: OK   Amp: OK
PSRAM: yes, max recording 8 s, max answer 15 s
Wi-Fi: connected. ...
*** Nani is ASLEEP (press the switch to wake her) ***
```

## 4. Run a demo

1. Toy on the power bank (or USB).
2. Double-click **`start-nani.bat`** (macOS: `./start-nani.sh`). Wait for `Connected. Talk to Nani!` and
   `Website mirror: stage page is open`.
3. Press the switch → greeting. Ask a question, pause → "Hmm…" → Nani answers.
4. Press the switch again to put her to sleep; close the window to stop the bridge.

Runtimes: bridge start ~5–15 s (finding the toy + opening the stage page); answers start ~3.5 s
after the speech reaches the laptop.

## 5. Hardware checks, one part at a time

Do these in order when building. Each is a separate sketch in `firmware/tests/`.

### 5.1 Mic — `mic-test`
Upload, open the Serial Monitor. It runs three checks and then a live meter:
```
[1/3] WIRING CHECK   PASS: mic is sending data on the LEFT slot
[2/3] QUIET CHECK    Room noise: -70 dB   OK
[3/3] VOICE CHECK    PASS: the mic clearly picks up your voice
 -41.5 dB |########################                | VOICE
```
Type `r` to repeat. A FAIL prints what to check (VDD on 3V3, SD on GPIO 6, L/R to GND).

### 5.2 Speaker — `speaker-test`
On start: 3 beeps and the sentence. Then type letters:

| Key | Plays | Use it to |
|---|---|---|
| `b` | 3 beeps | basic amp + speaker check |
| `2` / `3` | 440 / 1000 Hz tone | listen for crackle |
| `m` `n` `o` | melody low / middle / high octave | find where the speaker gets clean |
| `s` | sweep 150 → 6000 Hz | speaker range |
| `v` | the sentence | real speech |
| `z` | 4 s of digital silence, amp on | hiss here = power / ground problem |
| `p` | record 3 s, play back | full mic → speaker path |
| `+` / `-` | volume | find the clean maximum |

### 5.3 Mic to laptop — `mic-to-laptop` (USB)
```powershell
python tools\play_mic.py --port COM7 --gain 1     # hear the mic on the laptop
python tools\record_wav.py --seconds 5            # save recordings\rec_<time>.wav
```
Close the Arduino Serial Monitor first. In the Serial Monitor this sketch prints `level:…,peak:…`
(also works in the Serial Plotter).

### 5.4 Mic over Wi-Fi — `mic-wifi`
Put Wi-Fi in the sketch, upload, read the IP in the Serial Monitor, then:
```powershell
python tools\play_wifi.py --host 192.168.0.187 [--save]
```

## 6. Change what Nani says from flash

```powershell
python brain\make_voice.py "Hello Aarav, I missed you!"          # greeting
python brain\make_voice.py "Hmm, let me think!" --name FILLER
```
Then re-upload `nani-full`. Listen first: `recordings\nani_voice_preview.wav`.

## 7. Automated checks

```powershell
python tests\run_tests.py
```
~15 s; ends with `6/6 passed`. No hardware or website needed (uses fakes and the Windows Zira voice).

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Compile error: *USB CDC On Boot* | IDE setting | Tools → USB CDC On Boot → Enabled |
| Compile error: `secrets.h: No such file` | Wi-Fi file not created | copy `secrets.example.h` to `secrets.h` |
| `Failed uploading: no upload port provided` | no port selected | Tools → Port → the COM port |
| Upload: `port is busy` / `Access is denied` | Serial Monitor or a Python tool holds the port | close it; unplug/replug ends stuck Python tools |
| Upload can't connect | sketch owns the USB port | hold BOOT, tap RESET, release BOOT, upload |
| `Wi-Fi: failed` | 5 GHz network or wrong password | use the 2.4 GHz SSID (e.g. `sra`, not `sra_5G`) |
| Bridge: `not found yet` | toy off, or on another network | check the Serial Monitor shows Wi-Fi connected; same Wi-Fi as the laptop |
| Bridge: `getaddrinfo failed` / `refused` | a wrong `--host` was typed | run without `--host` (auto-find) |
| Toy says "Wait beta, I am waking up!" | bridge not connected | start `start-nani.bat` |
| Toy says "Nani cannot reach her brain" | website slow (`slow_brain`) or offline | ask again; check the website opens in a browser |
| Static / crackle on loud speech | speaker overdriven | `-` to lower volume; check the 1000 µF capacitor |
| Hiss even in `z` test | power / ground | short GND wire from amp to ESP32, capacitor, try laptop USB power |
| Toy dies after a while on the power bank | power bank auto-off at low current | power bank with "always on" mode |
| Reminders play twice / logged twice | two stage pages open | close other stage tabs |
| Eyes always on | LEDs on 3V3 instead of GPIO | wire to GPIO 9–14 (see [03](03-hardware.md)) |
| Eyes show wrong colours | common-anode LEDs | type `a` in the Serial Monitor |
