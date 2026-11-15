"""ARN-53 "Kok nyamuk lebih suka gigit kamu daripada temanmu?": waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 53,28 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen (±5-7 suku kata/dtk); jeda kalimat
lebih panjang dari jeda koma (mis. "mitos." 17,61 -> "Ternyata" 17,92).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (sore/build/nyamuk): python3 ../../align_nyamuk.py"""
import json, re

SEGS = [(0.02, 1.40), (1.78, 3.38),                                     # 0-1   frame 0 kamar berempat
        (3.93, 4.95), (5.09, 6.14),                                     # 2-3   close-up lengan, "darah manis?"
        (6.49, 6.86), (7.34, 8.06), (8.44, 11.43),                      # 4-6   coba tebak
        (11.86, 14.23), (14.65, 16.35), (16.50, 17.61),                 # 7-9   tersangka darah manis -> mitos
        (17.92, 20.10), (20.44, 22.26),                                 # 10-11 napas, 50 m
        (22.65, 24.42), (24.73, 25.72), (26.17, 27.61),                 # 12-14 kulit, asam
        (27.99, 28.65), (29.00, 32.84),                                 # 15-16 100x (puncak)
        (33.21, 34.41), (34.79, 36.43), (36.74, 38.00),                 # 17-19 golongan darah O
        (38.29, 40.12), (40.50, 42.03), (42.26, 43.11),                 # 20-22 setengah benar
        (43.44, 45.04), (45.27, 46.25), (46.55, 48.14),                 # 23-25 yang bisa diubah
        (48.47, 48.84), (48.97, 49.64), (50.01, 51.41), (51.70, 53.02)] # 26-29 tim korban vs tim aman

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("CUMA KAMU", "cuma kamu", ["KAMU"]), ("YANG BENTOL,", "yang bentol", [])],
    [("WALAU TIDUR", "walau tidur", []), ("BEREMPAT SEKAMAR.", "berempat sekamar", ["BEREMPAT"])],
    [("KATANYA SIH,", "katanya sih", [])],
    [("DARAHMU MANIS.", "darahmu manis", ["MANIS."])],
    [("BENER NGGAK?", "bener nggak", ["NGGAK?"])],
    [("COBA TEBAK DULU.", "coba tebak dulu", ["TEBAK"])],
    [("JAWABANNYA BIKIN", "jawabannya bikin", []), ("KAMU PENGIN CIUM", "kamu pengin cium", ["CIUM"]),
     ("LENGANMU SENDIRI.", "lenganmu sendiri", [])],
    [("TERSANGKA PERTAMA,", "tersangka pertama", []), ("JELAS DARAH MANIS.", "jelas darah manis", ["MANIS."])],
    [("TAPI KATA", "tapi kata", []), ("AHLI SERANGGA,", "ahli serangga", ["SERANGGA,"])],
    [("ITU CUMA MITOS.", "itu cuma mitos", ["MITOS."])],
    [("TERNYATA YANG DICIUM", "ternyata yang dicium", []), ("NYAMUK DULUAN", "nyamuk duluan", []),
     ("NAPASMU,", "napasmu", ["NAPASMU,"])],
    [("DARI JARAK SAMPAI", "dari jarak sampai", []), ("50 METER.", "lima puluh meter", ["50"])],
    [("TAPI SEMUA ORANG", "tapi semua orang", []), ("BERNAPAS, KAN?", "bernapas kan", ["BERNAPAS,"])],
    [("PEMBEDANYA DI KULIT:", "pembedanya di kulit", ["KULIT:"])],
    [("ASAM DARI", "asam dari", ["ASAM"]), ("MINYAK KULITMU.", "minyak kulitmu", [])],
    [("SATU STUDI:", "satu studi", [])],
    [("ORANG TERFAVORIT", "orang terfavorit", []), ("DISERBU", "diserbu", []),
     ("100× LIPAT", "seratus kali lipat", ["100×"]), ("DIBANDING YANG", "dibanding yang", []),
     ("PALING AMAN.", "paling aman", ["AMAN."])],
    [("TERUS GOLONGAN", "terus golongan", []), ("DARAH O?", "darah o", ["O?"])],
    [("SATU STUDI KECIL", "satu studi kecil", []), ("BILANG IYA,", "bilang iya", ["IYA,"])],
    [("STUDI LAIN", "studi lain", []), ("SEBALIKNYA.", "sebaliknya", ["SEBALIKNYA."])],
    [("JADI TIM DARAH MANIS", "jadi tim darah manis", []), ("SETENGAH BENAR:", "setengah benar", ["SETENGAH"])],
    [("KAMU MEMANG", "kamu memang", []), ("LEBIH MENGGODA,", "lebih menggoda", ["MENGGODA,"])],
    [("BUKAN DARAHNYA.", "bukan darahnya", ["BUKAN"])],
    [("YANG BISA KAMU UBAH", "yang bisa kamu ubah", ["UBAH"]), ("MALAM INI:", "malam ini", [])],
    [("LOTION ANTINYAMUK,", "lotion antinyamuk", ["LOTION"])],
    [("BAJU PANJANG,", "baju panjang", ["PANJANG,"]), ("DAN KELAMBU.", "dan kelambu", ["KELAMBU."])],
    [("NAH,", "nah", [])],
    [("SEKARANG JUJUR,", "sekarang jujur", ["JUJUR,"])],
    [("KAMU TIM", "kamu tim", []), ("KORBAN NYAMUK,", "korban nyamuk", ["KORBAN"])],
    [("ATAU TIM", "atau tim", []), ("TIDUR AMAN?", "tidur aman", ["AMAN?"])],
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
