"""Xuất kich-ban.md từ script_midway.py, ước tính thời gian (giọng Tuấn Anh ≈ 3,4 âm tiết/giây)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script_midway import SCENES, PARTS, SPEAKERS, VEO_PROMPTS

RATE, PAD = 3.4, 0.7
VIS = {"archive": "🎞️ Tư liệu", "photo": "🖼️ Ảnh", "map": "🗺️ Bản đồ", "vfx": "💥 Mô phỏng",
       "veo": "🎬 Veo", "card": "🔤 Đồ họa"}
mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"

def dur(sc):
    d = len(sc.get("nar", "").split()) / RATE + sc.get("hold", 0) + PAD
    for _, line, _ in sc.get("radio", []):
        d += len(line.split()) * 0.42 + 1.2
    return max(d, 2.5)

t, rows, part, part_start, counts = 0.0, [], None, {}, {}
for i, sc in enumerate(SCENES, 1):
    if sc["part"] != part:
        part = sc["part"]; part_start[part] = t
        rows.append(f"| | **{mmss(t)}** | **PHẦN {part} – {PARTS[part].upper()}** | | |")
    kind, desc = sc["vis"]
    counts[kind] = counts.get(kind, 0) + dur(sc)
    vis = f"{VIS[kind]}: {desc}" + (f"<br>*Chữ: {' / '.join(sc['cap'])}*" if sc.get("cap") else "")
    text = [sc["nar"]] if sc.get("nar") else []
    for v, line, sub in sc.get("radio", []):
        text.append(f"📻 **{SPEAKERS[v]}:** “{line}”<br>*({sub})*")
    if sc.get("hold") and sc["id"] != "end":
        text.append(f"*(ngừng lời {sc['hold']} giây)*")
    rows.append(f"| {i} | {mmss(t)} | {vis} | {'<br><br>'.join(text) or '—'} | {sc.get('sfx', '')} |")
    t += dur(sc)
total = t
syl = sum(len(s.get("nar", "").split()) for s in SCENES)

out = [
 "# Kịch bản: SÁU PHÚT ĐỊNH MỆNH – Trận Midway 1942", "",
 f"- **Thời lượng ước tính:** ~{mmss(total)} ({len(SCENES)} cảnh, ~{syl} âm tiết lời dẫn, giọng Tuấn Anh ≈ 3,4 âm tiết/giây).",
 "- **Tiêu đề YouTube đề xuất:** *6 Phút Định Mệnh: Trận Midway – Khi Mỹ Hạ Gục 4 Tàu Sân Bay Nhật Trong Một Ngày* "
 "(đúng nội dung: 3 chiếc cháy trong 6 phút, chiếc thứ 4 trúng bom chiều cùng ngày; cả 4 chìm trong đêm 4 và sáng 5/6).",
 "- **Mô-típ lặp lại:** \"sáu phút\" (cảnh 7, 79–82, câu kết 100) và \"Họ tin rằng… Nhưng họ đã nhầm\" (cảnh 4, 22, 30).",
 "- **Câu hỏi giữ người xem nửa sau:** \"Nhưng trận chiến vẫn chưa kết thúc… Hiryu\" (cảnh 83, khoảng 80% video).",
 "- **Giờ trong phim:** giờ địa phương Midway. Thoại điện đài/bộ đàm là **tái hiện** theo nội dung bức điện được "
 "ghi trong sử liệu, xử lý âm thanh như video Coventry, có phụ đề tiếng Việt.", "",
 "## Phân bổ thời lượng", "", "| Phần | Bắt đầu | Độ dài |", "|---|---|---|"]
ps = sorted(part_start)
for k, p in enumerate(ps):
    end = part_start[ps[k + 1]] if k + 1 < len(ps) else total
    out.append(f"| {p}. {PARTS[p]} | {mmss(part_start[p])} | {mmss(end - part_start[p])} |")
out += ["", "**Tỷ lệ hình ảnh:** " + ", ".join(f"{VIS[k]} {round(100 * v / total)}%" for k, v in
        sorted(counts.items(), key=lambda x: -x[1])), "",
        "## Kịch bản chi tiết", "", "| # | Thời điểm | Hình ảnh | Lời dẫn / Thoại | Âm thanh |", "|---|---|---|---|---|"]
out += rows
out += ["", "## Danh sách clip Veo cần tạo (bạn tạo trong Gemini/Flow, tải lên Google Drive)", "",
        "Mỗi clip 8 giây, khung 16:9, **tắt âm thanh hoặc không cần âm thanh** (mình sẽ lồng tiếng). "
        "Đặt tên file theo mã, ví dụ `V01.mp4`. Nếu clip có chữ/logo lạ thì tạo lại.", ""]
for k, v in VEO_PROMPTS.items():
    used = [str(i) for i, s in enumerate(SCENES, 1) if s["vis"][0] == "veo" and s["vis"][1].startswith(k)]
    out += [f"**{k}** (cảnh {', '.join(used)})", "```", v, "```", ""]
out += ["## Nguồn tư liệu dự kiến (public domain)", "",
 "- Phim **\"The Battle of Midway\" (1942)**, John Ford, Hải quân Mỹ quay – tác phẩm của chính phủ Mỹ (Internet Archive, NARA).",
 "- Phim/ảnh Trân Châu Cảng, cuộc không kích Doolittle, Yorktown trúng bom và chìm – Hải quân Mỹ, "
 "Bộ Tư lệnh Lịch sử và Di sản Hải quân (NHHC), NARA.",
 "- Chân dung Nimitz, Spruance, Rochefort, Waldron, McClusky, Best, Gay: ảnh Hải quân Mỹ (public domain).",
 "- Chân dung Yamamoto, Nagumo, Yamaguchi, Tomonaga: ảnh Nhật trước 1957 (Wikimedia Commons ghi public domain) – kiểm tra từng file khi tải.",
 "- **Không dùng** cảnh từ phim \"Midway\" (1976, 2019) hay game.", "",
 "## Nguồn sự kiện", "",
 "- Gordon Prange, *Miracle at Midway* (1982); Jonathan Parshall & Anthony Tully, *Shattered Sword* (2005) – nguồn cho "
 "việc bác bỏ chuyện \"5 phút\" trong hồi ký của Fuchida Mitsuo.",
 "- NHHC: *Battle of Midway, 4–7 June 1942* (history.navy.mil).",
 "- Số liệu: Nhật mất 4 tàu sân bay, tuần dương hạm Mikuma, ~248 máy bay, ~3.057 người; Mỹ mất Yorktown, khu trục hạm "
 "Hammann, ~150 máy bay, 307 người. Phi đội Ngư lôi 8: 15 máy bay, 30 người, 1 người sống sót.", ""]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kich-ban.md"), "w", encoding="utf-8").write("\n".join(out))
print("total", mmss(total), "syl", syl)
