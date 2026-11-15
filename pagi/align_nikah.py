"""ARN-52 Mana Lebih Hemat? #11 (nikah di gedung vs di rumah): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 66,04 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen. Segmen pendek yang menempel digabung:
4,82-5,05 + 5,21-5,98 ("kamu | pasti kenal"), 10,64-11,97 + 12,10-12,40, 27,99-29,05 + 29,19-29,43 + 29,61-30,94,
35,33-36,77 + 36,89-37,08, 42,70-45,40 + 45,69-46,56. Segmen 50,17-53,06 dipecah di lembah energi 51,10
(silencedetect -35 dB d=0,06): "tanpa cuci piring" | "jalan tengahnya, sebelum DP, tanyakan tiga hal".
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_nikah): python3 ../align_nikah.py"""
import json, re

SEGS = [(0.00, 2.36),                                                   # 0     adegan 0 hook
        (2.69, 3.20), (3.57, 4.37),                                     # 1-2   adegan 1 coba tebak
        (4.82, 5.98), (6.44, 8.40),                                     # 3-4   adegan 2 tetangga masak
        (8.65, 9.30), (9.61, 10.31),                                    # 5-6   adegan 3 tante
        (10.64, 12.40), (12.72, 15.62),                                 # 7-8   adegan 4 rumah gratis / kursi
        (16.07, 18.11),                                                 # 9     adegan 5 contoh 300 tamu
        (18.56, 20.36), (20.59, 21.72),                                 # 10-11 adegan 6 tenda
        (22.09, 23.10), (23.32, 24.43),                                 # 12-13 adegan 7 kursi
        (24.78, 25.89), (26.05, 27.64),                                 # 14-15 adegan 8 genset & sound
        (27.99, 30.94),                                                 # 16    adegan 9 struk 16 jt
        (31.28, 35.09),                                                 # 17    adegan 10 gedung 6,5 jt
        (35.33, 37.08),                                                 # 18    adegan 11 PUNCAK selisih
        (37.67, 39.27),                                                 # 19    adegan 12 tim rumah
        (39.52, 40.86), (41.15, 42.48),                                 # 20-21 adegan 13 pinjam RT, patungan
        (42.70, 46.56),                                                 # 22    adegan 14 tetangga masak
        (46.81, 47.69), (47.86, 48.84), (48.99, 49.87), (50.17, 51.10), # 23-26 adegan 15 tim gedung
        (51.15, 53.06),                                                 # 27    adegan 16 jalan tengah
        (53.36, 54.52), (54.88, 56.48), (56.70, 57.91),                 # 28-30 adegan 17 tiga pertanyaan
        (58.17, 59.90), (60.18, 60.95), (61.21, 61.93), (62.14, 63.38), # 31-34 adegan 18 timbangan
        (63.68, 64.59), (64.85, 65.74)]                                 # 35-36 adegan 19 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("KAMU BISA NOMBOK", "kamu bisa nombok", ["NOMBOK"]), ("GARA-GARA TENDA BIRU.", "gara gara tenda biru", ["BIRU."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("BOCORNYA DI MANA?", "bocornya di mana", ["BOCORNYA"])],
    [("KAMU PASTI KENAL:", "kamu pasti kenal", ["KENAL:"])],
    [("TETANGGA BANTU MASAK", "tetangga bantu masak", ["MASAK"]), ("SEJAK SUBUH,", "sejak subuh", ["SUBUH,"])],
    [("TANTE NANYA,", "tante nanya", ["TANTE"])],
    [("\"KAPAN NYUSUL?\"", "kapan nyusul", ["NYUSUL?\""])],
    [("KATANYA RUMAH", "katanya rumah", ["RUMAH"]), ("SENDIRI GRATIS.", "sendiri gratis", ["GRATIS."])],
    [("MASALAHNYA,", "masalahnya", []), ("RUMAH NGGAK DATANG", "rumah nggak datang", []),
     ("BERSAMA KURSI.", "bersama kursi", ["KURSI."])],
    [("CONTOH 300 TAMU", "contoh tiga ratus tamu", ["300"]), ("DI BEKASI.", "di bekasi", ["BEKASI."])],
    [("TENDA 200 M²:", "tenda dua ratus meter persegi", ["TENDA"])],
    [("Rp6,6 JUTA.", "enam koma enam juta", ["Rp6,6"])],
    [("300 KURSI:", "tiga ratus kursi", ["KURSI:"])],
    [("Rp4,2 JUTA.", "empat koma dua juta", ["Rp4,2"])],
    [("GENSET DAN SOUND:", "genset dan sound", ["SOUND:"])],
    [("Rp5,55 JUTA.", "lima koma lima lima juta", ["Rp5,55"])],
    [("BELUM ADA", "belum ada", []), ("NASI SEBUTIR,", "nasi sebutir", ["NASI"]),
     ("SUDAH Rp16 JUTA LEBIH.", "sudah enam belas juta lebih", ["Rp16"])],
    [("PADAHAL ADA GEDUNG", "padahal ada gedung", ["GEDUNG"]), ("SIANG DI BEKASI", "siang di bekasi", []),
     ("YANG DISEWA", "yang disewa", []), ("Rp6,5 JUTA.", "enam setengah juta", ["Rp6,5"])],
    [("SELISIHNYA", "selisihnya", []), ("HAMPIR Rp10 JUTA.", "hampir sepuluh juta", ["Rp10"])],
    [("TAPI TIM RUMAH", "tapi tim rumah", ["RUMAH"]), ("PUNYA JAWABAN.", "punya jawaban", ["JAWABAN."])],
    [("KURSI BISA PINJAM RT,", "kursi bisa pinjam er te", ["RT,"])],
    [("TENDA PATUNGAN", "tenda patungan", ["PATUNGAN"]), ("KELUARGA.", "keluarga", [])],
    [("DAN TETANGGA", "dan tetangga", ["TETANGGA"]), ("YANG BANTU MASAK", "yang bantu masak", []),
     ("NGGAK ADA", "nggak ada", []), ("DI PAKET GEDUNG.", "di paket gedung", ["PAKET"])],
    [("TIM GEDUNG BALAS:", "tim gedung balas", ["GEDUNG"])],
    [("4 JAM BERES,", "empat jam beres", ["BERES,"])],
    [("TANPA TUTUP JALAN,", "tanpa tutup jalan", ["JALAN,"])],
    [("TANPA CUCI PIRING.", "tanpa cuci piring", ["PIRING."])],
    [("JALAN TENGAHNYA,", "jalan tengahnya", ["TENGAHNYA,"]), ("SEBELUM DP,", "sebelum de pe", ["DP,"]),
     ("TANYAKAN 3 HAL.", "tanyakan tiga hal", ["3"])],
    [("KURSI & SOUND", "kursi dan sound", []), ("TERMASUK?", "termasuk", ["TERMASUK?"])],
    [("LEWAT JAM,", "lewat jam", ["JAM,"]), ("DENDANYA BERAPA?", "dendanya berapa", ["DENDANYA"])],
    [("BOLEH BAWA", "boleh bawa", []), ("KATERING SENDIRI?", "katering sendiri", ["KATERING"])],
    [("KURSI & TENDA", "kursi dan tenda", []), ("BISA DIPINJAM?", "bisa dipinjam", ["DIPINJAM?"])],
    [("RUMAH MENANG.", "rumah menang", ["RUMAH"])],
    [("SEMUA SEWA?", "semua sewa", ["SEWA?"])],
    [("GEDUNG BISA", "gedung bisa", ["GEDUNG"]), ("LEBIH HEMAT.", "lebih hemat", ["HEMAT."])],
    [("KAMU TIM GEDUNG,", "kamu tim gedung", ["GEDUNG,"])],
    [("ATAU TIM DI RUMAH?", "atau tim di rumah", ["RUMAH?"])],
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
