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

    st.info("Kerangka KPI real-time siap, tab grafik menyusul")


if __name__ == "__main__":
    main()
