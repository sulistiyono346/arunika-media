# tools/ — pipeline render reel Arunika

Dipakai skill `arunika-reels`. Clone repo ini, kerjakan di folder kerja terpisah (bukan di dalam repo), lalu panggil skrip dengan path lengkap. Aset (logo, Aru) dibaca otomatis dari `../assets`.

Contoh lengkap = reel ARN-24 "Pertamax, kok telat naik?" (3 Nov 2026, gaya B Polaroid, 25,9 dtk).

## Urutan

```bash
T=/path/ke/arunika-media/tools
ffmpeg -i vo.mp3 -ac 1 -ar 44100 vo.wav

# 1. cari jeda nyata (titik/tanya ±0,4 dtk, koma ±0,2 dtk)
ffmpeg -i vo.wav -af silencedetect=n=-30dB:d=0.12 -f null - 2>&1 | grep silence_

# 2. salin align.py ke folder kerja, isi SEGS (segmen bicara di antara jeda)
#    dan CHUNKS (teks layar, kata yang diucapkan, kata kunci kuning) -> timing.json
python3 align.py

# 3. salin render_polaroid.py, ubah bagian per-reel (lihat di bawah), lalu
export TOTAL=25.9            # durasi VO + LEAD 0,3 + ±0,5 dtk
python3 render_polaroid.py events        # events.json (sfx)
python3 $T/mix.py                        # mix.wav: VO + musik (ducking) + sfx
python3 render_polaroid.py stills 0,2.6,8,14,20,25   # sheet.png -> CEK dulu
python3 render_polaroid.py video a.mp4 0 13 & python3 render_polaroid.py video b.mp4 13 $TOTAL & wait
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart final.mp4
```

## Yang diubah per reel di `render_polaroid.py`

- `SC` — awal tiap adegan (pakai `cs(i)` = waktu chunk ke-i, biasanya `cs(i) - 0.25`).
- `CAPTIONS` — caption mesin ketik di bawah polaroid (maks ±36 karakter).
- `JANJI_T`, `FOLLOW` — detik janji payoff (2–5) dan ajakan follow (sebelum 15).
- `static_card()` — kartu-kartu isi adegan; `scene_photo(k, t)` — tata letak & pemicu animasi tiap adegan (pemicu = `cs(i)`, bukan detik tetap).
- `base_bg()` — teks pill kategori & baris "now playing".
- `title_layer()` — judul cover (3–6 kata, 1 kata kunci kuning).
- catatan kaki per adegan di `frame()`; `events()` — sfx (whoosh ganti adegan, pop elemen, cring Si Bocor, ding payoff).

Helper siap pakai: `draw_aru` (Aru resmi dari `assets/maskot`, bergoyang), `bocor_img` (Si Bocor), `coin`, `card`, `arrow`, ikon `icon_barrel/drop/pump/jerrycan`, `draw_chart`, subtitle kotak krem/kuning Lora Bold, judul Poppins Bold bergradasi biru tua, logo penutup 1,5 dtk, progress bar kuning.

Hasil final disimpan ke `reels/YYYY-MM-DD_<slot>_<slug>.mp4` lalu dijadwalkan di Buffer dengan link `https://raw.githubusercontent.com/sulistiyono346/arunika-media/main/reels/<file>`.
