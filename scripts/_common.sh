#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "Thiếu .env — chạy: cp .env.example .env rồi điền giá trị"; exit 1; }
set -a; source .env; set +a
BASE="docker compose -f docker-compose.base.yml --env-file .env"
IMPR="docker compose -f docker-compose.improved.yml --env-file .env"
wait_health() { # $1 = URL
  for i in $(seq 1 40); do curl -fs "$1/health" >/dev/null && { echo "OK: $1"; return 0; }; sleep 3; done
  echo "Hết thời gian chờ $1"; return 1
}
