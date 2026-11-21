#!/bin/bash
# Ghép hình + tiếng cho bản v2 (36 s)
ffmpeg -y -i video_only2.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 36 \
  -movflags +faststart demo-dbp-3d-v2.mp4
