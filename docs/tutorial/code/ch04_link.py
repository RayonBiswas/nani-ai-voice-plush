"""Chapter 04: sending speech and answers between the toy and the laptop.

Mini version of writeMsg()/readExact() in firmware/nani-full/nani-full.ino and
send_msg()/recv_exact() in brain/nani_brain.py.
Every message = 4-letter tag + 4-byte length (little-endian) + the data.
Run:  python ch04_link.py
"""
import socket
import struct


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


if __name__ == "__main__":
    toy, laptop = socket.socketpair()            # two ends of one connection, on this computer
    send_msg(laptop, b"ANS1", "Shabaash beta!".encode())
    send_msg(laptop, b"END1", b"")
    print(recv_msg(toy))
    print(recv_msg(toy))
