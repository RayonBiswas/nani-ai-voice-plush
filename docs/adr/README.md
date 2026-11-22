# Architecture Decision Records

One file per significant decision (Nygard format + an **Evidence** section). Copy
[template.md](template.md) for a new one.

| ADR | Title | Status | Date |
|---|---|---|---|
| [0001](0001-dev-kits-and-i2s-audio.md) | Dev kits + I2S mic + MAX98357A, no custom PCB | Accepted | 2026-11-20 |
| [0002](0002-laptop-bridge-architecture.md) | Toy is a thin client; a laptop bridge does the heavy work | Accepted | 2026-11-21 |
| [0003](0003-reuse-website-api-turn.md) | Reuse the website's `/api/turn` instead of a second AI | Accepted | 2026-11-21 |
| [0004](0004-filler-and-sentence-streaming.md) | Instant filler + play the answer sentence by sentence | Accepted | 2026-11-21 |
| [0005](0005-speaker-bass-cut-and-compression.md) | 400 Hz bass cut + speech compression + 1000 µF capacitor | Accepted | 2026-11-21 |
| [0006](0006-mirror-stage-page-audio.md) | Website speech on the toy by mirroring the stage page's audio | Accepted | 2026-11-21 |
| [0007](0007-edge-triggered-latching-switch.md) | Edge-triggered latching switch; start asleep | Accepted | 2026-11-21 |
| [0008](0008-wifi-secrets-file.md) | Wi-Fi details in a git-ignored `secrets.h` | Accepted | 2026-11-22 |
