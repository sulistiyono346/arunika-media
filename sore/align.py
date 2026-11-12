"""ARN-43 Diam-diam Makan Listrik: waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 52,8 dtk), dibagi per suku kata. TANPA Scribe.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan)."""
import json, re

SEGS = [(0.02, 2.60),                                                                 # 0 adegan 1
        (3.03, 4.70), (5.08, 5.39), (5.87, 6.38), (6.77, 7.90),                        # 1-4 adegan 2
        (8.42, 9.75), (9.97, 13.18),                                                   # 5-6 adegan 3
        (13.52, 16.19), (16.52, 18.38),                                                # 7-8 adegan 4
        (18.81, 19.35), (19.59, 20.39), (20.69, 22.38), (22.71, 23.34), (23.47, 24.40),# 9-13 adegan 5
        (24.72, 27.05), (27.37, 28.82), (29.13, 30.20),                                # 14-16 adegan 6
        (30.54, 32.12), (32.53, 34.94),                                                # 17-18 adegan 7
        (35.29, 36.19), (36.53, 37.39), (37.68, 39.13), (39.47, 39.99), (40.22, 41.40),# 19-23 adegan 8
        (41.78, 42.26), (42.47, 43.85), (44.15, 45.55), (45.71, 47.02),                # 24-27 adegan 9
        (47.36, 49.38), (49.68, 50.31), (50.51, 51.38), (51.70, 52.50)]                # 28-31 adegan 10

CHUNKS = [
    [("RUMAHMU", "rumahmu", []), ("KECOLONGAN", "kecolongan", ["KECOLONGAN"]), ("Rp80 RIBU", "delapan puluh ribu", ["Rp80", "RIBU"]),
     ("TIAP BULAN.", "tiap bulan", [])],
    [("KATANYA PELAKUNYA", "katanya pelakunya", []), ("KULKAS.", "kulkas", ["KULKAS."])],
    [("BENER?", "bener", ["BENER?"])],
    [("TAHAN DULU,", "tahan dulu", [])],
    [("KITA HITUNG", "kita hitung", ["HITUNG"]), ("SATU-SATU.", "satu satu", [])],
    [("TARIF PLN", "tarif pe el en", ["PLN"]), ("SEKARANG:", "sekarang", [])],
    [("Rp1.445", "seribu empat ratus empat puluh lima", ["Rp1.445"]), ("RUPIAH", "rupiah", []),
     ("PER kWh.", "per kilowatt jam", ["kWh."])],
    [("MULAI DARI", "mulai dari", []), ("CHARGER DAN TV", "charger dan tivi", ["CHARGER", "TV"]),
     ("YANG STANDBY TERUS.", "yang standbay terus", ["STANDBY"])],
    [("KIRA-KIRA", "kira kira", []), ("Rp10 RIBU SEBULAN.", "sepuluh ribu sebulan", ["Rp10", "RIBU"])],
    [("KULKAS,", "kulkas", ["KULKAS,"])],
    [("NYALA SEHARIAN:", "nyala seharian", [])],
    [("SEKITAR", "sekitar", []), ("Rp43 RIBU.", "empat puluh tiga ribu", ["Rp43", "RIBU."])],
    [("WAJAR,", "wajar", ["WAJAR,"])],
    [("MEMANG HARUS NYALA.", "memang harus nyala", [])],
    [("TAPI DISPENSER", "tapi dispenser", ["DISPENSER"]), ("PANAS-DINGIN", "panas dingin", []),
     ("LEBIH RAKUS:", "lebih rakus", ["RAKUS:"])],
    [("KIRA-KIRA", "kira kira", []), ("Rp50 RIBU,", "lima puluh ribu", ["Rp50", "RIBU,"])],
    [("GARA-GARA", "gara gara", []), ("PEMANASNYA.", "pemanasnya", ["PEMANASNYA."])],
    [("JUARANYA", "juaranya", ["JUARANYA"]), ("JUSTRU DI DAPUR:", "justru di dapur", ["DAPUR:"])],
    [("RICE COOKER", "rice cooker", ["RICE", "COOKER"]), ("YANG DIBIARKAN", "yang dibiarkan", []),
     ("MODE HANGAT", "mode hangat", ["HANGAT"]), ("SEHARIAN.", "seharian", [])],
    [("77 WATT,", "tujuh puluh tujuh watt", ["77"])],
    [("SEHARIAN PENUH:", "seharian penuh", [])],
    [("Rp80 RIBU", "delapan puluh ribu", ["Rp80", "RIBU"]), ("SEBULAN.", "sebulan", [])],
    [("SETAHUN?", "setahun", ["SETAHUN?"])],
    [("HAMPIR SEJUTA.", "hampir sejuta", ["SEJUTA."])],
    [("TRIKNYA:", "triknya", ["TRIKNYA:"])],
    [("CABUT BEGITU", "cabut begitu", ["CABUT"]), ("SELESAI MAKAN.", "selesai makan", [])],
    [("SISA NASI", "sisa nasi", []), ("MASUK KULKAS,", "masuk kulkas", ["KULKAS,"])],
    [("PANASKAN", "panaskan", ["PANASKAN"]), ("PAS MAU MAKAN.", "pas mau makan", [])],
    [("SI BOCOR", "si bocor", ["BOCOR"]), ("TERNYATA", "ternyata", []), ("DI DAPURMU.", "di dapurmu", ["DAPURMU."])],
    [("DI RUMAHMU,", "di rumahmu", [])],
    [("APA PALING BOROS?", "apa paling boros", ["BOROS?"])],
    [("TULIS DI KOMENTAR!", "tulis di komentar", ["KOMENTAR!"])],
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
