#!/usr/bin/env bash
source "$(dirname "$0")/_common.sh"
$BASE down 2>/dev/null || true
$IMPR up -d --build
wait_health http://localhost:8080
