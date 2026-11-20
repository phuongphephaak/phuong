#!/bin/bash
# mix narration + music + sfx for the 33.2s demo -> mix.wav
cd /tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/demo
A=/tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/dbp/aud
ffmpeg -y -loglevel error \
 -i aud/l1.mp3 -i aud/l2.mp3 -i aud/l3.mp3 -i aud/l4.mp3 -i aud/l5.mp3 -i aud/l6.mp3 \
 -ss 20 -t 34 -i /tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/doc10/aud/music_tension.mp3 \
 -i $A/jungle_night.mp3 -i $A/artillery_barrage.mp3 -i $A/howitzer_shot.mp3 -i $A/howitzer_shot.mp3 -i $A/mg_fire.mp3 -i /tmp/claude-0/-home-user-phuong/0c4d85f1-15c7-55c7-aaee-28eebc4ec7d5/scratchpad/pp/aud/cannon_burst.mp3 \
 -f lavfi -t 34 -i "anoisesrc=c=pink:a=0.5:r=48000" \
 -filter_complex "\
[0]adelay=300|300,volume=1.0[n1];[1]adelay=4100|4100[n2];[2]adelay=12900|12900[n3];[3]adelay=18900|18900[n4];[4]adelay=25000|25000[n5];[5]adelay=27900|27900[n6];\
[6]volume=0.22,afade=t=in:d=1.5,volume='if(between(t,18.6,24.6),0.6,1)':eval=frame,afade=t=out:st=31.6:d=1.6[mu];\
[7]volume=0.30,afade=t=in:d=1.5,afade=t=out:st=14:d=1,adelay=3600|3600[amb];\
[8]volume=0.75,afade=t=out:st=6:d=2,adelay=18600|18600[bar];[9]volume=0.9,adelay=18700|18700[h1];[10]volume=0.7,adelay=20100|20100[h2];\
[11]volume=0.28,afade=t=in:d=0.3,afade=t=out:st=2.4:d=0.6,adelay=24600|24600[mg];\
[12]volume=0.8,adelay=30650|30650[hit];\
[13]highpass=f=900,lowpass=f=4000,tremolo=f=24:d=0.7,volume=0.05,volume='if(lt(t,3.7)+between(t,24.5,27.7),1,0)':eval=frame[proj];\
[n1][n2][n3][n4][n5][n6]amix=inputs=6:normalize=0,asplit=2[nar][nar2];\
[mu][amb][bar][h1][h2][mg][hit][proj]amix=inputs=8:normalize=0[bed];\
[bed][nar]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[duck];\
[duck][nar2]amix=inputs=2:normalize=0,atrim=0:33.2,aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false[out]" \
 -map "[out]" -ar 48000 mix.wav
