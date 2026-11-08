#!/usr/bin/env bash
# FAIL-BASE-01: dừng APP01 (bản sao duy nhất) khi đang có tải, rồi bật lại. Ghi log có mốc thời gian.
# Điều kiện: kiến trúc cơ sở đang chạy (base-up.sh). Cùng tải và cùng mốc thời gian với FAIL-IMP-01 để so sánh.
source "$(dirname "$0")/_common.sh"
mkdir -p results; LOG=results/fail-base-01-$(date +%Y%m%d-%H%M%S).log
ev() { echo "$(date +%Y-%m-%dT%H:%M:%S%z) $*" | tee -a "$LOG"; }
code() { curl -s -o /dev/null -m 2 -w "%{http_code}" http://localhost:8080/health; }
command -v k6 >/dev/null || { echo "Cần cài k6"; exit 1; }

ev "START tải LOAD-NORMAL nền (120s)"
PROFILE=normal DURATION=120s BASE_URL=http://localhost:8080 k6 run load/load.js --summary-export "results/fail-base-01-k6.json" >> "$LOG" 2>&1 &
K6=$!
sleep 30; ev "EVENT dừng APP01"; $BASE stop app01 2>&1 | tee -a "$LOG"
sleep 30
ev "CHECK sau khi mất APP01 (000 = không kết nối được):"
for i in 1 2 3 4 5 6; do ev "HTTP $(code)"; done
ev "EVENT bật lại APP01"; $BASE start app01 2>&1 | tee -a "$LOG"
T=0; until [ "$(code)" = "200" ] || [ $T -ge 120 ]; do sleep 0.5; T=$((T+1)); done
if [ "$(code)" = "200" ]; then ev "APP01 NHAN LAI REQUEST"; else ev "TIMEOUT: APP01 chua phuc hoi"; fi
sleep 10
ev "CHECK sau khi phục hồi:"
for i in $(seq 1 8); do ev "HTTP $(code)"; done
wait $K6 || true
ev "END. Log: $LOG"
