# References

| | |
|---|---|
| **Document type** | Reference |
| **Audience** | Engineers |
| **Last updated** | 2026-11-22 |

| # | Reference | Supports |
|---|---|---|
| 1 | Espressif, *ESP32-S3-DevKitC-1 User Guide* (docs.espressif.com) | pin header layout, strapping pins, PSRAM pins avoided in [03](03-hardware.md) |
| 2 | Espressif, *ESP-IDF I2S driver, standard mode* (`driver/i2s_std.h`) | mic and amp setup in the firmware |
| 3 | Espressif, *arduino-esp32* core 3.x (github.com/espressif/arduino-esp32) | `ledcAttach`, `HWCDC`, `WiFiServer` APIs used |
| 4 | Analog Devices / Maxim, *MAX98357A datasheet* | 2.5–5.5 V supply, SD pin modes, GAIN pin settings (9/12/15 dB) |
| 5 | TDK InvenSense, *INMP441* and *ICS-43434* datasheets | 24-bit I2S output, L/R select, 3.3 V supply |
| 6 | R. Bristow-Johnson, *Audio EQ Cookbook* | biquad high-pass coefficients used in firmware and `make_voice.py` |
| 7 | SYSTRAN, *faster-whisper* (github.com/SYSTRAN/faster-whisper) | offline speech-to-text |
| 8 | Ollama (ollama.com) and the Qwen3 model | offline answers |
| 9 | Microsoft, *System.Speech.Synthesis* | Windows Zira voice clips |
| 10 | Microsoft, *Playwright for Python* (playwright.dev/python) | hidden Edge window and `expose_binding` for the mirror |
| 11 | MDN, *AudioBufferSourceNode.start()* | the function hooked to copy the stage page's audio |
| 12 | Tutor Grandma web app (tutor-grandma.vercel.app) by Hrishikesh Hundekari | `/api/turn` behaviour, stage page |
| 13 | M. Nygard, *Documenting Architecture Decisions* (2011) | ADR format |
| 14 | *Keep a Changelog* (keepachangelog.com) | `CHANGELOG.md` format |
| 15 | Diátaxis (diataxis.fr), arc42 (arc42.org) | documentation structure |
