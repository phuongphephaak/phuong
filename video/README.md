# HMS Coventry – Ngày cuối cùng (25/5/1982)

- `hms-coventry-ngay-cuoi-cung-720p.mp4`: phim hoàn chỉnh ~9 phút 49 giây (bản 720p để lưu trên GitHub)
- `kich-ban.md`: kịch bản đầy đủ, mốc thời gian từng cảnh, lời dẫn và thoại bộ đàm
- `credits.json`: nguồn và giấy phép ảnh (Wikimedia Commons)
- `scripts/phim-10-phut/`: toàn bộ mã dựng phim
  - `script_data.py` kịch bản dạng dữ liệu · `audio.py` giọng đọc, bộ đàm, hiệu ứng, nhạc (ElevenLabs)
  - `vfx.py`, `vfx2.py` cảnh mô phỏng · `maps2.py` bản đồ động · `build.py` dựng và trộn âm
- `scripts/` (gốc): công cụ của các bản nháp trước

Chạy lại: `python audio.py voices && python audio.py sfx && python build.py timeline &&
python audio.py music timeline.json && python build.py render && python build.py assemble out.mp4`
(cần ảnh trong `photos/`, `bg_ship1.jpg`, `bg_ship2.jpg`, `land10.geojson` và biến môi trường `ELEVENLABS_API_KEY`).
