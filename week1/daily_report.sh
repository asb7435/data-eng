#!/bin/bash
set -e          # 어느 한 줄이라도 실패하면 즉시 중단
set -u          # 선언하지 않은 변수를 쓰면 중단
log="${1:-access.log}"
today=$(date +%Y%m%d)
out="report_${today}.txt"
echo "===== $today 일일 리포트 =====" > "$out"
./count_errors.sh "$log" >> "$out"
echo "" >> "$out"
echo "[로그 레벨별 집계]" >> "$out"
cut -d ' ' -f 1 "$log" | sort | uniq -c | sort -k1,1rn -k2,2 >> "$out"
./backup.sh "$log" > /dev/null
echo "" >> "$out"
echo "백업 완료" >> "$out"
echo "리포트 생성: $out"
