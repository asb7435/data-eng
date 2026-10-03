#!/bin/bash
log="$1"
if [ ! -f "$log" ]; then
  echo "로그 파일을 찾을 수 없습니다: $log"
  exit 1
fi
total=$(wc -l < "$log" | tr -d " ")
errors=$(grep -c ERROR "$log")
echo "전체 라인: $total"
echo "에러 라인: $errors"
