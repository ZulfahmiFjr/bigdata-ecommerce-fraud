# bigdata-ecommerce-fraud

proyek akhir mata kuliah teknologi big data kelompok 12, fokus ke sistem deteksi anomali fraud dan analitik aktivitas e-commerce secara real-time dgan arsitektur ringan yg aman jalan di VPS terbatas

## anggota kelompok 12

- muhamad rifqi fadil itsnain (2406355306)
- muhammad zaki al khairi (2406432375)
- muhammad hashif jade (2406396786)
- zulfahmi fajri (2406345425)

## ringkasan proyek

sistem ini kami bikin buat nangani data transaksi, clickstream JSON, dan ulasan teks pembeli yg masuk cepet tiap detik, kalo cuma pake database relasional biasa bakalan berat pas volume udah jutaan baris atau lagi rame trafik, jadi kami bangun pipeline 4 layer yg modular dan hemat RAM

## arsitektur 4 layer

- **ingestion**: python producer simulasi transaksi normal, pola fraud, dan ulasan teks pembeli ke apache kafka mode kraft tanpa zookeeper
- **processing**: apache spark pyspark structured streaming dan batch mode local[2] dgan optimasi shuffle partitions, partisi parquet berdasarkan tanggal dan kategori, serta benchmark sebelum vs sesudah optimasi
- **storage**: mongodb buat nyimpen data streaming JSON dan alert fraud, ditambah parquet terpartisi buat data historis skala besar
- **visualization**: dashboard streamlit interaktif yg nampilin trafik real-time, deteksi fraud, sama panel rekomendasi aksi preskriptif buat tim operasional

## batasan resource VPS

proyek ini dirancang khusus biar jalan stabil di VPS 2 vCPU dan 4 GB RAM, semua container dikasih batas RAM eksplisit total puncak di bawah 2,6 GB RAM biar sistem tetap lancar dan ga kena OOM

## status pengerjaan dan branch

pengembangan aktif, dokumen rancangan, PPT progress report, kode pipeline, sampai bahan laporan PDF saat ini dikerjain di branch `dev` dulu, branch `main` cuma nyimpen gambaran proyek ini sampai seluruh tahap selesai dan siap digabung
