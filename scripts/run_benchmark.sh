#!/usr/bin/env bash
set -euo pipefail

# hentikan sementara container spark streaming biar benchmark 1 juta baris ga rebutan RAM di VPS
echo "[benchmark] menjeda sementara spark streaming biar RAM tetap lega"
docker compose stop spark || true

echo "[benchmark] menjalankan benchmark pyspark 1 juta baris (sebelum vs sesudah optimasi)"
docker compose run --rm --no-deps   -e BENCHMARK_ROWS="${BENCHMARK_ROWS:-1000000}"   spark   /opt/spark/bin/spark-submit   --master local[2]   --driver-memory 768m   /app/processing/batch_benchmark.py

echo "[benchmark] menyalakan kembali spark streaming"
docker compose start spark
echo "[benchmark] selesai, hasil tersimpan di docs/evidence/benchmark_results.json dan mongodb"
