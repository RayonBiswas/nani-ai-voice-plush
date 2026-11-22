// Nani · MIC OVER WI-FI -> laptop speaker
// Board: Tools > Board > "ESP32S3 Dev Module", Tools > USB CDC On Boot > Enabled
// Mic: SCK -> GPIO4, WS -> GPIO5, SD -> GPIO6, L/R -> GND, VDD -> 3V3
//
// 1. Put your Wi-Fi name and password below (2.4 GHz only: the ESP32 can't see 5 GHz).
// 2. Upload, open Serial Monitor at 115200: it prints the ESP32's IP address.
// 3. On the laptop (same Wi-Fi):  python play_wifi.py            (finds nani.local)
//                            or:  python play_wifi.py --host <IP printed here>
//
// The ESP32 runs a small TCP server on port 3333. When the laptop connects, it streams
// 20 ms packets: header A5 5A 4D 43, then 320 samples of 16-bit little-endian mono 16 kHz.

#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include "driver/i2s_std.h"

#if !ARDUINO_USB_CDC_ON_BOOT
#error "In Arduino IDE set Tools > USB CDC On Boot > Enabled (otherwise the Serial Monitor shows nothing over USB)"
#endif

// ======== CHANGE THESE ========
const char *WIFI_SSID = "YOUR_WIFI_NAME";
const char *WIFI_PASS = "YOUR_WIFI_PASSWORD";
// ==============================

static const char *HOSTNAME = "nani";        // laptop can use nani.local
static const uint16_t PORT = 3333;
static const int MIC_SCK = 4, MIC_WS = 5, MIC_SD = 6;
static const int EYE_L[3] = {9, 10, 11};      // R, G, B (optional LEDs)
static const int EYE_R[3] = {12, 13, 14};
static const uint32_t RATE = 16000;
static const int FRAME = 320;                 // 20 ms
static const int MIC_SHIFT = 14;              // 32-bit mic word >> this = 16-bit sample

WiFiServer server(PORT);
WiFiClient laptop;
i2s_chan_handle_t mic = nullptr;
static int32_t raw[FRAME];
static uint8_t packet[4 + FRAME * 2] = {0xA5, 0x5A, 0x4D, 0x43};
float dcX = 0, dcY = 0;
uint32_t sent = 0, lastReport = 0;
float sumSq = 0; int nSum = 0;

void eyes(uint8_t r, uint8_t g, uint8_t b) {
  uint8_t v[3] = {r, g, b};
  for (int i = 0; i < 3; i++) { ledcWrite(EYE_L[i], v[i]); ledcWrite(EYE_R[i], v[i]); }
}

bool micStart() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  if (i2s_new_channel(&cc, nullptr, &mic) != ESP_OK) return false;
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
  sc.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
  if (i2s_channel_init_std_mode(mic, &sc) != ESP_OK) return false;
  return i2s_channel_enable(mic) == ESP_OK;
}

void connectWifi() {
  Serial.printf("Connecting to Wi-Fi \"%s\"", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                       // no power saving: steadier audio
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  bool blink = false;
  while (WiFi.status() != WL_CONNECTED) {
    eyes(0, 0, (blink = !blink) ? 60 : 0);    // blue blink while connecting
    Serial.print(".");
    delay(500);
    if (millis() - t0 > 20000) {
      Serial.println("\nFAILED. Check the name/password, and that it's 2.4 GHz (not 5 GHz). Retrying...");
      WiFi.disconnect(); delay(1000);
      WiFi.begin(WIFI_SSID, WIFI_PASS);
      t0 = millis();
    }
  }
  Serial.printf("\nConnected! ESP32 IP address: %s  (signal %d dBm)\n",
                WiFi.localIP().toString().c_str(), WiFi.RSSI());
  if (MDNS.begin(HOSTNAME)) Serial.printf("Also reachable as %s.local\n", HOSTNAME);
  server.begin();
  server.setNoDelay(true);
  Serial.printf("On the laptop run:  python play_wifi.py --host %s\n", WiFi.localIP().toString().c_str());
  Serial.println("Waiting for the laptop to connect...");
  eyes(20, 20, 20);
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 4000) delay(10);
  delay(300);
  for (int i = 0; i < 3; i++) { ledcAttach(EYE_L[i], 5000, 8); ledcAttach(EYE_R[i], 5000, 8); }

  Serial.println("\n======== NANI MIC OVER WI-FI ========");
  if (!micStart()) { Serial.println("FAIL: mic did not start"); eyes(150, 0, 0); while (true) delay(1000); }
  Serial.println("Mic started.");
  connectWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { Serial.println("Wi-Fi lost, reconnecting..."); connectWifi(); }

  if (!laptop || !laptop.connected()) {
    if (laptop) { laptop.stop(); Serial.println("Laptop disconnected. Waiting..."); eyes(20, 20, 20); }
    WiFiClient c = server.accept();
    if (c) {
      laptop = c;
      laptop.setNoDelay(true);
      Serial.printf("Laptop connected from %s, streaming mic (eyes blue)\n", laptop.remoteIP().toString().c_str());
      eyes(0, 0, 150);
      sent = 0; lastReport = millis();
    }
  }

  // Always read the mic so audio stays fresh, send it only if a laptop is listening.
  size_t bytes = 0;
  if (i2s_channel_read(mic, raw, sizeof(raw), &bytes, 100) != ESP_OK || bytes != sizeof(raw)) return;
  int16_t *pcm = (int16_t *)(packet + 4);
  for (int i = 0; i < FRAME; i++) {
    float x = (float)(raw[i] >> MIC_SHIFT);
    dcY = x - dcX + 0.995f * dcY;             // remove the mic's DC offset
    dcX = x;
    pcm[i] = (int16_t)constrain((int32_t)dcY, (int32_t)-32768, (int32_t)32767);
    sumSq += (float)pcm[i] * pcm[i];
  }
  nSum += FRAME;

  if (laptop && laptop.connected()) {
    size_t w = laptop.write(packet, sizeof(packet));   // whole packet in one go
    if (w != sizeof(packet)) { Serial.println("Send failed, dropping the connection"); laptop.stop(); eyes(20, 20, 20); return; }
    sent++;
    if (millis() - lastReport >= 2000) {
      Serial.printf("streaming: %u packets/s (want 50), mic level %d, signal %d dBm\n",
                    (unsigned)(sent * 1000 / (millis() - lastReport)), (int)sqrtf(sumSq / nSum), WiFi.RSSI());
      sent = 0; lastReport = millis(); sumSq = 0; nSum = 0;
    }
  } else if (nSum >= (int)RATE) { sumSq = 0; nSum = 0; }
}
