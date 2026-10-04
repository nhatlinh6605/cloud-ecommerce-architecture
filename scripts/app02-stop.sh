#!/usr/bin/env bash
source "$(dirname "$0")/_common.sh"
$IMPR stop app02; echo "$(date +%Y-%m-%dT%H:%M:%S%z) APP02 STOPPED"
