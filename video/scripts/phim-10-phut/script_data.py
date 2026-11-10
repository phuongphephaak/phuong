"""Full script for "HMS Coventry – Ngày cuối cùng" (~10 min).

Each scene:
  id       unique id
  vis      visual spec: (kind, params)   kinds: card, photo, map, vfx, credits
  cap      on-screen caption lines (first line bold) or None
  nar      Vietnamese narration (None = no narration)
  radio    list of (voice, spoken text, Vietnamese subtitle)
  radio_first  play radio lines before narration
  sfx      list of (name, offset_sec, volume)
  min      minimum scene length in seconds
Radio dialogue is a dramatised reconstruction, not original recordings.
"""

NARRATOR = "47rM9DW5VmjOw23BVHWi"          # Tuan Anh – deep Vietnamese (northern)
VOICES = {
    "ops": "onwK4e9ZLuTAKqWW03F9",        # Daniel – British, steady (Coventry ops room)
    "capt": "JBFqnCBsd6RMkjVDRZzb",       # George – British (captain / Broadsword)
    "pilot1": "pNInz6obpgDQGcFmaJgB",     # Adam – Argentine lead pilot (Spanish)
    "pilot2": "N2lVS1w4EtoT3dr4eOWO",     # Callum – Argentine wingman (Spanish)
}

SCENES = [
    # ------------------------------------------------------------------ cold open
    dict(id="open_raid", vis=("clip", {"src": "raid2", "start": 0.9}), cap=None, nar=None, radio=[], min=5,
         sfx=[("jet_flyby", 0.0, 1.0), ("aa_fire", 0.0, 0.7), ("explosion", 1.45, 1.0)]),
    dict(id="open_pov", vis=("vfx", {"kind": "pov", "seed": 1}), cap=None, nar=None, min=7,
         radio=[("pilot1", "Aquí Líder. Rumbo cero ocho cero. Muy bajo sobre el agua.",
                 "Trưởng biên đội đây. Hướng 080. Bay rất thấp trên mặt nước."),
                ("pilot2", "Recibido, Líder. Lo sigo.", "Rõ, trưởng biên đội. Tôi bám theo.")],
         sfx=[("jet_cockpit", 0, 0.7)]),
    dict(id="open_radar", vis=("vfx", {"kind": "radar", "mode": "alarm"}), cap=None, nar=None, min=6,
         radio=[("ops", "Air raid warning red! Two fast movers, very low, closing from the west!",
                 "Báo động đỏ! Hai máy bay tốc độ cao, bay rất thấp, đang áp sát từ phía tây!")],
         sfx=[("alarm", 0.3, 0.28), ("ops_room", 0, 0.5)]),
    dict(id="open_attack", vis=("clip", {"src": "attack", "start": 0.5}), cap=None, nar=None, radio=[], min=4.5,
         sfx=[("aa_fire", 0.0, 0.8), ("jet_flyby", 0.4, 1.0), ("jet_flyby", 1.2, 0.9)]),
    dict(id="open_impact", vis=("clip", {"src": "impact", "start": 0.0}), cap=None, nar=None, radio=[], min=4.2,
         sfx=[("explosion", 0.55, 1.0), ("explosion", 1.1, 0.9), ("explosion", 1.7, 1.0)]),
    dict(id="title", vis=("card", {"lines": ["HMS COVENTRY", "Ngày cuối cùng · 25 tháng 5, 1982"]}), cap=None,
         nar=None, radio=[], min=6, sfx=[("boom_far", 0.4, 0.8)]),

    # ------------------------------------------------------------------ act 1: context
    dict(id="map_atlantic", vis=("map", {"kind": "atlantic"}), cap=["2/4/1982", "Argentina đổ bộ lên quần đảo Falkland"],
         nar="Ngày 2 tháng 4 năm 1982, quân đội Argentina đổ bộ lên quần đảo Falkland, một vùng lãnh thổ hải ngoại "
             "của Anh nằm giữa Nam Đại Tây Dương, mà người Argentina gọi là Malvinas. Chỉ vài ngày sau, một hạm đội "
             "đặc nhiệm Anh rời cảng, bắt đầu hành trình gần mười ba nghìn cây số về phía nam.",
         radio=[], min=8, sfx=[]),
    dict(id="map_region", vis=("map", {"kind": "region"}), cap=["Quần đảo Falkland (Malvinas)", "Nam Đại Tây Dương"],
         nar="Quần đảo nằm cách bờ biển Argentina chỉ khoảng năm trăm cây số. Với không quân Argentina, đó là "
             "khoảng cách đủ gần để tấn công, nhưng đủ xa để mỗi phi vụ đều là một cuộc đua với nhiên liệu.",
         radio=[], min=8, sfx=[]),
    dict(id="fleet", vis=("vfx", {"kind": "fleet", "seed": 2}), cap=["Hạm đội đặc nhiệm Anh", "Nam Đại Tây Dương, tháng 4–5/1982"],
         nar="Đó là một canh bạc lớn. Hạm đội ở cách nhà nửa vòng Trái Đất, trong khi máy bay Argentina chỉ cần cất "
             "cánh từ đất liền, cách quần đảo vài trăm cây số.",
         radio=[], min=7, sfx=[("ship_sea", 0, 0.5)]),
    dict(id="hermes", vis=("photo", {"key": "hermes", "pan": "lr"}), cap=["HMS Hermes và HMS Broadsword", "1982"],
         nar="Trung tâm của hạm đội là hai tàu sân bay Hermes và Invincible, mang theo những chiếc tiêm kích Sea Harrier. "
             "Nhưng số tiêm kích quá ít để che chở toàn bộ đội tàu trước hàng trăm phi vụ của không quân Argentina.",
         radio=[], min=7, sfx=[]),
    dict(id="coventry_intro", vis=("photo", {"key": "ship1", "pan": "lr"}), cap=["HMS Coventry (D118)", "Tàu khu trục phòng không Type 42"],
         nar="Lá chắn phòng không của hạm đội dựa rất nhiều vào những tàu khu trục Type 42 như HMS Coventry. "
             "Được đưa vào biên chế năm 1978, Coventry mang tên lửa phòng không tầm xa Sea Dart cùng hệ thống radar "
             "hiện đại, được thiết kế để bắn hạ máy bay đối phương từ khoảng cách hàng chục cây số.",
         radio=[], min=8, sfx=[]),
    dict(id="seadart", vis=("vfx", {"kind": "seadart"}), cap=None,
         nar="Trong những tuần đầu, Coventry tỏ ra rất đáng gờm. Tên lửa Sea Dart của nó đã bắn rơi một trực thăng "
             "Puma của Argentina, và con tàu được ghi nhận với nhiều chiến công phòng không.",
         radio=[], min=7, sfx=[("missile", 0.8, 1.0)]),
    dict(id="sheffield", vis=("vfx", {"kind": "fleet", "seed": 5, "burning": True}),
         cap=["4/5/1982 · HMS Sheffield", "Mô phỏng"],
         nar="Nhưng ngày 4 tháng 5, tàu cùng lớp HMS Sheffield trúng một tên lửa Exocet và bốc cháy. Sáu ngày sau, "
             "nó chìm khi đang được kéo đi. Đó là tàu chiến đầu tiên Hải quân Hoàng gia Anh mất trong chiến đấu "
             "kể từ Thế chiến thứ hai.",
         radio=[], min=7, sfx=[("fire_crackle", 0, 0.5)]),

    # ------------------------------------------------------------------ act 2: San Carlos
    dict(id="map_sancarlos", vis=("map", {"kind": "sancarlos"}), cap=["21/5/1982", "Đổ bộ vào eo San Carlos"],
         nar="Ngày 21 tháng 5, quân Anh đổ bộ vào eo San Carlos, ở bờ tây đảo Đông Falkland. Để bảo vệ bãi đổ bộ, "
             "các tàu chiến phải hoạt động trong vùng nước hẹp, bị những ngọn đồi trọc bao quanh.",
         radio=[], min=8, sfx=[]),
    dict(id="raid1", vis=("vfx", {"kind": "raid", "seed": 11}), cap=["Eo San Carlos", "Mô phỏng"],
         nar="Phi công Argentina lao xuống từ sau những ngọn đồi, bay sát mặt nước và thả bom chỉ cách mục tiêu "
             "vài trăm mét. Lính Anh gọi nơi này là Hẻm Bom.",
         radio=[("ops", "Raid, raid! Skyhawks over the hills, two-seven-zero!",
                 "Không kích! Skyhawk vượt qua dãy đồi, hướng 270!")], radio_first=False,
         min=8, sfx=[("jet_flyby", 1.2, 0.9), ("aa_fire", 0.8, 0.6), ("splash", 3.0, 0.8)]),
    dict(id="raid_wide", vis=("vfx", {"kind": "raid", "seed": 51}), cap=None, nar=None, min=7,
         radio=[], sfx=[("jet_flyby", 0.7, 1.0), ("aa_fire", 0.3, 0.8), ("splash", 2.3, 0.9), ("splash", 2.7, 0.8)]),
    dict(id="raid2", vis=("vfx", {"kind": "raid", "seed": 23, "hit": True}), cap=None,
         nar="Ngay trong ngày đầu tiên, khinh hạm HMS Ardent bị đánh chìm. Hai ngày sau, đến lượt HMS Antelope.",
         radio=[], min=7, sfx=[("jet_flyby", 0.8, 0.9), ("explosion", 2.6, 0.9), ("aa_fire", 0.4, 0.5)]),
    dict(id="raid4", vis=("vfx", {"kind": "raid", "seed": 64, "hit": True}), cap=None, nar=None, min=8,
         radio=[("pilot2", "¡Fuego antiaéreo muy intenso! ¡Salgo bajo!", "Hỏa lực phòng không rất dày! Tôi thoát ra ở độ cao thấp!")],
         sfx=[("aa_fire", 0.2, 0.8), ("jet_flyby", 0.9, 1.0), ("explosion", 2.6, 0.9)]),
    dict(id="raid3", vis=("vfx", {"kind": "raid", "seed": 37, "shootdown": True}), cap=None,
         nar="Cái giá cho phi công Argentina cũng rất đắt. Nhiều máy bay bị bắn rơi trên bầu trời San Carlos, "
             "bởi tên lửa, pháo phòng không và những chiếc Sea Harrier tuần tiễu phía trên.",
         radio=[("pilot2", "¡Me dieron! ¡Me dieron! ¡Eyecto!", "Tôi trúng đạn! Tôi trúng đạn! Tôi nhảy dù!")],
         min=8, sfx=[("aa_fire", 0.3, 0.7), ("jet_flyby", 1.0, 0.9), ("boom_far", 3.2, 0.9)]),
    dict(id="antelope", vis=("photo", {"key": "antelope", "zoom": [1.0, 1.15]}), cap=["23/5/1982 · HMS Antelope", "Eo San Carlos"],
         nar="Một quả bom găm vào Antelope nhưng không nổ. Khi đội chuyên gia đang tìm cách tháo ngòi, nó phát nổ. "
             "Con tàu cháy suốt đêm và chìm vào ngày hôm sau.",
         radio=[], min=7, sfx=[]),
    dict(id="a4", vis=("photo", {"key": "a4faa", "pan": "rl"}), cap=["Douglas A-4 Skyhawk", "Không quân Argentina"],
         nar="Vũ khí chủ lực trong những đợt tấn công này là A-4 Skyhawk, một cường kích nhỏ và đã cũ. Không có tên lửa "
             "chống hạm, phi công phải bay thẳng qua đầu mục tiêu để thả bom thông thường. Nhiều quả bom được thả "
             "ở độ cao quá thấp, không kịp kích hoạt ngòi nổ.",
         radio=[], min=8, sfx=[]),

    # ------------------------------------------------------------------ act 3: the picket
    dict(id="map_picket", vis=("map", {"kind": "picket"}), cap=["Phía tây bắc eo Falkland", "Gần đảo Pebble"],
         nar="Để giảm áp lực cho San Carlos, Coventry và khinh hạm Broadsword được đưa ra phía tây bắc eo Falkland, "
             "gần đảo Pebble. Nhiệm vụ của chúng là đánh chặn máy bay Argentina trước khi tới được bãi đổ bộ, "
             "và kéo các đòn tấn công về phía mình.",
         radio=[], min=9, sfx=[]),
    dict(id="broadsword", vis=("photo", {"key": "broadsword"}), cap=["HMS Broadsword (F88)", "Khinh hạm Type 22"],
         nar="Hai con tàu tạo thành cặp đôi Type 42 và Type 22. Sea Dart tầm xa của Coventry đánh những máy bay ở xa, "
             "còn Sea Wolf tầm ngắn của Broadsword chặn những kẻ lọt lưới bay sát mặt biển.",
         radio=[], min=7, sfx=[]),
    dict(id="radar_calm", vis=("vfx", {"kind": "radar", "mode": "calm"}), cap=["Phòng tác chiến", "Mô phỏng"],
         nar="Thuyền trưởng Coventry, David Hart Dyke, hiểu rõ vị trí này nguy hiểm đến mức nào. Sau này ông viết "
             "rằng nhiệm vụ đó gần như là một sự hy sinh.",
         radio=[], min=7, sfx=[("ops_room", 0, 0.5)]),
    dict(id="morning", vis=("vfx", {"kind": "fleet", "seed": 7, "pair": True}), cap=["25/5/1982", "Ngày Quốc khánh Argentina"],
         nar="Ngày 25 tháng 5 là ngày Quốc khánh của Argentina. Ai cũng đoán rằng không quân Argentina sẽ tung ra "
             "những đòn quyết liệt nhất.",
         radio=[], min=7, sfx=[("ship_sea", 0, 0.5)]),

    # ------------------------------------------------------------------ act 4: the attack
    dict(id="takeoff_pov", vis=("vfx", {"kind": "pov", "seed": 4}), cap=["Căn cứ Río Gallegos", "Hai cặp A-4 cất cánh"],
         nar="Buổi chiều, từ đất liền, hai cặp A-4 Skyhawk của Không quân Argentina cất cánh, hướng về phía hai con tàu.",
         radio=[("pilot1", "Formación, mantengan altura mínima. Silencio de radio.",
                 "Cả biên đội, giữ độ cao tối thiểu. Im lặng vô tuyến.")],
         min=7, sfx=[("jet_cockpit", 0, 0.7)]),
    dict(id="map_attack", vis=("map", {"kind": "attack"}), cap=None,
         nar="Họ bay sát mặt biển, vòng qua phía bắc quần đảo. Ở độ cao đó, radar trên tàu gần như không thể "
             "nhìn thấy họ cho đến phút chót.",
         radio=[], min=8, sfx=[("jet_approach", 4.0, 0.8)]),
    dict(id="lowlevel", vis=("vfx", {"kind": "pov", "seed": 12}), cap=None, nar=None, min=7,
         radio=[("pilot1", "Cinco minutos al blanco. Mantengan la formación.", "Năm phút nữa tới mục tiêu. Giữ đội hình.")],
         sfx=[("jet_cockpit", 0, 0.7)]),
    dict(id="radar_contact", vis=("vfx", {"kind": "radar", "mode": "alarm"}), cap=None, nar=None, min=6,
         radio=[("ops", "Contact! Two aircraft, very low, bearing two-five-zero, range fifteen miles!",
                 "Phát hiện mục tiêu! Hai máy bay, rất thấp, phương vị 250, cự ly 15 hải lý!"),
                ("capt", "Air raid warning red. Hands to action stations!",
                 "Báo động đỏ. Tất cả vào vị trí chiến đấu!")],
         sfx=[("alarm", 0.2, 0.28), ("ops_room", 0, 0.5)]),
    dict(id="action", vis=("photo", {"key": "action"}), cap=None,
         nar="Trên cả hai tàu, thủy thủ đội mũ trùm chống lóa, lao vào vị trí chiến đấu.",
         radio=[], min=5, sfx=[("alarm", 0.0, 0.18)]),
    dict(id="radar_nolock", vis=("vfx", {"kind": "radar", "mode": "clutter"}), cap=None,
         nar="Nhưng radar điều khiển Sea Dart không thể tách những chiếc A-4 bay thấp khỏi nền đất liền phía sau. "
             "Tên lửa không thể khai hỏa.",
         radio=[("ops", "No lock! Sea Dart can't separate them from the land!",
                 "Không khóa được! Sea Dart không tách được chúng khỏi nền đất liền!")], radio_first=True,
         min=7, sfx=[("ops_room", 0, 0.5)]),
    dict(id="attack_pov", vis=("vfx", {"kind": "pov", "seed": 8, "ships": True}), cap=None,
         nar="Với phi công Argentina, đây là những giây phút căng thẳng nhất. Bay ở độ cao chỉ vài chục mét, "
             "tốc độ rất lớn, họ phải lao thẳng vào làn đạn phòng không để có thể thả bom trúng mục tiêu.",
         radio=[("pilot1", "¡Ahí están! ¡Vamos, vamos!", "Chúng kia rồi! Lao vào! Lao vào!")],
         min=8, sfx=[("jet_cockpit", 0, 0.7)]),
    dict(id="approach", vis=("vfx", {"kind": "approach"}), cap=None, nar=None, min=5,
         radio=[("pilot1", "¡Blancos a la vista! Dos buques, a las doce.", "Thấy mục tiêu! Hai tàu, hướng 12 giờ.")],
         sfx=[("jet_approach", 0, 1.0)]),
    dict(id="bounce", vis=("vfx", {"kind": "bounce"}), cap=["Đợt tấn công thứ nhất", "Nhắm vào HMS Broadsword"],
         nar="Cặp A-4 đầu tiên nhắm vào Broadsword. Hệ thống Sea Wolf bất ngờ bị kẹt. Một quả bom nảy lên khỏi mặt nước, "
             "xuyên qua sàn đáp trực thăng, phá nát chiếc Lynx, rồi văng ra biển mà không phát nổ.",
         radio=[], min=9, sfx=[("jet_flyby", 1.0, 1.0), ("splash", 2.4, 0.9), ("metal_hit", 3.0, 1.0)]),
    dict(id="radar_second", vis=("vfx", {"kind": "radar", "mode": "alarm", "seed": 3}), cap=None,
         nar="Vài phút sau, cặp thứ hai xuất hiện. Lần này Sea Wolf đã được khởi động lại và bám được mục tiêu.",
         radio=[("capt", "Second pair inbound! Sea Wolf tracking!", "Cặp thứ hai đang lao tới! Sea Wolf đã bám mục tiêu!")],
         min=7, sfx=[("alarm", 0.2, 0.22), ("ops_room", 0, 0.5)]),
    dict(id="map_geometry", vis=("map", {"kind": "geometry"}), cap=None,
         nar="Nhưng đúng lúc đó, Coventry bẻ lái gấp, và vô tình đi thẳng vào đường bắn của Broadsword. "
             "Sea Wolf không thể khai hỏa.",
         radio=[("capt", "Check fire, check fire! Coventry is in the line of fire!",
                 "Ngừng bắn! Ngừng bắn! Coventry đang chắn đường bắn!")],
         min=9, sfx=[]),
    dict(id="attack", vis=("vfx", {"kind": "attack"}), cap=None,
         nar="Coventry chỉ còn pháo và súng máy để chống trả.",
         radio=[("ops", "All guns, engage! Engage!", "Tất cả súng, khai hỏa! Khai hỏa!")], radio_first=True,
         min=5, sfx=[("aa_fire", 0.3, 0.8), ("jet_flyby", 0.9, 1.0), ("jet_flyby", 1.7, 0.9)]),
    dict(id="impact", vis=("vfx", {"kind": "impact"}), cap=None, nar=None, radio=[], min=6.5,
         sfx=[("explosion", 0.55, 1.0), ("explosion", 1.1, 0.9), ("explosion", 1.7, 1.0)]),
    dict(id="bombs", vis=("vfx", {"kind": "aftermath"}), cap=["Ba quả bom trúng mạn trái", "Hai quả phát nổ"],
         nar="Ba quả bom xuyên vào mạn trái. Một quả không nổ. Hai quả còn lại phát nổ, một quả bên dưới phòng máy tính "
             "và phòng tác chiến, quả kia trong buồng máy phía trước.",
         radio=[], min=8, sfx=[("fire_crackle", 0, 0.6)]),

    # ------------------------------------------------------------------ act 5: the sinking
    dict(id="burning", vis=("vfx", {"kind": "aftermath"}), cap=None, nar=None, min=8,
         radio=[("ops", "Fire in the computer room! Damage control parties, close up!", "Cháy ở phòng máy tính! Các đội kiểm soát hư hại, vào vị trí!")],
         sfx=[("fire_crackle", 0, 0.7), ("alarm", 0.5, 0.15)]),
    dict(id="radar_dark", vis=("vfx", {"kind": "radar", "mode": "dark"}), cap=None,
         nar="Nước tràn qua vách ngăn giữa hai buồng máy. Điện mất. Khói đen đặc kín các khoang. "
             "Con tàu bắt đầu nghiêng sang trái.",
         radio=[], min=8, sfx=[("creak", 0.5, 0.7), ("fire_crackle", 0, 0.4)]),
    dict(id="abandon", vis=("vfx", {"kind": "sink", "part": 1}), cap=None,
         nar="Chỉ vài phút sau, lệnh rời tàu được đưa ra.",
         radio=[("capt", "Abandon ship. Abandon ship.", "Rời tàu. Tất cả rời tàu.")], radio_first=False,
         min=11, sfx=[("creak", 0.0, 0.7)]),
    dict(id="sink2", vis=("vfx", {"kind": "sink", "part": 2}), cap=None,
         nar="Thủy thủ nhảy xuống làn nước lạnh buốt của Nam Đại Tây Dương, leo lên những chiếc bè cứu sinh.",
         radio=[], min=9, sfx=[("creak", 0.5, 0.8), ("water_rush", 2.0, 0.6)]),
    dict(id="sink3", vis=("vfx", {"kind": "sink", "part": 3}), cap=["Chưa đầy 20 phút sau khi trúng bom", "Coventry lật úp và chìm"],
         nar=None, radio=[], min=18, sfx=[("water_rush", 0.5, 0.8), ("creak", 3.0, 0.8), ("creak", 9.0, 0.6), ("bubbles", 12.5, 0.8)]),
    dict(id="rescue", vis=("vfx", {"kind": "rescue"}), cap=None,
         nar="Broadsword quay lại, cùng các trực thăng cứu được 170 người. Mười chín thủy thủ của Coventry "
             "đã không bao giờ trở về.",
         radio=[], min=9, sfx=[("helicopter", 0, 0.6)]),

    dict(id="rescue2", vis=("vfx", {"kind": "rescue", "seed": 2}), cap=["Broadsword cứu 170 người", "Mô phỏng"],
         nar="Nhiều người bị bỏng, bị thương, ngấm nước lạnh hàng chục phút trước khi được kéo lên. "
             "Thuyền trưởng Hart Dyke cũng bị thương, nhưng sống sót.",
         radio=[("capt", "Broadsword, we have survivors in the water. Send everything you've got.",
                 "Broadsword, có người sống sót dưới nước. Đưa mọi thứ có thể tới đây.")],
         min=8, sfx=[("helicopter", 0, 0.6)]),

    # ------------------------------------------------------------------ act 6: aftermath
    dict(id="conveyor", vis=("vfx", {"kind": "fleet", "seed": 9, "burning": True, "big": True}),
         cap=["25/5/1982 · Atlantic Conveyor", "Mô phỏng"],
         nar="Cũng trong ngày hôm đó, tàu container Atlantic Conveyor trúng tên lửa Exocet. Ngày 25 tháng 5 trở thành "
             "một trong những ngày đen tối nhất của hạm đội Anh.",
         radio=[], min=8, sfx=[("fire_crackle", 0, 0.5)]),
    dict(id="map_end", vis=("map", {"kind": "end"}), cap=["14/6/1982", "Quân Argentina ở Stanley đầu hàng"],
         nar="Dù vậy, quân Anh vẫn giữ vững được San Carlos. Ngày 14 tháng 6, quân Argentina ở Stanley đầu hàng. "
             "Cuộc chiến kéo dài 74 ngày, cướp đi sinh mạng của 649 quân nhân Argentina, 255 quân nhân Anh "
             "và 3 người dân trên đảo.",
         radio=[], min=10, sfx=[]),
    dict(id="wreck", vis=("vfx", {"kind": "calm"}), cap=["51°03′S · 59°42′W", "Khu vực được bảo vệ"],
         nar="Xác HMS Coventry vẫn nằm dưới đáy biển, ở độ sâu khoảng một trăm mét phía bắc đảo Pebble. "
             "Nơi đây được pháp luật Anh bảo vệ như một khu mộ chiến tranh.",
         radio=[], min=9, sfx=[]),
    dict(id="lesson", vis=("photo", {"key": "ship2", "dark": True, "zoom": [1.15, 1.0]}), cap=None,
         nar="Những bài học từ Coventry, về radar không thể khóa mục tiêu bay thấp và về sự phối hợp giữa các con tàu, "
             "đã thay đổi cách hải quân nhiều nước thiết kế hệ thống phòng không trong nhiều thập kỷ sau đó.",
         radio=[], min=9, sfx=[]),
    dict(id="memorial", vis=("card", {"lines": ["Tưởng nhớ 19 thủy thủ HMS Coventry", "25 · 5 · 1982"]}), cap=None,
         nar=None, radio=[], min=7, sfx=[]),
    dict(id="credits", vis=("credits", {}), cap=None, nar=None, radio=[], min=9, sfx=[]),
]

# music cues: (track, start scene id, volume)
MUSIC = [("music_tension", "map_atlantic", 0.35), ("music_battle", "takeoff_pov", 0.40),
         ("music_mourn", "abandon", 0.40)]
