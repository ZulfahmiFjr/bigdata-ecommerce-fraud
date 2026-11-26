import os
import re
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLACK = RGBColor(0, 0, 0)
FONT_NAME = "Times New Roman"


def set_run_font(run, size=12, bold=False, italic=False, underline=False):
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.underline = underline
    run.font.color.rgb = BLACK
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT_NAME)


def add_page_number_footer(section):
    # tambah nomor halaman bold hitam di bawah tengah mulai halaman kedua kayak laporan kemjar
    section.different_first_page_header_footer = True
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)

    run = p.add_run()
    set_run_font(run, size=11, bold=True)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)


def add_heading_chapter(doc, text, page_break=True):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, size=14, bold=True)
    return p


def add_heading_sub(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, size=12, bold=True)
    return p


def add_body(doc, text, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    set_run_font(r, size=12)
    return p


def add_figure(doc, rel_path, caption, width_in=6.25):
    full_path = os.path.join(BASE_DIR, rel_path)
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(full_path, width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(8)
    p_cap.paragraph_format.line_spacing = 1.1
    r_cap = p_cap.add_run(caption)
    set_run_font(r_cap, size=11, bold=False)


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '</w:tblBorders>'
    )
    tbl_pr.append(borders)


def set_cell_padding(cell, top=60, bottom=60, left=100, right=100):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        '</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def add_styled_table(doc, caption, headers, rows, col_widths_in):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(6)
    p_cap.paragraph_format.space_after = Pt(4)
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption)
    set_run_font(r_cap, size=11, bold=False)

    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)

    # pasang header tabel biar otomatis berulang kalo kepotong halaman
    hdr_tr = table.rows[0]._tr
    hdr_trPr = hdr_tr.get_or_add_trPr()
    hdr_trPr.append(OxmlElement("w:tblHeader"))
    hdr_trPr.append(OxmlElement("w:cantSplit"))

    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.width = Inches(col_widths_in[c_idx])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_padding(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.08
        r = p.add_run(h_text)
        set_run_font(r, size=10.5, bold=True)

    for r_idx, row_vals in enumerate(rows, start=1):
        trPr = table.rows[r_idx]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx, c_idx)
            cell.width = Inches(col_widths_in[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            set_cell_padding(cell, top=42, bottom=42, left=85, right=85)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.08
            r = p.add_run(val)
            set_run_font(r, size=10.5, bold=(c_idx == 0))

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)
    return table


def build_report():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    add_page_number_footer(sec)

    # --- HALAMAN COVER (KLASIK POLOS HITAM ALA LAPORAN KEMJAR) ---
    for _ in range(3):
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_after = Pt(12)

    for txt, sz in [("PROYEK AKHIR", 20), ("TEKNOLOGI BIG DATA 2026", 18)]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(txt)
        set_run_font(r, size=sz, bold=True)

    p_gap = doc.add_paragraph()
    p_gap.paragraph_format.space_after = Pt(48)

    p_k = doc.add_paragraph()
    p_k.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_k.paragraph_format.space_after = Pt(10)
    set_run_font(p_k.add_run("KELOMPOK 12"), size=14, bold=True, underline=True)

    for member in [
        "Muhamad Rifqi Fadil Itsnain (2406355306)",
        "Muhammad Zaki Al Khairi (2406432375)",
        "Muhammad Hashif Jade (2406396786)",
        "Zulfahmi Fajri (2406345425)",
    ]:
        pm = doc.add_paragraph()
        pm.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pm.paragraph_format.space_after = Pt(4)
        set_run_font(pm.add_run(member), size=12)

    p_gap2 = doc.add_paragraph()
    p_gap2.paragraph_format.space_after = Pt(48)

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_after = Pt(10)
    set_run_font(p_t.add_run("TOPIK"), size=14, bold=True, underline=True)

    p_topik = doc.add_paragraph()
    p_topik.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topik.paragraph_format.space_after = Pt(6)
    set_run_font(p_topik.add_run("Sistem Deteksi Anomali (Fraud) dan Analitik Aktivitas E-Commerce Real-Time"), size=13, bold=True)

    # --- ABSTRAK ---
    add_heading_chapter(doc, "ABSTRAK", page_break=True)
    add_body(
        doc,
        "Aktivitas pengguna pada platform e-commerce berlangsung sangat cepat dan menghasilkan jutaan catatan klik, keranjang belanja, pembayaran, serta ulasan setiap hari, kondisi ini sering dimanfaatkan pelaku kecurangan untuk melakukan transaksi kilat, pembayaran bernominal ekstrem, atau penipuan toko yang baru ketahuan jika hanya diperiksa lewat rekap harian, oleh karena itu kami merancang dan membangun sistem deteksi anomali fraud dan analitik aktivitas e-commerce real-time yang berjalan end-to-end pada VPS Ubuntu 2 vCPU dan 4 GB RAM.",
    )
    add_body(
        doc,
        "Sistem kami disusun menjadi empat lapisan yang saling terpisah, yaitu Python Producer bersama Apache Kafka mode KRaft tanpa Zookeeper pada lapisan ingestion, Apache Spark dengan PySpark mode local[2] untuk Structured Streaming dan batch benchmark pada lapisan processing, MongoDB bersama arsip Apache Parquet Snappy terpartisi berdasarkan tanggal dan kategori pada lapisan storage, serta Streamlit Dashboard pada lapisan visualization yang menampilkan grafik real-time dan panel rekomendasi aksi preskriptif bagi tim operasional.",
    )
    add_body(
        doc,
        "Hasil pengujian nyata pada VPS menunjukkan seluruh lima container berjalan stabil dengan total pemakaian RAM gabungan di bawah 1 GB, tiga pola fraud serta satu sinyal konversi rendah berhasil terdeteksi dan menghasilkan rekomendasi tindakan otomatis, selain itu pengujian benchmark Apache Spark pada 1 juta baris membuktikan optimasi partisi Parquet, shuffle partitions 4, dan caching mempercepat waktu eksekusi dari 39,722 detik menjadi 6,966 detik atau 5,7x lebih cepat sekaligus menghemat ukuran penyimpanan hingga 94,92%.",
    )
    add_body(
        doc,
        "Kata kunci: Apache Kafka, Apache Spark, MongoDB, Apache Parquet, Streamlit, deteksi fraud, analitik real-time, aksi preskriptif.",
    )

    # --- BAB 1 PENDAHULUAN ---
    add_heading_chapter(doc, "BAB 1  PENDAHULUAN", page_break=True)

    add_heading_sub(doc, "1.1 Latar Belakang")
    add_body(
        doc,
        "Platform e-commerce modern mencatat aktivitas pengguna dalam jumlah besar setiap detik, mulai dari kunjungan halaman produk, penambahan barang ke keranjang, proses pembayaran, hingga penulisan ulasan pembeli, di balik padatnya trafik tersebut pelaku kecurangan memanfaatkan celah kecepatan sistem untuk menguji kartu secara beruntun, melakukan transaksi bernominal sangat besar, atau menjalankan toko fiktif yang memicu keluhan penipuan dari pembeli.",
    )
    add_body(
        doc,
        "Apabila deteksi kecurangan hanya mengandalkan pemeriksaan manual atau rekap batch di malam hari, dana transaksi sudah telanjur berpindah sebelum tim operasional sempat bertindak, selain itu banyak sistem pemantauan hanya menampilkan grafik statistik tanpa memberi arahan tindakan langsung, sehingga kami membangun pipeline pemrosesan streaming dan batch yang mendeteksi anomali secara cepat sekaligus menyajikan rekomendasi aksi preskriptif.",
    )

    add_heading_sub(doc, "1.2 Rumusan Masalah")
    add_body(
        doc,
        "Berdasarkan latar belakang tersebut kami merumuskan tiga masalah utama, pertama bagaimana merancang pipeline big data yang mampu memproses tiga jenis data e-commerce secara real-time tanpa membebani VPS terbatas 2 vCPU dan 4 GB RAM, kedua bagaimana menerapkan optimasi Apache Spark yang terukur agar pengolahan data historis skala 1 juta baris berjalan jauh lebih cepat dan hemat disk, dan ketiga bagaimana menyajikan hasil olahan menjadi dashboard interaktif dengan rekomendasi aksi nyata bagi tim operasional.",
    )

    add_heading_sub(doc, "1.3 Tujuan")
    add_body(
        doc,
        "Melalui proyek ini kami bertujuan membangun sistem deteksi fraud dan analitik e-commerce end-to-end dengan arsitektur empat lapisan menggunakan Docker Compose, membuktikan peningkatan performa Apache Spark melalui perbandingan sebelum dan sesudah optimasi partisi serta caching, dan menyediakan dashboard Streamlit interaktif yang menampilkan pemantauan real-time, arsip Parquet terpartisi, hasil benchmark, serta rekomendasi tindakan otomatis.",
    )

    add_heading_sub(doc, "1.4 Ruang Lingkup")
    add_body(
        doc,
        "Kami membatasi sumber data pada simulasi aliran event e-commerce yang kami bangkitkan dengan Python Producer untuk pola normal serta tiga pola fraud, ditambah data historis sintetis sebanyak 1 juta baris untuk pengujian benchmark, seluruh layanan dijalankan dengan Docker Compose pada satu VPS Ubuntu 2 vCPU, 4 GB RAM, dan swap 3,9 GiB dengan batas memori eksplisit di setiap container agar tidak mengganggu layanan lain pada server.",
    )

    # --- BAB 2 TINJAUAN PUSTAKA DAN TEKNOLOGI ---
    add_heading_chapter(doc, "BAB 2  TINJAUAN PUSTAKA DAN TEKNOLOGI", page_break=True)

    add_heading_sub(doc, "2.1 Konsep Big Data dan Karakteristik 3V+")
    add_body(
        doc,
        "Big data merujuk pada kumpulan data yang tidak lagi efisien ditangani oleh basis data konvensional karena tiga karakteristik utama yaitu volume yang besar, velocity atau kecepatan data masuk yang tinggi, dan variety atau keberagaman format data terstruktur, semi-terstruktur, serta tidak terstruktur, selain tiga unsur tersebut kami juga memperhatikan veracity untuk menjaga validitas skema aliran data dan value agar hasil analisis memberi nilai bisnis langsung berupa keputusan tindakan.",
    )

    add_heading_sub(doc, "2.2 Perbandingan RDBMS Tradisional dan Arsitektur Big Data")
    add_body(
        doc,
        "Basis data relasional atau RDBMS unggul untuk transaksi konsisten dengan skema tetap, tetapi menjadi kurang efisien saat harus menampung ribuan event per detik, menyimpan objek JSON yang atributnya beragam bersama teks ulasan bebas, sekaligus menjalankan query agregasi jutaan baris, oleh karena itu kami memisahkan peran ingest, pemrosesan, dan penyimpanan sebagaimana dirangkum pada tabel perbandingan di bawah ini.",
    )

    add_styled_table(
        doc,
        "Tabel 2.1 Perbandingan RDBMS tradisional dan arsitektur big data kami",
        ["Aspek", "RDBMS Tradisional", "Arsitektur Big Data Kami"],
        [
            ["Kecepatan tulis (Velocity)", "Tulis langsung beruntun memicu lock tabel dan beban indeks saat trafik melonjak", "Apache Kafka berperan sebagai penyangga aliran sehingga ingest terpisah dari pemrosesan"],
            ["Format data (Variety)", "Skema kolom kaku menyulitkan penyimpanan JSON bersarang dan teks ulasan", "MongoDB menyimpan dokumen JSON fleksibel dan Parquet menyimpan kolom terkompresi"],
            ["Deteksi real-time", "Polling query agregasi berulang ke database utama mengganggu transaksi aktif", "PySpark Structured Streaming memproses micro-batch langsung dari topik Kafka"],
            ["Analisis historis (Volume)", "Full table scan jutaan baris lambat dan skalabilitas bertumpu pada satu mesin", "Parquet terpartisi memangkas pembacaan folder lewat partition pruning dan siap scale-out"],
        ],
        [1.45, 2.4, 2.4],
    )

    add_heading_sub(doc, "2.3 Teknologi yang Digunakan")
    add_body(
        doc,
        "Kami memilih rangkaian teknologi yang paling ringan namun tetap memenuhi standar arsitektur big data, yaitu Apache Kafka mode KRaft sebagai message broker tanpa Zookeeper agar hemat RAM, Apache Spark dengan PySpark untuk pemrosesan streaming dan batch pada satu mesin yang sama, MongoDB dengan batas cache WiredTiger untuk penyimpanan data real-time berformat dokumen JSON, Apache Parquet berkompresi Snappy untuk arsip analitik berbasis kolom, Streamlit untuk membangun dashboard web interaktif berbasis Python, dan Docker Compose untuk mengatur seluruh container serta batas memorinya dalam satu konfigurasi.",
    )

    # --- BAB 3 METODOLOGI DAN PERANCANGAN ---
    add_heading_chapter(doc, "BAB 3  METODOLOGI DAN PERANCANGAN", page_break=True)

    add_heading_sub(doc, "3.1 Justifikasi Big Data (3V+ Terukur)")
    add_body(
        doc,
        "Kami mengukur kelayakan kasus e-commerce ini terhadap lima unsur 3V+ agar jelas bahwa permasalahan ini memang membutuhkan pendekatan big data, rincian ukuran dunia nyata beserta implementasi nyata pada VPS kami sajikan pada tabel di bawah ini.",
    )

    add_styled_table(
        doc,
        "Tabel 3.1 Justifikasi 3V+ yang terukur pada sistem kami",
        ["Karakteristik", "Skala Dunia Nyata", "Implementasi dan Bukti di VPS Kami"],
        [
            ["Volume", "50 ribu pengguna aktif x 40 event per hari menghasilkan sekitar 2 juta log per hari atau 60 juta baris per bulan", "Benchmark batch mengolah 1 juta baris data historis dan aliran streaming terus menambah arsip Parquet"],
            ["Velocity", "Trafik promo masuk puluhan hingga ribuan event per detik sehingga deteksi fraud harus berlatensi rendah", "Python Producer mengirim 6 event per detik ke Kafka dan diproses PySpark tiap micro-batch 10 detik"],
            ["Variety", "Menggabungkan data transaksi numerik, log clickstream JSON, dan teks ulasan pembeli", "Satu topik ecommerce_events memuat angka transaksi, objek nested JSON clickstream, dan teks ulasan"],
            ["Veracity", "Aliran rawan data kosong atau skema tidak sesuai", "Validasi skema StructType eksplisit dan filter event_id tidak null di PySpark"],
            ["Value", "Data perlu menghasilkan keputusan bisnis cepat", "Panel Rekomendasi Aksi Preskriptif otomatis untuk keamanan akun, audit toko, dan promo kategori"],
        ],
        [1.15, 2.5, 2.6],
    )

    add_heading_sub(doc, "3.2 Arsitektur Solusi 4 Layer")
    add_body(
        doc,
        "Sistem kami dibagi menjadi empat lapisan modular dari hulu ke hilir agar setiap komponen memiliki tanggung jawab jelas dan mudah dikembangkan, aliran data lengkap beserta batas alokasi RAM masing-masing layanan ditunjukkan pada diagram arsitektur di bawah ini.",
    )

    add_figure(
        doc,
        "docs/assets/arsitektur-4-layer.png",
        "Gambar 3.1 Diagram arsitektur 4 layer sistem deteksi fraud dan analitik e-commerce",
        width_in=6.25,
    )

    add_body(
        doc,
        "Berdasarkan diagram di atas, event yang dibangkitkan oleh Python Producer masuk ke satu topik Apache Kafka bernama ecommerce_events, kemudian PySpark Structured Streaming membaca topik tersebut untuk mendeteksi anomali, menulis arsip historis ke folder Parquet terpartisi, dan menyimpan metrik serta rekomendasi aksi ke MongoDB, selanjutnya Streamlit Dashboard membaca kedua penyimpanan tersebut untuk disajikan secara interaktif kepada pengguna.",
    )

    add_heading_sub(doc, "3.3 Skema Data")
    add_body(
        doc,
        "Kami menyatukan aliran ke satu topik Kafka agar kode PySpark tetap ringkas tanpa stream-to-stream join yang boros memori, namun setiap pesan JSON tetap membawa tiga format data sekaligus yaitu atribut transaksi terstruktur, objek bersarang clickstream yang berisi sesi, perangkat, kota, IP, serta referrer, dan teks bebas ulasan pembeli beserta rating.",
    )
    add_body(
        doc,
        "Pada lapisan storage, MongoDB menyimpan empat koleksi operasional yaitu realtime_metrics untuk ringkasan trafik tiap micro-batch, fraud_alerts untuk detail transaksi mencurigakan beserta skor risiko, prescriptive_actions untuk daftar saran tindakan otomatis, dan benchmark_results untuk hasil uji performa Spark, sementara data historis disimpan pada disk lokal dalam format Parquet Snappy yang dipartisi menurut event_date dan category.",
    )

    add_heading_sub(doc, "3.4 Pola Deteksi Fraud dan Aturan Aksi Preskriptif")
    add_body(
        doc,
        "Kami merancang tiga pola deteksi fraud utama dan satu sinyal konversi bisnis agar logika pemrosesan mudah dipahami namun langsung berdampak nyata bagi operasional e-commerce, seluruh aturan pemicu beserta rekomendasi aksi otomatisnya dirangkum pada tabel berikut.",
    )

    add_styled_table(
        doc,
        "Tabel 3.2 Pola deteksi fraud, sinyal bisnis, dan rekomendasi aksi preskriptif",
        ["Pola / Sinyal", "Kondisi Pemicu", "Prioritas", "Rekomendasi Aksi Preskriptif"],
        [
            ["Transaksi Kilat", "Satu akun melakukan >= 5 checkout beruntun dalam 1 jendela batch (skor risiko 95)", "Kritis", "Blokir sementara akun terindikasi fraud dan wajibkan verifikasi OTP"],
            ["Nominal Melonjak", "Nominal satu transaksi checkout melebihi Rp10 juta (skor risiko 88)", "Tinggi", "Tahan transaksi sementara untuk konfirmasi manual sebelum dana diteruskan"],
            ["Ulasan Penipuan", "Teks ulasan mengandung kata kunci palsu, penipu, scam, barang kosong, bohong, atau abal-abal (skor 82)", "Tinggi", "Audit toko secara manual dan tahan pencairan dana sementara"],
            ["Konversi Rendah", "Kategori memiliki >= 5 klik produk tetapi rasio checkout di bawah 10%", "Sedang", "Terbitkan voucher diskon 10-15% atau promo gratis ongkir khusus kategori tersebut"],
        ],
        [1.25, 2.15, 0.7, 2.15],
    )

    add_heading_sub(doc, "3.5 Alokasi Resource VPS dan Strategi Optimasi Spark")
    add_body(
        doc,
        "Karena VPS pengujian hanya memiliki 2 vCPU dan 4 GB RAM yang juga dipakai layanan lain, kami menambahkan swap sekunder 2 GiB sehingga total swap menjadi 3,9 GiB dan menetapkan batas memori eksplisit pada setiap container Docker agar total puncak tetap aman di bawah 2,6 GB RAM, pembagian batas resource tiap layanan disajikan pada tabel di bawah ini.",
    )

    add_styled_table(
        doc,
        "Tabel 3.3 Alokasi batas memori setiap container pada Docker Compose",
        ["Layanan", "Peran Utama", "Pengaturan Hemat RAM", "mem_limit"],
        [
            ["Kafka KRaft", "Broker pesan topik ecommerce_events", "Mode KRaft tanpa Zookeeper, heap 256-384 MB", "650 MB"],
            ["PySpark", "Structured Streaming dan batch benchmark", "Mode local[2], driver memory 768 MB, shuffle partitions 4", "1200 MB"],
            ["MongoDB", "Penyimpanan data real-time dan alert", "WiredTiger cache dibatasi 0,25 GB", "512 MB"],
            ["Streamlit", "Dashboard web interaktif port 8501", "Pembacaan partisi Parquet terbaru secara terfilter", "384 MB"],
            ["Producer", "Generator stream normal dan pola fraud", "Skrip Python ringan dengan laju 6 event per detik", "128 MB"],
        ],
        [1.1, 2.1, 2.25, 0.8],
    )

    add_body(
        doc,
        "Untuk memenuhi kriteria optimasi performa pada Apache Spark, kami menerapkan empat langkah nyata yaitu menurunkan jumlah shuffle partitions dari bawaan 200 menjadi 4 agar sesuai dengan 2 vCPU, mempartisi arsip Parquet berdasarkan event_date dan category agar query hanya membaca folder relevan, menggunakan format kolom Parquet dengan kompresi Snappy, serta memakai persist pada DataFrame yang diolah berulang dalam satu sesi batch.",
    )

    # --- BAB 4 IMPLEMENTASI DAN HASIL ---
    add_heading_chapter(doc, "BAB 4  IMPLEMENTASI DAN HASIL", page_break=False)

    add_heading_sub(doc, "4.1 Konfigurasi Lingkungan dan Orkestrasi Docker")
    add_body(
        doc,
        "Kami mendefinisikan lima layanan utama beserta batas memori dan healthcheck di dalam konfigurasi Docker Compose agar seluruh pipeline dapat dijalankan cukup dengan satu perintah, potongan konfigurasi penting tersebut terlihat pada cuplikan kode berikut.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/code_docker_compose.png",
        "Gambar 4.1 Cuplikan konfigurasi Docker Compose untuk batas memori dan layanan utama",
        width_in=6.0,
    )

    add_body(
        doc,
        "Setelah seluruh container dijalankan pada VPS Ubuntu, kami memeriksa status layanan dan konsumsi memori aktual melalui terminal Docker, hasilnya seluruh lima container berada pada status aktif serta sehat dengan total pemakaian RAM gabungan hanya sekitar 751 MiB atau jauh di bawah batas puncak 2,6 GB RAM.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/term_docker_status.png",
        "Gambar 4.2 Verifikasi status container dan pemakaian RAM aktual pada VPS Ubuntu",
        width_in=6.25,
    )

    add_heading_sub(doc, "4.2 Implementasi Layer Ingestion")
    add_body(
        doc,
        "Pada lapisan ingestion kami membangun skrip Python Producer yang menyusun payload JSON berisi tiga jenis data sekaligus dan mengirimkannya terus-menerus ke topik ecommerce_events, skrip ini juga secara berkala menyisipkan pola transaksi kilat, transaksi di atas Rp10 juta, ulasan mengandung kata kunci penipuan, serta rasio klik tinggi pada kategori elektronik dan gadget agar skenario konversi rendah ikut teruji.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/code_producer.png",
        "Gambar 4.3 Cuplikan kode Python Producer untuk payload tiga jenis data dan injeksi pola fraud",
        width_in=6.25,
    )

    add_heading_sub(doc, "4.3 Implementasi Layer Processing dan Storage")
    add_body(
        doc,
        "Pada lapisan processing kami menjalankan skrip PySpark Structured Streaming dalam mode local[2] dengan shuffle partitions bernilai 4 yang memproses setiap micro-batch berjarak 10 detik, setiap batch langsung ditulis ke arsip Parquet Snappy terpartisi menurut event_date dan category sambil mengevaluasi tiga pola fraud serta sinyal konversi rendah untuk disimpan ke koleksi MongoDB.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/code_spark_stream.png",
        "Gambar 4.4 Cuplikan kode PySpark Structured Streaming untuk partisi Parquet dan deteksi fraud",
        width_in=6.25,
    )

    add_body(
        doc,
        "Pemeriksaan log producer, koleksi MongoDB, dan direktori disk lokal membuktikan seluruh aliran data bekerja utuh tanpa error fatal, pada saat pencatatan bukti di terminal tercatat 1680 event telah terkirim, seluruh tiga jenis fraud dan empat kategori aksi preskriptif masuk ke MongoDB, serta lima folder partisi kategori di bawah tanggal aktif terbentuk otomatis dalam format Parquet.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/term_pipeline_storage.png",
        "Gambar 4.5 Bukti log producer, ringkasan koleksi MongoDB, dan struktur folder partisi Parquet",
        width_in=6.25,
    )

    add_heading_sub(doc, "4.4 Implementasi Layer Visualisasi dan Aksi Preskriptif")
    add_body(
        doc,
        "Lapisan visualisasi kami bangun dengan Streamlit pada port 8501 yang memuat empat tab utama, tangkapan layar berikut menampilkan Tab 1 Monitoring Real-Time dan Fraud yang menyajikan 4092 event masuk, total transaksi Rp5,22 miliar, 351 alert fraud dengan rasio anomali 8,58%, grafik tren per batch, distribusi tiga pola fraud, serta tabel detail alert terbaru.",
    )

    add_figure(
        doc,
        "docs/evidence/screenshots/tab1_monitoring.png",
        "Gambar 4.6 Tampilan langsung Tab 1 Monitoring Real-Time dan Fraud pada Streamlit Dashboard",
        width_in=6.25,
    )

    add_body(
        doc,
        "Agar sistem tidak berhenti pada grafik deskriptif saja, Tab 2 menyajikan panel Rekomendasi Aksi Preskriptif yang dikelompokkan berdasarkan warna prioritas, mulai dari prioritas kritis untuk pemblokiran sementara akun transaksi kilat dengan verifikasi OTP, prioritas tinggi untuk penahanan transaksi bernominal besar serta audit merchant terindikasi ulasan penipuan, hingga prioritas sedang berupa rekomendasi voucher diskon bagi kategori yang ramai klik tetapi rendah checkout.",
    )

    add_figure(
        doc,
        "docs/evidence/screenshots/tab2_preskriptif.png",
        "Gambar 4.7 Tampilan langsung Tab 2 Panel Rekomendasi Aksi Preskriptif pada Streamlit Dashboard",
        width_in=6.25,
    )

    add_body(
        doc,
        "Pada Tab 3 pengguna dapat menelusuri arsip historis Parquet terpartisi secara interaktif melalui filter event_date dan category, mekanisme pembacaan kami menerapkan partition pruning ke folder partisi terkait sehingga grafik nilai transaksi per kategori dan sampel tabel data tampil cepat walaupun jumlah file terus bertambah.",
    )

    add_figure(
        doc,
        "docs/evidence/screenshots/tab3_parquet.png",
        "Gambar 4.8 Tampilan langsung Tab 3 Data Historis Parquet Partisi pada Streamlit Dashboard",
        width_in=6.25,
    )

    add_body(
        doc,
        "Tab 4 menampilkan hasil pengujian benchmark optimasi Apache Spark secara visual agar perbandingan waktu eksekusi query dan efisiensi ruang penyimpanan antara kondisi sebelum dan sesudah optimasi dapat langsung diamati dari satu halaman dashboard.",
    )

    add_figure(
        doc,
        "docs/evidence/screenshots/tab4_benchmark.png",
        "Gambar 4.9 Tampilan langsung Tab 4 Bukti Optimasi Spark pada Streamlit Dashboard",
        width_in=6.25,
    )

    add_heading_sub(doc, "4.5 Hasil Benchmark Optimasi Spark dan Pembahasan")
    add_body(
        doc,
        "Kami menguji efektivitas optimasi Apache Spark secara adil pada dataset historis sebanyak 1 juta baris yang tersebar pada 7 tanggal dan 5 kategori, skrip benchmark membandingkan dua skenario query yang sama persis yaitu membaca JSON mentah tanpa partisi dengan shuffle partitions 200 tanpa cache melawan membaca Parquet terpartisi dengan shuffle partitions 4 dan persist, sebagaimana terlihat pada potongan kode dan hasil eksekusi berikut.",
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/code_benchmark.png",
        "Gambar 4.10 Cuplikan kode skenario sebelum dan sesudah optimasi pada skrip benchmark",
        width_in=6.25,
    )

    add_figure(
        doc,
        "docs/evidence/report_assets/term_benchmark.png",
        "Gambar 4.11 Output terminal hasil pengujian benchmark 1 juta baris pada VPS Ubuntu",
        width_in=6.25,
    )

    add_styled_table(
        doc,
        "Tabel 4.1 Ringkasan hasil benchmark Apache Spark pada 1 juta baris data",
        ["Metrik Pengujian", "Sebelum Optimasi (JSON, shuffle=200, tanpa cache)", "Sesudah Optimasi (Parquet Partisi, shuffle=4, persist)", "Perubahan"],
        [
            ["Waktu eksekusi 3 query analitik", "39,722 detik", "6,966 detik", "5,7x lebih cepat (hemat 82,46%)"],
            ["Ukuran file di disk", "180,77 MB", "9,18 MB", "Hemat 94,92% ruang disk"],
            ["Jumlah shuffle partitions", "200 (bawaan Spark)", "4 (sesuai 2 vCPU)", "Overhead penjadwalan turun drastis"],
            ["Partition pruning & caching", "Tidak aktif (full scan)", "Aktif (event_date & category + persist)", "Hanya membaca 1 dari 35 partisi"],
        ],
        [1.55, 1.65, 1.75, 1.3],
    )

    add_body(
        doc,
        "Berdasarkan tabel hasil benchmark di atas, percepatan sebesar 5,7x terjadi karena kombinasi tiga faktor yang saling menguatkan, yaitu partition pruning yang langsung menyaring pembacaan ke satu folder tanggal dan kategori dari total 35 kombinasi partisi, penyimpanan kolom Parquet Snappy yang memangkas ukuran disk sebesar 94,92%, serta penurunan shuffle partitions menjadi 4 bersama caching persist yang menghindari pembacaan ulang disk saat tiga query agregasi dijalankan berurutan.",
    )

    # --- BAB 5 KESIMPULAN DAN SARAN ---
    add_heading_chapter(doc, "BAB 5  KESIMPULAN DAN SARAN", page_break=True)

    add_heading_sub(doc, "5.1 Kesimpulan")
    add_body(
        doc,
        "Kami berhasil merancang dan menjalankan sistem deteksi fraud dan analitik aktivitas e-commerce real-time secara end-to-end pada VPS Ubuntu 2 vCPU dan 4 GB RAM dengan arsitektur empat lapisan yang hemat memori, seluruh lima container berjalan stabil dengan pemakaian RAM aktual di bawah 1 GB dan mampu mendeteksi tiga pola fraud serta satu sinyal konversi rendah secara langsung.",
    )
    add_body(
        doc,
        "Penerapan optimasi Apache Spark melalui partisi Parquet berdasarkan tanggal dan kategori, kompresi Snappy, penyesuaian shuffle partitions menjadi 4, dan caching terbukti secara nyata pada 1 juta baris data mempercepat waktu query dari 39,722 detik menjadi 6,966 detik atau 5,7x lebih cepat sekaligus menghemat ukuran disk 94,92%, sedangkan Streamlit Dashboard berhasil menyajikan metrik real-time bersama rekomendasi aksi preskriptif yang langsung dapat dipakai tim operasional.",
    )

    add_heading_sub(doc, "5.2 Saran")
    add_body(
        doc,
        "Untuk pengembangan berikutnya kami menyarankan penambahan integrasi notifikasi otomatis ke Telegram atau email saat alert prioritas kritis muncul, penerapan model machine learning ringan untuk penentuan skor risiko yang lebih adaptif terhadap pola fraud baru, serta pengembangan ke mode klaster multi-node dengan beberapa broker Apache Kafka dan worker Apache Spark apabila trafik sudah melampaui kapasitas satu VPS.",
    )

    # --- DAFTAR PUSTAKA ---
    add_heading_chapter(doc, "DAFTAR PUSTAKA", page_break=True)
    refs = [
        "Apache Software Foundation, 2024, Apache Kafka Documentation, KRaft Mode dan Distributed Streaming Platform, tersedia di kafka apache org.",
        "Apache Software Foundation, 2024, Apache Spark Documentation, Structured Streaming dan Spark SQL Programming Guide, tersedia di spark apache org.",
        "Apache Software Foundation, 2024, Apache Parquet Documentation, Columnar Storage Format dan Compression, tersedia di parquet apache org.",
        "Docker Inc, 2024, Docker Compose Specification dan Resource Constraints, tersedia di docs docker com.",
        "Laney, D, 2001, 3D Data Management, Controlling Data Volume, Velocity, and Variety, META Group Research Note.",
        "Marz, N dan Warren, J, 2015, Big Data, Principles and Best Practices of Scalable Realtime Data Systems, Manning Publications.",
        "MongoDB Inc, 2024, MongoDB Manual, WiredTiger Storage Engine dan Indexing, tersedia di mongodb com.",
        "Streamlit Inc, 2024, Streamlit Documentation, Interactive Data Apps in Python, tersedia di docs streamlit io.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        set_run_font(p.add_run(ref), size=11.5)

    # --- LAMPIRAN ---
    add_heading_chapter(doc, "LAMPIRAN  REPOSITORY DAN STRUKTUR KODE SUMBER", page_break=True)
    add_body(
        doc,
        "Seluruh kode sumber, konfigurasi Docker, dokumen rancangan, dan bukti pengujian kami simpan pada repository GitHub publik ZulfahmiFjr/bigdata-ecommerce-fraud, ringkasan berkas utama proyek beserta fungsinya disajikan pada tabel berikut.",
    )

    add_styled_table(
        doc,
        "Tabel Lampiran 1 Ringkasan berkas utama kode sumber proyek",
        ["Lokasi Berkas", "Fungsi Utama"],
        [
            ["docker-compose.yml", "Orkestrasi lima layanan (Kafka KRaft, MongoDB, Producer, PySpark, Streamlit) beserta batas memori"],
            ["docker/Dockerfile.*", "Definisi image ringan untuk Python Producer, PySpark dengan JAR Kafka, dan Streamlit Dashboard"],
            ["ingestion/producer.py", "Simulasi aliran 3 jenis data ke topik ecommerce_events disertai injeksi 3 pola fraud dan sinyal konversi"],
            ["processing/stream_fraud_detector.py", "PySpark Structured Streaming local[2] untuk deteksi fraud, aksi preskriptif, dan tulis Parquet terpartisi"],
            ["processing/batch_benchmark.py", "Benchmark 1 juta baris membandingkan sebelum dan sesudah optimasi partisi, shuffle partitions, dan cache"],
            ["storage/mongo_client.py", "Utilitas koneksi, indeks, penyimpanan, dan pembacaan empat koleksi MongoDB"],
            ["storage/parquet_reader.py", "Pembacaan arsip Parquet terpartisi dengan partition pruning berdasarkan event_date dan category"],
            ["dashboard/app.py", "Aplikasi Streamlit 4 tab untuk pemantauan real-time, panel aksi preskriptif, Parquet, dan benchmark"],
            ["scripts/run_benchmark.sh", "Skrip menjalankan benchmark Spark secara aman tanpa bentrok memori dengan proses streaming"],
            ["docs/evidence/*", "Bukti hasil benchmark JSON, log verifikasi VPS, dan 4 tangkapan layar langsung Streamlit"],
        ],
        [2.35, 3.9],
    )

    out_docx = os.path.join(BASE_DIR, "deliverables", "final", "Laporan_Akhir_BigData_Kelompok12.docx")
    os.makedirs(os.path.dirname(out_docx), exist_ok=True)
    doc.save(out_docx)
    print("DOCX SAVED:", out_docx)

    # validasi otomatis: cek aturan 1 titik per paragraf narasi dan semua run hitam
    body_errors = []
    color_errors = []
    for idx, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
        for r in p.runs:
            if r.font.color and r.font.color.rgb and r.font.color.rgb != BLACK:
                color_errors.append((idx, str(r.font.color.rgb), t[:60]))
        # cek paragraf body (yg panjangnya > 80 char, bukan heading/caption/cover)
        if len(t) > 80 and not t.startswith(("Tabel ", "Gambar ", "BAB ", "LAMPIRAN")):
            dots = t.count(".")
            if dots != 1 or not t.endswith("."):
                body_errors.append((idx, dots, t[:100]))

    print(f"AUDIT -> body_dot_violations={len(body_errors)}, non_black_runs={len(color_errors)}")
    for err in body_errors:
        print("  DOT_VIOLATION:", err)
    for err in color_errors:
        print("  COLOR_VIOLATION:", err)


if __name__ == "__main__":
    build_report()
