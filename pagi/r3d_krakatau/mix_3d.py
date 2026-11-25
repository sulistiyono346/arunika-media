"""Mix ARN-61 (3D sinematik Krakatau): VO (LEAD 0,3) + drone gelap + debur laut + sfx sintetis. Output mix_raw.wav.
Normalisasi -14 LUFS dua tahap terpisah (ffmpeg loudnorm). Tanpa suara sirene (sirene 'diam')."""
import json
import numpy as np, scipy.io.wavfile as wav
from scipy.signal import butter, lfilter
SR = 44100
T = json.load(open('timing.json')); CH = T['chunks']; SC = T['scenes']; TOTAL = T['total']; LEAD = T['lead']
cs = lambda i: CH[i]['s']
sr, vo = wav.read('vo.wav'); vo = vo.astype(np.float64) / 32768.0
N = int(TOTAL * SR); t = np.arange(N) / SR; rng = np.random.default_rng(61)
v = np.zeros(N); s0 = int(LEAD * SR); n = min(len(vo), N - s0); v[s0:s0 + n] = vo[:n]; v *= 0.707 / np.abs(v).max()
def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)
def env(a, b, fi=0.5, fo=0.5): return np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)
# drone gelap (A minor), turun saat adegan korban
drone = np.zeros(N)
for f, g in [(55.0, 1), (82.4, .5), (110.0, .35), (130.8, .2), (164.8, .12)]:
    drone += g * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.05 * t))
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.09 * t)
drone = lp(drone, 450) * 0.15
quiet = 1 - 0.85 * env(SC[6] + 0.2, SC[7] + 0.1, 0.6, 0.4)     # momen hening adegan 7
drone *= quiet
# debur laut jauh (surut: pelan), malam 2018 sedikit lebih dekat
noise = rng.standard_normal(N)
surf = lp(noise, 700, 2) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.12 * t) ** 2)
surfg = np.full(N, 0.10); surfg[(t >= SC[9]) & (t < SC[11])] = 0.16
surf *= surfg * quiet
# deru gelombang tsunami (adegan 6-7)
roar = lp(rng.standard_normal(N), 260, 4) * 2.2 * env(cs(15), SC[7] + 0.2, 2.5, 0.6)
sfx = np.zeros(N)
def add(x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if 0 <= i < N: sfx[i:j] += g * x[:j - i]
def whoosh(L=0.6):
    n = int(L * SR); tp = np.arange(n) / SR; x = bp(rng.standard_normal(n), 250, 3000); return x * np.sin(np.pi * tp / tp[-1]) ** 2 * 0.5
def slap():
    n = int(0.07 * SR); tp = np.arange(n) / SR; return bp(rng.standard_normal(n), 600, 3500) * np.exp(-tp * 70)
def boom(L=3.5):
    n = int(L * SR); tp = np.arange(n) / SR; return (lp(rng.standard_normal(n), 90, 4) * 6 + np.sin(2 * np.pi * 38 * tp) * 0.6) * np.exp(-tp * 1.1) * np.minimum(1, tp / 0.01)
def rumble(L=1.6):
    n = int(L * SR); tp = np.arange(n) / SR; return lp(rng.standard_normal(n), 120, 4) * 3 * np.exp(-tp * 2.0)
def tick(f=2600):
    n = int(0.04 * SR); return bp(rng.standard_normal(n), f - 800, f + 800) * np.exp(-np.arange(n) / SR * 120) * 1.5
def ding():
    n = int(1.2 * SR); tp = np.arange(n) / SR; return (np.sin(2 * np.pi * 880 * tp) + .5 * np.sin(2 * np.pi * 1320 * tp)) * np.exp(-tp * 3) / 1.5
def pop():
    n = int(0.12 * SR); tp = np.arange(n) / SR; return np.sin(2 * np.pi * (500 + 900 * tp / 0.12) * tp) * np.exp(-tp * 30) * 0.8
for a in SC[1:13]: add(whoosh(), a - 0.25, 0.2)
for cut in (cs(10), cs(21), cs(37)): add(whoosh(0.5), cut - 0.2, 0.15)
R = np.random.default_rng(5)
for k in range(40):                                 # ikan menggelepar (adegan 1-2, 8)
    add(slap(), R.uniform(0.2, SC[2] - 0.2), 0.07)
for k in range(14): add(slap(), R.uniform(cs(21), SC[8] - 0.2), 0.06)
add(boom(), cs(9) + 0.05, 0.55)                     # letusan
add(rumble(2.5), cs(10) - 0.1, 0.35)                # gelombang kejut
for k in range(6): add(rumble(0.9), cs(10) + 0.6 + k * 0.6, 0.15)
add(pop(), cs(11), 0.25)
for k in range(5): add(tick(2600 if k % 2 == 0 else 1900), cs(14) - 0.2 + k * 0.32, 0.18)  # tik-tok "coba tebak"
add(ding(), cs(20), 0.25)                           # kartu LARI
add(pop(), cs(23) - 0.2, 0.2)
add(pop(), cs(27) - 0.1, 0.18)                      # gelembung teks
for k in range(int((SC[11] - SC[10]) / 0.5)): add(tick(2200), SC[10] + 0.15 + k * 0.5, 0.16)   # stopwatch
add(ding(), cs(37), 0.2)                            # kartu layak simpan
add(pop(), SC[12] + 0.1, 0.18)
add(ding(), SC[13] + 0.05, 0.18)
e = np.sqrt(np.maximum(lp(v ** 2, 8), 0)); e = lp(np.clip(e / 0.05, 0, 1), 3)
bed = (drone + surf + roar) * (1 - 0.45 * np.clip(e, 0, 1))
bed *= np.minimum(1, t / 0.05) * np.minimum(1, (TOTAL - t) / 0.6)
mix = v + bed + sfx
mix *= 0.89 / np.abs(mix).max()
wav.write('mix_raw.wav', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print('mix_raw.wav', TOTAL)
