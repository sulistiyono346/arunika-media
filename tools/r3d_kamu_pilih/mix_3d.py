"""Mix ARN-40 (3D sinematik): VO (LEAD 0,3) + drone/ambience kabin + sfx sintesis. Output mix_raw.wav (normalisasi loudnorm 2 tahap terpisah)."""
import json
import numpy as np, scipy.io.wavfile as wav
from scipy.signal import butter, lfilter
SR = 44100
T = json.load(open('timing.json')); CH = T['chunks']; SC = T['scenes']; TOTAL = T['total']; LEAD = T['lead']
cs = lambda i: CH[i]['s']
sr, vo = wav.read('vo.wav'); vo = vo.astype(np.float64) / 32768.0
N = int(TOTAL * SR); t = np.arange(N) / SR; rng = np.random.default_rng(40)
v = np.zeros(N); s0 = int(LEAD * SR); v[s0:s0 + len(vo)] = vo[:N - s0]; v *= 0.707 / np.abs(v).max()
def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)
def seg(a, b): return (t >= a) & (t < b)
def env(a, b, fi=0.5, fo=0.5): return np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)
# drone: akor rendah gelap (D minor-ish), pelan berdenyut
drone = np.zeros(N)
for f, g in [(36.71, 1), (55.0, .6), (73.42, .5), (110.0, .18), (146.83, .12)]:
    drone += g * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t))
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)
drone = lp(drone, 400) * 0.16
# hum mesin jet (noise lowpass) — hilang saat mesin mati, kembali saat menyala
noise = rng.standard_normal(N)
hum = lp(noise, 300, 4) * 0.9
on = np.ones(N)
off_t = cs(8) + 0.45; back_t = cs(28)
on *= np.clip(1 - (t - off_t) / 2.5, 0, 1) * (t >= off_t) + (t < off_t)
on = np.maximum(on, np.clip((t - back_t) / 2.5, 0, 1))
inside = np.ones(N)  # adegan peta / penutup lebih sunyi
for a, b in [(SC[6], SC[8]), (SC[14], TOTAL)]: inside[seg(a, b)] = 0.35
hum *= on * inside * 0.35
# angin saat meluncur tanpa mesin
wind = bp(rng.standard_normal(N), 300, 2200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)) * 0.10
wind *= env(off_t + 0.5, back_t + 2, 2, 2) * inside
sfx = np.zeros(N)
def add(x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if 0 <= i < N: sfx[i:j] += g * x[:j - i]
def whoosh(L=0.6):
    n = int(L * SR); tp = np.arange(n) / SR; x = bp(rng.standard_normal(n), 250, 3000); return x * np.sin(np.pi * tp / tp[-1]) ** 2 * 0.5
def beep(f=1400, L=0.09):
    n = int(L * SR); tp = np.arange(n) / SR; return np.sin(2 * np.pi * f * tp) * np.minimum(1, (L - tp) / 0.01) * np.minimum(1, tp / 0.005)
def powerdown(L=2.2):
    n = int(L * SR); tp = np.arange(n) / SR; f = 420 * np.exp(-tp * 1.4) + 40; ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * 0.6 + lp(rng.standard_normal(n), 600) * 0.6) * np.exp(-tp * 1.2)
def ignite(L=1.8):
    n = int(L * SR); tp = np.arange(n) / SR; f = 60 + 360 * (1 - np.exp(-tp * 2)); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * 0.5 + bp(rng.standard_normal(n), 200, 2500) * 0.9) * np.minimum(1, tp / 0.3) * np.exp(-np.maximum(0, tp - 1.0) * 2)
def rumble(L=1.4):
    n = int(L * SR); tp = np.arange(n) / SR; return lp(rng.standard_normal(n), 120, 4) * 3 * np.exp(-tp * 2.5)
def tick(f=2600):
    n = int(0.04 * SR); return bp(rng.standard_normal(n), f - 800, f + 800) * np.exp(-np.arange(n) / SR * 120) * 1.5
def ding():
    n = int(1.2 * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * 880 * tp) + .5 * np.sin(2 * np.pi * 1320 * tp)) * np.exp(-tp * 3) / 1.5
def zap(L=0.25):
    n = int(L * SR); tp = np.arange(n) / SR; return hp(rng.standard_normal(n), 3000) * np.exp(-tp * 18) * 0.8
for a in SC[1:14]: add(whoosh(), a - 0.25, 0.22)
add(rumble(2.0), 0.0, 0.25)                       # rumble kabin di awal
for k in range(14): add(zap(), 9.6 + k * 0.27 + 0.1 * np.sin(k * 3), 0.05)   # gemeretak St. Elmo
add(powerdown(), off_t, 0.35)
for d in (0.35, 0.6, 0.85): add(powerdown(1.6), cs(9) + d, 0.25)
for k in range(int((SC[6] - SC[5]) / 0.5)): add(beep(1500), SC[5] + 0.15 + k * 0.5, 0.10)   # alarm altimeter
for k in range(int((SC[11] - SC[10]) / 0.6)): add(beep(1200 if k % 2 else 1500), SC[10] + 0.2 + k * 0.6, 0.08)
for k in range(10): add(tick(2600 if k % 2 == 0 else 1900), SC[9] + 0.2 + k * 0.29, 0.20)  # tik-tok jeda tebak
add(rumble(1.2), back_t - 0.1, 0.3); add(ignite(), back_t, 0.35)
for d in (0.05, 0.3, 0.55): add(ignite(1.4), cs(30) + d, 0.22)
add(rumble(1.6), cs(31) - 0.4, 0.35)  # roda menyentuh landasan
add(ding(), cs(31) + 1.1, 0.25)
for k in range(5): add(rumble(0.8), SC[13] + 0.6 + k * 1.1, 0.2)  # gemuruh gunung
add(ding(), SC[14] + 0.05, 0.2)
# ducking ringan untuk bed
e = np.sqrt(np.maximum(lp(v ** 2, 8), 0)); e = lp(np.clip(e / 0.05, 0, 1), 3)
bed = (drone + hum + wind) * (1 - 0.45 * np.clip(e, 0, 1))
bed *= np.minimum(1, t / 0.05) * np.minimum(1, (TOTAL - t) / 0.6)
mix = v + bed + sfx
mix *= 0.89 / np.abs(mix).max()
wav.write('mix_raw.wav', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print('mix_raw.wav', TOTAL)
