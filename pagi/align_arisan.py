"""ARN-51 Mana Lebih Hemat? #10 (arisan dapat pertama vs terakhir): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 67,60 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen. Segmen pendek yang menempel digabung:
4,49-4,76 + 4,89-5,61 ("kamu | pasti kenal"), 58,03-58,59 + 58,74-58,85, 65,88-66,31 + 66,44-67,34.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_arisan): python3 ../align_arisan.py"""
import json, re

SEGS = [(0.00, 2.39),                                                   # 0     adegan 0 hook
        (2.91, 3.33), (3.64, 3.99),                                     # 1-2   adegan 1 coba tebak
        (4.49, 5.61), (6.09, 6.85), (7.26, 8.11), (8.34, 9.58),         # 3-6   adegan 2 kocokan, Bu Yanti
        (10.07, 12.18),                                                 # 7     adegan 3 nama paling akhir
        (12.33, 12.97), (13.47, 14.61), (14.92, 16.30), (16.51, 17.98), # 8-11  adegan 4 tiga angka
        (18.31, 20.89),                                                 # 12    adegan 5 no.1 pinjam
        (21.30, 21.80), (22.16, 23.37), (23.62, 24.66),                 # 13-15 adegan 6 no.10 nabung
        (24.97, 28.48),                                                 # 16    adegan 7 LPS 3,75%
        (28.85, 31.80),                                                 # 17    adegan 8 setor sendiri
        (32.01, 34.65),                                                 # 18    adegan 9 -Rp70.300
        (34.97, 36.37), (36.67, 37.97),                                 # 19-20 adegan 10 no.1 +Rp70.300
        (38.27, 39.97), (40.15, 41.50),                                 # 21-22 adegan 11 PUNCAK Rp140 rb
        (41.89, 43.62), (43.87, 46.46),                                 # 23-24 adegan 12 tim arisan
        (46.83, 47.94), (48.22, 49.48),                                 # 25-26 adegan 13 rem
        (49.78, 52.58),                                                 # 27    adegan 14 kumpul
        (52.92, 54.23), (54.46, 56.67),                                 # 28-29 adegan 15 autodebet
        (56.94, 57.77), (58.03, 58.85), (59.17, 60.24),                 # 30-32 adegan 16 urutan awal
        (60.52, 61.21), (61.44, 62.66), (62.82, 64.01),                 # 33-35 adegan 17 nggak buru-buru
        (64.31, 65.67), (65.88, 67.34)]                                 # 36-37 adegan 18 penutup

# "|" = subtitle dipecah jadi 2 layar berurutan dalam waktu chunk yang sama
# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("KAMU PALING RUGI", "kamu paling rugi", ["RUGI"]), ("KALAU DAPAT ARISAN", "kalau dapat arisan", ["ARISAN"]),
     ("TERAKHIR.", "terakhir", ["TERAKHIR."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("BERAPA?", "berapa", ["BERAPA?"])],
    [("KAMU PASTI KENAL:", "kamu pasti kenal", ["KENAL:"])],
    [("GELAS DIKOCOK,", "gelas dikocok", ["DIKOCOK,"])],
    [("\"BU YANTI!\"", "bu yanti", ["YANTI!\""])],
    [("SEMUA TEPUK TANGAN.", "semua tepuk tangan", ["TANGAN."])],
    [("DAN SELALU ADA", "dan selalu ada", []), ("SATU NAMA", "satu nama", ["NAMA"]),
     ("YANG KELUAR", "yang keluar", []), ("PALING AKHIR.", "paling akhir", ["AKHIR."])],
    [("MISALNYA", "misalnya", [])],
    [("SEPULUH ORANG,", "sepuluh orang", ["SEPULUH"])],
    [("IURAN Rp500 RIBU,", "iuran lima ratus ribu", ["Rp500"])],
    [("TIAP BULAN", "tiap bulan", []), ("CAIR Rp5 JUTA.", "cair lima juta", ["Rp5"])],
    [("YANG PERTAMA", "yang pertama", ["PERTAMA"]), ("KAYAK PINJAM", "kayak pinjam", ["PINJAM"]),
     ("Rp5 JUTA", "lima juta", []), ("TANPA BUNGA.", "tanpa bunga", ["BUNGA."])],
    [("YANG TERAKHIR?", "yang terakhir", ["TERAKHIR?"])],
    [("MENABUNG", "menabung", ["MENABUNG"]), ("SEPULUH BULAN,", "sepuluh bulan", [])],
    [("JUGA TANPA BUNGA.", "juga tanpa bunga", ["BUNGA."])],
    [("PADAHAL BUNGA", "padahal bunga", ["BUNGA"]), ("PENJAMINAN LPS", "penjaminan el pe es", ["LPS"]),
     ("3,75 PERSEN.", "tiga koma tujuh lima persen", ["3,75"])],
    [("SETOR SENDIRI", "setor sendiri", ["SENDIRI"]), ("Rp500 RIBU", "lima ratus ribu", ["Rp500"]),
     ("KE DEPOSITO", "ke deposito", ["DEPOSITO"]), ("TIAP BULAN,", "tiap bulan", [])],
    [("BULAN KESEPULUH", "bulan kesepuluh", ["KESEPULUH"]), ("DAPAT BUNGA", "dapat bunga", []),
     ("SEKITAR Rp70 RIBU.", "sekitar tujuh puluh ribu", ["Rp70"])],
    [("SI NOMOR SATU", "si nomor satu", ["SATU"]), ("KEBALIKANNYA,", "kebalikannya", [])],
    [("UNTUNG", "untung", ["UNTUNG"]), ("KIRA-KIRA SEGITU.", "kira kira segitu", [])],
    [("JARAK YANG PERTAMA", "jarak yang pertama", ["PERTAMA"]), ("DAN YANG TERAKHIR:", "dan yang terakhir", ["TERAKHIR:"])],
    [("Rp140 RIBU.", "seratus empat puluh ribu", ["Rp140"])],
    [("TAPI TIM ARISAN", "tapi tim arisan", ["ARISAN"]), ("PUNYA ALASAN:", "punya alasan", [])],
    [("TANPA KOCOKAN,", "tanpa kocokan", ["KOCOKAN,"]), ("UANGNYA HABIS", "uangnya habis", []),
     ("BUAT JAJAN.", "buat jajan", ["JAJAN."])],
    [("ARISAN ITU REM.", "arisan itu rem", ["REM."])],
    [("MALU KALAU", "malu kalau", ["MALU"]), ("TELAT SETOR.", "telat setor", [])],
    [("DAN KUMPUL", "dan kumpul", ["KUMPUL"]), ("SEBULAN SEKALI", "sebulan sekali", []),
     ("NGGAK BISA DIHITUNG", "nggak bisa dihitung", []), ("PAKAI BUNGA.", "pakai bunga", ["BUNGA."])],
    [("TIM NABUNG SENDIRI", "tim nabung sendiri", ["NABUNG"]), ("BALAS:", "balas", [])],
    [("REMNYA CUKUP", "remnya cukup", []), ("AUTODEBET", "autodebet", ["AUTODEBET"]),
     ("TANGGAL GAJIAN.", "tanggal gajian", ["GAJIAN."])],
    [("JALAN TENGAHNYA:", "jalan tengahnya", ["TENGAHNYA:"])],
    [("BUTUH UANG CEPAT,", "butuh uang cepat", ["CEPAT,"])],
    [("MINTA URUTAN AWAL.", "minta urutan awal", ["AWAL."])],
    [("NGGAK BURU-BURU?", "nggak buru buru", ["BURU-BURU?"])],
    [("IKUT BUAT", "ikut buat", []), ("KUMPULNYA,", "kumpulnya", ["KUMPULNYA,"])],
    [("SISANYA", "sisanya", []), ("NABUNG SENDIRI.", "nabung sendiri", ["SENDIRI."])],
    [("KAMU TIM", "kamu tim", []), ("DAPAT DULUAN,", "dapat duluan", ["DULUAN,"])],
    [("ATAU TIM DAPAT", "atau tim dapat", []), ("BELAKANGAN?", "belakangan", ["BELAKANGAN?"])],
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
