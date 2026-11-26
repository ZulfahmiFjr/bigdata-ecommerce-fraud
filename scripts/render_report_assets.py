import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "evidence", "report_assets")
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def render_box(lines, out_name, mode="terminal"):
    # render kotak gelap polos tajam tanpa dekorasi jendela tambahan biar serasi dgan gaya laporan
    font = ImageFont.truetype(FONT_MONO, 25)
    font_b = ImageFont.truetype(FONT_MONO_B, 25)
    pad_x, pad_y = 32, 24
    line_h = 37
    dummy = Image.new("RGB", (10, 10))
    dd = ImageDraw.Draw(dummy)
    max_w = max(dd.textbbox((0, 0), ln, font=font)[2] for ln in lines)
    w = max(1320, max_w + pad_x * 2)
    h = len(lines) * line_h + pad_y * 2

    bg = (24, 24, 24) if mode == "terminal" else (30, 30, 30)
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    y = pad_y
    for ln in lines:
        col = (232, 232, 232)
        f = font
        s = ln.lstrip()
        if mode == "code":
            if s.startswith("#"):
                col = (106, 153, 85)
            elif any(s.startswith(k) for k in ("def ", "if ", "elif ", "else:", "for ", "return ", "services:", "kafka:", "mongodb:", "spark:", "dashboard:")):
                col = (86, 156, 214)
        else:
            if s.startswith("ubuntu@vps"):
                col = (78, 201, 176)
                f = font_b
            elif s.startswith("NAME") or s.startswith("[benchmark] SELESAI"):
                col = (220, 220, 170)
                f = font_b
        draw.text((pad_x, y), ln, font=f, fill=col)
        y += line_h

    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, out_name)
    img.save(out_path, "PNG", optimize=True)
    print(f"SAVED {out_name}: {w}x{h}")


def main():
    render_box([
        'services:',
        '  kafka:',
        '    image: apache/kafka:3.9.0',
        '    mem_limit: 650m',
        '    environment:',
        '      KAFKA_PROCESS_ROLES: broker,controller',
        '      KAFKA_HEAP_OPTS: "-Xmx384m -Xms256m"',
        '  mongodb:',
        '    image: mongo:7',
        '    mem_limit: 512m',
        '    command: ["mongod", "--wiredTigerCacheSizeGB", "0.25", "--quiet"]',
        '  spark:',
        '    mem_limit: 1200m',
        '    environment:',
        '      SPARK_DRIVER_MEMORY: 768m',
        '    command: ["/opt/spark/bin/spark-submit", "--master", "local[2]",',
        '              "--driver-memory", "768m", "/app/processing/stream_fraud_detector.py"]',
        '  dashboard:',
        '    mem_limit: 384m',
        '    ports: ["8501:8501"]',
    ], "code_docker_compose.png", mode="code")

    render_box([
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ docker compose ps',
        'NAME             IMAGE                               SERVICE     STATUS                   PORTS',
        'bdef-dashboard   bigdata-ecommerce-fraud-dashboard   dashboard   Up 38 minutes            0.0.0.0:8501->8501/tcp',
        'bdef-kafka       apache/kafka:3.9.0                  kafka       Up 37 minutes (healthy)  9092/tcp',
        'bdef-mongodb     mongo:7                             mongodb     Up 38 minutes (healthy)  127.0.0.1:27017->27017/tcp',
        'bdef-producer    bigdata-ecommerce-fraud-producer    producer    Up 37 minutes',
        'bdef-spark       bigdata-ecommerce-fraud-spark       spark       Up 33 minutes',
        '',
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ docker stats --no-stream',
        'NAME             CPU %     MEM USAGE / LIMIT     MEM %',
        'bdef-kafka       1.87%     327.1MiB / 650MiB     50.32%',
        'bdef-spark       33.99%    219.5MiB / 1.172GiB   18.29%',
        'bdef-producer    1.42%     17.55MiB / 128MiB     13.71%',
        'bdef-dashboard   0.00%     18.89MiB / 384MiB     4.92%',
        'bdef-mongodb     29.45%    168.3MiB / 512MiB     32.87%',
    ], "term_docker_status.png", mode="terminal")

    render_box([
        'def make_event(event_type, user_id, merchant_id, category, amount_idr=0, quantity=1, review_text="", rating=0):',
        '    # gabungin 3 jenis data (terstruktur, JSON clickstream, teks ulasan) dlam satu pesan JSON',
        '    return {',
        '        "event_id": str(uuid.uuid4())[:12], "event_time": datetime.now(timezone.utc).isoformat(),',
        '        "event_type": event_type, "user_id": user_id, "merchant_id": merchant_id,',
        '        "category": category, "amount_idr": int(amount_idr), "quantity": int(quantity),',
        '        "clickstream": {"session_id": f"sess_{random.randint(10000,99999)}", "device": random.choice(DEVICES),',
        '                        "city": random.choice(CITIES), "referrer": random.choice(REFERRERS)},',
        '        "review_text": review_text, "rating": int(rating),',
        '    }',
        '# injeksi 3 pola fraud secara berkala (burst 6x, nominal > 10 juta, ulasan penipuan)',
        'if cycle % 35 == 0:    # transaksi kilat (6 checkout beruntun dari satu akun)',
        'elif cycle % 22 == 0:  # nominal melonjak Rp11,5 juta - Rp26 juta',
        'elif cycle % 28 == 0:  # ulasan rating 1 dgan kata kunci penipuan',
    ], "code_producer.png", mode="code")

    render_box([
        'def build_spark_session():',
        '    # mode local[2] sama shuffle partitions 4 biar pas sama VPS 2 vCPU dan hemat RAM',
        '    return (SparkSession.builder.appName("EcommerceFraudRealTimeDetector").master("local[2]")',
        '            .config("spark.sql.shuffle.partitions", "4")',
        '            .config("spark.sql.parquet.compression.codec", "snappy").getOrCreate())',
        '',
        '# simpen arsip historis ke parquet terpartisi berdasarkan tanggal sama kategori',
        'enriched.coalesce(1).write.mode("append").partitionBy("event_date", "category").parquet(parquet_dir)',
        '',
        '# deteksi 3 pola fraud dan sinyal konversi rendah -> simpan alert + aksi preskriptif ke mongodb',
        'if amt > 10_000_000:                     # Nominal Melonjak -> tahan transaksi, konfirmasi manual',
        'if FRAUD_REVIEW_PATTERN.search(txt):     # Ulasan Penipuan  -> audit toko, tahan pencairan dana',
        'if len(tx_list) >= 5:                    # Transaksi Kilat  -> blokir sementara + verifikasi OTP',
        'if views >= 5 and conv_rate < 10.0:      # Konversi Rendah  -> rekomendasi voucher diskon 10-15%',
    ], "code_spark_stream.png", mode="code")

    render_box([
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ docker logs --tail 5 bdef-producer',
        '[producer] total event terkirim ke \'ecommerce_events\': 1440',
        '[producer] total event terkirim ke \'ecommerce_events\': 1500',
        '[producer] total event terkirim ke \'ecommerce_events\': 1560',
        '[producer] total event terkirim ke \'ecommerce_events\': 1620',
        '[producer] total event terkirim ke \'ecommerce_events\': 1680',
        '',
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ docker exec bdef-mongodb mongosh --quiet ecommerce_bigdata --eval ...',
        'realtime_metrics: 5  |  fraud_alerts: 30  |  prescriptive_actions: 31  |  benchmark_results: 1',
        'fraud_by_type:  Nominal Melonjak (14), Ulasan Penipuan (8), Transaksi Kilat (8)',
        'actions_by_cat: Verifikasi Transaksi (14), Keamanan Akun (8), Audit Merchant (8), Optimasi Konversi (1)',
        '',
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ find data/parquet/events -maxdepth 2 -type d | sort',
        'data/parquet/events/event_date=2026-11-26/category=elektronik',
        'data/parquet/events/event_date=2026-11-26/category=fashion',
        'data/parquet/events/event_date=2026-11-26/category=gadget',
        'data/parquet/events/event_date=2026-11-26/category=kecantikan',
        'data/parquet/events/event_date=2026-11-26/category=rumah_tangga',
    ], "term_pipeline_storage.png", mode="terminal")

    render_box([
        '# skenario 1 sebelum optimasi: baca JSON tanpa partisi, shuffle partitions default 200, tanpa cache',
        'spark.conf.set("spark.sql.shuffle.partitions", "200")',
        'base_df = spark.read.json(raw_json_dir).filter((F.col("event_date") == target_date) & (F.col("category") == target_cat))',
        'run_analytics_queries(base_df)',
        '',
        '# skenario 2 sesudah optimasi: parquet terpartisi (partition pruning), shuffle partitions 4, persist',
        'spark.conf.set("spark.sql.shuffle.partitions", "4")',
        'opt_df = (spark.read.parquet(opt_parquet_dir)',
        '          .filter((F.col("event_date") == target_date) & (F.col("category") == target_cat))',
        '          .persist(StorageLevel.MEMORY_AND_DISK))',
        'run_analytics_queries(opt_df)',
    ], "code_benchmark.png", mode="code")

    render_box([
        'ubuntu@vps:~/projects/bigdata-ecommerce-fraud$ bash scripts/run_benchmark.sh',
        '[benchmark] menyiapkan dataset historis sebanyak 1,000,000 baris',
        '[benchmark] ukuran disk -> raw JSON: 180.77 MB | parquet terpartisi: 9.18 MB (hemat 94.92%)',
        '[benchmark] SEBELUM optimasi (raw JSON, shuffle=200, no cache): 39.722 detik',
        '[benchmark] SESUDAH optimasi (parquet partisi, shuffle=4, cache): 6.966 detik',
        '[benchmark] hasil benchmark berhasil disimpan ke mongodb dan JSON evidence',
        '[benchmark] SELESAI -> percepatan 5.7x (82.46% lebih cepat), hemat disk 94.92%',
    ], "term_benchmark.png", mode="terminal")


if __name__ == "__main__":
    main()
