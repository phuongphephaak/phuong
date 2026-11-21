"""Visual + sound plan for script_pp.SCENES (by id).
Archive: s = 'Prince Sihanouk's Cambodian Visit' (1973, NARA/CIA), r = 'Vietnamese Refugees in Cambodia' (US Army, 1970),
m = '9th Infantry Division in Cambodia' (US Army, 1970), e = 'Aerial Views, South Vietnam and Cambodia' (1970),
b = 'Royal Ballet of Cambodia' (USIA, 1965), a = USAF 'Airstrikes North 1966', g = 'The Gunfighters' (USAF)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *segs: ("arch", {"segs": [list(s) for s in segs]})
P = lambda name, **k: ("photo", dict(key=name, **k))
X = lambda kind, **spec: ("gfx", dict(kind=kind, spec=spec))
T, Q, Wd = "t", "pa", "w"
YEL, WHT, CY, RD = (255, 215, 90), (255, 255, 255), (90, 200, 255), (255, 80, 70)

PP, HN, BJ = [104.92, 11.56], [105.85, 21.03], [116.40, 39.90]
THOCHU, PHUQUOC = [103.47, 9.30], [103.96, 10.23]
BACHUC, TAYNINH, HATIEN = [104.95, 10.49], [106.10, 11.31], [104.48, 10.38]
KRATIE, STUNGTRENG, KAMPOT, TAKEO = [106.02, 12.49], [105.97, 13.53], [104.18, 10.61], [104.79, 10.99]


def stat(photo, *lines):
    return X("stat", photo=photo, lines=[list(l) for l in lines])


VIS = {
    # 1 hook
    "o_date": A(["r", 271, 4, T], ["r", 1141, 4, T], ["r", 1151, 4, T]),
    "o_order": A(["r", 541, 4, T], ["r", 900, 4, T], ["m", 444, 3, Wd]),
    "o_never": A(["e", 252, 4, Wd], ["e", 266, 4, Wd], ["m", 444, 4, Wd]),
    "o_man": P("ceausescu"),
    "o_toll": stat("stupa", ["1.700.000", 170, RD], ["NGƯỜI CHẾT · GẦN 1/4 DÂN SỐ CAMPUCHIA", 56, WHT], ["1975 – 1979", 44, YEL]),
    "o_name": X("portrait", photo="polpot_c", name="Saloth Sar", sub="POL POT · 1925 – 1998", bg="photo", bgphoto="ceausescu"),
    "title": X("title", photo="stupa", l1="POL POT", l2="TỪ SINH VIÊN PARIS ĐẾN KẺ DIỆT CHỦNG"),
    "sting": X("sting"),
    # 2 childhood
    "village": P("preksbauv"),
    "palace": A(["b", 18, 4, T], ["b", 200, 4, T], ["b", 225, 4, T]),
    "monk": A(["b", 916, 4, T], ["b", 270, 4, T], ["b", 931, 4, T]),
    "fail": P("pp1964"),
    # 3 Paris
    "paris": X("phrase", photo="pp_air", text="PARIS · 1949", size=170, sub="HỌC BỔNG NGÀNH ĐIỆN TỬ VÔ TUYẾN"),
    "paris_red": X("portrait", photo="iengsary", name="Ieng Sary", sub="BẠN HỌC · \"CÁNH TAY PHẢI\" CỦA POL POT", bg="photo", bgphoto="pp_air"),
    "paris_fail": stat("pp_air", ["3 LẦN THI TRƯỢT", 140, RD], ["MẤT HỌC BỔNG · VỀ NƯỚC KHÔNG BẰNG CẤP", 50, WHT]),
    "paris_back": A(["e", 456, 4, Wd], ["e", 466, 4, Wd]),
    # 4 teacher
    "teacher": P("pp1964"),
    "marry": X("phrase", photo="pp1964", text="14/07/1956", size=160, sub="CƯỚI KHIEU PONNARY · ĐÚNG NGÀY QUỐC KHÁNH PHÁP"),
    "double": X("phrase", photo="pp_air", text="NGÀY: THẦY GIÁO", size=120, sub="ĐÊM: LÃNH ĐẠO MỘT ĐẢNG BÍ MẬT"),
    "jungle": X("phrase", photo="preksbauv", text="1963", size=210, sub="BÍ THƯ · BIẾN MẤT VÀO RỪNG SÂU"),
    "travel": X("map", view0=[110.5, 25.5, 34], view1=[110.5, 25.5, 30], items=[
        {"t": 0.4, "type": "pin", "at": PP, "small": "", "big": "PHNÔM PÊNH", "size": 40, "anchor": "r"},
        {"t": 1.4, "type": "arrow", "path": [PP, [106.6, 15.5], HN], "dur": 2.0, "color": "yellow", "dashed": True, "w": 6},
        {"t": 3.0, "type": "pin", "at": HN, "small": "1965", "big": "HÀ NỘI", "size": 40, "anchor": "r"},
        {"t": 4.0, "type": "arrow", "path": [HN, [110.5, 30.0], BJ], "dur": 2.4, "color": "red", "dashed": True, "w": 6},
        {"t": 6.2, "type": "pin", "at": BJ, "small": "1965 – 1966", "big": "BẮC KINH", "size": 44, "color": "red"}]),
    "secret": A(["s", 31, 4, T], ["s", 51, 4, T], ["s", 131, 4, T]),
    "coup": A(["m", 36, 4, Wd], ["m", 180, 4, Wd], ["m", 204, 4, Wd]),
    "pol": A(["s", 172, 4, T], ["s", 1262, 4, T], ["s", 51, 4, T]),
    "war": A(["g", 280, 3.5, Q], ["g", 290, 4, Q], ["a", 62, 3.5, Q], ["a", 266, 3.5, Q]),
    # 5 year zero
    "zero": X("phrase", photo="pp_air", text="NĂM SỐ 0", size=200, sub="17/04/1975"),
    "march": A(["r", 1140, 4, T], ["e", 262, 4, Wd], ["e", 272, 4, Wd]),
    "abolish": stat("pp1964", ["TIỀN · CHỢ · TRƯỜNG HỌC", 96, RD], ["CHÙA CHIỀN · BỆNH VIỆN", 96, RD], ["TẤT CẢ BỊ XÓA BỎ", 50, WHT]),
    "angkar": X("phrase", photo="ce_graves", text="ANGKAR", size=210, sub="\"TỔ CHỨC\" · CÓ MẮT NHƯ QUẢ DỨA, NHÌN THẤY TẤT CẢ"),
    "newpeople": stat("pp1964", ["\"NGƯỜI CŨ\"", 110, WHT], ["\"NGƯỜI MỚI\"", 110, RD], ["DÂN THÀNH PHỐ: ĂN ÍT NHẤT · LÀM NẶNG NHẤT", 46, WHT]),
    "black": A(["e", 384, 4, Wd], ["e", 396, 4, Wd], ["e", 420, 4, Wd]),
    "quota": stat("preksbauv", ["3 TẤN", 180, YEL], ["THÓC TRÊN MỖI HÉC-TA · CHỈ TIÊU CỦA POL POT", 50, WHT]),
    "kids": A(["s", 211, 4, T], ["m", 411.5, 2.5, Wd], ["s", 231, 4, T]),
    "slogan": X("quote", photo="ce_graves", lines=["\"Giữ ngươi lại chẳng được lợi gì,", "mất ngươi đi chẳng thiệt hại gì.\""], by="KHẨU HIỆU KHMER ĐỎ", size=64),
    # 6 S-21
    "school": P("ts_bldg"),
    "duch": P("duch"),
    "photos": P("ts_s21a"),
    "survivors": P("ts_cells"),
    "purge": P("ts_1"),
    "vn_s21": P("ts_s21d"),
    "fields": P("stupa"),
    # 7 Vietnam
    "vn_hate": A(["r", 261, 4, T], ["r", 120, 4, T], ["r", 545, 4, T]),
    "thochu": X("map", view0=[104.2, 10.2, 4.0], view1=[103.8, 9.7, 2.6], items=[
        {"t": 0.4, "type": "pin", "at": PHUQUOC, "small": "", "big": "PHÚ QUỐC", "size": 40, "color": "cyan"},
        {"t": 1.2, "type": "pin", "at": THOCHU, "small": "10/05/1975", "big": "ĐẢO THỔ CHU", "size": 48, "color": "red"},
        {"t": 2.6, "type": "arrow", "path": [[103.3, 10.4], [103.4, 9.8], THOCHU], "dur": 1.8, "color": "red", "w": 6},
        {"t": 4.6, "type": "tag", "at": THOCHU, "text": "HƠN 500 NGƯỜI DÂN BỊ BẮT ĐI", "dy": 100}]),
    "raids": X("map", view0=[105.4, 11.0, 4.6], view1=[105.4, 10.9, 4.0], items=[
        {"t": 0.3, "type": "pin", "at": PP, "small": "", "big": "PHNÔM PÊNH", "size": 38, "anchor": "r", "color": "red"},
        {"t": 0.9, "type": "pin", "at": TAYNINH, "small": "", "big": "TÂY NINH", "size": 40, "color": "cyan"},
        {"t": 1.4, "type": "pin", "at": BACHUC, "small": "", "big": "AN GIANG", "size": 40, "color": "cyan"},
        {"t": 1.9, "type": "pin", "at": HATIEN, "small": "", "big": "KIÊN GIANG", "size": 40, "anchor": "r", "color": "cyan"},
        {"t": 2.6, "type": "arrow", "path": [[105.6, 11.9], TAYNINH], "dur": 1.4, "color": "red", "w": 6},
        {"t": 3.2, "type": "arrow", "path": [[104.7, 11.0], BACHUC], "dur": 1.4, "color": "red", "w": 6},
        {"t": 3.8, "type": "arrow", "path": [[104.2, 10.9], HATIEN], "dur": 1.4, "color": "red", "w": 6}]),
    "talks": X("phrase", photo="memorial", text="05/02/1978", size=160, sub="VIỆT NAM ĐỀ NGHỊ NGỪNG BẮN, ĐÀM PHÁN · POL POT TỪ CHỐI"),
    "bachuc": X("map", view0=[105.3, 10.8, 4.0], view1=[104.97, 10.5, 1.3], items=[
        {"t": 1.0, "type": "pin", "at": BACHUC, "small": "TRI TÔN · AN GIANG", "big": "BA CHÚC", "size": 54, "color": "red"},
        {"t": 2.4, "type": "arrow", "path": [[104.8, 10.75], BACHUC], "dur": 1.6, "color": "red", "w": 7}]),
    "bachuc_pagoda": X("phrase", photo="ce_graves", text="CHÙA TAM BỬU · CHÙA PHI LAI", size=96, sub="NƠI NGƯỜI DÂN TÌM ĐẾN ẨN NÁU"),
    "bachuc_toll": stat("ce_graves", ["3.157", 210, RD], ["DÂN THƯỜNG BỊ SÁT HẠI TRONG 12 NGÀY", 56, WHT], ["18/04 – 30/04/1978", 44, YEL]),
    "bachuc_now": X("phrase", photo="ce_graves", text="1.159 CHIẾC SỌ", size=150, sub="NHÀ MỒ BA CHÚC · AN GIANG"),
    "counter": X("map", view0=[105.2, 12.2, 6.2], view1=[105.0, 11.9, 5.0], items=[
        {"t": 0.3, "type": "pin", "at": PP, "small": "", "big": "PHNÔM PÊNH", "size": 44, "color": "red"},
        {"t": 1.0, "type": "arrow", "path": [[106.6, 12.3], KRATIE, STUNGTRENG], "dur": 2.0, "color": "cyan", "w": 7},
        {"t": 1.6, "type": "arrow", "path": [TAYNINH, [105.5, 11.5], PP], "dur": 2.4, "color": "cyan", "w": 7},
        {"t": 2.2, "type": "arrow", "path": [[105.1, 10.6], TAKEO, PP], "dur": 2.4, "color": "cyan", "w": 7},
        {"t": 2.8, "type": "arrow", "path": [HATIEN, KAMPOT], "dur": 1.6, "color": "cyan", "w": 7}]),
    "liberate": P("memorial"),
    "tay": P("ts_rules"),
    # 8 end
    "china": X("map", view0=[105.6, 22.0, 6.0], view1=[105.6, 22.0, 5.2], items=[
        {"t": 0.3, "type": "pin", "at": HN, "small": "", "big": "HÀ NỘI", "size": 40, "color": "cyan"},
        {"t": 1.0, "type": "arrow", "path": [[103.5, 23.3], [103.5, 22.4]], "dur": 1.2, "color": "red", "w": 7},
        {"t": 1.4, "type": "arrow", "path": [[104.1, 23.2], [103.97, 22.48]], "dur": 1.2, "color": "red", "w": 7},
        {"t": 1.8, "type": "arrow", "path": [[106.2, 23.3], [106.25, 22.67]], "dur": 1.2, "color": "red", "w": 7},
        {"t": 2.2, "type": "arrow", "path": [[107.0, 22.6], [106.76, 21.85]], "dur": 1.2, "color": "red", "w": 7},
        {"t": 2.6, "type": "arrow", "path": [[108.0, 21.9], [107.9, 21.5]], "dur": 1.2, "color": "red", "w": 7},
        {"t": 3.6, "type": "tag", "at": [105.6, 22.0], "text": "6 TỈNH BIÊN GIỚI PHÍA BẮC", "dy": 120}]),
    "un": X("phrase", photo="ceausescu", text="GHẾ LIÊN HỢP QUỐC", size=130, sub="KHMER ĐỎ VẪN ĐẠI DIỆN CAMPUCHIA SUỐT NHIỀU NĂM"),
    "anlong": P("tamok"),
    "trial": X("phrase", photo="pp_air", text="TÙ CHUNG THÂN", size=160, sub="PHIÊN TÒA DO CHÍNH KHMER ĐỎ DỰNG LÊN · 07/1997"),
    "thayer": X("quote", photo="polpot", lines=["\"Hãy nhìn tôi xem,", "tôi có phải kẻ man rợ không?", "Lương tâm tôi trong sạch.\""], by="POL POT · PHỎNG VẤN NATE THAYER, 10/1997", size=68),
    "deny": X("phrase", photo="ts_cells", text="\"S-21 DO VIỆT NAM DỰNG LÊN\"", size=96, sub="POL POT CHỐI BỎ TỘI ÁC ĐẾN CUỐI ĐỜI"),
    "death": P("cremation"),
    "nojustice": P("grave"),
    "final": A(["b", 916, 4, T], ["b", 931, 5, T], ["e", 624, 4, Wd]),
    "end": X("end", credits=[
        "Ảnh: Wikimedia Commons · Phim tư liệu: U.S. Army, USIA, U.S. Air Force, National Archives (public domain)",
        "Giọng đọc, âm thanh: ElevenLabs"]),
}

SFX = {
    "o_date": [("crowd_village", 0, 0.4)], "o_order": [("alarm", 0.5, 0.25)], "o_never": [("wind", 0, 0.6)],
    "title": [("boom_far", 0, 0.8)], "sting": [("stamp", 0.3, 1.0)], "village": [("river_dusk", 0, 0.5)],
    "jungle": [("wind", 0, 0.5)], "coup": [("helicopter", 0, 0.4)], "war": [("big_explosion", 1, 0.6), ("boom_far", 6, 0.6)],
    "zero": [("stamp", 0.4, 0.9)], "march": [("wind", 0, 0.6)], "school": [("creak", 1, 0.5)], "duch": [("typewriter", 0, 0.4)],
    "purge": [("stamp", 1, 0.7)], "raids": [("boom_far", 2.5, 0.6)], "bachuc": [("fire_crackle", 0, 0.4)],
    "counter": [("boom_far", 1, 0.6), ("boom_far", 4, 0.5)], "china": [("boom_far", 1, 0.6)],
    "death": [("fire_crackle", 0, 0.5)], "final": [("wind", 0, 0.5)],
}
MUSIC = [
    ("music_tension", "o_date", 0.75), ("music_mourn", "village", 0.6), ("music_tension", "jungle", 0.7),
    ("music_battle", "war", 0.8), ("music_tension", "zero", 0.75), ("music_mourn", "school", 0.75),
    ("music_battle", "vn_hate", 0.75), ("music_mourn", "bachuc", 0.8), ("music_battle", "counter", 0.9),
    ("music_tension", "un", 0.7), ("music_mourn", "death", 0.85),
]
MUSIC_DIP = ["o_toll", "bachuc_toll"]
NO_LOGO = {"title", "sting", "end"}
BLACK_TRANS = {"title", "sting", "village", "paris", "teacher", "zero", "school", "vn_hate", "bachuc", "un", "end"}
BED = "wind"
BED_VOL = 0.03
LOUD = {"big_explosion", "boom_far", "helicopter", "alarm"}
SFX = {k: [(n, o, v * (0.5 if n in LOUD else 1.0)) for n, o, v in L] for k, L in SFX.items()}
ILLUS = {"o_date", "o_order", "o_never", "march", "angkar", "newpeople", "black", "kids", "vn_hate", "war", "coup", "trial"}
