# Naskah Panduan Presentasi YouTube — Progress Report (Kelompok 12)

Target durasi video: **6 sampai 8 menit** (ringkas, jelas, tidak bertele-tele, dan langsung menjawab semua poin panduan).

---

## Bagian 1 — Zulfahmi Fajri (Slide 1 & 2, ~1,5 menit)
- **Slide 1 (Cover):**
  "Halo Bapak/Ibu dosen dan teman-teman semua. Kami dari Kelompok 12 mata kuliah Teknologi Big Data yang beranggotakan Muhamad Rifqi Fadil Itsnain, Muhammad Zaki Al Khairi, Muhammad Hashif Jade, dan saya sendiri Zulfahmi Fajri. Pada Progress Report kali ini, kami memaparkan rancangan proyek akhir kami yang berjudul Sistem Deteksi Anomali Fraud dan Analitik Aktivitas E-Commerce Real-Time."
- **Slide 2 (Latar Belakang & Masalah):**
  "Setiap hari, platform e-commerce menerima jutaan aktivitas pengguna mulai dari klik produk, keranjang belanja, transaksi pembayaran, sampai ulasan pembeli. Masalahnya, celah kecepatan ini sering dimanfaatkan pelaku fraud, misalnya untuk card testing puluhan kali per menit atau pengambilalihan akun. Kalau pemeriksaan masih dilakukan secara manual atau rekap harian di malam hari, kerugian sudah telanjur terjadi. Karena itu kami merancang sistem yang bisa mendeteksi anomali secara real-time sekaligus menghasilkan rekomendasi tindakan langsung."

---

## Bagian 2 — Muhamad Rifqi Fadil Itsnain (Slide 3 & 4, ~2 menit)
- **Slide 3 (Justifikasi 3V+ Big Data):**
  "Kenapa kasus ini termasuk Big Data dan bukan sekadar data kecil yang dipaksakan? Kami mengukurnya lewat 3V+. Pertama, Volume: e-commerce menengah dengan 50 ribu pengguna aktif bisa menghasilkan sekitar 2 juta baris log per hari atau 60 juta baris per bulan. Di proyek ini kami menyiapkan simulasi data historis hingga skala jutaan baris dan stream berkelanjutan. Kedua, Velocity: event datang setiap detik sehingga deteksi fraud butuh latensi rendah lewat streaming, bukan batch harian. Ketiga, Variety: kami menggabungkan tiga jenis data sekaligus, yaitu data terstruktur transaksi, data semi-terstruktur JSON clickstream, dan data tidak terstruktur berupa teks ulasan pembeli."
- **Slide 4 (Mengapa RDBMS Tradisional Tidak Cukup):**
  "Kalau seluruh beban ini dipaksakan ke satu database RDBMS biasa, ada tiga kendala utama. Saat trafik tinggi, operasi tulis beruntun memicu lock dan bottleneck. Lalu skema tabel yang kaku menyulitkan penyimpanan clickstream JSON yang atributnya berubah-ubah dan teks ulasan bebas. Selain itu, agregasi historis jutaan baris lewat full table scan akan lambat dan mengganggu transaksi operasional. Karena itu kami memisahkan ingest, pemrosesan stream/batch, dan penyimpanan khusus."

---

## Bagian 3 — Muhammad Zaki Al Khairi (Slide 5, 6, & 7, ~2,5 menit)
- **Slide 5 (Jenis Data & Pola Fraud):**
  "Agar pipeline tetap simpel dan tidak perlu stream join yang rumit, kami menyatukan tiga jenis data tersebut dalam satu topik Kafka bernama ecommerce_events. Setiap event membawa angka transaksi, objek JSON clickstream, dan teks ulasan. Dari situ kami mendeteksi tiga pola fraud utama: Transaksi Kilat lima kali atau lebih dalam satu menit, Nominal Melonjak di atas sepuluh juta rupiah, dan Ulasan Indikasi Penipuan, ditambah satu sinyal bisnis untuk kategori yang ramai diklik tetapi rendah checkout."
- **Slide 6 (Arsitektur 4 Layer):**
  "Berikut diagram arsitektur 4 layer yang kami rancang. Di Layer 1 Ingestion, Python Producer mengirim stream ke satu topik Apache Kafka mode KRaft tanpa Zookeeper. Di Layer 2 Processing, Apache Spark PySpark menjalankan dua skrip yang jelas perannya: stream_fraud_detector untuk deteksi real-time, dan batch_benchmark untuk optimasi dan uji performa data historis. Di Layer 3 Storage, hasil real-time masuk ke MongoDB sedangkan arsip historis disimpan dalam format Parquet terpartisi. Terakhir di Layer 4 Visualization, Streamlit Dashboard membaca kedua storage untuk menampilkan grafik dan rekomendasi aksi."
- **Slide 7 (Tech Stack & Strategi Optimasi Spark):**
  "Seluruh sistem kami rancang agar bisa berjalan nyata dan stabil di VPS dengan 2 vCPU dan 4 GB RAM, menggunakan batas memori eksplisit di Docker Compose maksimal 2,6 GB. Untuk memenuhi kriteria optimasi performa di Spark, kami menurunkan spark.sql.shuffle.partitions menjadi 4 agar cocok dengan core VPS, mempartisi Parquet berdasarkan event_date dan category untuk partition pruning, serta memakai caching. Di Tahap 2 nanti, kami akan menjalankan skrip benchmark untuk membuktikan perbandingan waktu eksekusi sebelum dan sesudah optimasi."

---

## Bagian 4 — Muhammad Hashif Jade (Slide 8, 9, & 10, ~1,5 menit)
- **Slide 8 (Rancangan Dashboard & Insight Preskriptif):**
  "Dashboard Streamlit kami tidak hanya berhenti di grafik deskriptif. Kami menambahkan panel Rekomendasi Aksi Preskriptif untuk empat kondisi nyata: akun dengan transaksi kilat disarankan blokir sementara dan verifikasi OTP, transaksi di atas sepuluh juta disarankan ditahan untuk konfirmasi manual, merchant dengan ulasan indikasi penipuan disarankan diaudit dan ditahan pencairannya, serta kategori yang tinggi klik tetapi rendah checkout disarankan mendapat voucher diskon."
- **Slide 9 (Rencana Implementasi & Progress Saat Ini):**
  "Sampai tahap Progress Report ini, kami sudah memeriksa kesiapan VPS, menyiapkan repository GitHub beserta struktur proyek modular, menyusun analisis 3V+ dan desain arsitektur 4 layer, serta menyiapkan rencana pembagian kerja tim. Langkah kami berikutnya di Tahap 2 adalah instalasi Docker dan swap tambahan di VPS, membangun seluruh pipeline end-to-end, menjalankan benchmark optimasi Spark, lalu menyusun laporan akhir PDF dan video demo final di Tahap 3."
- **Slide 10 (Penutup):**
  "Sekian pemaparan Progress Report dari Kelompok 12. Terima kasih atas perhatiannya, sampai jumpa di demonstrasi sistem final kami."
