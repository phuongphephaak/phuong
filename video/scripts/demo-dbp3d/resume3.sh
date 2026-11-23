#!/bin/bash
# Dựng sa bàn v3 (tự chạy tiếp nếu Blender crash), rồi ghép video.
D=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/demo
B=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/tools/blender-4.2.3-linux-x64/blender
cd $D
[ -f labels3.json ] || $B -b -P scene3.py -- labels > labels3.log 2>&1
for try in $(seq 1 12); do
  s=1; while [ -f frames3/f_$(printf %04d $s).jpg ] && [ $s -le 630 ]; do s=$((s+1)); done
  [ $s -gt 630 ] && break
  echo "resume from $s (try $try) $(date +%T)"
  SAMPLES=8 $B -b -P scene3.py -- render $s 630 > render3_$try.log 2>&1
done
echo RENDER3_DONE $(date +%T)
