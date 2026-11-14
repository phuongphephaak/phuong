"""Visual + sound assignment for script_hamrong.SCENES (by id).
Archive: f = USAF 'There Is a Way' (F-105, 1967), n = 'The American Navy in Vietnam' (1967),
h = 'Carpet Bombing of Hanoi' (NARA 644905), p = 'Air Strike – South Vietnam' (NARA, 1965).
Flow clips H01.. are used when present in flow/ (see flowmap.json)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *segs: ("arch", {"segs": [list(s) for s in segs]})
M = lambda *segs: ("mix", {"segs": [list(s) for s in segs]})
P = lambda name, **k: ("photo", dict(key=name, **k))
X = lambda kind, **spec: ("gfx", dict(kind=kind, spec=spec))
T = "t"
YEL, WHT, CY = (255, 215, 90), (255, 255, 255), (90, 200, 255)

HANOI, NOIBAI, HR, VINH = [105.85, 21.03], [105.80, 21.22], [105.78, 19.84], [105.68, 18.67]
HONME, SAOVANG, NGHEAN, NINHBINH = [105.93, 19.38], [105.47, 19.74], [105.50, 19.08], [105.97, 20.25]


def _have(k):
    return any(os.path.exists(os.path.join(HERE, "photos", k + e)) for e in (".jpg", ".png", ".jpeg"))


def stat(photo, *lines):
    return X("stat", photo=photo, lines=[list(l) for l in lines])


def mig_route(corner, label):
    return X("map", view0=[105.9, 20.6, 3.6], view1=[105.85, 20.45, 3.0], corner=corner, items=[
        {"t": 0.3, "type": "pin", "at": NOIBAI, "small": "SÂN BAY", "big": "NỘI BÀI", "anchor": "r", "color": "cyan"},
        {"t": 0.9, "type": "pin", "at": HR, "small": "THANH HÓA", "big": "CẦU HÀM RỒNG", "anchor": "l"},
        {"t": 1.6, "type": "arrow", "path": [NOIBAI, [105.55, 20.6], [105.6, 20.1], HR], "dur": 3.0, "color": "cyan", "icon": "plane", "w": 6},
        {"t": 3.4, "type": "tag", "at": [105.5, 20.45], "text": label, "dx": -40, "dy": 0}])


VIS = {
    # ---- 1 hook
    "h_clock": X("clock", time="10:30", sub="SÁNG NGÀY 04/04/1965"),
    "h_strike": A(["f", 0.2, 5.3, T], ["f", 977, 5.5, T]),
    "h_belief": A(["f", 1022, 5.4, T], ["f", 1034, 6, T]),
    "h_dive": A(["p", 36, 4.2, T], ["f", 38, 4.4, T]),
    "h_impact": A(["p", 119.5, 2.4, T], ["f", 1145, 2, T]),
    "h_question": A(["f", 1212, 3.2, T], ["p", 120, 4, T], ["h", 50, 5.5, T]),
    "title": X("title", photo="fr_clouds", l1="TRẬN ĐẦU", l2="BẦU TRỜI HÀM RỒNG 1965"),
    "sting": X("sting"),
    # ---- 2 bridge
    "tonkin": A(["n", 393, 4, T], ["n", 405, 4, T], ["n", 444, 4.6, T]),
    "bridge": X("map", view0=[105.8, 20.4, 5.5], view1=[105.78, 19.9, 1.4], items=[
        {"t": 0.6, "type": "pin", "at": HANOI, "small": "", "big": "HÀ NỘI", "size": 44},
        {"t": 2.2, "type": "pin", "at": HR, "small": "SÔNG MÃ · THANH HÓA", "big": "CẦU HÀM RỒNG", "anchor": "l"},
        {"t": 6.0, "type": "tag", "at": HR, "text": "CẦU THÉP ~160 M · HOÀN THÀNH 1964", "dy": 90}]),
    "artery": X("map", view0=[105.9, 19.9, 6.5], view1=[105.85, 19.85, 5.2], items=[
        {"t": 0.2, "type": "pin", "at": HANOI, "small": "", "big": "HÀ NỘI", "size": 44},
        {"t": 0.5, "type": "pin", "at": HR, "small": "", "big": "HÀM RỒNG", "size": 44},
        {"t": 0.8, "type": "pin", "at": VINH, "small": "", "big": "VINH", "size": 40},
        {"t": 1.2, "type": "arrow", "path": [HANOI, NINHBINH, HR, VINH, [106.3, 17.6]], "dur": 3.2, "color": "yellow", "dashed": True, "w": 6},
        {"t": 4.2, "type": "tag", "at": [106.25, 18.2], "text": "ĐƯỜNG SẮT · QUỐC LỘ 1", "dx": 30},
        {"t": 6.2, "type": "x", "at": HR}]),
    "why_bridge": A(["f", 478, 5, T], ["f", 491, 4.5, T], ["f", 500, 4, T]),
    "jaw": A(["f", 1127, 5, T], ["f", 1136, 5.6, T]),
    "defense": A(["h", 44, 5, T], ["h", 262, 5, T]),
    "tuyen": stat("fr_militia", ["NGÔ THỊ TUYỂN", 110, YEL], ["NỮ DÂN QUÂN 19 TUỔI · NẶNG CHƯA ĐẾN 50 KG", 44, WHT],
                  ["VÁC 98 KG ĐẠN RA TRẬN ĐỊA", 66, WHT]),
    # ---- 3 the swallows
    "vpaf": P("vpaf_pilots"),
    "young": X("phrase", photo="vpaf_pilots", text="VÀI CHỤC CHIẾC MÁY BAY", sub="CHƯA AI TỪNG KHÔNG CHIẾN THẬT"),
    "training": A(["h", 282, 3.8, T], ["h", 334, 3.8, T], ["h", 36, 4, T]),
    "mig17": M(["p", "mig_card", 0, None], ["p", "f105_card", 0, None]),
    "thud": A(["f", 0.2, 4, T], ["f", 917, 3.5, T], ["f", 968, 4, T], ["f", 828, 3, T]),
    "edge": X("phrase", photo="mig_gear", text="ĐÁNH GẦN · ĐÁNH NHANH · ĐÁNH BẤT NGỜ", size=76, sub="MiG-17 LƯỢN VÒNG RẤT GẮT Ở TẦM THẤP"),
    "plan": mig_route("", "BAY THẤP · DẪN ĐƯỜNG TỪ MẶT ĐẤT"),
    # ---- 4 3 April
    "d3": stat("fr_clouds", ["03/04/1965", 150, YEL], ["ĐỢT TẤN CÔNG ĐẦU TIÊN VÀO CẦU HÀM RỒNG", 50, WHT]),
    "risner": A(["f", 983, 5.5, T], ["f", 992, 8.5, T]),
    "risner_note": X("portrait", photo="risner", name="Robinson Risner", sub="TRUNG TÁ KHÔNG QUÂN MỸ · CHỈ HUY ĐỢT TẤN CÔNG",
                     bg="photo", bgphoto="fr_refuel"),
    "bullpup": A(["f", 1142, 3, T], ["f", 1124, 2.6, T], ["f", 1145, 5.5, T]),
    "aaa": A(["f", 1223, 4, T], ["p", 119.5, 4.5, T]),
    "lan_up": M(["p", "mig4_kb", 0, None], ["a", "f", 1160, 3.2, T], ["p", "mig_fly_kb", 0, 3]),
    "lan_attack": A(["f", 1103, 2.2, T], ["f", 1106, 1.6, T], ["f", 1098, 4.2, T], ["f", 1160, 3.2, T], ["f", 1119.5, 2.4, T]),
    "lan_hit": A(["f", 1099.5, 2.6, T], ["p", 117.5, 5, T], ["f", 1223, 3.6, T]),
    "lan_fuel": A(["h", 270, 5, T], ["h", 286, 4, T], ["h", 290, 3.5, T]),
    "first": X("portrait", photo="lan_card", name="Phạm Ngọc Lan", sub="BIÊN ĐỘI TRƯỞNG · TRẬN ĐẦU 03/04/1965", bg="photo", bgphoto="vpaf_pilots"),
    "d3_end": A(["f", 1151, 4, T], ["f", 1157, 3.5, T]),
    "claims": A(["h", 342, 4.5, T], ["h", 350, 5, T]),
    # ---- 5 4 April
    "d4": stat("fr_formation", ["04/04/1965", 150, YEL], ["48 F-105 · HƠN 20 F-100", 64, WHT]),
    "hanh_up": mig_route("04/04/1965", "BIÊN ĐỘI TRẦN HANH"),
    "hanh": X("portrait", photo="hanh", name="Trần Hanh", sub="BIÊN ĐỘI TRƯỞNG · TRUNG ĐOÀN 921", bg="photo", bgphoto="fr_skywatch"),
    "spot": A(["f", 1058, 3, T], ["f", 1022, 5.6, T]),
    "cover": X("map", view0=[105.62, 20.08, 1.7], view1=[105.62, 20.05, 1.45], bg="tactical", items=[
        {"t": 0.2, "type": "pin", "at": HR, "small": "", "big": "HÀM RỒNG", "size": 40, "anchor": "m"},
        {"t": 0.5, "type": "arrow", "path": [[104.95, 19.93], [105.66, 19.87]], "dur": 2.4, "color": "red", "icon": "plane", "w": 6},
        {"t": 1.0, "type": "tag", "at": [105.1, 19.92], "text": "4 F-105", "dy": 60},
        {"t": 1.6, "type": "arrow", "path": [[105.7, 20.38], [106.12, 20.4]], "dur": 2.0, "color": "red", "dashed": True, "w": 4, "icon": "plane"},
        {"t": 2.4, "type": "tag", "at": [105.85, 20.39], "text": "F-100 HỘ TỐNG · SAI VỊ TRÍ", "dy": 60},
        {"t": 3.6, "type": "arrow", "path": [[105.0, 20.32], [105.3, 20.12], [105.5, 19.95]], "dur": 1.6, "color": "cyan", "icon": "plane", "w": 7},
        {"t": 4.6, "type": "tag", "at": [105.05, 20.3], "text": "MiG-17 TỪ TRÊN MÂY", "dy": -60}]),
    "attack": A(["p", 40, 4.5, T], ["f", 38, 4.4, T]),
    "fire": A(["f", 1094, 4.2, T], ["p", 119.5, 4.5, T], ["f", 1145, 3.5, T]),
    "two_down": X("map", view0=[105.95, 19.55, 1.6], view1=[105.95, 19.45, 1.25], items=[
        {"t": 0.2, "type": "pin", "at": HR, "small": "", "big": "HÀM RỒNG", "size": 40},
        {"t": 0.8, "type": "pin", "at": HONME, "small": "", "big": "ĐẢO HÒN MÊ", "size": 40, "color": "cyan", "anchor": "r"},
        {"t": 2.0, "type": "x", "at": [106.04, 19.43]}, {"t": 2.8, "type": "x", "at": [106.0, 19.32]},
        {"t": 4.0, "type": "tag", "at": [106.02, 19.37], "text": "2 F-105 RƠI XUỐNG BIỂN", "dy": 80}]),
    "shock": X("phrase", photo="fr_clouds", text="2 NGÀY · 2 TRẬN · 2 CHIẾN THẮNG", sub="03/04 – 04/04/1965"),
    "report": A(["n", 778, 4.5, T], ["f", 576, 4.5, T], ["f", 588, 4, T]),
    # ---- 6 the price
    "chase": A(["f", 1079, 3.6, T], ["f", 1212, 3, T], ["f", 1223, 2.5, T], ["f", 1142, 2.5, T]),
    "lost": X("phrase", photo="fr_sunset", text="PHẠM GIẤY · LÊ MINH HUÂN · TRẦN NGUYÊN NĂM", size=64,
              sub="ANH DŨNG HY SINH NGÀY 04/04/1965"),
    "hanh_back": X("map", view0=[105.65, 19.55, 2.4], view1=[105.6, 19.45, 2.0], items=[
        {"t": 0.2, "type": "pin", "at": HR, "small": "", "big": "HÀM RỒNG", "size": 40},
        {"t": 0.8, "type": "arrow", "path": [HR, [105.55, 19.55], NGHEAN], "dur": 3.0, "color": "cyan", "icon": "plane", "w": 6},
        {"t": 3.8, "type": "tag", "at": NGHEAN, "text": "HẠ CÁNH BẮT BUỘC · NGHỆ AN", "dy": 80}]),
    "price": A(["h", 50, 5.5, T], ["n", 8, 5, T]),
    "sao_vang": X("map", view0=[105.65, 20.4, 3.6], view1=[105.6, 20.1, 2.6], items=[
        {"t": 0.3, "type": "pin", "at": NOIBAI, "small": "", "big": "NỘI BÀI", "size": 40, "color": "cyan", "anchor": "r"},
        {"t": 0.8, "type": "pin", "at": HR, "small": "", "big": "HÀM RỒNG", "size": 40},
        {"t": 2.0, "type": "pin", "at": SAOVANG, "small": "SÂN BAY MỚI", "big": "SAO VÀNG", "color": "yellow", "anchor": "r"},
        {"t": 3.2, "type": "arrow", "path": [SAOVANG, HR], "dur": 1.2, "color": "yellow", "dashed": True, "w": 5},
        {"t": 4.6, "type": "tag", "at": [105.62, 19.8], "text": "SÁT CHIẾN TRƯỜNG HƠN", "dy": 70}]),
    "lesson": X("phrase", photo="fr_sight", text="ĐÁNH BẤT NGỜ · ĐÁNH NHANH · RÚT NHANH", size=76, sub="SỞ TRƯỜNG CỦA PHI CÔNG MiG"),
    # ---- 7 end
    "us_change": A(["n", 486, 3.5, T], ["n", 806, 3.5, T], ["f", 1628, 5, T]),
    "seven": A(["f", 1127, 4, T], ["f", 1151, 4.5, T], ["f", 1136, 4.5, T]),
    "cost_area": A(["f", 1223, 4.5, T], ["h", 344, 5.5, T]),
    "hanh_later": X("portrait", photo="hanh", name="Trần Hanh", sub="TƯ LỆNH KHÔNG QUÂN · THỨ TRƯỞNG BỘ QUỐC PHÒNG",
                    bg="photo", bgphoto="fr_sunset"),
    "lan_later": X("portrait", photo="lan_card", name="Phạm Ngọc Lan", sub="THIẾU TƯỚNG · NGƯỜI THẦY CỦA NHIỀU LỚP PHI CÔNG", bg="photo", bgphoto="fr_sunset"),
    "three": A(["n", 8, 6, T], ["h", 58, 4.5, T]),
    "final": A(["n", 20, 4.6, T], ["f", 1628, 5, T], ["n", 12, 4, T]),
    "end": X("end", credits=[
        "Ảnh: Wikimedia Commons · Phim tư liệu: U.S. Air Force \"There Is a Way\", U.S. Navy \"The American Navy in Vietnam\", National Archives (public domain)",
        "Bản đồ: NASA Blue Marble, sơ đồ minh họa · Giọng đọc, âm thanh: ElevenLabs"]),
}

# AI clips (Google Flow) override scenes when present
FLOWMAP = json.load(open(os.path.join(HERE, "flowmap.json")))
for code, sid in FLOWMAP.items():
    if os.path.exists(os.path.join(HERE, "flow", code + ".mp4")) and sid in VIS:
        VIS[sid] = ("flow", {"segs": [[code, 0, None]]})

SFX = {
    "h_clock": [("jet_formation", 0, 0.6)], "h_strike": [("jet_formation", 0, 0.8)], "h_belief": [("cockpit_wind", 0, 0.6)],
    "h_dive": [("jet_dive", 0.5, 1.0), ("cannon_burst", 5.0, 0.9)], "h_impact": [("jet_crash", 0, 1.0)],
    "h_question": [("aaa_fire", 2.5, 0.4)], "title": [("jet_flyby", 0, 0.8)], "sting": [("stamp", 0.3, 1.0)],
    "tonkin": [("ocean_calm", 0, 0.5)], "why_bridge": [("crowd_village", 0, 0.2)], "jaw": [("jet_formation", 0, 0.5)],
    "defense": [("aaa_fire", 1, 0.6)], "tuyen": [("aaa_fire", 0, 0.4)], "thud": [("jet_flyby", 4, 0.9), ("jet_flyby", 9, 0.8)],
    "plan": [("morse", 0, 0.35)], "lan_up": [("jet_flyby", 1.5, 0.7)], "hanh_up": [("jet_flyby", 1.5, 0.7)],
    "risner": [("jet_formation", 0, 0.7)], "bullpup": [("big_explosion", 2.5, 0.8), ("aaa_fire", 5, 0.5)],
    "aaa": [("aaa_fire", 0, 1.0), ("jet_crash", 4.5, 0.7)], "lan_attack": [("jet_flyby", 0.5, 0.8), ("cannon_burst", 7, 0.9)],
    "lan_hit": [("jet_crash", 0.3, 0.6)], "lan_fuel": [("crowd_village", 0, 0.6)], "d3_end": [("fire_crackle", 0, 0.4)],
    "claims": [("crowd_village", 0, 0.4)], "d4": [("jet_formation", 0, 0.7)], "spot": [("cockpit_wind", 0, 0.8)],
    "attack": [("jet_dive", 0, 1.0)], "fire": [("cannon_burst", 0.6, 1.0), ("cannon_burst", 4.0, 0.9), ("jet_crash", 5.5, 0.9)],
    "two_down": [("jet_crash", 1.5, 0.6)], "chase": [("jet_flyby", 0.5, 0.9), ("aaa_fire", 3, 0.7)],
    "hanh_back": [("cockpit_wind", 0, 0.6)], "us_change": [("jet_flyby", 1, 0.7)], "seven": [("big_explosion", 1.0, 0.5)],
    "cost_area": [("aaa_fire", 0, 0.6)], "three": [("river_dusk", 0, 0.7)], "final": [("river_dusk", 0, 0.8)],
}
MUSIC = [
    ("music_battle", "h_clock", 0.85), ("music_tension", "tonkin", 0.75), ("music_tension", "vpaf", 0.75),
    ("music_battle", "d3", 0.9), ("music_tension", "d3_end", 0.75), ("music_battle", "d4", 0.95),
    ("music_mourn", "lost", 0.9), ("music_tension", "us_change", 0.7), ("music_mourn", "hanh_later", 0.85),
]
MUSIC_DIP = ["h_impact", "lost"]
NO_LOGO = {"title", "sting", "end"}
BLACK_TRANS = {"title", "sting", "tonkin", "vpaf", "d3", "d4", "lost", "us_change", "end"}
BED = "jet_formation"
BED_VOL = 0.05
# quieter engines and guns (user feedback v1)
LOUD = {"jet_flyby", "jet_formation", "jet_dive", "cannon_burst", "aaa_fire", "jet_crash", "cockpit_wind", "big_explosion"}
SFX = {k: [(n, o, v * (0.5 if n in LOUD else 1.0)) for n, o, v in L] for k, L in SFX.items()}
ILLUS = {"lan_up", "lan_attack", "lan_hit", "h_dive", "attack", "fire", "chase"}
