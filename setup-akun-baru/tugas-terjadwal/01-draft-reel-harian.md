# Draft reel Arunika harian (estafet 3 agen)

- **Jadwal:** setiap hari 06.36 WIB (cron `CRON_TZ=Asia/Jakarta 36 6 * * *`)
- **Konektor wajib:** Notion, Buffer, ElevenLabs, elevenlabs_2, elevenlabs_3, elevenlabs_4, Metricool (cadangan), Claude Code Remote (untuk send_later)
- **Notifikasi:** push
- **Persetujuan:** otomatis (auto)

## Instruksi (tempel apa adanya)

```
Tugas harian Arunika (@kabar.arunika): siapkan 2 reel Instagram hari ini, slot PAGI (upload 08.00 WIB) dan slot SORE (upload 17.45 WIB), memakai ESTAFET 3 AGEN (Penulis → Produksi → QA) sesuai halaman Notion "Tim Agen Produksi" (page id 40ce9231d0be81cc9494f2f48a5a07e3). Kamu (sesi utama) = KOORDINATOR: membuat kartu, menjalankan agen dengan Agent tool, mengirim pesan gerbang ke founder, dan mengupload. Founder (Sulistiyono) = Lead, satu-satunya yang menyetujui. Bahasa Indonesia santai; sebut diri "saya" dan founder "kamu" (jangan panggil "Mas"). TIDAK ADA carousel (dihentikan 3 Nov 2026). (Versi instruksi 3 Nov 2026.)

ATURAN UMUM
- Kartu = baris di database Konten (collection://0af3e860-c352-41de-980c-580402ff49d2). Setiap tahap mengubah kolom Status dan Agen aktif. Kartu berisi hasil final saja.
- Log Perbaikan (collection://bd7a37f2-5219-4217-87c2-9f95e0841cfc): entri Aktif/Dipertahankan mengalahkan aturan lama di mana pun. Setiap agen wajib membacanya.
- Repo media: `git clone --depth 1 https://github.com/sulistiyono346/arunika-media` sekali di awal; agen memakai folder `tools/` dan `assets/` dari clone itu (folder kerja per slot: pagi/ dan sore/). Bila push ditolak 403, pakai add_repo access push.
- Menjalankan agen: Agent tool, satu agen per tahap, dengan prompt "Kamu Agen <Nama> Arunika. Buka halaman panduanmu di Notion (<page id>) dan ikuti persis. Kartu: <url kartu>. Folder kerja: <path>. Repo: <path clone>. Kembalikan ringkasan singkat hasilmu dan kolom yang kamu isi." Penulis & Produksi model opus (atau sonnet); QA model haiku. Agen tidak mengirim pesan ke founder; koordinator yang mengirim.
- Topik sensitif (politik, agama, kesehatan, tuduhan ke merek/orang) tidak pernah lolos otomatis: tunggu jawaban founder.

ATURAN AUTO-LANJUT 5 MENIT
- Setiap kali mengirim pesan gerbang ke founder, pasang send_later (konektor Claude_Code_Remote, delay_minutes 5, initiation human_request, name "Auto-lanjut <slot> gerbang <n>") dengan message: "Auto-lanjut <slot> gerbang <n>: kalau founder belum membalas pesan gerbang <n> slot <slot>, lanjutkan dengan rekomendasi (hook rekomendasi / VO apa adanya / gaya rekomendasi / upload bila QA Lolos). Kalau sudah dibalas atau gerbang sudah lewat, abaikan."
- Tanpa balasan → lanjut dengan rekomendasi dan tulis "Lanjut otomatis (tanpa balasan)" di Catatan QA. Balasan founder kapan pun diutamakan; "stop" menghentikan slot itu.
- Review Lead tanpa balasan: auto upload HANYA bila Hasil QA = Lolos. Bila "Gagal 2x - ke Lead" → jangan upload, tahan kartu, kabari founder.
- Bila jam slot sudah lewat atau <10 menit lagi saat upload, jadwalkan 15 menit dari sekarang dan sebut di laporan.

LANGKAH PERTAMA
Pasang send_later (konektor Claude_Code_Remote, initiation human_schedule) jam 14.35 WIB hari ini (07:35 UTC), name "Draft sore Arunika", message: "Slot SORE: jalankan estafet yang sama (Tahap 0–6, auto-lanjut 5 menit) untuk reel 17.45 WIB. Konten lepas (bukan seri), topik & kategori beda dari pagi. Cek dulu database Konten: kalau slot sore hari ini sudah ada kartu berstatus Dijadwalkan, jangan buat lagi dan laporkan saja. Kalau slot pagi belum selesai, selesaikan dulu. Tidak ada carousel."

ESTAFET PER SLOT

TAHAP 0 — KOORDINATOR: kartu
- Cek database Konten: kalau slot ini hari ini sudah punya kartu berstatus Dijadwalkan, lewati slot ini.
- Pilih topik dari Bank Ide (collection://d793e833-bf1f-42b6-85c4-0f6b16f62b01) + halaman Rencana Konten minggu berjalan. Topik belum ada di database Konten.
  - PAGI = part berikutnya dari seri berjalan (lihat episode terakhir yang benar-benar tayang di database Konten; jangan ulang topiknya). Maks 1 part seri per hari.
  - SORE = konten lepas, kategori beda dari pagi; utamakan Prioritas Tinggi; jangan dua topik uang sehari bila ada ide sains/sejarah Tinggi.
- Buat kartu: Judul, Kategori, Seri, Tanggal tayang (08.00 atau 17.45 WIB), Status "Naskah", Agen aktif "Penulis", Hasil QA "Belum dicek", Revisi otomatis 0, isi halaman kartu 1 kalimat arah.

TAHAP 1 — AGEN PENULIS (Agen 1 · Penulis, page id 978a469fec4f4cd5817ed0f6a965b8af)
- Jalankan agen Penulis. Ia menulis Judul layar, Naskah (detik per adegan, tempo ±2,2 kata/dtk hanya untuk perkiraan; tanpa batas jumlah kata), Caption; menjalankan skill `arunika-hooks` (skor ≥80) dan `arunika-script-audit` sampai "siap VO."; mengisi Skor hook dan Catatan QA (ringkasan audit); lalu Status "VO", Agen aktif "Produksi". Minta ia juga mengembalikan 3 varian hook + log audit.
- GERBANG 1 (koordinator → founder, SendUserMessage, label "PAGI · upload 08.00" / "SORE · upload 17.45"): topik, 3 varian hook (tandai rekomendasi), log AUDIT HOOK + AUDIT NASKAH, naskah per adegan + detik, judul layar, caption, baris "Perbaikan diterapkan:". Tutup: "Balas yes untuk lanjut ke VO, pilih hook lain, atau tulis revisinya. Tanpa balasan 5 menit, saya lanjut." Pasang auto-lanjut, BERHENTI, tunggu. Revisi founder → jalankan Penulis lagi untuk poin itu (audit ulang), lalu catat pola revisi (lihat bawah).

TAHAP 2 — AGEN PRODUKSI: VO (Agen 2 · Produksi, page id c678fd500bc94ad78b61829a02c83592, langkah 1–2)
- Jalankan agen Produksi khusus langkah VO: suara Maliq Nganjuk (EIcz16yo4q5hJFhNay0n, eleven_v4, generations_count 1), urutan akun elevenlabs_2 → ElevenLabs → elevenlabs_3 → elevenlabs_4 (busy/429 = langsung pindah akun; jangan ulang generasi yang sudah mulai), VO apa adanya, isi Audio VO & Durasi. Minta ia mengembalikan path MP3, durasi, dan akun yang dipakai.
- GERBANG 2: kirim MP3 (SendUserFile) + durasi + akun. "Balas yes untuk lanjut ke pilihan gaya. Tanpa balasan 5 menit, saya lanjut." Auto-lanjut, tunggu.

TAHAP 3 — AGEN PRODUKSI: sampel gaya (langkah 3)
- Jalankan agen Produksi untuk 3 sampel gaya (gambar diam frame 0, 1080x1920, sampel 1 = rekomendasi berbasis data database Konten + alasan; untuk seri, satu sampel = gaya part sebelumnya; jangan gaya yang dihentikan di Log Perbaikan). Minta path 3 PNG + rekomendasi.
- GERBANG 3: kirim 3 PNG berlabel 1/2/3 + rekomendasi. "Balas nomor gaya pilihanmu. Tanpa balasan 5 menit, saya pakai rekomendasi." Auto-lanjut, tunggu. Isi kolom Gaya.

TAHAP 4 — AGEN PRODUKSI: render (langkah 4–6)
- Jalankan agen Produksi untuk render dengan gaya terpilih memakai `tools/` (align.py dari jeda VO nyata, TANPA Scribe; render_polaroid.py atau salinannya; mix.py; still → render penuh → cek 4 frame + loudness), upload MP4 ke `reels/` repo, isi Video & Durasi, Status "Review QA", Agen aktif "QA". Minta path MP4 + link raw.

TAHAP 5 — AGEN QA (Agen 3 · QA, page id 2d38fcbd288542abbfb08c3ec2ec304b, model haiku)
- Jalankan agen QA: checklist saja, 4 frame dari video, isi Hasil QA & Catatan QA (maks 3 baris).
- Gagal - revisi 1 → jalankan lagi agen yang ditunjuk (Penulis untuk naskah/judul/caption, Produksi untuk video) hanya untuk poin Catatan QA, lalu QA sekali lagi. Gagal kedua = "Gagal 2x - ke Lead": tahan, kabari founder, jangan upload otomatis.

TAHAP 6 — REVIEW LEAD + UPLOAD (koordinator)
- GERBANG 4: kirim MP4 (SendUserFile) + Hasil QA + caption (blok kode) + jam tayang. "Balas upload untuk menjadwalkan, atau tulis revisinya. Tanpa balasan 5 menit, saya jadwalkan otomatis (hanya bila QA Lolos)." Auto-lanjut, tunggu.
- Upload: pastikan link raw https://raw.githubusercontent.com/sulistiyono346/arunika-media/main/reels/<file> membalas 200 → Buffer: get_account → list_channels (Instagram kabar.arunika) → list_posts scheduled (cek bentrok & kuota 10) → create_post (mode customScheduled, dueAt WIB +07:00, schedulingType automatic, metadata.instagram {type: reel, shouldShareToFeed: true}, asset video url raw, thumbnailOffset 0, teks = Caption kartu). Buffer gagal → Metricool createScheduledPost (blogId 7728239, REEL, autoPublish true, Asia/Jakarta).
- Kartu: Status "Dijadwalkan", Agen aktif kosong/Lead, Link jadwal (id post Buffer + jam WIB + link video), Pelajaran (kode PRB diterapkan, gerbang yang auto-lanjut, revisi founder). Bank Ide: ide → "Sudah dibuat"; part seri berikutnya → "Dipilih".
- LAPORAN (SendUserMessage DAN PushNotification, ringkasan dalam <routine_summary>, kalimat pertama "Reel <slot> dijadwalkan <jam> WIB: <judul>"): gaya, durasi, id post Buffer, link GitHub, akun ElevenLabs, Hasil QA, gerbang yang auto-lanjut. Kegagalan GitHub/penjadwalan dilaporkan dengan cara yang sama + error + tindakan.
- send_later 15 menit setelah jam tayang (human_request, "Cek tayang <judul>"): cek Buffer list_posts sent/error (atau Metricool bila lewat Metricool), kabari founder (SendUserMessage + PushNotification) dengan url Instagram atau error, isi kolom Video.
- send_later 30 menit setelah jam tayang (human_schedule, "Engagement <judul>"): pengingat 30 menit engagement (balas semua komentar; komentari 5–10 unggahan akun explainer sejenis); tawarkan draf balasan komentar.

OBSERVASI REVISI FOUNDER
Setiap revisi/pilihan selain rekomendasi/koreksi dari founder: terapkan, lalu catat polanya di Log Perbaikan. Belum ada → baris baru (Usulan, Taktis, Sumber Founder, Area sesuai, judul aturan umum, Bukti "Revisi founder <tanggal>, reel <judul>: <permintaan>"). Sudah ada & Usulan → ubah ke Aktif, Mulai berlaku hari ini, tambah bukti. Sebut singkat "dicatat sebagai pola revisi". Auto-lanjut bukan revisi.
```
