"""Visual + sound assignment for every scene of script_midway.SCENES (by id)."""
MID, PEARL, TOKYO = [-177.37, 28.21], [-157.95, 21.35], [139.7, 35.68]
KIDO, USF = [-179.3, 31.0], [-173.0, 32.0]
ALEUT, SF = [-166.54, 53.89], [-122.4, 37.8]
PAC = [-188, 32, 100]          # wide Pacific view (lon centre, lat centre, width deg)
BATTLE = [-176.0, 30.8, 21]    # tactical view around Midway

F = lambda src, st=0, en=None: ("flow", {"segs": [[src, st, en]]})
A = lambda *segs: ("arch", {"segs": [list(s) for s in segs]})
P = lambda name, **k: ("photo", dict(key=name, **k))
X = lambda kind, **spec: ("gfx", dict(kind=kind, spec=spec))
PRE = lambda name, st=0, en=None: ("pre", {"segs": [[name, st, en]]})

VIS = {
    # ---- 1 hook
    "h_clock": F("F17", 0, 5),
    "h_fleet": F("F01"),
    "h_deck": F("F02"),
    "h_belief": F("F12"),
    "h_dive": PRE("S03", 0, 9),
    "h_impact": F("F04", 0, 5),
    "h_six": F("F05", 3),
    "h_question": F("F21"),
    "title": X("title", photo="dauntless", l1="SÁU PHÚT ĐỊNH MỆNH", l2="TRẬN MIDWAY 1942"),
    "sting": X("sting"),
    # ---- 2 context
    "pearl": X("keyword", photo="pearl", word="TRÂN CHÂU CẢNG", sub="NGÀY 7 THÁNG 12 NĂM 1941"),
    "expand": X("map", view0=[116, 6, 56], view1=[117, 6, 50], items=[
        {"t": 0.5, "type": "pin", "at": [121, 14.6], "small": "THÁNG 12/1941", "big": "PHILIPPINES"},
        {"t": 1.7, "type": "pin", "at": [101.7, 3.1], "small": "THÁNG 1/1942", "big": "MÃ LAI", "anchor": "r"},
        {"t": 2.7, "type": "pin", "at": [103.8, 1.35], "small": "THÁNG 2/1942", "big": "SINGAPORE", "anchor": "m"},
        {"t": 3.9, "type": "pin", "at": [110, -7], "small": "THÁNG 3/1942", "big": "ĐÔNG ẤN HÀ LAN", "anchor": "m"}]),
    "yamamoto": X("portrait", photo="yamamoto", name="Yamamoto Isoroku", sub="TỔNG TƯ LỆNH HẠM ĐỘI LIÊN HỢP"),
    "industry": A(["npc2704", 200, 6, "npc"], ["npc2704", 446, 6, "npc"]),
    "missed": A(["npc11589", 700, 9, "full"]),
    "doolittle": A(["npc12472", 60, 9, "full"]),
    "doolittle2": A(["npc12472", 120, 8, "full"]),
    "midway_map": X("map", view0=PAC, view1=[-180, 30, 70], tilt=0.12, items=[
        {"t": 0.5, "type": "pin", "at": PEARL, "small": "CĂN CỨ HẠM ĐỘI MỸ", "big": "TRÂN CHÂU CẢNG", "anchor": "m"},
        {"t": 1.2, "type": "pin", "at": MID, "small": "ĐẢO SAN HÔ", "big": "MIDWAY"},
        {"t": 2.2, "type": "arrow", "path": [PEARL, MID], "dur": 1.6, "color": "yellow", "dashed": True, "w": 5},
        {"t": 3.6, "type": "tag", "at": [-167.5, 26.5], "text": "KHOẢNG 2.100 KM", "dy": -60}]),
    "plan": X("map", view0=PAC, view1=[-182, 30, 80], tilt=0.12, items=[
        {"t": 0.3, "type": "pin", "at": TOKYO, "small": "", "big": "NHẬT BẢN"},
        {"t": 0.6, "type": "pin", "at": MID, "small": "MỤC TIÊU", "big": "MIDWAY"},
        {"t": 1.0, "type": "arrow", "path": [[145, 15], [165, 22], [-178, 27.5]], "dur": 2.5, "color": "red", "icon": "ship"},
        {"t": 2.0, "type": "tag", "at": [158, 18], "text": "LỰC LƯỢNG ĐỔ BỘ", "dy": 40},
        {"t": 2.4, "type": "arrow", "path": [[150, 33], [170, 33], [-180, 31.5]], "dur": 2.5, "color": "red", "icon": "ship"},
        {"t": 3.4, "type": "tag", "at": [162, 34], "text": "4 TÀU SÂN BAY CHỜ SẴN", "dy": -50},
        {"t": 4.8, "type": "pin", "at": PEARL, "small": "HẠM ĐỘI MỸ", "big": "TRÂN CHÂU CẢNG", "anchor": "m"},
        {"t": 5.6, "type": "arrow", "path": [PEARL, [-172, 27]], "dur": 1.8, "color": "cyan", "dashed": True}]),
    "aleut": X("map", view0=[-182, 38, 90], view1=[-178, 42, 80], tilt=0.12, items=[
        {"t": 0.3, "type": "pin", "at": ALEUT, "small": "ĐÒN NGHI BINH", "big": "QUẦN ĐẢO ALEUT"},
        {"t": 0.8, "type": "arrow", "path": [[150, 42], [170, 48], [-168, 52.5]], "dur": 2.2, "color": "orange", "icon": "ship"},
        {"t": 0.3, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"}]),
    "force_jp": X("roster", photo="akagi", title="LỰC LƯỢNG CƠ ĐỘNG NHẬT BẢN",
                  portrait=["nagumo", "Nagumo Chuichi", "PHÓ ĐÔ ĐỐC"],
                  items=[["AKAGI", "SOÁI HẠM"], ["KAGA", ""], ["SORYU", ""], ["HIRYU", ""]]),
    "force_us": X("roster", photo="enterprise", title="TÀU SÂN BAY MỸ CÓ THỂ RA TRẬN",
                  items=[["ENTERPRISE", ""], ["HORNET", ""], ["YORKTOWN", "HƯ HẠI Ở TRẬN BIỂN SAN HÔ", [226, 40, 36]]]),
    "believe": F("F01", 4),
    # ---- 3 codebreaking
    "dungeon": F("F06"),
    "rochefort": X("portrait", photo="rochefort", name="Joseph Rochefort", sub="CHỈ HUY TRẠM GIẢI MÃ HYPO"),
    "jn25": X("codes"),
    "doubt": X("map", view0=[-160, 30, 80], view1=[-158, 31, 72], tilt=0.12, items=[
        {"t": 0.4, "type": "pin", "at": MID, "small": "ROCHEFORT", "big": "MIDWAY?"},
        {"t": 1.5, "type": "pin", "at": PEARL, "small": "WASHINGTON", "big": "HAWAII?", "anchor": "m"},
        {"t": 2.5, "type": "pin", "at": SF, "small": "", "big": "BỜ TÂY NƯỚC MỸ?", "anchor": "r"},
        {"t": 3.4, "type": "q", "at": [-150, 38]}]),
    "trick": X("telegram", header="MIDWAY → TRÂN CHÂU CẢNG · ĐIỆN KHÔNG MÃ HÓA", quote="“MÁY LỌC NƯỚC NGỌT TRÊN ĐẢO ĐÃ HỎNG.”"),
    "bite": X("telegram", header="ĐIỆN NHẬT BỊ CHẶN BẮT", quote="“AF ĐANG THIẾU NƯỚC NGỌT.”"),
    "nimitz": X("portrait", photo="nimitz", name="Chester Nimitz", sub="TỔNG TƯ LỆNH HẠM ĐỘI THÁI BÌNH DƯƠNG"),
    "trap": F("F07"),
    # ---- 4 the trap
    "yorktown_dock": P("yorktown_dock"),
    "welders": F("F08"),
    "spruance": X("portrait", photo="spruance", name="Raymond Spruance", sub="CHUẨN ĐÔ ĐỐC – THAY HALSEY"),
    "point_luck": X("map", view0=[-168, 27, 40], view1=[-169, 28, 33], tilt=0.16, bg="tactical", grid=5, items=[
        {"t": 0.3, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"},
        {"t": 0.6, "type": "pin", "at": PEARL, "small": "", "big": "TRÂN CHÂU CẢNG", "anchor": "m"},
        {"t": 1.0, "type": "arrow", "path": [PEARL, [-165, 27], USF], "dur": 3.0, "color": "cyan", "icon": "ship"},
        {"t": 3.6, "type": "ships", "at": USF, "n": 3, "side": "us", "ang": 200},
        {"t": 4.0, "type": "label", "at": USF, "small": "32°B · 173°T", "big": "ĐIỂM MAY MẮN", "dy": -140}]),
    "subs_late": X("map", view0=[-170, 27, 34], view1=[-170, 27, 30], tilt=0.16, bg="tactical", grid=5, items=[
        {"t": 0.3, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"},
        {"t": 0.4, "type": "arrow", "path": [PEARL, [-165, 27], USF], "dur": 1.5, "color": "cyan", "icon": "ship"},
        {"t": 2.2, "type": "subs", "path": [[-168, 31], [-163, 24]], "n": 7},
        {"t": 3.2, "type": "tag", "at": [-163, 24], "text": "TÀU NGẦM NHẬT ĐẾN MUỘN", "dy": 50}]),
    "pby_sight": PRE("R09_catalina"),
    # ---- 5 morning of 4 June
    "t0430": F("F10", 0, 3),
    "launch": F("F10", 3),
    "tone": X("map", view0=BATTLE, view1=[-176.4, 30.9, 18], bg="tactical", items=[
        {"t": 0.2, "type": "ships", "at": KIDO, "n": 4, "side": "jp", "label": "LỰC LƯỢNG CƠ ĐỘNG"},
        {"t": 0.5, "type": "fan", "at": [-178.8, 30.8], "rays": [[95, 0], [75, 0.15], [55, 0.3], [35, 1.6], [15, 0.45], [-5, 0.6], [-25, 0.75]], "len": 600, "late_label": "TONE SỐ 4 – TRỄ 30 PHÚT"},
        {"t": 0.3, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"}], corner="SÁNG 04/06/1942"),
    "pby_radio": PRE("R09_catalina", 2),
    "raid": A(["ford", 356, 3.4, "ford"], ["ford", 359.5, 2.8, "ford"], ["ford", 514, 6, "ford"], ["ford", 424, 3.8, "ford"]),
    "ford": A(["ford", 441, 4.5, "ford"], ["ford", 446, 6, "ford"], ["ford", 459, 3.5, "ford"]),
    "second": A(["ford", 503.5, 5.5, "ford"], ["ford", 529, 6.5, "ford"]),
    "mid_attack": A(["ford", 292, 8, "ford"], ["ford", 374, 5, "ford"], ["ford", 381, 3, "ford"]),
    "b26": F("F14", 0, 3.4),
    "no_hits": F("F01", 3),
    "rearm": X("portrait", photo="nagumo", name="Nagumo Chuichi",
               sub="07:15 – LỆNH THAY VŨ KHÍ"),
    "hangar": F("F11", 0, 3),
    "tone_report": F("F16"),
    "what_ships": F("F12", 3),
    "carrier": X("telegram", header="TRINH SÁT TONE SỐ 4 → NAGUMO", quote="“ĐỊCH CÓ VẺ CÓ MỘT TÀU SÂN BAY.”", clock="08:20"),
    "dilemma": X("map", view0=BATTLE, view1=[-176.5, 30.8, 17], bg="tactical", items=[
        {"t": 0.2, "type": "ships", "at": KIDO, "n": 4, "side": "jp"},
        {"t": 0.2, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"},
        {"t": 0.6, "type": "arrow", "path": [[-177.6, 28.6], [-178.6, 30.0], [-179.0, 30.8]], "dur": 2.2, "color": "yellow", "icon": "plane"},
        {"t": 1.6, "type": "tag", "at": [-178.0, 29.4], "text": "MÁY BAY VỀ – SẮP HẾT XĂNG", "dx": 30},
        {"t": 2.6, "type": "ships", "at": USF, "n": 3, "side": "us", "ang": 200},
        {"t": 3.0, "type": "tag", "at": USF, "text": "TÀU SÂN BAY MỸ", "dy": -80, "dx": -60}], clock="08:20"),
    "yamaguchi": X("portrait", photo="yamaguchi", name="Yamaguchi Tamon", sub="CHUẨN ĐÔ ĐỐC – TÀU HIRYU"),
    "refuse": F("F02", 0, 3.2),
    "recover": F("F02", 3),
    # ---- 6 US strike
    "spruance_go": PRE("R13_catcanh_my"),
    "scattered": X("map", view0=BATTLE, view1=[-175.8, 30.9, 18], bg="tactical", items=[
        {"t": 0.2, "type": "ships", "at": USF, "n": 3, "side": "us", "ang": 200},
        {"t": 0.2, "type": "ships", "at": [-178.6, 31.4], "n": 4, "side": "jp"},
        {"t": 0.6, "type": "arrow", "path": [USF, [-176.5, 32.3], [-178.3, 31.6]], "dur": 3, "color": "cyan", "icon": "plane"},
        {"t": 1.2, "type": "arrow", "path": [USF, [-176, 31], [-178.4, 30.4]], "dur": 3, "color": "cyan", "icon": "plane", "dashed": True},
        {"t": 1.8, "type": "arrow", "path": [USF, [-177, 33], [-180.5, 32.6]], "dur": 3, "color": "cyan", "icon": "plane", "dashed": True}]),
    "nowhere": X("map", view0=BATTLE, view1=[-176.5, 31, 20], bg="tactical", items=[
        {"t": 0.2, "type": "ships", "at": USF, "n": 3, "side": "us", "ang": 200},
        {"t": 0.2, "type": "ships", "at": [-178.6, 31.4], "n": 4, "side": "jp"},
        {"t": 0.5, "type": "arrow", "path": [USF, [-177, 32.6], [-182.5, 32.2]], "dur": 3.5, "color": "yellow", "icon": "plane"},
        {"t": 3.2, "type": "tag", "at": [-182.5, 32.2], "text": "NHÓM HORNET – BAY SAI HƯỚNG", "dy": -60, "dx": -120},
        {"t": 4.2, "type": "x", "at": [-182.5, 32.2]}]),
    "waldron": X("portrait", photo="waldron", name="John Waldron", sub="CHỈ HUY PHI ĐỘI NGƯ LÔI 8"),
    "vt8": A(["d84312", 176, 4.5, "per"], ["ford", 381, 3, "ford"]),
    "vt8_die": F("F14", 3.4),
    "gay": X("portrait", photo="gay", name="George Gay", sub="NGƯỜI SỐNG SÓT DUY NHẤT CỦA PHI ĐỘI 8"),
    "gay2": F("F15", 0, 6),
    "vt6vt3": X("stat", photo="dauntless", lines=[["41 MÁY BAY NGƯ LÔI", 120, [255, 255, 255]],
                                                    ["CHỈ KHOẢNG 6 CHIẾC TRỞ VỀ", 56, [255, 90, 80]]]),
    "sacrifice": A(["npc2649", 3, 8, "npc"]),
    "sky_open": X("altitude"),
    "mcclusky": X("portrait", photo="mcclusky", name="Wade McClusky", sub="CHỈ HUY KHÔNG ĐOÀN ENTERPRISE"),
    "search": A(["npc2649", 112.5, 9, "npc"]),
    "wake": F("F16"),
    "leslie": X("map", view0=[-178.6, 31.3, 12], view1=[-178.6, 31.3, 10], bg="tactical", grid=1, items=[
        {"t": 0.2, "type": "ships", "at": [-179.3, 31.0], "n": 4, "side": "jp", "label": "AKAGI · KAGA · SORYU · HIRYU", "ldx": -170},
        {"t": 0.6, "type": "arrow", "path": [[-176.3, 33.3], [-177.6, 32.0], [-179.0, 31.3]], "dur": 3, "color": "cyan", "icon": "plane"},
        {"t": 0.8, "type": "tag", "at": [-176.3, 33.3], "text": "ENTERPRISE – McCLUSKY", "dx": -100, "dy": -40},
        {"t": 1.4, "type": "arrow", "path": [[-174.8, 30.6], [-176.8, 30.9], [-178.8, 31.0]], "dur": 3, "color": "cyan", "icon": "plane"},
        {"t": 1.6, "type": "tag", "at": [-174.8, 30.6], "text": "YORKTOWN – LESLIE", "dx": -160, "dy": 50}], clock="10:20"),
    "see": F("F17", 2),
    # ---- 7 six minutes
    "t1022": X("clock", time="10:22", sub="NGÀY 4 THÁNG 6 NĂM 1942"),
    "peel": PRE("S03", 4, 9.2),
    "kaga": F("F04", 2),
    "best": PRE("S03", 9.2),
    "akagi_hit": PRE("R18_akagi"),
    "chain": F("F18old", 5.2),
    "soryu": F("F05", 0, 3.5),
    "t1028": F("F05", 3),
    "gay_sees": F("F15", 3),
    "nagumo_leave": F("F12", 4),
    "flip": X("stat", bg="white", flash=True, lines=[["TÀU SÂN BAY NHẬT: TỪ 4 CÒN 1", 110, [30, 30, 30]],
                                                    ["MỸ VẪN CÒN 3", 56, [20, 90, 170]]]),
    # ---- 8 Hiryu
    "not_over": A(["npc11589", 690, 10, "full"]),
    "hiryu_strike": F("F10", 2),
    "yorktown_hit": F("F19"),
    "repair": F("F20", 0, 5),
    "tomonaga": X("portrait", photo="tomonaga", name="Tomonaga Joichi", sub="CHỈ HUY ĐỢT TẤN CÔNG – KHÔNG ĐỦ XĂNG ĐỂ QUAY VỀ"),
    "torpedo": A(["ford", 686.5, 3.0, "ford"]),
    "found": A(["ford", 694, 2.8, "ford"], ["npc2649", 114, 6, "npc"]),
    "hiryu_hit": A(["d84312", 428, 10, "per"]),
    "hiryu_burn": F("F21"),
    "yamaguchi_end": F("F21", 3),
    # ---- 9 ending
    "retreat": X("map", view0=PAC, view1=[-190, 31, 90], tilt=0.12, items=[
        {"t": 0.3, "type": "pin", "at": MID, "small": "", "big": "MIDWAY"},
        {"t": 0.6, "type": "arrow", "path": [[-178, 31], [170, 33], [150, 34]], "dur": 3, "color": "red", "icon": "ship", "dashed": True},
        {"t": 2.0, "type": "tag", "at": [165, 34], "text": "HẠM ĐỘI NHẬT RÚT LUI", "dy": -60}]),
    "yorktown_end": F("F19", 4),
    "gay_rescue": A(["ford", 788, 4.6, "ford"], ["npc2649", 73.3, 5, "npc"]),
    "losses": X("stat", lines=[["NHẬT: 4 TÀU SÂN BAY · ~3.000 NGƯỜI", 92, [255, 255, 255]],
                               ["MỸ: 1 TÀU SÂN BAY · ~300 NGƯỜI", 92, [120, 200, 255]],
                               ["~250 MÁY BAY NHẬT – ~150 MÁY BAY MỸ", 44, [200, 200, 200]]]),
    "meaning": X("map", view0=PAC, view1=[-190, 20, 105], tilt=0.12, items=[
        {"t": 0.3, "type": "pin", "at": MID, "small": "6/1942", "big": "MIDWAY"},
        {"t": 1.0, "type": "arrow", "path": [PEARL, [175, 0], [160, -9]], "dur": 2.5, "color": "cyan", "icon": "ship"},
        {"t": 2.0, "type": "tag", "at": [160, -9], "text": "GUADALCANAL 8/1942", "dy": 50},
        {"t": 3.0, "type": "arrow", "path": [[-170, 15], [168, 10], [145, 15]], "dur": 2.5, "color": "cyan", "icon": "ship"},
        {"t": 4.5, "type": "tag", "at": [145, 15], "text": "MỸ PHẢN CÔNG", "dy": 50}]),
    "myth": X("memoir"),
    "not_luck": X("portraits", people=[["rochefort", "Joseph Rochefort", "GIẢI MÃ"], ["waldron", "John Waldron", "PHI ĐỘI NGƯ LÔI 8"],
                                       ["mcclusky", "Wade McClusky", "VỆT SÓNG ARASHI"]]),
    "close": F("F22"),
    "end": X("end", credits=[
        "Phim tư liệu: U.S. Navy / National Archives (public domain) – \"The Battle of Midway\" (1942), NPC-2649, NPC-2704, NPC-11589, NPC-12472, \"Introduction to Dive Bombing\"",
        "Ảnh: Hải quân Mỹ & Wikimedia Commons · Bản đồ: NASA Blue Marble · Giọng đọc, âm thanh: ElevenLabs",
        "Cảnh minh họa tạo bằng AI (Google Flow) · Thoại điện đài được tái hiện theo nội dung bức điện trong sử liệu"]),
}

SFX = {  # id: [(name, offset, volume)]
    "h_clock": [("prop_flyby", 0.3, 0.6)], "h_fleet": [("ocean_calm", 0, 0.5)], "h_deck": [("carrier_deck", 0, 0.6)],
    "h_dive": [("dive_scream", 1.0, 0.9)], "h_impact": [("big_explosion", 0, 1.0), ("fire_crackle", 2, 0.5)],
    "h_six": [("fire_crackle", 0, 0.5), ("boom_far", 2, 0.6)], "title": [("explosion", 0.0, 0.7)],
    "sting": [("stamp", 0.3, 1.0), ("morse", 0.6, 0.4)],
    "pearl": [("explosion", 0, 0.6), ("alarm", 0.5, 0.3)], "doolittle": [("prop_flyby", 1, 0.6)],
    "dungeon": [("typewriter", 0.5, 0.45)], "jn25": [("morse", 0, 0.45)], "trick": [("morse", 0.2, 0.5)],
    "bite": [("morse", 0.2, 0.5)], "welders": [("metal_hit", 0.5, 0.4)], "pby_sight": [("prop_flyby", 0.5, 0.5)],
    "t0430": [("carrier_deck", 0, 0.7)], "launch": [("prop_flyby", 0.5, 0.7)],
    "raid": [("alarm", 0, 0.35), ("aa_fire", 0.5, 0.7), ("explosion", 2.5, 0.7)], "ford": [("aa_fire", 0, 0.5), ("boom_far", 3, 0.5)],
    "mid_attack": [("flak", 0, 0.6)], "b26": [("prop_flyby", 0, 0.8), ("splash", 2.2, 0.7)], "no_hits": [("splash", 0.5, 0.5)],
    "hangar": [("metal_hit", 0.8, 0.4)], "carrier": [("morse", 0.2, 0.5)], "spruance_go": [("carrier_deck", 0, 0.6), ("prop_flyby", 4.5, 0.7)],
    "vt8": [("flak", 0, 0.5)], "vt8_die": [("flak", 0, 0.6), ("splash", 3.5, 0.8)], "gay2": [("ocean_calm", 0, 0.6)],
    "sacrifice": [("ocean_calm", 0, 0.5)], "search": [("prop_flyby", 0, 0.4)], "wake": [("ocean_calm", 0, 0.4)],
    "see": [("prop_flyby", 0, 0.5)], "peel": [("dive_scream", 0, 1.0)], "kaga": [("big_explosion", 0.4, 1.0)],
    "best": [("dive_scream", 0, 0.9)], "akagi_hit": [("big_explosion", 0.2, 1.0)], "chain": [("explosion", 0, 0.9), ("big_explosion", 1.5, 0.8)],
    "soryu": [("explosion", 0.3, 0.9)], "t1028": [("fire_crackle", 0, 0.6)], "gay_sees": [("fire_crackle", 0, 0.4), ("ocean_calm", 0, 0.4)],
    "nagumo_leave": [("fire_crackle", 0, 0.5)], "flip": [("boom_far", 0, 0.6)],
    "hiryu_strike": [("prop_flyby", 0.5, 0.6)], "yorktown_hit": [("flak", 0, 0.7), ("explosion", 3, 0.7)],
    "repair": [("fire_crackle", 0, 0.5)], "torpedo": [("explosion", 1.0, 0.7)], "hiryu_hit": [("dive_scream", 0, 0.8), ("big_explosion", 6, 0.8)],
    "hiryu_burn": [("fire_crackle", 0, 0.5)], "yorktown_end": [("water_rush", 1, 0.4)], "gay_rescue": [("prop_flyby", 0, 0.4)],
    "close": [("ocean_calm", 0, 0.6), ("prop_flyby", 1, 0.3)],
}

MUSIC = [  # (track, start scene id, volume)
    ("music_battle", "h_clock", 0.9), ("music_tension", "pearl", 0.8), ("music_tension", "t0430", 0.85),
    ("music_battle", "spruance_go", 0.95), ("music_battle", "not_over", 0.9), ("music_mourn", "retreat", 0.9),
]
MUSIC_DIP = ["h_impact", "t1022", "flip"]          # scenes where music drops away for impact
NO_LOGO = {"title", "sting", "end"}
BLACK_TRANS = {"title", "sting", "pearl", "dungeon", "yorktown_dock", "t0430", "spruance_go", "t1022", "not_over", "retreat", "end"}


# ---- v2: more archive footage in the hook, no frozen frames (segments sized to scene length)
M = lambda *segs: ("mix", {"segs": [list(s) for s in segs]})
N, FU, FO, PE = "npc", "full", "ford", "per"
VIS.update({
    "h_clock": M(["f", "F01", 0, 5.6]),
    "h_fleet": M(["a", "npc11589", 690, 4, FU], ["a", "npc11589", 702, 3.5, FU], ["a", "npc11589", 36, 2.2, FU]),
    "h_deck": M(["a", "npc2704", 200, 5, N], ["a", "npc11589", 144, 4.5, FU]),
    "h_belief": M(["a", "npc11589", 594, 4.5, FU], ["a", "npc11589", 312, 4, FU]),
    "h_dive": M(["p", "S03", 0, 10.5]),
    "h_impact": M(["a", "ford", 455.6, 1.3, FO], ["a", "ford", 520, 2.8, FO]),
    "h_six": M(["f", "F05", 3, None], ["a", "ford", 647, 1.4, FO], ["a", "ford", 652, 1.4, FO], ["a", "ford", 643, 1.5, FO]),
    "h_question": M(["a", "ford", 461, 2.5, FO], ["a", "npc11589", 576, 4.5, FU], ["a", "npc11589", 720, 2, FU]),
    "believe": M(["f", "F01", 4, None], ["a", "npc11589", 600, 5, FU]),
    "t0430": M(["a", "npc2704", 35, 2.5, N], ["f", "F10", 0, 3], ["a", "npc11589", 210, 4, FU]),
    "pby_sight": M(["p", "R09_catalina", 0, None], ["a", "ford", 792, 2.5, FO], ["a", "ford", 801, 2, FO]),
    "pby_radio": M(["p", "R09_catalina", 2, None], ["a", "ford", 56, 4, FO], ["a", "ford", 64, 3, FO], ["a", "ford", 72, 3, FO]),
    "launch": M(["f", "F10", 3, None], ["a", "npc2704", 165, 4, N]),
    "b26": M(["a", "ford", 360, 3.5, FO], ["f", "F14", 0, 3.4], ["a", "ford", 624, 1.4, FO]),
    "no_hits": M(["f", "F01", 3, None], ["a", "ford", 668.5, 3, FO]),
    "hangar": M(["f", "F11", 0, 3], ["a", "npc2704", 460, 5, N]),
    "what_ships": M(["f", "F12", 3, None], ["a", "npc11589", 360, 4.5, FU]),
    "refuse": M(["f", "F02", 0, 3.2], ["a", "npc2704", 445, 5, N], ["a", "npc11589", 450, 4.5, FU], ["a", "npc11589", 156, 3, FU]),
    "recover": M(["f", "F02", 3, None], ["a", "npc2704", 360, 5, N]),
    "vt8": M(["a", "d84312", 176, 4.5, PE], ["a", "npc2704", 75, 4, N], ["a", "ford", 381, 3, FO]),
    "vt8_die": M(["f", "F14", 3.4, None], ["a", "ford", 664, 3, FO], ["a", "ford", 673, 2, FO]),
    "wake": M(["f", "F16", 0, None], ["a", "npc11589", 84, 4, FU]),
    "peel": M(["p", "S03", 4, 9.2], ["a", "d84312", 412, 4, PE]),
    "akagi_hit": M(["p", "R18_akagi", 0, None], ["a", "ford", 470, 2.8, FO]),
    "chain": M(["f", "F18old", 5.2, None], ["a", "ford", 464, 0.9, FO], ["a", "ford", 473, 2, FO]),
    "soryu": M(["f", "F05", 0, 3.5], ["a", "d84312", 419, 3, PE], ["a", "ford", 504, 3.5, FO]),
    "t1028": M(["f", "F05", 3, None], ["a", "ford", 536, 4, FO], ["a", "ford", 688, 1.5, FO], ["a", "npc11589", 728, 2, FU]),
    "gay_sees": M(["f", "F15", 3, None], ["a", "ford", 805, 4, FO]),
    "nagumo_leave": M(["f", "F12", 4, None], ["a", "npc11589", 90, 2, FU], ["a", "npc11589", 222, 3, FU]),
    "torpedo": M(["a", "ford", 686.5, 3, FO], ["a", "npc11589", 624, 4, FU], ["a", "npc11589", 636, 3.5, FU]),
    "yamaguchi_end": M(["f", "F21", 3, None], ["a", "npc11589", 606, 4, FU], ["a", "npc11589", 714, 4, FU]),
    "yorktown_end": M(["f", "F19", 4, None], ["a", "npc11589", 678, 5, FU], ["a", "npc11589", 540, 3, FU]),
    "industry": A(["npc2704", 200, 6, "npc"], ["npc2704", 446, 6, "npc"], ["npc2704", 470, 2.5, "npc"]),
})
VIS.update({
    "hiryu_strike": M(["f", "F10", 2, None], ["a", "npc2704", 185, 3, N]),
    "best": M(["p", "S03", 9.2, None], ["a", "d84312", 456, 3, PE]),
    "see": M(["f", "F17", 2, None], ["a", "d84312", 428, 2.5, PE]),
})
VIS["h_impact"] = M(["a", "ford", 520, 3.6, FO])
