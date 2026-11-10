# What If You Could See Everyone's Lie Count? (60s pilot)

Flat 2D animated "What if…" story, rendered entirely in code. Original characters, story, music and SFX.

- `engine.py`: drawing primitives, characters, lie-counter label, speech bubbles, captions
- `scenes.py`: backgrounds (street, kitchen, living room, notepad, title card)
- `story.py`: shot list (timing, camera, dialogue, SFX cues)
- `audio.py`: synthesized lo-fi music + SFX matched to the shot list
- `render.py`: renders frames into ffmpeg

```bash
pip install pycairo numpy
python3 audio.py audio.wav
python3 render.py video silent.mp4        # or: python3 render.py preview <dir>
ffmpeg -i silent.mp4 -i audio.wav -c:v copy -c:a aac -shortest out/lie-count-60s.mp4
```

No voiceover yet: the story is carried by speech bubbles and captions.
