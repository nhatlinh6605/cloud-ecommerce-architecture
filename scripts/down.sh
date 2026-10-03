#!/usr/bin/env bash
# Dừng cả hai kiến trúc (giữ dữ liệu). Thêm --purge để xóa volume (dọn dẹp hoàn toàn)
source "$(dirname "$0")/_common.sh"
FLAG=""; [ "${1:-}" = "--purge" ] && FLAG="-v"
$BASE down $FLAG 2>/dev/null || true
$IMPR down $FLAG 2>/dev/null || true
echo "Đã dừng${FLAG:+ và xóa volume}."
