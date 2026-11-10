"""Write the human-readable script (kich-ban.md) from script_data.py + timeline.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_data import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
tl = {s["id"]: s for s in json.load(open(os.path.join(HERE, "timeline.json")))["scenes"]}
VIS = {"photo": "Ảnh tư liệu", "map": "Bản đồ động", "vfx": "Mô phỏng", "card": "Màn hình chữ", "credits": "Nguồn", "clip": "Mô phỏng (mở đầu)"}
VFX = {"pov": "góc nhìn buồng lái A-4", "radar": "phòng tác chiến / màn radar", "fleet": "tàu trên biển",
       "seadart": "Coventry phóng Sea Dart", "raid": "không kích ở San Carlos", "bounce": "bom nảy trúng Broadsword",
       "aftermath": "Coventry bốc cháy", "sink": "Coventry nghiêng, lật và chìm", "rescue": "cứu hộ, bè cứu sinh, trực thăng",
       "calm": "mặt biển lặng", "approach": "A-4 lao tới sát mặt biển", "attack": "A-4 lao qua Coventry, thả bom",
       "impact": "bom nổ trên thân tàu", "atlantic": "hành trình hạm đội", "region": "khu vực Falkland",
       "sancarlos": "eo San Carlos", "picket": "vị trí chốt chặn", "geometry": "sơ đồ đường bắn Sea Wolf",
       "end": "kết thúc chiến tranh"}
SPK = {"pilot1": "Phi công A-4 (trưởng biên đội)", "pilot2": "Phi công A-4 (số 2)", "ops": "Coventry – phòng tác chiến",
       "capt": "Chỉ huy (Coventry/Broadsword)"}
mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
out = ["# HMS Coventry – Ngày cuối cùng (25/5/1982)", "",
       f"Kịch bản phim tài liệu khoảng {round(json.load(open(os.path.join(HERE, 'timeline.json')))['total'] / 60, 1)} phút. "
       "Lời dẫn tiếng Việt; hội thoại bộ đàm bằng tiếng Anh và tiếng Tây Ban Nha có phụ đề tiếng Việt và được xử lý "
       "âm thanh như qua bộ đàm. Lời thoại bộ đàm là **tái hiện minh họa**, không phải ghi âm gốc.", "",
       "| # | Thời điểm | Hình ảnh | Lời dẫn / Thoại |", "|---|---|---|---|"]
for i, sc in enumerate(SCENES, 1):
    kind, p = sc["vis"]
    vis = VIS[kind] + (f": {VFX.get(p.get('kind'), p.get('kind'))}" if kind in ("vfx", "map") else
                       f": {p.get('key', '')}" if kind == "photo" else
                       f": cắt từ cảnh {p['src']}" if kind == "clip" else "")
    if sc.get("cap"):
        vis += f"<br>*Chữ: {' – '.join(sc['cap'])}*"
    text = []
    if sc.get("nar"):
        text.append(sc["nar"])
    for v, line, sub in sc.get("radio", []):
        text.append(f"📻 **{SPK[v]}:** “{line}”<br>*({sub})*")
    out.append(f"| {i} | {mmss(tl[sc['id']]['start'])} | {vis} | {'<br><br>'.join(text) or '—'} |")
out += ["", "## Nguồn sự kiện", "- Wikipedia: *HMS Coventry (D118)*, *Falklands War*.",
        "- Số liệu: 3 quả bom trúng (2 quả nổ), 19 người hy sinh, tàu lật trong vòng 20 phút; Broadsword cứu 170 người; "
        "thương vong toàn cuộc chiến 649 / 255 / 3.", ""]
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
print("wrote", sys.argv[1])
