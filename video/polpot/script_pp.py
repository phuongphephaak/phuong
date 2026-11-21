"""Kịch bản 'Pol Pot – từ cậu sinh viên Paris đến kẻ diệt chủng' (kênh Mật Lệnh).

Cùng định dạng script_coc.py: id, part, vis=(loại, mô tả), nar (lời dẫn), cap (chữ trên màn hình), hold.
Nguồn: Wikipedia tiếng Anh (Pol Pot, Tuol Sleng Genocide Museum, Nate Thayer), Wikipedia tiếng Việt (Thảm sát Ba Chúc),
Phnom Penh Post (1997, "Am I a savage person?"), VTC News, RFA. Số người chết theo ước tính của Ben Kiernan.
"""

PARTS = {
    1: "Mở đầu",
    2: "Cậu bé Prek Sbauv",
    3: "Paris",
    4: "Người thầy giáo dịu dàng",
    5: "Năm số không",
    6: "Ngôi trường S-21",
    7: "Lưỡi dao hướng về Việt Nam",
    8: "Kết",
}

SCENES = [
    # ---------------- 1. MỞ ĐẦU ----------------
    dict(id="o_date", part=1, vis=("archive", "Đường phố Phnôm Pênh, đoàn người"), cap=["17/04/1975 – PHNÔM PÊNH"],
         nar="Sáng ngày mười bảy tháng tư năm 1975, những người lính mặc đồ đen tiến vào Phnôm Pênh. "
             "Dân thủ đô đổ ra đường vẫy cờ trắng, tin rằng chiến tranh cuối cùng đã kết thúc."),
    dict(id="o_order", part=1, vis=("archive", "Đoàn người rời thành phố"),
         nar="Chỉ vài giờ sau, loa phóng thanh ra lệnh: tất cả phải rời thành phố ngay, vì Mỹ sắp ném bom. "
             "Đi ba ngày thôi, rồi sẽ được trở về."),
    dict(id="o_never", part=1, vis=("archive", "Con đường đất, người gánh gồng"),
         nar="Hơn hai triệu người lên đường. Phần lớn trong số họ không bao giờ được nhìn thấy nhà mình thêm một lần nào nữa."),
    dict(id="o_man", part=1, vis=("photo", "Chân dung Pol Pot"),
         nar="Người đứng sau mệnh lệnh ấy là một thầy giáo cũ, nói năng nhỏ nhẹ, luôn mỉm cười. "
             "Học trò nhớ về ông như một người hiền lành và dễ mến."),
    dict(id="o_toll", part=1, vis=("card", "Con số"), cap=["1,7 TRIỆU NGƯỜI"],
         nar="Chưa đầy bốn năm sau, khoảng một triệu bảy trăm nghìn người Campuchia đã chết, gần một phần tư dân số cả nước."),
    dict(id="o_name", part=1, vis=("photo", "Chân dung Pol Pot"),
         nar="Ông ta tên là Saloth Sar. Thế giới biết đến ông ta bằng một cái tên khác: Pol Pot."),
    dict(id="title", part=1, vis=("card", "Màn tiêu đề"), cap=["POL POT", "TỪ SINH VIÊN PARIS ĐẾN KẺ DIỆT CHỦNG"], hold=7),
    dict(id="sting", part=1, vis=("card", "Hiệu ứng chuyển"), hold=3.5),

    # ---------------- 2. CẬU BÉ PREK SBAUV ----------------
    dict(id="village", part=2, vis=("photo", "Làng Prek Sbauv"), cap=["PREK SBAUV – KAMPONG THOM"],
         nar="Saloth Sar sinh năm 1925 tại làng Prek Sbauv, tỉnh Kampong Thom, bên một nhánh sông nhỏ giữa vùng lúa. "
             "Cha cậu là một nông dân khá giả, có ruộng và trâu."),
    dict(id="palace", part=2, vis=("archive", "Hoàng cung Phnôm Pênh, múa cung đình"), cap=["HOÀNG CUNG PHNÔM PÊNH"],
         nar="Gia đình ấy còn có một mối quan hệ đặc biệt. Người chị họ của cậu là phi tần của nhà vua, "
             "nên cậu bé nhà quê sớm được gửi lên kinh đô và có dịp lui tới hoàng cung."),
    dict(id="monk", part=2, vis=("archive", "Chùa chiền, nhà sư"),
         nar="Lên sáu tuổi, cậu vào chùa làm chú tiểu hơn một năm, rồi học tiếp ở một trường Công giáo của người Pháp. "
             "Bạn học nhớ về cậu là một đứa trẻ trầm tính, dễ chịu, nhưng học hành rất bình thường."),
    dict(id="fail", part=2, vis=("archive", "Lớp học, học sinh"),
         nar="Cậu thi trượt nhiều lần, bị giữ lại lớp, rồi phải chuyển sang học nghề mộc ở một trường kỹ thuật. "
             "Tại đây cậu quen Ieng Sary, người về sau sẽ trở thành cánh tay phải của cậu."),

    # ---------------- 3. PARIS ----------------
    dict(id="paris", part=3, vis=("archive", "Tàu thủy, châu Âu thập niên 1950"), cap=["PARIS – 1949"],
         nar="Năm 1949, may mắn mỉm cười. Saloth Sar giành được học bổng sang Pháp, theo học ngành điện tử vô tuyến tại Paris."),
    dict(id="paris_red", part=3, vis=("card", "Nền tối, sách báo"),
         nar="Nhưng thứ thu hút cậu không nằm trong giảng đường. Cậu cùng Ieng Sary tham gia một nhóm sinh viên nghiên cứu chủ nghĩa Marx, "
             "rồi gia nhập Đảng Cộng sản Pháp."),
    dict(id="paris_fail", part=3, vis=("card", "Bảng điểm"), cap=["3 LẦN THI TRƯỢT"],
         nar="Chuyện học thì vẫn như cũ. Cậu trượt kỳ thi năm thứ nhất, trượt năm thứ hai, rồi trượt thêm lần nữa. "
             "Học bổng bị cắt."),
    dict(id="paris_back", part=3, vis=("archive", "Bến cảng, tàu cập bến"),
         nar="Tháng một năm 1953, Saloth Sar trở về quê nhà, không có tấm bằng nào trong tay. "
             "Thứ duy nhất cậu mang về là một hệ tư tưởng, cùng những người bạn sẵn sàng đi theo đến cùng."),

    # ---------------- 4. NGƯỜI THẦY GIÁO DỊU DÀNG ----------------
    dict(id="teacher", part=4, vis=("archive", "Phnôm Pênh thập niên 1950–60"), cap=["THẦY GIÁO SALOTH SAR"],
         nar="Về nước, anh đi dạy lịch sử, địa lý và văn học Pháp ở một trường tư tại Phnôm Pênh. "
             "Học trò kể rằng thầy Sar điềm tĩnh, ăn nói có sức thuyết phục. Thầy say mê thơ Verlaine."),
    dict(id="marry", part=4, vis=("card", "Nền ấm"), cap=["14/07/1956"],
         nar="Năm 1956, anh cưới Khieu Ponnary, một trong những phụ nữ Campuchia đầu tiên có bằng tú tài. "
             "Đám cưới diễn ra đúng ngày quốc khánh nước Pháp."),
    dict(id="double", part=4, vis=("card", "Nền tối, bóng người"),
         nar="Ban ngày là thầy giáo. Ban đêm, anh dần leo lên những vị trí cao nhất trong một đảng cộng sản hoạt động bí mật. "
             "Năm 1962, người đứng đầu đảng mất tích một cách bí ẩn."),
    dict(id="jungle", part=4, vis=("archive", "Rừng rậm, du kích"), cap=["1963 – BÍ THƯ"],
         nar="Đầu năm 1963, Saloth Sar trở thành bí thư. Ngay sau đó, anh bỏ lại tất cả và biến mất vào rừng sâu."),
    dict(id="travel", part=4, vis=("map", "Bản đồ Phnôm Pênh – Hà Nội – Bắc Kinh"),
         nar="Năm 1965, ông lặn lội theo đường mòn Trường Sơn ra Hà Nội, rồi sang Bắc Kinh. "
             "Ở Trung Quốc, ông được đón tiếp nồng hậu, đúng lúc nước này chuẩn bị bước vào Cách mạng Văn hóa."),
    dict(id="secret", part=4, vis=("card", "Nền tối"),
         nar="Trở về, ông đổi tên đảng, chuyển căn cứ lên vùng núi phía đông bắc, và giữ mọi thứ trong bí mật tuyệt đối. "
             "Ngay cả đảng viên cũng không biết ai thực sự đang lãnh đạo mình."),
    dict(id="coup", part=4, vis=("archive", "Binh lính, xe quân sự 1970"), cap=["18/03/1970 – ĐẢO CHÍNH"],
         nar="Năm 1970, tướng Lon Nol lật đổ Quốc vương Sihanouk. Từ Bắc Kinh, vị vua bị phế truất kêu gọi dân chúng vào rừng chiến đấu. "
             "Hàng vạn nông dân hưởng ứng, và họ đi theo Khmer Đỏ."),
    dict(id="pol", part=4, vis=("archive", "Sihanouk thăm vùng giải phóng 1973"), cap=["SAR → POL POT"],
         nar="Cũng năm ấy, Saloth Sar bắt đầu tự gọi mình là Pol, rồi Pol Pot. Ông từng nói với người thân cận: "
             "đổi tên giúp đánh lừa kẻ thù."),
    dict(id="war", part=4, vis=("archive", "Máy bay ném bom, khói lửa trên đồng ruộng"),
         nar="Năm năm nội chiến tàn khốc. Bom Mỹ trút xuống nông thôn. "
             "Lực lượng Khmer Đỏ từ vài nghìn tay súng lớn lên thành một đội quân siết chặt vòng vây quanh thủ đô."),

    # ---------------- 5. NĂM SỐ KHÔNG ----------------
    dict(id="zero", part=5, vis=("card", "Màn chữ"), cap=["NĂM SỐ 0"],
         nar="Rồi đến ngày mười bảy tháng tư năm 1975. Khmer Đỏ gọi đó là năm số không. "
             "Mọi thứ có từ trước phải bị xóa sạch, để làm lại một đất nước từ đầu."),
    dict(id="march", part=5, vis=("archive", "Đoàn người đi bộ dưới nắng"),
         nar="Cuộc di tản diễn ra giữa tháng nóng nhất trong năm. Hàng chục nghìn bệnh nhân bị đẩy ra khỏi bệnh viện, "
             "có người vẫn nằm nguyên trên giường bệnh. Ước tính khoảng hai mươi nghìn người chết ngay trên đường đi."),
    dict(id="abolish", part=5, vis=("stat", "Danh sách những thứ bị xóa bỏ"), cap=["TIỀN · CHỢ · TRƯỜNG HỌC · TÔN GIÁO"],
         nar="Tiền bị xóa bỏ. Ngân hàng quốc gia bị đánh sập. Chợ, trường học, chùa chiền, bệnh viện lần lượt đóng cửa. "
             "Đeo kính hay biết ngoại ngữ cũng đủ để bị nghi là trí thức."),
    dict(id="angkar", part=5, vis=("archive", "Người mặc đồ đen lao động tập thể"), cap=["ANGKAR – TỔ CHỨC"],
         nar="Không ai nói tên người lãnh đạo. Mọi mệnh lệnh đều nhân danh Angkar, nghĩa là Tổ chức. "
             "Angkar có mắt như quả dứa, nhìn thấy tất cả."),
    dict(id="newpeople", part=5, vis=("archive", "Dân thành phố lao động ngoài đồng"), cap=["\"NGƯỜI CŨ\" – \"NGƯỜI MỚI\""],
         nar="Người dân bị chia làm hai hạng. Nông dân ở các vùng Khmer Đỏ kiểm soát từ trước là người cũ. "
             "Còn dân thành phố bị gọi là người mới, phải nhận khẩu phần ít nhất, việc nặng nhất, và luôn bị nghi ngờ."),
    dict(id="black", part=5, vis=("archive", "Công trường thủy lợi, hàng nghìn người đào đất"),
         nar="Cả đất nước mặc một màu đen, sống trong những hợp tác xã khổng lồ, làm việc từ sáng sớm đến tối mịt. "
             "Bữa ăn chung chỉ có cháo loãng."),
    dict(id="quota", part=5, vis=("card", "Con số"), cap=["3 TẤN THÓC / HA"],
         nar="Pol Pot đặt chỉ tiêu ba tấn thóc trên mỗi héc-ta, gấp nhiều lần sản lượng trước chiến tranh. "
             "Gạo được thu gom để xuất khẩu, trong khi chính những người làm ra nó thì chết đói."),
    dict(id="kids", part=5, vis=("archive", "Trẻ em lao động"),
         nar="Trẻ em trên bảy tuổi bị tách khỏi cha mẹ để Angkar dạy dỗ. Nhiều em được trao súng, "
             "và được dạy rằng kẻ thù có thể là chính người thân của mình."),
    dict(id="slogan", part=5, vis=("quote", "Khẩu hiệu Khmer Đỏ"), cap=["\"Giữ lại không lợi gì,", "mất đi không hại gì.\""],
         nar="Một khẩu hiệu được truyền miệng khắp nơi: giữ ngươi lại cũng chẳng được lợi gì, mất ngươi đi cũng chẳng thiệt hại gì."),

    # ---------------- 6. NGÔI TRƯỜNG S-21 ----------------
    dict(id="school", part=6, vis=("photo", "Tòa nhà Tuol Sleng"), cap=["S-21 – TUOL SLENG"],
         nar="Giữa Phnôm Pênh vắng lặng, có một ngôi trường trung học vẫn sáng đèn. "
             "Các lớp học được ngăn thành phòng giam, sân chơi trở thành nơi tra tấn. Ký hiệu của nó là S-21."),
    dict(id="duch", part=6, vis=("photo", "Duch trước tòa"), cap=["DUCH – CỰU GIÁO VIÊN TOÁN"],
         nar="Người cai quản nhà tù cũng từng là một thầy giáo. Kang Kek Iew, tức Duch, trước kia dạy toán. "
             "Ông ta điều hành S-21 với sự tỉ mỉ đến lạnh người."),
    dict(id="photos", part=6, vis=("photo", "Tường ảnh tù nhân"), cap=["~18.000 TÙ NHÂN"],
         nar="Mỗi tù nhân bị chụp ảnh khi đến, bị ép viết bản thú tội, rồi bị đưa đi. "
             "Theo hồ sơ của tòa án quốc tế, khoảng mười tám nghìn người đã đi qua cánh cổng này."),
    dict(id="survivors", part=6, vis=("photo", "Phòng giam"), cap=["CHỈ VÀI NGƯỜI SỐNG SÓT"],
         nar="Số người còn sống bước ra chỉ đếm trên đầu ngón tay. Một họa sĩ được giữ lại để vẽ chân dung Pol Pot. "
             "Một người khác sống sót vì biết sửa máy."),
    dict(id="purge", part=6, vis=("card", "Nền tối"),
         nar="Nạn nhân không chỉ là kẻ thù cũ. Càng về sau, chính cán bộ Khmer Đỏ lần lượt bị đưa vào S-21. "
             "Pol Pot nhìn đâu cũng thấy phản bội, nhưng chưa từng một lần đặt chân đến đây."),
    dict(id="vn_s21", part=6, vis=("photo", "Hành lang nhà tù"), cap=["345 TÙ NHÂN VIỆT NAM"],
         nar="Trong số tù nhân ấy có cả người Việt Nam. Ra trước tòa nhiều năm sau, Duch thừa nhận đã ra lệnh giết ba trăm bốn mươi lăm tù nhân Việt Nam, "
             "phần lớn bị bắt trên biển hoặc dọc biên giới."),
    dict(id="fields", part=6, vis=("photo", "Tháp sọ Choeung Ek"), cap=["CHOEUNG EK – CÁNH ĐỒNG CHẾT"],
         nar="Cách thành phố mười lăm cây số là Choeung Ek, một trong hàng trăm cánh đồng chết trên khắp đất nước. "
             "Hôm nay, tháp tưởng niệm ở đó chứa hơn năm nghìn chiếc sọ người."),

    # ---------------- 7. LƯỠI DAO HƯỚNG VỀ VIỆT NAM ----------------
    dict(id="vn_hate", part=7, vis=("map", "Bản đồ biên giới Tây Nam"),
         nar="Trong tất cả kẻ thù mà Pol Pot tưởng tượng ra, có một cái tên được nhắc nhiều nhất: Việt Nam. "
             "Người Việt sinh sống ở Campuchia gần như bị xóa sổ ngay từ những năm đầu."),
    dict(id="thochu", part=7, vis=("map", "Đảo Thổ Chu"), cap=["05/1975 – THỔ CHU"],
         nar="Chưa đầy hai tuần sau ngày miền Nam được giải phóng, quân Khmer Đỏ đổ bộ lên đảo Thổ Chu, "
             "bắt đi hơn năm trăm người dân. Đó mới chỉ là khởi đầu."),
    dict(id="raids", part=7, vis=("archive", "Binh lính, súng đạn"), cap=["AN GIANG · TÂY NINH · KIÊN GIANG"],
         nar="Từ An Giang đến Tây Ninh, các cuộc tấn công vượt biên ngày càng dày đặc. "
             "Chúng nhắm vào làng mạc, trường học, những người nông dân đang làm đồng."),
    dict(id="talks", part=7, vis=("card", "Màn chữ"), cap=["05/02/1978 – ĐỀ NGHỊ ĐÀM PHÁN"],
         nar="Việt Nam nhiều lần đề nghị ngừng bắn và ngồi vào bàn đàm phán. Tất cả đều bị Pol Pot gạt đi. "
             "Ông ta tin rằng chỉ cần có chỗ dựa từ Bắc Kinh, đội quân của mình có thể đánh bại Việt Nam."),
    dict(id="bachuc", part=7, vis=("card", "Nền tối"), cap=["18/04/1978 – BA CHÚC"],
         nar="Đêm mười tám tháng tư năm 1978, quân Khmer Đỏ tràn vào xã Ba Chúc, huyện Tri Tôn, tỉnh An Giang."),
    dict(id="bachuc_pagoda", part=7, vis=("card", "Ngôi chùa"), cap=["CHÙA TAM BỬU · CHÙA PHI LAI"],
         nar="Người dân chạy vào chùa Tam Bửu và chùa Phi Lai, tin rằng cửa Phật sẽ che chở cho mình. "
             "Nhưng không có nơi nào an toàn."),
    dict(id="bachuc_toll", part=7, vis=("stat", "Con số"), cap=["3.157 NGƯỜI"],
         nar="Trong mười hai ngày, ba nghìn một trăm năm mươi bảy người dân thường bị sát hại. "
             "Có người mất cùng lúc hàng chục người thân. Chỉ một vài người may mắn sống sót."),
    dict(id="bachuc_now", part=7, vis=("card", "Nhà mồ Ba Chúc"),
         nar="Hôm nay, nhà mồ Ba Chúc vẫn lưu giữ hơn một nghìn chiếc sọ của nạn nhân, "
             "như một lời nhắc rằng tội ác ấy đã từng diễn ra trên chính đất Việt Nam."),
    dict(id="counter", part=7, vis=("map", "Mũi tiến công"), cap=["25/12/1978"],
         nar="Ngày hai mươi lăm tháng mười hai năm 1978, quân tình nguyện Việt Nam cùng lực lượng cách mạng Campuchia mở cuộc phản công. "
             "Những mũi tiến công thọc sâu, chia cắt đội quân của Pol Pot."),
    dict(id="liberate", part=7, vis=("card", "Màn chữ"), cap=["07/01/1979 – PHNÔM PÊNH ĐƯỢC GIẢI PHÓNG"],
         nar="Chỉ mười ba ngày sau, ngày bảy tháng một năm 1979, Phnôm Pênh được giải phóng. "
             "Pol Pot đã kịp rời thủ đô trước đó vài giờ, chạy về phía biên giới Thái Lan."),
    dict(id="tay", part=7, vis=("photo", "Cổng nhà tù Tuol Sleng"), cap=["NHIẾP ẢNH GIA HỒ VĂN TÂY"],
         nar="Những ngày sau đó, nhiếp ảnh gia quân đội Hồ Văn Tây lần theo một mùi hôi kỳ lạ, đến trước cánh cổng của S-21. "
             "Những bức ảnh ông chụp được ở đó đã cho cả thế giới thấy điều gì đã xảy ra."),

    # ---------------- 8. KẾT ----------------
    dict(id="china", part=8, vis=("map", "Biên giới phía Bắc"), cap=["17/02/1979"],
         nar="Pol Pot mất Phnôm Pênh, nhưng người đỡ đầu của ông ta chưa chịu buông tay. "
             "Tháng hai năm 1979, Trung Quốc tấn công sáu tỉnh biên giới phía Bắc Việt Nam, để giảm áp lực cho đội quân Khmer Đỏ đang tan rã."),
    dict(id="un", part=8, vis=("card", "Nền tối"), cap=["GHẾ LIÊN HỢP QUỐC"],
         nar="Nghịch lý là, nhiều năm sau đó, chính quyền Khmer Đỏ vẫn giữ chiếc ghế của Campuchia tại Liên Hợp Quốc. "
             "Pol Pot ẩn mình trong rừng, tiếp tục chiến tranh du kích thêm gần hai mươi năm."),
    dict(id="anlong", part=8, vis=("photo", "Hồ Anlong Veng"), cap=["ANLONG VENG – 1997"],
         nar="Đến năm 1997, tổ chức của ông ta tan rã. Pol Pot ra lệnh giết người đồng chí lâu năm Son Sen cùng cả gia đình. "
             "Lần này, chính thuộc hạ quay lưng với ông ta."),
    dict(id="trial", part=8, vis=("card", "Nền tối"),
         nar="Trong một khu rừng gần biên giới, Pol Pot bị đưa ra trước một phiên tòa do chính những người Khmer Đỏ dựng lên, "
             "và bị kết án quản thúc suốt đời."),
    dict(id="thayer", part=8, vis=("quote", "Lời Pol Pot"), cap=["\"Hãy nhìn tôi xem,", "tôi có phải kẻ man rợ không?\""],
         nar="Vài tháng sau, ông ta trả lời phỏng vấn nhà báo Mỹ Nate Thayer. "
             "Hãy nhìn tôi xem, tôi có phải là kẻ man rợ không? Lương tâm tôi trong sạch."),
    dict(id="deny", part=8, vis=("card", "Nền tối"),
         nar="Ông ta còn nói rằng con số hàng triệu người chết là quá đáng, và nhà tù S-21 chỉ là thứ do Việt Nam dựng lên. "
             "Đến cuối đời, Pol Pot vẫn không nhận bất cứ trách nhiệm nào."),
    dict(id="death", part=8, vis=("photo", "Nơi hỏa táng Pol Pot"), cap=["15/04/1998"],
         nar="Đêm mười lăm tháng tư năm 1998, Pol Pot chết trong căn nhà gỗ nơi ông ta bị quản thúc, ở tuổi bảy mươi hai. "
             "Ba ngày sau, thi thể được thiêu trên một đống lốp xe cũ và rác."),
    dict(id="nojustice", part=8, vis=("photo", "Mộ Pol Pot"),
         nar="Ông ta chết trước khi phải đứng trước bất kỳ tòa án quốc tế nào. "
             "Hàng triệu nạn nhân không bao giờ được nghe kẻ cầm đầu nhận tội."),
    dict(id="final", part=8, vis=("photo", "Tường ảnh tù nhân S-21"),
         nar="Từ một cậu bé hiền lành bên bờ sông, một sinh viên thi trượt ở Paris, một thầy giáo đọc thơ Verlaine, "
             "Saloth Sar đã trở thành Pol Pot. Lịch sử để lại một câu hỏi chưa ai trả lời trọn vẹn: "
             "điều gì đã biến con người ấy thành kẻ diệt chủng?"),
    dict(id="end", part=8, vis=("card", "Màn kết kênh, nhắc đăng ký"), hold=6),
]


if __name__ == "__main__":
    n = sum(len(s.get("nar", "")) for s in SCENES)
    w = sum(len(s.get("nar", "").split()) for s in SCENES)
    print(f"{len(SCENES)} cảnh, {n} ký tự lời dẫn, {w} từ")
