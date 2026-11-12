"""ARN-41 Mana Lebih Hemat? #5 (ojol saat hujan): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 50,8 dtk), dibagi per suku kata. TANPA Scribe.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan)."""
import json, re

# segmen bicara (detik audio VO) = celah di antara jeda silencedetect
SEGS = [(0.05, 0.58), (0.92, 1.95), (2.45, 2.89), (3.26, 4.06), (4.21, 4.87),          # 0-4  adegan 1
        (5.44, 6.16), (6.42, 8.22), (8.57, 9.66), (9.86, 11.59),                         # 5-8  adegan 2
        (12.01, 13.50), (13.90, 14.56), (14.73, 16.72),                                  # 9-11 adegan 3
        (17.04, 19.65), (19.92, 20.71), (20.96, 22.37),                                  # 12-14 adegan 4
        (22.69, 23.71), (24.00, 24.49), (24.79, 26.78),                                  # 15-17 adegan 5
        (27.10, 27.77), (28.00, 29.72), (29.93, 31.48),                                  # 18-20 adegan 6
        (31.78, 33.16), (33.40, 36.65),                                                  # 21-22 adegan 7
        (36.89, 38.19), (38.49, 39.04), (39.26, 41.11),                                  # 23-25 adegan 8
        (41.45, 42.59), (42.97, 43.76), (44.00, 45.17),                                  # 26-28 adegan 9
        (45.41, 46.43), (46.58, 47.78), (48.08, 49.51), (49.73, 50.60)]                  # 29-32 adegan 10

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning)
CHUNKS = [
    [("HUJAN,", "hujan", [])],
    [("ONGKOS OJOLMU", "ongkos ojolmu", []), ("NAIK.", "naik", ["NAIK."])],
    [("COBA TEBAK,", "coba tebak", [])],
    [("MOTOR SENDIRI", "motor sendiri", ["MOTOR"])],
    [("HABIS BERAPA?", "habis berapa", ["BERAPA?"])],
    [("JANJI KEMARIN:", "janji kemarin", ["JANJI"])],
    [("KOMENTAR TERATAS", "komentar teratas", ["TERATAS"]), ("TAMPIL DI SINI.", "tampil di sini", [])],
    [("KEMARIN MASIH", "kemarin masih", []), ("KOSONG,", "kosong", ["KOSONG,"])],
    [("JADI HARI INI", "jadi hari ini", []), ("KESEMPATANMU.", "kesempatanmu", ["KESEMPATANMU."])],
    [("ANGGAP KANTORMU", "anggap kantormu", []), ("8 KILO.", "delapan kilo", ["8", "KILO."])],
    [("OJOLNYA,", "ojolnya", [])],
    [("TARIF DASAR", "tarif dasar", []), ("SEKITAR Rp22 RIBU.", "sekitar dua puluh dua ribu", ["Rp22", "RIBU."])],
    [("MASALAHNYA,", "masalahnya", []), ("PAS HUJAN", "pas hujan", ["HUJAN"]),
     ("SEMUA ORANG", "semua orang", []), ("PESAN.", "pesan", ["PESAN."])],
    [("TARIFNYA", "tarifnya", []), ("IKUT NAIK,", "ikut naik", ["NAIK,"])],
    [("MISALNYA", "misalnya", []), ("Rp30 RIBU.", "tiga puluh ribu", ["Rp30", "RIBU."])],
    [("12 HARI HUJAN,", "dua belas hari hujan", ["12"])],
    [("PULANG PERGI?", "pulang pergi", [])],
    [("Rp720 RIBU", "tujuh ratus dua puluh ribu", ["Rp720", "RIBU"]), ("SEBULAN.", "sebulan", [])],
    [("MOTOR SENDIRI?", "motor sendiri", ["MOTOR"])],
    [("BENSIN CUMA", "bensin cuma", []), ("Rp48 RIBU.", "empat puluh delapan ribu", ["Rp48", "RIBU."])],
    [("TAPI,", "tapi", []), ("ADA YANG BOCOR.", "ada yang bocor", ["BOCOR."])],
    [("PARKIR Rp6 RIBU", "parkir enam ribu", ["Rp6", "RIBU"]), ("SEHARI,", "sehari", [])],
    [("PLUS JAS HUJAN,", "plus jas hujan", []), ("SERVIS, DAN OLI", "servis dan oli", []),
     ("DIBAGI PER BULAN.", "dibagi per bulan", ["BULAN."])],
    [("TOTALNYA", "totalnya", []), ("Rp200 RIBU.", "dua ratus ribu", ["Rp200", "RIBU."])],
    [("SELISIHNYA?", "selisihnya", [])],
    [("Rp520 RIBU", "lima ratus dua puluh ribu", ["Rp520", "RIBU"]), ("SEBULAN.", "sebulan", [])],
    [("SIMPAN JAS HUJAN", "simpan jas hujan", []), ("DI JOK.", "di jok", ["JOK."])],
    [("TERPAKSA OJOL?", "terpaksa ojol", [])],
    [("PESAN SEBELUM", "pesan sebelum", ["SEBELUM"]), ("DERAS.", "deras", ["DERAS."])],
    [("HUJANNYA GRATIS,", "hujannya gratis", ["GRATIS,"])],
    [("BURU-BURUNYA", "buru buru nya", []), ("YANG MAHAL.", "yang mahal", ["MAHAL."])],
    [("TIM OJOL", "tim ojol", ["OJOL"]), ("ATAU JAS HUJAN?", "atau jas hujan", ["JAS", "HUJAN?"])],
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
