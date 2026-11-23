import json, os, urllib.request, sys
KEY = os.environ["ELEVENLABS_API_KEY"]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aud")
L = {"c1": "Đại đoàn ba trăm lẻ tám, đại đoàn chủ lực đầu tiên của Quân đội nhân dân Việt Nam, bao vây Cốc Xá và điểm cao bốn trăm bảy mươi bảy.",
     "c2": "Trung đoàn hai trăm lẻ chín chặn phía bắc. Trung đoàn một trăm bảy mươi tư chặn đường ở Cốc Tồn, Khau Pia. Mọi lối thoát lần lượt bị bịt kín.",
     "c3": "Sáng sớm ngày sáu tháng mười, Trung đoàn ba mươi sáu mở cuộc tấn công vào Cốc Xá.",
     "c4": "Bị dồn vào lòng chảo, binh đoàn Lơ Pa-giơ vỡ trận. Đến trưa, gần như toàn bộ binh đoàn đã bị xoá sổ.",
     "c5": "Chỉ khoảng sáu trăm năm mươi người còn sống sót, tháo chạy lên điểm cao bốn trăm bảy mươi bảy, để tìm quân Sác-tông.",
     "c6": "Cuối cùng, hai đoàn quân cũng gặp nhau. Nhưng không phải để cứu nhau. Họ chỉ còn là những đơn vị tan tác, cùng mắc kẹt trong một vòng vây đang siết chặt.",
     "c7": "Ngày bảy tháng mười, Đại đoàn ba trăm lẻ tám tấn công dứt điểm. Binh đoàn Sác-tông bị tiêu diệt. Đại tá Sác-tông bị bắt sống.",
     "c8": "Ngày tám tháng mười, đến lượt Đại tá Lơ Pa-giơ cùng ban tham mưu bị bắt làm tù binh."}
for k, t in L.items():
    p = os.path.join(OUT, k + ".mp3")
    if os.path.exists(p): continue
    req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/47rM9DW5VmjOw23BVHWi?output_format=mp3_44100_128",
        data=json.dumps({"text": t, "model_id": "eleven_v3", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    open(p, "wb").write(urllib.request.urlopen(req, timeout=300).read()); print("ok", k, flush=True)
