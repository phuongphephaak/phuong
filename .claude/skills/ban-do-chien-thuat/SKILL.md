---
name: ban-do-chien-thuat
description: Dựng cảnh bản đồ chiến thuật 2.5D nhìn từ trên xuống (phong cách Epic History "Waterloo") cho kênh Mật Lệnh. Gồm địa hình đồi đổ bóng, ruộng, rừng, làng; bóng mây trôi; quân là các thanh tiểu đoàn có sọc; cờ hiệu gợn sóng có biển tên và chân dung tướng; mũi tên vàng mọc dần; vòng tròn vàng tự vẽ; khói, đất cày xới; đồng hồ giờ; máy quay trôi và phóng to. Dùng khi người dùng muốn cảnh mô phỏng diễn biến trận đánh, bản đồ chiến thuật, di chuyển quân trên bản đồ, mũi tên tấn công, hoặc nhắc đến "kiểu Waterloo" hay "bản đồ chiến thuật".
---

# Bản đồ chiến thuật 2.5D (kiểu Waterloo)

Bộ công cụ tự dựng toàn bộ: không dùng hình hay âm thanh nào từ video của kênh khác, chỉ học phong cách. Chân dung tướng lấy tranh phạm vi công cộng trên Wikimedia Commons (kiểm tra `LicenseShortName`).

Chạy hoàn toàn trên CPU bằng Python, numpy, PIL và scipy, không cần Blender. Dựng 24 giây (720 khung) mất khoảng 5–10 phút với 4 nhân.

## Các file

| File | Việc |
|---|---|
| `scripts/tactical_map.py` | Tạo bản đồ `map_full.png` (6144×4096, 1 px = 1 m) và `geo.json`. |
| `scripts/tactical_anim.py` | Dựng khung hình: `test F F ...` ra `test/`, `render [s e]` ra `frames/` với 4 tiến trình. |
| `scripts/tactical_audio.py` | Tổng hợp âm thanh `audio.wav`: nhạc trầm, trống, pháo, súng hỏa mai, vó ngựa, tiếng lướt. |
| `assets/fonts/` | Oswald 700 (đồng hồ), Barlow Condensed 700 (biển tên), Cormorant SC 700 (địa danh). Tất cả đều giấy phép OFL. |
| `assets/example-img/` | Chân dung mẫu (Wellington, Napoléon, d'Erlon, đều phạm vi công cộng). |
| `reference/style-notes.md` | Ghi chú phong cách đã phân tích từ video mẫu, kèm thông số và bài học kỹ thuật. **Đọc trước khi chỉnh.** |

Mọi script đọc và ghi trong thư mục `WORK` (mặc định là thư mục hiện tại). Chân dung đặt ở `WORK/img/<tên>.jpg`.

## Quy trình

1. **Nghiên cứu trận đánh.** Xác định:
   - địa hình: sống núi, sông suối, làng, đường;
   - bố trí quân hai bên theo từng mốc giờ;
   - các mũi tấn công.

   Chọn 1–3 diễn biến chính cho mỗi đoạn 20–30 giây.
2. **Sửa dữ liệu địa lý** ở đầu `tactical_map.py`:
   - `ROADS`, `STREAMS`, `VILLAGES` (tên, vị trí, số nhà, bán kính);
   - `RIDGE1` và `RIDGE2` (đường sống núi tạo độ cao);
   - các vùng rừng trong khối `wgt` (cx, cy, rx, ry, trọng số).

   Toạ độ tính bằng mét, gốc ở góc trên trái, trục y hướng xuống (về phía nam).
3. **Chạy** `WORK=<dir> python3 tactical_map.py`, mất khoảng 65 giây. Xem `map_prev.jpg`.
4. **Sửa kịch bản** trong `tactical_anim.py`:
   - `CAM`: các mốc (t, cx, cy, viewW mét, yaw độ, tilt độ), nội suy Catmull-Rom nên máy quay trôi liên tục;
   - `build_oob()`: quân là `Unit(kind, [(t, x, y, heading, alpha), ...])` và cờ là `dict(kind, label, keys=[(t, x, y), ...])`;
   - `ARROWS`: điểm (2 điểm cho mũi tên thẳng, nhiều điểm cho mũi tên cong), độ rộng `w` (mét), mốc `t=(bắt đầu mọc, mọc xong, bắt đầu mờ, tắt hẳn)`;
   - `RINGS`, `CLOCK`, `LABELS`, `smoke_events()` và `CHURN` (vùng đất chuyển nâu).
5. **Kiểm tra khung hình** bằng `python3 tactical_anim.py test 60 330 600`. Xem từng ảnh, so với ảnh mẫu, chỉnh, rồi lặp lại.
6. **Dựng và ghép:**
   - `python3 tactical_anim.py render`, chạy nền và theo dõi tới khi có chữ `RENDER_DONE`;
   - `python3 tactical_audio.py`, chỉnh các mốc âm thanh cho khớp với kịch bản;
   - ghép: `ffmpeg -framerate 30 -i frames/f_%04d.jpg -i audio.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -shortest out.mp4`.
7. **Kiểm tra lần cuối:**
   - làm bảng ảnh khoảng 12 khung trải đều;
   - kiểm tra chuyển động mượt bằng phase correlation quanh một lá cờ đứng yên; sai lệch so với máy quay phải dưới 0,5 px.

## Loại quân và màu

- `kind` của quân (định nghĩa trong `COL` và `bar_tex`):
  - `br`: đỏ sọc trắng;
  - `hn`: đỏ kẻ ô;
  - `nl`: cam;
  - `fr`, `frg`: xanh chữ X trắng;
  - `brcav`, `frcav`: kỵ binh;
  - `rf`: xanh lá;
  - `gun`: pháo;
  - `skb`, `skf`: tán binh (ghim nhỏ).
- `kind` của cờ (định nghĩa trong `flag_img`): `union`, `france`, `dutch`, `hanover`, `portrait:<tên ảnh>`. Thêm cờ mới thì vẽ thêm một nhánh trong `flag_img`.
- **Kênh Mật Lệnh, trận Việt Nam:** theo quy ước của kênh, đỏ là địch, xanh là ta. Thêm kind riêng, ví dụ `vn` (xanh) và `dich` (đỏ), cùng cờ Quân đội nhân dân Việt Nam. Ghi rõ nhãn Hoàng Sa và Trường Sa nếu bản đồ có biển Đông.

## Nguyên tắc chất lượng (đã kiểm chứng)

- **Đặt mọi thứ đứng trên bản đồ bằng `blit()`** (affine dưới mức pixel, có mipmap): quân, cờ, nhãn, khói. Không dán theo pixel nguyên, không làm tròn kích thước hay góc, nếu không sẽ giật.
- **Bóng mây phủ lên mặt đất trước khi vẽ mũi tên và quân.** Quân chỉ tối đi khoảng 10% theo mây, để mũi tên luôn sáng.
- **Cờ là vải treo dưới biển tên**, gợn bằng `wave_flag()`: sóng chạy ngang, mép dưới đung đưa nhiều hơn, có sáng tối theo nếp. Chân dung gợn khoảng 55% so với cờ.
- **Lính tán binh tí hon** (`skb`, `skf` vẽ trong `pin_tex`): đứng cầm súng dựng có lưỡi lê, áo màu phe, đai chéo trắng, mũ đen, bóng đổ nghiêng; tự gom thành nhóm 2–3 người (`_group_skirmishers`). Cao khoảng 17 m theo tỉ lệ bản đồ, ngang cỡ khối quân. Đổi súng hoặc quân phục theo thời kỳ ngay trong `pin_tex` (ví dụ thời chống Pháp vẽ K44, mũ cối).
- **Biểu tượng vũ khí riêng** (`WEAPONS_ICONS`: pháo 12 pound, Charleville, Brown Bess, Baker, kiếm 1796) đang tắt; bật bằng `WEAPONS = WEAPONS_ICONS`, cỡ bằng một khối quân.
- **Tông màu bản đồ:** độ sáng p5/p50/p95 khoảng 50/105/170, R ≈ G, B ≈ 0,6 R (màu kaki). Đổ bóng đồi vừa phải (`ex` khoảng 5,5); không để quá vàng, quá gồ ghề hay rừng có cạnh thẳng.
- **Mũi tên:** màu kem vàng (255, 246, 190), đầu sáng và đuôi mờ, mọc từ đuôi lên đầu trong khoảng 2,5 giây, giữ khoảng 3 giây rồi mờ trong khoảng 1 giây. Các mũi tên phụ xuất hiện lệch nhau khoảng 0,25 giây.
