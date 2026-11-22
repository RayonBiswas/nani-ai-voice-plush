# 10 — Known issues & roadmap

| | |
|---|---|
| **Document type** | Record |
| **Audience** | Maintainers, reviewers |
| **Last updated** | 2026-11-22 |

Severity: **High** = wrong output or broken entry point · **Medium** = limits the product or misleading ·
**Low** = debt.

## Known issues

| ID | Severity | Issue | Location | Suggested fix |
|---|---|---|---|---|
| K1 | Medium | Toy needs the laptop running `nani_brain.py`; without it Nani only says "Wait beta, I am waking up!" | architecture | call `/api/turn` from the ESP32 directly (HTTPS + MP3 decode), or a small always-on server |
| K2 | Medium | Volume at 0.60 is clean but too quiet for a room; 0.80 is the digital maximum | 40 mm speaker | speaker in a closed box; GAIN pin to GND (+3 dB) or 100 kΩ to GND (+6 dB); 50–66 mm speaker |
| K3 | Medium | LED eyes are wired to 3V3 on the prototype, so the mode colours don't show | wiring | move to GPIO 9–14 with 220 Ω ([03](03-hardware.md)) |
| K4 | Medium | Website reminders on the toy proven only with an injected tone, not a real scheduled reminder | `stage_mirror()` | trigger a reminder from the website's presenter controls and confirm on the toy |
| K5 | Medium | The toy's TCP port 3333 has no authentication: anyone on the same Wi-Fi can connect and play audio | `nani-full.ino:230` | shared secret in the first message, or pair by MAC |
| K6 | Medium | The website protocol was read from its public page code and can change without notice | `site_turn_stream()` | agree a documented device endpoint with the web app owner |
| K7 | Low | The compressor lowers loudness on beeping pure tones (it is tuned for speech) | `brain/make_voice.py` `compress()` | only matters for non-speech clips; skip compression for them |
| K8 | Low | Website `slow_brain` fallback (1 of 5 live turns) | web app | external; the toy says so out loud |
| K9 | Low | The switch is read only between turns; a press during an answer acts after it | `nani-full.ino:549` | check the switch inside `playMono()` |
| K10 | Low | `find_toy()` picks the first device with port 3333 open | `brain/nani_brain.py:311` | send a hello and check the reply before trusting it |
| K11 | Low | Auto-find probes show up as a brief "Brain connected / disconnected" in the Serial Monitor | `brainConnected()` | ignore connections that close immediately |
| ~~K12~~ | Low | ~~Dead code: `parse_turn_stream()` and the play-back fallback `speakReply()`~~ | brain, firmware | **Fixed 2026-11-22**: deleted before the first commit |
| K13 | Low | Flash 93 % full with the default partition | `nani-full` | partition *16M Flash (3MB APP/9.9MB FATFS)* |
| K14 | Low | A new random website session per bridge run | `nani_brain.py:369` | keep one session ID in a small file |
| K15 | Low | `test_compress` needs the Windows Zira voice | `tests/run_tests.py` | skip on non-Windows |
| K16 | Medium | macOS support (`start-nani.sh`, `say` voice, Chrome fallback for the mirror) is written but not yet run on a real Mac | `brain/`, `start-nani.sh` | first run on a colleague's Mac; fix what breaks |

## Roadmap

| Step | Name | Goal | Gate (done when) | Status |
|---|---|---|---|---|
| R1 | Eyes | mode colours visible | blue / purple / red seen during a turn | Next |
| R2 | Volume | clearly audible across a room | clean at a louder level with box / GAIN change | Next |
| R3 | Into the plush | toy form factor | perfboard build inside a 30–35 cm plush, zip access, power bank | Planned |
| R4 | Reminder on the toy | website speech confirmed | a real "paani pi lo" reminder heard from the toy | Planned |
| R5 | "Did you do it?" | confirm tasks | Nani asks, listens, logs yes / re-reminds | Needs web app support |
| R6 | No laptop | stand-alone toy | ESP32 talks to the website directly | Planned |
| R7 | Wispr hackathon version | custom-made plush | — | Planned (separate event) |
