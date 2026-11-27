"""ARN-68 "Kenapa TIP beda tiap negara?": waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 47,80 dtk). TANPA Scribe.
Jeda < 0,2 dtk di tengah frasa digabung (2,27-2,43 / 3,28-3,47 / 18,55-18,68 / 21,65-22,05).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_tip): python3 ../align_tip.py"""
import json, re

SEGS = [(0.000, 1.059), (1.473, 2.266),                      # 0-1   A1 hook
        (2.815, 3.276), (3.829, 4.813), (5.091, 5.742),       # 2-4   A2 coba tebak
        (6.172, 7.826),                                       # 5     katanya 20%
        (8.250, 9.056), (9.431, 11.863), (12.135, 12.770),    # 6-8   A3 Pew
        (13.137, 14.009), (14.418, 17.415),                   # 9-10  A4 upah
        (17.820, 18.547), (18.681, 19.721), (20.164, 22.788), # 11-13 A5 Jepang
        (23.103, 23.504), (23.822, 24.846), (25.241, 28.147), # 14-16 A6 servis 95%
        (28.586, 29.481), (29.798, 30.437), (30.890, 31.781), (32.168, 33.799),  # 17-20 A7 ojol
        (34.163, 35.082), (35.331, 36.407), (36.805, 37.640), (37.929, 39.130),  # 21-24 A8 dua kubu
        (39.445, 40.361), (40.676, 41.474), (41.748, 42.455), (42.898, 43.350), (43.672, 44.831),  # 25-29 A9
        (45.205, 45.883), (46.278, 47.473)]                   # 30-31 A10

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("SERVICE DI STRUKMU?", "service di strukmu", ["SERVICE"])],
    [("ITU BUKAN TIP.", "itu bukan tip", ["TIP."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("MAKAN DI AMERIKA,", "makan di amerika", ["AMERIKA,"])],
    [("NAMBAH BERAPA?", "nambah berapa", ["BERAPA?"])],
    [("KATANYA WAJIB", "katanya wajib", ["WAJIB"]), ("20 PERSEN.", "dua puluh persen", ["20"])],
    [("SURVEI PEW:", "survei pew", ["PEW:"])],
    [("57 PERSEN", "lima puluh tujuh persen", ["57"]), ("KASIH 15 PERSEN,", "kasih lima belas persen", ["15"])],
    [("ATAU KURANG.", "atau kurang", ["KURANG."])],
    [("KENAPA TETAP KASIH?", "kenapa tetap kasih", ["KENAPA"])],
    [("UPAH POKOK PELAYAN", "upah pokok pelayan", ["UPAH"]), ("BISA CUMA", "bisa cuma", []),
     ("2 DOLAR LEBIH SEJAM.", "dua dolar lebih sejam", ["2"])],
    [("NAH, DI JEPANG", "nah di jepang", ["JEPANG"])],
    [("KEBALIKANNYA:", "kebalikannya", ["KEBALIKANNYA:"])],
    [("PANDUAN RESMI TURISNYA", "panduan resmi turisnya", ["RESMI"]), ("BILANG TIP", "bilang tip", []),
     ("TIDAK LAZIM.", "tidak lazim", ["LAZIM."])],
    [("DI SINI?", "di sini", ["SINI?"])],
    [("UANG SERVIS HOTEL:", "uang servis hotel", ["SERVIS"])],
    [("95 PERSENNYA", "sembilan puluh lima persennya", ["95"]), ("WAJIB DIBAGI", "wajib dibagi", []),
     ("KE PEKERJA.", "ke pekerja", ["PEKERJA."])],
    [("TIP ITU LAIN:", "tip itu lain", ["LAIN:"])],
    [("SUKARELA,", "sukarela", ["SUKARELA,"])],
    [("DAN KATA GOJEK,", "dan kata gojek", ["GOJEK,"])],
    [("100 PERSEN", "seratus persen", ["100"]), ("MASUK KE DRIVER.", "masuk ke driver", ["DRIVER."])],
    [("TIM TIP BILANG:", "tim tip bilang", ["TIP"])],
    [("ITU TERIMA KASIH.", "itu terima kasih", ["KASIH."])],
    [("TIM PAS HARGA:", "tim pas harga", ["PAS"])],
    [("KAN SUDAH", "kan sudah", []), ("BAYAR SERVIS.", "bayar servis", ["SERVIS."])],
    [("CEK STRUKMU DULU:", "cek strukmu dulu", ["CEK"])],
    [("ADA SERVICE,", "ada service", ["SERVICE,"])],
    [("TIP BOLEH LEWAT.", "tip boleh lewat", ["LEWAT."])],
    [("NGGAK ADA?", "nggak ada", ["NGGAK"])],
    [("RECEH PUN BERARTI.", "receh pun berarti", ["RECEH"])],
    [("KAMU TIM TIP,", "kamu tim tip", ["TIP,"])],
    [("ATAU TIM PAS HARGA?", "atau tim pas harga", ["PAS"])],
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
