import os
from PIL import Image, ImageDraw, ImageFont

# atur ukuran kanvas rasio 2:1 biar tajam pas dipasang di PPT atau laporan PDF
WIDTH, HEIGHT = 2200, 1080
BG_COLOR = (248, 250, 252)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def draw_rounded_box(draw, xy, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(draw, x1, y1, x2, y2, color=(71, 85, 105), width=4, head=14):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    if x2 > x1 and abs(y2 - y1) < 10:
        pts = [(x2, y2), (x2 - head, y2 - head // 2), (x2 - head, y2 + head // 2)]
    elif y2 > y1 and abs(x2 - x1) < 10:
        pts = [(x2, y2), (x2 - head // 2, y2 - head), (x2 + head // 2, y2 - head)]
    elif y2 < y1 and abs(x2 - x1) < 10:
        pts = [(x2, y2), (x2 - head // 2, y2 + head), (x2 + head // 2, y2 + head)]
    else:
        pts = [(x2, y2), (x2 - head, y2 - head // 2), (x2 - head, y2 + head // 2)]
    draw.polygon(pts, fill=color)


def draw_centered_text(draw, box, text, font, fill):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 - th) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=fill)


def draw_multiline(draw, x, y, lines, font, fill, line_gap=8):
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        cy += (bbox[3] - bbox[1]) + line_gap
    return cy


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    f_title = load_font(FONT_BOLD, 34)
    f_sub = load_font(FONT_REG, 20)
    f_layer = load_font(FONT_BOLD, 21)
    f_card_title = load_font(FONT_BOLD, 21)
    f_card_body = load_font(FONT_REG, 17)
    f_badge = load_font(FONT_BOLD, 16)
    f_small = load_font(FONT_REG, 15)

    # tulis judul diagram di bagian atas biar langsung kebaca konteksnya
    draw.text((55, 34), "Arsitektur 4 Layer — Sistem Deteksi Fraud & Analitik E-Commerce Real-Time", font=f_title, fill=(15, 23, 42))
    draw.text((55, 82), "Kelompok 12 Teknologi Big Data  |  Desain Modular & Hemat Resource VPS (2 vCPU, 4 GB RAM, Target Puncak <= 2,6 GB RAM)", font=f_sub, fill=(71, 85, 105))

    # konfigurasi 4 kolom layer utama biar jaraknya rapi dan simetris
    cols = [
        ("LAYER 1: INGESTION", (30, 58, 95), (239, 246, 255), (147, 197, 253), 55, 515),
        ("LAYER 2: PROCESSING", (15, 118, 110), (240, 253, 250), (94, 234, 212), 575, 1075),
        ("LAYER 3: STORAGE", (146, 64, 14), (255, 251, 235), (252, 211, 77), 1135, 1615),
        ("LAYER 4: VISUALIZATION", (67, 56, 202), (238, 242, 255), (165, 180, 252), 1675, 2145),
    ]

    top_y, bot_y = 140, 965
    for label, hdr_col, bg_col, brd_col, x1, x2 in cols:
        draw_rounded_box(draw, (x1, top_y, x2, bot_y), 18, bg_col, brd_col, 3)
        draw_rounded_box(draw, (x1, top_y, x2, top_y + 56), 18, hdr_col)
        draw.rectangle((x1, top_y + 36, x2, top_y + 56), fill=hdr_col)
        draw_centered_text(draw, (x1, top_y, x2, top_y + 56), label, f_layer, (255, 255, 255))

    # isi kartu pada layer 1 ingestion (sumber data -> producer -> kafka kraft)
    # kartu 1a sumber 3 jenis data
    draw_rounded_box(draw, (80, 225, 490, 425), 14, (255, 255, 255), (191, 219, 254), 2)
    draw.text((102, 242), "Sumber Data (3 Variety)", font=f_card_title, fill=(30, 58, 95))
    draw_multiline(draw, 102, 280, [
        "- Terstruktur: Transaksi & nominal",
        "- Semi-Terstruktur: JSON clickstream",
        "- Tidak Terstruktur: Teks ulasan",
        "- Skenario: Normal + 3 pola fraud",
    ], f_card_body, (51, 65, 85), 10)

    draw_arrow(draw, 285, 425, 285, 472, (30, 58, 95), 4, 13)

    # kartu 1b python producer
    draw_rounded_box(draw, (80, 475, 490, 625), 14, (255, 255, 255), (191, 219, 254), 2)
    draw.text((102, 492), "Python Event Producer", font=f_card_title, fill=(30, 58, 95))
    draw_multiline(draw, 102, 528, [
        "- Replay dataset & stream real-time",
        "- Injeksi burst, spike, ulasan penipuan",
        "- Rate terkontrol (20-200 event/dtk)",
    ], f_card_body, (51, 65, 85), 8)

    draw_arrow(draw, 285, 625, 285, 672, (30, 58, 95), 4, 13)

    # kartu 1c apache kafka mode kraft
    draw_rounded_box(draw, (80, 675, 490, 920), 14, (255, 255, 255), (59, 130, 246), 3)
    draw.text((102, 694), "Apache Kafka (Mode KRaft)", font=f_card_title, fill=(30, 58, 95))
    draw_multiline(draw, 102, 732, [
        "- Tanpa Zookeeper (hemat RAM)",
        "- 1 Topik Terpadu: ecommerce_events",
        "- Muat 3 jenis data dalam 1 pesan",
        "- Tanpa stream join yang boros RAM",
    ], f_card_body, (51, 65, 85), 8)
    draw_rounded_box(draw, (102, 862, 468, 900), 8, (219, 234, 254))
    draw_centered_text(draw, (102, 862, 468, 900), "mem_limit: 650m | Heap: 256-384m", f_badge, (30, 64, 175))

    # isi kartu pada layer 2 processing (spark streaming & batch optimization)
    draw_rounded_box(draw, (600, 225, 1050, 545), 14, (255, 255, 255), (45, 212, 191), 3)
    draw.text((622, 244), "PySpark Structured Streaming", font=f_card_title, fill=(15, 118, 110))
    draw_multiline(draw, 622, 282, [
        "- Mode local[2] (2 vCPU, tanpa master)",
        "- Skrip: stream_fraud_detector.py",
        "- Watermarking & 1-min windowing",
        "- Deteksi 3 pola fraud & risk scoring",
        "- Analisis kata kunci ulasan negatif",
        "- Hitung rasio klik vs checkout",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (622, 488, 1028, 526), 8, (204, 251, 241))
    draw_centered_text(draw, (622, 488, 1028, 526), "mem_limit: 1200m | Driver: 768m", f_badge, (17, 94, 89))

    # kartu 2b batch & optimasi spark
    draw_rounded_box(draw, (600, 580, 1050, 920), 14, (255, 255, 255), (45, 212, 191), 2)
    draw.text((622, 598), "PySpark Batch & Optimasi", font=f_card_title, fill=(15, 118, 110))
    draw_multiline(draw, 622, 636, [
        "- spark.sql.shuffle.partitions = 4",
        "- partitionBy('event_date','category')",
        "- Skrip: batch_benchmark.py",
        "- Caching/Persist agregasi berulang",
        "- Skrip benchmark performa:",
        "  Sebelum vs Sesudah Optimasi",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (622, 862, 1028, 900), 8, (240, 253, 250), (45, 212, 191), 2)
    draw_centered_text(draw, (622, 862, 1028, 900), "Target Nilai A: Bukti Speedup Nyata", f_badge, (15, 118, 110))

    # isi kartu pada layer 3 storage (mongodb + parquet terpartisi)
    draw_rounded_box(draw, (1160, 225, 1590, 555), 14, (255, 255, 255), (245, 158, 11), 3)
    draw.text((1182, 244), "MongoDB (Hot / Streaming)", font=f_card_title, fill=(146, 64, 14))
    draw_multiline(draw, 1182, 282, [
        "- Fleksibel untuk dokumen JSON",
        "- Koleksi: realtime_metrics",
        "- Koleksi: fraud_alerts",
        "- Koleksi: prescriptive_actions",
        "- Koleksi: benchmark_results",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (1182, 494, 1568, 534), 8, (254, 243, 199))
    draw_centered_text(draw, (1182, 494, 1568, 534), "mem_limit: 512m | Cache: 0.25 GB", f_badge, (146, 64, 14))

    draw_rounded_box(draw, (1160, 590, 1590, 920), 14, (255, 255, 255), (245, 158, 11), 2)
    draw.text((1182, 608), "Parquet Lokal (Cold / Historis)", font=f_card_title, fill=(146, 64, 14))
    draw_multiline(draw, 1182, 646, [
        "- Format kolom terkompresi Snappy",
        "- Skala 1 juta+ baris data historis",
        "- Struktur folder terpartisi:",
        "  event_date=YYYY-MM-DD/",
        "    category=<kategori>/",
        "- Mendukung partition pruning",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (1182, 862, 1568, 900), 8, (255, 251, 235), (245, 158, 11), 2)
    draw_centered_text(draw, (1182, 862, 1568, 900), "Volume Lokal VPS (29 GB Free)", f_badge, (146, 64, 14))

    # isi kartu pada layer 4 visualization (streamlit dashboard + preskriptif)
    draw_rounded_box(draw, (1700, 225, 2120, 565), 14, (255, 255, 255), (99, 102, 241), 3)
    draw.text((1722, 244), "Streamlit Dashboard", font=f_card_title, fill=(67, 56, 202))
    draw_multiline(draw, 1722, 282, [
        "- KPI real-time (event, GMV, fraud)",
        "- Tren transaksi & anomali live",
        "- Tabel detail alert & risk score",
        "- Filter tanggal & kategori Parquet",
        "- Grafik hasil benchmark Spark",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (1722, 504, 2098, 544), 8, (224, 231, 255))
    draw_centered_text(draw, (1722, 504, 2098, 544), "mem_limit: 384m | UI Interaktif", f_badge, (55, 48, 163))

    draw_rounded_box(draw, (1700, 600, 2120, 920), 14, (255, 255, 255), (99, 102, 241), 2)
    draw.text((1722, 618), "Panel Aksi Preskriptif", font=f_card_title, fill=(67, 56, 202))
    draw_multiline(draw, 1722, 656, [
        "- Transaksi Kilat (>= 5/menit):",
        "  Blokir sementara + verifikasi OTP",
        "- Nominal > Rp10 Juta:",
        "  Tahan transaksi, konfirmasi manual",
        "- Ulasan penipuan / Konversi < 10%:",
        "  Audit toko / Voucher diskon",
    ], f_card_body, (51, 65, 85), 10)
    draw_rounded_box(draw, (1722, 862, 2098, 900), 8, (238, 242, 255), (99, 102, 241), 2)
    draw_centered_text(draw, (1722, 862, 2098, 900), "Aksi Nyata untuk Tim Operasional", f_badge, (67, 56, 202))

    # gambar panah penghubung antar layer biar aliran data hulu ke hilir jelas
    # kafka -> spark streaming (pakai jalur siku halus biar ga nabrak kotak)
    draw.line([(490, 795), (545, 795), (545, 385), (596, 385)], fill=(30, 58, 95), width=5)
    draw.polygon([(600, 385), (584, 377), (584, 393)], fill=(30, 58, 95))

    # spark streaming -> mongodb
    draw_arrow(draw, 1050, 385, 1158, 385, (15, 118, 110), 5, 15)
    # spark batch -> parquet
    draw_arrow(draw, 1050, 750, 1158, 750, (15, 118, 110), 5, 15)
    # spark streaming -> parquet juga lewat cabang vertikal
    draw.line([(1098, 385), (1098, 750)], fill=(15, 118, 110), width=4)

    # mongodb -> streamlit
    draw_arrow(draw, 1590, 385, 1698, 385, (146, 64, 14), 5, 15)
    # parquet -> streamlit
    draw.line([(1590, 750), (1645, 750), (1645, 450), (1696, 450)], fill=(146, 64, 14), width=5)
    draw.polygon([(1700, 450), (1684, 442), (1684, 458)], fill=(146, 64, 14))

    # panah internal dari streamlit ke panel preskriptif
    draw_arrow(draw, 1910, 565, 1910, 598, (67, 56, 202), 4, 12)

    # footer catatan arsitektur di bagian paling bawah
    draw_rounded_box(draw, (55, 992, 2145, 1046), 10, (241, 245, 249), (203, 213, 225), 2)
    draw_centered_text(
        draw,
        (55, 992, 2145, 1046),
        "Orkestrasi: Docker Compose (Memori Eksplisit per Layanan)  |  Pola: Hybrid Stream + Batch (Lambda-Lite)  |  Repo: github.com/ZulfahmiFjr/bigdata-ecommerce-fraud",
        f_small,
        (51, 65, 85),
    )

    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "arsitektur-4-layer.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    print(f"diagram tersimpan di: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
