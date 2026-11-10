# HMS Coventry 1982 – video nháp (không lời đọc)

- `hms-coventry-ban-nhap-3.mp4`: bản nháp 3 (69 giây, 1080p, có cảnh chiến đấu mô phỏng)
- Ảnh: Wikimedia Commons (public domain và CC/OGL, xem `credits.json`)
- Bản đồ: tự vẽ từ dữ liệu Natural Earth (`scripts/make_maps.py`)
- Hiệu ứng âm thanh và nhạc: ElevenLabs (`scripts/gen_audio.py`)
- Cảnh chiến đấu: hiệu ứng đồ họa tự viết trên ảnh tư liệu (`scripts/vfx.py`)
- Dựng phim: FFmpeg (`scripts/compose.py`)

Cách chạy lại: tải ảnh (`commons_fetch.py photos`), tạo âm thanh (`gen_audio.py audio`),
vẽ bản đồ (`make_maps.py ne_10m_land.geojson clips`), rồi `compose.py <thư mục làm việc> out.mp4`.
