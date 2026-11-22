# ADR-0008: Wi-Fi details in a git-ignored `secrets.h`

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-22 |
| **Related** | [secrets.example.h](../../firmware/nani-full/secrets.example.h), [.gitignore](../../.gitignore) |

## Context
During development the Wi-Fi name and password were written into the sketch. A public repository must
not contain them.

## Decision
The sketch includes `secrets.h`, which is listed in `.gitignore`. The repository ships
`secrets.example.h` with placeholders; builders copy it.

## Alternatives considered
| Option | Why not |
|---|---|
| Placeholders inside the `.ino` | easy to commit real values by mistake |
| Wi-Fi provisioning (captive portal / BLE) | more code; good later for a real product |

## Evidence
Before the first commit, a search of all tracked files found no Wi-Fi password, and `git check-ignore`
confirmed `secrets.h` is ignored.

## Consequences
A fresh clone does not compile until `secrets.h` is created; the compiler names the missing file.
