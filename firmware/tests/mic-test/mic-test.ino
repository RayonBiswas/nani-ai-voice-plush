// Nani · MIC TEST (open in Arduino IDE, results in Serial Monitor at 115200)
// Board: ESP32-S3 (Tools > Board > "ESP32S3 Dev Module"), Tools > USB CDC On Boot: Enabled
// Mic: INMP441 or ICS-43434 (I2S)
//   VDD -> 3V3    GND -> GND    L/R (SEL) -> GND
//   SCK (BCLK) -> GPIO4    WS (LRCL) -> GPIO5    SD (DOUT) -> GPIO6
//
// What it does:
//  1. Wiring check: is the mic sending any real data at all?
//  2. Quiet check: measures the room noise for 2 s (stay quiet)
//  3. Voice check: you speak for 4 s, it says PASS or FAIL
//  4. Live meter: a level bar every 0.1 s, says VOICE when it hears you
// Type r in the Serial Monitor (then Enter) to run the checks again.

#include <Arduino.h>
#include <math.h>
#include "driver/i2s_std.h"

static const int MIC_SCK = 4, MIC_WS = 5, MIC_SD = 6;
static const uint32_t RATE = 16000;
static const int N = 1600;                 // 0.1 s of audio per reading

i2s_chan_handle_t mic = nullptr;
bool rightSlot = false;
static int32_t raw[N];
float floorRms = 0;

// ---------- mic setup ----------
bool micStart(bool useRight) {
  if (mic) { i2s_channel_disable(mic); i2s_del_channel(mic); mic = nullptr; }
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
  sc.slot_cfg.slot_mask = useRight ? I2S_STD_SLOT_RIGHT : I2S_STD_SLOT_LEFT;
  if (i2s_channel_init_std_mode(mic, &sc) != ESP_OK) return false;
  if (i2s_channel_enable(mic) != ESP_OK) return false;
  rightSlot = useRight;
  delay(100);
  return true;
}

// Reads 0.1 s. Fills raw[], returns number of samples.
int readBlock() {
  size_t bytes = 0, got = 0;
  while (got < sizeof(raw)) {
    if (i2s_channel_read(mic, (uint8_t *)raw + got, sizeof(raw) - got, &bytes, 300) != ESP_OK || bytes == 0) break;
    got += bytes;
  }
  return got / 4;
}

// Loudness of a block, with the DC offset removed. 24-bit audio sits in the top of each 32-bit word.
float blockRms(int n, int *peakOut) {
  if (n == 0) { if (peakOut) *peakOut = 0; return 0; }
  double sum = 0;
  for (int i = 0; i < n; i++) sum += (raw[i] >> 8);
  double mean = sum / n, e = 0;
  int peak = 0;
  for (int i = 0; i < n; i++) {
    double v = (raw[i] >> 8) - mean;
    e += v * v;
    peak = max(peak, (int)fabs(v));
  }
  if (peakOut) *peakOut = peak;
  return sqrt(e / n);
}

// dB relative to a full-scale 24-bit sample (0 dB = loudest possible)
float toDb(float rms) { return 20.0f * log10f(max(rms, 1.0f) / 8388608.0f); }

// ---------- step 1: wiring ----------
// Returns true if the current slot carries real, changing data.
bool dataLooksReal(bool verbose) {
  int zeros = 0, ones = 0, total = 0;
  int32_t lo = INT32_MAX, hi = INT32_MIN;
  for (int b = 0; b < 5; b++) {
    int n = readBlock();
    for (int i = 0; i < n; i++) {
      int32_t v = raw[i];
      if (v == 0) zeros++;
      if (v == -1) ones++;
      lo = min(lo, v); hi = max(hi, v);
      total++;
    }
  }
  if (verbose) {
    Serial.printf("   %s slot: %d samples, %d%% zero, %d%% all-ones, raw range %ld .. %ld\n",
                  rightSlot ? "RIGHT" : "LEFT", total, total ? zeros * 100 / total : 0,
                  total ? ones * 100 / total : 0, (long)lo, (long)hi);
  }
  if (total == 0) return false;
  if (zeros * 100 / total > 95) return false;   // nothing coming in
  if (ones * 100 / total > 95) return false;    // data line stuck high
  if (lo == hi) return false;                   // stuck at one value
  return true;
}

bool wiringCheck() {
  Serial.println("\n[1/3] WIRING CHECK");
  if (!micStart(false)) { Serial.println("   FAIL: could not start I2S on the ESP32"); return false; }
  if (dataLooksReal(true)) { Serial.println("   PASS: mic is sending data on the LEFT slot"); return true; }

  Serial.println("   No data on LEFT, trying RIGHT (L/R pin may be tied to 3V3)...");
  micStart(true);
  if (dataLooksReal(true)) {
    Serial.println("   PASS: mic is sending data on the RIGHT slot (its L/R pin is HIGH; fine, or tie it to GND)");
    return true;
  }
  Serial.println("   FAIL: no real data from the mic on either slot. Check:");
  Serial.println("     - VDD to 3V3 (NOT 5V) and GND connected");
  Serial.println("     - SD/DOUT to GPIO6, SCK/BCLK to GPIO4, WS/LRCL to GPIO5");
  Serial.println("     - L/R (SEL) pin connected to GND, not left floating");
  Serial.println("     - Jumper wires firmly seated; try another mic module if you have one");
  micStart(false);
  return false;
}

// ---------- step 2: room noise ----------
void quietCheck() {
  Serial.println("\n[2/3] QUIET CHECK: stay silent for 2 seconds...");
  delay(500);
  readBlock();                               // drop stale audio
  float acc = 0;
  for (int i = 0; i < 20; i++) acc += blockRms(readBlock(), nullptr);
  floorRms = acc / 20;
  float db = toDb(floorRms);
  Serial.printf("   Room noise: %.1f dB\n", db);
  if (db < -95) Serial.println("   WARNING: suspiciously silent. The mic may be giving almost no signal.");
  else if (db > -40) Serial.println("   WARNING: very loud for a quiet room. Noisy place, loose wire, or noisy power.");
  else Serial.println("   OK: normal room-noise level (about -80 to -55 dB is typical)");
}

// ---------- step 3: voice ----------
bool voiceCheck() {
  Serial.println("\n[3/3] VOICE CHECK: speak normally about 20-30 cm from the mic for 4 seconds");
  Serial.println("   (count 1-2-3-4 or say 'Hello Nani')");
  delay(1500);
  Serial.println("   GO!");
  float best = 0; int bestPeak = 0;
  for (int i = 0; i < 40; i++) {
    int pk;
    float r = blockRms(readBlock(), &pk);
    if (r > best) best = r;
    bestPeak = max(bestPeak, pk);
  }
  float rise = toDb(best) - toDb(floorRms);
  Serial.printf("   Loudest: %.1f dB, that's %.1f dB above room noise\n", toDb(best), rise);
  if (bestPeak >= 8000000) Serial.println("   NOTE: peak hit full scale (clipping). Speak a bit further away.");
  if (rise >= 15) { Serial.println("   PASS: the mic clearly picks up your voice"); return true; }
  if (rise >= 6)  { Serial.println("   WEAK: it hears you, but quietly. Speak closer, check the mic hole isn't covered"); return false; }
  Serial.println("   FAIL: no clear change when you spoke. Check wiring, and that the mic hole faces you");
  return false;
}

void runChecks() {
  Serial.println("\n======== NANI MIC TEST ========");
  bool wiring = wiringCheck();
  quietCheck();
  bool voice = voiceCheck();
  Serial.println("\n---------- RESULT ----------");
  Serial.printf("Wiring: %s   Voice: %s\n", wiring ? "PASS" : "FAIL", voice ? "PASS" : "FAIL/WEAK");
  Serial.println("Live meter below: speak and watch the bar. Type r + Enter to test again.\n");
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 5000) delay(10);   // wait for the Serial Monitor
  delay(500);
  runChecks();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'r' || c == 'R') { runChecks(); return; }
  }
  int pk;
  float r = blockRms(readBlock(), &pk);
  float db = toDb(r);
  int bars = constrain((int)((db + 90.0f) / 2.0f), 0, 40);   // -90 dB = empty, -10 dB = full
  char bar[41];
  for (int i = 0; i < 40; i++) bar[i] = i < bars ? '#' : ' ';
  bar[40] = 0;
  bool voice = r > floorRms * 4.0f && db > -70;
  Serial.printf("%6.1f dB |%s| %s\n", db, bar, voice ? "VOICE" : "quiet");
}
