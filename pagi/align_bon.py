"""ARN-47 Mana Lebih Hemat? #8 (bon makan bareng, bagi rata vs bayar masing-masing): waktu chunk subtitle
dari jeda VO nyata (ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 63,56 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen (±5-8 suku kata/dtk di semua segmen).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build/bon): python3 ../../align_bon.py"""
import json, re

SEGS = [(0.06, 2.06), (2.52, 2.95), (3.34, 4.85),                       # 0-2   adegan 0 hook
        (5.33, 7.01), (7.45, 9.01), (9.23, 9.95),                       # 3-5   adegan 1 meja
        (10.35, 11.07), (11.37, 12.95), (13.31, 14.59),                 # 6-8   adegan 2 si paling mahal
        (14.95, 16.92), (17.34, 18.34), (18.69, 19.23),                 # 9-11  adegan 3 total + patungan
        (19.59, 20.21), (20.42, 21.77), (22.14, 24.18),                 # 12-14 adegan 4 bagi rata
        (24.57, 25.95), (26.31, 26.70), (27.06, 27.72),                 # 15-17 adegan 5 nombok
        (28.11, 31.69),                                                 # 18    adegan 6 sebulan
        (32.06, 32.50), (32.86, 34.87),                                 # 19-20 adegan 7 setahun (puncak)
        (35.22, 36.99), (37.37, 39.27),                                 # 21-22 adegan 8 tim rata: kasir ribet
        (39.79, 42.42),                                                 # 23    adegan 9 minggu depan gantian
        (42.87, 46.02),                                                 # 24    adegan 10 soal teman
        (46.33, 47.84), (48.15, 50.31),                                 # 25-26 adegan 11 tim masing-masing
        (50.70, 51.84), (52.16, 53.86), (54.01, 56.07),                 # 27-29 adegan 12 jalan tengah
        (56.44, 57.62), (57.82, 59.88),                                 # 30-31 adegan 13 sepakati
        (60.22, 61.60), (61.73, 63.29)]                                 # 32-33 adegan 14 penutup

# "|" = subtitle dipecah jadi 2 layar berurutan dalam waktu chunk yang sama (biar 1 baris tetap besar)
# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("KAMU BAYAR", "kamu bayar", []), ("DUA KALI LIPAT", "dua kali lipat", ["DUA"]), ("PESANANMU.", "pesananmu", [])],
    [("COBA TEBAK,", "coba tebak", [])],
    [("SETAHUN KAMU", "setahun kamu", []), ("NOMBOK BERAPA?", "nombok berapa", ["BERAPA?"])],
    [("SATU MEJA,", "satu meja", []), ("EMPAT ORANG.", "empat orang", ["EMPAT"])],
    [("NASI GORENG", "nasi goreng", []), ("PLUS ES TEHMU:", "plus es tehmu", ["TEHMU:"])],
    [("Rp30 RIBU.", "tiga puluh ribu", ["Rp30"])],
    [("TERUS ADA DIA:", "terus ada dia", ["DIA:"])],
    [("YANG SELALU PESAN", "yang selalu pesan", []), ("PALING MAHAL.", "paling mahal", ["MAHAL."])],
    [("Rp120 RIBU.", "seratus dua puluh ribu", ["Rp120"])],
    [("TOTAL", "total", []), ("Rp240 RIBU.", "dua ratus empat puluh ribu", ["Rp240"])],
    [("LALU DIA BILANG,", "lalu dia yang bilang", ["DIA"])],
    [("\"PATUNGAN YA!\"", "patungan ya", ["\"PATUNGAN"])],
    [("BAGI RATA,", "bagi rata", ["RATA,"])],
    [("MASING-MASING", "masing-masing", []), ("Rp60 RIBU.", "enam puluh ribu", ["Rp60"])],
    [("PADAHAL PESANANMU", "padahal pesananmu", []), ("CUMA SETENGAHNYA.", "cuma setengahnya", ["SETENGAHNYA."])],
    [("KAMU NOMBOK", "kamu nombok", ["NOMBOK"]), ("Rp30 RIBU.", "tiga puluh ribu", ["Rp30"])],
    [("KECIL?", "kecil", ["KECIL?"])],
    [("TUNGGU DULU.", "tunggu dulu", [])],
    [("KALAU NONGKRONGNYA", "kalau nongkrongnya", []), ("SEMINGGU SEKALI,", "seminggu sekali", ["SEKALI,"]),
     ("SEBULAN", "sebulan", []), ("Rp120 RIBU.", "seratus dua puluh ribu", ["Rp120"])],
    [("SETAHUN?", "setahun", ["SETAHUN?"])],
    [("Rp1.560.000.", "satu juta lima ratus enam puluh ribu", ["Rp1.560.000."])],
    [("TAPI TIM BAGI RATA", "tapi tim bagi rata", ["RATA"]), ("PUNYA ALASAN.", "punya alasan", [])],
    [("HITUNG PER ORANG", "hitung per orang", []), ("DI KASIR ITU RIBET.", "di kasir itu ribet", ["RIBET."])],
    [("MINGGU DEPAN,", "minggu depan", []), ("BISA JADI KAMU", "bisa jadi kamu", ["KAMU"]),
     ("YANG PESAN|PALING MAHAL.", "yang pesan paling mahal", ["MAHAL."])],
    [("LAGIAN,", "lagian", []), ("NONGKRONG ITU|SOAL TEMAN,", "nongkrong itu soal teman", ["TEMAN,"]),
     ("BUKAN KALKULATOR.", "bukan kalkulator", ["KALKULATOR."])],
    [("TIM BAYAR|MASING-MASING", "tim bayar masing-masing", ["MASING-MASING"]), ("BALAS:", "balas", [])],
    [("TEMAN YANG BAIK", "teman yang baik", ["BAIK"]), ("NGGAK BIKIN TEMANNYA", "nggak bikin temannya", []),
     ("NOMBOK.", "nombok", ["NOMBOK."])],
    [("JADI JALAN|TENGAHNYA:", "jadi jalan tengahnya", ["TENGAHNYA:"])],
    [("CAMILAN BARENG", "camilan bareng", ["CAMILAN"]), ("DIBAGI RATA,", "dibagi rata", [])],
    [("MAKANAN & MINUMAN", "makanan dan minuman", []), ("BAYAR MASING-MASING.", "bayar masing-masing", ["MASING-MASING."])],
    [("SEPAKATI|SEBELUM PESAN,", "sepakati sebelum pesan", ["SEBELUM"])],
    [("BIAR NASI GORENG", "biar nasi goreng", []), ("BAYAR HARGA|NASI GORENG.", "bayar harga nasi goreng", ["HARGA"])],
    [("KAMU TIM BAGI RATA,", "kamu tim bagi rata", ["RATA,"])],
    [("ATAU TIM BAYAR", "atau tim bayar", []), ("MASING-MASING?", "masing-masing", ["MASING-MASING?"])],
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
