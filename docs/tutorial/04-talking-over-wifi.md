# 4 — Talking over Wi-Fi

| | |
|---|---|
| **Document type** | Tutorial |
| **Audience** | Beginners |
| **Last updated** | 2026-11-22 |

**You will build:** [`code/ch04_link.py`](code/ch04_link.py) · **Full version:** `writeMsg()` /
`readExact()` in [`nani-full.ino`](../../firmware/nani-full/nani-full.ino), `send_msg()` /
`recv_exact()` in [`brain/nani_brain.py`](../../brain/nani_brain.py)

## 💡 Idea

The toy and the laptop are connected by **TCP**, a reliable "pipe" over Wi-Fi: bytes go in at one end and
come out in the same order at the other. But a pipe has no idea where one message ends and the next
begins, like water with no bottles.

So we put every message in a labelled **envelope**:

```
| tag (4 letters) | length (4 bytes) | the data (length bytes) |
```

The reader first reads 8 bytes, learns the tag and how many bytes follow, then reads exactly that many.

| Tag | Means |
|---|---|
| `UTT1` | the child's speech (toy → laptop) |
| `HRD1` | what the AI heard, as text |
| `ANS1` | one sentence of Nani's answer, as text |
| `RPL1` | that sentence's audio |
| `END1` | the answer is finished |

## The code

```python
def send_msg(sock, tag: bytes, payload: bytes):
    assert len(tag) == 4
    sock.sendall(tag + struct.pack("<I", len(payload)) + payload)


def recv_exact(sock, n):
    """TCP may deliver data in pieces, so keep reading until we have exactly n bytes."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("other side closed the connection")
        data += chunk
    return data


def recv_msg(sock):
    tag = recv_exact(sock, 4)
    length = struct.unpack("<I", recv_exact(sock, 4))[0]
    return tag, recv_exact(sock, length)
```

- `"<I"` = an unsigned 32-bit number, **little-endian** (lowest byte first). The ESP32 stores numbers that
  way too, so it can copy the 4 bytes straight into a `uint32_t`.
- `recv_exact` is the important part: one `recv()` may return only part of a message.

## Try it

```powershell
python ch04_link.py
```

## ✅ Check

```
(b'ANS1', b'Shabaash beta!')
(b'END1', b'')
```

## ⚠️ Common mistakes

| Symptom | Cause |
|---|---|
| Garbage text / random audio | read with a single `recv()` and lost the message boundaries |
| Lengths look huge | big-endian vs little-endian mix-up |
| Laptop can't connect to the toy | different networks, or the toy is on 5 GHz Wi-Fi (ESP32 is 2.4 GHz only) |

## In the full project

The **toy is the server** (port 3333) and the laptop connects to it, so the toy never needs the laptop's
address. The laptop finds the toy by trying every address on its network (`find_toy()`), which keeps
working when the router gives the toy a new address. The same envelope idea first fixed a real bug: when
packets were cut short on USB, counting bytes between envelope headers revealed it
([M1](../evidence/development-measurements.md)).

Next: [5 — The bridge](05-the-bridge.md).
