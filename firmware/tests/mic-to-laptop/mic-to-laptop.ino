// Tutor Grandma · mic-to-laptop
// Board: ESP32-S3 DevKitC-1 N16R8 · Arduino-ESP32 core 3.x · USB CDC on boot enabled
// Pins: same as bench-test (mic SCK 4, WS 5, SD 6 · eyes 9-11 and 12-14)
//
// Two output modes, eyes BLUE in both:
//  TEXT  (default): prints "level:<rms>,peak:<peak>" 10 times a second. Readable in the
//        Arduino Serial Monitor, and drawn as a live graph in Tools > Serial Plotter.
//  AUDIO: streams the mic to the laptop, which plays it (run play_mic.py on the laptop).
// Switch by sending one letter: 'A' = audio, 'T' = text. play_mic.py sends 'A' itself.
//
// AUDIO wire format: every 20 ms one packet = 4-byte header A5 5A 4D 43 ("..MC")
// followed by 320 samples, 16-bit signed, little-endian, mono, 16 kHz.
// No text is printed in AUDIO mode, so text never mixes into the audio.

#include <Arduino.h>
#include "driver/i2s_std.h"

#if !ARDUINO_USB_CDC_ON_BOOT
#error "In Arduino IDE set Tools > USB CDC On Boot > Enabled (otherwise Serial goes to the UART pins, not the USB cable)"
#endif

static const int MIC_SCK = 4, MIC_WS = 5, MIC_SD = 6;
static const int EYE_L[3] = {9, 10, 11};    // R, G, B
static const int EYE_R[3] = {12, 13, 14};   // R, G, B
static const bool COMMON_ANODE = false;     // set true if the eye colours look inverted

static const uint32_t RATE = 16000;
static const int FRAME = 320;               // 20 ms
static const int MIC_SHIFT = 14;            // 32-bit mic word >> this = 16-bit sample
static const uint8_t HEADER[4] = {0xA5, 0x5A, 0x4D, 0x43};

i2s_chan_handle_t micCh = nullptr;
static int32_t micRaw[FRAME];
static int16_t pcm[FRAME];
float dcX = 0, dcY = 0;                     // DC-blocking filter state
bool audioMode = false;                     // false = TEXT, true = AUDIO
float sumSq = 0; int peakAbs = 0, frames = 0, samplesInSum = 0;

void eyes(uint8_t r, uint8_t g, uint8_t b) {
  uint8_t v[3] = {r, g, b};
  for (int i = 0; i < 3; i++) {
    ledcWrite(EYE_L[i], COMMON_ANODE ? 255 - v[i] : v[i]);
    ledcWrite(EYE_R[i], COMMON_ANODE ? 255 - v[i] : v[i]);
  }
}

bool micStart() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  if (i2s_new_channel(&cc, nullptr, &micCh) != ESP_OK) return false;
  i2s_std_config_t sc = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(RATE),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = (gpio_num_t)MIC_SCK,
      .ws = (gpio_num_t)MIC_WS,
      .dout = I2S_GPIO_UNUSED,
      .din = (gpio_num_t)MIC_SD,
      .invert_flags = {.mclk_inv = false, .bclk_inv = false, .ws_inv = false},
    },
  };
  sc.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;   // mic L/R pin to GND
  if (i2s_channel_init_std_mode(micCh, &sc) != ESP_OK) return false;
  return i2s_channel_enable(micCh) == ESP_OK;
}

void setup() {
  Serial.setTxBufferSize(4096);              // room for several packets (default is too small)
  Serial.begin(115200);
  Serial.setTxTimeoutMs(0);                  // never stall if the laptop isn't reading
  for (int i = 0; i < 3; i++) {
    ledcAttach(EYE_L[i], 5000, 8);
    ledcAttach(EYE_R[i], 5000, 8);
  }
  bool ok = micStart();
  eyes(ok ? 0 : 150, 0, ok ? 150 : 0);       // blue = listening, red = mic failed
  delay(1500);
  Serial.println(ok ? "mic-to-laptop ready. TEXT mode: speak and watch the level. Send A for audio, T for text."
                    : "ERROR mic did not start");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'A' || c == 'a') audioMode = true;
    else if (c == 'T' || c == 't') { audioMode = false; Serial.println("TEXT mode"); }
  }

  size_t bytes = 0;
  if (!micCh || i2s_channel_read(micCh, micRaw, sizeof(micRaw), &bytes, 100) != ESP_OK) return;
  size_t n = bytes / 4;
  for (size_t i = 0; i < n; i++) {
    float x = (float)(micRaw[i] >> MIC_SHIFT);
    dcY = x - dcX + 0.995f * dcY;            // remove the mic's DC offset
    dcX = x;
    pcm[i] = (int16_t)constrain((int32_t)dcY, (int32_t)-32768, (int32_t)32767);
  }
  if (n != (size_t)FRAME) return;

  if (audioMode) {
    // Send a packet only if all of it fits, so the laptop never gets half a packet.
    // If it doesn't fit, this 20 ms is skipped whole.
    if (Serial && Serial.availableForWrite() >= 4 + FRAME * 2) {
      Serial.write(HEADER, 4);
      Serial.write((const uint8_t *)pcm, FRAME * 2);
    }
    return;
  }

  // TEXT mode: one line every 5 frames (100 ms)
  for (size_t i = 0; i < n; i++) {
    sumSq += (float)pcm[i] * pcm[i];
    peakAbs = max(peakAbs, abs((int)pcm[i]));
  }
  samplesInSum += n;
  if (++frames >= 5) {
    int rms = (int)sqrtf(sumSq / samplesInSum);
    if (Serial && Serial.availableForWrite() >= 40) Serial.printf("level:%d,peak:%d\n", rms, peakAbs);
    sumSq = 0; peakAbs = 0; frames = 0; samplesInSum = 0;
  }
}
