"""ARN-46 Mana Lebih Hemat? #7 (motor cash vs kredit): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 51,33 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kata dicek dengan hitungan puncak energi (suku kata) per segmen.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (sore/build/motor): python3 ../../align_motor.py"""
import json, re

# segmen bicara (detik audio VO) = celah di antara jeda silencedetect
SEGS = [(0.05, 1.40), (1.56, 2.78), (3.19, 3.60), (3.88, 4.68),                          # 0-3   adegan 1 hook
        (5.14, 6.50), (6.64, 7.10), (7.23, 7.91), (8.34, 9.13), (9.32, 9.89),             # 4-8   adegan 2 komentar
        (10.26, 11.58), (12.09, 12.72), (12.92, 14.75),                                   # 9-11  adegan 3 cash
        (15.19, 15.52), (15.88, 17.73), (17.86, 19.88),                                   # 12-14 adegan 4 kredit
        (20.25, 21.26), (21.60, 22.38), (22.53, 24.21), (24.46, 25.57),                   # 15-18 adegan 5 47 bulan
        (25.94, 26.40), (26.65, 28.30), (28.61, 30.40),                                   # 19-21 adegan 6 total
        (30.70, 32.02), (32.32, 34.51),                                                   # 22-23 adegan 7 bunga
        (34.86, 36.58), (36.88, 37.56), (37.85, 39.80),                                   # 24-26 adegan 8 11 bulan
        (40.14, 42.91), (43.21, 43.75), (43.93, 44.61), (44.85, 45.87),                   # 27-30 adegan 9 rincian
        (46.22, 48.09), (48.50, 49.87), (50.23, 51.07)]                                   # 31-33 adegan 10 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris, 1 kata kunci (PRB-37)
CHUNKS = [
    [("KAMU", "kamu", []), ("BAYAR DUA MOTOR,", "bayar dua motor", ["DUA"])],   # frame 0: judul 4 kata + "KAMU" = 5
    [("YANG DIBAWA PULANG", "yang dibawa pulang", []), ("SATU.", "satu", ["SATU."])],
    [("COBA TEBAK,", "coba tebak", [])],
    [("SELISIHNYA BERAPA?", "selisihnya berapa", ["BERAPA?"])],
    [("KOMENTAR TERATAS", "komentar teratas", ["TERATAS"]), ("NOMOR 6,", "nomor enam", ["6,"])],
    [("JANJINYA", "janjinya", [])],
    [("TAMPIL DI SINI.", "tampil di sini", [])],
    [("MASIH KOSONG,", "masih kosong", ["KOSONG,"])],
    [("GILIRANMU.", "giliranmu", ["GILIRANMU."])],
    [("PATOKANNYA", "patokannya", []), ("HONDA BeAT.", "honda biit", ["BeAT."])],
    [("BAYAR CASH:", "bayar kes", ["CASH:"])],
    [("SEKITAR", "sekitar", []), ("Rp19,2 JUTA.", "sembilan belas koma dua juta", ["Rp19,2"])],
    [("KREDIT?", "kredit", ["KREDIT?"])],
    [("DP Rp4,9 JUTA,", "de pe empat koma sembilan juta", ["Rp4,9"])],
    [("CICILAN", "cicilan", []), ("Rp793 RIBU.", "tujuh ratus sembilan puluh tiga ribu", ["Rp793"])],
    [("KEDENGARANNYA RINGAN.", "kedengarannya ringan", ["RINGAN."])],
    [("MASALAHNYA,", "masalahnya", [])],
    [("ITU", "itu", []), ("47 BULAN.", "empat puluh tujuh bulan", ["47"])],
    [("HAMPIR 4 TAHUN.", "hampir empat tahun", ["4"])],
    [("TOTALNYA?", "totalnya", ["TOTALNYA?"])],
    [("Rp42,2 JUTA.", "empat puluh dua koma dua juta", ["Rp42,2"])],
    [("SELISIHNYA", "selisihnya", []), ("Rp23 JUTA.", "dua puluh tiga juta", ["Rp23"])],
    [("LEBIH MAHAL", "lebih mahal", ["MAHAL"]), ("DARI MOTORNYA!", "dari motornya", [])],
    [("SETARA BUNGA", "setara bunga", ["BUNGA"]), ("SEKITAR 5% SEBULAN.", "sekitar lima persen sebulan", ["5%"])],
    [("TAPI KALAU", "tapi kalau", []), ("TENORNYA 11 BULAN?", "tenornya sebelas bulan", ["11"])],
    [("CICILAN NAIK,", "cicilan naik", ["NAIK,"])],
    [("SELISIHNYA TINGGAL", "selisihnya tinggal", ["TINGGAL"]), ("Rp5,1 JUTA.", "lima koma satu juta", ["Rp5,1"])],
    [("JADI SEBELUM", "jadi sebelum", []), ("TANDA TANGAN,", "tanda tangan", ["TANGAN,"]),
     ("MINTA RINCIAN TERTULIS:", "minta rincian tertulis", ["TERTULIS:"])],
    [("ADMIN,", "admin", ["ADMIN,"])],
    [("ASURANSI,", "asuransi", ["ASURANSI,"])],
    [("TOTAL SAMPAI LUNAS.", "total sampai lunas", ["LUNAS."])],
    [("SATU MOTOR,", "satu motor", ["SATU"]), ("HARGANYA BISA DUA.", "harganya bisa dua", ["DUA."])],
    [("TIM NABUNG", "tim nabung", ["NABUNG"]), ("ATAU TIM KREDIT?", "atau tim kredit", ["KREDIT?"])],
    [("BELA DI KOMENTAR!", "bela di komentar", ["KOMENTAR!"])],
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
for i, c in enumerate(out):
    print(i, c["seg"], c["start"], c["end"], c["text"])
