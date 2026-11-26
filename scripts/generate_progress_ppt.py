import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# palet warna sederhana dan bersih biar tampilan slide ga rame
NAVY = RGBColor(30, 58, 95)
TEAL = RGBColor(15, 118, 110)
SLATE_DARK = RGBColor(30, 41, 59)
SLATE_MID = RGBColor(100, 116, 139)
BORDER = RGBColor(203, 213, 225)
BG_WHITE = RGBColor(255, 255, 255)
BG_SOFT = RGBColor(248, 250, 252)
BLUE_SOFT = RGBColor(239, 246, 255)
TEAL_SOFT = RGBColor(240, 253, 250)
AMBER_SOFT = RGBColor(255, 251, 235)
AMBER_DARK = RGBColor(146, 64, 14)
RED_SOFT = RGBColor(254, 242, 242)
RED_DARK = RGBColor(153, 27, 27)

FONT_MAIN = "Calibri"


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text, size=15, bold=False, color=SLATE_DARK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT_MAIN
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_bullets(slide, left, top, width, height, items, size=14.5, color=SLATE_DARK, space_after=8):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.18
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run()
            r1.text = f"• {lead}: "
            r1.font.name = FONT_MAIN
            r1.font.size = Pt(size)
            r1.font.bold = True
            r1.font.color.rgb = NAVY
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_MAIN
            r2.font.size = Pt(size)
            r2.font.color.rgb = color
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.name = FONT_MAIN
            r.font.size = Pt(size)
            r.font.color.rgb = color
    return box


def add_card(slide, left, top, width, height, fill_color=BG_SOFT, border_color=BORDER, radius=True):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color is not None:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    if radius and hasattr(shape, "adjustments") and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.04
    return shape


def add_header_footer(slide, section_label, title_text, slide_num, total_slides=10):
    set_slide_bg(slide, BG_WHITE)
    # garis aksen tipis di atas biar tiap slide konsisten
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()

    add_textbox(slide, 0.7, 0.32, 8.0, 0.3, section_label.upper(), size=11, bold=True, color=TEAL)
    add_textbox(slide, 0.7, 0.60, 11.9, 0.55, title_text, size=25, bold=True, color=NAVY)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.22), Inches(11.93), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.fill.background()

    # footer rapi di bawah
    fline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(7.02), Inches(11.93), Inches(0.01))
    fline.fill.solid()
    fline.fill.fore_color.rgb = BORDER
    fline.line.fill.background()
    add_textbox(slide, 0.7, 7.08, 9.0, 0.3, "Kelompok 12 — Teknologi Big Data  |  Progress Report", size=10.5, color=SLATE_MID)
    add_textbox(slide, 11.5, 7.08, 1.13, 0.3, f"{slide_num} / {total_slides}", size=10.5, bold=True, color=SLATE_MID, align=PP_ALIGN.RIGHT)


def style_cell(cell, text, size=12.5, bold=False, color=SLATE_DARK, fill=None, align=PP_ALIGN.LEFT):
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.12)
    cell.margin_right = Inches(0.12)
    cell.margin_top = Inches(0.07)
    cell.margin_bottom = Inches(0.07)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = FONT_MAIN
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


def build_ppt():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # slide 1 cover
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, BG_WHITE)
    left_band = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.32), Inches(7.5))
    left_band.fill.solid()
    left_band.fill.fore_color.rgb = NAVY
    left_band.line.fill.background()

    add_card(s1, 0.9, 0.95, 4.3, 0.44, fill_color=TEAL_SOFT, border_color=TEAL)
    add_textbox(s1, 1.05, 1.03, 4.0, 0.3, "PROGRESS REPORT — TUGAS AKHIR", size=12, bold=True, color=TEAL)

    add_textbox(s1, 0.9, 1.65, 11.4, 1.5, "Sistem Deteksi Anomali (Fraud) &\nAnalitik Aktivitas E-Commerce Real-Time", size=34, bold=True, color=NAVY)
    add_textbox(s1, 0.9, 3.25, 10.6, 0.5, "Mata Kuliah Teknologi Big Data  |  Arsitektur Streaming & Batch Hemat Resource", size=16.5, color=SLATE_MID)

    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(3.95), Inches(11.4), Inches(0.02))
    div.fill.solid()
    div.fill.fore_color.rgb = BORDER
    div.line.fill.background()

    # kartu identitas kelompok 12 di bawah biar jelas dan rapi
    add_card(s1, 0.9, 4.25, 7.3, 2.35, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(s1, 1.15, 4.40, 6.8, 0.35, "Kelompok 12", size=16, bold=True, color=NAVY)
    members = [
        "Muhamad Rifqi Fadil Itsnain  (2406355306)",
        "Muhammad Zaki Al Khairi  (2406432375)",
        "Muhammad Hashif Jade  (2406396786)",
        "Zulfahmi Fajri  (2406345425)",
    ]
    add_bullets(s1, 1.15, 4.82, 6.8, 1.65, members, size=14, color=SLATE_DARK, space_after=6)

    add_card(s1, 8.45, 4.25, 3.85, 2.35, fill_color=BLUE_SOFT, border_color=BORDER)
    add_textbox(s1, 8.70, 4.40, 3.4, 0.35, "Informasi Proyek", size=15.5, bold=True, color=NAVY)
    add_bullets(s1, 8.70, 4.85, 3.4, 1.6, [
        "Repository: ZulfahmiFjr/bigdata-ecommerce-fraud",
        "Target: Implementasi end-to-end di VPS Ubuntu",
        "November 2026",
    ], size=13, color=SLATE_DARK, space_after=8)

    # slide 2 latar belakang dan masalah
    s2 = prs.slides.add_slide(blank)
    add_header_footer(s2, "01. Latar Belakang", "Mengapa Deteksi Fraud E-Commerce Harus Real-Time?", 2)

    add_card(s2, 0.7, 1.55, 5.75, 5.1, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(s2, 0.95, 1.78, 5.2, 0.4, "Permasalahan di Lapangan", size=18, bold=True, color=NAVY)
    add_bullets(s2, 0.95, 2.30, 5.25, 4.1, [
        ("Aktivitas Sangat Padat", "Platform e-commerce menerima jutaan event klik, keranjang, transaksi, dan ulasan setiap hari."),
        ("Pola Serangan Cepat", "Pelaku memanfaatkan celah kecepatan untuk card testing puluhan kali per menit atau pengambilalihan akun."),
        ("Kelemahan Rekap Harian", "Jika deteksi baru dijalankan lewat laporan malam (batch), dana transaksi sudah telanjur berpindah."),
        ("Minim Tindak Lanjut Otomatis", "Banyak sistem berhenti di grafik statistik tanpa memberi rekomendasi aksi konkret bagi tim operasional."),
    ], size=14, space_after=12)

    add_card(s2, 6.85, 1.55, 5.78, 5.1, fill_color=TEAL_SOFT, border_color=TEAL)
    add_textbox(s2, 7.10, 1.78, 5.3, 0.4, "Tujuan Solusi yang Kami Bangun", size=18, bold=True, color=TEAL)
    add_bullets(s2, 7.10, 2.30, 5.3, 4.1, [
        ("Deteksi Berlatensi Rendah", "Memproses aliran event transaksi, clickstream, dan ulasan secara langsung lewat Kafka dan Spark Streaming."),
        ("Penyimpanan Historis Efisien", "Menyimpan data historis terpartisi dalam format Parquet agar analisis jutaan baris tetap cepat."),
        ("Optimasi Performa Nyata", "Menguji dan membandingkan waktu eksekusi Spark sebelum dan sesudah optimasi partisi serta caching."),
        ("Insight Preskriptif", "Menyajikan rekomendasi aksi langsung di dashboard Streamlit, seperti blokir sementara akun atau voucher diskon kategori."),
    ], size=14, space_after=12)

    # slide 3 justifikasi big data 3v+
    s3 = prs.slides.add_slide(blank)
    add_header_footer(s3, "02. Justifikasi Big Data", "Analisis Karakteristik 3V+ Secara Terukur", 3)

    v_cards = [
        ("VOLUME", "Skala Jutaan Baris", BLUE_SOFT, NAVY, [
            "E-commerce menengah dengan 50.000 pengguna aktif x 40 event/hari menghasilkan ~2 juta log/hari (60 juta baris/bulan).",
            "Pada implementasi VPS, kami menyiapkan data historis simulasi 1 juta+ baris Parquet ditambah stream berkelanjutan.",
        ]),
        ("VELOCITY", "Aliran Event Per Detik", TEAL_SOFT, TEAL, [
            "Saat jam sibuk atau promo, event transaksi dan klik masuk terus-menerus dalam hitungan detik.",
            "Python Producer mengalirkan stream ke Apache Kafka (20–200 event/detik) untuk diproses jendela waktu 1 menit oleh Spark.",
        ]),
        ("VARIETY", "3 Jenis Data Berbeda", AMBER_SOFT, AMBER_DARK, [
            "Terstruktur: angka transaksi (nominal, jumlah, metode bayar, timestamp).",
            "Semi-terstruktur: log clickstream dalam format JSON bersarang.",
            "Tidak terstruktur: teks bebas ulasan pembeli untuk deteksi bot dan keluhan penipuan.",
        ]),
    ]

    for i, (title, sub, bg, accent, pts) in enumerate(v_cards):
        x = 0.7 + i * 4.08
        add_card(s3, x, 1.55, 3.78, 4.15, fill_color=bg, border_color=BORDER)
        add_textbox(s3, x + 0.22, 1.75, 3.3, 0.35, title, size=18, bold=True, color=accent)
        add_textbox(s3, x + 0.22, 2.12, 3.3, 0.32, sub, size=13, bold=True, color=SLATE_MID)
        add_bullets(s3, x + 0.22, 2.55, 3.34, 3.0, pts, size=13.5, space_after=10)

    # kotak tambahan veracity dan value di bagian bawah biar 3V+ lengkap
    add_card(s3, 0.7, 5.92, 11.93, 0.88, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(
        s3, 0.92, 6.04, 11.5, 0.65,
        "Unsur Tambahan (+)  —  Veracity: validasi skema dan watermarking di Spark untuk menangani data telat/duplikat.  |  Value: data tidak hanya ditampilkan sebagai grafik, tetapi diubah menjadi rekomendasi aksi pencegahan fraud dan promosi.",
        size=13.2, color=SLATE_DARK
    )

    # slide 4 perbandingan dgan RDBMS tradisional
    s4 = prs.slides.add_slide(blank)
    add_header_footer(s4, "02. Justifikasi Big Data", "Mengapa Tidak Efisien Diselesaikan dengan RDBMS Tradisional?", 4)

    tbl_shape = s4.shapes.add_table(5, 3, Inches(0.7), Inches(1.55), Inches(11.93), Inches(4.55))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.43)
    tbl.columns[1].width = Inches(4.75)
    tbl.columns[2].width = Inches(4.75)

    headers = ["Aspek Teknis", "Keterbatasan RDBMS Tradisional", "Solusi Big Data Kami"]
    for c, h in enumerate(headers):
        style_cell(tbl.cell(0, c), h, size=13.5, bold=True, color=BG_WHITE, fill=NAVY)

    rows = [
        ("Kecepatan Tulis\n(Velocity)", "Tulis langsung memicu row/table lock dan overhead indeks B-Tree saat trafik melonjak.", "Apache Kafka menjadi buffer terdistribusi sehingga ingest terpisah dari beban pemrosesan."),
        ("Format Data Beragam\n(Variety)", "Skema tabel kaku; menyimpan JSON clickstream dan teks ulasan membuat tabel boros atau mahal saat JOIN.", "MongoDB menyimpan dokumen JSON secara fleksibel, sedangkan Parquet menyimpan kolom analitik terkompresi."),
        ("Deteksi Real-Time\n(Low Latency)", "Polling query agregasi tiap detik langsung ke database operasional mengganggu transaksi pelanggan.", "Spark Structured Streaming menghitung windowing 1 menit secara inkremental dari aliran Kafka."),
        ("Analisis Historis\n(Volume & Scale)", "Full table scan jutaan baris lambat; skalabilitas bertumpu pada scale-up mesin tunggal.", "Parquet terpartisi event_date & category memangkas bacaan disk (partition pruning) dan siap scale-out."),
    ]
    for r_idx, (a, b, c_txt) in enumerate(rows, start=1):
        bg = BG_WHITE if r_idx % 2 == 1 else BG_SOFT
        style_cell(tbl.cell(r_idx, 0), a, size=13, bold=True, color=NAVY, fill=bg)
        style_cell(tbl.cell(r_idx, 1), b, size=12.8, color=SLATE_DARK, fill=bg)
        style_cell(tbl.cell(r_idx, 2), c_txt, size=12.8, color=SLATE_DARK, fill=TEAL_SOFT if r_idx % 2 == 1 else bg)

    add_textbox(
        s4, 0.7, 6.28, 11.93, 0.55,
        "Kesimpulan: Kami menggabungkan Stream Processing (deteksi cepat saat kejadian berlangsung) dan Batch Processing (analisis historis & benchmark optimasi).",
        size=13.5, bold=True, color=TEAL
    )

    # slide 5 karakteristik data dan pola fraud
    s5 = prs.slides.add_slide(blank)
    add_header_footer(s5, "03. Data & Skenario Kasus", "Tiga Jenis Data & Empat Pola Anomali Fraud", 5)

    add_card(s5, 0.7, 1.55, 5.65, 5.15, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(s5, 0.95, 1.76, 5.1, 0.38, "Sumber & Format Data (Simulasi Terukur)", size=17, bold=True, color=NAVY)
    add_bullets(s5, 0.95, 2.25, 5.15, 4.25, [
        ("Topik ecommerce.transactions (Terstruktur)", "transaction_id, user_id, merchant_id, category, amount_idr, quantity, payment_method, city, device_id, event_time."),
        ("Topik ecommerce.clickstream (Semi-Terstruktur)", "JSON bersarang berisi session_id, action (view, add_to_cart, checkout), product_id, dan objek metadata (browser, os, ip, referrer)."),
        ("Topik ecommerce.reviews (Tidak Terstruktur)", "Teks bebas ulasan pembeli beserta rating dan timestamp untuk mendeteksi spam bot serta keluhan penipuan."),
    ], size=13.5, space_after=13)

    add_card(s5, 6.65, 1.55, 5.98, 5.15, fill_color=RED_SOFT, border_color=BORDER)
    add_textbox(s5, 6.90, 1.76, 5.4, 0.38, "Empat Pola Anomali Fraud yang Dideteksi", size=17, bold=True, color=RED_DARK)
    add_bullets(s5, 6.90, 2.25, 5.5, 4.25, [
        ("1. Velocity Burst (Card Testing)", "Satu akun atau IP melakukan >= 5 transaksi beruntun dalam jendela waktu 1 menit."),
        ("2. High-Value Transaction Spike", "Nominal transaksi melonjak drastis di atas kewajaran kategori atau histori akun baru."),
        ("3. Geo / Device Hopping", "Satu akun berpindah kota atau perangkat berbeda dalam rentang waktu yang tidak masuk akal."),
        ("4. Suspicious Review & Bot Pattern", "Lonjakan ulasan berulang dengan teks identik atau kata kunci penipuan (scam, palsu, barang kosong) pada merchant tertentu."),
    ], size=13.5, space_after=12)

    # slide 6 diagram arsitektur 4 layer
    s6 = prs.slides.add_slide(blank)
    add_header_footer(s6, "04. Arsitektur Solusi", "Rancangan Arsitektur 4 Layer (Ingestion -> Visualization)", 6)

    diag_path = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "arsitektur-4-layer.png")
    # atur tinggi gambar biar pas di atas footer dan posisinya tetap center
    s6.shapes.add_picture(diag_path, Inches(1.08), Inches(1.38), height=Inches(5.48))

    # slide 7 tech stack, resource VPS, dan optimasi spark
    s7 = prs.slides.add_slide(blank)
    add_header_footer(s7, "05. Tech Stack & Optimasi", "Alokasi Resource VPS & Strategi Optimasi Spark", 7)

    # tabel alokasi resource di kiri
    add_textbox(s7, 0.7, 1.45, 6.8, 0.35, "Konfigurasi Hemat RAM (VPS 2 vCPU, 4 GB RAM, Target <= 2,6 GB)", size=14.5, bold=True, color=NAVY)
    t7_shape = s7.shapes.add_table(5, 3, Inches(0.7), Inches(1.88), Inches(6.95), Inches(4.75))
    t7 = t7_shape.table
    t7.columns[0].width = Inches(1.85)
    t7.columns[1].width = Inches(3.65)
    t7.columns[2].width = Inches(1.45)
    for c, h in enumerate(["Komponen", "Konfigurasi Kunci", "mem_limit"]):
        style_cell(t7.cell(0, c), h, size=12.5, bold=True, color=BG_WHITE, fill=NAVY)

    r7 = [
        ("Kafka KRaft", "Mode tanpa Zookeeper, Heap 256–384m, 3 topik event.", "650m"),
        ("PySpark\nlocal[2]", "Structured Streaming + Batch dalam 1 container, Driver 768m.", "1200m"),
        ("MongoDB +\nParquet", "MongoDB cache 0.25 GB (hot data) + Parquet Snappy di disk lokal.", "512m"),
        ("Streamlit", "Dashboard interaktif membaca MongoDB & Parquet terfilter.", "384m"),
    ]
    for i, (k, v, m) in enumerate(r7, start=1):
        bg = BG_WHITE if i % 2 == 1 else BG_SOFT
        style_cell(t7.cell(i, 0), k, size=12.2, bold=True, color=NAVY, fill=bg)
        style_cell(t7.cell(i, 1), v, size=12, color=SLATE_DARK, fill=bg)
        style_cell(t7.cell(i, 2), m, size=12.2, bold=True, color=TEAL, fill=bg, align=PP_ALIGN.CENTER)

    # kartu strategi optimasi spark di kanan
    add_card(s7, 7.9, 1.48, 4.73, 5.15, fill_color=TEAL_SOFT, border_color=TEAL)
    add_textbox(s7, 8.15, 1.68, 4.25, 0.38, "Optimasi Spark (Target Nilai A)", size=16.5, bold=True, color=TEAL)
    add_bullets(s7, 8.15, 2.18, 4.25, 4.25, [
        ("Shuffle Partitions = 4", "Menurunkan default 200 menjadi 4 agar cocok dengan 2 vCPU dan mengurangi overhead task."),
        ("Partitioned Parquet", "Menggunakan partitionBy('event_date', 'category') supaya query hanya membaca partisi relevan."),
        ("Caching / Persist", "Menyimpan sementara DataFrame yang dipakai berulang pada agregasi batch."),
        ("Benchmark Terukur", "Skrip khusus membandingkan waktu eksekusi sebelum vs sesudah optimasi sebagai bukti nyata."),
    ], size=13.2, space_after=11)

    # slide 8 rancangan dashboard dan insight preskriptif
    s8 = prs.slides.add_slide(blank)
    add_header_footer(s8, "06. Visualisasi & Insight", "Dashboard Interaktif & Panel Aksi Preskriptif", 8)

    add_card(s8, 0.7, 1.55, 5.3, 5.1, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(s8, 0.95, 1.78, 4.8, 0.38, "Monitoring Deskriptif (Real-Time)", size=17, bold=True, color=NAVY)
    add_bullets(s8, 0.95, 2.28, 4.8, 4.1, [
        "Kartu KPI langsung: total event masuk, GMV transaksi, jumlah alert fraud, dan rasio anomali.",
        "Grafik tren trafik transaksi normal vs terindikasi fraud per menit.",
        "Tabel daftar alert prioritas lengkap dengan risk score (0–100) dan alasan deteksi.",
        "Tab hasil benchmark Spark (durasi eksekusi & ukuran disk sebelum vs sesudah optimasi).",
    ], size=13.8, space_after=12)

    add_textbox(s8, 6.3, 1.52, 6.3, 0.38, "Panel Rekomendasi Aksi Preskriptif (Bukan Sekadar Grafik)", size=16.5, bold=True, color=TEAL)
    actions = [
        ("1. Keamanan Akun (Risk Score >= 80 / Velocity Burst)", "Rekomendasi: Blokir sementara akun terindikasi fraud dan paksa verifikasi OTP/KYC sebelum transaksi berikutnya.", RED_SOFT, RED_DARK),
        ("2. Keamanan Merchant (Lonjakan Ulasan Penipuan)", "Rekomendasi: Tandai toko untuk audit manual dan tahan pencairan dana sementara hingga verifikasi selesai.", AMBER_SOFT, AMBER_DARK),
        ("3. Optimasi Konversi (Klik Tinggi, Checkout < 10%)", "Rekomendasi: Terbitkan voucher diskon 10–15% atau promo gratis ongkir khusus pada kategori produk tersebut.", BLUE_SOFT, NAVY),
    ]
    for idx, (atitle, adesc, abg, aclr) in enumerate(actions):
        y = 2.02 + idx * 1.58
        add_card(s8, 6.3, y, 6.33, 1.40, fill_color=abg, border_color=BORDER)
        add_textbox(s8, 6.52, y + 0.14, 5.9, 0.34, atitle, size=13.8, bold=True, color=aclr)
        add_textbox(s8, 6.52, y + 0.52, 5.9, 0.78, adesc, size=13.0, color=SLATE_DARK)

    # slide 9 status progress, roadmap, dan pembagian peran
    s9 = prs.slides.add_slide(blank)
    add_header_footer(s9, "07. Rencana Kerja", "Status Progress, Tahapan Berikutnya & Pembagian Peran", 9)

    # 3 tahap di atas
    stages = [
        ("Tahap 1 (Selesai — 27–29 Nov)", TEAL_SOFT, TEAL, [
            "Audit resource VPS (CPU, RAM, disk, swap)",
            "Setup repo GitHub & struktur modular",
            "Justifikasi 3V+ & diagram 4 layer",
            "PPT & video Progress Report",
        ]),
        ("Tahap 2 (Implementasi VPS)", BLUE_SOFT, NAVY, [
            "Tambah swap aman + pasang Docker",
            "Bangun Producer, Kafka KRaft, PySpark",
            "Setup MongoDB, Parquet & Streamlit",
            "Uji end-to-end & benchmark Spark",
        ]),
        ("Tahap 3 (Final EMAS)", BG_SOFT, SLATE_DARK, [
            "Susun Laporan PDF (Abstrak, Bab 1–5)",
            "Lengkapi bukti log & screenshot live",
            "Susun PPT Final + video demo YouTube",
            "Arsip .zip siap unggah ke EMAS",
        ]),
    ]
    for i, (stitle, sbg, sclr, sitems) in enumerate(stages):
        x = 0.7 + i * 4.08
        add_card(s9, x, 1.48, 3.78, 2.65, fill_color=sbg, border_color=BORDER)
        add_textbox(s9, x + 0.2, 1.62, 3.4, 0.34, stitle, size=14, bold=True, color=sclr)
        add_bullets(s9, x + 0.2, 2.02, 3.4, 2.0, sitems, size=12.5, space_after=6)

    # tabel pembagian peran di bawah
    add_textbox(s9, 0.7, 4.30, 6.0, 0.32, "Pembagian Peran Kelompok 12", size=14.5, bold=True, color=NAVY)
    t9_shape = s9.shapes.add_table(5, 3, Inches(0.7), Inches(4.68), Inches(11.93), Inches(2.15))
    t9 = t9_shape.table
    t9.columns[0].width = Inches(3.4)
    t9.columns[1].width = Inches(1.8)
    t9.columns[2].width = Inches(6.73)
    for c, h in enumerate(["Nama Anggota", "NPM", "Fokus Tanggung Jawab"]):
        style_cell(t9.cell(0, c), h, size=12, bold=True, color=BG_WHITE, fill=NAVY)
    roles = [
        ("Zulfahmi Fajri", "2406345425", "Infrastruktur VPS, Docker Compose, arsitektur sistem, integrasi repo & pipeline"),
        ("Muhamad Rifqi Fadil Itsnain", "2406355306", "Layer Ingestion: Python Producer, simulasi transaksi/fraud/ulasan, Apache Kafka KRaft"),
        ("Muhammad Zaki Al Khairi", "2406432375", "Layer Processing: PySpark Structured Streaming, partisi Parquet, benchmark optimasi"),
        ("Muhammad Hashif Jade", "2406396786", "Layer Storage & Visualization: MongoDB, Parquet, Streamlit Dashboard & aksi preskriptif"),
    ]
    for i, (nm, npm, role) in enumerate(roles, start=1):
        bg = BG_WHITE if i % 2 == 1 else BG_SOFT
        style_cell(t9.cell(i, 0), nm, size=11.8, bold=True, color=SLATE_DARK, fill=bg)
        style_cell(t9.cell(i, 1), npm, size=11.8, color=SLATE_MID, fill=bg)
        style_cell(t9.cell(i, 2), role, size=11.8, color=SLATE_DARK, fill=bg)

    # slide 10 penutup dan slot link youtube
    s10 = prs.slides.add_slide(blank)
    set_slide_bg(s10, BG_WHITE)
    band10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    band10.fill.solid()
    band10.fill.fore_color.rgb = NAVY
    band10.line.fill.background()

    add_textbox(s10, 0.9, 1.35, 11.5, 0.7, "Terima Kasih", size=38, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_textbox(s10, 0.9, 2.15, 11.5, 0.5, "Kelompok 12 — Sistem Deteksi Anomali (Fraud) & Analitik Aktivitas E-Commerce Real-Time", size=16.5, color=SLATE_MID, align=PP_ALIGN.CENTER)

    # kotak slot link youtube sesuai panduan tugas akhir
    add_card(s10, 2.15, 3.10, 9.03, 1.85, fill_color=BLUE_SOFT, border_color=NAVY)
    add_textbox(s10, 2.4, 3.32, 8.5, 0.38, "LINK VIDEO PRESENTASI YOUTUBE (PROGRESS REPORT)", size=13.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_textbox(s10, 2.4, 3.82, 8.5, 0.45, "[ Tempelkan Link YouTube Kelompok 12 di Sini Sebelum Upload ]", size=17, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_textbox(s10, 2.4, 4.38, 8.5, 0.35, "Contoh format: https://youtu.be/xxxxxxxxxxx", size=12.5, color=SLATE_MID, align=PP_ALIGN.CENTER)

    add_card(s10, 2.15, 5.25, 9.03, 0.95, fill_color=BG_SOFT, border_color=BORDER)
    add_textbox(s10, 2.4, 5.42, 8.5, 0.3, "Repository Proyek GitHub", size=12.5, bold=True, color=SLATE_MID, align=PP_ALIGN.CENTER)
    add_textbox(s10, 2.4, 5.72, 8.5, 0.35, "https://github.com/ZulfahmiFjr/bigdata-ecommerce-fraud", size=14.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

    add_textbox(s10, 0.7, 7.05, 11.93, 0.3, "Kelompok 12 — Teknologi Big Data  |  10 / 10", size=10.5, color=SLATE_MID, align=PP_ALIGN.CENTER)

    out_path = os.path.join(os.path.dirname(__file__), "..", "deliverables", "progress-report", "Kelompok12_ProgressReport_BigData.pptx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prs.save(out_path)
    print(f"PPT progress report tersimpan di: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    build_ppt()
