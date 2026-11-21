# Bộ đồ họa thông tin (phong cách kênh lịch sử quân sự)

`gfx2.py` dựng các loại đồ họa 1920x1080, 30 fps:

| Mẫu | Hàm | Dùng cho |
|---|---|---|
| Bản đồ vệ tinh nghiêng 3D, ghim + nhãn 2 dòng (xanh/trắng), đường khoảng cách | `s_map_pacific` | địa điểm, khoảng cách |
| Bản đồ tác chiến: nền biển + lưới kinh vĩ độ, biểu tượng tàu/máy bay, mũi tên động | `s_map_attack` | diễn biến trận đánh |
| Thẻ chân dung trên nền lưới / trên bản đồ | `s_portrait_grid`, `s_portrait_map` | giới thiệu nhân vật |
| Chữ giờ + ngày ở góc dưới trái | `s_time` | mốc thời gian |
| Ảnh + 3 thông số đếm số | `s_stats` | giới thiệu vũ khí, máy bay |
| Chữ đỏ lớn trên ảnh tư liệu | `s_keyword` | từ khóa, sự kiện |
| Cột phát sóng + sóng âm + câu trích đánh máy | `s_signal` | điện tín, bộ đàm |
| Số liệu trên nền trắng sau chớp sáng | `s_casualty` | tổn thất, kết quả |

Chạy: `python3 gfx2.py <mẫu> out.mp4` hoặc `python3 gfx2.py still <mẫu> <giây> out.png`.

Cần (đặt cạnh file): `oswald-700.ttf` (Oswald, SIL OFL – ghép từ gói npm @fontsource/oswald), font Inter (có sẵn),
`dl/earth-blue-marble.jpg` (NASA Blue Marble, public domain), ảnh trong `photos/`.
Ảnh mẫu: Nagumo, Dauntless, USS Arizona – public domain (Wikimedia Commons); ảnh Nimitz trong bản mẫu là ảnh chụp
tranh (CC BY-SA) – khi làm thật sẽ thay bằng ảnh Hải quân Mỹ public domain.
