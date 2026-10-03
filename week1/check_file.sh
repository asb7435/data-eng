#!/bin/bash
target="$1"
if [ -f "$target" ]; then
  echo "$target 파일이 존재합니다."
else
  echo "$target 파일이 없습니다."
  exit 1
fi
