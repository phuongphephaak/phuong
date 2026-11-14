"""Kịch bản 'Chim cắt số 2 – Nguyễn Văn Cốc, phi công bắn rơi nhiều máy bay Mỹ nhất' (kênh Mật Lệnh).

Cùng định dạng script_hamrong.py: id, part, vis=(loại, mô tả), nar (lời dẫn), cap (chữ trên màn hình), hold.
Nguồn: Wikipedia tiếng Việt và tiếng Anh (Nguyễn Văn Cốc), VietNamNet ("Chim cắt số 2 của Không quân Việt Nam"),
Soha (2015), Dân Việt, vietnameseairwarriors.com. Kể theo góc nhìn và số liệu phía Việt Nam.
"""

PARTS = {
    1: "Mở đầu",
    2: "Cậu bé Bích Sơn",
    3: "Con ngựa chiến MiG-21",
    4: "Cái bẫy đầu năm",
    5: "Trận đầu",
    6: "Chim cắt số 2",
    7: "Chín chiến công",
    8: "Kết",
}

SCENES = [
    # ---------------- 1. MỞ ĐẦU ----------------
    dict(id="o_date", part=1, vis=("archive", "Đội hình F-105 bay trên mây"), cap=["30/04/1967 – HÒA BÌNH"],
         nar="Trưa ngày ba mươi tháng tư năm 1967. Trên bầu trời Hòa Bình, một đội hình F-105 của Không quân Mỹ "
             "đang ung dung bay về phía Hà Nội, khoang bom chất đầy."),
    dict(id="o_two", part=1, vis=("flow", "Hai chiếc MiG-21 bay sát núi rừng"),
         nar="Bên dưới, men theo những dãy núi, hai chiếc MiG-21 lặng lẽ áp sát. Người bay phía sau là một thiếu úy hai mươi bốn tuổi. "
             "Anh mới có hơn ba trăm giờ bay, và chưa từng bắn rơi một chiếc máy bay nào."),
    dict(id="o_role", part=1, vis=("archive", "Buồng lái, tay phi công trên cần lái"),
         nar="Trong biên đội, anh là số hai. Nhiệm vụ của số hai chỉ là bám theo, quan sát và che chắn cho số một. "
             "Người được nổ súng là biên đội trưởng."),
    dict(id="o_turn", part=1, vis=("archive", "F-105 trúng tên lửa, bốc cháy"),
         nar="Vậy mà chỉ hai năm sau, chính người phi công số hai ấy đã có chín lần bắn rơi máy bay Mỹ, "
             "nhiều hơn bất kỳ phi công nào trong cuộc chiến trên bầu trời miền Bắc."),
    dict(id="o_name", part=1, vis=("card", "Nền tối, tên nhân vật"),
         nar="Đồng đội gọi anh bằng một cái tên rất riêng: Chim cắt số hai. Còn tên thật của anh là Nguyễn Văn Cốc."),
    dict(id="title", part=1, vis=("card", "Màn tiêu đề"), cap=["CHIM CẮT SỐ 2", "NGUYỄN VĂN CỐC"], hold=7),

    # ---------------- 2. CẬU BÉ BÍCH SƠN ----------------
    dict(id="village", part=2, vis=("archive", "Làng quê Bắc Bộ, cánh đồng lúa"), cap=["BÍCH SƠN – VIỆT YÊN – BẮC GIANG"],
         nar="Nguyễn Văn Cốc sinh tháng mười hai năm 1942, ở xã Bích Sơn, huyện Việt Yên, tỉnh Bắc Giang. "
             "Tuổi thơ của cậu đến sớm với mất mát."),
    dict(id="father", part=2, vis=("card", "Ảnh làng quê đen trắng, ngọn đèn dầu"),
         nar="Năm 1947, khi Cốc mới lên năm, cha cậu, ông Nguyễn Văn Bảy, Chủ tịch Việt Minh huyện Việt Yên, "
             "bị quân Pháp sát hại. Người mẹ một mình đưa các con đi nơi khác sinh sống."),
    dict(id="sky_boy", part=2, vis=("archive", "Máy bay cất cánh, nhìn từ xa qua cánh đồng"),
         nar="Nơi gia đình chuyển đến nằm gần một sân bay. Ngày ngày, cậu bé ngửa mặt nhìn những chiếc máy bay lên xuống, "
             "và một giấc mơ cứ thế lớn dần."),
    dict(id="select", part=2, vis=("archive", "Thanh niên khám sức khỏe, tuyển chọn"), cap=["1961"],
         nar="Năm 1961, đang học lớp tám trường Ngô Sĩ Liên ở thị xã Bắc Giang, Cốc trúng tuyển đợt chọn người đi học lái máy bay. "
             "Khi ấy, miền Bắc gần như chưa có không quân."),
    dict(id="catbi", part=2, vis=("archive", "Máy bay huấn luyện cánh quạt"),
         nar="Những bài học đầu tiên diễn ra ở sân bay Cát Bi, Hải Phòng. Rồi tháng tám năm 1962, cậu cùng một trăm hai mươi học viên "
             "lên tàu hỏa sang Liên Xô. Chuyến đi kéo dài nửa tháng."),
    dict(id="ussr", part=2, vis=("archive", "Trường bay, máy bay phản lực xếp hàng trên sân"), cap=["120 HỌC VIÊN → 17 PHI CÔNG MiG-17"],
         nar="Ở đó là tiếng Nga, là khí động học, là những giờ bay mệt nhoài. Từng người một bị loại. "
             "Đến cuối năm 1964, chỉ mười bảy người tốt nghiệp phi công MiG-17. Nguyễn Văn Cốc là một trong số đó."),
    dict(id="conv", part=2, vis=("photo", "MiG-21 trên đường băng"),
         nar="Anh chưa kịp về nước thì lại được giữ lại thêm một năm. Lần này là để học một loại máy bay hoàn toàn mới: MiG-21."),

    # ---------------- 3. CON NGỰA CHIẾN MiG-21 ----------------
    dict(id="mig21", part=3, vis=("photo", "MiG-21 cất cánh"), cap=["MiG-21"],
         nar="MiG-21 nhỏ, nhẹ, cánh hình tam giác, bay nhanh gấp đôi tốc độ âm thanh. Nhưng nó không dễ chiều. "
             "Nhiều năm sau, ông Cốc vẫn ví nó như một con ngựa chiến khó thuần, mà đã thuần được thì lợi hại vô cùng."),
    dict(id="two_missile", part=3, vis=("card", "Hai tên lửa dưới cánh MiG-21"), cap=["CHỈ 2 TÊN LỬA"],
         nar="Chiếc MiG-21 mà phi công Việt Nam dùng khi ấy không có pháo. Dưới cánh chỉ treo hai quả tên lửa tầm nhiệt. "
             "Bắn trượt cả hai là coi như hết cách đánh."),
    dict(id="f4", part=3, vis=("archive", "F-4 Phantom cất cánh, đội hình F-4"), cap=["F-4 PHANTOM"],
         nar="Đối thủ chính của nó là F-4 Phantom, chiếc tiêm kích hiện đại bậc nhất của Mỹ lúc bấy giờ. Phantom mang tới tám tên lửa, "
             "radar có thể phát hiện mục tiêu từ khoảng sáu, bảy mươi cây số."),
    dict(id="radar", part=3, vis=("card", "So sánh tầm radar F-4 và MiG-21"), cap=["F-4: 60–70 KM", "MiG-21: 15–16 KM"],
         nar="Radar trên MiG-21 chỉ nhìn được chừng mười lăm cây số. Nói cách khác, phi công Mỹ thường thấy MiG từ rất xa, "
             "trong khi phi công Việt Nam gần như phải dựa vào mắt mình."),
    dict(id="gci", part=3, vis=("archive", "Sở chỉ huy, màn hình radar mặt đất, sĩ quan dẫn đường"),
         nar="Để bù lại, họ có đôi mắt ở mặt đất. Các trạm radar và sĩ quan dẫn đường liên tục báo hướng, báo độ cao, "
             "đưa MiG-21 bay thấp, ẩn mình dưới tầm radar đối phương, rồi bất ngờ vọt lên đúng sau lưng đội hình Mỹ."),
    dict(id="return", part=3, vis=("photo", "Phi công Đoàn Sao Đỏ"), cap=["TRUNG ĐOÀN KHÔNG QUÂN 921 – SAO ĐỎ"],
         nar="Năm 1966, Nguyễn Văn Cốc trở về đơn vị cũ, Trung đoàn không quân 921, Đoàn Sao Đỏ. "
             "Lúc này, cuộc chiến trên bầu trời miền Bắc đã bước sang giai đoạn khốc liệt."),
    dict(id="rt", part=3, vis=("archive", "F-105 thả bom hàng loạt, cột khói bốc lên"), cap=["CHIẾN DỊCH SẤM RỀN"],
         nar="Mỗi ngày, hàng trăm lượt máy bay Mỹ vượt qua biên giới, đánh vào cầu cống, nhà máy, đường sắt quanh Hà Nội. "
             "Phần lớn trong số đó là F-105, chiếc tiêm kích bom mà phi công Mỹ thân mật gọi là Thud."),

    # ---------------- 4. CÁI BẪY ĐẦU NĂM ----------------
    dict(id="bolo_date", part=4, vis=("archive", "Đội hình F-4 cất cánh từ căn cứ"), cap=["02/01/1967"],
         nar="Ngày hai tháng một năm 1967. Radar phía Việt Nam phát hiện một đội hình lớn bay vào từ hướng Lào. "
             "Tốc độ, độ cao, đội hình, mọi thứ giống hệt một tốp F-105 đi ném bom."),
    dict(id="bolo_trap", part=4, vis=("archive", "F-4 Phantom bay đội hình, mang tên lửa"),
         nar="Nhưng đó không phải F-105. Đó là những chiếc F-4 Phantom ngụy trang, giả cả mật danh liên lạc lẫn đường bay. "
             "Người Mỹ đã giăng một cái bẫy, và nó mang tên chiến dịch Bolo."),
    dict(id="bolo_cloud", part=4, vis=("archive", "Máy bay lao xuyên qua lớp mây dày"),
         nar="Hôm ấy trời nhiều mây. Những chiếc MiG-21 vừa xuyên qua tầng mây đã thấy mình ở giữa bầy Phantom đang chờ sẵn."),
    dict(id="bolo_shot", part=4, vis=("archive", "Máy bay trúng tên lửa, dù bung giữa trời"),
         nar="Nguyễn Văn Cốc bị bắn trúng gần như ngay sau khi cất cánh. Anh kịp nhảy dù và sống sót. "
             "Trận đánh ấy, Đoàn Sao Đỏ chịu tổn thất nặng nề."),
    dict(id="bolo_lesson", part=4, vis=("archive", "Phi công họp rút kinh nghiệm bên bản đồ"), cap=["BÀI HỌC ĐẮT GIÁ"],
         nar="Đó là một bài học đắt giá. Nhưng các phi công trẻ không gục ngã. Họ ngồi lại với nhau, mổ xẻ từng phút của trận đánh, "
             "và chuẩn bị cho lần gặp lại."),
    dict(id="bolo_why", part=4, vis=("archive", "Phi công Mỹ đáp xuống căn cứ, ăn mừng"),
         nar="Người Mỹ coi Bolo là một chiến thắng vang dội. Nhưng chính họ cũng hiểu, cái bẫy ấy chỉ dùng được một lần. "
             "Lần sau, những chiếc MiG sẽ không lao lên một cách mù quáng nữa."),

    # ---------------- 5. TRẬN ĐẦU ----------------
    dict(id="do", part=5, vis=("photo", "Phi công MiG-21 trong bộ đồ bay"), cap=["NGUYỄN NGỌC ĐỘ – BIÊN ĐỘI TRƯỞNG"],
         nar="Gần bốn tháng sau, đêm hai mươi chín tháng tư, biên đội trưởng Nguyễn Ngọc Độ nhận kèm cặp Nguyễn Văn Cốc. "
             "Hai người sẽ cùng trực chiến vào sáng hôm sau."),
    dict(id="rule", part=5, vis=("card", "Sơ đồ biên đội: số 1 công kích, số 2 yểm hộ"), cap=["SỐ 1 CÔNG KÍCH", "SỐ 2 YỂM HỘ"],
         nar="Nguyên tắc rất rõ ràng. Số một công kích, số hai yểm hộ. Cốc sẽ bay sau lưng Độ, canh chừng phía sau, "
             "để biên đội trưởng yên tâm nhắm bắn."),
    dict(id="scramble", part=5, vis=("archive", "Phi công chạy ra máy bay, MiG cất cánh"), cap=["30/04/1967"],
         nar="Ngày ba mươi tháng tư, lệnh xuất kích được phát ra. Hai chiếc MiG-21 rời sân bay Nội Bài, "
             "bay về phía tây, nơi tốp F-105 đang tiến vào Hòa Bình."),
    dict(id="approach", part=5, vis=("flow", "MiG-21 vọt lên từ dưới mây, đội hình F-105 phía trước"),
         nar="Theo chỉ dẫn từ mặt đất, họ bám sát mặt đất, rồi ngóc lên ngay phía sau đội hình địch. "
             "Những chiếc F-105 hiện ra trước mặt, vẫn chưa hay biết gì."),
    dict(id="do_fire", part=5, vis=("archive", "Vòng ngắm, F-105 trong khung ngắm"),
         nar="Nguyễn Ngọc Độ lao vào trước. Tên lửa rời giá phóng. Một chiếc F-105 trúng đạn, bốc cháy."),
    dict(id="coc_ask", part=5, vis=("archive", "F-105 khác đang bay phía trước, nhìn từ buồng lái"),
         nar="Lúc ấy, Cốc nhận ra phía trước mình vẫn còn một chiếc F-105 khác. Anh xin phép biên đội trưởng. Độ đồng ý."),
    dict(id="coc_fire", part=5, vis=("archive", "Tên lửa lao đi, F-105 nổ tung"),
         nar="Cốc bấm nút phóng. Quả tên lửa lao thẳng vào luồng khí nóng sau đuôi chiếc F-105. "
             "Chiếc máy bay chao đảo, rồi bùng cháy."),
    dict(id="cheer", part=5, vis=("archive", "Sở chỉ huy, sĩ quan đeo tai nghe reo mừng"),
         nar="Trong tai nghe vang lên tiếng reo của biên đội trưởng. Từ sở chỉ huy, trung đoàn trưởng Trần Mạnh ra lệnh "
             "cho biên đội thoát ly, hạ cánh. Cả hai chiếc MiG trở về an toàn."),
    dict(id="first_kill", part=5, vis=("card", "Hai biểu tượng F-105 bị gạch chéo"), cap=["2 F-105 – CẢ BIÊN ĐỘI TRỞ VỀ"],
         nar="Một biên đội hai chiếc, hạ hai F-105, không mất một ai. Đó là chiến công đầu tiên của Nguyễn Văn Cốc."),
    dict(id="goal", part=5, vis=("photo", "Nguyễn Văn Cốc thời trẻ"),
         nar="Về sau, ông ví chuyện ấy như một cầu thủ ghi được bàn đầu tiên. Đã phá được dớp, những bàn sau đến dễ hơn nhiều."),

    # ---------------- 6. CHIM CẮT SỐ 2 ----------------
    dict(id="idea", part=6, vis=("card", "Sơ đồ biên đội, mũi tên số 2 tách ra công kích"),
         nar="Trận đầu tiên ấy để lại cho Cốc một ý nghĩ. MiG-21 chỉ có hai quả tên lửa. "
             "Nếu cả trận chỉ có số một được bắn, thì biên đội đã bỏ phí một nửa sức mạnh của mình."),
    dict(id="falcon", part=6, vis=("flow", "MiG-21 số 2 tách khỏi đội hình, bổ nhào như chim cắt"),
         nar="Vậy là số hai không chỉ bám theo. Khi số một đã vào công kích, số hai quan sát, chờ thời cơ, "
             "rồi lao vào đúng chiếc máy bay mà đối phương bỏ sơ hở. Nhanh, gọn, như một con chim cắt."),
    dict(id="falcon_name", part=6, vis=("card", "Chữ CHIM CẮT SỐ 2"), cap=["CHIM CẮT SỐ 2"],
         nar="Đồng đội gọi anh là Chim cắt số hai từ đó. Trong chín chiến công của mình, sáu lần anh bắn rơi máy bay Mỹ "
             "khi đang bay ở vị trí số hai."),
    dict(id="hit_run", part=6, vis=("archive", "Máy bay bổ nhào xuyên mây, vệt khói"),
         nar="Cách đánh của họ được gói gọn trong mấy chữ: bay thấp, vọt lên, phóng tên lửa, rồi bổ nhào thoát ly. "
             "Không quần nhau lâu, không cho đối phương kịp dùng tới ưu thế về số lượng và radar."),
    dict(id="training", part=6, vis=("archive", "Phi công nghe giảng bài bên mô hình máy bay"),
         nar="Có trận, cả biên đội hạ được ba máy bay Mỹ nhờ lối đánh này. Về sau, nó được đưa vào giáo trình huấn luyện "
             "của Không quân Việt Nam."),
    dict(id="olds", part=6, vis=("archive", "Đội hình F-4, phi công Mỹ trong buồng lái"),
         nar="Không phải trận nào cũng suôn sẻ. Có lần, máy bay của anh bị Phantom bắn hỏng. Có lần, anh phải nhảy dù "
             "vì cạn nhiên liệu giữa trận. Nhưng lần nào trở về, anh cũng lại xin lên trực chiến."),

    # ---------------- 7. CHÍN CHIẾN CÔNG ----------------
    dict(id="y1967", part=7, vis=("card", "Lịch năm 1967, các ngày được khoanh đỏ"), cap=["1967: 6 CHIẾN CÔNG"],
         nar="Chỉ riêng năm 1967, Nguyễn Văn Cốc bắn rơi sáu máy bay Mỹ."),
    dict(id="aug", part=7, vis=("archive", "F-4 Phantom trúng đạn"), cap=["23/08/1967 – F-4D"],
         nar="Ngày hai mươi ba tháng tám, nạn nhân là một chiếc F-4D, đúng loại máy bay đã giăng bẫy anh đầu năm."),
    dict(id="oct", part=7, vis=("archive", "F-105 bay qua vùng núi, khói đạn cao xạ"), cap=["07/10 · 18/11 · 20/11/1967"],
         nar="Rồi đến những chiếc F-105. Ngày bảy tháng mười. Ngày mười tám tháng mười một. Và chỉ hai ngày sau, "
             "ngày hai mươi tháng mười một, thêm một chiếc nữa rơi trên vùng trời Vĩnh Phú."),
    dict(id="nov20", part=7, vis=("flow", "MiG-21 vọt lên sau lưng F-105 trên vùng đồi Vĩnh Phú"),
         nar="Hôm ấy, đội hình F-105 vừa cắt bom xong, đang quay đầu về căn cứ. Đó là lúc phi công Mỹ thả lỏng nhất. "
             "Chiếc MiG-21 trồi lên từ phía dưới, chui đúng vào khoảng trống mà không ai canh chừng."),
    dict(id="ace", part=7, vis=("archive", "F-105 bốc cháy rơi xuống"),
         nar="Theo cách tính của chính người Mỹ, một phi công bắn rơi năm máy bay là đã trở thành át chủ bài. "
             "Thiếu úy số hai năm nào đã vượt qua mốc ấy chỉ trong chưa đầy bảy tháng."),
    dict(id="may68", part=7, vis=("archive", "F-4B cất cánh từ tàu sân bay"), cap=["07/05/1968 – F-4B HẢI QUÂN MỸ"],
         nar="Ngày bảy tháng năm năm 1968, trên vùng trời Nghệ An, anh gặp một chiếc F-4B của Hải quân Mỹ "
             "cất cánh từ tàu sân bay Enterprise."),
    dict(id="may68_hit", part=7, vis=("archive", "Tên lửa lao đi, máy bay rơi trong hoàng hôn"),
         nar="Từ khoảng cách một nghìn rưỡi mét, anh phóng cả hai quả tên lửa. Sáu giờ bốn mươi tư phút chiều, "
             "chiếc Phantom rơi xuống. Hai phi công Mỹ nhảy dù."),
    dict(id="drones", part=7, vis=("archive", "Máy bay trinh sát không người lái được thả từ máy bay mẹ"),
         nar="Hai chiến công cuối cùng của anh là những chiếc máy bay trinh sát không người lái. "
             "Chúng nhỏ, bay nhanh, rất khó đánh chặn, nhưng vẫn không thoát."),
    dict(id="nine", part=7, vis=("card", "Chín biểu tượng máy bay"), cap=["5 F-105 · 2 F-4 · 2 MÁY BAY KHÔNG NGƯỜI LÁI"],
         nar="Tổng cộng chín máy bay Mỹ: năm chiếc F-105, hai chiếc F-4 và hai máy bay trinh sát không người lái. "
             "Ngoài ra, anh còn yểm hộ cho đồng đội bắn rơi thêm chín chiếc khác."),
    dict(id="top", part=7, vis=("card", "Số 9 lớn"), cap=["9"],
         nar="Đến nay, đó vẫn là thành tích cao nhất của một phi công trong các trận không chiến trên bầu trời miền Bắc, "
             "và chính báo chí nước ngoài cũng ghi nhận điều này."),
    dict(id="t4326", part=7, vis=("photo", "MiG-21PF số hiệu 4326 trưng bày ở bảo tàng"), cap=["MiG-21 SỐ HIỆU 4326 – BẢO VẬT QUỐC GIA"],
         nar="Chiếc MiG-21 số hiệu bốn ba hai sáu mà anh từng lái giờ nằm trong bảo tàng. Trên thân nó có mười ba ngôi sao, "
             "ứng với mười ba lần bắn rơi máy bay Mỹ. Sáu phi công từng lái nó đã được phong Anh hùng. "
             "Chiếc máy bay đã được công nhận là Bảo vật quốc gia."),
    dict(id="t4326b", part=7, vis=("photo", "Cận cảnh những ngôi sao trên thân MiG-21 4326"),
         nar="Mỗi ngôi sao ấy là một lần cất cánh không biết có trở về. Và đằng sau nó là những người thợ máy, "
             "những sĩ quan dẫn đường, những người đứng trên đường băng chờ tiếng động cơ quay lại."),

    # ---------------- 8. KẾT ----------------
    dict(id="uncle", part=8, vis=("card", "Ngày đầu năm 1969, nền ảnh lưu niệm"), cap=["01/01/1969"],
         nar="Ngày đầu năm 1969, Nguyễn Văn Cốc được gặp Chủ tịch Hồ Chí Minh. Bác nói một câu mà ông nhớ mãi: "
             "Bác mong không quân Việt Nam có thêm nhiều Cốc nữa."),
    dict(id="hero", part=8, vis=("card", "Huân chương, danh hiệu Anh hùng"), cap=["ANH HÙNG LỰC LƯỢNG VŨ TRANG NHÂN DÂN – 1969"],
         nar="Cùng năm ấy, ở tuổi hai mươi sáu, anh được tuyên dương Anh hùng Lực lượng vũ trang nhân dân. "
             "Trên ngực anh là chín chiếc Huy hiệu Bác Hồ, mỗi chiếc cho một máy bay bắn rơi."),
    dict(id="teacher", part=8, vis=("archive", "Phi công trẻ tập bay, người thầy đứng bên"),
         nar="Rời buồng lái chiến đấu, anh chuyển sang dạy bay. Một trong những học trò của anh là Nguyễn Đức Soát, "
             "người về sau cũng trở thành một phi công át chủ bài."),
    dict(id="love", part=8, vis=("card", "Nền ấm, hoa"),
         nar="Có một câu chuyện ít người biết. Năm 1966, chàng phi công trẻ gặp nữ diễn viên Đới Thu Hương. "
             "Chiến tranh khiến họ phải chờ đợi suốt tám năm, đến năm 1974 mới nên duyên vợ chồng."),
    dict(id="career", part=8, vis=("photo", "MiG-21 xếp hàng trên sân bay"), cap=["TRUNG TƯỚNG – TƯ LỆNH KHÔNG QUÂN"],
         nar="Rồi anh trở thành trung đoàn trưởng chính Đoàn Sao Đỏ năm xưa, sư đoàn trưởng, Tư lệnh Không quân, "
             "và năm 1999 được phong quân hàm Trung tướng."),
    dict(id="fall", part=8, vis=("card", "Nền tối, ánh đèn mờ"),
         nar="Năm 2004, một tai nạn trên cầu thang khiến ông bị tổn thương cột sống, liệt gần như toàn thân. "
             "Người phi công từng làm chủ bầu trời giờ phải nằm một chỗ."),
    dict(id="joke", part=8, vis=("photo", "Nguyễn Văn Cốc thời trẻ, nụ cười"),
         nar="Vậy mà khi có người hỏi thăm, ông vẫn cười: tớ chỉ bị liệt từ cổ trở xuống thôi. "
             "Đầu óc ông vẫn minh mẫn, giọng nói vẫn sắc như thời còn bay."),
    dict(id="final", part=8, vis=("flow", "Hai chiếc MiG-21 bay vào hoàng hôn"),
         nar="Từ một cậu bé mồ côi cha ngước nhìn máy bay, đến chiếc MiG-21 số hai mà đối phương phải dè chừng. "
             "Chim cắt số hai đã chứng minh rằng trên bầu trời, vị trí không quyết định ai là người chiến thắng."),
    dict(id="end", part=8, vis=("card", "Màn kết kênh, nhắc đăng ký"), hold=6),
]


if __name__ == "__main__":
    n = sum(len(s.get("nar", "")) for s in SCENES)
    w = sum(len(s.get("nar", "").split()) for s in SCENES)
    print(f"{len(SCENES)} cảnh, {n} ký tự lời dẫn, {w} từ")
