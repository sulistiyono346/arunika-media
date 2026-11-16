"""ARN-56 Mana Lebih Hemat? #13 (LDR vs satu kota): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 65,72 dtk; lembah -36 dB d=0.05 untuk cek segmen panjang).
TANPA Scribe. Pemetaan segmen -> kalimat dicek dengan DP hitungan suku kata (laju ±6,2 suku kata/dtk).
Segmen 16,89-17,40 + 17,55-18,25 digabung (bensin tiga puluh ribu); 18,81-19,16 + 19,29-19,40 digabung (empat Sabtu);
49,02-49,15 + 49,30-49,79 digabung ("Tapi..."), lalu 50,18-51,29 = "Tim satu kota balas"; 31,81-32,86 dan 33,01-34,05
dipisah (dua kencan di sana | empat ratus ribu); 26,12-28,02 | 28,10-28,90 (lembah -36 dB) kereta | enam ratus ribu.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_ldr): python3 ../align_ldr.py"""
import json, re

SEGS = [(0.00, 0.877), (1.378, 3.021),                  # 0-1  hook
        (3.465, 4.028), (4.283, 5.426),                 # 2-3  coba tebak
        (5.957, 9.476),                                 # 4    teman tiap Jumat malam lari ke Stasiun Senen
        (10.021, 10.752), (11.131, 12.202),             # 5-6  satu kota dulu: kencan tiap Sabtu
        (12.646, 13.496), (13.672, 14.356),             # 7-8  nonton berdua, seratus ribu
        (14.803, 15.602), (15.762, 16.431),             # 9-10 makan berdua, seratus ribu
        (16.888, 18.254),                               # 11   bensin tiga puluh ribu
        (18.811, 19.401), (19.808, 21.448),             # 12-13 empat Sabtu: 920 rb
        (21.921, 25.585),                               # 14   sekarang LDR
        (26.121, 28.018), (28.098, 28.899),             # 15-16 kereta, 600 rb
        (29.361, 31.395),                               # 17   penginapan
        (31.807, 32.860), (33.006, 34.052),             # 18-19 dua kencan, 400 rb
        (34.489, 36.276), (36.757, 37.723), (38.224, 38.654),   # 20-22 total 1,3 jt, LDR kalah, selesai?
        (39.129, 39.401), (39.773, 40.784),             # 23-24 tunggu, tim LDR menjawab
        (41.289, 44.537),                               # 25   pesan jauh hari, Rp74 rb
        (44.941, 47.625), (47.899, 48.507), (49.019, 49.794),   # 26-28 Rp848 rb, lebih murah, tapi
        (50.184, 51.289), (51.684, 53.347),             # 29-30 tim satu kota balas
        (53.599, 55.107),                               # 31   tinggal Rp720 rb
        (55.529, 56.884), (57.143, 58.653),             # 32-33 penentunya
        (59.186, 59.821), (60.123, 61.323), (61.527, 62.929),   # 34-36 biar adil
        (63.374, 64.322), (64.541, 65.424)]             # 37-38 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("LDR IRIT?", "el de er irit", ["IRIT?"])],
    [("DOMPETMU JEBOL", "dompetmu jebol", ["JEBOL"]), ("TIAP KETEMU.", "tiap ketemu", ["KETEMU."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("MANA LEBIH MAHAL", "mana lebih mahal", ["MAHAL"]), ("SEBULAN?", "sebulan", [])],
    [("KAMU PASTI KENAL", "kamu pasti kenal", ["KENAL"]), ("TEMAN YANG TIAP", "teman yang tiap", []),
     ("JUMAT MALAM LARI", "jumat malam lari", ["JUMAT"]), ("KE STASIUN SENEN.", "ke stasiun senen", ["SENEN."])],
    [("SATU KOTA DULU:", "satu kota dulu", ["KOTA"])],
    [("KENCAN TIAP SABTU.", "kencan tiap sabtu", ["SABTU."])],
    [("NONTON BERDUA,", "nonton berdua", ["NONTON"])],
    [("Rp100 RIBU.", "seratus ribu", ["Rp100"])],
    [("MAKAN BERDUA,", "makan berdua", ["MAKAN"])],
    [("Rp100 RIBU.", "seratus ribu", ["Rp100"])],
    [("BENSIN", "bensin", ["BENSIN"]), ("Rp30 RIBU.", "tiga puluh ribu", ["Rp30"])],
    [("EMPAT SABTU:", "empat sabtu", ["SABTU:"])],
    [("Rp920 RIBU.", "sembilan ratus dua puluh ribu", ["Rp920"])],
    [("SEKARANG LDR", "sekarang el de er", ["LDR"]), ("JAKARTA–JOGJA,", "jakarta jogja", []),
     ("KETEMU SEBULAN SEKALI.", "ketemu sebulan sekali", ["SEBULAN"])],
    [("KERETA EKONOMI", "kereta ekonomi", ["KERETA"]), ("PREMIUM PULANG PERGI,", "premium pulang pergi", ["PREMIUM"])],
    [("Rp600 RIBU.", "enam ratus ribu", ["Rp600"])],
    [("PENGINAPAN", "penginapan", ["PENGINAPAN"]), ("DUA MALAM,", "dua malam", []),
     ("Rp300 RIBU.", "tiga ratus ribu", ["Rp300"])],
    [("DUA KENCAN", "dua kencan", ["KENCAN"]), ("DI SANA,", "di sana", [])],
    [("Rp400 RIBU.", "empat ratus ribu", ["Rp400"])],
    [("TOTAL Rp1,3 JUTA.", "total satu koma tiga juta", ["Rp1,3"])],
    [("LDR KALAH.", "el de er kalah", ["KALAH."])],
    [("SELESAI?", "selesai", ["SELESAI?"])],
    [("TUNGGU,", "tunggu", ["TUNGGU,"])],
    [("TIM LDR", "tim el de er", ["LDR"]), ("MENJAWAB.", "menjawab", [])],
    [("PESAN JAUH HARI,", "pesan jauh hari", ["JAUH"]), ("KERETA EKONOMI", "kereta ekonomi", ["EKONOMI"]),
     ("MULAI Rp74 RIBU.", "mulai tujuh puluh empat ribu", ["Rp74"])],
    [("TOTALNYA JADI", "totalnya jadi", []), ("Rp848 RIBU.", "delapan ratus empat puluh delapan ribu", ["Rp848"])],
    [("LEBIH MURAH.", "lebih murah", ["MURAH."])],
    [("TAPI…", "tapi", ["TAPI…"])],
    [("TIM SATU KOTA", "tim satu kota", ["KOTA"]), ("BALAS:", "balas", [])],
    [("NONTON CUKUP", "nonton cukup", ["NONTON"]), ("2 MINGGU SEKALI.", "dua minggu sekali", ["2"])],
    [("TINGGAL", "tinggal", []), ("Rp720 RIBU.", "tujuh ratus dua puluh ribu", ["Rp720"])],
    [("JADI PENENTUNYA", "jadi penentunya", []), ("BUKAN JARAK,", "bukan jarak", ["JARAK,"])],
    [("TAPI SEBERAPA", "tapi seberapa", []), ("SERING KETEMU.", "sering ketemu", ["SERING"])],
    [("BIAR ADIL:", "biar adil", ["ADIL:"])],
    [("YANG BERANGKAT", "yang berangkat", ["BERANGKAT"]), ("BAYAR TIKET,", "bayar tiket", ["TIKET,"])],
    [("YANG DITUNGGU", "yang ditunggu", ["DITUNGGU"]), ("BAYAR KENCAN.", "bayar kencan", ["KENCAN."])],
    [("KAMU TIM LDR,", "kamu tim el de er", ["LDR,"])],
    [("ATAU TIM", "atau tim", []), ("SATU KOTA?", "satu kota", ["KOTA?"])],
]
assert len(SEGS) == len(CHUNKS), (len(SEGS), len(CHUNKS))


def syl(word):
    return max(1, len(re.findall(r"[aiueo]+", word.lower())))


out = []
for si, ((s, e), chunks) in enumerate(zip(SEGS, CHUNKS)):
    weights = [sum(syl(w) + 0.4 for w in sp.split()) for _, sp, _ in chunks]
    tot = sum(weights)
    t = s
    for (disp, sp, keys), wgt in zip(chunks, weights):
        d = (e - s) * wgt / tot
        out.append({"text": disp, "keys": keys, "seg": si, "start": round(t, 3), "end": round(t + d, 3)})
        t += d

json.dump(out, open("timing.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "chunk")
