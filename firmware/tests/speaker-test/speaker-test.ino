// Nani · SPEAKER TEST (Arduino IDE, Serial Monitor at 115200)
// Board: Tools > Board > "ESP32S3 Dev Module", Tools > USB CDC On Boot > Enabled
//
// Amp: MAX98357A            Speaker: 3 W, 4 ohm on the amp's + and - screw terminals
//   VIN  -> 5V (VBUS pin)   GND  -> GND
//   BCLK -> GPIO15          LRC  -> GPIO16      DIN -> GPIO17
//   SD   -> GPIO18 (if not wired, leave it floating: the amp is then always on)
//   GAIN -> leave floating (9 dB)
// Mic (for the 'p' parrot test): SCK -> GPIO4, WS -> GPIO5, SD -> GPIO6, L/R -> GND, VDD -> 3V3
//
// On start it plays 3 beeps. Then type a letter + Enter in the Serial Monitor:
//   b  3 beeps            1 2 3 4  tone 250 / 440 / 1000 / 3000 Hz
//   s  sweep low -> high  m / n / o  melody (Sa Re Ga Ma Pa Dha Ni Sa) low / middle / high
//   v  speak the sentence in nani_voice.h (change it: python make_voice.py "new sentence")
//   p  parrot: record 3 s from the mic, play it back
//   +  louder             -  quieter          h  help

#include <Arduino.h>
#include <math.h>
#include "driver/i2s_std.h"
#include "nani_voice.h"     // the sentence, made by: python make_voice.py "your sentence"

#if !ARDUINO_USB_CDC_ON_BOOT
#error "In Arduino IDE set Tools > USB CDC On Boot > Enabled (otherwise the Serial Monitor shows nothing over USB)"
#endif

static const int AMP_BCLK = 15, AMP_LRC = 16, AMP_DIN = 17, AMP_SD = 18;
static const int MIC_SCK = 4, MIC_WS = 5, MIC_SD = 6;
static const uint32_t RATE = 16000;

i2s_chan_handle_t amp = nullptr, mic = nullptr;
float volume = 0.5f;                  // 0.05 .. 0.6 (400 Hz bass cut; 0.5 used in testing with the 1000 uF capacitor)
static int16_t stereo[512];          // 256 stereo frames

// ---------- amp ----------
bool ampStart() {
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
  cc.auto_clear = true;              // silence when nothing is queued (no buzzing)
  if (i2s_new_channel(&cc, &amp, nullptr) != ESP_OK) return false;
  i2s_std_config_t sc = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(RATE),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = (gpio_num_t)AMP_BCLK,
      .ws = (gpio_num_t)AMP_LRC,
      .dout = (gpio_num_t)AMP_DIN,
      .din = I2S_GPIO_UNUSED,
      .invert_flags = {.mclk_inv = false, .bclk_inv = false, .ws_inv = false},
    },
  };
  if (i2s_channel_init_std_mode(amp, &sc) != ESP_OK) return false;
  return i2s_channel_enable(amp) == ESP_OK;
}

// ---------- bass-cut filter ----------
// This small speaker distorts below ~280 Hz (tested: 250 and 262 Hz crackle, 294 Hz and up clean),
// so everything sent to it goes through a 280 Hz high-pass filter first. Speech stays clear.
static const float HPF_HZ = 400.0f;   // was 280; raised for more clean volume
float hb0, hb1, hb2, ha1, ha2, hx1 = 0, hx2 = 0, hy1 = 0, hy2 = 0;
void hpfSetup() {
  float w0 = 2.0f * PI * HPF_HZ / RATE, al = sinf(w0) / (2.0f * 0.7071f), c = cosf(w0), a0 = 1.0f + al;
  hb0 = (1.0f + c) / 2.0f / a0; hb1 = -(1.0f + c) / a0; hb2 = hb0;
  ha1 = -2.0f * c / a0; ha2 = (1.0f - al) / a0;
}
void hpfReset() { hx1 = hx2 = hy1 = hy2 = 0; }
inline int16_t hpf(float x) {
  float y = hb0 * x + hb1 * hx1 + hb2 * hx2 - ha1 * hy1 - ha2 * hy2;
  hx2 = hx1; hx1 = x; hy2 = hy1; hy1 = y;
  return (int16_t)constrain((int32_t)y, (int32_t)-32768, (int32_t)32767);
}

void ampOn(bool on) {
  digitalWrite(AMP_SD, on ? HIGH : LOW);   // LOW = amp asleep (silent)
  if (on) { hpfReset(); delay(10); }
}

// Sends n mono samples to both speaker channels, through the bass-cut filter.
void play(const int16_t *m, size_t n) {
  size_t i = 0;
  while (i < n) {
    size_t k = min((size_t)256, n - i);
    for (size_t j = 0; j < k; j++) { int16_t s = hpf(m[i + j]); stereo[2 * j] = s; stereo[2 * j + 1] = s; }
    size_t w;
    i2s_channel_write(amp, stereo, k * 4, &w, portMAX_DELAY);
    i += k;
  }
}

void silence(int ms) {
  static int16_t z[256] = {0};
  for (size_t n = RATE * ms / 1000; n > 0;) { size_t k = min((size_t)256, n); play(z, k); n -= k; }
}

// Sine tone, with a 10 ms fade in/out so there is no click.
void playTone(float hz, int ms) {
  static int16_t buf[256];
  size_t total = RATE * ms / 1000, fade = RATE / 100, done = 0;
  float ph = 0, inc = 2.0f * PI * hz / RATE;
  while (done < total) {
    size_t k = min((size_t)256, total - done);
    for (size_t j = 0; j < k; j++) {
      size_t t = done + j;
      float env = 1.0f;
      if (t < fade) env = (float)t / fade;
      else if (t > total - fade) env = (float)(total - t) / fade;
      buf[j] = (int16_t)(sinf(ph) * 32000.0f * volume * env);
      ph += inc; if (ph > 2.0f * PI) ph -= 2.0f * PI;
    }
    play(buf, k);
    done += k;
  }
}

// ---------- tests ----------
void beeps() {
  Serial.println("BEEPS: you should hear 3 short beeps");
  ampOn(true);
  for (int i = 0; i < 3; i++) { playTone(880, 150); silence(150); }
  silence(50); ampOn(false);
}

void steadyTone(float hz) {
  Serial.printf("TONE: %.0f Hz for 2 s at volume %.2f\n", hz, volume);
  ampOn(true); playTone(hz, 2000); silence(50); ampOn(false);
}

void sweep() {
  Serial.println("SWEEP: 150 Hz -> 6000 Hz over 4 s (low hum rising to a high whistle)");
  static int16_t buf[256];
  ampOn(true);
  size_t total = RATE * 4, done = 0;
  float ph = 0;
  while (done < total) {
    size_t k = min((size_t)256, total - done);
    for (size_t j = 0; j < k; j++) {
      float f = 150.0f * powf(6000.0f / 150.0f, (float)(done + j) / total);   // even steps by ear
      buf[j] = (int16_t)(sinf(ph) * 32000.0f * volume);
      ph += 2.0f * PI * f / RATE; if (ph > 2.0f * PI) ph -= 2.0f * PI;
    }
    play(buf, k);
    done += k;
  }
  silence(50); ampOn(false);
  Serial.println("  Low notes quiet or buzzy is normal for a small speaker. Rattling = loose speaker or too loud.");
}

// octave: 1 = low (262-523 Hz), 2 = middle (523-1047 Hz), 4 = high (1047-2093 Hz)
void melody(int octave) {
  Serial.printf("MELODY x%d: Sa Re Ga Ma Pa Dha Ni Sa (%.0f-%.0f Hz)\n", octave, 261.6f * octave, 523.3f * octave);
  const float notes[] = {261.6f, 293.7f, 329.6f, 349.2f, 392.0f, 440.0f, 493.9f, 523.3f};
  ampOn(true);
  for (float n : notes) { playTone(n * octave, 400); silence(60); }
  silence(50); ampOn(false);
}

// Hiss test: amp ON, sending perfect digital silence. Any sound now is NOT from the audio data.
void silenceTest() {
  Serial.println("SILENCE TEST: amp on for 4 s, sending pure zeros. Listen: is there hiss?");
  ampOn(true); silence(4000); ampOn(false);
  Serial.println("  Hiss now = power/ground noise.  Quiet now but hiss while speaking = signal wires or audio.");
}

// Speaks the sentence stored in nani_voice.h (from the ESP32's own flash, no Wi-Fi).
void speakSentence() {
  Serial.printf("SPEAK: \"%s\" (%.1f s)\n", NANI_TEXT, NANI_VOICE_LEN / (float)RATE);
  static int16_t buf[256];
  float g = volume / 0.8f;
  ampOn(true);
  for (uint32_t i = 0; i < NANI_VOICE_LEN; i += 256) {
    uint32_t k = min((uint32_t)256, NANI_VOICE_LEN - i);
    for (uint32_t j = 0; j < k; j++) buf[j] = (int16_t)(NANI_VOICE[i + j] * g);
    play(buf, k);
  }
  silence(80); ampOn(false);
}

// ---------- mic (parrot test) ----------
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

void parrot() {
  const size_t n = RATE * 3;
  static int16_t *rec = nullptr;
  static int32_t raw[256];
  if (!mic && !micStart()) { Serial.println("PARROT: mic failed to start"); return; }
  if (!rec) rec = (int16_t *)(psramFound() ? ps_malloc(n * 2) : malloc(n * 2));
  if (!rec) { Serial.println("PARROT: not enough memory"); return; }

  Serial.println("PARROT: talk now for 3 seconds...");
  size_t got = 0, bytes;
  i2s_channel_read(mic, raw, sizeof(raw), &bytes, 200);   // drop stale audio
  while (got < n) {
    if (i2s_channel_read(mic, raw, sizeof(raw), &bytes, 200) != ESP_OK || !bytes) break;
    for (size_t i = 0; i < bytes / 4 && got < n; i++) rec[got++] = (int16_t)constrain(raw[i] >> 14, -32768, 32767);
  }
  long sum = 0; int peak = 1;
  for (size_t i = 0; i < got; i++) sum += rec[i];
  int mean = got ? sum / (long)got : 0;
  for (size_t i = 0; i < got; i++) { rec[i] -= mean; peak = max(peak, abs((int)rec[i])); }
  float g = min(28000.0f / peak, 10.0f) * (volume / 0.8f);     // make it clearly audible
  for (size_t i = 0; i < got; i++) rec[i] = (int16_t)constrain((int)(rec[i] * g), -32768, 32767);

  Serial.println("  Playing it back...");
  ampOn(true); play(rec, got); silence(50); ampOn(false);
  Serial.println("  Done. You should have heard your own voice.");
}

// ---------- menu ----------
void help() {
  Serial.println("\nType a letter + Enter:");
  Serial.println("  b = 3 beeps     1/2/3/4 = tone 250/440/1000/3000 Hz");
  Serial.println("  v = SPEAK the sentence     z = silence test (amp on, no sound: listen for hiss)");
  Serial.println("  s = sweep       p = parrot (mic -> speaker)");
  Serial.println("  m / n / o = melody low / middle / high octave (compare which is clearest)");
  Serial.printf ("  + / - = volume (now %.2f)     h = help\n\n", volume);
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 5000) delay(10);
  delay(300);
  pinMode(AMP_SD, OUTPUT);
  hpfSetup();
  ampOn(false);

  Serial.println("\n======== NANI SPEAKER TEST ========");
  Serial.println("Amp: BCLK 15, LRC 16, DIN 17, SD 18 · VIN 5V");
  if (!ampStart()) { Serial.println("FAIL: I2S for the amp did not start"); return; }
  Serial.println("Amp I2S started.");
  beeps();
  delay(300);
  speakSentence();
  Serial.println("Heard them?  YES = speaker works.  NO = see the checklist:");
  Serial.println("  - amp VIN on 5V (VBUS), GND shared with the ESP32");
  Serial.println("  - BCLK 15, LRC 16, DIN 17 not swapped");
  Serial.println("  - speaker wires tight in the amp's + / - terminals");
  Serial.println("  - SD pin on GPIO18 or left unconnected (never on GND)");
  help();
}

void loop() {
  if (!Serial.available()) { delay(10); return; }
  char c = Serial.read();
  switch (c) {
    case 'b': beeps(); break;
    case '1': steadyTone(250); break;
    case '2': steadyTone(440); break;
    case '3': steadyTone(1000); break;
    case '4': steadyTone(3000); break;
    case 's': sweep(); break;
    case 'm': melody(1); break;
    case 'n': melody(2); break;
    case 'o': melody(4); break;
    case 'p': parrot(); break;
    case 'v': speakSentence(); break;
    case 'z': silenceTest(); break;
    case '+': volume = min(volume + 0.05f, 0.6f); Serial.printf("Volume %.2f\n", volume); beeps(); break;
    case '-': volume = max(volume - 0.05f, 0.05f); Serial.printf("Volume %.2f\n", volume); beeps(); break;
    case 'h': help(); break;
    default: break;
  }
}
