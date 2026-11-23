---
name: ban-do-ve-tinh-short
description: Dựng video dọc ngắn 20–60 giây (Shorts/Reels/TikTok) giải thích một địa danh trên ảnh vệ tinh thật, theo nhịp kiểu "This narrow waterway separates Europe from Asia". Gồm đường phát sáng vẽ dọc địa danh, zoom vụt ra/vào, tô vùng màu (đỏ, xanh lá, cam, xanh ngọc), tô biển xanh đậm có quầng sáng, nhãn chữ nảy có mũi tên, đường nét đứt chạy, vòng tròn đỏ, băng tiêu đề trắng, cùng mô hình 3D xe tăng, máy bay, tàu có bóng đổ. Dùng khi người dùng muốn video dọc về địa lý hay lịch sử trên bản đồ vệ tinh, giải thích vị trí một con sông, eo biển, đèo hay vùng đất, hoặc nhắc đến "video ngắn bản đồ" hay "short vệ tinh".
---

# Video dọc bản đồ vệ tinh

Bản mẫu đã làm xong: **Sông Bến Hải – vết cắt chia đôi đất nước** (26 giây, 1080×1920), mã nguồn gốc ở `video/scripts/song-ben-hai-short/`. Mọi bước chạy bằng Python trên CPU; dựng 26 giây mất khoảng 10 phút với 4 nhân.

## Các file

| File | Việc |
|---|---|
| `scripts/fetch.py` | Tải ảnh vệ tinh, ghép thành ảnh lớn ở 4 mức zoom (`LEV`), ra `mosaic_{z}.jpg` và `mosaic_meta.json`. |
| `scripts/water.py` | Tạo mặt nạ biển `sea_{z}.png` từ Natural Earth `ne_10m_land`. |
| `scripts/geo_prep.py` | Chuẩn bị hình học ra `geo.pkl`: quốc gia, tỉnh, đường sông, các nửa vùng, điểm đặt nhãn. |
| `scripts/tts.py` | Tạo lời dẫn ElevenLabs (giọng `47rM9DW5VmjOw23BVHWi`, `eleven_v3`) vào `aud/`. Sau đó cắt khoảng lặng thành `.wav`. |
| `scripts/short_anim.py` | Dựng khung hình: `test <giây> ...` ra `test/`, `render` ra `frames/` (4 tiến trình). |
| `scripts/short_audio.py` | Trộn lời dẫn, nhạc nền nhẹ 100 bpm, tiếng lướt khi zoom và tiếng "bụp" khi nhãn hiện, ra `audio.wav`. |
| `scripts/models.py` | Dựng 3 mô hình 3D trong Blender và chụp từ trên xuống ở 24 hướng. Đã có sẵn trong `assets/sprites/`. |

Mọi script đọc và ghi trong thư mục `WORK`, mặc định là thư mục hiện tại; dữ liệu đặt ở `WORK/data/`.

## Nguồn dữ liệu (được dùng thương mại)

- **Ảnh vệ tinh:** EOX lớp **`s2cloudless_3857` (Sentinel-2 năm 2016, CC BY 4.0)**, URL `https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg`.
  - Phải ghi nguồn ở góc khung hình.
  - **Không dùng** lớp 2018 trở đi vì giấy phép CC BY-NC-SA cấm dùng thương mại.
  - Lớp 2017 thiếu dữ liệu Việt Nam.
- **Ranh giới:** Natural Earth 10m (phạm vi công cộng) từ `raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/`, gồm `admin_0_countries`, `admin_1_states_provinces` và `land`.
- **Sông, địa danh:** Nominatim (OSM) với `polygon_geojson=1`; gọi cách nhau từ 1 giây trở lên và có User-Agent.
- **Hoàng Sa, Trường Sa:** Natural Earth không gán hai quần đảo cho Việt Nam. Luôn vẽ chấm đảo cùng màu Việt Nam, kèm nhãn **"QĐ. Hoàng Sa"** và **"QĐ. Trường Sa"** khi khung hình có Biển Đông.

## Nhịp kể chuẩn (học từ video mẫu 24 giây, 8 câu)

| Giây | Hình | Lời |
|---|---|---|
| 0–3 | Đường xanh lam phát sáng vẽ dọc địa danh, zoom vụt ra, hai vùng lớn tô xanh lá và cam | Câu móc: "X nhỏ này từng…" |
| 3–5 | **Cắt** về cận cảnh, địa danh tô xanh đậm, nhãn trắng có mũi tên cong | "Đây là X." |
| 5–8 | Tỉnh hoặc thành phố tô xanh ngọc, zoom ra, quốc gia tô đỏ | "Nó nằm ở…" |
| 8–12 | Lia lên tô xanh lá, lia xuống tô cam, chữ rất lớn | "Một bên là…, bên kia là…" |
| 12–15 | **Cắt** về cận cảnh, biển tô xanh đậm có quầng sáng, nhãn vàng | "X nối / đổ ra…" |
| 15–21 | Đường nét đứt chạy, nhãn phụ, có thể thêm máy bay hoặc tàu | Ý nghĩa, sự kiện |
| 21–26 | Zoom vào, vòng tròn đỏ nhấp nháy, băng tiêu đề trắng chữ đen trượt vào | Câu chốt |

**Quy tắc hình:**
- Chữ: Inter Black Italic, kiểu chữ hoa nhỏ (chữ đầu to, phần còn lại in hoa cỡ 0,76), viền đen và bóng mờ.
- Nhãn biển màu vàng (255, 228, 30). Tên vùng lớn màu trắng, cỡ 78–120 px.
- Nhãn hiện ra theo kiểu nảy (0,55 → 1,1 → 1 trong 0,28 giây).
- Lúc cắt cảnh có chớp sáng nhẹ trong 0,12 giây; cuối video mờ dần sang đen trong 0,4 giây.

## Cách làm một địa danh mới

1. Viết 6–8 câu lời dẫn theo bảng nhịp, kiểm chứng sự kiện, rồi chạy `tts.py`.
2. Sửa `LEV` trong `fetch.py` (vùng bao cho từng mức zoom 13, 10, 7, 5), rồi chạy `fetch.py` và `water.py`.
3. Sửa `geo_prep.py`: tên quốc gia và tỉnh, tên sông hoặc địa danh tra trên Nominatim, đường chia hai vùng, toạ độ đặt nhãn trong `pts`.
4. Sửa `short_anim.py`:
   - `CAM` gồm (giây, kinh độ, vĩ độ, zoom, cắt cảnh), khớp với các mốc lời dẫn;
   - mốc hiện/ẩn của từng lớp tô màu và từng nhãn trong `render()`;
   - `VEH` cho phương tiện;
   - `DUR`.
5. Chạy `short_anim.py test 1 4 7 10 13 18 24` và xem từng khung. Kiểm tra:
   - nhãn bị cắt ở mép;
   - các nhãn đè lên nhau;
   - vùng tô lệch so với ảnh vệ tinh;
   - vệt mây hoặc tuyết trắng (xử lý bằng cách vá ảnh như với `mosaic_7`).
6. Chạy `short_audio.py` (sửa các mốc `VO`, tiếng lướt và tiếng bụp), rồi `short_anim.py render`, rồi ghép bằng `ffmpeg -framerate 30 -i frames/f_%04d.jpg -i audio.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -shortest out.mp4`.

## Phương tiện 3D (`VEH`)

- `("ship" | "plane" | "tank", [(giây, kinh độ, vĩ độ), ...], chiều dài px ở zoom 11, độ lệch bóng)`.
- Đầu phương tiện tự xoay theo hướng đi. Tàu có vệt sóng trắng; máy bay đặt độ lệch bóng 70–90 để trông như đang bay cao.
- Kích cỡ là biểu tượng, phóng to so với thật, như quân trên sa bàn.
- Đặt cách nhau xa hơn chiều dài sprite để không chồng lên nhau; kiểm tra điểm đặt tàu nằm trên nền biển bằng `sea_13.png`.
- Muốn có loại xe khác (T-54, M48, F-4, tàu chiến...), sửa `models.py` rồi chạy `blender -b -P models.py -- <thư mục sprite>`. Giữ quy ước đầu hướng +X và 24 hướng mỗi 15°.
- Phù hiệu phải đúng phe và đúng thời kỳ; nếu không chắc thì để trơn, không vẽ phù hiệu.
