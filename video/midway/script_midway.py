"""Kịch bản 'Sáu phút định mệnh – Trận Midway 1942'.

Mỗi cảnh: id, part (phần), vis=(loại, mô tả), nar (lời dẫn), cap (chữ trên màn hình),
radio=[(người nói, câu gốc, phụ đề)], sfx (âm thanh), hold (giây giữ thêm không lời).
Loại hình ảnh: archive (phim tư liệu public domain), photo (ảnh tư liệu), map (bản đồ động),
vfx (mô phỏng bằng code), veo (clip AI tạo bằng Veo – xem VEO_PROMPTS), card (màn chữ / đồ họa).
Giờ trong phim là giờ địa phương Midway.
"""

PARTS = {
    1: "Mở đầu (hook)",
    2: "Bối cảnh: sáu tháng bất bại",
    3: "Cuộc chiến mật mã",
    4: "Giăng bẫy",
    5: "Buổi sáng 4/6: những quyết định của Nagumo",
    6: "Đòn đánh của Mỹ",
    7: "Sáu phút",
    8: "Hiryu phản công",
    9: "Kết",
}

SCENES = [
    # ---------------- 1. HOOK ----------------
    dict(id="h_clock", part=1, vis=("vfx", "Góc nhìn từ buồng lái SBD Dauntless trên mây, kính ngắm, mặt biển xanh phía dưới"),
         cap=["10:22 – 04/06/1942"], sfx="tiếng gió, động cơ cánh quạt",
         nar="Mười giờ hai mươi hai phút sáng, ngày bốn tháng sáu năm 1942."),
    dict(id="h_fleet", part=1, vis=("veo", "V01 – bốn tàu sân bay Nhật rẽ sóng nhìn từ trên cao"),
         nar="Giữa Thái Bình Dương, cách hòn đảo nhỏ Midway vài trăm cây số, bốn chiếc tàu sân bay mạnh nhất "
             "của Hải quân Đế quốc Nhật Bản đang rẽ sóng tiến lên."),
    dict(id="h_deck", part=1, vis=("veo", "V02 – boong tàu sân bay Nhật đầy máy bay, thợ máy chạy qua lại"),
         nar="Trên boong và trong khoang chứa, hàng chục máy bay đang được nạp đầy xăng, bom và ngư lôi, "
             "chuẩn bị cho một đòn tấn công quyết định."),
    dict(id="h_belief", part=1, vis=("vfx", "Chiến đấu cơ Zero bay tuần tra sát mặt biển, tàu sân bay phía sau"),
         nar="Suốt sáu tháng qua, hạm đội này chưa từng nếm mùi thất bại. Quân Nhật tin rằng người Mỹ hoàn toàn không biết "
             "mình đang đến."),
    dict(id="h_dive", part=1, vis=("vfx", "Đội hình máy bay ném bom bổ nhào Dauntless lần lượt nghiêng cánh, lao xuống"),
         sfx="tiếng rít bổ nhào tăng dần",
         nar="Nhưng quân Nhật không hề hay biết, ở độ cao gần năm nghìn mét ngay trên đầu, hàng chục máy bay ném bom bổ nhào "
             "của Mỹ vừa nghiêng cánh. Và lao xuống."),
    dict(id="h_impact", part=1, vis=("vfx", "Bom xuyên boong tàu, cầu lửa bùng lên, khói đen"), hold=3,
         sfx="ba tiếng nổ lớn, nhạc dừng"),
    dict(id="h_six", part=1, vis=("vfx", "Ba cột khói đen trên mặt biển nhìn từ xa"),
         nar="Chỉ trong khoảng sáu phút, ba trong bốn chiếc tàu sân bay ấy bốc cháy dữ dội. "
             "Sáu phút đã xoay chuyển toàn bộ cuộc chiến Thái Bình Dương."),
    dict(id="h_question", part=1, vis=("card", "Nền tối, chữ trắng mờ dần"),
         nar="Nhưng chỉ vài giờ trước đó, mọi lợi thế vẫn nằm trọn trong tay người Nhật. "
             "Vậy điều gì đã xảy ra trong buổi sáng định mệnh ấy?"),
    dict(id="title", part=1, vis=("card", "Màn tiêu đề: ảnh ghép tàu Akagi, Dauntless, chân dung Nimitz và Yamamoto"),
         cap=["SÁU PHÚT ĐỊNH MỆNH", "TRẬN MIDWAY 1942"], hold=7, sfx="tiếng trống lớn, logo kênh"),

    # ---------------- 2. BỐI CẢNH ----------------
    dict(id="pearl", part=2, vis=("archive", "Trân Châu Cảng 7/12/1941 – phim/ảnh Hải quân Mỹ, thiết giáp hạm cháy"),
         cap=["NGÀY 7 THÁNG 12 NĂM 1941"],
         nar="Ngày bảy tháng mười hai năm 1941, Nhật Bản tập kích Trân Châu Cảng. Tám thiết giáp hạm của Hạm đội "
             "Thái Bình Dương bị đánh chìm hoặc hư hại. Hơn hai nghìn bốn trăm người Mỹ thiệt mạng."),
    dict(id="expand", part=2, vis=("map", "Bản đồ châu Á – Thái Bình Dương, vùng Nhật chiếm lan rộng từ 12/1941 đến 5/1942"),
         nar="Trong sáu tháng tiếp theo, quân Nhật tràn qua Thái Bình Dương như một cơn bão. Philippines, Mã Lai, "
             "Singapore, Đông Ấn Hà Lan. Đi đến đâu, quân Nhật thắng đến đó."),
    dict(id="yamamoto", part=2, vis=("photo", "Thẻ chân dung Đô đốc Yamamoto Isoroku trên nền lưới"),
         cap=["ĐÔ ĐỐC YAMAMOTO ISOROKU"],
         nar="Người đứng sau những chiến thắng ấy là Đô đốc Yamamoto Isoroku, Tổng tư lệnh Hạm đội Liên hợp. "
             "Nhưng chính ông hiểu rõ hơn ai hết một sự thật đáng sợ."),
    dict(id="industry", part=2, vis=("archive", "Xưởng đóng tàu và nhà máy máy bay Mỹ thời chiến"),
         nar="Ông từng sống và học tập ở Mỹ. Ông biết nền công nghiệp Mỹ lớn gấp nhiều lần Nhật Bản. "
             "Nếu chiến tranh kéo dài, Nhật chắc chắn sẽ thua. Muốn thắng, phải tiêu diệt hạm đội Mỹ thật nhanh, "
             "trước khi những con tàu mới kịp ra đời."),
    dict(id="missed", part=2, vis=("photo", "Tàu sân bay Enterprise trên biển"),
         nar="Và ở Trân Châu Cảng, Nhật đã bỏ lỡ mục tiêu quan trọng nhất: các tàu sân bay Mỹ. "
             "Sáng hôm đó, không một chiếc nào có mặt trong cảng."),
    dict(id="doolittle", part=2, vis=("archive", "B-25 cất cánh từ tàu sân bay Hornet (phim Hải quân Mỹ)"),
         cap=["NGÀY 18 THÁNG 4 NĂM 1942"],
         nar="Ngày mười tám tháng tư năm 1942, mười sáu máy bay ném bom B-25 cất cánh từ tàu sân bay Hornet, "
             "bay hơn một nghìn cây số để ném bom Tokyo. Thiệt hại không lớn. Nhưng đó là một cái tát vào niềm "
             "kiêu hãnh của Nhật Bản."),
    dict(id="doolittle2", part=2, vis=("archive", "B-25 bay thấp qua mặt biển"),
         nar="Bầu trời thủ đô, nơi Thiên hoàng ngự, không còn an toàn nữa. Kế hoạch táo bạo nhất của Yamamoto "
             "lập tức được thông qua."),
    dict(id="midway_map", part=2, vis=("map", "Bản đồ: Hawaii – Midway, đường kẻ 2.100 km, phóng to vào đảo san hô"),
         cap=["MIDWAY"],
         nar="Mục tiêu: Midway. Một đảo san hô nhỏ bé nằm giữa Thái Bình Dương, cách Trân Châu Cảng khoảng hai nghìn "
             "một trăm cây số. Tiền đồn cuối cùng của Mỹ ở phía tây Hawaii."),
    dict(id="plan", part=2, vis=("map", "Mũi tên kế hoạch Nhật: lực lượng đổ bộ đến Midway, hạm đội chờ sẵn phía sau"),
         nar="Ý tưởng của Yamamoto rất rõ ràng. Đánh chiếm Midway, buộc các tàu sân bay Mỹ phải lao ra ứng cứu. "
             "Khi đó, hạm đội Nhật đang chờ sẵn sẽ tiêu diệt chúng trong một trận quyết chiến."),
    dict(id="aleut", part=2, vis=("map", "Mũi tên phụ lên quần đảo Aleut ở phía bắc"),
         nar="Để đánh lạc hướng, một hạm đội khác sẽ tấn công quần đảo Aleut ở tận phía bắc."),
    dict(id="force_jp", part=2, vis=("card", "Đồ họa lực lượng Nhật: 4 thẻ tàu sân bay Akagi, Kaga, Soryu, Hiryu; chân dung Nagumo"),
         cap=["AKAGI", "KAGA", "SORYU", "HIRYU"],
         nar="Lực lượng Nhật huy động gần hai trăm tàu chiến lớn nhỏ. Mũi nhọn là Lực lượng Cơ động của Phó Đô đốc "
             "Nagumo Chuichi, với bốn tàu sân bay: Akagi, Kaga, Soryu và Hiryu. Chính là những con tàu đã tấn công "
             "Trân Châu Cảng."),
    dict(id="force_us", part=2, vis=("card", "Đồ họa lực lượng Mỹ: 3 thẻ tàu sân bay Enterprise, Hornet, Yorktown (Yorktown có dấu hư hại)"),
         cap=["ENTERPRISE", "HORNET", "YORKTOWN"],
         nar="Phía Mỹ chỉ còn ba tàu sân bay có thể ra trận. Trong đó, Yorktown vừa trúng bom ở trận biển San Hô "
             "tháng trước, thân tàu vẫn còn rò dầu."),
    dict(id="believe", part=2, vis=("veo", "V03 – hạm đội Nhật tiến trong sương sớm, cờ mặt trời mọc"),
         nar="Trên giấy tờ, người Nhật nắm chắc phần thắng. Bộ chỉ huy Nhật tin rằng hạm đội Mỹ sẽ bị bất ngờ thêm một lần nữa. "
             "Nhưng đó là một sai lầm chết người."),

    # ---------------- 3. MẬT MÃ ----------------
    dict(id="dungeon", part=3, vis=("veo", "V04 – tầng hầm không cửa sổ, bàn đầy giấy, máy đánh chữ, khói thuốc"),
         cap=["TRÂN CHÂU CẢNG – TRẠM GIẢI MÃ HYPO"],
         nar="Tại Trân Châu Cảng, dưới tầng hầm không có cửa sổ của một tòa nhà, một nhóm nhỏ chuyên gia mật mã "
             "làm việc ngày đêm. Người trong nhóm gọi nơi đó là Hầm Ngục."),
    dict(id="rochefort", part=3, vis=("photo", "Thẻ chân dung Trung tá Joseph Rochefort"),
         cap=["TRUNG TÁ JOSEPH ROCHEFORT"],
         nar="Người chỉ huy là Trung tá Joseph Rochefort. Ông mặc áo choàng, đi dép lê trong hầm, "
             "có những ngày làm việc liền hơn hai mươi tiếng."),
    dict(id="jn25", part=3, vis=("vfx", "Đồ họa: dãy mã số chạy, một số nhóm sáng lên thành chữ, cuối cùng hiện 'AF'"),
         nar="Nhiệm vụ của nhóm là bẻ khóa hệ thống mật mã của Hải quân Nhật, có tên JN hai lăm. Các chuyên gia Mỹ chỉ đọc được "
             "một phần nhỏ. Nhưng đủ để biết người Nhật đang chuẩn bị một chiến dịch lớn, nhằm vào một mục tiêu "
             "có mật danh: AF."),
    dict(id="doubt", part=3, vis=("map", "Bản đồ: dấu hỏi trên Midway, Hawaii, bờ Tây nước Mỹ"),
         nar="Rochefort tin rằng AF chính là Midway. Nhưng ở Washington, nhiều người lại nghĩ đó là Hawaii, "
             "thậm chí là bờ Tây nước Mỹ. Nếu đoán sai, hạm đội Mỹ sẽ có mặt ở sai chỗ. Và mọi thứ sẽ kết thúc."),
    dict(id="trick", part=3, vis=("card", "Đồ họa bức điện đánh máy: 'MIDWAY – MÁY LỌC NƯỚC NGỌT BỊ HỎNG'"),
         nar="Để chứng minh, nhóm của ông nghĩ ra một mẹo: bí mật yêu cầu Midway gửi đi một bức điện không mã "
             "hóa, báo rằng máy lọc nước ngọt trên đảo đã bị hỏng."),
    dict(id="bite", part=3, vis=("card", "Đồ họa: bức điện Nhật bị chặn, dòng chữ 'AF ĐANG THIẾU NƯỚC' tô vàng"),
         sfx="tiếng máy điện báo",
         nar="Ít lâu sau, các điện đài viên Mỹ bắt được một bức điện của Nhật: AF đang thiếu nước ngọt. "
             "Con cá đã cắn câu. AF chính là Midway."),
    dict(id="nimitz", part=3, vis=("photo", "Thẻ chân dung Đô đốc Chester Nimitz"),
         cap=["ĐÔ ĐỐC CHESTER NIMITZ"],
         nar="Thông tin được trình lên Đô đốc Chester Nimitz, Tổng tư lệnh Hạm đội Thái Bình Dương. Các chuyên gia "
             "còn đoán được thời điểm tấn công: đầu tháng sáu. Nimitz quyết định đặt cược tất cả vào đó."),
    dict(id="trap", part=3, vis=("veo", "V05 – phòng chỉ huy hải quân thập niên 1940, sĩ quan đẩy mô hình tàu trên bàn bản đồ"),
         nar="Lần này, người Mỹ sẽ không bị đánh úp. Lần này, chính quân Mỹ sẽ giăng bẫy."),

    # ---------------- 4. GIĂNG BẪY ----------------
    dict(id="yorktown_dock", part=4, vis=("archive", "Ảnh Yorktown trong ụ khô Trân Châu Cảng, cuối tháng 5/1942"),
         cap=["NGÀY 27 THÁNG 5 NĂM 1942"],
         nar="Ngày hai mươi bảy tháng năm, tàu Yorktown khập khiễng về đến Trân Châu Cảng. Các kỹ sư ước tính "
             "cần nhiều tuần, thậm chí vài tháng để sửa chữa. Nimitz chỉ cho các kỹ sư ba ngày."),
    dict(id="welders", part=4, vis=("veo", "V06 – công nhân hàn trong ụ tàu ban đêm, tia lửa bắn"),
         sfx="tiếng hàn, búa gõ kim loại",
         nar="Hơn một nghìn công nhân làm việc không nghỉ, cả ngày lẫn đêm. Ngày ba mươi tháng năm, Yorktown rời "
             "cảng, khi một số công nhân vẫn còn đang sửa chữa ngay trên tàu."),
    dict(id="spruance", part=4, vis=("photo", "Thẻ chân dung Chuẩn đô đốc Raymond Spruance"),
         cap=["CHUẨN ĐÔ ĐỐC RAYMOND SPRUANCE"],
         nar="Một bất ngờ khác. Đô đốc Halsey, chỉ huy tàu sân bay dày dạn nhất của Mỹ, phải nhập viện vì bệnh "
             "ngoài da. Người thay thế là Chuẩn đô đốc Raymond Spruance, một sĩ quan tàu tuần dương trầm lặng, "
             "chưa từng chỉ huy tàu sân bay."),
    dict(id="point_luck", part=4, vis=("map", "Ba biểu tượng tàu sân bay Mỹ tiến tới điểm hẹn phía đông bắc Midway"),
         cap=["ĐIỂM MAY MẮN"],
         nar="Ba tàu sân bay Enterprise, Hornet và Yorktown lặng lẽ tiến đến một điểm hẹn ở phía đông bắc Midway. "
             "Điểm hẹn ấy mang một cái tên đầy hy vọng: Điểm May Mắn."),
    dict(id="subs_late", part=4, vis=("map", "Hàng tàu ngầm Nhật đến muộn, mũi tên tàu sân bay Mỹ đã đi qua"),
         nar="Trong khi đó, hàng rào tàu ngầm Nhật lẽ ra phải phát hiện hạm đội Mỹ lại đến vị trí quá muộn. "
             "Các tàu sân bay Mỹ đã đi qua từ trước. Hạm đội Nhật vẫn không hề hay biết."),
    dict(id="pby_sight", part=4, vis=("veo", "V07 – thủy phi cơ PBY Catalina bay trên đại dương lúc bình minh"),
         cap=["NGÀY 3 THÁNG 6 NĂM 1942"],
         nar="Ngày ba tháng sáu, một thủy phi cơ tuần tra Catalina phát hiện đoàn tàu vận tải Nhật cách Midway "
             "hơn một nghìn cây số. Cuộc săn đuổi đã bắt đầu."),

    # ---------------- 5. BUỔI SÁNG 4/6 ----------------
    dict(id="t0430", part=5, vis=("vfx", "Tàu sân bay Nhật trong bóng tối trước bình minh, đèn boong, cánh quạt quay"),
         cap=["04:30 – 04/06/1942"], sfx="động cơ máy bay khởi động, nhạc căng",
         nar="Bốn giờ ba mươi phút sáng ngày bốn tháng sáu. Trời còn tối. Trên boong bốn tàu sân bay Nhật, "
             "động cơ gầm lên."),
    dict(id="launch", part=5, vis=("veo", "V08 – máy bay Nhật cất cánh từ tàu sân bay lúc rạng đông"),
         nar="Một trăm lẻ tám máy bay cất cánh, hướng về Midway. Chỉ huy đợt tấn công là Đại úy Tomonaga Joichi."),
    dict(id="tone", part=5, vis=("vfx", "Thủy phi cơ trinh sát được phóng từ tuần dương hạm, máy phóng bị kẹt"),
         nar="Cùng lúc, Nagumo phóng bảy thủy phi cơ đi tìm tàu Mỹ. Nhưng chiếc số bốn trên tuần dương hạm Tone "
             "gặp trục trặc, cất cánh trễ gần nửa giờ. Một chậm trễ tưởng như nhỏ nhặt."),
    dict(id="pby_radio", part=5, vis=("vfx", "Góc nhìn từ PBY: đội hình máy bay Nhật bay qua phía dưới"),
         cap=["05:45"],
         radio=[("pby", "Many planes heading Midway. Bearing three-two-zero, distance one-five-zero.",
                 "Nhiều máy bay đang hướng về Midway. Phương vị 320, cự ly 150 hải lý.")],
         nar="Gần sáu giờ, một chiếc Catalina khác phát hiện máy bay Nhật và gửi về một bức điện không mã hóa."),
    dict(id="raid", part=5, vis=("archive", "Phim 'The Battle of Midway' (1942): Midway bị ném bom, kho dầu cháy, pháo phòng không"),
         cap=["06:30"], sfx="còi báo động, súng phòng không, nổ",
         nar="Sáu giờ ba mươi, máy bay Nhật ập xuống Midway. Các chiến đấu cơ cũ kỹ của Thủy quân Lục chiến Mỹ "
             "lao lên đánh chặn, phần lớn bị bắn rơi hoặc hư hại. Bom rơi xuống kho dầu, nhà chứa máy bay."),
    dict(id="ford", part=5, vis=("archive", "Phim 'The Battle of Midway': cảnh rung, khói, cờ Mỹ trên cột"),
         nar="Trên đảo có một người đặc biệt: đạo diễn Hollywood John Ford, khi đó là sĩ quan Hải quân. Ông cầm máy "
             "quay ghi lại tất cả, kể cả khi bị thương. Những thước phim bạn đang xem là của ông."),
    dict(id="second", part=5, vis=("vfx", "Máy bay Nhật quay về, khói từ Midway phía sau"),
         cap=["07:00"],
         radio=[("tomonaga", "Dai niji kōgeki no yō ari.", "Cần tấn công đợt hai.")],
         nar="Nhưng đường băng Midway vẫn hoạt động. Bảy giờ sáng, Tomonaga gửi điện về tàu."),
    dict(id="mid_attack", part=5, vis=("vfx", "Máy bay ném bom Mỹ từ Midway lao vào hạm đội Nhật, Zero đánh chặn, cột nước"),
         nar="Trong lúc đó, máy bay từ Midway bắt đầu tấn công hạm đội Nhật. Từng tốp, từng tốp lao vào, rời rạc, "
             "không có chiến đấu cơ hộ tống."),
    dict(id="b26", part=5, vis=("vfx", "Một chiếc B-26 bốc cháy lao sượt qua đài chỉ huy tàu sân bay rồi rơi xuống biển"),
         sfx="tiếng gầm lướt qua, nước bắn",
         nar="Một chiếc B-26 trúng đạn lao thẳng về phía đài chỉ huy tàu Akagi, nơi Nagumo đang đứng. "
             "Nó sượt qua trong gang tấc, rồi lao xuống biển."),
    dict(id="no_hits", part=5, vis=("vfx", "Cột nước bom trượt quanh tàu sân bay, thủy thủ Nhật giơ tay reo"),
         nar="Không một quả bom, không một quả ngư lôi nào trúng đích. Hàng chục máy bay Mỹ bị bắn rơi. "
             "Trên tàu Nhật, các thủy thủ reo hò."),
    dict(id="rearm", part=5, vis=("photo", "Thẻ chân dung Phó Đô đốc Nagumo Chuichi"),
         cap=["07:15", "PHÓ ĐÔ ĐỐC NAGUMO CHUICHI"],
         nar="Bảy giờ mười lăm. Nagumo đưa ra quyết định đầu tiên. Những máy bay dự bị, vốn mang ngư lôi để đánh "
             "tàu, được lệnh tháo ngư lôi, lắp bom để tấn công Midway lần hai."),
    dict(id="hangar", part=5, vis=("veo", "V09 – khoang chứa máy bay tàu sân bay Nhật, thợ máy kéo ngư lôi trên xe đẩy"),
         sfx="tiếng xích, kim loại",
         nar="Dưới khoang chứa, hàng trăm thợ máy bắt đầu công việc nặng nhọc: tháo từng quả ngư lôi nặng gần một "
             "tấn, đưa bom lên thay."),
    dict(id="tone_report", part=5, vis=("vfx", "Góc nhìn từ thủy phi cơ trinh sát: mười chấm tàu trên mặt biển"),
         cap=["07:40"],
         radio=[("scout", "Teki rashiki mono jusseki miyu.", "Thấy mười tàu, có vẻ là tàu địch.")],
         nar="Bảy giờ bốn mươi. Chiếc thủy phi cơ cất cánh trễ của tàu Tone gửi về một bức điện."),
    dict(id="what_ships", part=5, vis=("veo", "V10 – sĩ quan Nhật trên đài chỉ huy đọc bức điện, căng thẳng"),
         nar="Tàu Mỹ? Ở đây? Có tàu sân bay hay không? Bức điện không nói rõ. Nagumo ra lệnh dừng thay vũ khí, "
             "chờ thêm tin."),
    dict(id="carrier", part=5, vis=("card", "Đồng hồ 08:20, bức điện tô vàng: 'ĐỊCH CÓ VẺ CÓ MỘT TÀU SÂN BAY'"),
         cap=["08:20"],
         nar="Phải đến tám giờ hai mươi, câu trả lời mới đến. Địch có vẻ có một tàu sân bay đi kèm."),
    dict(id="dilemma", part=5, vis=("map", "Sơ đồ: máy bay đánh Midway quay về (sắp hết xăng), tàu Mỹ ở phía đông bắc, đồng hồ chạy"),
         nar="Nagumo rơi vào thế khó. Các máy bay đánh Midway đang quay về, nhiên liệu cạn dần, cần hạ cánh ngay. "
             "Máy bay dự bị thì vũ khí đang tháo dở. Chiến đấu cơ đã lên trời chống đỡ các đợt tấn công."),
    dict(id="yamaguchi", part=5, vis=("photo", "Thẻ chân dung Chuẩn đô đốc Yamaguchi Tamon"),
         cap=["CHUẨN ĐÔ ĐỐC YAMAGUCHI TAMON"],
         nar="Trên tàu Hiryu, Chuẩn đô đốc Yamaguchi Tamon, người được xem là chỉ huy tàu sân bay xuất sắc nhất của "
             "Nhật, gửi tín hiệu: đề nghị tung lực lượng tấn công ngay lập tức."),
    dict(id="refuse", part=5, vis=("vfx", "Tàu sân bay Akagi nhìn ngang, cờ hiệu, mặt biển"),
         nar="Nagumo từ chối. Ông chọn cách an toàn: thu hồi máy bay trước, lắp lại ngư lôi, rồi tung ra một đòn "
             "đánh đầy đủ, có hộ tống. Một quyết định hợp lý. Nhưng thời gian là thứ ông không còn."),
    dict(id="recover", part=5, vis=("vfx", "Máy bay Nhật lần lượt hạ cánh xuống boong, boong chật kín"),
         cap=["08:37"],
         nar="Từ tám giờ ba mươi bảy phút, các tàu sân bay Nhật bận rộn thu hồi máy bay. Trong khoang chứa, bom vừa "
             "tháo và ngư lôi vừa lắp nằm ngổn ngang, chưa kịp đưa về kho."),

    # ---------------- 6. ĐÒN ĐÁNH CỦA MỸ ----------------
    dict(id="spruance_go", part=6, vis=("veo", "V11 – máy bay Mỹ cất cánh từ tàu sân bay Enterprise, thủy thủ vẫy cờ"),
         cap=["07:00 – TÀU SÂN BAY ENTERPRISE"], sfx="nhạc trống, động cơ",
         nar="Trong khi đó, ở phía đông bắc, Spruance đã đưa ra quyết định quan trọng nhất đời mình. Từ bảy giờ sáng, "
             "ông tung gần như toàn bộ máy bay trên Enterprise và Hornet, đánh ngay khi người Nhật còn đang bận rộn."),
    dict(id="scattered", part=6, vis=("map", "Các mũi tên phi đội Mỹ tỏa ra nhiều hướng"),
         nar="Nhưng đòn đánh ấy cũng rời rạc. Các phi đội cất cánh lần lượt, bay theo những hướng khác nhau."),
    dict(id="nowhere", part=6, vis=("map", "Mũi tên nhóm Hornet đi lệch về phía tây, biểu tượng hết xăng"),
         nar="Phần lớn máy bay ném bom và chiến đấu cơ của Hornet bay sai hướng, không bao giờ tìm thấy hạm đội Nhật. "
             "Nhiều chiếc hết xăng, rơi xuống biển."),
    dict(id="waldron", part=6, vis=("photo", "Thẻ chân dung Thiếu tá John Waldron, Phi đội Ngư lôi 8"),
         cap=["THIẾU TÁ JOHN WALDRON"],
         nar="Chỉ có một người dám làm khác: Thiếu tá John Waldron, chỉ huy Phi đội Ngư lôi Tám. Tin vào linh cảm của "
             "mình, ông bẻ lái về hướng tây bắc, dẫn theo mười lăm máy bay ngư lôi Devastator. Và ông đã đúng."),
    dict(id="vt8", part=6, vis=("vfx", "Máy bay ngư lôi TBD bay sát mặt biển về phía tàu sân bay"),
         cap=["09:20"],
         nar="Chín giờ hai mươi. Phi đội Tám tìm thấy tàu sân bay Nhật. Không có chiến đấu cơ hộ tống. Những chiếc "
             "Devastator chậm chạp phải bay thẳng, bay thấp sát mặt nước để thả ngư lôi."),
    dict(id="vt8_die", part=6, vis=("vfx", "Zero bổ nhào bắn, Devastator bốc cháy đâm xuống biển, cột nước"),
         sfx="súng máy, nổ, nước bắn",
         nar="Hàng chục chiếc Zero lao xuống. Từng chiếc Devastator bốc cháy, đâm xuống biển. "
             "Không một quả ngư lôi nào trúng đích."),
    dict(id="gay", part=6, vis=("photo", "Thẻ chân dung Thiếu úy George Gay"),
         cap=["THIẾU ÚY GEORGE GAY"],
         nar="Trong số ba mươi người của phi đội, chỉ một người sống sót: Thiếu úy George Gay. Máy bay rơi, anh nổi "
             "trên mặt biển, nấp dưới một tấm đệm ghế để không bị phát hiện."),
    dict(id="gay2", part=6, vis=("vfx", "Góc nhìn từ mặt nước: sóng, tàu sân bay Nhật lướt qua phía xa"),
         nar="Từ chỗ đó, anh sẽ trở thành nhân chứng cho những gì xảy ra tiếp theo."),
    dict(id="vt6vt3", part=6, vis=("vfx", "Thêm các đợt máy bay ngư lôi lao vào, bị bắn hạ"),
         nar="Ngay sau đó, phi đội ngư lôi của Enterprise, rồi của Yorktown lao vào. Kết quả gần như lặp lại. "
             "Trong bốn mươi mốt chiếc máy bay ngư lôi xuất kích sáng hôm đó, chỉ khoảng sáu chiếc trở về."),
    dict(id="sacrifice", part=6, vis=("veo", "V12 – mặt biển có mảnh vỡ máy bay và vệt dầu, ánh nắng"),
         hold=2, nar="Một cuộc thảm sát. Nhưng sự hy sinh ấy không vô ích."),
    dict(id="sky_open", part=6, vis=("vfx", "Mặt cắt độ cao: tất cả Zero ở sát mặt biển, bầu trời phía trên trống"),
         nar="Để săn những chiếc máy bay ngư lôi, gần như toàn bộ chiến đấu cơ Zero đã bị kéo xuống sát mặt biển. "
             "Bầu trời phía trên hạm đội Nhật giờ bỏ ngỏ."),
    dict(id="mcclusky", part=6, vis=("photo", "Thẻ chân dung Thiếu tá Wade McClusky"),
         cap=["THIẾU TÁ WADE McCLUSKY"],
         nar="Ở độ cao hơn năm nghìn mét, Thiếu tá Wade McClusky dẫn hơn ba mươi máy bay ném bom bổ nhào của "
             "Enterprise. Cả đội bay đã đến điểm dự kiến, nhưng mặt biển trống trơn. Xăng đang cạn dần."),
    dict(id="search", part=6, vis=("vfx", "Đội hình Dauntless trên mây, mặt biển trống bên dưới"),
         nar="Theo tính toán, lẽ ra ông phải quay về. McClusky quyết định tìm thêm."),
    dict(id="wake", part=6, vis=("vfx", "Nhìn từ trên cao: một tàu khu trục để lại vệt sóng trắng dài như mũi tên"),
         nar="Và rồi, ông nhìn thấy một vệt sóng trắng. Đó là tàu khu trục Arashi của Nhật, vừa săn đuổi một tàu "
             "ngầm Mỹ, đang hối hả chạy về hạm đội. McClusky bám theo vệt sóng ấy."),
    dict(id="leslie", part=6, vis=("map", "Hai mũi tên: Enterprise (McClusky) và Yorktown (Leslie) hội tụ trên hạm đội Nhật"),
         nar="Cùng lúc, từ một hướng khác, mười bảy máy bay ném bom của Yorktown do Thiếu tá Maxwell Leslie dẫn đầu "
             "cũng tiến đến. Hai nhóm không hề hẹn trước. Nhưng cả hai lại đến cùng một thời điểm."),
    dict(id="see", part=6, vis=("vfx", "Góc nhìn từ buồng lái Dauntless: tàu sân bay Nhật hiện ra qua lớp mây"),
         cap=["10:20"],
         nar="Mười giờ hai mươi. Bên dưới, McClusky nhìn thấy các tàu sân bay Nhật. Boong tàu chật kín máy bay "
             "đang chuẩn bị cất cánh."),

    # ---------------- 7. SÁU PHÚT ----------------
    dict(id="t1022", part=7, vis=("card", "Đồng hồ 10:22 đếm giây, nền đen"), hold=1, sfx="tiếng tích tắc, nhạc dừng",
         nar="Mười giờ hai mươi hai."),
    dict(id="peel", part=7, vis=("vfx", "Dauntless lần lượt lật cánh, lao xuống gần thẳng đứng, cánh hãm mở"),
         sfx="tiếng rít bổ nhào",
         nar="Những chiếc Dauntless lần lượt lật cánh, lao xuống gần như thẳng đứng. Do nhầm lẫn mệnh lệnh, "
             "phần lớn cùng lao vào một mục tiêu: tàu Kaga."),
    dict(id="kaga", part=7, vis=("vfx", "Bom liên tiếp trúng tàu Kaga, một quả nổ trước đài chỉ huy"),
         sfx="nổ liên tiếp",
         nar="Kaga trúng ít nhất bốn quả bom. Một quả nổ ngay trước đài chỉ huy, giết chết hạm trưởng và nhiều sĩ quan."),
    dict(id="best", part=7, vis=("vfx", "Ba chiếc Dauntless tách khỏi đội hình, lao về tàu sân bay thứ hai"),
         cap=["ĐẠI ÚY DICK BEST"],
         nar="Thấy vậy, Đại úy Dick Best cùng hai máy bay đi kèm tách ra, lao về chiếc tàu còn lại: Akagi, "
             "soái hạm của Nagumo."),
    dict(id="akagi_hit", part=7, vis=("vfx", "Một quả bom xuyên boong Akagi gần thang nâng máy bay"),
         nar="Chỉ một quả bom của Best trúng đích. Nhưng nó xuyên xuống khoang chứa, giữa những chiếc máy bay đầy "
             "xăng và những quả ngư lôi vừa lắp xong."),
    dict(id="chain", part=7, vis=("vfx", "Nổ dây chuyền bên trong, lửa phụt ra từ thang nâng, boong cong vênh"), hold=3,
         sfx="chuỗi nổ lớn",
         nar="Một chuỗi vụ nổ dây chuyền xé toạc con tàu từ bên trong."),
    dict(id="soryu", part=7, vis=("vfx", "Máy bay Yorktown bổ nhào xuống tàu Soryu, ba quả bom trúng"),
         nar="Cùng lúc, các máy bay của Leslie lao xuống tàu Soryu. Ba quả bom trúng đích. Chỉ vài phút sau, "
             "Soryu biến thành một biển lửa."),
    dict(id="t1028", part=7, vis=("vfx", "Nhìn từ trên cao: ba tàu sân bay cháy, khói đen trải dài"),
         cap=["10:28"], hold=2,
         nar="Mười giờ hai mươi tám. Chỉ sáu phút sau khi những chiếc Dauntless đầu tiên bổ nhào, ba trong bốn tàu "
             "sân bay Nhật đã bốc cháy, không thể cứu vãn."),
    dict(id="gay_sees", part=7, vis=("vfx", "Góc nhìn từ mặt nước: tàu sân bay cháy ở chân trời"),
         nar="Từ mặt nước, George Gay chứng kiến tất cả. Những con tàu từng tấn công Trân Châu Cảng giờ đang cháy "
             "rực ngay trước mắt anh."),
    dict(id="nagumo_leave", part=7, vis=("veo", "V13 – sĩ quan Nhật rời đài chỉ huy đầy khói bằng dây thừng"),
         nar="Trên Akagi, các sĩ quan phải thuyết phục mãi, Nagumo mới chịu rời soái hạm đang cháy, chuyển sang "
             "một tuần dương hạm nhỏ."),
    dict(id="flip", part=7, vis=("card", "Đồ họa cán cân: 4 tàu sân bay Nhật thành 1, Mỹ vẫn 3"),
         nar="Chỉ trong sáu phút, cán cân sức mạnh trên Thái Bình Dương đã đảo ngược."),

    # ---------------- 8. HIRYU PHẢN CÔNG ----------------
    dict(id="not_over", part=8, vis=("vfx", "Tàu sân bay Hiryu nguyên vẹn, rẽ sóng ra khỏi màn khói"),
         sfx="nhạc trầm, căng",
         nar="Nhưng trận chiến vẫn chưa kết thúc. Người Nhật vẫn còn một tàu sân bay: Hiryu. Và chỉ huy của nó là "
             "người không bao giờ chịu khuất phục."),
    dict(id="hiryu_strike", part=8, vis=("vfx", "Máy bay ném bom bổ nhào Nhật cất cánh từ Hiryu"),
         cap=["10:50"],
         nar="Gần mười một giờ, Yamaguchi tung ra mười tám máy bay ném bom bổ nhào và sáu chiếc Zero, "
             "bám theo máy bay Mỹ đang quay về."),
    dict(id="yorktown_hit", part=8, vis=("archive", "Ảnh Hải quân Mỹ: Yorktown trúng bom, khói đen, pháo phòng không"),
         cap=["KHOẢNG 12:00"], sfx="pháo phòng không, nổ",
         nar="Khoảng giữa trưa, máy bay Nhật tìm thấy Yorktown. Phần lớn bị bắn hạ, nhưng ba quả bom vẫn trúng đích. "
             "Yorktown chết máy, đứng yên giữa biển."),
    dict(id="repair", part=8, vis=("veo", "V14 – thủy thủ Mỹ dập lửa trên boong tàu sân bay đầy khói"),
         nar="Thủy thủ Mỹ dập lửa, sửa nồi hơi. Chỉ hơn một giờ sau, Yorktown lại chạy được."),
    dict(id="tomonaga", part=8, vis=("vfx", "Máy bay ngư lôi Nhật cất cánh; cận cảnh thùng xăng cánh trái bị thủng"),
         nar="Yamaguchi tung đợt tấn công thứ hai: mười máy bay ngư lôi. Dẫn đầu vẫn là Tomonaga. Thùng xăng cánh "
             "trái máy bay của ông bị thủng từ trận đánh Midway sáng hôm đó, chưa kịp sửa. Ông biết mình sẽ không "
             "đủ xăng để quay về. Ông vẫn cất cánh."),
    dict(id="torpedo", part=8, vis=("archive", "Ảnh Hải quân Mỹ: máy bay ngư lôi Nhật bay qua làn đạn phòng không về phía Yorktown"),
         cap=["14:40"], sfx="nổ dưới nước",
         nar="Khoảng mười bốn giờ bốn mươi, hai quả ngư lôi đánh trúng Yorktown. Con tàu nghiêng nặng. Hạm trưởng "
             "ra lệnh bỏ tàu. Tomonaga không bao giờ trở về."),
    dict(id="found", part=8, vis=("vfx", "Máy bay trinh sát Mỹ phát hiện Hiryu, radio"),
         radio=[("scout_us", "One carrier, two battleships, three heavy cruisers, four destroyers.",
                 "Một tàu sân bay, hai thiết giáp hạm, ba tuần dương hạm hạng nặng, bốn khu trục hạm.")],
         nar="Nhưng gần như cùng lúc, một máy bay trinh sát của Yorktown đã tìm ra Hiryu."),
    dict(id="hiryu_hit", part=8, vis=("vfx", "Dauntless bổ nhào xuống Hiryu trong ánh hoàng hôn, bốn quả bom trúng"),
         cap=["17:00"],
         nar="Khoảng năm giờ chiều, máy bay của Enterprise, cùng những phi công vừa mất tàu mẹ Yorktown, lao xuống. "
             "Bốn quả bom trúng Hiryu."),
    dict(id="hiryu_burn", part=8, vis=("vfx", "Hiryu cháy trong đêm, ánh lửa phản chiếu trên mặt biển"),
         nar="Chiếc tàu sân bay cuối cùng của Nagumo bốc cháy."),
    dict(id="yamaguchi_end", part=8, vis=("vfx", "Mặt biển lặng lúc rạng sáng, khói mỏng, ánh trăng"), hold=2,
         nar="Sáng hôm sau, khi Hiryu bị đánh chìm, Yamaguchi từ chối rời tàu. Ông ở lại cùng hạm trưởng Kaku Tomeo, "
             "chìm xuống đáy Thái Bình Dương."),

    # ---------------- 9. KẾT ----------------
    dict(id="retreat", part=9, vis=("map", "Mũi tên hạm đội Nhật quay về phía tây"),
         cap=["NGÀY 5 THÁNG 6 NĂM 1942"],
         nar="Ngày năm tháng sáu, Yamamoto ra lệnh rút lui. Chiến dịch Midway thất bại hoàn toàn."),
    dict(id="yorktown_end", part=9, vis=("archive", "Ảnh Hải quân Mỹ: Yorktown nghiêng nặng, thủy thủ trên boong"),
         nar="Người Mỹ cố gắng cứu Yorktown. Nhưng ngày sáu tháng sáu, tàu ngầm Nhật I một trăm sáu mươi tám luồn "
             "qua vòng bảo vệ, phóng ngư lôi kết liễu nó. Sáng ngày bảy tháng sáu, Yorktown lật nghiêng và chìm."),
    dict(id="gay_rescue", part=9, vis=("archive", "Thủy phi cơ PBY Catalina trên mặt nước"),
         nar="Còn George Gay, sau khoảng ba mươi tiếng trôi trên biển, được một thủy phi cơ Catalina cứu sống."),
    dict(id="losses", part=9, vis=("card", "Bảng tổn thất hai bên, số lớn hiện dần"),
         cap=["NHẬT: 4 TÀU SÂN BAY – ~3.000 NGƯỜI", "MỸ: 1 TÀU SÂN BAY – ~300 NGƯỜI"],
         nar="Tổng kết, Nhật mất bốn tàu sân bay, một tuần dương hạm, khoảng hai trăm năm mươi máy bay và hơn ba "
             "nghìn người, trong đó có nhiều thợ máy và phi công giàu kinh nghiệm. Mỹ mất một tàu sân bay, một tàu "
             "khu trục, khoảng một trăm năm mươi máy bay và hơn ba trăm người."),
    dict(id="meaning", part=9, vis=("map", "Bản đồ Thái Bình Dương, mũi tên phản công Mỹ bắt đầu xuất hiện"),
         nar="Nhật Bản không bao giờ bù đắp được những tổn thất ấy. Sau Midway, quân Nhật mất thế chủ động trên Thái Bình "
             "Dương. Từ đây, người Mỹ bắt đầu phản công."),
    dict(id="myth", part=9, vis=("card", "Trang hồi ký cũ, dòng chữ '5 PHÚT' bị gạch đi"),
         nar="Nhiều năm sau, một sĩ quan Nhật viết trong hồi ký rằng, chỉ cần thêm năm phút nữa, máy bay Nhật đã "
             "kịp cất cánh, và lịch sử có thể đã khác. Các nhà sử học ngày nay cho rằng điều đó không đúng. "
             "Khi bom rơi xuống, các tàu Nhật còn xa mới sẵn sàng."),
    dict(id="not_luck", part=9, vis=("photo", "Ghép chân dung: Rochefort, công nhân xưởng tàu, Waldron, McClusky"),
         nar="Midway không được quyết định chỉ bởi may mắn. Nó được quyết định bởi những người giải mã trong căn hầm "
             "không cửa sổ, những công nhân sửa tàu ba ngày đêm, những phi công ngư lôi biết mình khó trở về, "
             "và một phi công dám bám theo một vệt sóng giữa đại dương."),
    dict(id="close", part=9, vis=("vfx", "Mặt biển lúc hoàng hôn, một chiếc Dauntless bay xa dần"), hold=3,
         sfx="nhạc dây/piano kết",
         nar="Sáu tháng để xây dựng một đế chế trên biển. Và chỉ sáu phút để nó bắt đầu sụp đổ."),
    dict(id="end", part=9, vis=("card", "Màn hình kết: nguồn tư liệu, nút đăng ký, video tiếp theo"), hold=15),
]

SPEAKERS = {
    "pby": "Phi công thủy phi cơ PBY (tiếng Anh, bộ đàm)",
    "tomonaga": "Đại úy Tomonaga (tiếng Nhật, điện đài)",
    "scout": "Thủy phi cơ trinh sát tàu Tone (tiếng Nhật, điện đài)",
    "scout_us": "Máy bay trinh sát Yorktown (tiếng Anh, bộ đàm)",
}

# Clip Veo (8 giây, 16:9). Ghi "hình ảnh minh họa" góc dưới khi dựng.
STYLE = ("1940s WWII documentary look, realistic, natural light, subtle film grain, no text, no logos, "
         "no modern objects")
VEO_PROMPTS = {
    "V01": "Aerial shot high above the Pacific Ocean, four Japanese WWII aircraft carriers sailing in formation "
           "with long white wakes, escort destroyers around them, morning sun, scattered clouds. " + STYLE,
    "V02": "On the flight deck of a WWII Japanese aircraft carrier, rows of parked propeller planes with "
           "wings folded, deck crew in white and brown uniforms running between them, wind, morning light. " + STYLE,
    "V03": "WWII Japanese battle fleet moving through morning sea mist, rising sun naval ensign flapping on a "
           "warship mast in the foreground, slow push-in. " + STYLE,
    "V04": "Windowless basement office in 1942, US Navy codebreakers in shirtsleeves at desks covered with "
           "paper and index cards, typewriters, cigarette smoke under bare light bulbs, slow dolly. " + STYLE,
    "V05": "1940s naval headquarters, officers in khaki uniforms leaning over a large map table of the Pacific, "
           "one pushes small ship models with a long stick, tense, warm lamp light. " + STYLE,
    "V06": "Night in a dry dock, workers welding the hull of a large WWII aircraft carrier, bright sparks "
           "falling, searchlights, steam. " + STYLE,
    "V07": "A WWII PBY Catalina flying boat flying low over the open ocean at dawn, camera tracking alongside, "
           "orange sky. " + STYLE,
    "V08": "Dawn on a WWII Japanese aircraft carrier, propeller fighter planes taking off one after another, "
           "deck crew waving caps, exhaust smoke, low sun. " + STYLE,
    "V09": "Inside the hangar deck of a WWII aircraft carrier, mechanics pushing a heavy torpedo on a "
           "wheeled cart under a propeller plane, chains and hoists, sweat, dim yellow light. " + STYLE,
    "V10": "Bridge of a WWII Japanese aircraft carrier, officers in dark uniforms reading a paper message, "
           "binoculars, tense faces, ocean visible through windows. " + STYLE,
    "V11": "WWII US aircraft carrier deck, dark blue propeller dive bombers taking off one by one, flight deck "
           "officer waving a flag, sailors watching, bright morning. " + STYLE,
    "V12": "Calm ocean surface with floating aircraft wreckage pieces and an oil slick, sunlight glittering, "
           "slow aerial pull-back, somber. " + STYLE,
    "V13": "Smoke-filled bridge of a burning warship, officers climbing out of a window down a rope, flames "
           "below, chaos. " + STYLE,
    "V14": "US Navy sailors fighting fires with hoses on the deck of a damaged WWII aircraft carrier, thick "
           "black smoke, water spray. " + STYLE,
}
