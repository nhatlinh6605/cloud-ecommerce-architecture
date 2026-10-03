#!/usr/bin/env bash
# Chạy 3 mức tải và lưu kết quả thô. Dùng: run-load.sh <baseline|improved> [số lần lặp=3]
source "$(dirname "$0")/_common.sh"
ARCH=${1:?baseline|improved}; REPS=${2:-3}
command -v k6 >/dev/null || { echo "Cần cài k6"; exit 1; }
mkdir -p results
for p in normal peak spike; do
  for r in $(seq 1 $REPS); do
    bash scripts/reset-data.sh $([ "$ARCH" = improved ] && echo improved || echo base) >/dev/null
    OUT=results/${ARCH}-${p}-run${r}
    echo "$(date -Is) $ARCH LOAD-${p^^} lần $r"
    PROFILE=$p BASE_URL=http://localhost:8080 k6 run load/load.js --summary-export $OUT.json 2>&1 | tee $OUT.log | tail -n 25
  done
done
