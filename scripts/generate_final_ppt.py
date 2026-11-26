import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# palet warna tenang dan elegan mengikuti gaya presentasi proyek akhir
DARK_GREEN = RGBColor(15, 46, 34)       # #0F2E22 cover & penutup
ACCENT_GREEN = RGBColor(21, 128, 61)    # #15803D aksen utama
MINT_LIGHT = RGBColor(126, 185, 148)    # #7EB994 aksen di latar gelap
BG_WHITE = RGBColor(255, 255, 255)      # #FFFFFF
BG_MINT = RGBColor(243, 247, 245)       # #F3F7F5 selang-seling lembut
CARD_BG = RGBColor(255, 255, 255)
CARD_ALT = RGBColor(236, 245, 240)
TEXT_DARK = RGBColor(30, 41, 59)        # #1E293B
TEXT_MUTED = RGBColor(71, 85, 105)      # #475569
TEXT_SOFT_LIGHT = RGBColor(203, 213, 225)
BORDER = RGBColor(203, 213, 225)
LINE_DARK = RGBColor(45, 86, 68)
RED_ACCENT = RGBColor(185, 28, 28)
AMBER_ACCENT = RGBColor(180, 83, 9)
BLUE_ACCENT = RGBColor(29, 78, 216)

FONT = "Calibri"
TOTAL_SLIDES = 14


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, x, y, w, h, text, size=14, bold=False, color=TEXT_DARK, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.03)
    tf.margin_right = Inches(0.03)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tb


def add_bullets(slide, x, y, w, h, items, size=13, color=TEXT_DARK, space_after=7, lead_color=DARK_GREEN):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.03)
    tf.margin_right = Inches(0.03)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.16
        if isinstance(item, tuple):
            lead, rest = item
            r1 = p.add_run()
            r1.text = f"• {lead}: "
            r1.font.name = FONT
            r1.font.size = Pt(size)
            r1.font.bold = True
            r1.font.color.rgb = lead_color
            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT
            r2.font.size = Pt(size)
            r2.font.color.rgb = color
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.name = FONT
            r.font.size = Pt(size)
            r.font.color.rgb = color
    return tb


def add_box(slide, x, y, w, h, fill=CARD_BG, border=BORDER, rounded=True, border_pt=1):
    st = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(st, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if border is not None:
        sh.line.color.rgb = border
        sh.line.width = Pt(border_pt)
    else:
        sh.line.fill.background()
    if rounded and hasattr(sh, "adjustments") and len(sh.adjustments) > 0:
        sh.adjustments[0] = 0.05
    return sh


def add_circle_num(slide, cx, cy, dia, num_text, fill=ACCENT_GREEN):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - dia / 2), Inches(cy - dia / 2), Inches(dia), Inches(dia))
    sh.shadow.inherit = False
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    tf = sh.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(num_text)
    r.font.name = FONT
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BG_WHITE
    return sh


def add_header(slide, eyebrow, title, subtitle, slide_num, bg_color=BG_WHITE):
    set_bg(slide, bg_color)
    add_text(slide, 0.65, 0.36, 11.5, 0.28, eyebrow.upper(), size=11, bold=True, color=ACCENT_GREEN)
    # judul 1 baris lega biar ga pernah nabrak subjudul pas dirender libreoffice atau powerpoint
    add_text(slide, 0.65, 0.64, 12.0, 0.52, title, size=22.5, bold=True, color=TEXT_DARK)
    add_text(slide, 0.65, 1.24, 12.0, 0.36, subtitle, size=13.5, color=TEXT_MUTED)
    add_text(
        slide,
        6.5,
        7.05,
        6.18,
        0.28,
        f"Kelompok 12 · Proyek Akhir Teknologi Big Data 2026 · {slide_num}",
        size=10,
        color=TEXT_MUTED,
        align=PP_ALIGN.RIGHT,
    )


def add_picture_fit(slide, rel_path, box_x, box_y, box_w, box_h, border_color=BORDER):
    # masukin gambar proporsional di dalam kotak target biar ga gepeng dan ga keluar batas
    from PIL import Image
    full_path = os.path.join(BASE_DIR, rel_path)
    with Image.open(full_path) as im:
        iw, ih = im.size
    ratio = iw / ih
    box_ratio = box_w / box_h
    if ratio > box_ratio:
        w = box_w
        h = w / ratio
    else:
        h = box_h
        w = h * ratio
    x = box_x + (box_w - w) / 2
    y = box_y + (box_h - h) / 2
    if border_color is not None:
        frame = add_box(slide, x - 0.03, y - 0.03, w + 0.06, h + 0.06, fill=BG_WHITE, border=border_color, rounded=False, border_pt=1)
    slide.shapes.add_picture(full_path, Inches(x), Inches(y), width=Inches(w), height=Inches(h))
    return x, y, w, h


def style_cell(cell, text, size=12, bold=False, color=TEXT_DARK, fill=None, align=PP_ALIGN.LEFT):
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.11)
    cell.margin_right = Inches(0.11)
    cell.margin_top = Inches(0.06)
    cell.margin_bottom = Inches(0.06)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


def build_ppt():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ==========================================================
    # SLIDE 1: COVER (LATAR GELAP HIJAU TUA ELEGAN ALA REFERENSI)
    # ==========================================================
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, DARK_GREEN)
    # garis grid tipis atas dan bawah
    add_box(s1, 0, 1.05, 13.333, 0.015, fill=LINE_DARK, border=None, rounded=False)
    add_box(s1, 9.55, 0, 0.015, 1.05, fill=LINE_DARK, border=None, rounded=False)
    add_box(s1, 0, 5.78, 13.333, 0.015, fill=LINE_DARK, border=None, rounded=False)
    add_box(s1, 9.55, 5.78, 0.015, 1.72, fill=LINE_DARK, border=None, rounded=False)

    add_text(s1, 0.65, 0.42, 8.6, 0.35, "PROYEK AKHIR TEKNOLOGI BIG DATA 2026", size=12, bold=True, color=MINT_LIGHT)
    add_text(s1, 9.8, 0.42, 2.9, 0.35, "KELOMPOK 12", size=12.5, bold=True, color=BG_WHITE, align=PP_ALIGN.RIGHT)

    add_text(s1, 0.65, 1.62, 11.8, 2.1, "Sistem Deteksi Fraud &\nAnalitik E-Commerce\nReal-Time", size=42, bold=True, color=BG_WHITE)
    add_text(
        s1, 0.65, 4.45, 11.4, 0.85,
        "Pipeline Streaming dan Batch Hemat Resource pada VPS Ubuntu dengan\nApache Kafka, Apache Spark, MongoDB, Apache Parquet, dan Streamlit",
        size=16, color=TEXT_SOFT_LIGHT
    )

    add_text(
        s1, 0.65, 6.02, 8.7, 1.0,
        "Muhamad Rifqi Fadil Itsnain (2406355306)  ·  Muhammad Zaki Al Khairi (2406432375)\nMuhammad Hashif Jade (2406396786)  ·  Zulfahmi Fajri (2406345425)",
        size=12.5, color=TEXT_SOFT_LIGHT
    )
    # 4 titik aksen minimalis kanan bawah seperti referensi
    for idx, clr in enumerate([ACCENT_GREEN, BLUE_ACCENT, MINT_LIGHT, TEXT_SOFT_LIGHT]):
        dot = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.25 + idx * 0.56), Inches(6.28), Inches(0.28), Inches(0.28))
        dot.fill.solid()
        dot.fill.fore_color.rgb = clr
        dot.line.fill.background()
    add_text(s1, 9.7, 6.95, 3.0, 0.3, "Kelompok 12 · Big Data 2026 · 1", size=10, color=TEXT_SOFT_LIGHT, align=PP_ALIGN.RIGHT)

    # ==========================================================
    # SLIDE 2: MULAI DARI NOL — APA ITU BIG DATA (3V+)
    # ==========================================================
    s2 = prs.slides.add_slide(blank)
    add_header(
        s2,
        "Dasar Big Data · Mulai dari Nol",
        "Kenapa kasus e-commerce ini termasuk Big Data?",
        "Big Data bukan cuma soal data besar, tapi gabungan ukuran, kecepatan masuk, dan bentuk data yang beragam",
        2,
        BG_WHITE,
    )
    # garis penghubung 3 lingkaran
    add_box(s2, 2.4, 2.30, 8.5, 0.03, fill=MINT_LIGHT, border=None, rounded=False)
    v_items = [
        ("1", "Volume (Ukuran Besar)", "Contohnya 50 ribu pembeli klik 40 kali per hari sudah jadi 2 juta baris log per hari, atau 60 juta baris per bulan.", "Di proyek ini kami uji 1 juta baris data historis + stream aktif."),
        ("2", "Velocity (Masuk Cepat)", "Saat promo atau jam sibuk, transaksi dan klik masuk setiap detik sehingga deteksi fraud tidak bisa menunggu rekap malam.", "Di proyek ini data mengalir per detik lewat Kafka dan dicek tiap 10 detik."),
        ("3", "Variety (Format Beragam)", "Datanya campur: angka transaksi (tabel), log klik JSON (semi-terstruktur), dan teks bebas ulasan pembeli.", "Di proyek ini 3 jenis data tersebut diproses bersama dalam 1 pipeline."),
    ]
    for i, (num, vtitle, desc, proof) in enumerate(v_items):
        cx = 2.4 + i * 4.25
        add_circle_num(s2, cx, 2.31, 0.56, num, fill=ACCENT_GREEN)
        add_text(s2, cx - 1.85, 2.75, 3.7, 0.38, vtitle, size=17, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
        add_box(s2, cx - 1.85, 3.22, 3.7, 2.35, fill=BG_MINT, border=BORDER)
        add_text(s2, cx - 1.65, 3.38, 3.3, 1.25, desc, size=13, color=TEXT_DARK)
        add_text(s2, cx - 1.65, 4.72, 3.3, 0.72, proof, size=12, bold=True, color=ACCENT_GREEN)

    add_box(s2, 0.65, 5.88, 12.03, 0.88, fill=CARD_ALT, border=MINT_LIGHT)
    add_text(
        s2, 0.9, 6.03, 11.5, 0.6,
        "Tambahan (+):  Veracity = kami validasi skema data agar event rusak tersaring.   |   Value = data langsung diubah menjadi saran tindakan nyata, bukan sekadar grafik angka.",
        size=13, color=TEXT_DARK
    )

    # ==========================================================
    # SLIDE 3: MASALAH NYATA & KENAPA DATABASE BIASA KURANG COCOK
    # ==========================================================
    s3 = prs.slides.add_slide(blank)
    add_header(
        s3,
        "Latar Belakang Masalah",
        "Masalah di toko online & batas database biasa (RDBMS)",
        "Kenapa tidak cukup memakai satu MySQL atau PostgreSQL saja untuk kasus ini?",
        3,
        BG_MINT,
    )
    add_box(s3, 0.65, 1.82, 5.8, 4.9, fill=BG_WHITE, border=BORDER)
    add_text(s3, 0.92, 2.04, 5.2, 0.38, "Masalah yang Ingin Kami Selesaikan", size=17, bold=True, color=DARK_GREEN)
    add_bullets(s3, 0.92, 2.52, 5.25, 3.95, [
        ("Transaksi Kilat (Card Testing)", "Pelaku mencoba banyak transaksi beruntun dalam hitungan detik untuk menguji kartu curian."),
        ("Nominal Melonjak", "Tiba-tiba muncul transaksi sangat besar di atas Rp10 juta yang rawan penipuan."),
        ("Ulasan Penipuan", "Pembeli mengeluhkan barang palsu atau paket kosong di kolom ulasan teks."),
        ("Rugi Peluang Penjualan", "Banyak pembeli klik produk di kategori tertentu tapi jarang lanjut sampai checkout."),
    ], size=13.2, space_after=11)

    add_box(s3, 6.8, 1.82, 5.88, 4.9, fill=BG_WHITE, border=BORDER)
    add_text(s3, 7.08, 2.04, 5.3, 0.38, "Kenapa RDBMS Biasa Kewalahan?", size=17, bold=True, color=RED_ACCENT)
    add_bullets(s3, 7.08, 2.52, 5.35, 3.95, [
        ("Macet saat Trafik Ramai", "Menulis ribuan event klik dan pembayaran langsung ke satu tabel memicu antrean lock."),
        ("Skema Kaku", "Sulit menyimpan objek JSON clickstream yang berubah-ubah bersama teks ulasan bebas."),
        ("Query Rekap Mengganggu Transaksi", "Membaca jutaan baris log lama sekaligus di database utama bikin aplikasi melambat."),
        ("Solusi Kami", "Pisahkan peran: penampung aliran (Kafka), pengolah (Spark), gudang cepat + arsip (MongoDB + Parquet), dan layar (Streamlit)."),
    ], size=13.2, space_after=11, lead_color=RED_ACCENT)

    # ==========================================================
    # SLIDE 4: KENALAN DARI NOL — FUNGSI TIAP TOOLS
    # ==========================================================
    s4 = prs.slides.add_slide(blank)
    add_header(
        s4,
        "Pengenalan Tools · Bahasa Sederhana",
        "Untuk apa masing-masing tool di proyek ini?",
        "Penjelasan singkat peran tiap teknologi agar mudah dipahami bahkan dari nol",
        4,
        BG_WHITE,
    )
    tools_info = [
        ("1. Python Producer", "Simulasi Pembeli", "Skrip Python yang membangkitkan aktivitas belanja normal, 3 pola fraud, dan ulasan pembeli secara terus-menerus."),
        ("2. Apache Kafka (KRaft)", "Pos Antrean Data Cepat", "Menampung aliran event di topik ecommerce_events agar data masuk tidak hilang. Mode KRaft tanpa Zookeeper bikin RAM hemat."),
        ("3. Apache Spark (PySpark)", "Otak Pengolah Data", "Membaca stream Kafka untuk deteksi fraud real-time, sekaligus mengolah 1 juta baris historis dengan optimasi partisi & cache."),
        ("4. MongoDB", "Gudang JSON Live", "Database dokumen fleksibel untuk menyimpan metrik real-time, daftar alert fraud, dan rekomendasi aksi yang dibaca dashboard."),
        ("5. Apache Parquet", "Arsip Hemat Disk", "Format penyimpanan per kolom berkompresi Snappy, dibagi per folder tanggal & kategori agar query jauh lebih cepat."),
        ("6. Streamlit & Docker", "Dashboard & Wadah", "Streamlit menampilkan grafik + tombol filter berbasis Python, sedangkan Docker Compose menyalakan semua tool dengan 1 perintah."),
    ]
    for idx, (tname, analogi, tdesc) in enumerate(tools_info):
        col = idx % 2
        row = idx // 2
        x = 0.65 + col * 6.18
        y = 1.80 + row * 1.68
        add_box(s4, x, y, 5.85, 1.48, fill=BG_MINT if row % 2 == 0 else CARD_BG, border=BORDER)
        add_text(s4, x + 0.2, y + 0.14, 3.3, 0.32, tname, size=15, bold=True, color=DARK_GREEN)
        add_text(s4, x + 3.4, y + 0.16, 2.25, 0.28, analogi, size=11.5, bold=True, color=ACCENT_GREEN, align=PP_ALIGN.RIGHT)
        add_text(s4, x + 0.2, y + 0.52, 5.45, 0.86, tdesc, size=12.5, color=TEXT_DARK)

    # ==========================================================
    # SLIDE 5: FLOWCHART & ARSITEKTUR 4 LAYER
    # ==========================================================
    s5 = prs.slides.add_slide(blank)
    add_header(
        s5,
        "Alur Sistem · Flowchart 4 Layer",
        "Alur data pembeli hingga rekomendasi aksi",
        "Seluruh sistem berjalan di 1 VPS Ubuntu (2 vCPU, 4 GB RAM) dengan batas memori eksplisit per layanan",
        5,
        BG_MINT,
    )
    add_picture_fit(s5, "docs/assets/arsitektur-4-layer.png", 0.65, 1.72, 12.03, 5.15, border_color=BORDER)

    # ==========================================================
    # SLIDE 6: CARA KERJA 1 TOPIK KAFKA & 4 KASUS YANG DISELESAIKAN
    # ==========================================================
    s6 = prs.slides.add_slide(blank)
    add_header(
        s6,
        "Desain Sederhana & Kasus Proyek",
        "1 topik Kafka (3 format) untuk 4 kasus nyata",
        "Menyatukan 3 jenis data dalam 1 topik ecommerce_events membuat kode Spark ringkas tanpa stream join berat",
        6,
        BG_WHITE,
    )
    # kiri: struktur 1 pesan
    add_box(s6, 0.65, 1.82, 4.95, 4.9, fill=BG_MINT, border=BORDER)
    add_text(s6, 0.9, 2.02, 4.45, 0.36, "Isi 1 Pesan di ecommerce_events", size=16, bold=True, color=DARK_GREEN)
    add_bullets(s6, 0.9, 2.48, 4.45, 4.05, [
        ("Terstruktur (Angka)", "event_id, user_id, merchant_id, category, amount_idr, quantity, payment_method."),
        ("Semi-Terstruktur (JSON)", "Objek clickstream: session_id, device, city, ip_address, referrer."),
        ("Tidak Terstruktur (Teks)", "review_text dan rating dari pembeli untuk deteksi kata kunci penipuan."),
        ("Kenapa 1 Topik?", "Lebih mudah dijelaskan, lebih stabil di VPS 4 GB RAM, tapi tetap memenuhi 3 Variety."),
    ], size=12.8, space_after=11)

    # kanan: 4 kartu kasus + aksi preskriptif
    cases = [
        ("1. Transaksi Kilat (>= 5 checkout / batch)", "Aksi [KRITIS]: Blokir sementara akun & wajibkan verifikasi OTP.", RED_ACCENT),
        ("2. Nominal Melonjak (> Rp10 juta)", "Aksi [TINGGI]: Tahan transaksi sementara untuk konfirmasi manual.", AMBER_ACCENT),
        ("3. Ulasan Penipuan (palsu, penipu, scam)", "Aksi [TINGGI]: Audit toko secara manual & tahan pencairan dana.", AMBER_ACCENT),
        ("4. Konversi Rendah (klik ramai, checkout < 10%)", "Aksi [SEDANG]: Terbitkan voucher diskon 10–15% / gratis ongkir.", BLUE_ACCENT),
    ]
    for i, (ctitle, cact, clr) in enumerate(cases):
        y = 1.82 + i * 1.25
        add_box(s6, 5.9, y, 6.78, 1.10, fill=CARD_BG, border=BORDER)
        add_box(s6, 5.9, y, 0.12, 1.10, fill=clr, border=None, rounded=False)
        add_text(s6, 6.18, y + 0.14, 6.3, 0.34, ctitle, size=14, bold=True, color=TEXT_DARK)
        add_text(s6, 6.18, y + 0.54, 6.3, 0.42, cact, size=12.8, color=clr, bold=True)

    # ==========================================================
    # SLIDE 7: BUKTI INFRASTRUKTUR DOCKER & RAM VPS
    # ==========================================================
    s7 = prs.slides.add_slide(blank)
    add_header(
        s7,
        "Bukti Praktikum · Infrastruktur VPS",
        "Seluruh 5 container berjalan sehat dengan RAM < 1 GB",
        "Batas mem_limit eksplisit di Docker Compose menjaga VPS 2 vCPU / 4 GB RAM tetap lancar dan bebas OOM",
        7,
        BG_MINT,
    )
    add_picture_fit(s7, "docs/evidence/report_assets/code_docker_compose.png", 0.65, 1.78, 5.65, 3.85, border_color=BORDER)
    add_picture_fit(s7, "docs/evidence/report_assets/term_docker_status.png", 6.55, 1.78, 6.13, 3.85, border_color=BORDER)

    add_text(s7, 0.65, 5.74, 5.65, 0.32, "Pengaturan mem_limit di docker-compose.yml", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s7, 0.65, 6.08, 5.65, 0.65, "Kafka 650m (KRaft), Spark 1200m (local[2]), MongoDB 512m (cache 0,25 GB), Streamlit 384m, Producer 128m.", size=11.8, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    add_text(s7, 6.55, 5.74, 6.13, 0.32, "Hasil docker compose ps & docker stats di VPS", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s7, 6.55, 6.08, 6.13, 0.65, "Total pemakaian RAM aktual gabungan 5 container hanya ~751 MiB, sangat aman di bawah batas puncak 2,6 GB.", size=11.8, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    # ==========================================================
    # SLIDE 8: BUKTI PROCESSING SPARK & STORAGE MONGODB + PARQUET
    # ==========================================================
    s8 = prs.slides.add_slide(blank)
    add_header(
        s8,
        "Bukti Praktikum · Processing & Storage",
        "Aliran streaming berhasil masuk ke MongoDB dan Parquet",
        "PySpark memproses event tiap 10 detik, mendeteksi seluruh pola fraud, dan mempartisi arsip otomatis",
        8,
        BG_WHITE,
    )
    add_picture_fit(s8, "docs/evidence/report_assets/code_spark_stream.png", 0.65, 1.78, 5.85, 3.85, border_color=BORDER)
    add_picture_fit(s8, "docs/evidence/report_assets/term_pipeline_storage.png", 6.75, 1.78, 5.93, 3.85, border_color=BORDER)

    add_text(s8, 0.65, 5.74, 5.85, 0.32, "Logika Inti stream_fraud_detector.py", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s8, 0.65, 6.08, 5.85, 0.65, "Mode local[2], shuffle.partitions=4, simpan Parquet partitionBy('event_date','category'), lalu cek 4 aturan.", size=11.8, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    add_text(s8, 6.75, 5.74, 5.93, 0.32, "Bukti Log Producer, MongoDB, & Folder Parquet", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s8, 6.75, 6.08, 5.93, 0.65, "Semua 3 pola fraud dan 4 kategori aksi preskriptif tercatat di MongoDB, 5 folder partisi kategori terbentuk di disk.", size=11.8, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    # ==========================================================
    # SLIDE 9: BUKTI DASHBOARD LIVE — TAB 1 & TAB 2 PRESKRIPTIF
    # ==========================================================
    s9 = prs.slides.add_slide(blank)
    add_header(
        s9,
        "Bukti Praktikum · Dashboard Streamlit Live",
        "Monitoring Live & Panel Aksi Preskriptif",
        "Tangkapan layar langsung dari http://43.156.152.8:8501 — bukan mockup, seluruh angka terisi dari data live",
        9,
        BG_MINT,
    )
    add_picture_fit(s9, "docs/evidence/screenshots/tab1_monitoring.png", 0.65, 1.75, 5.9, 4.15, border_color=BORDER)
    add_picture_fit(s9, "docs/evidence/screenshots/tab2_preskriptif.png", 6.78, 1.75, 5.9, 4.15, border_color=BORDER)

    add_text(s9, 0.65, 6.00, 5.9, 0.30, "Tab 1 · Monitoring Real-Time & Fraud", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s9, 0.65, 6.32, 5.9, 0.55, "Menampilkan 4.092 event, GMV Rp5,22 M, 351 alert (8,58%), grafik tren, distribusi 3 pola fraud, dan tabel detail.", size=11.5, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    add_text(s9, 6.78, 6.00, 5.9, 0.30, "Tab 2 · Panel Rekomendasi Aksi Preskriptif", size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s9, 6.78, 6.32, 5.9, 0.55, "Saran tindakan langsung sesuai prioritas: blokir + OTP (Kritis), tahan transaksi & audit toko (Tinggi), voucher (Sedang).", size=11.5, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    # ==========================================================
    # SLIDE 10: BUKTI TAB 3 PARQUET & STRATEGI OPTIMASI SPARK
    # ==========================================================
    s10 = prs.slides.add_slide(blank)
    add_header(
        s10,
        "Bukti Praktikum · Data Historis & Optimasi Spark",
        "Arsip Parquet terpartisi & 4 teknik optimasi Apache Spark",
        "Bagaimana cara kami membuat query 1 juta baris tetap kencang di VPS 2 vCPU?",
        10,
        BG_WHITE,
    )
    add_picture_fit(s10, "docs/evidence/screenshots/tab3_parquet.png", 0.65, 1.78, 6.35, 4.5, border_color=BORDER)
    add_text(s10, 0.65, 6.38, 6.35, 0.45, "Tab 3 · Filter langsung folder partisi event_date dan 5 category di dashboard", size=11.5, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    add_box(s10, 7.25, 1.78, 5.43, 4.95, fill=BG_MINT, border=BORDER)
    add_text(s10, 7.5, 1.98, 4.95, 0.36, "4 Teknik Optimasi yang Kami Terapkan", size=16, bold=True, color=DARK_GREEN)
    add_bullets(s10, 7.5, 2.46, 4.95, 4.05, [
        ("1. Partitioning Parquet", "Memecah folder berdasarkan event_date & category. Query hanya membaca 1 folder yang dicari (partition pruning)."),
        ("2. Format Kolom + Snappy", "Parquet hanya membaca kolom yang dihitung dan terkompresi jauh lebih kecil dibanding JSON mentah."),
        ("3. Shuffle Partitions = 4", "Default Spark adalah 200 (terlalu banyak untuk 2 vCPU). Menurunkan ke 4 memangkas overhead antrean task."),
        ("4. Caching (persist)", "DataFrame hasil filter disimpan sementara agar 3 query agregasi tidak membaca disk berulang kali."),
    ], size=12.6, space_after=11)

    # ==========================================================
    # SLIDE 11: HASIL BENCHMARK NYATA 1 JUTA BARIS
    # ==========================================================
    s11 = prs.slides.add_slide(blank)
    add_header(
        s11,
        "Bukti Optimasi · Benchmark 1 Juta Baris",
        "Benchmark 1 juta baris: 5,7x lebih cepat & hemat 94,92% disk",
        "Pengujian adil pada dataset historis 1.000.000 baris (7 hari x 5 kategori) dengan 3 query agregasi sama persis",
        11,
        BG_MINT,
    )
    add_picture_fit(s11, "docs/evidence/screenshots/tab4_benchmark.png", 0.65, 1.78, 6.85, 4.85, border_color=BORDER)

    # kartu angka sorotan besar kanan atas
    stats = [
        ("5,7x", "Lebih Cepat", "39,722 dtk -> 6,966 dtk", ACCENT_GREEN),
        ("94,92%", "Hemat Disk", "180,77 MB -> 9,18 MB", DARK_GREEN),
    ]
    for i, (big, lbl, sub, clr) in enumerate(stats):
        x = 7.75 + i * 2.55
        add_box(s11, x, 1.78, 2.38, 1.75, fill=BG_WHITE, border=BORDER)
        add_text(s11, x + 0.1, 1.92, 2.18, 0.65, big, size=30, bold=True, color=clr, align=PP_ALIGN.CENTER)
        add_text(s11, x + 0.1, 2.62, 2.18, 0.32, lbl, size=13.5, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
        add_text(s11, x + 0.1, 2.98, 2.18, 0.36, sub, size=11, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    add_picture_fit(s11, "docs/evidence/report_assets/term_benchmark.png", 7.75, 3.75, 4.93, 2.05, border_color=BORDER)
    add_text(s11, 7.75, 5.92, 4.93, 0.72, "Output asli bash scripts/run_benchmark.sh di VPS — otomatis tersimpan ke MongoDB dan tampil di Tab 4 dashboard.", size=11.5, color=TEXT_MUTED)

    # ==========================================================
    # SLIDE 12: RINGKASAN HASIL PROYEK (TABEL BERSIH)
    # ==========================================================
    s12 = prs.slides.add_slide(blank)
    add_header(
        s12,
        "Ringkasan Capaian",
        "Ringkasan capaian proyek dengan bukti nyata",
        "Rangkuman keterkaitan arsitektur, implementasi VPS, optimasi Spark, dan nilai bisnis preskriptif",
        12,
        BG_WHITE,
    )
    t_sh = s12.shapes.add_table(6, 3, Inches(0.65), Inches(1.85), Inches(12.03), Inches(4.75))
    t = t_sh.table
    t.columns[0].width = Inches(2.5)
    t.columns[1].width = Inches(4.6)
    t.columns[2].width = Inches(4.93)
    for c, h in enumerate(["Komponen Penilaian", "Yang Kami Bangun", "Bukti Nyata di VPS"]):
        style_cell(t.cell(0, c), h, size=13, bold=True, color=BG_WHITE, fill=DARK_GREEN)
    rows12 = [
        ("Justifikasi 3V+", "Volume (1 juta baris), Velocity (stream per detik), Variety (3 tipe data), + Veracity & Value.", "Perbandingan terukur vs RDBMS dan 3 format data mengalir nyata di topik ecommerce_events."),
        ("Arsitektur 4 Layer", "Ingestion (Kafka KRaft) -> Processing (PySpark) -> Storage (MongoDB + Parquet) -> Streamlit.", "Diagram 4 layer modular dan 5 container berjalan stabil dengan 1 berkas Docker Compose."),
        ("Implementasi & RAM", "Kode modular Python + Docker dengan mem_limit ketat agar aman di VPS 2 vCPU / 4 GB RAM.", "5 container aktif tanpa error fatal, total pemakaian RAM aktual gabungan < 1 GB."),
        ("Optimasi Spark", "shuffle.partitions=4, partitionBy('event_date','category'), Snappy Parquet, dan persist.", "Benchmark 1 juta baris: waktu turun 39,722 -> 6,966 dtk (5,7x) & disk hemat 94,92%."),
        ("Insight Preskriptif", "Panel rekomendasi otomatis untuk 3 pola fraud + 1 sinyal konversi rendah kategori.", "Tampil live di Tab 2 dashboard dengan prioritas Kritis, Tinggi, dan Sedang."),
    ]
    for r_i, (a, b, c_txt) in enumerate(rows12, start=1):
        bg = BG_WHITE if r_i % 2 == 1 else BG_MINT
        style_cell(t.cell(r_i, 0), a, size=12.5, bold=True, color=DARK_GREEN, fill=bg)
        style_cell(t.cell(r_i, 1), b, size=12, color=TEXT_DARK, fill=bg)
        style_cell(t.cell(r_i, 2), c_txt, size=12, color=TEXT_DARK, fill=bg)

    # ==========================================================
    # SLIDE 13: PANDUAN LIVE DEMO DI VPS (5 LANGKAH PRAKTIS)
    # ==========================================================
    s13 = prs.slides.add_slide(blank)
    add_header(
        s13,
        "Panduan Live Demo di VPS",
        "Lima langkah demo langsung saat presentasi",
        "Cukup siapkan 1 terminal SSH ke VPS Ubuntu dan 1 jendela browser ke port 8501",
        13,
        BG_MINT,
    )
    steps = [
        ("1", "Cek Container & RAM VPS", "Jalankan  docker compose ps  dan  docker stats --no-stream  -> tunjukkan 5 container aktif & RAM < 1 GB."),
        ("2", "Tunjukkan Aliran Event Kafka", "Jalankan  docker logs --tail 10 bdef-producer  -> tunjukkan event terus dikirim ke topik ecommerce_events."),
        ("3", "Tunjukkan Hasil di MongoDB & Parquet", "Jalankan  bash scripts/check_status.sh  dan  find data/parquet/events -maxdepth 2  -> tunjukkan koleksi & folder partisi."),
        ("4", "Demo 4 Tab Streamlit Dashboard Live", "Buka  http://43.156.152.8:8501  -> klik Tab 1 (Live KPI), Tab 2 (Aksi Preskriptif), Tab 3 (Filter Parquet), Tab 4 (Benchmark)."),
        ("5", "Opsional: Jalankan Ulang Benchmark 1 Juta Baris", "Jalankan  bash scripts/run_benchmark.sh  -> tunjukkan langsung perbandingan 39,7 dtk vs 6,9 dtk di terminal."),
    ]
    # garis vertikal tipis penghubung 5 lingkaran
    add_box(s13, 0.99, 2.25, 0.025, 4.1, fill=MINT_LIGHT, border=None, rounded=False)
    for i, (num, stitle, sdesc) in enumerate(steps):
        cy = 2.18 + i * 1.02
        add_circle_num(s13, 1.0, cy, 0.50, num, fill=ACCENT_GREEN)
        add_text(s13, 1.48, cy - 0.28, 11.1, 0.34, stitle, size=15.5, bold=True, color=TEXT_DARK)
        add_text(s13, 1.48, cy + 0.06, 11.1, 0.38, sdesc, size=12.8, color=TEXT_MUTED)

    # ==========================================================
    # SLIDE 14: PENUTUP, KESIMPULAN & SLOT LINK YOUTUBE (GELAP)
    # ==========================================================
    s14 = prs.slides.add_slide(blank)
    set_bg(s14, DARK_GREEN)
    add_box(s14, 0, 1.05, 13.333, 0.015, fill=LINE_DARK, border=None, rounded=False)
    add_box(s14, 0, 5.75, 13.333, 0.015, fill=LINE_DARK, border=None, rounded=False)

    add_text(s14, 0.65, 0.42, 8.6, 0.35, "KESIMPULAN & LINK VIDEO PRESENTASI", size=12, bold=True, color=MINT_LIGHT)
    add_text(s14, 9.8, 0.42, 2.9, 0.35, "KELOMPOK 12", size=12.5, bold=True, color=BG_WHITE, align=PP_ALIGN.RIGHT)

    add_text(
        s14, 0.65, 1.42, 12.0, 1.05,
        "Arsitektur Big Data yang tepat tetap bisa ringan,\n5,7x lebih cepat, dan memberi rekomendasi aksi nyata.",
        size=24, bold=True, color=BG_WHITE
    )

    # kotak slot link youtube wajib di slide terakhir sesuai panduan tugas akhir
    add_box(s14, 0.65, 2.88, 12.03, 1.48, fill=RGBColor(22, 62, 46), border=MINT_LIGHT, border_pt=1.5)
    add_text(s14, 0.95, 3.05, 11.4, 0.32, "LINK VIDEO PRESENTASI YOUTUBE (PROYEK AKHIR KELOMPOK 12)", size=12, bold=True, color=MINT_LIGHT)
    add_text(s14, 0.95, 3.44, 11.4, 0.44, "[ Tempelkan Link YouTube Kelompok 12 di Sini Sebelum Upload ke EMAS ]", size=18, bold=True, color=BG_WHITE)
    add_text(s14, 0.95, 3.94, 11.4, 0.30, "Contoh: https://youtu.be/xxxxxxxxxxx", size=12, color=TEXT_SOFT_LIGHT)

    # info repo & live dashboard
    add_box(s14, 0.65, 4.62, 12.03, 0.85, fill=RGBColor(20, 54, 40), border=LINE_DARK)
    add_text(
        s14, 0.95, 4.86, 11.4, 0.38,
        "Repository GitHub:  github.com/ZulfahmiFjr/bigdata-ecommerce-fraud    |    Dashboard Live:  http://43.156.152.8:8501",
        size=11.8, bold=True, color=TEXT_SOFT_LIGHT
    )

    add_text(
        s14, 0.65, 6.02, 9.2, 0.95,
        "Terima kasih atas perhatiannya.\nMuhamad Rifqi Fadil Itsnain  ·  Muhammad Zaki Al Khairi  ·  Muhammad Hashif Jade  ·  Zulfahmi Fajri",
        size=12.5, color=TEXT_SOFT_LIGHT
    )
    add_text(s14, 9.7, 6.95, 3.0, 0.3, f"Kelompok 12 · Big Data 2026 · {TOTAL_SLIDES}", size=10, color=TEXT_SOFT_LIGHT, align=PP_ALIGN.RIGHT)

    out_pptx = os.path.join(BASE_DIR, "deliverables", "final", "Presentasi_Proyek_Akhir_BigData_Kelompok12.pptx")
    os.makedirs(os.path.dirname(out_pptx), exist_ok=True)
    prs.save(out_pptx)
    print("PPTX SAVED:", out_pptx)


if __name__ == "__main__":
    build_ppt()
