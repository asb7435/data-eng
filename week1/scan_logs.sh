#!/bin/bash
dir="${1:-logs}"        # 인자가 없으면 logs를 기본값으로
for f in "$dir"/*.log; do
  lines=$(wc -l < "$f" | tr -d " ")
  errors=$(grep -c ERROR "$f")
  echo "$f : 전체 ${lines}줄 · ERROR ${errors}건"
done
