"""Timing ARN-58 (3D bongkar, kunci pin tumbler) dari jeda VO nyata (ffmpeg silencedetect -30dB d=0.12), TANPA Scribe.
Output timing.json (waktu video = VO + LEAD)."""
import json
LEAD = 0.3
VO_LEN = 54.05
# segmen bicara di antara jeda (detik VO)
SEGS = [
 (0.00, 2.11, "Kuncimu ditolak hampir semua pintu,"), (2.47, 3.25, "kecuali satu."), (3.68, 3.81, "Yuk,"), (4.08, 4.63, "kita bongkar."),
 (5.05, 5.86, "Coba tebak dulu:"), (6.27, 9.11, "rahasianya bukan di gerigi yang selama ini kamu lihat."),
 (9.75, 10.49, "Di dalamnya,"), (10.77, 13.44, "ada lima atau enam tumpuk pin berpegas,"), (13.74, 14.73, "panjangnya beda-beda."),
 (15.20, 15.46, "Nah,"), (15.78, 16.73, "anak kunci masuk."), (17.30, 20.18, "Tiap lekuk mendorong pin sampai rata di garis geser."),
 (20.71, 21.27, "Kunci benar?"), (21.71, 22.62, "Silinder berputar."), (23.19, 23.80, "Kunci salah?"),
 (24.19, 25.67, "Cukup satu pin nggak pas,"), (25.95, 26.34, "nyangkut."), (26.75, 27.11, "Macet."),
 (27.76, 28.33, "Makanya,"), (28.68, 30.47, "dari sepuluh kunci di gantunganmu,"), (30.66, 31.79, "cuma satu yang muter."), (32.26, 33.00, "Siapa penemunya?"),
 (33.55, 37.80, "Idenya dari kunci kayu Mesir kuno, lalu dikecilkan Linus Yale Junior."), (38.28, 38.74, "Masih cukup?"),
 (39.21, 39.84, "Kubu sebelah:"), (40.13, 41.32, "ganti kunci pintar!"), (41.69, 42.36, "Praktis,"), (42.59, 44.71, "tapi banyak yang masih simpan silinder ini."),
 (45.20, 46.51, "Jadi kuno atau canggih,"), (46.74, 49.41, "tetap titip satu kunci cadangan ke orang terpercaya."),
 (49.92, 50.60, "Sekarang jujur:"), (51.01, 53.73, "kamu tim kunci biasa, atau tim kunci pintar?"),
]
# (teks layar, kata kunci kuning, jumlah kata yang diucapkan)
CHUNKS = [
 ("Kuncimu ditolak", "ditolak", 2), ("hampir semua pintu,", "semua", 3), ("kecuali satu.", "satu", 2), ("Yuk, kita bongkar.", "bongkar", 3),
 ("Coba tebak dulu:", "tebak", 3), ("rahasianya bukan", "bukan", 2), ("di gerigi", "gerigi", 2), ("yang selama ini kamu lihat.", "lihat", 5),
 ("Di dalamnya,", "dalamnya", 2), ("ada 5 atau 6", "5 atau 6", 4), ("tumpuk pin berpegas,", "pin", 3), ("panjangnya beda-beda.", "beda-beda", 2),
 ("Nah, anak kunci masuk.", "masuk", 4), ("Tiap lekuk mendorong pin", "lekuk", 4), ("sampai rata", "rata", 2), ("di garis geser.", "garis geser", 3),
 ("Kunci benar?", "benar", 2), ("Silinder berputar.", "berputar", 2), ("Kunci salah?", "salah", 2), ("Cukup satu pin nggak pas,", "satu pin", 5),
 ("nyangkut.", "nyangkut", 1), ("Macet.", "Macet", 1),
 ("Makanya, dari 10 kunci", "10", 4), ("di gantunganmu,", "gantunganmu", 2), ("cuma satu yang muter.", "satu", 4), ("Siapa penemunya?", "penemunya", 2),
 ("Idenya dari kunci kayu", "kayu", 4), ("Mesir kuno,", "Mesir", 2), ("lalu dikecilkan", "dikecilkan", 2), ("Linus Yale Junior.", "Linus Yale", 3), ("Masih cukup?", "cukup", 2),
 ("Kubu sebelah:", "Kubu", 2), ("ganti kunci pintar!", "pintar", 3), ("Praktis,", "Praktis", 1), ("tapi banyak yang masih", "masih", 4), ("simpan silinder ini.", "silinder", 3),
 ("Jadi kuno atau canggih,", "canggih", 4), ("tetap titip satu", "titip", 3), ("kunci cadangan", "cadangan", 2), ("ke orang terpercaya.", "terpercaya", 3),
 ("Sekarang jujur:", "jujur", 2), ("kamu tim kunci biasa,", "biasa", 4), ("atau tim kunci pintar?", "pintar", 4),
]
words = []
for a, b, txt in SEGS:
    ws = txt.split(); w = [len(x) + 1 for x in ws]; tot = sum(w); t = a
    for x, wi in zip(ws, w):
        d = (b - a) * wi / tot; words.append((x, t + LEAD, t + d + LEAD)); t += d
assert sum(c[2] for c in CHUNKS) == len(words), (sum(c[2] for c in CHUNKS), len(words))
out = []; i = 0
for txt, kw, n in CHUNKS:
    ws = words[i:i + n]; i += n
    assert kw in txt, (kw, txt)
    out.append({"text": txt, "kw": kw, "s": round(ws[0][1], 3), "e": round(ws[-1][2], 3), "spoken": " ".join(w[0] for w in ws)})
out[0]["s"] = 0.0
for k, c in enumerate(out):
    nxt = out[k + 1]["s"] if k + 1 < len(out) else c["e"] + 0.4
    c["show_end"] = round(min(nxt, c["e"] + 0.5) if nxt - c["e"] > 0.5 else nxt, 3)
# awal adegan (chunk pertama tiap adegan), 10 adegan
SC_CHUNK = [0, 4, 8, 12, 16, 22, 26, 31, 36, 40]
scenes = [0.0] + [round(out[c]["s"] - 0.15, 3) for c in SC_CHUNK[1:]]
CLOSE = round(max(out[-1]["e"] + 0.13, VO_LEN + LEAD - 0.1), 3)
scenes.append(CLOSE)
TOTAL = round(CLOSE + 1.5, 2)
json.dump({"lead": LEAD, "chunks": out, "scenes": scenes, "total": TOTAL, "vo_end": VO_LEN + LEAD}, open("timing.json", "w"), indent=1, ensure_ascii=False)
for k, c in enumerate(out): print(k, c["s"], c["show_end"], c["text"], "|", c["spoken"])
print("scenes", scenes, "TOTAL", TOTAL)
print("durasi adegan", [round(b - a, 2) for a, b in zip(scenes, scenes[1:] + [TOTAL])])
