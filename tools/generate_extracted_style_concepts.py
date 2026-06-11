from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design_references"
W, H = 1680, 945


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for item in candidates:
        path = Path(item)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = value.strip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def vertical_gradient(top: str, bottom: str, size=(W, H)) -> Image.Image:
    a = hex_rgba(top)
    b = hex_rgba(bottom)
    out = Image.new("RGBA", size)
    px = out.load()
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        color = tuple(lerp(a[i], b[i], t) for i in range(4))
        for x in range(size[0]):
            px[x, y] = color
    return out


def draw_text(draw: ImageDraw.ImageDraw, xy, text: str, size: int, color: str, bold: bool = False, anchor=None):
    draw.text(xy, text, font=font(size, bold), fill=color, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box, radius=12, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def leaf_icon(draw: ImageDraw.ImageDraw, cx, cy, scale=1.0, fill="#6e8a63"):
    r = int(10 * scale)
    draw.ellipse((cx - r * 2, cy - r, cx, cy + r), fill=fill)
    draw.ellipse((cx, cy - r, cx + r * 2, cy + r), fill=fill)
    draw.line((cx, cy + r * 2, cx, cy - r), fill=fill, width=max(1, int(2.6 * scale)))


def sun_icon(draw, cx, cy, scale=1.0, fill="#f4bd42"):
    r = int(8 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    for i in range(8):
        a = math.pi * 2 * i / 8
        x1 = cx + math.cos(a) * r * 1.6
        y1 = cy + math.sin(a) * r * 1.6
        x2 = cx + math.cos(a) * r * 2.4
        y2 = cy + math.sin(a) * r * 2.4
        draw.line((x1, y1, x2, y2), fill=fill, width=max(1, int(2 * scale)))


def waves_icon(draw, cx, cy, scale=1.0, fill="#6e8a63"):
    for i in range(3):
        y = cy - 12 * scale + i * 12 * scale
        draw.arc((cx - 28 * scale, y - 8 * scale, cx, y + 8 * scale), 200, 340, fill=fill, width=max(1, int(2 * scale)))
        draw.arc((cx - 2 * scale, y - 8 * scale, cx + 26 * scale, y + 8 * scale), 200, 340, fill=fill, width=max(1, int(2 * scale)))


def gear_icon(draw, cx, cy, scale=1.0, fill="#617363"):
    r = int(12 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=max(1, int(2 * scale)))
    draw.ellipse((cx - 4 * scale, cy - 4 * scale, cx + 4 * scale, cy + 4 * scale), fill=fill)
    for i in range(8):
        a = math.pi * 2 * i / 8
        draw.line(
            (
                cx + math.cos(a) * r * 1.15,
                cy + math.sin(a) * r * 1.15,
                cx + math.cos(a) * r * 1.55,
                cy + math.sin(a) * r * 1.55,
            ),
            fill=fill,
            width=max(1, int(2 * scale)),
        )


def blur_shadow(base: Image.Image, box, radius=18, alpha=30, blur=18):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rounded(d, box, radius, hex_rgba("#2e402e", alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def glass(base: Image.Image, box, radius=12, fill="#fffdf4", alpha=218, border="#ded8cb"):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rounded(d, box, radius, hex_rgba(fill, alpha), hex_rgba(border, 210), 1)
    base.alpha_composite(layer)


def button(draw, box, label, bg="#f5bd40", fg="#314932", secondary=False):
    if secondary:
        rounded(draw, box, 12, hex_rgba("#fffdf4", 218), hex_rgba("#dacdb6", 225), 1)
    else:
        rounded(draw, box, 12, bg, "#d9a12b", 1)
    x1, y1, x2, y2 = box
    leaf_icon(draw, x1 + 82, (y1 + y2) // 2, 0.78, fg if not secondary else "#6e8a63")
    draw_text(draw, (x1 + 122, y1 + 24), label, 23, fg if not secondary else "#6d7e68", True)
    if not secondary:
        draw.line((x2 - 55, (y1 + y2) // 2, x2 - 30, (y1 + y2) // 2), fill=fg, width=3)
        draw.line((x2 - 42, (y1 + y2) // 2 - 10, x2 - 30, (y1 + y2) // 2), fill=fg, width=3)
        draw.line((x2 - 42, (y1 + y2) // 2 + 10, x2 - 30, (y1 + y2) // 2), fill=fg, width=3)


def background_world(seed=1, warm=True) -> Image.Image:
    random.seed(seed)
    img = vertical_gradient("#eaf7fb" if warm else "#eaf6ee", "#f9f4df", (W, H))
    d = ImageDraw.Draw(img)

    # Sun and distant glow.
    for r, a in [(260, 28), (180, 34), (110, 44)]:
        d.ellipse((45 - r, 185 - r, 45 + r, 185 + r), fill=hex_rgba("#fff4c8", a))

    # Distant rolling hills.
    hill_colors = ["#dcebcf", "#cbdcbc", "#b9d2ab"]
    for idx, color in enumerate(hill_colors):
        y0 = 360 + idx * 58
        pts = [(0, H)]
        for x in range(-40, W + 80, 80):
            y = y0 + math.sin((x + seed * 83) / 170) * (22 + idx * 8) + random.randint(-6, 6)
            pts.append((x, y))
        pts.extend([(W, H), (0, H)])
        d.polygon(pts, fill=hex_rgba(color, 170 - idx * 25))

    # Foreground meadow.
    d.polygon([(0, 650), (W, 610), (W, H), (0, H)], fill=hex_rgba("#c5d7ad", 176))
    d.polygon([(0, 735), (W, 705), (W, H), (0, H)], fill=hex_rgba("#aabf91", 150))

    # Soft wildflowers in foreground.
    for _ in range(140):
        x = random.randint(0, W)
        y = random.randint(700, 930)
        stem = random.randint(8, 22)
        d.line((x, y, x + random.randint(-3, 3), y - stem), fill=hex_rgba("#718c60", 95), width=1)
        petal = random.choice(["#fff7e6", "#f3d2db", "#f6e0a1"])
        d.ellipse((x - 3, y - stem - 3, x + 3, y - stem + 3), fill=hex_rgba(petal, 125))
    return img.filter(ImageFilter.GaussianBlur(0.2))


def draw_cottage_scene(size=(930, 600), seed=1, variant="cottage") -> Image.Image:
    random.seed(seed)
    w, h = size
    img = vertical_gradient("#dceef2", "#e8d9ab", size)
    d = ImageDraw.Draw(img)

    # Distant valley.
    for idx, color in enumerate(["#c8ddb4", "#afcb9b", "#8fb17a"]):
        base = 210 + idx * 55
        pts = [(0, h)]
        for x in range(-30, w + 80, 70):
            y = base + math.sin((x + idx * 87) / 140) * (22 + idx * 6)
            pts.append((x, y))
        pts += [(w, h), (0, h)]
        d.polygon(pts, fill=hex_rgba(color, 175 - idx * 26))

    # Waterfall / light column.
    if variant != "courtyard":
        d.rounded_rectangle((170, 155, 220, 340), radius=22, fill=hex_rgba("#eaf7f5", 120))
        d.line((195, 160, 174, 340), fill=hex_rgba("#fffdf4", 100), width=2)
        d.line((208, 165, 226, 345), fill=hex_rgba("#b9d8d5", 90), width=3)

    # Cottage / garden studio.
    if variant == "cottage":
        d.polygon([(545, 170), (825, 180), (890, 290), (512, 280)], fill=hex_rgba("#7c6b45", 230))
        rounded(d, (570, 255, 875, 492), 18, hex_rgba("#dacb9e", 238), hex_rgba("#8c7a52", 180), 2)
        rounded(d, (686, 312, 770, 462), 42, hex_rgba("#5f8a58", 245), hex_rgba("#385b36", 210), 3)
        d.ellipse((744, 386, 758, 400), fill=hex_rgba("#d0a642", 255))
        for x in [595, 814]:
            rounded(d, (x, 315, x + 60, 390), 10, hex_rgba("#fff8d6", 105), hex_rgba("#7f8d63", 130), 1)
        for x in [610, 830]:
            d.ellipse((x - 18, 248, x + 18, 285), fill=hex_rgba("#6b8d50", 205))
    elif variant == "gate":
        rounded(d, (565, 235, 860, 510), 22, hex_rgba("#e6d8af", 235), hex_rgba("#a58d60", 170), 2)
        rounded(d, (610, 280, 815, 500), 98, hex_rgba("#5e8c5b", 248), hex_rgba("#3e6540", 210), 4)
        d.polygon([(540, 235), (710, 125), (888, 235)], fill=hex_rgba("#806d48", 240))
    else:
        rounded(d, (540, 220, 850, 494), 18, hex_rgba("#e4d6aa", 230), hex_rgba("#9e8a5d", 160), 2)
        rounded(d, (615, 270, 770, 440), 70, hex_rgba("#5f8a58", 245), hex_rgba("#385b36", 210), 3)

    # Garden bed and path.
    d.ellipse((300, 415, 630, 560), fill=hex_rgba("#8d866b", 230), outline=hex_rgba("#d7c899", 220), width=18)
    d.ellipse((358, 444, 572, 530), fill=hex_rgba("#6d5736", 240))
    for i, (x, y) in enumerate([(250, 560), (215, 515), (185, 475), (150, 440)]):
        d.ellipse((x, y, x + 70, y + 28), fill=hex_rgba("#d4cdb7", 210), outline=hex_rgba("#9c9b88", 120))

    # Central glowing sprout.
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((424, 340, 516, 432), fill=hex_rgba("#f4ff9a", 92))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.line((470, 458, 470, 390), fill=hex_rgba("#7ca14f", 255), width=8)
    d.ellipse((428, 374, 470, 404), fill=hex_rgba("#cfe96b", 255), outline=hex_rgba("#fff8a9", 220), width=2)
    d.ellipse((470, 374, 512, 404), fill=hex_rgba("#cfe96b", 255), outline=hex_rgba("#fff8a9", 220), width=2)

    # Cute floating leaf companions.
    for x, y, s in [(440, 265, 1.0), (510, 325, 0.68), (370, 338, 0.58)]:
        d.ellipse((x - 28 * s, y - 20 * s, x + 28 * s, y + 34 * s), fill=hex_rgba("#fff7cf", 235), outline=hex_rgba("#e0e8a4", 220), width=max(1, int(2 * s)))
        leaf_icon(d, x, y - 24 * s, 0.72 * s, "#cce86d")
        d.ellipse((x - 9 * s, y + 2 * s, x - 4 * s, y + 7 * s), fill=hex_rgba("#6d7e58"))
        d.ellipse((x + 5 * s, y + 2 * s, x + 10 * s, y + 7 * s), fill=hex_rgba("#6d7e58"))
        d.arc((x - 9 * s, y + 8 * s, x + 9 * s, y + 20 * s), 10, 170, fill=hex_rgba("#8b8c66"), width=max(1, int(2 * s)))

    # Flowers, lights, watering can.
    for _ in range(90):
        x = random.randint(40, w - 40)
        y = random.randint(410, h - 28)
        col = random.choice(["#fff7e8", "#efe5a7", "#d5b0d7", "#f4cfd3"])
        d.line((x, y, x, y - random.randint(10, 26)), fill=hex_rgba("#6f895b", 160), width=1)
        d.ellipse((x - 4, y - 25, x + 4, y - 17), fill=hex_rgba(col, 210))
    for _ in range(28):
        x = random.randint(30, w - 30)
        y = random.randint(165, 520)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=hex_rgba("#fff3a8", 210))
    rounded(d, (790, 455, 850, 505), 18, hex_rgba("#b99a62", 230), hex_rgba("#7e714f", 200), 2)
    d.arc((830, 430, 900, 500), 180, 320, fill=hex_rgba("#7e714f", 210), width=4)
    d.line((784, 466, 742, 446), fill=hex_rgba("#7e714f", 210), width=4)

    # Soft vignette and haze.
    haze = Image.new("RGBA", size, hex_rgba("#fff7dc", 28))
    img.alpha_composite(haze)
    return img


def top_nav(draw):
    rounded(draw, (0, 0, W, 112), 0, hex_rgba("#fffdf4", 235), hex_rgba("#dbe1d5"))
    leaf_icon(draw, 64, 56, 1.15, "#6f8c63")
    draw_text(draw, (108, 38), "灵感世界", 32, "#315d38", True)
    nav = ["首页", "花园", "练习", "记录", "关于"]
    x = 575
    for i, item in enumerate(nav):
        if i == 0:
            rounded(draw, (x - 24, 36, x + 62, 82), 10, hex_rgba("#e8eee4"))
        draw_text(draw, (x, 51), item, 17, "#314932", i == 0)
        x += 112
    rounded(draw, (1284, 30, 1558, 90), 12, hex_rgba("#fffdf4", 218), hex_rgba("#dbe1d5"))
    leaf_icon(draw, 1318, 58, 0.48, "#9bb08d")
    draw_text(draw, (1352, 45), "Level 3", 17, "#617363", True)
    rounded(draw, (1352, 68, 1470, 74), 3, hex_rgba("#dce3d8"))
    rounded(draw, (1352, 68, 1426, 74), 3, hex_rgba("#6f8c63"))
    rounded(draw, (1586, 30, 1642, 90), 12, hex_rgba("#fffdf4", 218), hex_rgba("#dbe1d5"))
    gear_icon(draw, 1614, 60, 0.72, "#617363")


def concept_one() -> Path:
    img = background_world(seed=11)
    d = ImageDraw.Draw(img)
    top_nav(d)

    # Large right game world preview.
    scene = draw_cottage_scene((960, 650), seed=7, variant="cottage")
    blur_shadow(img, (660, 158, 1620, 815), 18, 42, 26)
    img.alpha_composite(scene, (660, 158))
    rounded(d, (660, 158, 1620, 815), 18, None, hex_rgba("#fffdf4", 226), 2)

    glass(img, (700, 182, 816, 242), 12, "#405c46", 128, "#fffdf4")
    sun_icon(d, 730, 212, 0.88, "#ffd45a")
    draw_text(d, (764, 195), "晨间", 15, "#fffdf4", True)
    draw_text(d, (764, 217), "7:38 AM", 15, "#fffdf4")
    glass(img, (1460, 182, 1588, 232), 12, "#405c46", 122, "#fffdf4")
    draw_text(d, (1482, 196), "能量 120", 17, "#fff3bf", True)
    draw_text(d, (1566, 188), "+", 32, "#fffdf4", True)

    glass(img, (694, 680, 1068, 790), 14, "#fffdf4", 224)
    actions = [("水", "Water"), ("息", "Breathe"), ("叶", "Nourish"), ("净", "Cleanse")]
    for i, (a, b) in enumerate(actions):
        cx = 744 + i * 92
        d.ellipse((cx - 29, 697, cx + 29, 755), fill=hex_rgba("#f8f8f0"), outline=hex_rgba("#dbe1d5"))
        draw_text(d, (cx, 713), a, 20, "#6f8c63", True, "ma")
        draw_text(d, (cx, 766), b, 13, "#526651", False, "ma")

    glass(img, (1290, 710, 1600, 794), 14, "#fffdf4", 224)
    draw_text(d, (1312, 728), "今日意图", 15, "#526651", True)
    draw_text(d, (1312, 758), "我愿意温柔地开始。", 16, "#314932")
    leaf_icon(d, 1560, 752, 0.8, "#6f8c63")

    # Left copy.
    draw_text(d, (98, 248), "灵感世界", 78, "#315d38", True)
    leaf_icon(d, 540, 248, 0.88, "#7c9a6b")
    draw_text(d, (100, 358), "一个温和的世界，陪你慢下来。", 27, "#60745f")
    draw_text(d, (100, 416), "种下光、植物与呼吸。", 22, "#647464")
    draw_text(d, (100, 450), "一点一点，让平静成为习惯。", 22, "#647464")
    button(d, (98, 505, 532, 582), "开始一次平静创作")
    button(d, (98, 602, 460, 666), "查看练习", secondary=True)

    chips = [("clock", "5 分钟", "建议时长"), ("waves", "呼吸", "专注主题"), ("leaf", "花园照护", "创作活动")]
    for i, (kind, title, desc) in enumerate(chips):
        x = 90 + i * 180
        glass(img, (x, 798, x + 154, 888), 14, "#fffdf4", 226)
        if kind == "clock":
            d.ellipse((x + 20, 815, x + 72, 867), fill=hex_rgba("#fbfbf4"), outline=hex_rgba("#dbe1d5"))
            draw_clock = ImageDraw.Draw(img)
            draw_clock.ellipse((x + 32, 827, x + 60, 855), outline="#6f8c63", width=2)
            draw_clock.line((x + 46, 841, x + 46, 830), fill="#6f8c63", width=2)
            draw_clock.line((x + 46, 841, x + 54, 846), fill="#6f8c63", width=2)
        elif kind == "waves":
            waves_icon(d, x + 46, 840, 0.6, "#6f8c63")
        else:
            leaf_icon(d, x + 46, 834, 0.62, "#6f8c63")
        draw_text(d, (x + 78, 818), title, 18, "#314932", True)
        draw_text(d, (x + 78, 850), desc, 13, "#617363")
    return save(img, "extracted-01-warm-game-garden.png")


def concept_two() -> Path:
    img = background_world(seed=24, warm=True)
    d = ImageDraw.Draw(img)
    top_nav(d)

    # Wider, more fantasy-forward main scene.
    scene = draw_cottage_scene((1040, 660), seed=23, variant="gate")
    scene = scene.filter(ImageFilter.GaussianBlur(0.15))
    blur_shadow(img, (580, 148, 1620, 824), 22, 42, 28)
    img.alpha_composite(scene, (580, 148))
    rounded(d, (580, 148, 1620, 824), 22, None, hex_rgba("#fffdf4", 230), 2)

    # Focus on a world-entry feel.
    glass(img, (616, 184, 782, 246), 14, "#405c46", 126, "#fffdf4")
    sun_icon(d, 648, 214, 0.8, "#ffd45a")
    draw_text(d, (682, 194), "山谷晨光", 15, "#fffdf4", True)
    draw_text(d, (682, 216), "适合低刺激", 14, "#fffdf4")
    glass(img, (1310, 690, 1580, 784), 14, "#fffdf4", 224)
    draw_text(d, (1332, 710), "本次目标", 15, "#526651", True)
    draw_text(d, (1332, 742), "把空间改造成更可待的地方。", 16, "#314932")
    leaf_icon(d, 1540, 740, 0.8, "#6f8c63")

    # Left text shifted slightly upward for openness.
    draw_text(d, (92, 226), "进入一个", 48, "#315d38", True)
    draw_text(d, (92, 288), "会慢慢变好的空间", 62, "#315d38", True)
    draw_text(d, (94, 380), "用游戏一样轻的方式，完成一次环境疗愈创作。", 25, "#60745f")
    draw_text(d, (94, 430), "从一株发光的新芽开始。", 22, "#647464")
    button(d, (94, 492, 518, 568), "开始体验")
    button(d, (94, 588, 430, 650), "查看练习", secondary=True)

    # Calm status cards.
    for i, (label, value) in enumerate([("环境", "柔和"), ("动效", "轻"), ("时长", "5 min")]):
        x = 94 + i * 150
        glass(img, (x, 760, x + 132, 844), 14, "#fffdf4", 224)
        draw_text(d, (x + 20, 782), label, 13, "#6f8c63", True)
        draw_text(d, (x + 20, 810), value, 21, "#314932", True)
    return save(img, "extracted-02-valley-world-entry.png")


def concept_three() -> Path:
    img = vertical_gradient("#fffef9", "#f3f4ec")
    d = ImageDraw.Draw(img)
    rounded(d, (28, 26, 1652, 918), 16, hex_rgba("#fffdf8", 238), hex_rgba("#d8d4c8"))

    # Shell nav.
    rounded(d, (28, 26, 328, 918), 16, hex_rgba("#fbfaf3", 235), hex_rgba("#d8d4c8"))
    leaf_icon(d, 76, 66, 1.0, "#6f8c63")
    draw_text(d, (112, 48), "灵感世界", 28, "#173126", True)
    draw_text(d, (112, 82), "环境疗愈生成程序", 15, "#5d645c")
    for i, label in enumerate(["首页", "我的花园", "练习", "记录", "设置"]):
        y = 150 + i * 64
        rounded(d, (48, y, 296, y + 50), 10, hex_rgba("#e9eee2") if i == 0 else None)
        if i == 0:
            leaf_icon(d, 82, y + 24, 0.45, "#3d6845")
        else:
            d.ellipse((78, y + 22, 84, y + 28), outline="#789178", width=1)
        draw_text(d, (112, y + 13), label, 17, "#173126", i == 0)
    glass(img, (48, 742, 296, 878), 12, "#fffdf8", 226)
    draw_text(d, (76, 770), "今日状态", 15, "#6f8c63", True)
    draw_text(d, (76, 810), "平静 / 可继续", 22, "#173126", True)
    rounded(d, (76, 850, 246, 856), 3, hex_rgba("#ddd8ca"))
    rounded(d, (76, 850, 174, 856), 3, hex_rgba("#496c3f"))

    # Header metrics.
    rounded(d, (328, 26, 1388, 102), 0, hex_rgba("#fffdf8", 180), hex_rgba("#e5ded2"))
    for i, (label, value) in enumerate([("光线", "柔和"), ("水分", "80"), ("绿意", "12")]):
        x = 382 + i * 150
        rounded(d, (x, 48, x + 126, 84), 10, hex_rgba("#fffdf8", 232), hex_rgba("#e5ded2"))
        draw_text(d, (x + 18, 57), label, 14, "#e8a423", True)
        draw_text(d, (x + 70, 57), value, 15, "#173126", True)
    rounded(d, (1300, 50, 1340, 90), 10, hex_rgba("#fffdf8", 232), hex_rgba("#e5ded2"))
    gear_icon(d, 1376, 70, 0.56, "#617363")

    # Main content and illustrated scene.
    draw_text(d, (376, 150), "欢迎回来，Luna", 31, "#173126", True)
    leaf_icon(d, 620, 152, 0.58, "#6f8c63")
    draw_text(d, (376, 190), "今天从一个温和的小动作开始。", 18, "#5d645c")
    scene = draw_cottage_scene((590, 300), seed=45, variant="courtyard")
    scene = Image.blend(Image.new("RGBA", scene.size, "#fffdf4"), scene, 0.82)
    img.alpha_composite(scene, (792, 104))

    glass(img, (370, 236, 932, 472), 12, "#fffdf8", 232)
    leaf_icon(d, 432, 278, 0.55, "#6f8c63")
    draw_text(d, (462, 266), "呼吸练习", 26, "#173126", True)
    draw_text(d, (418, 314), "用 5 分钟把注意力从屏幕带回身体。", 17, "#5d645c")
    rounded(d, (418, 358, 488, 392), 10, hex_rgba("#fffdf8"), hex_rgba("#ded8cb"))
    draw_text(d, (436, 366), "5 min", 14, "#314932")
    rounded(d, (500, 358, 584, 392), 10, hex_rgba("#fffdf8"), hex_rgba("#ded8cb"))
    draw_text(d, (518, 366), "Focus", 14, "#314932")
    rounded(d, (418, 408, 914, 456), 10, "#315d38")
    draw_text(d, (588, 420), "开始练习", 21, "#ffffff", True)
    d.line((852, 432, 880, 432), fill="#ffffff", width=3)
    d.line((868, 420, 880, 432), fill="#ffffff", width=3)
    d.line((868, 444, 880, 432), fill="#ffffff", width=3)

    glass(img, (950, 236, 1246, 472), 12, "#fffdf8", 232)
    rounded(d, (982, 258, 1066, 386), 12, hex_rgba("#eee6d8"))
    mini = draw_cottage_scene((84, 128), seed=10, variant="cottage")
    img.alpha_composite(mini, (982, 258))
    draw_text(d, (1090, 272), "我的花园", 24, "#173126", True)
    draw_text(d, (1090, 320), "植物状态稳定，适合轻量维护。", 16, "#4f5f52")
    draw_text(d, (1090, 362), "6 / 8 项良好", 15, "#173126")
    rounded(d, (1090, 392, 1210, 398), 3, hex_rgba("#ded8cb"))
    rounded(d, (1090, 392, 1168, 398), 3, hex_rgba("#496c3f"))
    rounded(d, (1090, 414, 1228, 450), 10, hex_rgba("#fffdf8"), hex_rgba("#ded8cb"))
    draw_text(d, (1132, 423), "查看花园", 15, "#173126", True)

    glass(img, (370, 492, 1004, 666), 12, "#fffdf8", 232)
    draw_text(d, (418, 526), "每日小任务", 22, "#173126", True)
    tasks = [("浇灌一盆植物", "+20"), ("完成一次呼吸练习", "+15"), ("记录今天的空间感受", "+10")]
    for i, (task, pts) in enumerate(tasks):
        y = 566 + i * 36
        d.ellipse((418, y, 436, y + 18), fill=hex_rgba("#496c3f") if i < 2 else None, outline=hex_rgba("#cfc9ba"))
        draw_text(d, (454, y - 2), task, 16, "#314932")
        draw_text(d, (920, y - 2), pts, 16, "#3d6845", True)
        sun_icon(d, 972, y + 9, 0.36, "#e8a423")
    draw_text(d, (418, 638), "查看全部  →", 16, "#173126", True)

    glass(img, (1022, 492, 1374, 666), 12, "#fffdf8", 224)
    draw_text(d, (1070, 526), "“", 46, "#8b9b7d", True)
    draw_text(d, (1070, 572), "当你慢下来，花园也会亮起来。", 22, "#314932")
    leaf_icon(d, 1308, 572, 1.35, "#d7dfcf")

    # QA callouts.
    for i, (title, desc) in enumerate([
        ("AA 对比度", "正文与图标满足可读性。"),
        ("44px 触控区", "主按钮和图标按钮容易点击。"),
        ("清晰焦点态", "键盘导航有明确边界。"),
        ("低动效", "只保留必要的微动效。"),
    ]):
        y = 118 + i * 166
        glass(img, (1420, y, 1638, y + 118), 12, "#fffdf8", 232)
        d.ellipse((1440, y + 24, 1462, y + 46), fill=hex_rgba("#496c3f"))
        draw_text(d, (1476, y + 22), title, 18, "#314932", True)
        draw_text(d, (1476, y + 56), desc, 15, "#4d554e")

    rounded(d, (320, 894, 1604, 938), 10, hex_rgba("#eef0e8", 230))
    leaf_icon(d, 366, 916, 0.42, "#526651")
    draw_text(d, (390, 908), "统一 token  |  8px spacing  |  radius 8px  |  soft shadow 1  |  reduced motion", 16, "#526651")
    return save(img, "extracted-03-game-ui-system.png")


def save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    img.convert("RGB").save(path, quality=96)
    return path


def main():
    for path in [concept_one(), concept_two(), concept_three()]:
        print(path)


if __name__ == "__main__":
    main()
