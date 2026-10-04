#!/usr/bin/env bash
# FAIL-IMP-01: dừng APP02 khi đang có tải, rồi bật lại. Ghi log sự kiện có mốc thời gian.
# Điều kiện: kiến trúc cải tiến đang chạy (improved-up.sh). Thoại đo recovery time từ mốc trong log.
source "$(dirname "$0")/_common.sh"
mkdir -p results; LOG=results/fail-imp-01-$(date +%Y%m%d-%H%M%S).log
ev() { echo "$(date +%Y-%m-%dT%H:%M:%S%z) $*" | tee -a "$LOG"; }
command -v k6 >/dev/null || { echo "Cần cài k6"; exit 1; }

ev "START tải LOAD-NORMAL nền (120s)"
PROFILE=normal DURATION=120s BASE_URL=http://localhost:8080 k6 run load/load.js --summary-export "results/fail-imp-01-k6.json" >> "$LOG" 2>&1 &
K6=$!
sleep 30;  ev "EVENT dừng APP02"; bash scripts/app02-stop.sh | tee -a "$LOG"
sleep 30
ev "CHECK phân phối sau khi mất APP02:"
for i in 1 2 3 4 5 6; do curl -si localhost:8080/health | grep -iE "^HTTP|x-instance" | tr '\r\n' ' ' | tee -a "$LOG"; echo | tee -a "$LOG"; done
ev "EVENT bật lại APP02"; bash scripts/app02-start.sh | tee -a "$LOG"
until curl -si localhost:8080/health | grep -qi "x-instance: app02"; do sleep 0.5; done
ev "APP02 NHAN LAI REQUEST"
sleep 10
ev "CHECK sau khi phục hồi:"
for i in $(seq 1 8); do curl -si localhost:8080/health | grep -i "x-instance" | tr -d '\r' | tee -a "$LOG"; done
wait $K6 || true
ev "END. Log: $LOG"
