# Justifikasi Big Data (3V+) & Karakteristik Masalah

## 1. Latar Belakang Masalah
Platform e-commerce modern mencatat jutaan aktivitas pengguna setiap hari, mulai dari klik produk, pencarian barang, penambahan keranjang, hingga transaksi pembayaran dan ulasan pembeli. Di balik tingginya transaksi tersebut, pelaku kecurangan (*fraud*) memanfaatkan celah kecepatan transaksi, misalnya melakukan pengujian kartu (*card testing*) puluhan kali dalam hitungan detik, pengambilalihan akun (*account takeover*) dari perangkat dan lokasi berbeda, hingga manipulasi ulasan produk menggunakan akun bot.

Jika pemeriksaan anomali hanya dilakukan secara manual atau melalui rekap harian di akhir malam, kerugian finansial sudah telanjur terjadi dan dana transaksi sudah berpindah. Oleh karena itu, kami merancang **Sistem Deteksi Anomali (Fraud) & Analitik Aktivitas E-Commerce Real-Time** yang memproses aliran kejadian saat itu juga (*low latency*) sekaligus menyimpan data historis dalam format terpartisi untuk kebutuhan analisis dan optimasi query skala besar.

## 2. Analisis 3V+ Secara Terukur

### A. Volume (Skala Data Besar)
- **Kondisi dunia nyata:** Platform e-commerce skala menengah dengan 50.000 pengguna aktif harian yang menghasilkan rata-rata 40 event clickstream dan transaksi per pengguna per hari akan membentuk **2.000.000 baris log per hari**, atau sekitar **60 juta baris per bulan** (belasan hingga puluhan gigabyte data mentah).
- **Skala implementasi & simulasi kami di VPS:** Kami menyiapkan generator/replay data historis berskala ratusan ribu hingga **1.000.000+ baris transaksi & clickstream** untuk pengujian batch processing dan benchmark partisi Parquet, ditambah data streaming berkelanjutan yang terus bertambah di MongoDB dan storage lokal.

### B. Velocity (Kecepatan Aliran Data)
- **Kondisi dunia nyata:** Pada jam sibuk atau promo tanggal kembar, aktivitas masuk secara kontinu hingga ratusan sampai ribuan event per detik. Deteksi fraud harus terjadi dalam hitungan detik (*near real-time*), bukan menunggu rekap harian.
- **Skala implementasi kami:** Python Producer mengalirkan event transaksi, clickstream, dan ulasan ke **Apache Kafka (KRaft)** secara terus-menerus (dapat diatur 20–200 event/detik pada VPS 2 vCPU) dan langsung diproses menggunakan **PySpark Structured Streaming** dengan *sliding/tumbling window* untuk mendeteksi lonjakan aktivitas anomali secara langsung.

### C. Variety (Keberagaman Format Data)
Sistem kami menangani **tiga jenis data berbeda** dalam satu pipeline terpadu:
1. **Data Terstruktur (Structured):** Data transaksi numerik dan tabel tetap seperti `transaction_id`, `user_id`, `amount_idr`, `quantity`, `payment_method`, `timestamp`, dan `status`.
2. **Data Semi-Terstruktur (Semi-Structured):** Log *clickstream* dan metadata sesi dalam format **JSON bersarang (nested)** yang atributnya bisa bervariasi per jenis event (misalnya `view_item`, `add_to_cart`, `checkout`, `device_info`, `geo_location`, `ip_address`).
3. **Data Tidak Terstruktur (Unstructured):** Teks bebas **ulasan pembeli** (*customer review text*) berbahasa Indonesia/Inggris yang dianalisis untuk mendeteksi indikasi ulasan spam, kata kunci keluhan penipuan, atau sentimen negatif berulang pada toko tertentu.

### D. Nilai Tambah: Veracity & Value
- **Veracity (Keakuratan Data):** Data streaming sering mengandung duplikasi event, field kosong, atau timestamp terlambat (*late-arriving data*). Kami menangani ini melalui validasi skema dan *watermarking* di Spark Structured Streaming.
- **Value (Nilai Bisnis Preskriptif):** Data tidak berhenti pada angka statistik, melainkan diubah menjadi **rekomendasi aksi langsung** seperti pemblokiran sementara akun berisiko tinggi dan pemberian voucher tertarget untuk kategori produk yang ramai diklik tetapi rendah checkout.

## 3. Mengapa Tidak Efisien dengan RDBMS Tradisional?

| Aspek | RDBMS Tradisional (misal MySQL/PostgreSQL tunggal) | Pendekatan Big Data Kami (Kafka + Spark + MongoDB + Parquet) |
|---|---|---|
| **Kecepatan Tulis (High Velocity)** | Tulis langsung ke tabel relasional memicu *row/table lock*, overhead indeks B-Tree, dan berisiko *bottleneck* saat lonjakan trafik | Kafka bertindak sebagai *distributed buffer* berkecepatan tinggi sehingga ingest terpisah dari beban pemrosesan |
| **Skema Multi-Format (Variety)** | Skema kolom kaku; menyimpan clickstream JSON bervariasi dan teks ulasan membuat tabel penuh NULL atau mahal saat di-JOIN | MongoDB menyimpan dokumen JSON fleksibel tanpa migrasi skema kaku, sementara Parquet menyimpan skema kolom terkompresi |
| **Deteksi Real-Time (Windowing)** | Query agregasi berulang tiap detik (polling) membebani database operasional utama | Spark Structured Streaming memproses agregasi *windowed* secara inkremental pada aliran data langsung |
| **Analisis Historis Skala Jutaan Baris (Volume)** | *Full table scan* pada jutaan baris log lambat dan boros I/O disk | Parquet berformat *columnar* dengan partisi `event_date` dan `category` memangkas data yang dibaca (*partition pruning*) |
| **Skalabilitas** | Cenderung *scale-up* (menambah spek satu mesin) yang mahal dan punya batas fisik | Arsitektur modular siap *scale-out* (menambah broker Kafka, worker Spark, atau shard MongoDB) |

## 4. Sifat Pemrosesan (Hybrid: Stream + Batch)
Kami menerapkan pola pemrosesan gabungan (*Lambda-lite*):
- **Real-Time / Stream Processing:** Memproses event yang baru masuk dari Kafka untuk mendeteksi fraud berlatensi rendah dan memperbarui metrik dashboard secara langsung.
- **Batch Processing:** Mengolah arsip data historis dalam format Parquet untuk analisis tren konversi per kategori, analisis sentimen/kata kunci ulasan, serta **benchmark performa Spark** (perbandingan waktu eksekusi sebelum dan sesudah optimasi partisi dan caching).

## 5. Tiga Pola Anomali Fraud & Satu Sinyal Bisnis yang Dideteksi
Agar logika sistem tetap sederhana, mudah dijelaskan, dan langsung berdampak ke operasional, kami fokus pada 3 pola fraud utama ditambah 1 sinyal konversi bisnis:
1. **Transaksi Kilat (Velocity Burst / Card Testing):** Satu akun melakukan >= 5 transaksi beruntun dalam jendela waktu 1 menit -> *Aksi:* blokir sementara akun dan minta verifikasi OTP.
2. **Nominal Melonjak (High-Value Spike):** Nominal transaksi melebihi Rp10.000.000 dalam satu kali pembayaran -> *Aksi:* tahan transaksi sementara untuk konfirmasi manual.
3. **Ulasan Indikasi Penipuan (Unstructured Text):** Teks ulasan pembeli mengandung kata kunci keluhan penipuan (*palsu*, *penipu*, *scam*, *barang kosong*, *bohong*, *abal-abal*) -> *Aksi:* audit toko dan tahan pencairan dana sementara.
4. **Konversi Rendah (Clickstream Funnel):** Kategori produk mencatat jumlah klik tinggi tetapi rasio checkout di bawah 10% -> *Aksi:* rekomendasikan penerbitan voucher diskon 10–15% atau gratis ongkir khusus kategori tersebut.
