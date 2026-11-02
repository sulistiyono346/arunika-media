# Setup akun Claude baru untuk Arunika

Folder ini berisi semua yang dibutuhkan supaya akun Claude lain bisa langsung memproduksi reel Arunika (@kabar.arunika) dengan aturan terbaru. Terakhir diperbarui 3 Nov 2026.

```
setup-akun-baru/
├── README.md                 ← panduan ini
├── konteks.md                ← hal yang biasanya diingat Claude (gaya bahasa, alat, ID Notion)
├── skills/
│   ├── arunika-reels/        ← alur produksi 8 tahap
│   ├── arunika-hooks/        ← audit & tulis ulang hook
│   ├── arunika-script-audit/ ← audit struktur naskah sebelum VO
│   └── *.zip                 ← versi zip siap upload
└── tugas-terjadwal/
    ├── 01-draft-reel-harian.md
    ├── 02-analisa-mingguan.md
    ├── 03-riset-tren-mingguan.md
    └── 04-tinjauan-bulanan.md
```

Skrip render (`tools/`), logo, dan maskot (`assets/`) ada di repo yang sama, jadi tidak perlu dipindahkan.

## Langkah (±10 menit)

### 1. Hubungkan konektor
Di akun baru: **Settings → Connectors**, lalu login dengan akun yang sama seperti sekarang:
- **Notion** (workspace Arunika HQ)
- **Buffer** (organisasi "My organization", channel Instagram kabar.arunika)
- **ElevenLabs** — 4 akun. Akun pertama lewat konektor ElevenLabs biasa; akun 2–4 sebagai *custom connector* `https://api.elevenlabs.io/v1/mcp`, beri nama `elevenlabs_2`, `elevenlabs_3`, `elevenlabs_4`.
- **Metricool** (cadangan jadwal + analitik, brand 7728239)
- **GitHub** (supaya bisa push video ke repo `sulistiyono346/arunika-media`)

### 2. Izinkan domain unduhan VO
**Settings → Capabilities → Additional allowed domains**: tambahkan `elevenlabsusercontent.com` dan `storage.googleapis.com`.

### 3. Pasang 3 skill
**Settings → Capabilities → Skills → Upload skill**, upload satu per satu:
- `skills/arunika-reels.zip`
- `skills/arunika-hooks.zip`
- `skills/arunika-script-audit.zip`

(Unduh zip dari GitHub: buka file-nya → tombol *Download raw file*.)

### 4. Buat tugas terjadwal
Cara paling cepat: buka chat baru di akun itu (Claude dengan akses cloud / Claude Code) dan kirim:

> Clone https://github.com/sulistiyono346/arunika-media, baca folder `setup-akun-baru/`, lalu buat semua tugas terjadwal di `tugas-terjadwal/` persis sesuai jadwal, konektor, dan instruksinya. Baca juga `konteks.md`.

Atau buat manual: setiap file di `tugas-terjadwal/` berisi jadwal (cron WIB), konektor yang wajib dipasang, dan blok instruksi yang tinggal ditempel.

### 5. Matikan tugas di akun lama
Supaya reel tidak dibuat dua kali, nonaktifkan tugas dengan nama yang sama di akun lama (atau biarkan jalan di satu akun saja).

### 6. Tes
Di akun baru, kirim: "pakai skill arunika-reels, audit naskah ARN-24 di Notion". Kalau audit keluar dalam format log, setup berhasil.

## Yang tidak ikut pindah
- **Memori Claude** (fakta tentang kamu dan kanal). Ringkasan pentingnya ada di `konteks.md`; minta Claude di akun baru membacanya, atau simpan sebagai instruksi project/preferensi.
- **Riwayat chat dan artifact** (mis. Strategi Pertumbuhan 30 Hari, Media Kit) tetap di akun lama. Bagikan link artifact ke akun baru bila perlu.
- **Project "Reels"** (file `jadwal/log-konten.md`, `analisa/…`) tetap di akun lama; database Konten di Notion sudah jadi sumber utama.

Repo ini publik: jangan menaruh API key, password, atau data pribadi di folder ini.
