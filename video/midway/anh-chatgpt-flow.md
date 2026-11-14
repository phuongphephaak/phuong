# Danh sách cảnh: ảnh ChatGPT → video Google Flow (Midway)

## Quy trình cho mỗi cảnh

1. **ChatGPT:** dán *Lời nhắc ảnh* + câu đuôi chung bên dưới. Yêu cầu khổ **ngang**. Tải ảnh về, đặt tên theo mã (`S01.png`).
2. **Kiểm tra ảnh** (quan trọng – xem mục *Lỗi hay gặp*). Sai thì bảo ChatGPT sửa đúng chỗ sai.
3. **Google Flow:** chọn **Frames to Video** (Khung hình thành video), tải ảnh lên làm **khung hình đầu**, dán *Lời nhắc chuyển động*, khổ 16:9.
   Tạo 2 phiên bản, chọn bản đẹp nhất, tải về đặt tên `S01.mp4`. Âm thanh của Flow không cần (mình lồng tiếng và hiệu ứng riêng).
4. Tải cả ảnh và video vào thư mục **Midway** trên Google Drive.

**Câu đuôi chung cho mọi lời nhắc ảnh:**
```
Photorealistic photograph, 1942 World War II, shot on 35mm film, natural light, subtle film grain, landscape 16:9, main subject centered, no text, no logos, no modern objects.
```

## Mẹo để video trông thật
- Lời nhắc chuyển động chỉ tả **chuyển động và máy quay**, không tả lại cảnh; chuyển động **nhỏ, chậm** (khói, sóng, cánh quạt, máy quay đẩy vào chậm) trông thật nhất.
- Tránh cận mặt người và bàn tay: AI dễ làm méo khi chuyển động. Ưu tiên cảnh toàn, cảnh trung, người quay lưng hoặc nghiêng.
- Giữ đồng nhất: tạo S01 và S03 trước. Khi tạo ảnh sau, tải ảnh trước lên ChatGPT và nói *"giữ cùng phong cách màu và kiểu máy bay/tàu như ảnh này"*.
- Nếu video bị biến dạng (máy bay mọc thêm cánh, tàu đổi hình), tạo lại hoặc rút gọn lời nhắc chuyển động.
- **Không** tạo ảnh/video giả người thật (Nimitz, Nagumo, McClusky…). Nhân vật thật dùng ảnh thật.

## Lỗi lịch sử hay gặp – kiểm tra trước khi dùng
- Máy bay Mỹ 1942: **ngôi sao trắng trong vòng tròn xanh, KHÔNG có chấm đỏ ở giữa** (chấm đỏ bị xóa từ giữa tháng 5/1942), không có sọc ngang hai bên sao (kiểu đó có từ 1943).
- Máy bay Nhật: vòng tròn đỏ (hinomaru), Zero màu xám nhạt.
- Tàu sân bay Nhật: boong gỗ màu vàng nâu, **hình tròn đỏ trên boong phía mũi**; đài chỉ huy nhỏ (Akagi, Hiryu ở **bên trái**; Kaga, Soryu ở bên phải).
- Không có máy bay phản lực, tàu hiện đại, radar hình đĩa, chữ viết lạ.

## Ưu tiên
- **Ưu tiên 1** (cảnh mở đầu và cao trào – nên làm trước): S01, S02, S03, S04, S05, S10, S13, S14, S16, S17, S18
- **Ưu tiên 2:** S06, S07, S08, S11, S12, S15, S19, S20, S21
- **Ưu tiên 3** (có thể dùng mô phỏng thay): S09, S22

Cảnh nào chưa có, mình dùng mô phỏng bằng code thay thế để dựng bản nháp.

## Danh sách cảnh

### S01 – Hạm đội 4 tàu sân bay Nhật nhìn từ trên cao (cảnh 2 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
High aerial view of four Imperial Japanese Navy aircraft carriers of 1942 sailing in formation across the deep blue Pacific, long white wakes, escort destroyers, scattered cumulus clouds, morning sun. The carriers have wooden flight decks with a red circle painted near the bow and a small island on the left side.
```
**Lời nhắc chuyển động (Flow):**
```
Slow aerial drift forward following the fleet. Ships move steadily, wakes trail behind, cloud shadows slide across the water. Camera steady, documentary feel.
```

### S02 – Boong tàu sân bay Nhật đầy máy bay (cảnh 3 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Flight deck of a 1942 Japanese aircraft carrier crowded with parked Zero fighters and Kate torpedo bombers in light grey-green paint with red circles, deck crew in white and brown uniforms, wind, morning light, open ocean beyond.
```
**Lời nhắc chuyển động (Flow):**
```
Propellers start spinning, deck crew walk between the planes, flags flutter in strong wind. Slow handheld push-in.
```

### S03 – Máy bay ném bom bổ nhào Mỹ lật cánh lao xuống (cảnh 5, 73 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Formation of US Navy SBD Dauntless dive bombers in 1942 blue-grey paint with plain white star in a blue circle insignia (no red center), flying high above scattered clouds, the leading plane rolling over into a steep dive, ocean far below.
```
**Lời nhắc chuyển động (Flow):**
```
The lead plane rolls over and dives steeply out of frame, the next plane follows. Camera tracks alongside, wind and engine vibration.
```

### S04 – Bom nổ trên boong tàu sân bay (cảnh 6, 76 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Moment a bomb explodes on the wooden flight deck of a 1942 Japanese aircraft carrier among parked planes, huge orange fireball, debris flying, black smoke, seen from a low angle on the sea nearby.
```
**Lời nhắc chuyển động (Flow):**
```
The fireball expands, debris arcs outward, thick black smoke rises, secondary small explosions. Camera shakes slightly. No new ships appear.
```

### S05 – Ba tàu sân bay bốc cháy nhìn từ xa (cảnh 7, 79 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Wide view of the Pacific Ocean with three distant aircraft carriers burning, three tall columns of black smoke rising into a bright sky, calm sea in the foreground.
```
**Lời nhắc chuyển động (Flow):**
```
Smoke columns slowly billow and drift with the wind, flames flicker at the base, gentle waves in the foreground. Very slow push-in.
```

### S06 – Căn hầm giải mã (cảnh 23 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
Windowless basement office at Pearl Harbor in 1942, US Navy codebreakers in shirtsleeves at desks piled with papers, index cards and IBM punch cards, typewriters, ashtrays, cigarette smoke under bare light bulbs.
```
**Lời nhắc chuyển động (Flow):**
```
Cigarette smoke curls upward, one man types, another flips through cards, a light bulb sways slightly. Slow dolly sideways.
```

### S07 – Phòng chỉ huy, bàn bản đồ (cảnh 30 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
1942 US Navy headquarters room, officers in khaki uniforms seen from behind and the side leaning over a large map table of the Pacific Ocean with small wooden ship markers, warm lamp light, tense atmosphere.
```
**Lời nhắc chuyển động (Flow):**
```
An officer pushes a ship marker across the map with a long stick, others lean in. Slow push-in. Faces stay mostly turned away.
```

### S08 – Sửa Yorktown trong ụ khô ban đêm (cảnh 32 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
Night in a Pearl Harbor dry dock in 1942, workers welding the damaged steel hull of a huge aircraft carrier, bright welding sparks falling, searchlights, steam, scaffolding.
```
**Lời nhắc chuyển động (Flow):**
```
Sparks shower down, welders move along the scaffolding, searchlight beams sweep through steam. Slow tilt up along the hull.
```

### S09 – Thủy phi cơ Catalina lúc bình minh (cảnh 36 · ưu tiên 3)

**Lời nhắc ảnh (ChatGPT):**
```
A US Navy PBY Catalina flying boat in 1942 blue-grey paint flying low over the open ocean at dawn, orange sky, long shadows on the water.
```
**Lời nhắc chuyển động (Flow):**
```
The aircraft flies steadily across frame, propellers spinning, camera tracks alongside it. Sun glints on the sea.
```

### S10 – Máy bay Nhật cất cánh lúc rạng đông (cảnh 38 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Dawn on a 1942 Japanese aircraft carrier, a Zero fighter lifting off the bow of the flight deck while others wait with engines running, deck crew waving caps, exhaust smoke, low orange sun.
```
**Lời nhắc chuyển động (Flow):**
```
The plane accelerates and lifts off the bow, the next taxis forward, crew wave caps. Camera static on deck, slight wind shake.
```

### S11 – Thợ máy tháo ngư lôi trong khoang chứa (cảnh 48 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
Hangar deck of a 1942 Japanese aircraft carrier, sweating mechanics pushing a heavy torpedo on a wheeled cart beneath a torpedo bomber, bombs stacked nearby, chains and hoists, dim yellow light.
```
**Lời nhắc chuyển động (Flow):**
```
Mechanics strain to push the cart, a chain hoist lowers a bomb, a lamp swings slightly. Slow lateral camera move.
```

### S12 – Đài chỉ huy tàu Nhật nhận điện (cảnh 50 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
Bridge of a 1942 Japanese aircraft carrier, officers in dark navy uniforms reading a paper message, one with binoculars, seen in medium-wide shot, ocean visible through the windows, tense.
```
**Lời nhắc chuyển động (Flow):**
```
An officer lowers binoculars and turns to the others, the paper trembles in the wind, sea moves outside the windows. Slow push-in.
```

### S13 – Máy bay Mỹ cất cánh từ Enterprise (cảnh 56 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Deck of the US aircraft carrier in 1942, dark blue SBD Dauntless dive bombers with plain white star in a blue circle insignia (no red center) lined up, the first one taking off, flight deck officer waving a checkered flag, sailors in blue dungarees watching.
```
**Lời nhắc chuyển động (Flow):**
```
The first bomber accelerates down the deck and lifts off, the flag officer waves the next one forward. Camera static, propeller wash blows sailors' clothes.
```

### S14 – Máy bay ngư lôi bay sát mặt biển giữa làn đạn (cảnh 60, 61 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
US Navy TBD Devastator torpedo bombers flying extremely low over the ocean toward distant Japanese ships, anti-aircraft shell bursts in the sky, water splashes from gunfire around them.
```
**Lời nhắc chuyển động (Flow):**
```
The planes skim the waves toward the ships, splashes erupt nearby, one plane trails smoke and drops toward the sea. Tracking shot from the side.
```

### S15 – Phi công trôi trên biển nhìn tàu cháy (cảnh 63, 80 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
A lone American pilot in a 1942 life vest floating in the open ocean, holding a seat cushion over his head, three burning ships with black smoke on the horizon, seen from just above water level.
```
**Lời nhắc chuyển động (Flow):**
```
Waves gently rise and fall, the pilot bobs in the water, distant smoke drifts. Camera floats at water level.
```

### S16 – Vệt sóng tàu khu trục nhìn từ trên cao (cảnh 69 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
View from a high-flying plane looking down at the ocean, a single 1942 Japanese destroyer racing at high speed leaving a long white arrow-shaped wake, scattered clouds below the camera.
```
**Lời nhắc chuyển động (Flow):**
```
The destroyer moves forward leaving the wake, thin clouds pass beneath the camera. Slow aerial drift following the wake.
```

### S17 – Góc nhìn bổ nhào xuống tàu sân bay (cảnh 71, 74 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Point of view from the cockpit of a diving 1942 dive bomber, looking down through the windscreen at a Japanese aircraft carrier far below with planes on its yellow wooden deck, anti-aircraft bursts around.
```
**Lời nhắc chuyển động (Flow):**
```
The carrier grows larger as the plane dives, flak bursts pass by, the windscreen vibrates. Steady accelerating dive.
```

### S18 – Nổ dây chuyền trong khoang chứa (cảnh 77 · ưu tiên 1)

**Lời nhắc ảnh (ChatGPT):**
```
Huge explosion bursting up through the flight deck elevator of a 1942 aircraft carrier, deck planks buckled, burning planes, flames and black smoke pouring out, sailors running.
```
**Lời nhắc chuyển động (Flow):**
```
Flames erupt upward, secondary explosions flash, smoke billows, burning debris falls. Camera shakes. No new objects appear.
```

### S19 – Máy bay Nhật tấn công Yorktown, pháo phòng không (cảnh 84, 85 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
A 1942 US aircraft carrier under air attack, dense black anti-aircraft bursts in the sky, Japanese dive bombers diving toward it, a column of smoke rising from the deck, seen from a nearby ship.
```
**Lời nhắc chuyển động (Flow):**
```
Flak bursts pop across the sky, a plane dives and pulls away, smoke rises from the carrier. Handheld documentary camera from a ship's deck.
```

### S20 – Thủy thủ Mỹ dập lửa (cảnh 86 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
US Navy sailors in 1942 helmets and blue dungarees fighting a fire with hoses on the deck of a damaged aircraft carrier, thick black smoke, water spray.
```
**Lời nhắc chuyển động (Flow):**
```
Water jets spray into the smoke, sailors drag hoses forward, smoke swirls. Handheld camera.
```

### S21 – Tàu sân bay cháy lúc hoàng hôn (cảnh 91 · ưu tiên 2)

**Lời nhắc ảnh (ChatGPT):**
```
A burning Japanese aircraft carrier at dusk on a calm sea, flames along the flight deck reflecting on the water, black smoke against an orange sky.
```
**Lời nhắc chuyển động (Flow):**
```
Flames flicker, smoke rises and drifts, reflections ripple on the water. Very slow push-in.
```

### S22 – Kết: biển lúc hoàng hôn, máy bay bay xa (cảnh 100 · ưu tiên 3)

**Lời nhắc ảnh (ChatGPT):**
```
Calm Pacific Ocean at sunset, golden light on gentle waves, a single 1942 dive bomber flying away toward the horizon, peaceful and somber.
```
**Lời nhắc chuyển động (Flow):**
```
The plane slowly shrinks toward the horizon, waves glitter, clouds drift. Slow pull-back.
```
