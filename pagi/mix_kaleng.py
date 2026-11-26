"""Mix ARN-62 (reel bisu, tanpa VO, PRB-19): salinan tools/mix.py -- musik latar sintesis + sfx,
ditambah sfx "tingtong" (bel pintu) dan "tik" (timer). Tanpa vo.wav. Output mix.wav."""
import json, os
import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import butter, lfilter

SR = 44100
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "12.0"))

N = int(TOTAL * SR)
out_vo = np.zeros(N)   # reel bisu: tidak ada VO

t = np.arange(N) / SR
rng = np.random.default_rng(24)


def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), "low")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


# --- musik: pad akor lembut + plucks ringan, 96 bpm ---
chords = [[220.0, 277.18, 329.63], [196.0, 246.94, 293.66], [174.61, 220.0, 261.63], [196.0, 246.94, 329.63]]
bar = 60 / 96 * 4
music = np.zeros(N)
for i in range(int(TOTAL / bar) + 1):
    c = chords[i % 4]
    a0, a1 = int(i * bar * SR), min(N, int((i + 1) * bar * SR))
    if a0 >= N:
        break
    tt = t[a0:a1] - i * bar
    env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.4)
    for f in c:
        music[a0:a1] += env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) / 3
    # pluck tiap ketukan
    for k in range(4):
        p0 = a0 + int(k * bar / 4 * SR)
        L = int(0.35 * SR)
        if p0 + L > N:
            continue
        tp = np.arange(L) / SR
        f = c[k % 3] * 2
        music[p0:p0 + L] += 0.35 * np.exp(-tp * 9) * np.sin(2 * np.pi * f * tp)
music = lp(music, 2500)
music *= 0.25 / max(1e-6, np.abs(music).max())

# ducking: amplop VO -> musik turun ±12 dB saat ada narasi
env = np.sqrt(np.maximum(lp(out_vo ** 2, 8), 0))
env = np.clip(env / 0.05, 0, 1)
env = lp(env, 3)
music *= 1 - 0.75 * np.clip(env, 0, 1)
# fade in/out musik
fade = np.minimum(1, t / 0.6) * np.minimum(1, (TOTAL - t) / 0.8)
music *= fade

sfx = np.zeros(N)


def add(x, at, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if i < N:
        sfx[i:j] += gain * x[: j - i]


def pop(f=880):
    L = int(0.12 * SR); tp = np.arange(L) / SR
    return np.exp(-tp * 35) * np.sin(2 * np.pi * (f + 600 * np.exp(-tp * 40)) * tp)


def whoosh():
    L = int(0.45 * SR); tp = np.arange(L) / SR
    n = rng.standard_normal(L)
    x = bp(n, 400, 4000)
    return x * np.sin(np.pi * tp / tp[-1]) ** 2 * 0.5


def cring():
    L = int(0.6 * SR); tp = np.arange(L) / SR
    x = sum(np.exp(-tp * d) * np.sin(2 * np.pi * f * tp) for f, d in [(2637, 7), (3520, 9), (4186, 11), (5274, 14)])
    x2 = np.zeros(L); o = int(0.07 * SR)
    x2[o:] = x[: L - o] * 0.7
    return (x + x2) / 4


def ding():
    L = int(0.9 * SR); tp = np.arange(L) / SR
    return (np.sin(2 * np.pi * 1318.5 * tp) + 0.5 * np.sin(2 * np.pi * 1975.5 * tp)) * np.exp(-tp * 4) / 1.5


def klik():
    L = int(0.03 * SR)
    return bp(rng.standard_normal(L), 2000, 6000) * np.exp(-np.arange(L) / SR * 150)


def tingtong():
    L = int(1.1 * SR); tp = np.arange(L) / SR
    def tone(f, t0):
        x = np.zeros(L); i = int(t0 * SR); tt = tp[: L - i]
        x[i:] = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) + 0.2 * np.sin(2 * np.pi * 3.01 * f * tt)) * np.exp(-tt * 3.2)
        return x
    return (tone(659.25, 0.0) + tone(523.25, 0.38)) / 1.6


def tik():
    L = int(0.04 * SR); tp = np.arange(L) / SR
    return (np.sin(2 * np.pi * 3200 * tp) * 0.6 + bp(rng.standard_normal(L), 3000, 7000) * 0.5) * np.exp(-tp * 160)


ev = json.load(open("events.json"))
for e in ev:
    f = {"pop": pop, "whoosh": whoosh, "cring": cring, "ding": ding, "klik": klik, "tingtong": tingtong, "tik": tik}[e["sfx"]]
    add(f(), e["t"], e.get("gain", 0.35))

mix = out_vo + music + sfx
mix *= 0.89 / max(1e-6, np.abs(mix).max())
wav.write("mix.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print("mix.wav", TOTAL, "dtk")
