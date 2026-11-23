#!/bin/bash
D=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/demo
B=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/tools/blender-4.2.3-linux-x64/blender
cd $D
for try in 1 2 3 4 5 6 7 8; do
  s=1; while [ -f frames2/f_$(printf %04d $s).jpg ] && [ $s -le 630 ]; do s=$((s+1)); done
  [ $s -gt 630 ] && break
  echo "resume from $s (try $try)"
  SAMPLES=12 $B -b -P scene2.py -- render $s 630 > render2_$try.log 2>&1
done
python3 compose.py $D/video_only2.mp4 > compose2.log 2>&1 || { echo COMPOSE_FAIL; exit 1; }
ffmpeg -y -loglevel error -i video_only2.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 36 demo-dbp-3d-v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 demo-dbp-3d-v2.mp4
