# 0 — The big picture

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners |
| **Last updated** | 2026-11-22 |

## The story

Aarav is four. His Nani (grandmother) lives far away, so his parents use a web app where an AI "Nani"
chats with him in Hindi and English, teaches him letters, and reminds him to drink water. But a four-year-old
doesn't want a screen. He wants something to **hug and talk to**.

So we put Nani inside a soft toy. Aarav presses its switch, says *"Nani, apple kaunse colour ka hota hai?"*,
the toy says *"Hmm, let me think!"*, and a few seconds later Nani answers from the toy's chest.

## What has to happen, step by step

```mermaid
flowchart LR
    A[1. Hear<br/>mic records] --> B[2. Notice the end<br/>child stopped talking]
    B --> C[3. Send<br/>over Wi-Fi]
    C --> D[4. Think<br/>the AI answers]
    D --> E[5. Send back<br/>sentence by sentence]
    E --> F[6. Speak<br/>clean, loud enough]
```

| Step | Who does it | Chapter |
|---|---|---|
| 1–2 Hear and notice the end | the toy's chip (ESP32-S3) | [2](02-hearing.md) |
| 6 Speak cleanly | the toy's chip + amplifier + speaker | [3](03-speaking.md) |
| 3, 5 Send and receive | toy ↔ laptop over Wi-Fi | [4](04-talking-over-wifi.md) |
| 4 Think | the web app's AI, reached through a laptop "bridge" | [5](05-the-bridge.md) |

## Why a laptop in the middle?

The ESP32 is a tiny computer (it costs about ₹750). It's great at reading a mic and driving a speaker, but
far too small to understand speech or run an AI. So the toy does the "ears and mouth", and a small Python
program on a laptop (the **bridge**) talks to the web app, which does the "brain". The web app already
knows Aarav (his favourite fruit, what he learned this week), so the toy gets the *same* Nani.

## What you won't need to understand in advance

No electronics theory, no signal-processing maths. Every idea is introduced when you need it, with an
everyday analogy first. Next: [1 — Setup](01-setup.md).
