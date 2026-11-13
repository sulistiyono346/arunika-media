"""ARN-45 Hujan deras 1 jam di Jakarta = berapa liter: waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 52,32 dtk), dibagi per suku kata. TANPA Scribe.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (build): python3 /path/sore/align_hujan.py"""
import json, re

# segmen bicara (detik audio VO) = celah di antara jeda silencedetect
SEGS = [(0.02, 0.97), (1.32, 3.56),                                                     # 0-1   adegan 1
        (4.04, 5.13), (5.62, 6.39), (6.81, 7.24), (7.56, 8.72),                          # 2-5   adegan 2
        (9.14, 10.82), (11.30, 12.32), (12.67, 14.76),                                   # 6-8   adegan 3
        (15.22, 16.37), (16.80, 17.44), (17.76, 19.02), (19.15, 20.70),                  # 9-12  adegan 4
        (21.10, 22.55), (22.87, 24.38), (24.69, 25.51),                                  # 13-15 adegan 5
        (25.95, 27.82), (28.17, 31.02),                                                  # 16-17 adegan 6
        (31.36, 32.16), (32.34, 33.65), (33.95, 35.74), (36.00, 36.64),                  # 18-21 adegan 7
        (37.03, 38.18), (38.41, 39.71), (40.03, 40.52), (40.65, 42.45),                  # 22-25 adegan 8
        (42.80, 45.96), (46.22, 48.52),                                                  # 26-27 adegan 9
        (48.90, 51.01), (51.30, 52.07)]                                                  # 28-29 adegan 10

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning)
CHUNKS = [
    [("HUJAN", "hujan", []), ("SEJAM,", "sejam", [])],        # frame 0: judul 4 kata + "HUJAN" = 5 kata
    [("ATAPMU KETIBAN", "atapmu ketiban", ["KETIBAN"]), ("38 GALON.", "tiga puluh delapan galon", ["38"])],
    [("ITU BARU SATU ATAP.", "itu baru satu atap", ["SATU"])],
    [("KALAU SEJAKARTA?", "kalau sejakarta", ["SEJAKARTA?"])],
    [("COBA TEBAK,", "coba tebak", [])],
    [("BERAPA KOLAM OLIMPIADE?", "berapa kolam olimpiade", ["KOLAM"])],
    [("PATOKANNYA DARI BMKG:", "patokannya dari be em ka ge", ["BMKG:"])],
    [("HUJAN SANGAT LEBAT,", "hujan sangat lebat", ["LEBAT,"])],
    [("LEBIH DARI 20 MM", "lebih dari dua puluh milimeter", ["20"]), ("SEJAM.", "sejam", [])],
    [("KEDENGARANNYA TIPIS.", "kedengarannya tipis", ["TIPIS."])],
    [("PADAHAL,", "padahal", [])],
    [("DI TIAP METER PERSEGI,", "di tiap meter persegi", ["METER"])],
    [("ITU 20 LITER AIR.", "itu dua puluh liter air", ["20", "LITER"])],
    [("ATAP 36 M²?", "atap tiga puluh enam meter persegi", ["36"])],
    [("720 LITER.", "tujuh ratus dua puluh liter", ["720"])],
    [("SEJAM SAJA.", "sejam saja", ["SEJAM"])],
    [("NAH, SEKARANG", "nah sekarang", []), ("SELURUH JAKARTA:", "seluruh jakarta", ["JAKARTA:"])],
    [("661 KM²", "enam ratus enam puluh satu kilometer persegi", ["661"]), ("DARATAN.", "daratan", [])],
    [("KALAU MERATA,", "kalau merata", ["MERATA,"])],
    [("KALIKAN 20 LITER TADI:", "kalikan dua puluh liter tadi", ["20"])],
    [("13 MILIAR LITER.", "tiga belas miliar liter", ["13"])],
    [("SEJAM!", "sejam", ["SEJAM!"])],
    [("SATU KOLAM OLIMPIADE:", "satu kolam olimpiade", ["KOLAM"])],
    [("2,5 JUTA LITER.", "dua setengah juta liter", ["2,5"])],
    [("JADI,", "jadi", [])],
    [("5.300 KOLAM!", "lima ribu tiga ratus kolam", ["5.300"])],
    [("MAKANYA,", "makanya", []), ("BERSIHKAN TALANG", "bersihkan talang", ["TALANG"]),
     ("SEBELUM PUNCAK HUJAN.", "sebelum puncak hujan", ["PUNCAK"])],
    [("38 GALON ITU", "tiga puluh delapan galon itu", ["38"]), ("BUTUH JALAN.", "butuh jalan", ["JALAN."])],
    [("TALANG RUMAHMU", "talang rumahmu", ["TALANG"]), ("PERNAH MELUAP", "pernah meluap", ["MELUAP"]),
     ("WAKTU HUJAN DERAS?", "waktu hujan deras", [])],
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
