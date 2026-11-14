"""Xuất kich-ban.md từ script_coc.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_coc import SCENES, PARTS
RATE, PAD = 3.4, 0.7
mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
t, part, out = 0.0, None, []
chars = sum(len(s.get("nar", "")) for s in SCENES); syl = sum(len(s.get("nar", "").split()) for s in SCENES)
for i, s in enumerate(SCENES, 1):
    if s["part"] != part:
        part = s["part"]; out += ["", f"## Phần {part} – {PARTS[part]}  *({mmss(t)})*", ""]
    line = f"**{i}.** "
    if s.get("cap"): line += f"`{' / '.join(s['cap'])}` "
    line += s.get("nar") or f"*(không lời – {s['vis'][1].lower()}, {s.get('hold', 0)} giây)*"
    out.append(line + "\n")
    t += max(len(s.get("nar", "").split()) / RATE + s.get("hold", 0) + PAD, 2.5)
head = ["# Kịch bản: CHIM CẮT SỐ 2 – Nguyễn Văn Cốc", "",
        f"- **Độ dài ước tính:** ~{mmss(t)} · {len(SCENES)} cảnh · {chars:,} ký tự lời dẫn ({syl:,} từ)".replace(",", "."),
        f"- **Credit ElevenLabs:** ~{chars:,} / ~116.000 còn lại".replace(",", "."),
        "- Chữ trong `khung` là chữ hiện trên màn hình (không đọc)."]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kich-ban.md"), "w").write("\n".join(head + out) + "\n")
print(mmss(t))
