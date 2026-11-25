"""Timing ARN-61 (Krakatau Anyer 1883) dari jeda VO nyata (ffmpeg silencedetect -30/-40 dB), TANPA Scribe.
Output timing.json (waktu video = VO + LEAD)."""
import json
LEAD = 0.3
SEGS = [
 (0.00, 0.96, "Kamu di pantai,"), (1.32, 3.06, "lautnya tiba-tiba mundur jauh."),
 (3.57, 4.23, "Kamu pilih apa?"), (4.77, 6.53, "Ikan-ikan menggelepar di depanmu."),
 (7.08, 8.08, "Bayangkan ini Anyer,"), (8.46, 11.75, "dua puluh tujuh Agustus seribu delapan ratus delapan puluh tiga."),
 (12.37, 13.06, "Di seberang selat,"), (13.42, 14.52, "Krakatau meledak."),
 (15.09, 18.53, "Dentumannya terdengar sampai empat ribu delapan ratus kilometer."),
 (19.17, 21.11, "Tapi yang paling mematikan bukan ledakannya."), (21.61, 22.00, "Coba tebak,"), (22.37, 22.60, "apa?"),
 (23.18, 24.40, "Lautnya sendiri."), (24.93, 27.64, "Gelombang tsunaminya sampai sekitar empat puluh meter."),
 (28.17, 31.19, "Tsunami merenggut lebih dari tiga puluh empat ribu nyawa."),
 (31.69, 32.10, "Jadi,"), (32.36, 32.77, "lari."), (33.25, 36.02, "Laut surut tiba-tiba itu salah satu tanda tsunami."),
 (36.47, 37.97, "Ikannya bukan rezeki."), (38.40, 40.70, "Pasti ada satu orang di rombonganmu yang bilang:"),
 (41.05, 43.35, "santai, nanti juga ada sirene."), (43.72, 44.50, "Masalahnya,"),
 (44.67, 46.29, "Desember dua ribu delapan belas,"), (46.42, 48.62, "tsunami Selat Sunda datang tanpa gempa."),
 (49.17, 50.15, "Kata BMKG,"), (50.49, 52.45, "waktu emasnya bisa kurang dari lima menit."),
 (52.86, 54.15, "Sirene tetap penting."), (54.57, 55.93, "Tapi laut mundur?"), (56.32, 57.59, "Itu alarm pertamamu:"),
 (57.92, 58.92, "lari ke tempat tinggi."), (59.36, 59.68, "Kamu:"), (60.01, 60.73, "lari duluan,"), (61.09, 62.30, "atau tunggu sirene?"),
]
# (teks layar, kata kunci kuning, jumlah kata yang diucapkan)
CHUNKS = [
 ("Kamu di pantai,", "pantai", 3), ("lautnya tiba-tiba", "tiba-tiba", 2), ("mundur jauh.", "mundur", 2),          # 0-2
 ("Kamu pilih apa?", "pilih", 3), ("Ikan-ikan menggelepar", "Ikan-ikan", 2), ("di depanmu.", "", 2),              # 3-5
 ("Bayangkan ini Anyer,", "Anyer", 3), ("27 Agustus 1883.", "1883", 10),                                         # 6-7
 ("Di seberang selat,", "selat", 3), ("Krakatau meledak.", "meledak", 2),                                         # 8-9
 ("Dentumannya terdengar", "terdengar", 2), ("sampai 4.800 kilometer.", "4.800", 6),                            # 10-11
 ("Tapi yang paling mematikan", "mematikan", 4), ("bukan ledakannya.", "bukan", 2), ("Coba tebak, apa?", "apa", 3),  # 12-14
 ("Lautnya sendiri.", "Lautnya", 2), ("Gelombang tsunaminya", "tsunaminya", 2), ("sampai sekitar 40 meter.", "40 meter", 5),  # 15-17
 ("Tsunami merenggut", "merenggut", 2), ("lebih dari 34.000 nyawa.", "34.000", 7),                             # 18-19
 ("Jadi, lari.", "lari", 2), ("Laut surut tiba-tiba", "surut", 3), ("itu salah satu", "", 3), ("tanda tsunami.", "tanda tsunami", 2),  # 20-23
 ("Ikannya bukan rezeki.", "bukan rezeki", 3),                                                                  # 24
 ("Pasti ada satu orang", "satu orang", 4), ("di rombonganmu yang bilang:", "rombonganmu", 4),                  # 25-26
 ("“santai, nanti", "santai", 2), ("juga ada sirene.”", "sirene", 3),                                            # 27-28
 ("Masalahnya,", "Masalahnya", 1), ("Desember 2018,", "2018", 5), ("tsunami Selat Sunda", "Selat Sunda", 3), ("datang tanpa gempa.", "tanpa gempa", 3),  # 29-32
 ("Kata BMKG,", "BMKG", 2), ("waktu emasnya", "waktu emas", 2), ("bisa kurang dari 5 menit.", "5 menit", 5),      # 33-35
 ("Sirene tetap penting.", "penting", 3), ("Tapi laut mundur?", "mundur", 3), ("Itu alarm pertamamu:", "alarm", 3), ("lari ke tempat tinggi.", "tempat tinggi", 4),  # 36-39
 ("Kamu: lari duluan,", "lari duluan", 3), ("atau tunggu sirene?", "tunggu sirene", 3),                          # 40-41
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
    assert not kw or kw in txt, (kw, txt)
    out.append({"text": txt, "kw": kw, "s": round(ws[0][1], 3), "e": round(ws[-1][2], 3), "spoken": " ".join(w[0] for w in ws)})
out[0]["s"] = 0.0
for k, c in enumerate(out):
    nxt = out[k + 1]["s"] if k + 1 < len(out) else c["e"] + 0.6
    c["show_end"] = round(min(nxt, c["e"] + 0.5) if nxt - c["e"] > 0.5 else nxt, 3)
# adegan naskah [1]..[13] -> chunk awal
SC_CHUNK = [0, 3, 6, 8, 12, 15, 18, 20, 25, 29, 33, 36, 40]
scenes = [0.0] + [round(out[c]["s"] - 0.15, 3) for c in SC_CHUNK[1:]]
VO_END = 62.30 + LEAD
CLOSE = round(VO_END + 0.1, 3)      # logo kecil sesudah VO selesai
scenes.append(CLOSE)
TOTAL = round(CLOSE + 1.2, 2)        # penutup <= 1,5 dtk
json.dump({"lead": LEAD, "chunks": out, "scenes": scenes, "total": TOTAL, "vo_end": VO_END}, open("timing.json", "w"), indent=1, ensure_ascii=False)
for k, c in enumerate(out): print(k, c["s"], c["show_end"], c["text"], "|", c["spoken"])
print("scenes", scenes, "TOTAL", TOTAL)
print("durasi adegan", [round(b - a, 2) for a, b in zip(scenes, scenes[1:] + [TOTAL])])
