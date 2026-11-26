# Rencana Kerja Tahap 1 — Proyek Akhir Teknologi Big Data

## 1. Identitas Kelompok & Repository
- **Mata Kuliah:** Teknologi Big Data
- **Kelompok:** Kelompok 12
- **Topik:** Sistem Deteksi Anomali (Fraud) & Analitik Aktivitas E-Commerce Real-Time
- **Anggota Kelompok:**
  1. Muhamad Rifqi Fadil Itsnain (2406355306)
  2. Muhammad Zaki Al Khairi (2406432375)
  3. Muhammad Hashif Jade (2406396786)
  4. Zulfahmi Fajri (2406345425)
- **Repository GitHub:** https://github.com/ZulfahmiFjr/bigdata-ecommerce-fraud
- **Strategi Branch:**
  - `main`: menyimpan `README.md` pengenalan proyek terlebih dahulu hingga seluruh implementasi selesai dan siap digabungkan.
  - `dev`: branch pengembangan aktif untuk dokumen rancangan, PPT Progress Report, kode pipeline, skrip benchmark, dan bahan laporan akhir.

## 2. Hasil Pemeriksaan Kondisi VPS Ubuntu
Pemeriksaan dilakukan pada 27 November 2026 pada VPS Ubuntu 2 vCPU dan 4 GB RAM sebelum instalasi container.

| Komponen | Hasil Pengecekan | Catatan & Rekomendasi |
|---|---|---|
| CPU | 2 vCPU | Cukup untuk Spark mode `local[2]` dan container ringan |
| RAM Total | 3,6 GiB | Terpakai 2,0 GiB (available 1,6 GiB) oleh layanan VPS eksisting |
| Swap | 1,9 GiB (`/swap.img`, terpakai 801 MiB) | Perlu ditambah file swap sekunder +2 GiB (total ~4 GiB) sebelum menjalankan Docker agar aman dari OOM |
| Disk (`/`) | 59 GiB total, 28 GiB terpakai, **29 GiB tersedia** | Cukup longgar untuk image Docker ringan, data Parquet, dan MongoDB |
| Docker & Compose | Belum terpasang (`command not found`) | Akan dipasang pada awal Tahap 2 (`docker.io` + `docker-compose-plugin`) |
| Git & Python | Git 2.43.0, Python 3.12.3, `uv`, Java tersedia | Siap untuk skrip Python, pembuatan PPT, dan tooling pengembangan |
| Akses Root | `sudo` aktif | Memungkinkan penambahan swap sekunder dan instalasi Docker secara aman |

### Catatan Keamanan Resource untuk Tahap 2
Karena RAM fisik yang tersedia saat ini sekitar 1,6 GiB (selebihnya dipakai layanan eksisting VPS), pada Tahap 2 kami akan:
1. Menambahkan swap file sekunder 2 GiB (`/swapfile-bigdata`) tanpa mengubah `/swap.img` yang sudah ada.
2. Menerapkan `mem_limit` eksplisit di `docker-compose.yml` dengan total batas puncak <= 2,6 GB (Kafka KRaft 650m, Spark local[2] 1200m, MongoDB 512m, Streamlit 384m — dan saat operasi normal di VPS menjalankan benchmark batch secara terpisah dari mode streaming agar beban nyata tetap stabil di bawah 1,5 GB RAM).
3. Memantau `docker stats` dan `free -h` secara berkala selama pengujian.

## 3. Pemetaan Target Rubrik Nilai A (85–100)

| Kriteria Panduan | Bobot | Target Implementasi Kami |
|---|---|---|
| Justifikasi Big Data (3V+) | 15% | Analisis terukur Volume (jutaan baris historis + stream), Velocity (streaming per detik via Kafka), Variety (terstruktur, JSON semi-terstruktur, teks ulasan) serta bukti mengapa RDBMS biasa tidak efisien |
| Arsitektur & Metodologi | 25% | Diagram 4 layer modular (Ingestion -> Processing -> Storage -> Visualization) dengan alasan pemilihan setiap tool dan skema data yang jelas |
| Implementasi Teknis | 40% | Pipeline end-to-end berjalan stabil di VPS, kode Python modular, optimasi nyata Spark (`shuffle.partitions=4`, `partitionBy`, caching) disertai benchmark sebelum vs sesudah |
| Visualisasi & Insight | 10% | Dashboard Streamlit interaktif membaca MongoDB & Parquet, disertai panel Rekomendasi Aksi Preskriptif otomatis |
| Laporan & Presentasi | 10% | Laporan PDF lengkap (Abstrak, Bab 1–5, Daftar Pustaka), PPT Progress Report & PPT Final (slide terakhir link YouTube), dan arsip `.zip` untuk EMAS |

## 4. Jadwal Pengerjaan & Pembagian Tugas Kelompok 12

### Tahap 1 — Progress Report (Target selesai: 27–29 November 2026)
- Pemeriksaan resource VPS dan pembuatan struktur repository GitHub (`main` & `dev`).
- Penyusunan dokumen justifikasi 3V+ terukur dan rancangan arsitektur 4 layer.
- Pembuatan diagram arsitektur dan file PPT Progress Report + naskah presentasi.
- Perekaman dan unggah video YouTube Progress Report oleh Kelompok 12 sebelum 29 November 2026 pukul 23.59 WIB.

### Tahap 2 — Implementasi & Verifikasi di VPS
- Penambahan swap sekunder 2 GiB dan instalasi Docker + Docker Compose secara aman.
- Implementasi modular: `docker-compose.yml`, Python Producer (normal + pola fraud + ulasan), Kafka KRaft, PySpark Structured Streaming & Batch Benchmark, MongoDB + Partitioned Parquet, dan Streamlit Dashboard.
- Pengujian end-to-end, pemantauan `docker stats`, pengambilan log, hasil benchmark, dan screenshot dashboard.

### Tahap 3 — Final Deliverables (Upload EMAS)
- Penyusunan Laporan PDF lengkap (Abstrak, Bab 1–5, Daftar Pustaka).
- Pembuatan PPT Final dengan hasil demo nyata dan slot link YouTube di slide terakhir.
- Pengemasan file Laporan PDF + PPT Final ke arsip `.zip` siap unggah ke EMAS.

### Pembagian Peran Tim
| Anggota | Fokus Utama | Peran di Presentasi Progress Report |
|---|---|---|
| **Zulfahmi Fajri** | Infrastruktur VPS, Docker Compose, arsitektur sistem, integrasi repo & pipeline end-to-end | Pembukaan, latar belakang masalah, dan alur arsitektur 4 layer |
| **Muhamad Rifqi Fadil Itsnain** | Layer Ingestion (Python Producer, generator pola fraud & ulasan, Apache Kafka KRaft) | Justifikasi Big Data (3V+) dan alasan RDBMS tidak cukup |
| **Muhammad Zaki Al Khairi** | Layer Processing & Optimasi (PySpark Structured Streaming, partisi Parquet, benchmark) | Jenis data, pola anomali fraud, dan strategi optimasi Spark |
| **Muhammad Hashif Jade** | Layer Storage & Visualization (MongoDB, Parquet, Streamlit Dashboard, panel preskriptif) | Rancangan dashboard preskriptif, rencana kerja, dan penutup |
