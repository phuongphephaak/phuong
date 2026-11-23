# Ghi chú phong cách: bản đồ chiến thuật kiểu Epic History "Waterloo"

Phân tích toàn bộ 35 phút video mẫu: bảng ảnh 6 giây một khung, rồi xem từng giây ở đoạn 9:00–10:30 và đoạn cờ gợn ở 2:48. Chỉ học phong cách, không sao chép tài sản của video.

## Bố cục kể chuyện
- Cảnh bản đồ xen kẽ với tranh sơn dầu và trích dẫn. Bản đồ chiếm khoảng 60% thời lượng.
- Mỗi nhịp kể:
  1. đồng hồ đổi giờ;
  2. vòng tròn vàng khoanh đơn vị được nhắc tới;
  3. mũi tên chỉ hướng hành động;
  4. quân di chuyển;
  5. khói và đất chuyển nâu ở vùng giao chiến;
  6. máy quay từ từ phóng vào điểm nóng.
- Mở đầu toàn cảnh có chữ "BELGIUM" lớn và các mũi tên hành quân dài. Ban đêm thì bản đồ tối, lửa trại vàng.

## Bản đồ
- **Góc nhìn:** từ trên xuống, nghiêng nhẹ (tilt khoảng 24–28°), xoay khoảng −3° đến −9°. Phía bắc ở trên; sống núi chính chạy chéo từ dưới trái lên trên phải.
- **Màu và đồi:** kaki ô liu. Sườn đón nắng vàng kem, sườn khuất ô liu sẫm. Đồi lớn, thoải.
- **Ruộng:** các dải ô dài, mỗi ô có vân luống cày mảnh theo một hướng riêng, viền ô rất mờ.
- **Rừng:** cây nhỏ dày đặc, có điểm sáng ở góc trên trái và bóng đổ ở góc dưới phải. Mép rừng không đều.
- **Đường, suối, làng:**
  - đường màu nâu sẫm mảnh, lõi sáng hơn;
  - suối màu xanh xám, uốn khúc, có ao nhỏ;
  - làng là cụm nhà mái đỏ nâu hoặc xám dọc đường;
  - trang trại có tường bao.
- **Bóng mây:** mảng tối lớn mềm, trôi chậm khoảng 40 m/s, che khoảng 35–45% diện tích.
- **Viền tối:** vignette rõ ở các góc.

## Quân
- **Tiểu đoàn:** hai thanh dài song song, nổi khối (có độ dày, mép trên sáng, bóng đổ xuống dưới phải).
  - Anh: đỏ có sọc trắng chéo.
  - Hà Lan: cam.
  - Hanover và KGL: đỏ kẻ ô trắng.
  - Pháp: xanh có chữ X trắng.
  - Kỵ binh: thanh ngắn hơn. Kỵ binh Pháp màu trắng sọc xanh.
- **Tán binh:** ghim nhỏ đứng thành hàng thưa trước tuyến.
- **Pháo:** cụm nòng xám kèm xe kéo màu nâu.
- **Cờ hiệu:**
  - biển tên trắng viền đỏ (Anh) hoặc viền xanh (Pháp), chữ in hoa nhỏ, có núm trên đỉnh;
  - dưới biển tên là tấm vải cờ, cán cờ xuống đất;
  - bóng đổ nghiêng xuống mặt đất về phía phải;
  - tướng thì thay cờ bằng chân dung trong khung.
- **Tan hàng:** khi bị đẩy lùi, quân xoay lệch, giãn ra và một số biến mất.

## Hiệu ứng
- **Vòng tròn:** vàng kem dày, quầng sáng mềm, tự vẽ theo chiều kim đồng hồ từ đỉnh trong khoảng 1 giây, giữ rồi mờ đi.
- **Mũi tên:**
  - rộng, nửa trong suốt, đầu sáng đuôi mờ, có vân nhẹ, nằm trên mặt đất (chịu phối cảnh);
  - mọc dần, đầu mũi tên đi theo ngọn;
  - các mũi song song xuất hiện lệch nhau;
  - mũi tên cong dùng cho xung phong hoặc vu hồi.
- **Khói:** cụm trắng sáng ở góc trên trái, phồng ra rồi tan trong khoảng 3 giây và trôi theo gió.
- **Mặt đất:** chuyển nâu dần ở vùng đã giao chiến.
- **Đồng hồ:** góc trên phải, chữ condensed đậm màu xám gradient, nổi khối, có bóng; đổi giờ bằng crossfade khoảng 0,45 giây.
- **Địa danh:** chữ serif in hoa nhỏ màu kem, bóng mềm, cỡ chữ theo mức phóng to.

## Máy quay
- Luôn trôi chậm, không đứng yên hẳn.
- Đến nhịp quan trọng thì phóng vào (viewW từ khoảng 3,7 km xuống khoảng 1,8 km) và xoay nhẹ.
- Đi theo hướng hành động, ví dụ lia xuống theo kỵ binh xung phong.

## Bài học kỹ thuật
1. **Giật hình:** do dán sprite theo pixel nguyên và làm tròn kích thước hay góc. Sửa bằng `blit()` affine dưới mức pixel; sai lệch đo được còn khoảng 0,2 px.
2. **Cache mipmap theo `id()` của ảnh:** phải giữ tham chiếu tới ảnh gốc. Nếu không, `id` bị tái sử dụng và cờ này hiện thành cờ khác.
3. **Mây che làm mũi tên xỉn:** phải phủ mây lên mặt đất trước khi vẽ mũi tên.
4. **Quầng sáng mũi tên rò thành vệt:** quầng sáng lọt ra phía trước đầu mũi tên. Cần giới hạn quầng sáng trong `tpar <= Lc` và `best < hw + 30`.
5. **Bản đồ quá tối hoặc quá vàng:** chuẩn hoá độ sáng theo phân vị (p5 → 0,30, p95 → 0,74) rồi nén vùng sáng.
6. **Hàng rào cây:** đặt dày dọc một vài đoạn đường. Không rải chấm cây lẻ dọc viền ô ruộng, nhìn rất xấu.
