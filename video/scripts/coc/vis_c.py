"""Visual + sound plan for script_coc.SCENES (by id).
Archive: f = USAF 'There Is a Way' (F-105, 1967), n = 'The American Navy in Vietnam' (1967),
h = 'Carpet Bombing of Hanoi' (NARA), p = 'Air Strike – South Vietnam' (NARA, 1965),
a = USAF Film Report 'Airstrikes North 1966', g = '366th TFW – The Gunfighters' (USAF)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *segs: ("arch", {"segs": [list(s) for s in segs]})
P = lambda name, **k: ("photo", dict(key=name, **k))
X = lambda kind, **spec: ("gfx", dict(kind=kind, spec=spec))
T, Q = "t", "pa"
YEL, WHT, CY, RD = (255, 215, 90), (255, 255, 255), (90, 200, 255), (255, 80, 70)


def stat(photo, *lines):
    return X("stat", photo=photo, lines=[list(l) for l in lines])


VIS = {
    # 1 hook
    "o_date": A(["f", 0.2, 5.3, T], ["f", 977, 5.5, T]),
    "o_two": A(["f", 1160, 3.2, T], ["a", 962, 3.5, Q], ["f", 917, 3.5, T]),
    "o_role": A(["a", 966, 4.5, Q], ["f", 1022, 5.4, T]),
    "o_turn": A(["f", 1099.5, 2.6, T], ["p", 117.5, 4.5, T], ["a", 436, 2.5, Q]),
    "o_name": X("phrase", photo="mig4324", text="CHIM CẮT SỐ 2", size=150, sub="9 MÁY BAY MỸ BỊ BẮN RƠI"),
    "title": X("title", photo="mig4324", l1="CHIM CẮT SỐ 2", l2="NGUYỄN VĂN CỐC"),
    "sting": X("sting"),
    # 2 childhood
    "village": A(["h", 270, 5, T], ["h", 286, 4, T]),
    "father": X("phrase", photo="fr_sunset", text="1947", size=170, sub="NGƯỜI CHA BỊ QUÂN PHÁP SÁT HẠI · CẬU BÉ MỚI LÊN 5"),
    "sky_boy": P("fr_skywatch"),
    "select": A(["h", 282, 3.8, T], ["h", 334, 3.8, T], ["h", 36, 4, T]),
    "catbi": A(["f", 828, 3, T], ["f", 917, 3.5, T], ["h", 290, 3.5, T]),
    "ussr": stat("mig21pf", ["120 HỌC VIÊN", 120, WHT], ["CHỈ 17 NGƯỜI TỐT NGHIỆP PHI CÔNG MiG-17", 52, YEL], ["NGUYỄN VĂN CỐC LÀ MỘT TRONG SỐ ĐÓ", 40, CY]),
    "conv": P("mig21pf"),
    # 3 MiG-21
    "mig21": P("mig4324"),
    "two_missile": X("phrase", photo="mig21b52", text="CHỈ 2 TÊN LỬA", size=150, sub="KHÔNG CÓ PHÁO · BẮN TRƯỢT CẢ HAI LÀ HẾT CÁCH ĐÁNH"),
    "f4": A(["a", 920, 4, Q], ["a", 946, 4, Q], ["a", 950, 4.5, Q]),
    "radar": stat("f4c_ubon", ["F-4 PHANTOM: 60–70 KM", 96, RD], ["MiG-21: 15–16 KM", 96, CY], ["TẦM PHÁT HIỆN CỦA RADAR", 40, WHT]),
    "gci": A(["h", 44, 5, T], ["f", 1034, 5, T], ["a", 966, 3, Q]),
    "return": P("vpaf_pilots"),
    "rt": A(["g", 280, 3.5, Q], ["g", 290, 4, Q], ["a", 62, 3.5, Q], ["a", 266, 3.5, Q]),
    # 4 Bolo
    "bolo_date": A(["a", 924, 4, Q], ["a", 930, 4, Q]),
    "bolo_trap": A(["a", 946, 4, Q], ["a", 950, 4, Q], ["a", 986, 4, Q]),
    "bolo_cloud": A(["a", 822, 3.5, Q], ["a", 840, 3.5, Q]),
    "bolo_shot": A(["a", 597, 3.5, Q], ["a", 606, 3, Q], ["a", 860, 3, Q]),
    "bolo_lesson": stat("vpaf_pilots", ["02/01/1967", 130, YEL], ["BÀI HỌC ĐẮT GIÁ", 70, WHT]),
    "bolo_why": P("olds_crew"),
    # 5 first kill
    "do": X("portrait", photo="do_card", name="Nguyễn Ngọc Độ", sub="BIÊN ĐỘI TRƯỞNG · NGƯỜI KÈM CẶP", bg="photo", bgphoto="mig21pf"),
    "rule": stat("mig4324", ["SỐ 1 CÔNG KÍCH", 110, YEL], ["SỐ 2 YỂM HỘ", 110, WHT]),
    "scramble": A(["f", 1628, 4, T], ["f", 917, 3.5, T], ["f", 828, 3, T]),
    "approach": A(["f", 1160, 3.2, T], ["f", 0.2, 4, T], ["f", 977, 4, T]),
    "do_fire": A(["f", 1103, 2.2, T], ["f", 1106, 1.6, T], ["f", 1099.5, 2.6, T], ["p", 117.5, 3.5, T]),
    "coc_ask": A(["f", 1098, 4.2, T], ["f", 1119.5, 2.4, T]),
    "coc_fire": A(["f", 1094, 3.5, T], ["p", 119, 3.5, T], ["a", 436, 2.5, Q]),
    "cheer": A(["f", 1034, 4, T], ["f", 1022, 5.4, T]),
    "first_kill": stat("fr_clouds", ["30/04/1967", 120, YEL], ["2 F-105 BỊ BẮN RƠI", 80, WHT], ["CẢ BIÊN ĐỘI TRỞ VỀ AN TOÀN", 44, CY]),
    "goal": X("portrait", photo="coc_card", name="Nguyễn Văn Cốc", sub="\"ĐÃ PHÁ ĐƯỢC DỚP, NHỮNG BÀN SAU ĐẾN DỄ HƠN\"", bg="photo", bgphoto="mig4324"),
    # 6 falcon
    "idea": X("phrase", photo="mig21b52", text="SỐ 2 CŨNG CÓ THỂ TẤN CÔNG", size=110, sub="ĐỪNG BỎ PHÍ MỘT NỬA SỨC MẠNH CỦA BIÊN ĐỘI"),
    "falcon": A(["f", 1160, 3.2, T], ["f", 1106, 1.6, T], ["f", 1098, 4.2, T], ["p", 117.5, 3, T]),
    "falcon_name": stat("mig4324", ["CHIM CẮT SỐ 2", 150, YEL], ["6 / 9 CHIẾN CÔNG Ở VỊ TRÍ SỐ 2", 56, WHT]),
    "hit_run": X("phrase", photo="fr_clouds", text="BAY THẤP · VỌT LÊN · PHÓNG · THOÁT LY", size=84, sub="KHÔNG QUẦN NHAU LÂU"),
    "training": A(["h", 282, 3.8, T], ["h", 334, 3.8, T]),
    "olds": A(["a", 952, 4, Q], ["a", 994, 4, Q], ["a", 972, 4, Q]),
    # 7 nine victories
    "y1967": stat("fr_formation", ["1967", 170, YEL], ["6 MÁY BAY MỸ BỊ BẮN RƠI", 64, WHT]),
    "aug": A(["a", 946, 3, Q], ["a", 600, 2, Q], ["p", 118, 3, T]),
    "oct": A(["f", 1223, 4, T], ["f", 1212, 3.2, T], ["f", 1079, 3.6, T]),
    "nov20": A(["f", 1160, 3.2, T], ["f", 1098, 3.5, T], ["f", 1145, 3.5, T]),
    "ace": A(["p", 117.5, 4, T], ["a", 436, 3, Q], ["f", 1223, 3, T]),
    "may68": A(["n", 393, 4, T], ["n", 405, 4, T], ["n", 444, 4, T]),
    "may68_hit": A(["f", 1099.5, 2.6, T], ["p", 119, 3.5, T], ["n", 12, 4, T]),
    "drones": A(["a", 930, 4, Q], ["a", 994, 4, Q]),
    "nine": stat("fr_clouds", ["9", 220, YEL], ["5 F-105 · 2 F-4 · 2 MÁY BAY KHÔNG NGƯỜI LÁI", 56, WHT], ["+ YỂM HỘ ĐỒNG ĐỘI BẮN RƠI 9 CHIẾC KHÁC", 40, CY]),
    "top": X("phrase", photo="mig21b52", text="THÀNH TÍCH CAO NHẤT", size=130, sub="TRÊN BẦU TRỜI MIỀN BẮC – CẢ HAI PHÍA"),
    "t4326": P("mig4326"),
    "t4326b": stat("mig4326", ["13 NGÔI SAO", 130, YEL], ["6 PHI CÔNG ANH HÙNG", 70, WHT], ["BẢO VẬT QUỐC GIA", 50, CY]),
    # 8 end
    "uncle": X("quote", photo="vpaf_pilots", lines=["\"Bác mong không quân Việt Nam", "có thêm nhiều Cốc nữa.\""], by="CHỦ TỊCH HỒ CHÍ MINH · 01/01/1969", size=70),
    "hero": stat("mig4324", ["ANH HÙNG LLVT NHÂN DÂN", 100, YEL], ["1969 · 26 TUỔI · 9 HUY HIỆU BÁC HỒ", 56, WHT]),
    "teacher": A(["h", 334, 4, T], ["h", 36, 4, T], ["f", 828, 3, T]),
    "love": X("phrase", photo="fr_sunset", text="1966 – 1974", size=150, sub="TÁM NĂM CHỜ ĐỢI · NỮ DIỄN VIÊN ĐỚI THU HƯƠNG"),
    "career": stat("mig21b52", ["TRUNG TƯỚNG", 130, YEL], ["TƯ LỆNH KHÔNG QUÂN", 70, WHT]),
    "fall": X("phrase", photo="fr_sunset", text="2004", size=170, sub="TỔN THƯƠNG CỘT SỐNG · LIỆT GẦN NHƯ TOÀN THÂN"),
    "joke": X("quote", photo="mig4324", lines=["\"Tớ chỉ bị liệt", "từ cổ trở xuống thôi.\""], by="NGUYỄN VĂN CỐC", size=80),
    "final": A(["n", 20, 4.6, T], ["f", 1628, 5, T], ["n", 12, 4, T]),
    "end": X("end", credits=[
        "Ảnh: Wikimedia Commons · Phim tư liệu: U.S. Air Force \"There Is a Way\", \"Airstrikes North 1966\", \"The Gunfighters\", U.S. Navy, National Archives (public domain)",
        "Giọng đọc, âm thanh: ElevenLabs"]),
}

SFX = {
    "o_date": [("jet_formation", 0, 0.7)], "o_two": [("jet_flyby", 1.0, 0.8)], "o_role": [("cockpit_wind", 0, 0.6)],
    "o_turn": [("jet_crash", 2.5, 0.9)], "title": [("jet_flyby", 0, 0.8)], "sting": [("stamp", 0.3, 1.0)],
    "village": [("crowd_village", 0, 0.3)], "sky_boy": [("jet_flyby", 2, 0.5)], "catbi": [("jet_flyby", 1, 0.5)],
    "f4": [("jet_formation", 0, 0.7)], "rt": [("big_explosion", 4, 0.6), ("aaa_fire", 7, 0.4)],
    "bolo_date": [("jet_formation", 0, 0.7)], "bolo_trap": [("jet_flyby", 3, 0.7)], "bolo_cloud": [("cockpit_wind", 0, 0.8)],
    "bolo_shot": [("cannon_burst", 0.5, 0.7), ("jet_crash", 3.5, 0.8)], "scramble": [("jet_flyby", 2, 0.9)],
    "approach": [("jet_dive", 0.5, 0.9)], "do_fire": [("jet_flyby", 0, 0.6), ("jet_crash", 5.5, 0.9)],
    "coc_ask": [("cockpit_wind", 0, 0.7)], "coc_fire": [("jet_flyby", 0, 0.7), ("big_explosion", 3.5, 0.9)],
    "falcon": [("jet_dive", 0, 0.9), ("jet_crash", 8, 0.7)], "olds": [("jet_formation", 0, 0.6)],
    "aug": [("jet_crash", 3, 0.8)], "oct": [("aaa_fire", 0, 0.7)], "nov20": [("jet_dive", 0.5, 0.8), ("jet_crash", 7, 0.8)],
    "ace": [("big_explosion", 0.5, 0.7)], "may68": [("jet_flyby", 1, 0.8)], "may68_hit": [("jet_crash", 2.5, 0.9)],
    "drones": [("jet_formation", 0, 0.5)], "final": [("jet_flyby", 4, 0.4)],
}
MUSIC = [
    ("music_battle", "o_date", 0.85), ("music_tension", "village", 0.7), ("music_tension", "mig21", 0.75),
    ("music_battle", "bolo_date", 0.85), ("music_tension", "do", 0.75), ("music_battle", "scramble", 0.95),
    ("music_tension", "idea", 0.75), ("music_battle", "y1967", 0.9), ("music_mourn", "uncle", 0.85),
]
MUSIC_DIP = ["o_turn", "coc_fire"]
NO_LOGO = {"title", "sting", "end"}
BLACK_TRANS = {"title", "sting", "village", "mig21", "bolo_date", "do", "idea", "y1967", "uncle", "end"}
BED = "jet_formation"
BED_VOL = 0.04
LOUD = {"jet_flyby", "jet_formation", "jet_dive", "cannon_burst", "aaa_fire", "jet_crash", "cockpit_wind", "big_explosion"}
SFX = {k: [(n, o, v * (0.5 if n in LOUD else 1.0)) for n, o, v in L] for k, L in SFX.items()}
ILLUS = {"o_two", "o_turn", "approach", "do_fire", "coc_ask", "coc_fire", "falcon", "aug", "nov20", "ace", "may68_hit", "bolo_shot", "bolo_cloud"}
