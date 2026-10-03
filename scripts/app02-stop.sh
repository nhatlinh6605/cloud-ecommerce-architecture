#!/usr/bin/env bash
source "$(dirname "$0")/_common.sh"
$IMPR stop app02; echo "$(date -Is) APP02 STOPPED"
