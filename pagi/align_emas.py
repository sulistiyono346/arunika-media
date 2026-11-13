"""ARN-44 Mana Lebih Hemat? #6 (emas buyback): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 50,96 dtk), dibagi per suku kata. TANPA Scribe.
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build/emas): python3 ../../align_emas.py"""
import json, re

# segmen bicara (detik audio VO) = celah di antara jeda silencedetect
SEGS = [(0.02, 0.78), (1.09, 3.07), (3.55, 3.98), (4.35, 5.24),                         # 0-3   adegan 1
        (5.69, 7.21), (7.36, 7.87), (8.01, 8.70), (9.16, 9.90), (10.22, 11.78),         # 4-8   adegan 2
        (12.20, 13.40), (13.71, 15.57), (15.72, 16.20),                                  # 9-11  adegan 3
        (16.66, 17.82), (18.24, 20.57),                                                  # 12-13 adegan 4
        (20.95, 21.74), (21.88, 22.74), (22.89, 24.49), (24.81, 25.67),                  # 14-17 adegan 5
        (26.01, 29.01), (29.23, 30.38),                                                  # 18-19 adegan 6
        (30.74, 33.43), (33.77, 34.60), (34.91, 35.71),                                  # 20-22 adegan 7
        (36.09, 36.48), (36.65, 37.24), (37.54, 39.02), (39.27, 40.34),                  # 23-26 adegan 8
        (40.72, 42.31), (42.45, 43.86), (44.04, 45.26),                                  # 27-29 adegan 9
        (45.59, 46.41), (46.66, 47.64), (47.95, 49.50), (49.81, 50.67)]                  # 30-33 adegan 10

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning)
CHUNKS = [
    [("BELI", "beli", []), ("EMAS,", "emas", ["EMAS,"])],   # frame 0: judul 4 kata + "BELI" = 5 kata
    [("UANGMU SUSUT", "uangmu susut", ["SUSUT"]), ("Rp190 RIBU.", "seratus sembilan puluh ribu", ["Rp190", "RIBU."])],
    [("COBA TEBAK,", "coba tebak", [])],
    [("KAPAN BALIK MODAL?", "kapan balik modal", ["MODAL?"])],
    [("KOMENTAR TERATAS", "komentar teratas", ["TERATAS"]), ("NOMOR 5,", "nomor lima", ["5,"])],
    [("JANJINYA", "janjinya", [])],
    [("TAMPIL DI SINI.", "tampil di sini", [])],
    [("MASIH KOSONG,", "masih kosong", ["KOSONG,"])],
    [("KURSINYA", "kursinya", []), ("MENUNGGU NAMAMU.", "menunggu namamu", ["NAMAMU."])],
    [("EMAS ANTAM", "emas antam", ["ANTAM"]), ("1 GRAM:", "satu gram", ["1", "GRAM:"])],
    [("Rp2.560.000,", "dua juta lima ratus enam puluh ribu", ["Rp2.560.000,"])],
    [("PLUS PAJAK.", "plus pajak", ["PAJAK."])],
    [("TAPI DIJUAL BALIK?", "tapi dijual balik", ["BALIK?"])],
    [("CUMA", "cuma", []), ("Rp2.375.000.", "dua juta tiga ratus tujuh puluh lima ribu", ["Rp2.375.000."])],
    [("SELISIHNYA,", "selisihnya", [])],
    [("PLUS PAJAK BELI,", "plus pajak beli", ["PAJAK"])],
    [("Rp191.400.", "seratus sembilan puluh satu ribu", ["Rp191.400."])],
    [("ITU BOCORNYA.", "itu bocornya", ["BOCORNYA."])],
    [("JADI HARGA BUYBACK", "jadi harga buyback", ["BUYBACK"]), ("HARUS NAIK", "harus naik", ["NAIK"]),
     ("SEKITAR 8% DULU,", "sekitar delapan persen dulu", ["8%"])],
    [("BARU KAMU", "baru kamu", []), ("BALIK MODAL.", "balik modal", ["MODAL."])],
    [("KALAU NAIK", "kalau naik", []), ("1% SEBULAN,", "satu persen sebulan", ["1%"]),
     ("ITU 8 BULAN.", "itu delapan bulan", ["8", "BULAN."])],
    [("KALAU HARGANYA TURUN?", "kalau harganya turun", ["TURUN?"])],
    [("LEBIH LAMA.", "lebih lama", ["LAMA."])],
    [("TERUS,", "terus", [])],
    [("PAJAK BUYBACK?", "pajak buyback", ["BUYBACK?"])],
    [("BARU KENA", "baru kena", []), ("DI ATAS Rp10 JUTA,", "di atas sepuluh juta", ["Rp10", "JUTA,"])],
    [("1,5 PERSEN.", "satu setengah persen", ["1,5"])],
    [("MAKANYA,", "makanya", []), ("SEBELUM BELI,", "sebelum beli", ["SEBELUM"])],
    [("CEK HARGA BUYBACK-NYA", "cek harga buyback nya", ["BUYBACK-NYA"]), ("DULU,", "dulu", [])],
    [("BUKAN CUMA", "bukan cuma", []), ("HARGA JUAL.", "harga jual", ["JUAL."])],
    [("YANG BIKIN SUSUT,", "yang bikin susut", ["SUSUT,"])],
    [("JUAL BURU-BURU.", "jual buru buru", ["BURU-BURU."])],
    [("TIM SIMPAN", "tim simpan", ["SIMPAN"]), ("ATAU JUAL CEPAT?", "atau jual cepat", ["CEPAT?"])],
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
