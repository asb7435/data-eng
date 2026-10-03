#!/bin/bash
src="$1"
if [ ! -e "$src" ]; then
  echo "백업할 대상이 없습니다: $src"
  exit 1
fi
dest="backup_$(date +%Y%m%d)"
mkdir -p "$dest"
cp -r "$src" "$dest"/
echo "$src -> $dest 백업 완료"
