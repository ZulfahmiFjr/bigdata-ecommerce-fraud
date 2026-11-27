import json
import os
import time
import pandas as pd
import plotly.express as px
import streamlit as st
from storage.mongo_client import (
    get_mongo_db,
    fetch_recent_metrics,
    fetch_recent_alerts,
    fetch_prescriptive_actions,
    fetch_latest_benchmark,
)
from storage.parquet_reader import list_parquet_partitions, read_partitioned_parquet

st.set_page_config(
    page_title="Deteksi Fraud & Analitik E-Commerce Real-Time",
    page_icon="🛡️",
    layout="wide",
)

PARQUET_DIR = os.getenv("PARQUET_DIR", "/app/data/parquet/events")
BENCHMARK_FILE = os.getenv("BENCHMARK_FILE", "/app/docs/evidence/benchmark_results.json")


@st.cache_resource
def load_db():
    return get_mongo_db()


def load_benchmark_data(db):
    # ambil hasil benchmark dari mongodb dulu, kalo belum ada coba baca file JSON lokal
    doc = None
    try:
        doc = fetch_latest_benchmark(db)
    except Exception:
        doc = None
    if doc is None and os.path.isfile(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
    return doc


def format_idr(val):
    num = float(val or 0)
    if num >= 1_000_000_000:
        return f"Rp{num / 1_000_000_000:.2f} M".replace(".", ",")
    if num >= 1_000_000:
        return f"Rp{num / 1_000_000:.1f} Jt".replace(".", ",")
    return f"Rp{int(num):,}".replace(",", ".")


def main():
    st.title("Sistem Deteksi Fraud & Analitik E-Commerce Real-Time")
    st.caption("Kelompok 12 — Teknologi Big Data | Kafka KRaft + PySpark local[2] + MongoDB + Partitioned Parquet")

    # sidebar buat kontrol filter sama auto-refresh biar dashboard interaktif
    with st.sidebar:
        st.header("Pengaturan Tampilan")
        auto_refresh = st.checkbox("Auto-refresh tiap 10 detik", value=False)
        if st.button("Muat Ulang Data"):
            st.rerun()

        st.divider()
        st.subheader("Filter Alert Fraud")
        fraud_filter = st.selectbox("Jenis Fraud", ["Semua", "Transaksi Kilat", "Nominal Melonjak", "Ulasan Penipuan"])
        cat_filter = st.selectbox("Kategori Produk", ["Semua", "elektronik", "fashion", "gadget", "rumah_tangga", "kecantikan"])
        prio_filter = st.selectbox("Prioritas Aksi Preskriptif", ["Semua", "Kritis", "Tinggi", "Sedang"])

    try:
        db = load_db()
        metrics = fetch_recent_metrics(db, limit=60)
        alerts = fetch_recent_alerts(db, limit=120, fraud_type=fraud_filter, category=cat_filter)
        actions = fetch_prescriptive_actions(db, limit=80, priority=prio_filter)
        # pastikan contoh rekomendasi optimasi konversi ikut ditarik pas filter semua aktif
        if prio_filter == "Semua" and not any(a.get("action_category") == "Optimasi Konversi" for a in actions):
            conv_doc = db.prescriptive_actions.find_one({"action_category": "Optimasi Konversi"}, {"_id": 0}, sort=[("created_at", -1)])
            if conv_doc:
                actions.append(conv_doc)
        benchmark = load_benchmark_data(db)
    except Exception as err:
        st.error(f"Gagal terhubung ke MongoDB: {err}")
        return

    # hitung ringkasan KPI utama dari batch real-time
    total_events = sum(m.get("total_events", 0) for m in metrics)
    total_gmv = sum(m.get("total_gmv", 0) for m in metrics)
    total_fraud = sum(m.get("fraud_count", 0) for m in metrics)
    anomaly_pct = (total_fraud / total_events * 100.0) if total_events > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Event Real-Time", f"{total_events:,}")
    c2.metric("Total Nilai Transaksi (GMV)", format_idr(total_gmv))
    c3.metric("Alert Fraud Terdeteksi", f"{total_fraud:,}")
    c4.metric("Rasio Anomali", f"{anomaly_pct:.2f}%")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Monitoring Real-Time & Fraud",
        "Rekomendasi Aksi Preskriptif",
        "Data Historis (Parquet Partisi)",
        "Bukti Optimasi Spark (Benchmark)",
    ])

    # tab 1 grafik aktivitas streaming sama tabel detail alert fraud
    with tab1:
        if not metrics:
            st.info("Menunggu data streaming pertama dari Kafka & PySpark (sekitar 10-20 detik)...")
        else:
            mdf = pd.DataFrame(metrics)
            mdf["waktu"] = pd.to_datetime(mdf["recorded_at"]).dt.strftime("%H:%M:%S")

            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("Tren Event Masuk vs Deteksi Fraud per Batch")
                fig_trend = px.line(
                    mdf,
                    x="waktu",
                    y=["total_events", "total_checkouts", "fraud_count"],
                    markers=True,
                    labels={"value": "Jumlah", "waktu": "Waktu (UTC)", "variable": "Metrik"},
                    color_discrete_sequence=["#1E3A5F", "#0F766E", "#DC2626"],
                )
                fig_trend.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_r:
                st.subheader("Distribusi Pola Fraud")
                if alerts:
                    adf_pie = pd.DataFrame(alerts)
                    counts = adf_pie["fraud_type"].value_counts().reset_index()
                    counts.columns = ["Pola Fraud", "Jumlah"]
                    fig_pie = px.bar(
                        counts,
                        x="Pola Fraud",
                        y="Jumlah",
                        color="Pola Fraud",
                        color_discrete_sequence=["#DC2626", "#D97706", "#1E3A5F"],
                    )
                    fig_pie.update_layout(height=340, showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Belum ada alert fraud sesuai filter.")

            st.subheader("Daftar Alert Fraud Terbaru")
            if alerts:
                adf = pd.DataFrame(alerts)
                cols_show = [c for c in ["detected_at", "fraud_type", "risk_score", "user_id", "merchant_id", "category", "amount_idr", "reason"] if c in adf.columns]
                st.dataframe(adf[cols_show], use_container_width=True, height=320)
            else:
                st.info("Belum ada alert fraud yang tercatat.")

    # tab 2 panel rekomendasi aksi preskriptif yg langsung bisa dipakai tim operasional
    with tab2:
        st.subheader("Panel Rekomendasi Aksi Preskriptif")
        st.write("Sistem menerjemahkan hasil deteksi fraud dan rasio konversi clickstream menjadi saran tindakan langsung untuk tim operasional dan pemasaran.")
        if not actions:
            st.info("Belum ada rekomendasi aksi yang terbentuk.")
        else:
            # tampilkan perwakilan terbaru dari tiap kategori aksi dulu biar semua tipe rekomendasi langsung kebaca
            featured = []
            seen_cats = set()
            for act in actions:
                acat = act.get("action_category", "")
                if acat not in seen_cats:
                    featured.append(act)
                    seen_cats.add(acat)
            ordered_actions = featured + [a for a in actions if a not in featured]
            for act in ordered_actions[:15]:
                prio = act.get("priority", "Sedang")
                title_line = f"[{prio.upper()}] {act.get('action_category', 'Aksi')} — {act.get('target', '-')}"
                body = f"**Pemicu:** {act.get('trigger', '-')}  \n**Rekomendasi Aksi:** {act.get('recommendation', '-')}"
                if prio == "Kritis":
                    st.error(f"**{title_line}**  \n{body}")
                elif prio == "Tinggi":
                    st.warning(f"**{title_line}**  \n{body}")
                else:
                    st.info(f"**{title_line}**  \n{body}")

    # tab 3 eksplorasi arsip parquet terpartisi event_date & category
    with tab3:
        st.subheader("Eksplorasi Arsip Historis Parquet Terpartisi")
        try:
            dates, cats = list_parquet_partitions(PARQUET_DIR)
            if not dates:
                st.info("Folder Parquet terpartisi masih menunggu batch pertama dari Spark.")
            else:
                p1, p2 = st.columns(2)
                sel_date = p1.selectbox("Filter Partisi event_date", ["Semua"] + dates)
                sel_cat = p2.selectbox("Filter Partisi category", ["Semua"] + cats)

                pdf, total_files = read_partitioned_parquet(PARQUET_DIR, event_date=sel_date, category=sel_cat, max_rows=300)
                st.caption(f"Struktur partisi aktif: event_date ({len(dates)} tanggal) x category ({len(cats)} kategori) | File partisi cocok: **{total_files:,} file Parquet** | Sampel ditampilkan: **{len(pdf):,} baris**")
                if not pdf.empty:
                    if "category" in pdf.columns and "amount_idr" in pdf.columns:
                        agg = pdf.groupby("category", as_index=False)["amount_idr"].sum()
                        fig_cat = px.bar(agg, x="category", y="amount_idr", title="Total Nilai Transaksi per Kategori (Sampel Partisi Parquet)", color_discrete_sequence=["#0F766E"])
                        fig_cat.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
                        st.plotly_chart(fig_cat, use_container_width=True)
                    st.dataframe(pdf.head(100), use_container_width=True, height=280)
        except Exception as err:
            st.warning(f"Gagal membaca sampel Parquet: {err}")

    # tab 4 bukti nyata optimasi spark (sebelum vs sesudah partisi + caching)
    with tab4:
        st.subheader("Bukti Performa Optimasi Apache Spark")
        if not benchmark:
            st.info("Belum ada data benchmark. Jalankan bash scripts/run_benchmark.sh untuk menguji perbandingan 1 juta baris.")
        else:
            base = benchmark["baseline"]
            opt = benchmark["optimized"]

            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Jumlah Data Uji", f"{benchmark['dataset_rows']:,} baris")
            b2.metric("Waktu Baseline", f"{base['query_time_sec']} dtk")
            b3.metric("Waktu Optimized", f"{opt['query_time_sec']} dtk", delta=f"-{benchmark['time_saved_pct']}%")
            b4.metric("Percepatan (Speedup)", f"{benchmark['speedup_x']}x lebih cepat")

            col_t, col_s = st.columns(2)
            with col_t:
                time_df = pd.DataFrame([
                    {"Skenario": "Sebelum Optimasi\n(JSON, shuffle=200)", "Waktu (detik)": base["query_time_sec"]},
                    {"Skenario": "Sesudah Optimasi\n(Parquet Partisi, shuffle=4, cache)", "Waktu (detik)": opt["query_time_sec"]},
                ])
                fig_t = px.bar(
                    time_df,
                    x="Skenario",
                    y="Waktu (detik)",
                    text="Waktu (detik)",
                    title="Perbandingan Waktu Eksekusi Query",
                    color="Skenario",
                    color_discrete_sequence=["#DC2626", "#0F766E"],
                )
                fig_t.update_layout(showlegend=False, height=340)
                st.plotly_chart(fig_t, use_container_width=True)

            with col_s:
                size_df = pd.DataFrame([
                    {"Format": "Raw JSON Tanpa Partisi", "Ukuran Disk (MB)": base["storage_mb"]},
                    {"Format": "Parquet Snappy Terpartisi", "Ukuran Disk (MB)": opt["storage_mb"]},
                ])
                fig_s = px.bar(
                    size_df,
                    x="Format",
                    y="Ukuran Disk (MB)",
                    text="Ukuran Disk (MB)",
                    title=f"Perbandingan Ukuran Penyimpanan (Hemat {benchmark['storage_saved_pct']}%)",
                    color="Format",
                    color_discrete_sequence=["#D97706", "#1E3A5F"],
                )
                fig_s.update_layout(showlegend=False, height=340)
                st.plotly_chart(fig_s, use_container_width=True)

            st.caption(f"Query uji: {benchmark['filter_query']} | Waktu uji: {benchmark['run_at']}")

    if auto_refresh:
        time.sleep(10)
        st.rerun()


if __name__ == "__main__":
    main()
