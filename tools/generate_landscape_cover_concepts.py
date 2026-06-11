from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design_references"
IMG = ROOT / "app" / "static" / "images"
W, H = 1680, 945
S = 1


def f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size * S)
    return ImageFont.load_default()


def c(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def cover(path: Path, size: tuple[int, int], focus_x: float = 0.5, focus_y: float = 0.5) -> Image.Image:
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, min(nw - sw, int((nw - sw) * focus_x)))
    y = max(0, min(nh - sh, int((nh - sh) * focus_y)))
    return im.crop((x, y, x + sw, y + sh)).convert("RGBA")


def gradient(size, stops):
    w, h = size
    out = Image.new("RGBA", size)
    px = out.load()
    for y in range(h):
        t = y / max(1, h - 1)
        lo, hi = stops[0], stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = max(0.001, hi[0] - lo[0])
        k = (t - lo[0]) / span
        col = tuple(int(lo[1][j] + (hi[1][j] - lo[1][j]) * k) for j in range(4))
        for x in range(w):
            px[x, y] = col
    return out


def rounded(draw, box, radius=8, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, body, size=24, fill="#173126", bold=False, anchor=None):
    draw.text(xy, body, font=f(size, bold), fill=fill, anchor=anchor)


def wrap(draw, xy, body, size, fill, max_w, line_gap=10, bold=False):
    x, y = xy
    line = ""
    font = f(size, bold)
    for ch in body:
        test = line + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w or not line:
            line = test
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += size + line_gap
            line = ch
    if line:
        draw.text((x, y), line, font=font, fill=fill)
        y += size + line_gap
    return y


def icon_leaf(draw, cx, cy, scale=1.0, fill="#6f8c63", outline=None):
    r = int(12 * scale)
    draw.ellipse((cx - r * 2, cy - r, cx, cy + r), fill=fill, outline=outline)
    draw.ellipse((cx, cy - r, cx + r * 2, cy + r), fill=fill, outline=outline)
    draw.line((cx, cy + r * 2, cx, cy - r), fill=fill, width=max(1, int(3 * scale)))


def icon_sun(draw, cx, cy, scale=1.0, fill="#f2bd42"):
    r = int(9 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    for dx, dy in [(0, -22), (0, 22), (-22, 0), (22, 0), (-15, -15), (15, -15), (-15, 15), (15, 15)]:
        draw.line((cx + dx * scale * 0.7, cy + dy * scale * 0.7, cx + dx * scale, cy + dy * scale), fill=fill, width=max(1, int(2 * scale)))


def icon_clock(draw, cx, cy, scale=1.0, color="#6f8c63"):
    r = int(18 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=max(1, int(2 * scale)))
    draw.line((cx, cy, cx, cy - r + 6), fill=color, width=max(1, int(2 * scale)))
    draw.line((cx, cy, cx + r - 8, cy + 5), fill=color, width=max(1, int(2 * scale)))


def icon_waves(draw, cx, cy, scale=1.0, color="#6f8c63"):
    for i in range(3):
        y = cy - 12 * scale + i * 12 * scale
        draw.arc((cx - 24 * scale, y - 8 * scale, cx + 4 * scale, y + 8 * scale), 200, 340, fill=color, width=max(1, int(2 * scale)))
        draw.arc((cx + 2 * scale, y - 8 * scale, cx + 30 * scale, y + 8 * scale), 200, 340, fill=color, width=max(1, int(2 * scale)))


def icon_gear(draw, cx, cy, scale=1.0, color="#617363"):
    r = int(13 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=max(1, int(2 * scale)))
    draw.ellipse((cx - 4 * scale, cy - 4 * scale, cx + 4 * scale, cy + 4 * scale), fill=color)
    for dx, dy in [(0, -20), (0, 20), (-20, 0), (20, 0), (-14, -14), (14, -14), (-14, 14), (14, 14)]:
        draw.line((cx + dx * scale * 0.65, cy + dy * scale * 0.65, cx + dx * scale, cy + dy * scale), fill=color, width=max(1, int(2 * scale)))


def button(draw, box, label, bg="#f5be3f", fg="#314932", outline=None, icon=True):
    rounded(draw, box, radius=8, fill=bg, outline=outline or bg, width=1)
    x1, y1, x2, y2 = box
    if icon:
        icon_leaf(draw, x1 + 78, (y1 + y2) // 2, 0.75, fill=fg)
        tx = x1 + 120
    else:
        tx = x1 + 40
    text(draw, (tx, (y1 + y2) // 2 - 15), label, 24, fg, True)
    draw.line((x2 - 58, (y1 + y2) // 2, x2 - 34, (y1 + y2) // 2), fill=fg, width=3)
    draw.line((x2 - 44, (y1 + y2) // 2 - 10, x2 - 34, (y1 + y2) // 2), fill=fg, width=3)
    draw.line((x2 - 44, (y1 + y2) // 2 + 10, x2 - 34, (y1 + y2) // 2), fill=fg, width=3)


def glass_card(base: Image.Image, box, radius=8, fill=(255, 255, 248, 210), outline=(38, 70, 52, 34)):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rounded(d, box, radius, fill, outline, 1)
    base.alpha_composite(layer)


def soft_shadow(base: Image.Image, box, radius=12, alpha=32, blur=22):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rounded(d, box, radius, (41, 66, 50, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def save(im: Image.Image, name: str) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    im.convert("RGB").save(path, quality=96)
    return path


def concept_01_game_garden() -> Path:
    bg = cover(IMG / "presets" / "lakeside-deck.png", (W, H), 0.47, 0.45)
    bg = Image.blend(Image.new("RGBA", (W, H), "#f9fbef"), bg, 0.72)
    bg.alpha_composite(gradient((W, H), [(0, c("#fffdf4", 185)), (0.48, c("#eef7f1", 40)), (1, c("#eef7f1", 170))]))
    d = ImageDraw.Draw(bg)

    # Top navigation
    rounded(d, (0, 0, W, 112), 0, c("#fffdf4", 232), c("#d9dfd3", 255))
    icon_leaf(d, 64, 56, 1.1, "#6f8c63")
    text(d, (108, 40), "灵感世界", 34, "#2f5639", True)
    nav = ["首页", "花园", "练习", "记录", "关于"]
    x = 560
    for i, item in enumerate(nav):
        if i == 0:
            rounded(d, (x - 24, 36, x + 62, 82), 8, c("#e8eee4"), None)
        text(d, (x, 50), item, 17, "#314932", True if i == 0 else False)
        x += 115
    rounded(d, (1286, 30, 1554, 90), 8, c("#fffdf4", 210), c("#d9dfd3"))
    text(d, (1348, 45), "Level 3", 18, "#425d47", True)
    rounded(d, (1348, 68, 1468, 74), 3, c("#dbe1d5"), None)
    rounded(d, (1348, 68, 1426, 74), 3, c("#6f8c63"), None)
    rounded(d, (1582, 30, 1640, 90), 8, c("#fffdf4", 210), c("#d9dfd3"))
    icon_gear(d, 1611, 60, 0.8, "#617363")

    # Hero text
    text(d, (98, 247), "灵感世界", 76, "#2e563a", True)
    icon_leaf(d, 542, 248, 0.9, "#7c9a6b")
    text(d, (100, 356), "慢下来，给空间一点生长的时间。", 28, "#60745f", False)
    wrap(d, (100, 416), "选择一个真实空间，加入植物、光线与呼吸练习，把环境改造成更温和的样子。", 24, "#647464", 490, 13)
    button(d, (98, 505, 532, 582), "开始一次平静创作", "#f2bd42", "#334a32")
    rounded(d, (98, 602, 460, 666), 8, c("#fffdf4", 220), c("#d8d0bd"))
    icon_leaf(d, 176, 633, 0.64, "#6f8c63")
    text(d, (234, 618), "查看练习", 22, "#6b806b", True)

    # Main garden preview
    hero = cover(IMG / "presets" / "bamboo-courtyard.png", (960, 650), 0.52, 0.45)
    hero = Image.blend(Image.new("RGBA", hero.size, "#fff7df"), hero, 0.86)
    hero.alpha_composite(gradient(hero.size, [(0, c("#fffdf4", 30)), (1, c("#203c28", 60))]))
    soft_shadow(bg, (660, 158, 1620, 815), 16, 40, 28)
    bg.alpha_composite(hero, (660, 158))
    rounded(d, (660, 158, 1620, 815), 16, None, c("#fffdf4", 210), 2)
    glass_card(bg, (700, 182, 814, 242), 8, c("#395943", 118), c("#fffdf4", 40))
    icon_sun(d, 758, 212, 0.75, "#ffd45a")
    text(d, (786, 194), "晨间", 15, "#fffdf4", True)
    text(d, (786, 216), "7:38 AM", 15, "#fffdf4", False)
    glass_card(bg, (1465, 182, 1588, 232), 8, c("#314932", 120), c("#fffdf4", 54))
    text(d, (1488, 194), "能量 120", 18, "#fff3bf", True)
    text(d, (1565, 188), "+", 32, "#fffdf4", True)

    # Overlay actions
    glass_card(bg, (690, 680, 1068, 788), 8, c("#fffdf4", 222), c("#d9dfd3"))
    actions = [("水", "Water"), ("息", "Breathe"), ("叶", "Nourish"), ("光", "Light")]
    for i, (zh, en) in enumerate(actions):
        cx = 742 + i * 92
        d.ellipse((cx - 28, 697, cx + 28, 753), fill=c("#f7f8f0"), outline=c("#dce3d8"))
        text(d, (cx, 711), zh, 20, "#6f8c63", True, anchor="ma")
        text(d, (cx, 762), en, 13, "#526651", anchor="ma")
    glass_card(bg, (1290, 710, 1600, 794), 8, c("#fffdf4", 222), c("#d9dfd3"))
    text(d, (1310, 728), "今日意图", 15, "#526651", True)
    text(d, (1310, 758), "我愿意温柔地开始。", 16, "#314932")
    icon_leaf(d, 1560, 752, 0.8, "#6f8c63")

    chips = [("clock", "5 分钟", "建议时长"), ("waves", "低刺激", "舒缓动效"), ("leaf", "花园照护", "创作主题")]
    for i, (ic, a, b) in enumerate(chips):
        x1 = 90 + i * 180
        glass_card(bg, (x1, 798, x1 + 154, 888), 8, c("#fffdf4", 226), c("#d9dfd3"))
        if ic == "clock":
            icon_clock(d, x1 + 38, 840, 0.75, "#6f8c63")
        elif ic == "waves":
            icon_waves(d, x1 + 38, 840, 0.65, "#6f8c63")
        else:
            icon_leaf(d, x1 + 38, 834, 0.65, "#6f8c63")
        text(d, (x1 + 76, 818), a, 19, "#314932", True)
        text(d, (x1 + 76, 850), b, 13, "#617363")
    return save(bg, "landscape-01-healing-game-cover.png")


def concept_02_product_shell() -> Path:
    bg = Image.new("RGBA", (W, H), "#fbfbf5")
    paper = cover(IMG / "light-bamboo-paper.png", (W, H), 0.5, 0.5)
    bg = Image.blend(bg, paper, 0.18)
    d = ImageDraw.Draw(bg)
    rounded(d, (28, 26, 1652, 918), 12, c("#fffdf8", 230), c("#d8d4c8"), 1)

    # Left sidebar
    icon_leaf(d, 74, 62, 1.05, "#6f8c63")
    text(d, (112, 46), "灵感世界", 28, "#173126", True)
    text(d, (112, 80), "环境疗愈生成程序", 15, "#5d645c")
    items = [("首页", True), ("我的花园", False), ("练习", False), ("记录", False), ("设置", False)]
    y = 150
    for label, active in items:
        rounded(d, (46, y, 294, y + 50), 8, c("#e9eee2") if active else None, None)
        text(d, (72, y + 14), "◆" if active else "◇", 15, "#3d6845")
        text(d, (110, y + 13), label, 17, "#173126", active)
        y += 64
    glass_card(bg, (46, 752, 294, 878), 8, c("#fffdf8", 224), c("#ded8cb"))
    text(d, (76, 776), "当前状态", 15, "#6f8c63", True)
    text(d, (76, 810), "平静 / 可继续", 19, "#173126", True)
    rounded(d, (76, 846, 246, 852), 3, c("#ddd8ca"), None)
    rounded(d, (76, 846, 172, 852), 3, c("#496c3f"), None)

    # Top metrics
    rounded(d, (330, 26, 1384, 102), 0, c("#fffdf8", 172), c("#e5ded2"))
    metrics = [("光", "今日光线", "柔和"), ("水", "水分", "80"), ("叶", "绿意", "12")]
    x = 382
    for ic, label, value in metrics:
        rounded(d, (x, 48, x + 126, 84), 8, c("#fffdf8", 230), c("#e5ded2"))
        text(d, (x + 18, 56), ic, 17, "#e8a423", True)
        text(d, (x + 48, 57), value, 16, "#173126", True)
        x += 150
    rounded(d, (1300, 50, 1340, 90), 8, c("#fffdf8", 230), c("#e5ded2"))
    rounded(d, (1356, 50, 1396, 90), 8, c("#fffdf8", 230), c("#e5ded2"))
    text(d, (1314, 58), "信", 16, "#173126", True)
    icon_gear(d, 1376, 70, 0.58, "#617363")

    # Main content
    text(d, (376, 150), "欢迎回来，Luna", 31, "#173126", True)
    icon_leaf(d, 620, 150, 0.6, "#6f8c63")
    text(d, (376, 190), "深呼吸。今天的花园可以从一个小动作开始。", 18, "#5d645c")

    hero = cover(IMG / "presets" / "community-flower-lane.png", (590, 300), 0.42, 0.45)
    hero = Image.blend(Image.new("RGBA", hero.size, "#fffdf4"), hero, 0.72)
    hero.alpha_composite(gradient(hero.size, [(0, c("#fffdf4", 30)), (1, c("#fffdf4", 155))]))
    bg.alpha_composite(hero, (792, 104))

    glass_card(bg, (370, 236, 932, 472), 8, c("#fffdf8", 232), c("#ded8cb"))
    icon_leaf(d, 430, 277, 0.55, "#6f8c63")
    text(d, (458, 266), "呼吸练习", 25, "#173126", True)
    text(d, (418, 314), "用 5 分钟把注意力从屏幕带回身体。", 17, "#5d645c")
    rounded(d, (418, 358, 488, 392), 8, c("#fffdf8"), c("#ded8cb"))
    text(d, (436, 366), "5 min", 14, "#314932")
    rounded(d, (500, 358, 584, 392), 8, c("#fffdf8"), c("#ded8cb"))
    text(d, (518, 366), "Focus", 14, "#314932")
    button(d, (418, 408, 914, 456), "开始练习", "#315d38", "#ffffff", icon=False)

    glass_card(bg, (950, 236, 1246, 472), 8, c("#fffdf8", 232), c("#ded8cb"))
    plant = cover(IMG / "presets" / "bamboo-courtyard.png", (84, 126), 0.32, 0.55)
    rounded(d, (982, 258, 1066, 386), 8, c("#eee6d8"), None)
    bg.alpha_composite(plant, (982, 258))
    text(d, (1090, 272), "我的花园", 24, "#173126", True)
    text(d, (1090, 320), "植物状态稳定，适合轻量维护。", 16, "#4f5f52")
    text(d, (1090, 362), "6 / 8 项良好", 15, "#173126")
    rounded(d, (1090, 392, 1210, 398), 3, c("#ded8cb"), None)
    rounded(d, (1090, 392, 1168, 398), 3, c("#496c3f"), None)
    rounded(d, (1090, 414, 1228, 450), 8, c("#fffdf8"), c("#ded8cb"))
    text(d, (1132, 422), "查看花园", 15, "#173126", True)

    glass_card(bg, (370, 492, 1004, 666), 8, c("#fffdf8", 232), c("#ded8cb"))
    text(d, (418, 526), "每日小任务", 22, "#173126", True)
    tasks = [("浇灌一盆植物", "+20"), ("完成一次呼吸练习", "+15"), ("记录今天的空间感受", "+10")]
    y = 566
    for i, (task, pts) in enumerate(tasks):
        d.ellipse((418, y, 436, y + 18), fill=c("#496c3f") if i < 2 else None, outline=c("#cfc9ba"))
        text(d, (454, y - 2), task, 16, "#314932")
        text(d, (920, y - 2), pts, 16, "#3d6845", True)
        icon_sun(d, 972, y + 8, 0.38, "#e8a423")
        y += 36
    text(d, (418, 638), "查看全部  →", 16, "#173126", True)

    glass_card(bg, (1022, 492, 1374, 666), 8, c("#fffdf8", 224), c("#ded8cb"))
    text(d, (1070, 526), "“", 46, "#8b9b7d", True)
    text(d, (1070, 572), "当你慢下来，花园也会亮起来。", 22, "#314932")
    icon_leaf(d, 1298, 566, 1.35, "#d7dfcf")

    # QA callouts from reference 3
    callouts = [("AA 对比度", "正文与图标满足可读性。", 1260, 116), ("44px 触控区", "主按钮和图标按钮易点击。", 1260, 284), ("清晰焦点态", "键盘导航有明确边界。", 1260, 450), ("低动效", "只保留必要的微动效。", 1260, 616)]
    for title, desc, x0, y0 in callouts:
        glass_card(bg, (1420, y0, 1638, y0 + 118), 8, c("#fffdf8", 232), c("#ded8cb"))
        d.ellipse((1440, y0 + 22, 1462, y0 + 44), fill=c("#496c3f"))
        text(d, (1476, y0 + 20), title, 18, "#314932", True)
        wrap(d, (1476, y0 + 52), desc, 15, "#4d554e", 136, 5)
        d.line((1418, y0 + 60, x0, y0 + 60), fill="#4fa3ff", width=2)
        d.ellipse((x0 - 5, y0 + 55, x0 + 5, y0 + 65), outline="#4fa3ff", width=2)

    rounded(d, (320, 894, 1604, 938), 8, c("#eef0e8", 222), None)
    icon_leaf(d, 366, 916, 0.42, "#526651")
    text(d, (390, 908), "统一 token    |    8px spacing    |    radius 8px    |    soft shadow 1    |    reduced motion", 16, "#526651")
    return save(bg, "landscape-02-product-shell-qa.png")


def concept_03_quiet_ritual() -> Path:
    bg = Image.new("RGBA", (W, H), "#fbfbf7")
    d = ImageDraw.Draw(bg)
    rounded(d, (24, 24, 1656, 921), 12, c("#fffefd"), c("#d7d9d2"), 1)
    d.ellipse((1190, 96, 1548, 454), fill=c("#d8ece1", 130))
    d.ellipse((1120, 560, 1390, 830), fill=c("#f0dfb8", 118))
    # Subtle line-art planter
    line = "#8a948b"
    rounded(d, (958, 390, 1460, 520), 0, None, line, 1)
    d.line((958, 452, 1460, 452), fill=line, width=1)
    for x in [1040, 1130, 1225, 1320]:
        d.line((x, 390, x + 20, 250), fill=line, width=1)
        d.line((x + 20, 250, x + 48, 220), fill=line, width=1)
        d.ellipse((x + 30, 205, x + 70, 235), outline=line, width=1)
        d.ellipse((x - 20, 280, x + 20, 310), outline=line, width=1)
    for x in range(910, 1510, 55):
        d.line((x, 540, x + 20, 540), fill="#c4c8c1", width=1)

    rounded(d, (64, 62, 120, 118), 28, None, c("#789178"), 2)
    icon_leaf(d, 92, 90, 0.65, "#789178")
    rounded(d, (1570, 62, 1620, 112), 8, None, c("#d0d3cc"), 1)
    icon_gear(d, 1595, 88, 0.65, "#68736a")

    text(d, (118, 260), "灵感世界", 72, "#101810", False)
    text(d, (120, 360), "A small ritual for softer spaces.", 26, "#616761")
    rounded(d, (118, 454, 430, 546), 8, None, c("#789178"), 2)
    icon_leaf(d, 202, 500, 0.75, "#789178")
    text(d, (256, 484), "Begin", 28, "#789178")
    text(d, (118, 606), "Rituals", 24, "#101810")
    d.line((118, 636, 184, 636), fill="#101810", width=1)

    for i, (ic, label) in enumerate([("clock", "5 min"), ("waves", "Low motion"), ("leaf", "Garden log")]):
        x = 118 + i * 214
        if ic == "clock":
            icon_clock(d, x + 12, 790, 0.68, "#666b66")
        elif ic == "waves":
            icon_waves(d, x + 12, 790, 0.58, "#666b66")
        else:
            icon_leaf(d, x + 12, 784, 0.56, "#666b66")
        text(d, (x + 50, 772), label, 21, "#6b706b")
        if i < 2:
            d.line((x + 138, 746, x + 138, 798), fill="#caccc6", width=1)

    d.ellipse((1090, 578, 1292, 780), outline=c("#789178"), width=2)
    d.ellipse((1182, 572, 1206, 596), fill=c("#789178"))
    text(d, (1191, 672), "Breathe in", 21, "#789178", anchor="ma")
    text(d, (1191, 716), "4  • • •", 18, "#789178", anchor="ma")

    glass_card(bg, (1368, 742, 1588, 846), 8, c("#fffdf8", 220), c("#d8d4c8"))
    text(d, (1400, 764), "安静模式", 18, "#314932", True)
    text(d, (1400, 796), "无滚动动效 / 低刺激", 16, "#6b706b")
    rounded(d, (1510, 792, 1566, 824), 16, c("#e6e8e0"), None)
    d.ellipse((1532, 796, 1560, 824), fill=c("#789178"))
    return save(bg, "landscape-03-quiet-ritual-minimal.png")


def main() -> None:
    paths = [
        concept_01_game_garden(),
        concept_02_product_shell(),
        concept_03_quiet_ritual(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
