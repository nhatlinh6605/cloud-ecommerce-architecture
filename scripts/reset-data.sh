#!/usr/bin/env bash
# Reset dữ liệu về trạng thái seed. Chạy nhiều lần cho kết quả giống nhau.
# Dùng: reset-data.sh [base|improved]
source "$(dirname "$0")/_common.sh"
C=$([ "${1:-base}" = improved ] && echo "$IMPR" || echo "$BASE")
$C exec -T db01 psql -U "$DB_USER" -d "$DB_NAME" < db/schema.sql
$C exec -T db01 psql -U "$DB_USER" -d "$DB_NAME" < db/seed.sql
echo "Đã reset dữ liệu seed (${1:-base})."
