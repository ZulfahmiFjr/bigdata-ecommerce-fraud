#!/usr/bin/env bash
set -euo pipefail

# cek kondisi container, pemakaian RAM, dan jumlah dokumen di mongodb
echo "=== STATUS CONTAINER ==="
docker compose ps
echo ""
echo "=== PENGGUNAAN RESOURCE CONTAINER ==="
docker stats --no-stream --format "table {{.Name}}	{{.CPUPerc}}	{{.MemUsage}}	{{.MemPerc}}"
echo ""
echo "=== MEMORI HOST VPS ==="
free -h
echo ""
echo "=== RINGKASAN MONGODB ==="
docker exec bdef-mongodb mongosh --quiet ecommerce_bigdata --eval '
  print("realtime_metrics:", db.realtime_metrics.countDocuments());
  print("fraud_alerts:", db.fraud_alerts.countDocuments());
  print("prescriptive_actions:", db.prescriptive_actions.countDocuments());
  print("benchmark_results:", db.benchmark_results.countDocuments());
'
