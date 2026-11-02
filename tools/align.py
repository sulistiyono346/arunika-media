"""Waktu per chunk subtitle ARN-24 dari segmen bicara nyata (jeda silencedetect),
dibagi per suku kata di dalam tiap segmen. Output: timing.json (waktu audio VO)."""
import json, re

# segmen bicara (detik audio VO), dari silencedetect -35 dB / 0,25 dtk
SEGS = [(0.03, 1.99), (2.45, 3.05), (3.48, 4.30), (4.81, 7.11), (7.37, 8.26), (8.83, 12.72),
        (13.33, 17.00), (17.44, 19.08), (19.29, 21.62), (22.18, 22.68), (22.86, 23.63), (24.05, 24.85)]

# per segmen: list chunk (teks layar, kata yang diucapkan, kata kunci kuning)
CHUNKS = [
    [("MINYAK DUNIA", "minyak dunia", []), ("NAIK TURUN", "naik turun", ["NAIK", "TURUN"]),
     ("TIAP HARI.", "tiap hari", [])],
    [("PERTAMAX-MU?", "pertamaxmu", ["PERTAMAX-MU?"])],
    [("DIAM SEBULAN.", "diam sebulan", ["SEBULAN."])],
    [("KARENA HARGANYA", "karena harganya", []), ("CUMA DIUBAH", "cuma diubah", []),
     ("SEBULAN SEKALI,", "sebulan sekali", ["SEBULAN", "SEKALI,"])],
    [("TIAP TANGGAL 1", "tiap tanggal satu", ["TANGGAL", "1"])],
    [("PATOKANNYA", "patokannya", []), ("HARGA BENSIN SINGAPURA", "harga bensin singapura", ["SINGAPURA"]),
     ("DAN KURS DOLAR", "dan kurs dolar", ["DOLAR"]), ("SEBULAN SEBELUMNYA", "sebulan sebelumnya", ["SEBELUMNYA"])],
    [("JADI PERTAMAX", "jadi pertamax", []), ("NOVEMBER INI", "november ini", ["NOVEMBER"]),
     ("SEBENARNYA", "sebenarnya", []), ("HARGA MINYAK", "harga minyak", []),
     ("BULAN LALU", "bulan lalu", ["BULAN", "LALU"])],
    [("ISI 30 LITER", "isi tiga puluh liter", ["30", "LITER"]), ("SEBULAN,", "sebulan", [])],
    [("NAIK Rp1.000", "naik seribu", ["Rp1.000"]), ("SAMA DENGAN", "sama dengan", []),
     ("Rp30 RIBU", "tiga puluh ribu", ["Rp30", "RIBU"])],
    [("DESEMBER", "desember", ["DESEMBER"])], [("NAIK ATAU TURUN?", "naik atau turun", [])],
    [("TULIS TEBAKANMU", "tulis tebakanmu", ["TEBAKANMU"])],
]


def syl(word):
    return max(1, len(re.findall(r"[aiueo]+", word.lower())))


out = []
for (s, e), chunks in zip(SEGS, CHUNKS):
    weights = [sum(syl(w) + 0.4 for w in sp.split()) for _, sp, _ in chunks]
    tot = sum(weights)
    t = s
    for (disp, sp, keys), wgt in zip(chunks, weights):
        d = (e - s) * wgt / tot
        out.append({"text": disp, "keys": keys, "start": round(t, 3), "end": round(t + d, 3)})
        t += d

json.dump(out, open("timing.json", "w"), ensure_ascii=False, indent=1)
for i, c in enumerate(out):
    print(i, c["start"], c["end"], c["text"])
