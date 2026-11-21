# Pipeline dựng video Midway (kênh Mật Lệnh)

| File | Việc |
|---|---|
| `audio_m.py` | Lời dẫn (ElevenLabs, giọng Tuấn Anh), thoại điện đài Anh/Nhật + hiệu ứng bộ đàm, hiệu ứng âm thanh |
| `vis_m.py` | Phân cảnh: mỗi cảnh dùng clip Flow / phim tư liệu / ảnh / đồ họa nào; tiếng động; nhạc |
| `gfx3.py` | Đồ họa theo spec: bản đồ vệ tinh & bản đồ tác chiến, thẻ nhân vật, bức điện, đồng hồ, tiêu đề, logo đóng dấu, màn kết, **thanh nhắc đăng ký** |
| `build_m.py` | `timeline` → `render` (song song) → `assemble` (xfade theo khối, logo góc trên, nhắc đăng ký ~4 lần, trộn âm -16 LUFS) |

Thứ tự: `python audio_m.py voices && python audio_m.py sfx && python build_m.py timeline && python build_m.py render && python build_m.py assemble out.mp4`
Kịch bản lấy từ `video/midway/script_midway.py`; logo từ `video/brand/`.
