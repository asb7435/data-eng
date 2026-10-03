#!/bin/bash
dir=$1
for f in $dir/*.log; do
  n=`grep -c ERROR $f`
  if [ $n -ge 1 ]; then
    echo $f
  fi
done
