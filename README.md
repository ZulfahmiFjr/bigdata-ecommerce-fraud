# Big Data E-Commerce Fraud & Real-Time Analytics

Proyek akhir mata kuliah Teknologi Big Data dari Kelompok 12, fokusnya bikin sistem deteksi anomali fraud dan analitik aktivitas e-commerce secara real-time dgan arsitektur ringan yg aman jalan di VPS terbatas.

## Anggota Kelompok 12

- Muhamad Rifqi Fadil Itsnain (2406355306)
- Muhammad Zaki Al Khairi (2406432375)
- Muhammad Hashif Jade (2406396786)
- Zulfahmi Fajri (2406345425)

## Ringkasan Proyek

Sistem ini kami bangun buat nangani aliran data transaksi, clickstream JSON, dan ulasan teks pembeli yg masuk tiap detik, kalo cuma ngandelin RDBMS biasa pasti berat pas volume udah tembus jutaan baris atau lagi rame trafik, jadi kami pake arsitektur 4 layer yg modular, simpel dipahami, dan hemat RAM.

## Arsitektur 4 Layer

- **Ingestion:** Python Producer ngirim simulasi transaksi normal, 3 pola fraud, clickstream JSON, dan ulasan teks ke satu topik Apache Kafka mode KRaft tanpa Zookeeper (`ecommerce_events`)
- **Processing:** Apache Spark (PySpark) mode `local[2]` jalanin Structured Streaming buat deteksi fraud plus skrip Batch buat optimasi partisi, caching, dan benchmark sebelum vs sesudah
- **Storage:** MongoDB buat nyimpen metrik real-time, alert fraud, dan rekomendasi aksi, ditambah Parquet terpartisi berdasarkan tanggal dan kategori buat arsip historis
- **Visualization:** Streamlit Dashboard interaktif yg nampilin grafik aktivitas live, tabel alert fraud, hasil benchmark Spark, sama panel rekomendasi aksi preskriptif

## Pola Deteksi dan Aksi Preskriptif

- **Transaksi Kilat (Velocity Burst):** satu akun bikin >= 5 transaksi dalam 1 menit, sistem nyaranin blokir sementara akun plus verifikasi OTP
- **Nominal Melonjak (High-Value Spike):** transaksi di atas Rp10 juta langsung ditandai buat ditahan sementara sambil nunggu konfirmasi manual
- **Ulasan Indikasi Penipuan:** teks ulasan yg ngandung kata kunci penipuan bikin sistem nyaranin audit toko dan tahan pencairan dana sementara
- **Konversi Rendah:** kategori yg tinggi klik tapi rasio checkout di bawah 10 persen dapet rekomendasi voucher diskon atau gratis ongkir

## Batasan Resource VPS

Semua layanan dikasih batas RAM eksplisit di Docker Compose supaya total puncak tetep di bawah 2,6 GB RAM dan lancar jalan di VPS 2 vCPU 4 GB RAM, Apache Kafka KRaft dibatasi 650 MB, PySpark 1200 MB, MongoDB 512 MB, Streamlit 384 MB, dan Python Producer 128 MB.

## Struktur Folder

- `ingestion/` kode Python Producer buat simulasi aliran event ke Apache Kafka
- `processing/` skrip PySpark Structured Streaming deteksi fraud dan Batch Benchmark optimasi
- `storage/` utilitas koneksi MongoDB dan pembacaan arsip Parquet terpartisi
- `dashboard/` aplikasi UI interaktif Streamlit
- `docs/` dokumen analisis 3V+, desain arsitektur 4 layer, naskah presentasi, dan bukti pengujian
- `deliverables/` file PPT Progress Report, bahan Laporan PDF, dan PPT Final

## Cara Menjalankan Singkat

Pastikan Docker dan Docker Compose udah aktif di VPS atau laptop, trus jalankan `docker compose up -d --build` buat nyalain seluruh pipeline secara otomatis, setelah itu buka browser ke port `8501` buat liat Streamlit Dashboard dan jalankan `bash scripts/run_benchmark.sh` kalo mau ngulang pengujian benchmark Spark.

