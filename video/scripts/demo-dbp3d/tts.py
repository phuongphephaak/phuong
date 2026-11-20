import json, os, urllib.request
KEY = os.environ["ELEVENLABS_API_KEY"]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aud")
L = {"l1": "Chiều ngày mười ba tháng ba, năm một nghìn chín trăm năm mươi tư. Điện Biên Phủ, vùng núi Tây Bắc Việt Nam.",
     "l2": "Dưới đáy lòng chảo Điện Biên Phủ, quân Pháp dựng bốn mươi chín cứ điểm. Họ tin đây là một pháo đài không thể công phá.",
     "l3": "Nhưng trên những ngọn núi bao quanh, từng khẩu pháo của ta đã được kéo bằng tay vào trận địa.",
     "l4": "Mười bảy giờ năm phút, toàn bộ trận địa pháo đồng loạt khai hỏa. Mục tiêu đầu tiên: Him Lam.",
     "l5": "Chỉ sau một đêm, Him Lam thất thủ.",
     "l6": "Đánh chắc, tiến chắc. Năm mươi sáu ngày đêm, chỉ vừa mới bắt đầu."}
for k, t in L.items():
    p = os.path.join(OUT, k + ".mp3")
    if os.path.exists(p): continue
    req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/47rM9DW5VmjOw23BVHWi?output_format=mp3_44100_128",
        data=json.dumps({"text": t, "model_id": "eleven_v3", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    open(p, "wb").write(urllib.request.urlopen(req, timeout=300).read()); print("ok", k)
