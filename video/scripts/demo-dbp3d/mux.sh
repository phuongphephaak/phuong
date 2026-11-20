#!/bin/bash
# Ghép hình + tiếng; kéo dài tiếng (apad) cho khớp 33,2 s hình, mờ dần ở cuối.
ffmpeg -y -i video_only.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy \
  -af "apad,afade=t=out:st=32.2:d=1" -c:a aac -b:a 192k -t 33.2 \
  -movflags +faststart demo-dbp-3d.mp4
