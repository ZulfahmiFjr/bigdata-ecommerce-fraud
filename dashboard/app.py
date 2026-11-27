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

    with tab3:
        st.info("Tab eksplorasi parquet dalam pengerjaan")
    with tab4:
        st.info("Tab benchmark spark dalam pengerjaan")


if __name__ == "__main__":
    main()
