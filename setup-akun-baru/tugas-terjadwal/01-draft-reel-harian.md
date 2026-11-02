# Draft reel Arunika harian

- **Jadwal:** setiap hari 06.36 WIB (cron `CRON_TZ=Asia/Jakarta 36 6 * * *`)
- **Konektor wajib:** Notion, Buffer, ElevenLabs, elevenlabs_2, elevenlabs_3, elevenlabs_4, Metricool (cadangan), Claude Code Remote (untuk send_later)
- **Notifikasi:** push
- **Persetujuan:** otomatis (auto)

## Instruksi (tempel apa adanya)

```
Tugas harian Arunika (@kabar.arunika): dalam SATU sesi ini siapkan 2 reel Instagram, slot PAGI (upload 08.00 WIB) dan slot SORE prime time (upload 17.45 WIB). TIDAK ADA carousel (dihentikan founder 3 Nov 2026: carousel tidak ada penonton) — jangan membuat, menawarkan, atau menjadwalkan carousel. Bahasa Indonesia santai; sebut diri "saya" dan user "kamu" (jangan panggil "Mas"). Setiap slot bertahap melalui gerbang persetujuan, dengan ATURAN AUTO-LANJUT di bawah supaya upload tetap sesuai jadwal. (Instruksi versi 3 Nov 2026: audit hook & naskah sebelum VO, render dari repo arunika-media/tools, tanpa Scribe, jadwal lewat Buffer, tanpa carousel.)

ATURAN AUTO-LANJUT (wewenang dari founder, 30 Okt 2026)
- Setiap kali selesai mengirim pesan gerbang (Gerbang 1, 2, 3, atau 4), langsung pasang send_later (konektor Claude_Code_Remote, delay_minutes 5, initiation human_request, name "Auto-lanjut <slot> gerbang <n>") dengan message: "Auto-lanjut <slot> gerbang <n>: kalau user belum membalas pesan gerbang <n> slot <slot> sejak dikirim, lanjutkan sendiri dengan rekomendasi Claude (hook rekomendasi / VO apa adanya / gaya rekomendasi / upload). Kalau user sudah membalas atau gerbang ini sudah lewat, abaikan pengingat ini."
- Saat pengingat itu tiba: jika user belum membalas, lanjutkan ke gerbang berikutnya memakai pilihan yang Claude rekomendasikan, dan sebut di awal pesan berikutnya "Auto-lanjut (tidak ada balasan 5 menit): memakai <pilihan>". Jika user sudah membalas, ikuti balasannya; jangan memproses dua kali.
- Setelah Gerbang 4 tanpa balasan 5 menit, jalankan langkah UPLOAD & LAPORAN persis seperti saat user membalas "upload".
- Jika jam slot sudah lewat atau kurang dari 10 menit lagi saat upload, jadwalkan 15 menit dari sekarang dan sebutkan di laporan.
- Balasan user kapan pun tetap diutamakan: revisi atau "stop" menghentikan auto-lanjut untuk slot itu.

LANGKAH PERTAMA (sebelum apa pun)
Pasang pengingat ke sesi ini dengan send_later (konektor Claude_Code_Remote, initiation human_schedule) untuk jam 14.35 WIB hari ini (07:35 UTC), name "Draft sore Arunika", message: "Slot SORE: jalankan alur yang sama (Persiapan → Gerbang 1–4 → Upload & Laporan → Penutup, termasuk ATURAN AUTO-LANJUT 5 menit dan audit hook + naskah sebelum VO) untuk reel upload 17.45 WIB. Slot sore WAJIB konten lepas (bukan part seri) dengan topik dan kategori berbeda dari reel pagi. Baca ulang Log Perbaikan (status Aktif) dan Pedoman Naskah & Caption sebelum menulis naskah. Kalau slot pagi belum selesai, selesaikan dulu dengan auto-lanjut lalu kerjakan slot sore. Sebelum membuat reel sore, cek database Konten: kalau slot sore hari ini sudah punya reel berstatus Dijadwalkan, jangan buat lagi dan laporkan saja. Tidak ada carousel."

PERSIAPAN (tiap slot)
1. Muat skill `arunika-reels` (Skill tool) dan ikuti seluruh aturannya versi terbaru, terutama "Formula retensi", "Alur 8 tahap", "Sinkron per kata & render", dan "Upload & jadwal (Buffer)". Muat juga skill `arunika-hooks` dan `arunika-script-audit` (dipakai di Gerbang 1). Abaikan saran carousel di dokumen mana pun.
2. WAJIB baca di Notion:
   - Log Perbaikan (collection://bd7a37f2-5219-4217-87c2-9f95e0841cfc): semua perbaikan berstatus "Aktif" atau "Dipertahankan" HARUS diterapkan di naskah, visual, subtitle, caption, jam tayang, pemilihan topik, dan alur kerja. Jika bertentangan dengan aturan lama (di skill atau dokumen lain), Log Perbaikan yang berlaku. Perhatikan juga Usulan bersumber "Founder" (revisi yang pernah diminta founder): hindari mengulang kesalahan yang sama.
   - SOP Produksi Reel (page id 408e9231d0be8193893acc77d78b14f2), Pedoman Naskah & Caption (page id 408e9231d0be8196b054ce6ec8322c3b) dan Pedoman Brand (page id 408e9231d0be8193b0caf1cf6d276ef3).
3. Clone repo media: `git clone --depth 1 https://github.com/sulistiyono346/arunika-media` (bila push nanti ditolak 403, pakai add_repo access push). Baca `tools/README.md`, lalu salin `tools/align.py` dan `tools/render_polaroid.py` ke folder kerja per slot (mis. pagi/ dan sore/); `tools/mix.py` dipanggil langsung. Aset (logo, Aru) dibaca dari `assets/` repo. Bila project Reels bisa dibaca, baca juga `jadwal/log-konten.md` dan `analisa/insight-reels-2026-10-28.md`; kalau tidak bisa, lanjut tanpa itu (database Konten jadi sumber utama).
4. Pilih topik dari Bank Ide di Notion (collection://d793e833-bf1f-42b6-85c4-0f6b16f62b01) dan halaman Rencana Konten minggu berjalan. Topik harus belum ada di database Konten (collection://0af3e860-c352-41de-980c-580402ff49d2). Cek juga database Konten untuk slot hari ini: kalau slot itu sudah punya reel berstatus "Dijadwalkan", jangan buat reel baru untuk slot itu.
   - SLOT PAGI = part berikutnya dari seri yang sedang berjalan (cek kolom Seri dan episode terakhir yang benar-benar tayang di database Konten, bukan hanya jadwal di Rencana Konten; jangan mengulang topik episode yang sudah tayang). Maksimal 1 part seri per hari. Kalau tidak ada seri yang sedang berjalan, pilih ide Prioritas "Tinggi" yang momennya paling dekat (boleh membuka seri baru sebagai Part 1).
   - SLOT SORE = konten lepas, bukan part seri, dengan topik dan kategori berbeda dari reel pagi. Utamakan Prioritas "Tinggi"; jaga variasi kategori (jangan dua reel topik uang dalam sehari bila ada ide sains/sejarah berprioritas tinggi).

OBSERVASI REVISI FOUNDER (berlaku di semua gerbang)
Setiap kali founder merevisi, memilih selain rekomendasi Claude (mis. memilih hook 2 padahal rekomendasinya hook 1, atau gaya lain), atau mengoreksi sesuatu: terapkan dulu ke reel ini, lalu catat polanya di Log Perbaikan. Cari dulu baris yang polanya sama:
- Belum ada: buat baris baru, Status "Usulan", Jenis "Taktis", Sumber "Founder", Area yang sesuai, judul berupa aturan umum (bukan detail reel ini), Bukti "Revisi founder <tanggal>, reel <judul>: <apa yang diminta>".
- Sudah ada dan berstatus Usulan (berarti pola ini muncul kedua kalinya): ubah Status menjadi "Aktif", Mulai berlaku hari ini, tambahkan bukti kedua.
Jangan menanyakan izin untuk pencatatan ini; sebut singkat di pesan berikutnya ("dicatat sebagai pola revisi"). Auto-lanjut tanpa balasan BUKAN revisi founder dan tidak dicatat.

GERBANG 1 — DRAFT + AUDIT
Tulis naskah mengikuti alur di Pedoman Naskah & Caption dan skill arunika-reels. Hook harus tampil sebagai 3 hook sekaligus di detik pertama: visual, ucapan VO, dan teks layar yang sama-sama menyebut topik. Hitung perkiraan detik tiap adegan dengan tempo ±2,2 kata per detik (hanya untuk memperkirakan durasi; tidak ada batas jumlah kata).
Sebelum dikirim: jalankan `arunika-hooks` (skor hook rekomendasi ≥80/100; kalau kurang, pakai versi tulis ulangnya) lalu `arunika-script-audit`. Perbaiki naskah sampai status audit "siap VO." (tanpa ✗). VO tidak boleh dibuat sebelum lolos audit.
Kirim ke user lewat SendUserMessage, diawali label slot ("PAGI · upload 08.00" atau "SORE · upload 17.45"):
- topik dan sudut pandang (untuk seri: sebut seri dan nomor part);
- 3 varian hook (label teknik, tandai rekomendasi; tiap varian sebut visual + ucapan + teks layarnya) + blok AUDIT HOOK (log hooks scan + skor) untuk hook rekomendasi;
- blok AUDIT NASKAH (log script-audit) dan apa yang diperbaiki;
- konsep visual, naskah VO per adegan (angka ditulis huruf, satu paragraf = satu adegan, perkiraan detik per adegan dan total), teks layar per adegan, judul cover "Part n" bila serial;
- caption siap tempel (sudah lewat penyaring anti-AI);
- satu baris "Perbaikan diterapkan:" berisi kode PRB yang dipakai.
Akhiri dengan: "Balas yes untuk lanjut ke VO, pilih varian hook lain (mis. 'hook 2'), atau tulis revisinya. Tanpa balasan 5 menit, saya lanjut dengan hook rekomendasi." Pasang pengingat auto-lanjut, lalu BERHENTI dan tunggu. Bila user merevisi naskah, jalankan ulang audit sebelum VO.

GERBANG 2 — VO
Setelah yes (atau auto-lanjut): buat VO dengan suara Maliq Nganjuk (voice_id EIcz16yo4q5hJFhNay0n, model eleven_v4, generations_count 1) lewat konektor `elevenlabs_2`; kalau habis kuota/sibuk/gagal, pakai `ElevenLabs`, lalu `elevenlabs_3` / `elevenlabs_4`, dan sebut akun yang dipakai. Error 429 atau "Free generations are busy … Nothing was charged" = belum ada kredit terpakai → langsung pindah akun; jangan ulang generasi yang sudah dimulai. VO dipakai apa adanya: tidak dipercepat atau diperlambat. Unduh MP3 dengan curl dari content_url (domain elevenlabsusercontent.com dan storage.googleapis.com sudah diizinkan). Kirim MP3 (SendUserFile) + durasinya, lalu tulis: "Balas yes untuk lanjut ke pilihan animasi. Tanpa balasan 5 menit, saya lanjut." Pasang pengingat auto-lanjut, lalu BERHENTI dan tunggu.

GERBANG 3 — PILIH ANIMASI
Setelah yes (atau auto-lanjut): buat 3 sampel gaya berupa GAMBAR DIAM (frame adegan pembuka/hook, 1080x1920, lengkap dengan teks layar hook dan contoh subtitle), bukan klip. Untuk part seri, salah satu sampel memakai gaya part sebelumnya agar seri tetap konsisten. Minimal satu memakai gaya dengan data terbaik untuk kategori topik ini (hitung dari database Konten: rata-rata % ditonton, like, share per gaya), satu boleh gaya baru untuk diuji. Gaya Polaroid bisa langsung dibuat dengan `render_polaroid.py stills`; gaya lain dengan salinan renderer itu (helper Aru, Si Bocor, kartu, panah, subtitle tetap dipakai). Jangan pakai gaya yang dihentikan di Log Perbaikan (saat ini: kartun kepala bulat). Kirim ketiganya (SendUserFile) dengan label 1/2/3 dan satu rekomendasi berbasis data beserta alasan 1–2 kalimat. Tulis: "Balas nomor gaya pilihanmu (boleh dengan catatan revisi). Tanpa balasan 5 menit, saya pakai gaya rekomendasi." Pasang pengingat auto-lanjut, lalu BERHENTI dan tunggu.

GERBANG 4 — VIDEO
Setelah user memilih (atau auto-lanjut dengan gaya rekomendasi): ikuti "Sinkron per kata & render" di skill arunika-reels. Waktu teks layar dari jeda VO nyata (ffmpeg silencedetect → isi SEGS & CHUNKS di align.py → timing.json), TANPA Scribe. Sesuaikan renderer (SC, CAPTIONS, JANJI_T, FOLLOW, kartu & adegan, judul cover, catatan kaki, events), lalu `export TOTAL=<durasi VO + 0,8>` → `render_polaroid.py events` → `mix.py` → contact sheet `stills` (cek frame 0, tumpang tindih, teks terpotong, glyph hilang, sinkron) → render penuh 2 bagian paralel → mux → cek 4 frame + loudness ±-14 LUFS. Subtitle: maksimal 2 baris di layar, 3–5 kata per baris, angka dan kata kunci berwarna aksen. Kirim MP4 (SendUserFile) + caption dalam blok kode + jam upload slotnya, lalu tulis: "Balas upload untuk menjadwalkan, atau tulis revisinya. Tanpa balasan 5 menit, saya jadwalkan otomatis." Pasang pengingat auto-lanjut, lalu BERHENTI dan tunggu.

UPLOAD & LAPORAN
Jika user membalas "upload" (atau auto-lanjut setelah 5 menit tanpa balasan):
- kirim MP4 ke repo sulistiyono346/arunika-media sebagai `reels/YYYY-MM-DD_<pagi|sore>_<slug>.mp4`, commit, push ke main; pastikan link raw https://raw.githubusercontent.com/sulistiyono346/arunika-media/main/reels/<file> membalas HTTP 200;
- jadwalkan reel lewat BUFFER (alat utama): get_account → list_channels (Instagram kabar.arunika) → list_posts status scheduled (cek bentrok & kuota 10 post) → create_post dengan mode customScheduled, dueAt WIB berakhiran +07:00, schedulingType automatic, metadata.instagram {type: reel, shouldShareToFeed: true}, asset video url raw dengan thumbnailOffset 0, teks = caption final. Bila Buffer gagal, pakai Metricool createScheduledPost (blogId 7728239, media url raw, instagramData type REEL, autoPublish true, timezone Asia/Jakarta) sebagai cadangan;
- tanpa minta konfirmasi ulang.
- LAPORAN UPLOAD (wajib, permintaan founder): langsung kirim lewat SendUserMessage DAN PushNotification (ringkasan dalam tag <routine_summary>, kalimat pertama = "Reel <slot> dijadwalkan <jam> WIB: <judul>"). Isi: judul, slot + jam tayang, gaya, durasi, id post Buffer (atau link planner Metricool), link file di GitHub, akun ElevenLabs yang dipakai, ringkasan audit, dan daftar gerbang yang berjalan lewat auto-lanjut beserta pilihan yang dipakai. Jika GitHub atau penjadwalan gagal, laporkan kegagalannya dengan cara yang sama beserta errornya dan apa yang perlu dilakukan user.
- Pasang send_later 15 menit setelah jam tayang reel (initiation human_request, name "Cek tayang <judul>"), message: "Cek tayang reel <judul>: periksa apakah reel sudah benar-benar terbit (Buffer list_posts status sent/error untuk post ini, atau Metricool getScheduledPosts bila dijadwalkan lewat Metricool). Kirim hasilnya ke user lewat SendUserMessage DAN PushNotification: 'Reel <judul> sudah tayang: <url Instagram>' bila berhasil, atau status/error bila belum terbit beserta saran tindakan. Isi kolom Video di database Konten dengan url Instagram bila sudah ada."
- Pasang pengingat send_later 30 menit setelah jam tayang reel (initiation human_schedule), message: "Rutinitas engagement reel <judul>: kirim ke user pengingat 30 menit engagement (balas semua komentar di reel ini; komentari 5–10 unggahan akun explainer/edukasi sejenis dengan komentar yang menambah informasi). Tawarkan: kalau user menempelkan komentar yang masuk, susun draf balasan yang memancing obrolan."

PENUTUP (tiap slot)
- Tambahkan/perbarui baris di database Konten Notion: Judul, Status ("Siap upload" atau "Dijadwalkan"), Seri, Gaya, Kategori, Durasi, Tanggal tayang, Link jadwal (id post Buffer + jam WIB + link video, atau link Metricool), Naskah (teks VO final lengkap persis seperti yang dibacakan, dengan detik per adegan), Caption (caption final), Skor hook ("4/4 lolos", "3/4", atau "2/4 atau kurang", plus skor 0–100 dari arunika-hooks di Catatan QA), Catatan QA (ringkasan audit naskah: yang gagal → perbaikan, serta hasil cek render), dan di Pelajaran tulis kode PRB yang diterapkan (sebut juga bila ada revisi founder dan gerbang mana yang auto-lanjut).
- Ubah status ide di Bank Ide menjadi "Sudah dibuat". Bila reel ini part seri dan part berikutnya sudah dijanjikan di reel, tambahkan/tandai ide part berikutnya di Bank Ide dengan Status "Dipilih".
- Bila project Reels bisa ditulis, tambahkan 1 baris ke `jadwal/log-konten.md` lalu tulis ulang doc tersebut.
```
