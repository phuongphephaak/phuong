# Công thức thumbnail kiểu Trạm Cuối (phân tích 30 video gần nhất, 11/2026)

Ảnh so sánh: [nhóm nhiều view nhất](tram-cuoi-thumb-top.jpg) · [nhóm ít view nhất](tram-cuoi-thumb-bottom.jpg)

## Khung cố định (video nào cũng có – không phải yếu tố tạo khác biệt)
- **1 dòng chữ, 2–4 từ**, chữ in hoa rất đậm, hơi hẹp, chiếm gần hết chiều ngang, nằm trên cùng (đôi khi dưới cùng).
- **Trắng + vàng (#FFE600)**: phần đầu trắng, từ khoá quan trọng màu vàng. Viền đen dày + bóng đổ.
- Dải đen mờ phía sau chữ để chữ luôn đọc được.
- **1 ảnh chính** siêu thực (ảnh AI), màu rất rực, tương phản mạnh, chủ thể to ở giữa, chụp đúng **khoảnh khắc đang xảy ra** (bánh xe toé lửa, lũ đang ập, máy bay đang cháy).
- Không logo kênh, không chữ nhỏ. Chú thích phụ chỉ khi cần: ô vàng/đỏ có tên, ghim cờ, mũi tên, vòng tròn đỏ.

## Nhóm nhiều view (500K – 2,5 triệu)
| View | Chữ |
|---|---|
| 2,5M | CẬN KỀ THẢM HOẠ... |
| 1,5M | 600 KILOGRAM MA TUÝ |
| 1,5M | ĐÁNH ÚP PHI ĐỘI MỸ (MiG Việt Nam bắn rơi F-4, ghim cờ Mỹ trên từng chiếc) |
| 1,0M | 3000 NGƯỜI TỬ NẠN |
| 1,0M | TỪ ĐÁM MÂY ĐI RA... (MiG-17 cờ Việt Nam) |
| 682K | ĐẠP NHẦM CHÂN PHANH? |
| 557K | ĐỐI MẶT SIÊU BÃO... |
| 508K | 10 TẤN TIỀN GIẤY |

## Nhóm ít view (84K – 300K)
TAI NẠN TRÊN KHÔNG · MÁY BAY ĐÓNG BĂNG · KHÔNG THỂ HẠ CÁNH · THOÁT CHẾT GANG TẤC · THẢM HOẠ NGỚ NGẨN · CÁI KẾT KINH NGƯỜI · MÁY BAY MUI TRẦN · VIETJET KHỦNG HOẢNG

## Khác biệt rút ra
1. **Gắn với Việt Nam** → view gấp 3–5 lần: Vietnam Airlines, phi công Việt Nam, MiG mang sao vàng. Nhóm ít view gần như toàn hãng/sự kiện nước ngoài.
2. **Chữ cụ thể, có con số hoặc hành động rõ** ("600 KILOGRAM", "3000 NGƯỜI", "10 TẤN", "ĐÁNH ÚP PHI ĐỘI MỸ") thắng chữ chung chung ("TAI NẠN TRÊN KHÔNG", "KHÔNG THỂ HẠ CÁNH", "CÁI KẾT KINH NGƯỜI").
3. **Bỏ lửng / câu hỏi** ("...", "?") để kích tò mò – nhưng chỉ hiệu quả khi đi kèm chủ thể rõ.
4. **Phân phe bằng ký hiệu**: thumbnail quân sự tốt nhất dùng ghim cờ trên từng máy bay → nhìn 1 giây hiểu "ai đánh ai, bao nhiêu chiếc".
5. **Ảnh có chủ thể to, đang hành động**. Ảnh tĩnh, chủ thể đứng yên (máy bay bị xích, máy bay đỗ) ít view.

Lưu ý: chỉ xem được 30 video gần nhất; lượt xem còn phụ thuộc đề tài, không chỉ thumbnail.

## Áp dụng cho Mật Lệnh
- Script: `video/scripts/midway/make_thumb_tc.py` (font Barlow Condensed ExtraBold, `video/brand/fonts/`).
- Đề tài chiến tranh Việt Nam rất hợp quy luật #1 → nên ưu tiên.
