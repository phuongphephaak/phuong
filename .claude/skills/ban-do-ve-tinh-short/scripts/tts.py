import json, os, urllib.request
KEY = os.environ["ELEVENLABS_API_KEY"]; OUT = os.path.join(os.path.abspath(os.environ.get("WORK", os.getcwd())), "aud"); os.makedirs(OUT, exist_ok=True)
LV = {"l1": "Dòng sông nhỏ này từng chia đôi đất nước Việt Nam.",
     "l2": "Đây là sông Bến Hải.",
     "l3": "Dòng sông chảy qua tỉnh Quảng Trị, miền Trung Việt Nam.",
     "l4": "Bờ bắc là miền Bắc,",
     "l5": "còn bờ nam là miền Nam.",
     "l6": "Sông Bến Hải đổ ra Biển Đông tại cửa Tùng.",
     "l7": "Năm 1954, Hiệp định Giơ-ne-vơ lấy dòng sông này làm giới tuyến quân sự tạm thời.",
     "l8": "Một dòng sông nhỏ, nhưng là vết cắt chia đôi đất nước suốt hai mươi mốt năm."}
# Bản tiếng Anh: viết tên riêng không dấu để giọng đọc phát âm ổn ("Ben Hai", "Quang Tri", "Cua Tung")
LE = {"l1": "This small river once split Vietnam in two.",
      "l2": "This is the Ben Hai River.",
      "l3": "It flows through Quang Tri, in central Vietnam.",
      "l4": "To the north, North Vietnam...",
      "l5": "...to the south, South Vietnam.",
      "l6": "The river meets the East Sea at Cua Tung.",
      "l7": "In 1954, the Geneva Accords made it a temporary military border.",
      "l8": "A small river that split a nation for twenty-one years."}
VLANG = os.environ.get("VLANG", "vi")
L = LE if VLANG == "en" else LV
# giọng: vi = giọng Việt của kênh; en = "Daniel" (giọng Anh, trầm, kiểu người dẫn phim tài liệu). Đổi bằng VOICE=<id>
VOICE = os.environ.get("VOICE", "onwK4e9ZLuTAKqWW03F9" if VLANG == "en" else "47rM9DW5VmjOw23BVHWi")
for k, t in L.items():
    p = os.path.join(OUT, k + ".mp3")
    if os.path.exists(p): continue
    req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/" + VOICE + "?output_format=mp3_44100_128",
        data=json.dumps({"text": t, "model_id": "eleven_v3", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    open(p, "wb").write(urllib.request.urlopen(req, timeout=300).read()); print("ok", k, flush=True)
