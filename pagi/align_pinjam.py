"""ARN-49 Mana Lebih Hemat? #9 (uang dipinjam teman setahun): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 72,80 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen (±6-7 suku kata/dtk). Segmen 24,64-30,48
(tanpa jeda -30 dB) dipecah di lembah energi 26,05 dan 28,35 (RMS 50 ms).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build/pinjam): python3 ../../align_pinjam.py"""
import json, re

SEGS = [(0.00, 1.20), (1.62, 2.79),                                     # 0-1   adegan 0 hook
        (3.25, 3.69), (4.07, 5.29),                                     # 2-3   adegan 1 coba tebak
        (5.83, 7.08), (7.62, 8.56), (9.02, 9.76), (9.96, 10.44),        # 4-7   adegan 2 kenal dia
        (10.91, 11.86), (12.34, 13.42), (13.85, 15.17),                 # 8-10  adegan 3 lewat, liburan
        (15.65, 16.52), (16.74, 17.81), (18.14, 18.68),                 # 11-13 adegan 4 balik utuh
        (19.14, 19.61), (20.06, 22.24), (22.47, 24.06),                 # 14-16 adegan 5 inflasi 3,23%
        (24.64, 26.05), (26.10, 28.35),                                 # 17-18 adegan 6 daya beli tinggal
        (28.45, 30.48),                                                 # 19    adegan 7 PUNCAK Rp968.700
        (31.09, 32.33), (32.69, 33.73),                                 # 20-21 adegan 8 menguap
        (34.17, 34.91), (35.34, 37.99),                                 # 22-23 adegan 9 deposito 3,75%
        (38.13, 39.16), (39.29, 41.25),                                 # 24-25 adegan 10 +Rp37.500
        (41.67, 43.30), (43.47, 44.35),                                 # 26-27 adegan 11 kamu nanggung
        (44.74, 46.32), (46.73, 48.14),                                 # 28-29 adegan 12 tim nunggu: canggung
        (48.59, 51.66),                                                 # 30    adegan 13 pertemanan
        (52.13, 54.38),                                                 # 31    adegan 14 pernah nolong
        (54.80, 56.07), (56.46, 57.67), (57.86, 59.79),                 # 32-34 adegan 15 tim tagih balas
        (60.21, 61.09), (61.37, 62.05), (62.18, 63.23), (63.47, 64.13), # 35-38 adegan 16 jalan tengah
        (64.64, 67.39), (67.64, 68.60),                                 # 39-40 adegan 17 chat pribadi
        (69.03, 70.30), (70.68, 72.58)]                                 # 41-42 adegan 18 penutup

# "|" = subtitle dipecah jadi 2 layar berurutan dalam waktu chunk yang sama
# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("UANGMU DI", "uangmu di", []), ("TANGAN TEMAN,", "tangan teman", ["TEMAN,"])],
    [("TIAP BULAN", "tiap bulan", []), ("MENGECIL.", "mengecil", ["MENGECIL."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("SETAHUN HILANG", "setahun hilang", []), ("BERAPA?", "berapa", ["BERAPA?"])],
    [("KAMU PASTI", "kamu pasti", []), ("KENAL DIA.", "kenal dia", ["DIA."])],
    [("PINJAM SATU JUTA:", "pinjam satu juta", ["JUTA:"])],
    [("\"BULAN DEPAN YA,", "bulan depan ya", ["DEPAN"])],
    [("PASTI!\"", "pasti", ["PASTI!\""])],
    [("BULAN DEPAN LEWAT.", "bulan depan lewat", ["LEWAT."])],
    [("TIGA BULAN LEWAT.", "tiga bulan lewat", ["TIGA"])],
    [("DIA MALAH", "dia malah", []), ("POSTING LIBURAN.", "posting liburan", ["LIBURAN."])],
    [("SETAHUN KEMUDIAN,", "setahun kemudian", ["SETAHUN"])],
    [("UANGMU BALIK UTUH.", "uangmu balik utuh", ["UTUH."])],
    [("AMAN, KAN?", "aman kan", ["AMAN,"])],
    [("TUNGGU DULU.", "tunggu dulu", ["TUNGGU"])],
    [("INFLASI TAHUNAN", "inflasi tahunan", ["INFLASI"]), ("BPS OKTOBER LALU:", "be pe es oktober lalu", ["BPS"])],
    [("3,23 PERSEN.", "tiga koma dua tiga persen", ["3,23"])],
    [("KALAU HARGA", "kalau harga", []), ("NAIK SEGITU,", "naik segitu", ["NAIK"])],
    [("DAYA BELI", "daya beli", ["BELI"]), ("SATU JUTAMU", "satu jutamu", []), ("TINGGAL…", "tinggal", ["TINGGAL…"])],
    [("Rp968.700.", "sembilan ratus enam puluh delapan ribu", ["Rp968.700."])],
    [("Rp31 RIBU", "tiga puluh satu ribu", ["Rp31"]), ("MENGUAP,", "menguap", [])],
    [("TANPA ADA", "tanpa ada", []), ("YANG NYOLONG.", "yang nyolong", ["NYOLONG."])],
    [("BELUM SELESAI.", "belum selesai", ["BELUM"])],
    [("DI DEPOSITO", "di deposito", ["DEPOSITO"]), ("BERBUNGA", "berbunga", []),
     ("3,75 PERSEN,", "tiga koma tujuh lima persen", ["3,75"])],
    [("SATU JUTAMU", "satu jutamu", []), ("MALAH TUMBUH", "malah tumbuh", ["TUMBUH"])],
    [("Rp37.500.", "tiga puluh tujuh ribu lima ratus", ["Rp37.500."])],
    [("JADI DIA PINJAM", "jadi dia pinjam", []), ("TANPA BUNGA,", "tanpa bunga", ["BUNGA,"])],
    [("KAMU YANG NANGGUNG.", "kamu yang nanggung", ["NANGGUNG."])],
    [("TAPI TIM NUNGGU", "tapi tim nunggu", ["NUNGGU"]), ("PUNYA ALASAN.", "punya alasan", [])],
    [("NAGIH TEMAN", "nagih teman", []), ("ITU CANGGUNG.", "itu canggung", ["CANGGUNG."])],
    [("Rp30 RIBUAN", "tiga puluh ribuan", ["Rp30"]), ("NGGAK SEBANDING", "nggak sebanding", []),
     ("DENGAN PERTEMANAN", "dengan pertemanan", ["PERTEMANAN"]), ("BERTAHUN-TAHUN.", "bertahun tahun", [])],
    [("LAGIAN,", "lagian", []), ("DIA JUGA PERNAH", "dia juga pernah", []), ("NOLONGIN KAMU.", "nolongin kamu", ["NOLONGIN"])],
    [("TIM LANGSUNG TAGIH", "tim langsung tagih", ["TAGIH"]), ("BALAS:", "balas", [])],
    [("JUSTRU KARENA", "justru karena", []), ("TEMAN,", "teman", ["TEMAN,"])],
    [("JANGAN BIARKAN", "jangan biarkan", []), ("UTANG JADI", "utang jadi", []), ("GANJALAN.", "ganjalan", ["GANJALAN."])],
    [("JALAN TENGAHNYA:", "jalan tengahnya", ["TENGAHNYA:"])],
    [("UBAH \"BULAN DEPAN\"", "ubah bulan depan", ["DEPAN\""])],
    [("JADI TANGGAL,", "jadi tanggal", ["TANGGAL,"])],
    [("SEJAK AWAL.", "sejak awal", ["AWAL."])],
    [("LEWAT TANGGAL,", "lewat tanggal", []), ("INGATKAN SANTAI", "ingatkan santai", ["SANTAI"]),
     ("LEWAT CHAT PRIBADI,", "lewat chat pribadi", ["PRIBADI,"])],
    [("BUKAN SINDIRAN GRUP.", "bukan sindiran grup", ["GRUP."])],
    [("KAMU TIM", "kamu tim", []), ("LANGSUNG TAGIH,", "langsung tagih", ["TAGIH,"])],
    [("ATAU TIM NUNGGU", "atau tim nunggu", ["NUNGGU"]), ("DIA INGAT SENDIRI?", "dia ingat sendiri", [])],
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
