# Format "3D bongkar" (exploded view benda sehari-hari)

Dipakai pertama kali di reel 2026-11-18 sore (ARN-58, kunci pin tumbler). Pangkalan: `tools/r3d_kamu_pilih/`.

Gaya: latar gelap gradien abu-biru, grid lantai perspektif, lingkaran oranye di lantai + cahaya oranye di belakang benda, benda logam (kuningan/krom, env map PMREM) melayang berputar pelan, komponen terpisah dengan garis penunjuk putih + pill 1 kata, subtitle 1 baris bawah tengah (1 kata kunci kotak kuning #FFB800), teks ajakan kirim di puncak, sumber kecil y≈1640, logo kecil (setelah dtk 4) dan penutup 1,5 dtk.

- `scene.html` + `scene.js`: three.js r160 (salin `three.module.js`, `Poppins-Bold.ttf`, `Poppins-Medium.ttf`, `arunika-logo-putih.png` ke folder kerja yang sama; tidak di-commit). Mengekspos `window.renderFrame(t)` deterministik. Model kunci: `makeLock()` / `makeKey(tinggi_lekuk)` / `poseLock(L, {e, key, kz, rot, ghost, shear, shake})` (e = tingkat bongkar 0..1, kz = posisi masuk kunci, ghost = cutaway transparan).
- `render.js`: Playwright headless Chromium + SwiftShader. `node render.js stills <dir> t1,t2,...` lalu `node render.js frames <dir> <f0> <f1> 30` (bagi 2 proses; ±0,45 dtk/frame).
- `align_3d.py`: timing.json dari jeda VO nyata (`ffmpeg -af silencedetect=n=-30dB:d=0.12`), tanpa Scribe. Isi SEGS + CHUNKS.
- `mix_3d.py`: VO + pad + sfx mekanis sintetis -> mix_raw.wav; lalu loudnorm 2 tahap ke -14 LUFS (TP -1,5).

```bash
ffmpeg -i vo.mp3 -ac 1 -ar 44100 vo.wav
python3 align_3d.py && python3 mix_3d.py
ffmpeg -i mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null -   # ukur, lalu tahap 2 dengan measured_*
node render.js stills st 0,2.4,14.6,19.8,25,30.8,44.6,53.2      # cek dulu
node render.js frames fr 0 837 30 & node render.js frames fr 837 <N> 30 & wait
ffmpeg -framerate 30 -i fr/f_%05d.jpg -i mix.wav -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart final.mp4
```

Adegan, teks, dan timing di `scene.js` spesifik reel kunci; ganti benda dan adegan untuk cerita berikutnya. Jangan tampilkan cara membobol/merusak benda.
