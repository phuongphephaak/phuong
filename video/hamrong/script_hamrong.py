"""Kịch bản 'Trận đầu trên bầu trời Hàm Rồng – 3 và 4/4/1965' (kênh Mật Lệnh).

Cùng định dạng script_dbp.py: id, part, vis=(loại, mô tả), nar (lời dẫn), cap (chữ trên màn hình), hold.
Nguồn chính: Wikipedia (Thanh Hóa Bridge, Trần Hanh, Phạm Ngọc Lan), The Aviationist (2018),
HistoryNet ("Crusader"), VietTimes. Chỗ hai phía ghi nhận khác nhau thì lời dẫn nói rõ.
"""

PARTS = {
    1: "Mở đầu",
    2: "Cây cầu không thể phá",
    3: "Những cánh én non trẻ",
    4: "Ngày 3 tháng 4",
    5: "Ngày 4 tháng 4",
    6: "Cái giá",
    7: "Kết",
}

SCENES = [
    # ---------------- 1. MỞ ĐẦU ----------------
    dict(id="h_clock", part=1, vis=("flow", "Đội hình F-105 bay trên mây, mang đầy bom"), cap=["10:30 – 04/04/1965"],
         nar="Mười giờ ba mươi phút sáng, ngày bốn tháng tư năm 1965."),
    dict(id="h_strike", part=1, vis=("archive", "F-105 Thunderchief bay đội hình, bom dưới cánh"),
         nar="Gần năm mươi chiếc tiêm kích bom F-105 của Không quân Mỹ đang lao về Thanh Hóa. Mỗi chiếc mang nhiều quả bom "
             "ba trăm bốn mươi ký. Mục tiêu: cây cầu Hàm Rồng."),
    dict(id="h_belief", part=1, vis=("archive", "Phi công Mỹ trong buồng lái, F-100 hộ tống"),
         nar="Phía trên là hơn hai mươi chiếc F-100 hộ tống. Các phi công Mỹ biết miền Bắc Việt Nam có máy bay tiêm kích. "
             "Nhưng chưa ai nghĩ những chiếc máy bay ấy dám cất cánh."),
    dict(id="h_dive", part=1, vis=("flow", "Bốn chiếc MiG-17 lao ra từ đám mây, bổ nhào từ phía sau"),
         nar="Rồi từ trong tầng mây, bốn chiếc MiG-17 nhỏ bé bất ngờ bổ nhào xuống, ngay sau đuôi đội hình F-105."),
    dict(id="h_impact", part=1, vis=("flow", "F-105 trúng đạn bốc cháy, lao xuống biển"), hold=3),
    dict(id="h_question", part=1, vis=("card", "Nền tối"),
         nar="Chỉ trong vài phút, hai chiếc F-105 rơi xuống. Đó là những chiếc máy bay Mỹ đầu tiên bị bắn rơi trong không chiến "
             "trên bầu trời Việt Nam. Nhưng trong bốn phi công MiG cất cánh sáng hôm ấy, chỉ một người trở về."),
    dict(id="title", part=1, vis=("card", "Màn tiêu đề"), cap=["TRẬN ĐẦU", "BẦU TRỜI HÀM RỒNG 1965"], hold=7),

    # ---------------- 2. CÂY CẦU ----------------
    dict(id="tonkin", part=2, vis=("archive", "Tàu khu trục Mỹ, máy bay cất cánh từ tàu sân bay 1964"),
         cap=["THÁNG 8/1964"],
         nar="Tháng tám năm 1964, sau sự kiện Vịnh Bắc Bộ, Mỹ bắt đầu ném bom miền Bắc Việt Nam. "
             "Đầu tháng ba năm 1965, chiến dịch Sấm Rền chính thức mở màn."),
    dict(id="bridge", part=2, vis=("photo", "Cầu Hàm Rồng bắc qua sông Mã, hai bên là núi Rồng và núi Ngọc"),
         cap=["CẦU HÀM RỒNG – THANH HÓA"],
         nar="Trên đường tiến công, có một mục tiêu đặc biệt: cầu Hàm Rồng ở Thanh Hóa. Cây cầu thép dài khoảng một trăm sáu mươi mét, "
             "bắc qua sông Mã giữa hai ngọn núi, vừa hoàn thành năm 1964."),
    dict(id="artery", part=2, vis=("map", "Bản đồ miền Bắc: tuyến đường sắt và quốc lộ 1 đi qua Hàm Rồng"),
         nar="Cả đường sắt lẫn quốc lộ một đều đi qua đây. Đây là mạch máu nối Hà Nội với các tỉnh phía nam. "
             "Phá được cầu Hàm Rồng, Mỹ sẽ cắt đứt một con đường tiếp tế quan trọng bậc nhất."),
    dict(id="why_bridge", part=2, vis=("archive", "Đoàn tàu hỏa, xe tải chở hàng qua cầu"),
         nar="Mỗi ngày, những đoàn tàu và đoàn xe chở lương thực, vũ khí đi qua cây cầu này về phía nam. Với Bộ chỉ huy Mỹ, "
             "đánh sập Hàm Rồng là cách nhanh nhất để làm chậm dòng tiếp tế ấy."),
    dict(id="jaw", part=2, vis=("archive", "Ảnh trinh sát cây cầu từ trên cao"),
         nar="Phi công Mỹ gọi nó là Hàm Rồng, Dragon's Jaw. Họ chưa biết rằng cây cầu này sẽ đứng vững suốt bảy năm, "
             "qua hàng trăm phi vụ ném bom."),
    dict(id="defense", part=2, vis=("archive", "Pháo cao xạ, dân quân trên đồi"),
         nar="Quanh cầu, hàng chục trận địa pháo cao xạ được bố trí trên núi Rồng, núi Ngọc. Dân quân, tự vệ, "
             "cả những cô gái Thanh Hóa, đều sẵn sàng."),

    # ---------------- 3. NHỮNG CÁNH ÉN ----------------
    dict(id="tuyen", part=2, vis=("photo", "Nữ dân quân Hàm Rồng vác đạn"), cap=["NGÔ THỊ TUYỂN"],
         nar="Trong số đó có cô dân quân mười chín tuổi Ngô Thị Tuyển. Theo những gì được kể lại, giữa trận đánh, "
             "cô gái nặng chưa đến năm mươi ký đã vác hai hòm đạn tổng cộng chín mươi tám ký ra trận địa pháo."),
    dict(id="vpaf", part=3, vis=("archive", "MiG-17 trên đường băng, phi công 1960s"),
         nar="Nhưng lần này, bầu trời Hàm Rồng còn có một lực lượng mới. Tháng tám năm 1964, Trung đoàn không quân "
             "tiêm kích 921, đoàn Sao Đỏ, đưa những chiếc MiG-17 đầu tiên về sân bay Nội Bài."),
    dict(id="young", part=3, vis=("photo", "Phi công trẻ bên máy bay"),
         nar="Đó là một lực lượng non trẻ. Các phi công phần lớn mới học bay ở nước ngoài, chưa ai từng không chiến thật. "
             "Họ chỉ có vài chục chiếc máy bay."),
    dict(id="training", part=3, vis=("archive", "Phi công tập luyện, máy bay huấn luyện"),
         nar="Nhiều người từng là bộ đội bộ binh, được chọn đi học lái máy bay khi chưa từng ngồi trên một chiếc ô tô. "
             "Họ học tiếng nước ngoài, học khí động học, rồi học bay, chỉ trong vài năm."),
    dict(id="mig17", part=3, vis=("card", "So sánh MiG-17 và F-105 trên bản vẽ kỹ thuật"),
         cap=["MiG-17: ~6 TẤN · DƯỚI TỐC ĐỘ ÂM THANH", "F-105: GẦN 24 TẤN · VƯỢT TỐC ĐỘ ÂM THANH"],
         nar="MiG-17 là một thiết kế từ đầu thập niên năm mươi. Nhỏ, nhẹ, bay dưới tốc độ âm thanh, chỉ có pháo. "
             "Đối diện là F-105, nặng gấp gần bốn lần, bay nhanh hơn tốc độ âm thanh."),
    dict(id="thud", part=3, vis=("archive", "F-105 cất cánh, cận cảnh khoang bom"),
         nar="F-105 Thunderchief được thiết kế để mang bom hạt nhân bay thật nhanh ở tầm thấp. Ở Việt Nam, nó trở thành "
             "con ngựa thồ chở bom chủ lực của Không quân Mỹ. Phi công Mỹ thân mật gọi nó là Thud."),
    dict(id="edge", part=3, vis=("archive", "MiG-17 lượn vòng gắt"),
         nar="Nhưng MiG-17 có một lợi thế: nó lượn vòng rất gắt ở tầm thấp. Còn F-105 khi mang đầy bom thì nặng nề, "
             "khó xoay trở. Nếu đánh nhanh, đánh gần, đánh bất ngờ, những chiếc MiG nhỏ bé có cơ hội."),
    dict(id="plan", part=3, vis=("flow", "Phòng chỉ huy dẫn đường, màn hình radar, bản đồ"),
         nar="Kế hoạch được vạch ra: các biên đội MiG bay thấp để tránh radar, được dẫn đường từ mặt đất đến khu vực Hàm Rồng, "
             "rồi bất ngờ vọt lên tấn công. Đánh xong lập tức rút về."),

    # ---------------- 4. NGÀY 3 THÁNG 4 ----------------
    dict(id="d3", part=4, vis=("card", "Ngày 03/04/1965"), cap=["03/04/1965"],
         nar="Sáng ngày ba tháng tư năm 1965, đợt tấn công đầu tiên vào cầu Hàm Rồng bắt đầu."),
    dict(id="risner", part=4, vis=("archive", "F-105 cất cánh từ căn cứ Thái Lan, máy bay tiếp dầu KC-135"),
         nar="Gần tám mươi máy bay Mỹ tham gia, dẫn đầu là Trung tá Robinson Risner, một át chủ bài từ chiến tranh Triều Tiên. "
             "Chúng cất cánh từ các căn cứ ở Thái Lan, tiếp dầu trên không, rồi lao vào Thanh Hóa."),
    dict(id="risner_note", part=4, vis=("photo", "Robinson Risner"), cap=["ROBINSON RISNER"],
         nar="Risner khi ấy là một trong những phi công nổi tiếng nhất nước Mỹ. Chỉ vài tháng sau, ngày mười sáu tháng chín "
             "năm 1965, chính ông bị bắn rơi trên miền Bắc và trải qua hơn bảy năm trong trại giam ở Hà Nội."),
    dict(id="bullpup", part=4, vis=("archive", "Tên lửa Bullpup phóng đi, bom nổ quanh cầu"),
         nar="Những quả tên lửa Bullpup đầu tiên đánh trúng cầu. Nhưng khi khói tan, cây cầu vẫn đứng vững, "
             "chỉ bị cháy sém. Đầu đạn quá nhỏ so với kết cấu thép đồ sộ."),
    dict(id="aaa", part=4, vis=("archive", "Pháo cao xạ bắn lên trời, máy bay trúng đạn"),
         nar="Pháo cao xạ quanh cầu bắn dữ dội. Một chiếc F-100 và một máy bay trinh sát RF-101 bị bắn rơi."),
    dict(id="lan_up", part=4, vis=("flow", "Bốn MiG-17 bay thấp trên đồng lúa và núi"),
         nar="Cùng lúc, bốn chiếc MiG-17 cất cánh. Biên đội trưởng là Phạm Ngọc Lan, cùng các phi công Phan Văn Túc, "
             "Hồ Văn Quỳ và Trần Minh Phương."),
    dict(id="lan_attack", part=4, vis=("flow", "MiG-17 bám đuôi F-8 Crusader, đạn pháo xé không khí"),
         nar="Phạm Ngọc Lan phát hiện những chiếc F-8 Crusader của Hải quân Mỹ vừa bổ nhào tấn công trận địa pháo. "
             "Anh lặng lẽ áp sát từ phía sau, đến khoảng hai, ba trăm mét, rồi bóp cò."),
    dict(id="lan_hit", part=4, vis=("flow", "F-8 trúng đạn, bốc khói, bật đốt sau bỏ chạy"),
         nar="Đạn trúng chiếc F-8 của Thiếu tá Spence Thomas. Phía Việt Nam ghi nhận chiếc máy bay bị bắn rơi. "
             "Theo phía Mỹ, chiếc F-8 hư hại nặng nhưng vẫn lết được về hạ cánh ở Đà Nẵng."),
    dict(id="lan_fuel", part=4, vis=("flow", "MiG-17 hạ cánh bắt buộc trên bãi cát ven sông"),
         nar="Mải đuổi theo đối phương ra hướng biển, Phạm Ngọc Lan cạn nhiên liệu. Anh phải hạ cánh bắt buộc "
             "trên một bãi cát ven sông. Người dân địa phương chạy ra, giúp anh và chiếc máy bay."),
    dict(id="first", part=4, vis=("photo", "Phạm Ngọc Lan"), cap=["PHẠM NGỌC LAN"],
         nar="Đó là trận không chiến đầu tiên của Không quân Nhân dân Việt Nam. Về sau, ngày ba tháng tư được chọn làm "
             "ngày truyền thống của Không quân."),
    dict(id="d3_end", part=4, vis=("archive", "Cầu Hàm Rồng vẫn đứng giữa khói"),
         nar="Cầu Hàm Rồng vẫn đứng. Và người Mỹ quyết định quay lại vào ngày hôm sau, với lực lượng lớn hơn."),

    # ---------------- 5. NGÀY 4 THÁNG 4 ----------------
    dict(id="claims", part=4, vis=("archive", "Mảnh xác máy bay, dân quân bên xác máy bay"),
         nar="Theo thống kê của phía Việt Nam, trong hai ngày ba và bốn tháng tư, quân và dân Hàm Rồng bắn rơi bốn mươi bảy máy bay Mỹ. "
             "Phía Mỹ thừa nhận con số thấp hơn nhiều. Nhưng cả hai phía đều đồng ý một điều: cây cầu vẫn đứng."),
    dict(id="d4", part=5, vis=("card", "Ngày 04/04/1965"), cap=["04/04/1965"],
         nar="Sáng ngày bốn tháng tư, khoảng tám mươi máy bay Mỹ lại xuất kích. Bốn mươi tám chiếc F-105 mang bom, "
             "hơn hai mươi chiếc F-100 bay phía trên để chặn MiG."),
    dict(id="hanh_up", part=5, vis=("flow", "Bốn MiG-17 cất cánh từ đường băng trong sương sớm"),
         nar="Ở Nội Bài, một biên đội MiG-17 khác cất cánh. Biên đội trưởng là Trần Hanh. Bay cùng anh là Phạm Giấy, "
             "Lê Minh Huân và Trần Nguyên Năm."),
    dict(id="hanh", part=5, vis=("photo", "Trần Hanh"), cap=["TRẦN HANH"],
         nar="Trần Hanh khi đó ba mươi hai tuổi, đại đội trưởng của trung đoàn 921. Biên đội bay thấp, bám theo địa hình, "
             "được sở chỉ huy dẫn đường từng phút."),
    dict(id="spot", part=5, vis=("flow", "Từ buồng lái MiG, nhìn thấy đội hình F-105 phía dưới qua lớp mây mỏng"),
         nar="Khoảng mười giờ ba mươi, qua một lớp mây mỏng, Trần Hanh nhìn thấy bốn chiếc F-105 đang chuẩn bị bổ nhào vào cầu."),
    dict(id="cover", part=5, vis=("map", "Sơ đồ: MiG từ trên mây lao xuống phía sau đội hình F-105, F-100 ở xa"),
         nar="Những chiếc F-100 hộ tống đang ở sai vị trí. Không ai che chắn phía sau đội hình F-105."),
    dict(id="attack", part=5, vis=("flow", "MiG-17 bổ nhào xuyên mây, ngắm vào F-105 phía trước"),
         nar="Trần Hanh ra lệnh công kích. Bốn chiếc MiG bổ nhào xuyên qua mây, từ phía trên và phía sau. "
             "Các phi công Mỹ hoàn toàn bất ngờ."),
    dict(id="fire", part=5, vis=("flow", "Pháo 37 ly khai hỏa, F-105 bốc cháy"),
         nar="Ở cự ly chừng bốn trăm mét, Trần Hanh khai hỏa. Đạn pháo ba mươi bảy ly xé toạc chiếc F-105 phía trước. "
             "Gần như cùng lúc, Lê Minh Huân bắn trúng một chiếc khác."),
    dict(id="two_down", part=5, vis=("flow", "Hai chiếc F-105 lao xuống biển, một chiếc dù bung"),
         nar="Hai chiếc F-105 bốc cháy, lao xuống vùng biển gần đảo Hòn Mê. Thiếu tá Frank Bennett nhảy dù ra biển nhưng "
             "chết đuối trước khi đội cứu hộ kịp đến. Đại úy James Magnusson mất tích, không bao giờ được tìm thấy."),
    dict(id="shock", part=5, vis=("archive", "Phi công Mỹ họp rút kinh nghiệm, bản đồ"),
         nar="Đó là những chiếc máy bay Mỹ đầu tiên bị bắn rơi trong không chiến ở Việt Nam. Thứ máy bay mà người Mỹ "
             "coi là lỗi thời vừa hạ gục niềm tự hào của Không quân Mỹ."),

    # ---------------- 6. CÁI GIÁ ----------------
    dict(id="report", part=5, vis=("archive", "Báo chí Mỹ đưa tin, bản tin thời sự"),
         nar="Tin tức gây chấn động trong giới chỉ huy Mỹ. Một lực lượng không quân mới thành lập, với những chiếc máy bay "
             "cận âm, đã xuyên qua lưới hộ tống và hạ hai chiếc tiêm kích bom hiện đại chỉ trong vài phút."),
    dict(id="chase", part=6, vis=("flow", "F-100 lao xuống đuổi theo MiG-17 bay sát mặt đất"),
         nar="Nhưng trận đánh chưa kết thúc. Những chiếc F-100 quay lại truy đuổi. Bầu trời Hàm Rồng lúc ấy dày đặc "
             "đạn pháo cao xạ, máy bay hai bên quần nhau ở tầm rất thấp."),
    dict(id="lost", part=6, vis=("card", "Ba ngôi sao, nền tối"), cap=["PHẠM GIẤY · LÊ MINH HUÂN · TRẦN NGUYÊN NĂM"],
         nar="Phạm Giấy, Lê Minh Huân và Trần Nguyên Năm không trở về. Đến nay, nguyên nhân chính xác vẫn còn tranh luận: "
             "có thể bị F-100 bắn, có thể trúng đạn trong vùng hỏa lực dày đặc."),
    dict(id="hanh_back", part=6, vis=("flow", "MiG-17 đơn độc bay thấp qua thung lũng, kim nhiên liệu chạm vạch đỏ"),
         nar="Trần Hanh liên tục lượn gắt để thoát khỏi vòng vây. Khi thoát ra được, máy bay gần cạn nhiên liệu. "
             "Anh hạ cánh bắt buộc ngoài sân bay ở Nghệ An, sống sót trở về."),
    dict(id="price", part=6, vis=("archive", "Đồng đội tiễn biệt, hoa"),
         nar="Hai chiếc F-105 đổi lấy ba phi công. Với một lực lượng không quân chỉ có vài chục người lái, "
             "đó là một mất mát rất lớn."),
    dict(id="sao_vang", part=6, vis=("archive", "Công trường xây sân bay, người dân đắp đường băng"),
         nar="Trận đánh cũng cho thấy MiG cần một sân bay gần chiến trường hơn. Chưa đầy hai tháng sau, việc xây dựng sân bay Sao Vàng "
             "ở Thanh Hóa được quyết định. Hàng nghìn thanh niên xung phong lao vào công trường."),
    dict(id="lesson", part=6, vis=("archive", "Phi công MiG nghe phân tích trận đánh"),
         nar="Nhưng bài học được rút ra ngay. Đánh bất ngờ, đánh nhanh, rút nhanh. Không quần lâu với đối phương "
             "ở nơi mình bất lợi. Lối đánh ấy về sau trở thành sở trường của các phi công MiG."),

    # ---------------- 7. KẾT ----------------
    dict(id="us_change", part=7, vis=("archive", "F-4 Phantom cất cánh, đội hình hộ tống"),
         nar="Phía Mỹ cũng phải thay đổi. Từ đó, mỗi phi vụ ném bom miền Bắc đều cần thêm máy bay hộ tống, "
             "thêm cảnh báo. Những chiếc MiG nhỏ bé buộc đối phương phải tính toán lại."),
    dict(id="seven", part=7, vis=("archive", "Cầu Hàm Rồng trong khói bom các năm sau"),
         cap=["7 NĂM · HƠN 870 PHI VỤ"],
         nar="Còn cây cầu Hàm Rồng, nó đứng vững thêm bảy năm, qua hơn tám trăm bảy mươi phi vụ. Phải đến năm 1972, "
             "với bom điều khiển bằng laser, Mỹ mới đánh sập được nhịp cầu."),
    dict(id="cost_area", part=7, vis=("archive", "Máy bay Mỹ trúng đạn trên vùng trời Thanh Hóa"),
         nar="Theo một số thống kê của phía Mỹ, trong vùng trời quanh cây cầu, khoảng một trăm phi công Mỹ đã bị bắn rơi trong suốt cuộc chiến. "
             "Hàm Rồng trở thành một trong những nơi đáng sợ nhất với phi công Mỹ."),
    dict(id="hanh_later", part=7, vis=("photo", "Trần Hanh những năm sau"),
         nar="Trần Hanh về sau trở thành Tư lệnh Không quân, rồi Thứ trưởng Bộ Quốc phòng. Ông qua đời cuối năm 2024, "
             "ở tuổi chín mươi hai."),
    dict(id="lan_later", part=7, vis=("photo", "Phạm Ngọc Lan những năm sau"),
         nar="Phạm Ngọc Lan bị thương ở cột sống sau một lần hạ cánh, phải rời buồng lái chiến đấu. Ông chuyển sang huấn luyện "
             "những lớp phi công trẻ, sau này trở thành Thiếu tướng. Ông mất năm 2019."),
    dict(id="three", part=7, vis=("archive", "Bia tưởng niệm, hoa trên sông Mã"),
         nar="Còn Phạm Giấy, Lê Minh Huân và Trần Nguyên Năm, ba phi công đầu tiên hy sinh trong không chiến, "
             "tên của họ gắn liền với trận đánh mở đầu của Không quân Nhân dân Việt Nam."),
    dict(id="final", part=7, vis=("flow", "Hoàng hôn trên cầu Hàm Rồng, sông Mã, bốn vệt máy bay xa"),
         nar="Ngày bốn tháng tư năm 1965, bốn chiếc MiG-17 cất cánh, một chiếc trở về. Nhưng từ ngày ấy, bầu trời miền Bắc "
             "không còn là nơi máy bay Mỹ có thể bay đến mà không phải trả giá."),
    dict(id="end", part=7, vis=("card", "Màn kết kênh, nhắc đăng ký"), hold=6),
]


if __name__ == "__main__":
    n = sum(len(s.get("nar", "")) for s in SCENES)
    w = sum(len(s.get("nar", "").split()) for s in SCENES)
    print(f"{len(SCENES)} cảnh, {n} ký tự lời dẫn, {w} từ")
