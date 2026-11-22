# Development measurements (2026-11-20 → 2026-11-22)

Command output recorded during development, copied verbatim. Listening results
("clean", "crackles") are what the builder heard on the real speaker. Re-runnable
checks live in [`tests/run_tests.py`](../../tests/run_tests.py) (output:
[test-output.txt](test-output.txt)).

## M1. USB mic stream: broken packets, then fixed
Bug: the firmware wrote with `setTxTimeoutMs(0)` into a small USB buffer, so packets were cut.
```
before:  bytes 54080  packets 206  (~52/s, expected 50/s)        # headers every ~262 bytes, not 644
after:   bytes 135278 in 4 s (expected ~128800)   headers 210
         gap between headers -> count: {644: 209} (all should be 644)
         rms 2769  peak 18238  lag-1 corr 0.991 (real sound > 0.5)
```
Fix: `Serial.setTxBufferSize(4096)` + send a packet only if `availableForWrite() >= 644`.

## M2. "Static" on the speaker: where it came from
```
preview: quietest 10% of the sentence rms 0 ... -> noise -90 dBFS (below -60 = no audible hiss in the file)
```
| Test | Heard | Meaning |
|---|---|---|
| `z`: amp on, sending pure zeros | silent | not power / ground noise |
| sentence at volume 0.30 | hiss / static | — |
| sentence at volume 0.10 | clean | overdrive of the 40 mm speaker |
| melody, low octave (262–523 Hz) | first note (262 Hz) static | low notes distort first |
| melody, middle octave (523–1047 Hz) | clean | — |
| steady 250 Hz tone | static | confirms low-frequency overdrive |

## M3. Bass-cut (high-pass) filter response
```
  freq    280 Hz cut   400 Hz cut
   125 Hz    -14.2 dB     -20.3 dB
   200 Hz     -6.9 dB     -12.3 dB
   262 Hz     -3.6 dB      -8.1 dB
   300 Hz     -2.5 dB      -6.2 dB
   400 Hz     -0.9 dB      -3.0 dB
   523 Hz     -0.3 dB      -1.3 dB
   800 Hz     -0.1 dB      -0.3 dB
  1000 Hz     -0.0 dB      -0.1 dB
  2000 Hz     -0.0 dB      -0.0 dB
```

## M4. Clean volume limit (listening tests)
| Setup | Loudest clean | First crackle |
|---|---|---|
| no filter | 0.10 | 0.30 |
| 280 Hz bass cut | 0.25 | 0.30 |
| 400 Hz bass cut | 0.30 (limit at the time) | — |
| 400 Hz + 1000 µF across amp VIN/GND | 0.60 (limit at the time) | — |

`volume` scales a sentence whose peak is 28000/32768; `0.8` = full digital level.

## M5. Loudness boost (speech compression) on the greeting sentence
```
gentle (thresh -26 dB, ratio 4):  Loudness: -18.2 dB -> -15.9 dB  (+2.4 dB louder at the same peak)
round off top  0.0% of peaks: +5.0 dB louder
round off top  0.1% of peaks: +6.8 dB louder
round off top  0.5% of peaks: +7.7 dB louder      <- chosen
round off top  1.0% of peaks: +8.3 dB louder
round off top  2.0% of peaks: +9.0 dB louder
final, 280 Hz cut:  Loudness: -18.2 dB -> -11.2 dB  (+7.1 dB louder at the same peak)
final, 400 Hz cut:  Loudness: -19.7 dB -> -11.8 dB  (+7.9 dB louder at the same peak)
```

## M6. Offline laptop brain (Whisper + Ollama qwen3 + Zira), fake toy
```
{'HRD1': 'What color is a banana?', 'ANS1': "A banana is yellow, beta. But when it's ripe, it can also be
 a little brown. Let me show you!", 'RPL1_s': 8.304625, 'secs': 13.05448603630066, 'peak': 28000}
```
CPU only (no GPU), 15.4 GB RAM. 13.1 s question → full answer.

## M7. First real turn through the website's `/api/turn`
```
took 7.2 s   session c1f6ea46
heard : 'What color is a banana?'
answer: 'Aarav beta, banana pila hota hai! Yellow! Tere paas aur kaunsa yellow fruit hai?'
reply audio: 7.00 s, peak 28000
```

## M8. Sentence streaming: buffering bug and fix (fake website sends heard 0.5 s, sentences 2.5/4.5/6.5 s)
| Event | Website sends | Toy received, `iter_lines()` | Toy received, `iter_content(None)` |
|---|---|---|---|
| heard | 0.5 s | 2.8 s | 0.8 s |
| first sentence | 2.5 s | 4.9 s | 2.9 s |
| last sentence | 6.5 s | 7.0 s | 6.9 s |

## M9. Website audio hook on the real stage page (hidden Edge)
```
woke the stage page
sounds the page played by itself in 8 s: 0
total captured: 1
  page sample rate 48000 Hz -> toy audio 1.00 s, peak 28000, main pitch 1000 Hz   # injected test tone
```

## M10. Flash usage of nani-full as features were added (1,310,720 bytes available)
| Version | Bytes | % |
|---|---|---|
| record + parrot, Wi-Fi | 1,112,362 | 84 |
| + filler, streaming | 1,162,618 | 88 |
| + offline clip, switch | 1,221,578 | 93 |
