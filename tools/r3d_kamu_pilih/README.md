# Format "Bayangkan kamu… kamu pilih apa?" (3D sinematik gelap)

Dipakai pertama kali di reel 2026-11-11 sore (Galunggung 1982 / BA Flight 9).

- `scene.html` + `scene.js`: adegan three.js r160 (salin `three.module.js` dari `npm i three@0.160.0`, letakkan di folder yang sama; font Poppins + logo putih dari `assets/`). Halaman mengekspos `window.renderFrame(t)` (deterministik).
- `render.js`: Playwright headless Chromium (WebGL via SwiftShader: `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`).
  - `node render.js stills <dir> t1,t2,...`
  - `node render.js frames <dir> <f0> <f1> 30`
- `align_3d.py`: timing.json dari jeda VO nyata (ffmpeg silencedetect), tanpa Scribe.
- `mix_3d.py`: VO + drone/jet/whoosh/beep sintetis, lalu normalisasi -14 LUFS dua tahap.

Adegan, teks, dan timing di `scene.js` spesifik reel Galunggung; ganti untuk cerita berikutnya.
