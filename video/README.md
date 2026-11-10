# HMS Coventry 1982 – video nháp (không lời đọc)

- `hms-coventry-ban-nhap.mp4`: bản nháp 1 (~47 giây, 1080p)
- Ảnh: Wikimedia Commons (public domain, xem `credits.json`)
- Bản đồ: tự vẽ từ dữ liệu Natural Earth (`scripts/make_maps.py`)
- Hiệu ứng âm thanh và nhạc: ElevenLabs (`scripts/gen_audio.py`)
- Dựng phim: FFmpeg (`scripts/compose.py`)

Cách chạy lại: tải ảnh (`commons_fetch.py photos`), tạo âm thanh (`gen_audio.py audio`),
vẽ bản đồ (`make_maps.py ne_10m_land.geojson clips`), rồi `compose.py <thư mục làm việc> out.mp4`.
