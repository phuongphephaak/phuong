#!/bin/bash
# mix narration + music + sfx cho bản demo 36s (mở đầu địa cầu 6.4s) -> mix.wav
cd /tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/demo
S=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad
A=$S/dbp/aud
ffmpeg -y -loglevel error \
 -i aud/l1.mp3 -i aud/l2.mp3 -i aud/l3.mp3 -i aud/l4.mp3 -i aud/l5.mp3 -i aud/l6.mp3 \
 -ss 20 -t 37 -i $S/doc10/aud/music_tension.mp3 \
 -i $A/jungle_night.mp3 -i $A/artillery_barrage.mp3 -i $A/howitzer_shot.mp3 -i $A/howitzer_shot.mp3 -i $A/mg_fire.mp3 -i $S/pp/aud/cannon_burst.mp3 \
 -i $S/audio/wind.mp3 \
 -filter_complex "\
[0]adelay=500|500[n1];[1]adelay=6900|6900[n2];[2]adelay=15700|15700[n3];[3]adelay=21700|21700[n4];[4]adelay=27800|27800[n5];[5]adelay=30700|30700[n6];\
[6]volume=0.22,afade=t=in:d=1.5,volume='if(between(t,21.4,27.4),0.6,1)':eval=frame,afade=t=out:st=34.4:d=1.6[mu];\
[7]volume=0.30,afade=t=in:d=1.5,afade=t=out:st=14:d=1,adelay=6400|6400[amb];\
[8]volume=0.75,afade=t=out:st=6:d=2,adelay=21400|21400[bar];[9]volume=0.9,adelay=21500|21500[h1];[10]volume=0.7,adelay=22900|22900[h2];\
[11]volume=0.28,afade=t=in:d=0.3,afade=t=out:st=2.4:d=0.6,adelay=27400|27400[mg];\
[12]volume=0.8,adelay=33450|33450[hit];\
[13]atrim=0:6.8,volume=0.35,afade=t=in:d=1.2,afade=t=out:st=5.4:d=1.2[wind];\
[n1][n2][n3][n4][n5][n6]amix=inputs=6:normalize=0,asplit=2[nar][nar2];\
[mu][amb][bar][h1][h2][mg][hit][wind]amix=inputs=8:normalize=0[bed];\
[bed][nar]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[duck];\
[duck][nar2]amix=inputs=2:normalize=0,apad,atrim=0:36,aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false[out]" \
 -map "[out]" -ar 48000 mix.wav
