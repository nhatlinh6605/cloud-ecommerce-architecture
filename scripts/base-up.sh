#!/usr/bin/env bash
source "$(dirname "$0")/_common.sh"
$IMPR down 2>/dev/null || true      # tránh trùng cổng 8080
$BASE up -d --build
wait_health http://localhost:8080
