"""ARN-54 Mana Lebih Hemat? #12 (UMR Jakarta vs UMR Jogja): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 66,93 dtk; lembah internal -35 dB d=0.05 untuk segmen panjang).
TANPA Scribe. Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen.
Segmen panjang dipecah di lembah: 6,66-10,42 -> 6,66-8,79 | 8,87-9,22 | 9,29-10,42 ;
42,65-47,53 -> 42,65-43,61 | 43,71-46,20 | 46,30-47,53. Segmen 57,37-57,48 + 57,61-58,38 digabung.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_umr): python3 ../align_umr.py"""
import json, re

SEGS = [(0.00, 1.65),                                   # 0  hook
        (2.06, 2.54), (2.93, 3.75),                     # 1-2  sisanya? belum tentu
        (4.17, 4.57), (4.91, 6.07),                     # 3-4  coba tebak
        (6.66, 8.79), (8.87, 9.22), (9.29, 10.42),      # 5-7  teman mudik, langsung ditanya pakde
        (10.81, 11.53),                                 # 8    gajinya berapa
        (12.01, 12.99), (13.28, 14.87),                 # 9-10 UMP Jakarta
        (15.29, 16.52), (16.74, 18.45),                 # 11-12 UMK Jogja
        (18.82, 19.40), (19.52, 20.52),                 # 13-14 tiga pos antre
        (20.89, 22.02), (22.21, 23.18),                 # 15-16 kos Jakarta
        (23.52, 25.12), (25.31, 26.52),                 # 17-18 makan warteg
        (26.875, 27.99), (28.13, 30.21),                # 19-20 transjakarta, sisa
        (30.62, 31.04), (31.38, 32.60), (32.74, 34.13), (34.34, 34.89),   # 21-24 Jogja
        (35.25, 36.83),                                 # 25 sisa 1,2 jt
        (37.25, 39.41), (39.85, 40.27),                 # 26-27 dua kali lipat, selesai?
        (40.64, 40.98), (41.31, 42.24),                 # 28-29 tunggu, tim Jogja menjawab
        (42.65, 43.61), (43.71, 46.20), (46.30, 47.53), # 30-32 kosmu 2 jt, ojol, sisa 1,03
        (47.85, 48.85),                                 # 33 kalah dari Jogja
        (49.28, 50.30), (50.63, 52.51),                 # 34-35 tim Jakarta balas
        (52.87, 54.52), (54.65, 54.89), (55.04, 55.99), # 36-38 penentunya
        (56.35, 57.23), (57.37, 58.38),                 # 39-40 cek kos dekat halte
        (58.74, 59.43), (59.73, 60.63), (60.95, 61.72), (62.07, 63.13),  # 41-44 dua skenario
        (63.44, 65.01), (65.14, 66.62)]                 # 45-46 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("GAJIMU DOBEL", "gajimu dobel", ["DOBEL"]), ("DI JAKARTA.", "di jakarta", [])],
    [("SISANYA?", "sisanya", ["SISANYA?"])],
    [("BELUM TENTU.", "belum tentu", ["TENTU."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("SIAPA SISA", "siapa sisa", []), ("LEBIH BANYAK?", "lebih banyak", ["BANYAK?"])],
    [("KAMU PASTI KENAL", "kamu pasti kenal", ["KENAL"]), ("TEMAN MUDIK", "teman yang mudik", ["MUDIK"]),
     ("DARI JAKARTA,", "dari jakarta", ["JAKARTA,"])],
    [("LANGSUNG", "langsung", ["LANGSUNG"])],
    [("DITANYA PAKDE,", "ditanya pakde", ["PAKDE,"])],
    [("\"GAJINYA BERAPA?\"", "gajinya berapa", ["BERAPA?\""])],
    [("UMP JAKARTA:", "u em pe jakarta", ["UMP"])],
    [("Rp5,73 JUTA.", "lima koma tujuh tiga juta", ["Rp5,73"])],
    [("UMK KOTA JOGJA:", "u em ka kota jogja", ["UMK"])],
    [("Rp2,83 JUTA.", "dua koma delapan tiga juta", ["Rp2,83"])],
    [("TAPI TIGA POS", "tapi tiga pos", ["POS"])],
    [("LANGSUNG ANTRE.", "langsung antre", ["ANTRE."])],
    [("KOS STANDAR", "kos standar", []), ("JAKARTA:", "jakarta", ["JAKARTA:"])],
    [("Rp1,5 JUTA.", "satu setengah juta", ["Rp1,5"])],
    [("MAKAN WARTEG", "makan warteg", ["WARTEG"]), ("2× SEHARI:", "dua kali sehari", [])],
    [("Rp1,2 JUTA.", "satu koma dua juta", ["Rp1,2"])],
    [("PLUS TRANSJAKARTA,", "plus transjakarta", ["TRANSJAKARTA,"])],
    [("SISA HAMPIR", "sisa hampir", []), ("Rp2,9 JUTA.", "dua koma sembilan juta", ["Rp2,9"])],
    [("JOGJA:", "jogja", ["JOGJA:"])],
    [("KOS Rp600 RIBU,", "kos enam ratus ribu", ["Rp600"])],
    [("MAKAN Rp900 RIBU,", "makan sembilan ratus ribu", ["Rp900"])],
    [("PLUS BUS.", "plus bus", ["BUS."])],
    [("SISA Rp1,2 JUTA.", "sisa satu koma dua juta", ["Rp1,2"])],
    [("JAKARTA SISA", "jakarta sisa", []), ("2× LIPAT LEBIH.", "dua kali lipat lebih", ["2×"])],
    [("SELESAI?", "selesai", ["SELESAI?"])],
    [("TUNGGU,", "tunggu", ["TUNGGU,"])],
    [("TIM JOGJA", "tim jogja", ["JOGJA"]), ("MENJAWAB.", "menjawab", [])],
    [("KALAU KOSMU", "kalau kosmu", []), ("Rp2 JUTA,", "dua juta", ["Rp2"])],
    [("TIAP HARI OJOL,", "dan tiap hari ojol", ["OJOL,"]), ("SISANYA TINGGAL", "sisanya tinggal", [])],
    [("Rp1,03 JUTA.", "satu koma nol tiga juta", ["Rp1,03"])],
    [("KALAH DARI JOGJA.", "kalah dari jogja", ["KALAH"])],
    [("TIM JAKARTA BALAS:", "tim jakarta balas", ["JAKARTA"])],
    [("KOS PINGGIRAN", "kos pinggiran", ["PINGGIRAN"]), ("MULAI Rp700 RIBU.", "mulai tujuh ratus ribu", [])],
    [("PENENTUNYA", "jadi penentunya", []), ("BUKAN GAJI,", "bukan gaji", ["GAJI,"])],
    [("TAPI", "tapi", [])],
    [("KOS DAN ONGKOS.", "kos dan ongkos", ["ONGKOS."])],
    [("SEBELUM MERANTAU,", "sebelum merantau", ["MERANTAU,"])],
    [("CEK KOS", "cek kos", ["KOS"]), ("DEKAT HALTE.", "dekat halte", [])],
    [("DEKAT HALTE?", "dekat halte", ["HALTE?"])],
    [("JAKARTA UNGGUL.", "jakarta unggul", ["UNGGUL."])],
    [("TIAP HARI OJOL?", "tiap hari ojol", ["OJOL?"])],
    [("JOGJA BISA MENANG.", "jogja bisa menang", ["MENANG."])],
    [("KAMU TIM MERANTAU", "kamu tim merantau", ["MERANTAU"]), ("KE JAKARTA,", "ke jakarta", [])],
    [("ATAU TIM BERTAHAN", "atau tim bertahan", []), ("DI JOGJA?", "di jogja", ["JOGJA?"])],
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
