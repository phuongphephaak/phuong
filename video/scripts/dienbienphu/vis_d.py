"""Visual + sound assignment for script_dbp.SCENES (by id).
Flow clips (D01..D16) are used when present in flow/, otherwise the archive fallback is used."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

A = lambda *segs: ("arch", {"segs": [list(s) for s in segs]})
M = lambda *segs: ("mix", {"segs": [list(s) for s in segs]})
P = lambda name, **k: ("photo", dict(key=name, **k))
X = lambda kind, **spec: ("gfx", dict(kind=kind, spec=spec))
T = "t"   # 4:3 -> 16:9 crop


def FL(code, fallback, st=0, en=None):
    if os.path.exists(os.path.join(HERE, "flow", code + ".mp4")):
        return ("flow", {"segs": [[code, st, en]]})
    return fallback


HANOI, DBP, LUANG = [105.85, 21.03], [103.02, 21.39], [102.13, 19.89]
YEL, WHT, CY = (255, 215, 90), (255, 255, 255), (90, 200, 255)
ALL = [["himlam", "HIM LAM", "BÉATRICE", "l"], ["doclap", "ĐỘC LẬP", "GABRIELLE", "l"], ["bankeo", "BẢN KÉO", "ANNE-MARIE", "r"],
       ["huguette", "HUGUETTE", "", "r"], ["claudine", "CLAUDINE", "", "r"], ["dominique", "DOMINIQUE", "", "l"],
       ["eliane", "ÉLIANE", "", "l"], ["isabelle", "HỒNG CÚM", "ISABELLE", "l"]]
GUNS = [[6.0, 3.5], [6.6, 0.8], [6.2, -2.2], [5.6, 5.5], [-5.8, 3.0], [-6.2, -0.5], [-5.4, 5.8]]


def pts(names, t0=0.4, dt=0.35, color="red"):
    return [{"t": t0 + i * dt, "type": "pt", "at": n, "label": l, "sub": s, "anchor": a, "color": color}
            for i, (n, l, s, a) in enumerate(names)]


VIS = {
    # ---- 1 hook
    "h_clock": FL("D01", A(["wv", 289, 5.6, T])),
    "h_valley": A(["wv", 289.5, 4.8, T], ["in88", 26, 4.4, T]),
    "h_belief": A(["wv", 380, 4, T], ["in2", 523, 3.6, T], ["wv", 296, 3.4, T]),
    "h_fire": FL("D02", A(["in2", 453, 7.6, T])),
    "h_impact": A(["in2", 458, 2.2, T], ["in2", 601, 2, T]),
    "h_question": P("how105a"),
    "title": X("title", photo="artillery", l1="KÉO PHÁO LÊN NÚI", l2="ĐIỆN BIÊN PHỦ 1954"),
    "sting": X("sting"),
    # ---- 2 Navarre
    "war8": A(["in2", 361, 5.6, T], ["in2", 383, 5.6, T]),
    "navarre": X("portrait", photo="navarre", name="Henri Navarre", sub="TỔNG CHỈ HUY QUÂN PHÁP Ở ĐÔNG DƯƠNG"),
    "castor": A(["wv", 280, 3, T], ["wv", 284, 5, T], ["wv", 294, 4.6, T]),
    "map_dbp": X("map", view0=[105.5, 18.5, 20], view1=[103.6, 20.8, 9], tilt=0.12, items=[
        {"t": 0.4, "type": "pin", "at": HANOI, "small": "", "big": "HÀ NỘI"},
        {"t": 1.4, "type": "pin", "at": DBP, "small": "LÒNG CHẢO MƯỜNG THANH", "big": "ĐIỆN BIÊN PHỦ", "anchor": "r"},
        {"t": 2.6, "type": "pin", "at": LUANG, "small": "THƯỢNG LÀO", "big": "LUANG PRABANG", "anchor": "m", "color": "cyan"},
        {"t": 3.6, "type": "arrow", "path": [HANOI, DBP], "dur": 1.6, "color": "yellow", "dashed": True, "w": 5},
        {"t": 5.0, "type": "tag", "at": [104.4, 21.5], "text": "~300 KM ĐƯỜNG BAY", "dy": -60}]),
    "fortress": X("valley", view0=[0.6, 0.2, 30], view1=[0.6, 0.2, 27], items=pts(ALL, 0.6, 0.45) + [
        {"t": 0.3, "type": "pt", "at": "hq", "label": "MƯỜNG THANH", "sub": "SỞ CHỈ HUY", "anchor": "r", "color": "orange"},
        {"t": 5.0, "type": "title", "text": "49 CỨ ĐIỂM · 3 PHÂN KHU · 2 SÂN BAY"}]),
    "decastries": X("portrait", photo="decastries", name="Christian de Castries", sub="CHỈ HUY TẬP ĐOÀN CỨ ĐIỂM"),
    "piroth": X("portrait", photo="piroth", name="Charles Piroth", sub="CHỈ HUY PHÁO BINH PHÁP"),
    "logic": A(["wv", 380, 5, T], ["wv", 289, 4.8, T], ["in2", 523, 4.8, T]),
    "airlift": A(["wv", 276, 2.6, T], ["in88", 372, 4, T], ["wv", 290, 4, T], ["wv", 284, 4.1, T]),
    "h_trap": A(["wv", 294, 3.6, T], ["wv", 300, 3.9, T]),
    # ---- 3 pulling in
    "giap": X("portrait", photo="giap_mr", name="Võ Nguyên Giáp", sub="TỔNG CHỈ HUY CHIẾN DỊCH ĐIỆN BIÊN PHỦ"),
    "march": FL("D05", A(["wv", 330, 4, T], ["wv", 528, 6.4, T])),
    "fast": X("phrase", photo="artillery", text="ĐÁNH NHANH, GIẢI QUYẾT NHANH", sub="TẤN CÔNG TRONG KHOẢNG BA ĐÊM HAI NGÀY"),
    "guns": P("how105b"),
    "estimate": A(["wv", 276, 2.6, T], ["in2", 468, 3.4, T], ["wv", 380, 4, T], ["wv", 289.5, 3.4, T]),
    "pull": FL("D03", P("artillery")),
    "slow": FL("D04", A(["wv", 528, 5.2, T], ["wv", 538, 5.2, T])),
    "todien": X("portrait", photo="todien", name="Tô Vĩnh Diện", sub="ANH HÙNG LỰC LƯỢNG VŨ TRANG NHÂN DÂN"),
    "ready": FL("D08", P("how105a", dark=0.2)),
    # ---- 4 decision
    "doubt": FL("D06", P("map1315", dark=0.3)),
    "risk": A(["in2", 553, 3.2, T], ["in2", 543, 4, T], ["in2", 523, 3.7, T]),
    "decision": X("stat", photo="giap1951", lines=[["26/01/1954", 150, YEL], ["HOÃN TẤN CÔNG · KÉO PHÁO RA", 54, WHT]]),
    "quote": X("quote", photo="giap_mr", lines=["“Đây là quyết định khó khăn nhất", "trong cuộc đời chỉ huy của tôi.”"],
               by="— Đại tướng Võ Nguyên Giáp"),
    "steady": X("phrase", photo="artillery", text="ĐÁNH CHẮC, TIẾN CHẮC", sub="THAY CHO: ĐÁNH NHANH, GIẢI QUYẾT NHANH"),
    "morale": FL("D03", A(["wv", 304, 6, T], ["wv", 534, 6.5, T]), st=3),
    # ---- 5 up the mountains
    "roads": A(["wv", 528, 5.6, T], ["wv", 538, 5.7, T]),
    "casemate": FL("D08", X("valley", view0=[5.5, 1.5, 9], view1=[5.0, 1.5, 8], items=[
        {"t": 0.5, "type": "guns", "at": [[6.0, 3.5], [6.6, 0.8], [6.2, -2.2], [5.6, 5.5]], "aim": "hq", "stagger": 0.3},
        {"t": 2.5, "type": "tag", "at": [6.2, -2.2], "text": "HẦM PHÁO KHOÉT VÀO SƯỜN NÚI", "dy": 70}])),
    "direct": X("valley", view0=[1.5, 0.8, 18], view1=[1.2, 0.8, 16], items=[
        {"t": 0.2, "type": "pt", "at": "hq", "label": "MƯỜNG THANH", "anchor": "r", "color": "orange"},
        {"t": 0.6, "type": "guns", "at": GUNS, "aim": "hq", "stagger": 0.15, "fire": 2.5},
        {"t": 4.5, "type": "title", "text": "NGẮM BẮN TRỰC TIẾP", "sub": "PHÁO ĐẶT TRÊN SƯỜN NÚI HƯỚNG VÀO LÒNG CHẢO"}]),
    "decoy": X("valley", view0=[1.0, 0.8, 18], items=[
        {"t": 0.2, "type": "guns", "at": GUNS, "aim": "hq", "stagger": 0.1},
        {"t": 1.2, "type": "guns", "at": [[4.2, 6.5], [7.8, 2.0], [-4.6, -3.0], [7.2, -4.5], [-7.4, 4.5]], "aim": "hq", "stagger": 0.2},
        {"t": 2.6, "type": "tag", "at": [7.2, -4.5], "text": "TRẬN ĐỊA GIẢ", "dy": 70}]),
    "bikes": FL("D07", P("dancong")),
    "phadin": A(["in2", 446, 4.2, T], ["in2", 453, 5.4, T], ["wv", 528, 5.4, T]),
    "nav_blind": P("castor_cogny"),
    "wait": A(["wv", 380, 5.2, T], ["wv", 289, 5.2, T]),
    # ---- 6 Him Lam
    "d13": X("clock", time="17:05", sub="NGÀY 13 THÁNG 3 NĂM 1954"),
    "barrage": FL("D09", A(["in2", 453, 6, T], ["in2", 556, 6, T])),
    "himlam": FL("D10", X("valley", view0=[2.0, 2.4, 9], view1=[2.3, 2.6, 7], items=[
        {"t": 0.2, "type": "pt", "at": "himlam", "label": "HIM LAM", "sub": "BÉATRICE"},
        {"t": 0.8, "type": "arrow", "path": [[5.0, 4.6], [3.2, 3.2]], "dur": 1.4, "color": "yellow"},
        {"t": 1.2, "type": "arrow", "path": [[4.6, 1.0], [3.0, 2.4]], "dur": 1.4, "color": "yellow"},
        {"t": 6.0, "type": "x", "at": "himlam"}, {"t": 6.6, "type": "tag", "at": "himlam", "text": "THẤT THỦ ĐÊM 13/3", "dy": 80}])),
    "doclap": X("valley", view0=[0.8, 4.4, 10], items=[
        {"t": 0.0, "type": "x", "at": "himlam", "fade": 0.01},
        {"t": 0.3, "type": "pt", "at": "doclap", "label": "ĐỘC LẬP", "sub": "GABRIELLE"},
        {"t": 4.2, "type": "x", "at": "doclap"}, {"t": 4.8, "type": "tag", "at": "doclap", "text": "THẤT THỦ SÁNG 15/3", "dy": 80}]),
    "bankeo": X("valley", view0=[0.4, 3.0, 12], items=[
        {"t": 0.0, "type": "x", "at": "himlam", "fade": 0.01}, {"t": 0.0, "type": "x", "at": "doclap", "fade": 0.01},
        {"t": 0.3, "type": "pt", "at": "bankeo", "label": "BẢN KÉO", "sub": "ANNE-MARIE", "anchor": "r"},
        {"t": 3.5, "type": "x", "at": "bankeo"}, {"t": 6.5, "type": "title", "text": "PHÂN KHU BẮC SỤP ĐỔ", "sub": "CHỈ TRONG 5 NGÀY"}]),
    "counter": A(["in2", 523, 4.8, T], ["in2", 536, 4.8, T]),
    "piroth_end": X("phrase", photo="castor_cogny", text="RẠNG SÁNG 15/03/1954", size=110, color=WHT,
                    sub="TRUNG TÁ PIROTH TỰ SÁT TRONG HẦM"),
    "airfield": A(["wv", 290, 4, T], ["in2", 456, 5, T], ["wv", 300, 4.6, T]),
    # ---- 7 tightening
    "trenches": FL("D12", A(["wv", 271, 5.2, T], ["wv", 272, 5.2, T])),
    "parachute": FL("D11", A(["wv", 284, 5, T], ["wv", 280, 3, T], ["wv", 294, 3.9, T])),
    "paras": A(["wv", 280, 4, T], ["wv", 304, 6.8, T]),
    "vulture": X("stat", photo="indo003", lines=[["PARIS CẦU CỨU WASHINGTON", 84, WHT], ["MỸ CÂN NHẮC DÙNG MÁY BAY NÉM BOM HẠNG NẶNG", 44, CY],
                                                 ["CUỐI CÙNG: KHÔNG CAN THIỆP", 60, YEL]]),
    "hills": X("valley", view0=[0.8, 0.2, 9], view1=[1.0, 0.1, 7], items=[
        {"t": 0.2, "type": "pt", "at": "dominique", "label": "D1", "sub": "DOMINIQUE"},
        {"t": 0.6, "type": "pt", "at": [1.9, 0.0], "label": "C1", "sub": ""},
        {"t": 1.0, "type": "pt", "at": "a1", "label": "A1", "sub": "ÉLIANE 2", "anchor": "r", "color": "orange"},
        {"t": 1.4, "type": "pt", "at": [1.5, -1.2], "label": "E1", "sub": ""}]),
    "a1": P("trench_a1"),
    "rain": FL("D13", A(["in2", 383, 5.7, T], ["in2", 418, 5.7, T])),
    "cost": P("bridge_photo"),
    "tunnel": FL("D14", P("crater_a1")),
    # ---- 8 7 May
    "boom": FL("D15", A(["in2", 453, 7, T], ["in2", 601, 3, T], ["wv", 300, 4.6, T])),
    "collapse": A(["in2", 601, 3, T], ["wv", 300, 3.6, T]),
    "bunker": P("victory"),
    "isabelle": X("valley", view0=[0.3, -3.0, 13], items=[
        {"t": 0.0, "type": "x", "at": "hq", "fade": 0.01},
        {"t": 0.3, "type": "pt", "at": "isabelle", "label": "HỒNG CÚM", "sub": "ISABELLE"},
        {"t": 1.0, "type": "arrow", "path": [[0.2, -5.6], [-1.5, -8.5], [-3.5, -11]], "dur": 2.0, "color": "red", "dashed": True},
        {"t": 3.2, "type": "tag", "at": [-1.5, -8.5], "text": "PHÁ VÂY SANG LÀO – BỊ CHẶN", "dy": 60},
        {"t": 6.0, "type": "x", "at": "isabelle"}]),
    "prisoners": A(["wv", 323, 5, T], ["wv", 330, 4.6, T]),
    # ---- 9 end
    "geneva": A(["wv", 334, 4, T], ["wv", 338, 4.4, T], ["wv", 344, 4.2, T]),
    "legacy": A(["wv", 328, 2.4, T], ["wv", 330, 4, T], ["wv", 357, 5.5, T]),
    "lesson": P("how105b", dark=0.2),
    "final": FL("D16", A(["wv", 380, 5.6, T], ["wv", 289, 5.2, T])),
    "end": X("end", credits=[
        "Phim tư liệu: U.S. Army \"Why Viet-Nam\", Indo-China Newsreels – National Archives (public domain) · Ảnh: Wikimedia Commons",
        "Bản đồ: NASA Blue Marble, sơ đồ minh họa · Giọng đọc, âm thanh: ElevenLabs · Cảnh minh họa tạo bằng AI (Google Flow)"]),
}

SFX = {
    "h_clock": [("jungle_night", 0, 0.5)], "h_valley": [("dakota_drone", 1, 0.5)], "h_belief": [("jungle_night", 0, 0.4)],
    "h_fire": [("howitzer_shot", 0.6, 1.0), ("artillery_barrage", 1.5, 0.9)], "h_impact": [("big_explosion", 0, 1.0)],
    "title": [("howitzer_shot", 0.0, 0.8)], "sting": [("stamp", 0.3, 1.0)],
    "war8": [("mg_fire", 0.5, 0.35)], "castor": [("dakota_drone", 0, 0.8)], "airlift": [("dakota_drone", 0, 0.7)],
    "h_trap": [("boom_far", 2, 0.5)], "march": [("jungle_night", 0, 0.5)], "estimate": [("dakota_drone", 3, 0.4)],
    "pull": [("men_heave", 0, 0.8)], "slow": [("men_heave", 0, 0.8)], "ready": [("jungle_night", 0, 0.5)],
    "doubt": [("jungle_night", 0, 0.4)], "morale": [("men_heave", 0, 0.6)], "roads": [("digging", 0, 0.7)],
    "casemate": [("digging", 0, 0.5)], "direct": [("howitzer_shot", 3, 0.6)], "bikes": [("jungle_night", 0, 0.4)],
    "phadin": [("dakota_drone", 0, 0.6), ("explosion", 4.5, 0.8)], "wait": [("jungle_night", 0, 0.6)],
    "d13": [("morse", 0, 0.3)], "barrage": [("artillery_barrage", 0, 1.0), ("howitzer_shot", 0.3, 0.9)],
    "himlam": [("mg_fire", 0, 0.7), ("explosion", 3, 0.6)], "doclap": [("boom_far", 0, 0.6), ("mg_fire", 1, 0.4)],
    "bankeo": [("boom_far", 1, 0.5)], "counter": [("howitzer_shot", 0.4, 0.9), ("howitzer_shot", 4.9, 0.9)],
    "airfield": [("explosion", 4, 0.8), ("fire_crackle", 6, 0.5)], "trenches": [("digging", 0, 0.7)],
    "parachute": [("dakota_drone", 0, 0.7)], "paras": [("dakota_drone", 0, 0.5)], "a1": [("mg_fire", 0, 0.5)],
    "rain": [("rain_heavy", 0, 0.9)], "cost": [("rain_heavy", 0, 0.4)], "tunnel": [("digging", 0, 0.5)],
    "boom": [("big_explosion", 1.0, 1.0), ("mg_fire", 7, 0.5)], "collapse": [("mg_fire", 0, 0.5)],
    "isabelle": [("mg_fire", 1, 0.4)], "final": [("jungle_night", 0, 0.5)],
}

MUSIC = [  # (track, start scene id, volume)
    ("music_battle", "h_clock", 0.9), ("music_tension", "war8", 0.8), ("music_tension", "doubt", 0.85),
    ("music_tension", "roads", 0.8), ("music_battle", "d13", 0.95), ("music_tension", "trenches", 0.85),
    ("music_battle", "boom", 0.95), ("music_mourn", "geneva", 0.9),
]
MUSIC_DIP = ["h_impact", "quote", "piroth_end"]
NO_LOGO = {"title", "sting", "end"}
BLACK_TRANS = {"title", "sting", "war8", "giap", "doubt", "roads", "d13", "trenches", "boom", "geneva", "end"}
BED = "jungle_night"


# ---- Flow clips received (D01..D16): mix with archive so nothing freezes
VIS.update({
    "h_clock": M(["f", "D01", 0, None]),
    "h_fire": M(["f", "D02", 0, None]),
    "march": M(["f", "D05", 0, None], ["a", "wv", 330, 2.5, T]),
    "pull": M(["f", "D03", 0, None], ["a", "wv", 534, 4, T]),
    "slow": M(["f", "D04", 0, None], ["a", "wv", 538, 3, T]),
    "ready": M(["f", "D02", 2, None], ["a", "wv", 380, 1.8, T]),
    "doubt": M(["f", "D06", 0, None], ["a", "in2", 553, 2.4, T]),
    "morale": M(["f", "D03", 3, None], ["a", "wv", 534, 4, T], ["f", "D04", 5, None]),
    "casemate": M(["f", "D08", 0, None], ["a", "wv", 528, 4, T]),
    "bikes": M(["f", "D07", 0, None], ["a", "wv", 357, 4, T], ["a", "wv", 360, 2, T]),
    "barrage": M(["f", "D09", 0, None], ["a", "in2", 453, 4, T]),
    "himlam": M(["f", "D10", 0, None], ["a", "in2", 601, 3, T]),
    "parachute": M(["f", "D11", 0, 3], ["f", "D11", 5, None], ["a", "wv", 284, 5, T]),
    "trenches": M(["f", "D12", 0, None], ["a", "wv", 268, 3, T]),
    "rain": M(["f", "D13", 0, None], ["a", "in2", 383, 3.5, T]),
    "tunnel": M(["f", "D14", 0, None], ["a", "wv", 268, 2, T]),
    "boom": M(["f", "D15", 0, None], ["a", "in2", 453, 4, T], ["a", "wv", 300, 3, T]),
    "final": M(["f", "D16", 0, None], ["a", "wv", 380, 2.5, T]),
})


# ---- fallbacks while Wikimedia photos are unavailable (switch back automatically when the photo exists)
def _have(k):
    return any(os.path.exists(os.path.join(HERE, "photos", k + e)) for e in (".jpg", ".png", ".jpeg"))


_FB = {
    "h_question": ("how105a", M(["f", "D16", 0, 4.5], ["a", "wv", 296, 4, T])),
    "guns": ("how105b", M(["f", "D16", 2, None], ["a", "wv", 528, 4, T], ["a", "wv", 538, 3, T])),
    "nav_blind": ("castor_cogny", A(["in2", 553, 3, T], ["wv", 290, 4, T], ["in2", 523, 3.4, T])),
    "a1": ("trench_a1", M(["f", "D10", 2, None], ["a", "in2", 556, 5, T])),
    "cost": ("bridge_photo", M(["f", "D13", 2, None], ["a", "wv", 330, 4, T], ["a", "wv", 304, 2.5, T])),
    "bunker": ("victory", A(["wv", 323, 5, T], ["wv", 328, 2.4, T], ["wv", 330, 4, T], ["wv", 324, 2.9, T])),
    "lesson": ("how105b", P("fr_gun")),
}
for _k, (_ph, _alt) in _FB.items():
    if not _have(_ph):
        VIS[_k] = _alt
for _k in ("title", "fast", "steady"):
    if not _have("artillery"):
        VIS[_k][1]["spec"]["photo"] = "fr_pull"
if not _have("castor_cogny"):
    VIS["piroth_end"][1]["spec"]["photo"] = "decastries"
if not _have("indo003"):
    VIS["vulture"][1]["spec"].pop("photo", None)
