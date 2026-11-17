"""Mix ARN-58 (3D bongkar kunci): VO (LEAD 0,3) + pad hangat + sfx mekanis sintetis. Output mix_raw.wav.
Normalisasi -14 LUFS dua tahap dilakukan terpisah dengan ffmpeg loudnorm (lihat README)."""
import json
import numpy as np, scipy.io.wavfile as wav
from scipy.signal import butter, lfilter
SR = 44100
T = json.load(open('timing.json')); CH = T['chunks']; SC = T['scenes']; TOTAL = T['total']; LEAD = T['lead']
cs = lambda i: CH[i]['s']
sr, vo = wav.read('vo.wav'); vo = vo.astype(np.float64) / 32768.0
if vo.ndim > 1: vo = vo.mean(1)
N = int(TOTAL * SR); t = np.arange(N) / SR; rng = np.random.default_rng(58)
v = np.zeros(N); s0 = int(LEAD * SR); n = min(len(vo), N - s0); v[s0:s0 + n] = vo[:n]; v *= 0.707 / np.abs(v).max()
def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)
# pad: akor hangat pelan (A mayor add9), berdenyut halus
pad = np.zeros(N)
for f, g in [(55.0, 1), (110.0, .5), (164.81, .35), (220.0, .25), (277.18, .18), (329.63, .12), (493.88, .06)]:
    pad += g * np.sin(2 * np.pi * f * t + 0.4 * np.sin(2 * np.pi * 0.05 * t + f))
pad *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.125 * t)
pad = lp(pad, 900) * 0.10
pulse = lp(rng.standard_normal(N), 90, 4) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 1.0 * t))) * 0.25
sfx = np.zeros(N)
def add(x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if 0 <= i < N: sfx[i:j] += g * x[:j - i]
def whoosh(L=0.55):
    n = int(L * SR); tp = np.arange(n) / SR; x = bp(rng.standard_normal(n), 300, 3500); return x * np.sin(np.pi * tp / tp[-1]) ** 2 * 0.5
def tick(f=3200, L=0.035):
    n = int(L * SR); return bp(rng.standard_normal(n), f - 900, f + 900) * np.exp(-np.arange(n) / SR * 140) * 1.6
def clink(f=2400):
    n = int(0.5 * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * f * tp) + .6 * np.sin(2 * np.pi * f * 2.76 * tp) + .3 * np.sin(2 * np.pi * f * 5.4 * tp)) * np.exp(-tp * 9) * 0.5
def klik():
    n = int(0.25 * SR); tp = np.arange(n) / SR; a = bp(rng.standard_normal(n), 1500, 6000) * np.exp(-tp * 90); b = np.sin(2 * np.pi * 180 * tp) * np.exp(-tp * 30) * 0.8
    return a * 1.4 + b
def thud(f=70, L=0.4):
    n = int(L * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * f * tp) + lp(rng.standard_normal(n), 300) * 0.6) * np.exp(-tp * 12)
def ding(f=1320):
    n = int(1.2 * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * f * tp) + .5 * np.sin(2 * np.pi * f * 1.5 * tp)) * np.exp(-tp * 3.2) / 1.5
def buzz(L=0.35):
    n = int(L * SR); tp = np.arange(n) / SR; return np.sign(np.sin(2 * np.pi * 110 * tp)) * lp(np.ones(n), 50) * np.minimum(1, (L - tp) / 0.03) * 0.25
def scrape(L):
    n = int(L * SR); tp = np.arange(n) / SR; return bp(rng.standard_normal(n), 2000, 7000) * np.minimum(1, tp / 0.05) * np.minimum(1, (L - tp) / 0.1) * 0.25
def beep(f=1800, L=0.07):
    n = int(L * SR); tp = np.arange(n) / SR; return np.sin(2 * np.pi * f * tp) * np.minimum(1, (L - tp) / 0.01) * np.minimum(1, tp / 0.004)
def jingle(L=0.8):
    out = np.zeros(int(L * SR))
    for k in range(9):
        c = clink(2200 + rng.random() * 2600); i = int(rng.random() * (L - 0.3) * SR); j = min(len(out), i + len(c)); out[i:j] += c[:j - i] * (0.3 + 0.4 * rng.random())
    return out
def wood(L=0.25):
    n = int(L * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * 420 * tp) + .5 * np.sin(2 * np.pi * 980 * tp)) * np.exp(-tp * 35) + bp(rng.standard_normal(n), 400, 2500) * np.exp(-tp * 60) * 0.5
for a in SC[1:10]: add(whoosh(), a - 0.25, 0.25)
# 1 hook: meledak + denting pin + counter
add(whoosh(0.8), 1.25, 0.45); add(thud(55, 0.6), 1.5, 0.35)
for k in range(12): add(clink(1800 + 300 * (k % 5)), 1.55 + k * 0.05 + 0.02 * np.sin(k), 0.12)
for k in range(6): add(tick(3600), 1.85 + k * 0.15, 0.30)
# 2 sapuan cahaya di gerigi
add(whoosh(1.2), cs(5) + 0.1, 0.18); add(ding(1760), cs(6), 0.12)
# 3 label muncul
for tt in [cs(8) + 0.1, cs(8) + 0.7, cs(10) + 0.35, cs(10) + 0.95, cs(11) + 0.05]: add(tick(2600), tt, 0.35)
# 4 kunci masuk: gesek + tik tiap pin terangkat
ks, ke = cs(12) + 0.35, cs(14) + 0.45
add(scrape(ke - ks), ks, 0.6)
for k in range(15): add(tick(4200 if k % 2 else 3300), ks + (k + 0.5) * (ke - ks) / 15, 0.35)
add(ding(1568), cs(15) + 0.05, 0.22)
# 5 klik berputar, lalu kunci salah macet
add(klik(), cs(17) + 0.42, 0.55); add(ding(2093), cs(17) + 0.45, 0.15)
add(scrape(cs(19) + 0.1 - (cs(18) - 0.0)), cs(18), 0.5)
add(thud(90, 0.3), cs(20), 0.4)
for k in range(8): add(thud(140, 0.12), cs(21) + k * 0.06, 0.25 * np.exp(-k * 0.3))
add(buzz(), cs(21), 0.25)
# 6 gantungan: gemerincing + 9 ditolak + 1 berhasil
add(jingle(1.0), SC[5] + 0.05, 0.4)
ts, te = SC[5] + 0.45, cs(24); dt = (te - ts) / 9
for j in range(9): add(tick(2000), ts + j * dt, 0.35); add(beep(330, 0.09), ts + j * dt + 0.05, 0.12)
add(klik(), te, 0.4); add(ding(1760), te + 0.05, 0.25)
add(whoosh(0.7), cs(25) + 0.0, 0.3)
# 7 kayu -> logam, denyut
for k in range(3): add(wood(), SC[6] + 0.1 + k * 0.14, 0.35)
add(whoosh(0.9), cs(28), 0.3); add(clink(2600), cs(28) + 0.8, 0.3); add(ding(1320), cs(29), 0.12)
add(thud(60, 0.5), cs(30), 0.3)
# 8 kunci pintar: bip keypad, dibongkar
for k in range(5): add(beep(1600 + 200 * (k % 3)), cs(32) + 0.12 + k * 0.13, 0.12)
add(beep(2400, 0.15), cs(32) + 0.85, 0.12)
add(whoosh(0.7), cs(34), 0.35); add(clink(2000), cs(34) + 0.5, 0.25)
add(tick(2600), cs(35) + 0.1, 0.35)
# 9 kunci cadangan melayang
add(whoosh(1.4), cs(37) - 0.1, 0.3); add(ding(1568), cs(38) + 0.05, 0.2)
# 10 tim biasa / tim pintar + penutup
add(tick(2400), cs(41) + 0.1, 0.4); add(tick(3000), cs(42) + 0.1, 0.4)
add(ding(1320), SC[10] + 0.02, 0.22)
e = np.sqrt(np.maximum(lp(v ** 2, 8), 0)); e = lp(np.clip(e / 0.05, 0, 1), 3)
bed = (pad + pulse) * (1 - 0.5 * np.clip(e, 0, 1))
bed *= np.minimum(1, t / 0.05) * np.minimum(1, (TOTAL - t) / 0.6)
mix = v + bed + sfx * 0.8
mix *= 0.89 / np.abs(mix).max()
wav.write('mix_raw.wav', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print('mix_raw.wav', TOTAL)
