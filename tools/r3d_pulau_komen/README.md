# Pulau Komen (3D low-poly, three.js r160)

Dipakai pertama kali untuk Hari 2 Kopdes (tayang 17 Nov 2026 sore).

- `align_kopdes.py`: timing.json dari VO (silencedetect + DP frasa ke segmen bicara), tanpa Scribe. Butuh `naskah.txt` & `vo.wav`.
- `scene.js`: pulau, Kapten Jarwo low-poly, koperasi bertahap, kartu 2D, subtitle. Butuh juga `env.json` (amplitudo VO 30 fps untuk gerak mulut), `three.module.js` (npm pack three@0.160.0), Poppins-Bold/Medium.ttf, arunika-logo-putih.png.
- `render.js`: `node render.js stills <dir> t1,t2` · `node render.js frames <dir> f0 f1 30 [step]` (step 2 = 15 fps, frame digandakan sebelum encode).
- Kecepatan: ±0,6 dtk/frame efektif dengan 2 proses paralel (SwiftShader, tanpa GPU). 120 dtk penuh 30 fps ≈ 35 menit.
- Suara Jarwo: Macazzart Makassar Natural `hGKBtk3J6UEQtxLtsVRC` (eleven_v4).
