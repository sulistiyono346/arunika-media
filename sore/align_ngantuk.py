"""ARN-50 "Kok kamu ngantuk habis makan siang?": waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 53,20 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen (±5-8 suku kata/dtk).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (sore/build/ngantuk): python3 ../../align_ngantuk.py"""
import json, re

SEGS = [(0.05, 2.28), (2.74, 4.23),                                     # 0-1   adegan 0 frame 0
        (4.57, 5.07), (5.49, 6.31), (6.71, 7.67), (7.79, 8.58),         # 2-5   adegan 1 coba tebak
        (9.11, 9.57), (9.96, 11.38), (11.82, 12.86),                    # 6-8   adegan 2 rapat
        (13.22, 14.80), (15.37, 16.57),                                 # 9-10  adegan 3 mengangguk
        (16.98, 17.92), (18.13, 18.86), (19.29, 21.41), (21.92, 22.69), # 11-14 adegan 4 tersangka nasi
        (23.04, 24.16), (24.44, 27.66),                                 # 15-16 adegan 5 tetap ngantuk
        (28.05, 28.61), (28.98, 30.55), (30.90, 31.71), (31.89, 32.85), # 17-20 adegan 6 jam tubuh
        (33.06, 34.48), (34.82, 35.66), (35.83, 38.87),                 # 21-23 adegan 7 simulator (puncak)
        (39.22, 40.51), (40.82, 42.45), (42.66, 44.27),                 # 24-26 adegan 8 dua-duanya
        (44.69, 45.22), (45.53, 46.84), (47.02, 48.71),                 # 27-29 adegan 9 besok coba
        (49.07, 49.72), (50.04, 51.46), (51.69, 52.98)]                 # 30-32 adegan 10 tim nasi vs tim jam

# "|" = subtitle dipecah jadi 2 layar berurutan dalam waktu chunk yang sama
# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("OTAKMU MATI LAMPU", "otakmu mati lampu", ["MATI", "LAMPU"]), ("TIAP JAM DUA SIANG.", "tiap jam dua siang", [])],
    [("KATANYA", "katanya", []), ("GARA-GARA NASI.", "gara-gara nasi", ["NASI."])],
    [("BENER NGGAK?", "bener nggak", ["NGGAK?"])],
    [("COBA TEBAK DULU,", "coba tebak dulu", ["TEBAK"])],
    [("JAWABANNYA BUKAN", "jawabannya bukan", ["BUKAN"])],
    [("YANG KAMU KIRA.", "yang kamu kira", [])],
    [("BAYANGIN:", "bayangin", [])],
    [("RAPAT HABIS", "rapat habis", []), ("MAKAN SIANG.", "makan siang", ["SIANG."])],
    [("BOS PRESENTASI,", "bos presentasi", [])],
    [("KEPALAMU", "kepalamu", []), ("MENGANGGUK…", "mengangguk", ["MENGANGGUK…"])],
    [("BUKAN KARENA SETUJU.", "bukan karena setuju", ["SETUJU."])],
    [("TERSANGKA PERTAMA,", "tersangka pertama", [])],
    [("JELAS NASI.", "jelas nasi", ["NASI."])],
    [("KARBOHIDRAT TINGGI", "karbohidrat tinggi", []), ("MEMANG BIKIN", "memang bikin", []),
     ("LEBIH NGANTUK.", "lebih ngantuk", ["NGANTUK."])],
    [("TAPI…", "tapi", ["TAPI…"])],
    [("PENELITI MENEMUKAN,", "peneliti menemukan", [])],
    [("NGANTUK JAM SEGINI", "ngantuk jam segini", []), ("TETAP DATANG", "tetap datang", ["TETAP"]),
     ("WALAU KAMU", "walau kamu", []), ("NGGAK MAKAN SIANG.", "nggak makan siang", [])],
    [("KOK BISA?", "kok bisa", ["BISA?"])],
    [("TUBUHMU PUNYA", "tubuhmu punya", []), ("JAM SENDIRI.", "jam sendiri", ["JAM", "SENDIRI."])],
    [("AWAL SIANG,", "awal siang", [])],
    [("SINYAL MELEK", "sinyal melek", ["MELEK"]), ("OTAK TURUN.", "otak turun", [])],
    [("TERUS NASINYA?", "terus nasinya", ["NASINYA?"])],
    [("DI SIMULATOR,", "di simulator", [])],
    [("MAKAN SIANG", "makan siang", []), ("3× LIPAT", "tiga kali lipat", ["3×"]),
     ("BIKIN PENGEMUDI", "bikin pengemudi", []), ("MAKIN OLENG.", "makin oleng", ["OLENG."])],
    [("JADI DUA-DUANYA", "jadi dua-duanya", ["DUA-DUANYA"]), ("BENAR.", "benar", [])],
    [("JAM TUBUH", "jam tubuh", []), ("MEMATIKAN LAMPU,", "mematikan lampu", ["LAMPU,"])],
    [("PORSI BESAR", "porsi besar", ["BESAR"]), ("BIKIN MAKIN GELAP.", "bikin makin gelap", [])],
    [("BESOK COBA:", "besok coba", [])],
    [("PORSI NASI", "porsi nasi", []), ("LEBIH KECIL,", "lebih kecil", ["KECIL,"])],
    [("LALU JALAN SEBENTAR", "lalu jalan sebentar", []), ("KENA MATAHARI.", "kena matahari", ["MATAHARI."])],
    [("SEKARANG JUJUR,", "sekarang jujur", [])],
    [("KAMU TIM", "kamu tim", []), ("SALAHIN NASI,", "salahin nasi", ["NASI,"])],
    [("ATAU TIM", "atau tim", []), ("SALAHIN JAM?", "salahin jam", ["JAM?"])],
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
