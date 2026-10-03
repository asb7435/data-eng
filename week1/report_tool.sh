#!/bin/bash
set -euo pipefail

usage() {
  echo "사용법: $0 [summary|detail|help] [폴더]"
}

count_errors() {
  local file="$1"
  grep -c ERROR "$file" || true
}

mode="${1:-summary}"
dir="${2:-logs}"

case "$mode" in
  summary)
    total=0
    for f in "$dir"/*.log; do
      total=$(( total + $(count_errors "$f") ))
    done
    echo "ERROR 합계: ${total}건"
    ;;
  detail)                       # ← 이번에 더한 갈래
    for f in "$dir"/*.log; do
      echo "[$f]"
      while read -r line; do
        case "$line" in
          ERROR*) echo "   $line" ;;
        esac
      done < "$f"
    done
    ;;
  help)
    usage
    ;;
  *)
    echo "모르는 모드: $mode"
    usage
    exit 2
    ;;
esac
