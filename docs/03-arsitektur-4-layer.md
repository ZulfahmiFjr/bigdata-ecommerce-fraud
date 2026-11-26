# Rancangan Arsitektur 4 Layer & Strategi Optimasi

## 1. Gambaran Aliran Data End-to-End
Arsitektur sistem kami dibagi menjadi 4 lapisan modular yang saling terpisah (*decoupled*) agar mudah dirawat, hemat resource di VPS 2 vCPU / 4 GB RAM, dan siap diskalakan (*scale-out*):

`Sumber Event (Transaksi + Clickstream JSON + Ulasan Teks)`
-> **Layer 1: Ingestion** (`Python Producer` -> `Apache Kafka KRaft`)
-> **Layer 2: Processing & Optimization** (`Apache Spark PySpark local[2]` — Streaming & Batch)
-> **Layer 3: Storage** (`MongoDB` untuk data streaming/alert + `Partitioned Parquet` untuk data historis)
-> **Layer 4: Visualization & Prescriptive Insight** (`Streamlit Dashboard`)

Diagram visual arsitektur tersimpan pada: `docs/assets/arsitektur-4-layer.png`.

## 2. Detail Setiap Layer & Alokasi Resource VPS
Total batas puncak seluruh container di `docker-compose.yml` dijaga **<= 2,6 GB RAM** (sehingga aman di VPS 4 GB RAM + total 4 GB swap tanpa mengganggu layanan eksisting).

| Layer | Komponen / Tool | Peran Utama | Konfigurasi Hemat RAM | Batas `mem_limit` |
|---|---|---|---|---|
| **1. Ingestion** | Python Producer | Mensimulasikan replay transaksi normal, injeksi 4 pola fraud, event clickstream JSON, dan ulasan teks pembeli | Script Python ringan (`kafka-python`) | ~128 MB (proses/container ringan) |
| **1. Ingestion** | Apache Kafka (Mode KRaft) | Message broker berkecepatan tinggi tanpa Zookeeper; memisahkan producer dari consumer | `KAFKA_HEAP_OPTS="-Xmx384m -Xms256m"`, 3 topik terpisah (`ecommerce.transactions`, `ecommerce.clickstream`, `ecommerce.reviews`) | **650m** |
| **2. Processing** | Apache Spark (PySpark) | Structured Streaming untuk deteksi fraud real-time (windowing, scoring risiko) + Batch ETL & benchmark optimasi | Mode `local[2]` (tanpa Master/Worker terpisah), `SPARK_DRIVER_MEMORY=768m`, `spark.sql.shuffle.partitions=4` | **1200m** |
| **3. Storage** | MongoDB + Parquet Lokal | MongoDB menyimpan event terbaru, alert fraud, dan rekomendasi preskriptif; Parquet menyimpan arsip historis terpartisi | MongoDB `--wiredTigerCacheSizeGB 0.25`; Parquet `snappy` terpartisi `event_date` & `category` | **512m** (MongoDB) |
| **4. Visualization** | Streamlit Dashboard | Menampilkan KPI real-time, grafik trafik, tabel alert fraud, performa optimasi Spark, dan panel Rekomendasi Aksi Preskriptif | Polling ringan ke MongoDB & pembacaan terfilter ke Parquet | **384m** |

*Catatan operasional VPS:* Total batas gabungan 4 container utama adalah 650m + 1200m + 512m + 384m = 2.746 MB secara batas maksimum, namun dalam operasional nyata Spark hanya memakai heap aktif ~500–768 MB dan tugas batch benchmark dijalankan bergantian sehingga konsumsi puncak aktual di VPS tetap **<= 2,6 GB RAM** (dan dipantau dengan `docker stats`).

## 3. Rancangan Skema Data

### A. Topik Kafka
1. `ecommerce.transactions` (Structured -> JSON payload):
   `event_id`, `event_time`, `user_id`, `merchant_id`, `category`, `amount_idr`, `quantity`, `payment_method`, `city`, `device_id`, `is_simulated_fraud`
2. `ecommerce.clickstream` (Semi-Structured JSON):
   `session_id`, `event_time`, `user_id`, `action` (`view`, `add_to_cart`, `checkout`), `category`, `product_id`, `metadata` (nested object: `browser`, `os`, `ip`, `referrer`)
3. `ecommerce.reviews` (Unstructured Text + Metadata):
   `review_id`, `event_time`, `user_id`, `merchant_id`, `category`, `rating`, `review_text`

### B. Koleksi MongoDB (Hot / Operational Data)
- `realtime_metrics`: ringkasan trafik, nilai transaksi, dan rasio fraud per jendela waktu (1 menit).
- `fraud_alerts`: daftar transaksi/akun yang terdeteksi anomali lengkap dengan `risk_score` (0–100), `fraud_reasons`, dan status tindak lanjut.
- `prescriptive_actions`: daftar rekomendasi tindakan otomatis yang siap ditampilkan ke tim operasional.
- `benchmark_results`: hasil pengukuran waktu eksekusi Spark sebelum vs sesudah optimasi.

### C. Penyimpanan Historis Parquet (Cold / Analytical Data)
Disimpan pada volume lokal `data/parquet/events/` dengan struktur partisi hierarkis:
```text
data/parquet/events/
├── event_date=2026-11-25/
│   ├── category=elektronik/part-*.snappy.parquet
│   ├── category=fashion/part-*.snappy.parquet
│   └── category=gadget/part-*.snappy.parquet
└── event_date=2026-11-26/
    └── ...
```

## 4. Strategi Optimasi Apache Spark (Syarat Nilai A)
Kami tidak hanya menjalankan Spark secara default, melainkan menerapkan 4 teknik optimasi nyata yang akan diuji lewat skrip benchmark di Tahap 2:
1. **Penyesuaian Shuffle Partitions:** Menurunkan `spark.sql.shuffle.partitions` dari default `200` menjadi `4` agar sesuai dengan 2 vCPU VPS dan menghilangkan overhead penjadwalan ratusan task kosong.
2. **Partitioning Parquet (`partitionBy("event_date", "category")`):** Memungkinkan *partition pruning* sehingga query berdasarkan tanggal dan kategori hanya membaca folder relevan, bukan seluruh dataset.
3. **Format Columnar + Kompresi Snappy:** Menyimpan data historis dalam Parquet dibandingkan CSV/JSON mentah agar ukuran file lebih kecil dan pembacaan kolom agregasi jauh lebih cepat.
4. **Caching / Persist (`df.persist(StorageLevel.MEMORY_AND_DISK)`):** Mencegah Spark menghitung ulang transformasi dasar saat menjalankan beberapa agregasi analitik berulang dalam satu sesi batch.

### Skenario Benchmark Sebelum vs Sesudah Optimasi
Skrip `processing/benchmark_spark.py` pada Tahap 2 akan membandingkan secara adil (pada dataset historis yang sama):
- **Baseline (Tanpa Optimasi):** Membaca CSV/JSON mentah atau Parquet tanpa partisi, `spark.sql.shuffle.partitions=200`, tanpa caching.
- **Optimized:** Membaca Parquet terpartisi `event_date` & `category`, `spark.sql.shuffle.partitions=4`, dengan caching/persist.
- **Metrik yang dicatat:** Durasi eksekusi (detik), percepatan (*speedup*), dan ukuran penyimpanan di disk (MB).

## 5. Rancangan Dashboard & Insight Preskriptif
Dashboard Streamlit akan dibagi menjadi 4 bagian utama:
1. **Ringkasan Real-Time (KPI):** Total event masuk, total nilai transaksi (GMV), jumlah alert fraud aktif, dan persentase anomali.
2. **Analitik Aktivitas & Deteksi Fraud:** Grafik tren transaksi vs fraud per menit, distribusi jenis anomali (Velocity Burst, High-Value Spike, Geo Hopping, Review Bot), serta tabel detail akun/transaksi berisiko tinggi.
3. **Panel Rekomendasi Aksi Preskriptif (Nilai Tambah Utama):**
   - *Keamanan Akun:* Jika `risk_score >= 80` atau terjadi >= 5 transaksi dalam 1 menit -> rekomendasikan **Blokir Sementara Akun & Minta Verifikasi OTP/KYC**.
   - *Keamanan Merchant:* Jika merchant menerima lonjakan ulasan negatif mengandung kata kunci penipuan -> rekomendasikan **Audit Toko & Tahan Pencairan Dana Sementara**.
   - *Strategi Konversi Bisnis:* Jika kategori produk memiliki rasio klik tinggi tetapi konversi checkout < 10% -> rekomendasikan **Terbitkan Voucher Diskon 10–15% / Gratis Ongkir Khusus Kategori Tersebut**.
4. **Panel Performa Big Data:** Grafik perbandingan waktu eksekusi Spark sebelum vs sesudah optimasi partisi dan caching.
