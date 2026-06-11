from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design_references"
IMAGES = ROOT / "app" / "static" / "images"
W, H = 430, 932
SCALE = 2


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/msyhbd.ttc") if weight == "bold" else Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for item in candidates:
        if item.exists():
            return ImageFont.truetype(str(item), size * SCALE)
    return ImageFont.load_default()


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def cover_image(path: Path, size: tuple[int, int] = (W * SCALE, H * SCALE), focus_y: float = 0.5) -> Image.Image:
    img = Image.open(path).convert("RGB")
    sw, sh = size
    iw, ih = img.size
    scale = max(sw / iw, sh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, (nw - sw) // 2)
    y = max(0, min(nh - sh, int((nh - sh) * focus_y)))
    return img.crop((x, y, x + sw, y + sh)).convert("RGBA")


def gradient(size: tuple[int, int], stops: list[tuple[float, tuple[int, int, int, int]]]) -> Image.Image:
    w, h = size
    out = Image.new("RGBA", size)
    px = out.load()
    for y in range(h):
        t = y / max(1, h - 1)
        lo = stops[0]
        hi = stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = max(0.0001, hi[0] - lo[0])
        local = (t - lo[0]) / span
        color = tuple(int(lo[1][c] + (hi[1][c] - lo[1][c]) * local) for c in range(4))
        for x in range(w):
            px[x, y] = color
    return out


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill, width: int, line_gap: int = 8) -> int:
    x, y = xy
    line = ""
    for ch in text:
        test = line + ch
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width or not line:
            line = test
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
            y += fnt.size + line_gap * SCALE
            line = ch
    if line:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap * SCALE
    return y


def pill(draw, xy, text, bg, fg):
    x, y = xy
    fnt = font(11, "bold")
    box = draw.textbbox((0, 0), text, font=fnt)
    pad_x, pad_y = 12 * SCALE, 7 * SCALE
    w = box[2] + pad_x * 2
    h = box[3] - box[1] + pad_y * 2
    draw.rounded_rectangle((x, y, x + w, y + h), radius=999, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1 * SCALE), text, font=fnt, fill=fg)


def button(draw, xy, w, label, bg, fg, border=None):
    x, y = xy
    h = 54 * SCALE
    draw.rounded_rectangle((x, y, x + w, y + h), radius=27 * SCALE, fill=bg, outline=border, width=1 * SCALE if border else 0)
    fnt = font(15, "bold")
    box = draw.textbbox((0, 0), label, font=fnt)
    draw.text((x + (w - box[2]) / 2, y + (h - (box[3] - box[1])) / 2 - 2 * SCALE), label, font=fnt, fill=fg)


def panel(draw, xy, wh, fill, outline):
    x, y = xy
    w, h = wh
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8 * SCALE, fill=fill, outline=outline, width=SCALE)


def common_text(draw, title_color, sub_color, y0=86):
    x = 28 * SCALE
    draw.text((x, y0 * SCALE), "INSPIRATION WORLD", font=font(11, "bold"), fill=sub_color)
    y = y0 * SCALE + 42 * SCALE
    draw.text((x, y), "\u7075\u611f\u4e16\u754c", font=font(42, "bold"), fill=title_color)
    draw.text((x, y + 58 * SCALE), "Inspiration World", font=font(13, "bold"), fill=sub_color)


def save(img: Image.Image, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.resize((W, H), Image.Resampling.LANCZOS).save(path)
    return path


def concept_bamboo():
    img = cover_image(IMAGES / "presets" / "bamboo-courtyard.png", focus_y=0.52)
    img = Image.blend(Image.new("RGBA", img.size, "#f8fbf1"), img, 0.76)
    img.alpha_composite(gradient(img.size, [(0, rgba("#fffdf4", 92)), (0.44, rgba("#fffdf4", 28)), (1, rgba("#eff6e8", 235))]))
    draw = ImageDraw.Draw(img)
    common_text(draw, rgba("#173126"), rgba("#315e46", 180))
    panel(draw, (24 * SCALE, 710 * SCALE), (382 * SCALE, 144 * SCALE), rgba("#fffdf4", 224), rgba("#264634", 34))
    draw.text((42 * SCALE, 730 * SCALE), "\u4eca\u5929\u5148\u8ba9\u547c\u5438\u6162\u4e0b\u6765", font=font(14, "bold"), fill=rgba("#173126"))
    draw.text((42 * SCALE, 758 * SCALE), "\u4ece\u4e00\u4e2a\u6e29\u548c\u7684\u573a\u666f\u5f00\u59cb", font=font(12), fill=rgba("#173126", 150))
    button(draw, (42 * SCALE, 790 * SCALE), 346 * SCALE, "\u5f00\u59cb\u4f53\u9a8c", rgba("#2f7b58"), rgba("#ffffff"))
    return save(img, "concept-01-morning-bamboo.png")


def concept_lake():
    img = cover_image(IMAGES / "presets" / "lakeside-deck.png", focus_y=0.50)
    img = Image.blend(Image.new("RGBA", img.size, "#fff8e8"), img, 0.82)
    img.alpha_composite(gradient(img.size, [(0, rgba("#fffaf0", 82)), (0.42, rgba("#ffffff", 0)), (1, rgba("#f7f1df", 230))]))
    draw = ImageDraw.Draw(img)
    common_text(draw, rgba("#243528"), rgba("#485c4c", 175), y0=74)
    pill(draw, (28 * SCALE, 310 * SCALE), "\u6e56\u9762\u00b7\u6696\u5149\u00b7\u7f13\u6162\u8fdb\u5165", rgba("#fffdf4", 205), rgba("#315e46"))
    button(draw, (28 * SCALE, 810 * SCALE), 374 * SCALE, "\u5f00\u59cb\u4f53\u9a8c", rgba("#315e46"), rgba("#ffffff"))
    draw.text((28 * SCALE, 878 * SCALE), "\u4e00\u6b21\u8f7b\u91cf\u3001\u4e0d\u538b\u8feb\u7684\u73af\u5883\u521b\u4f5c\u5165\u53e3", font=font(11), fill=rgba("#243528", 150))
    return save(img, "concept-02-lakeside-breath.png")


def concept_garden():
    img = cover_image(IMAGES / "presets" / "pocket-garden.png", focus_y=0.50)
    img = Image.blend(Image.new("RGBA", img.size, "#f6faf4"), img, 0.68)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7 * SCALE))
    img.alpha_composite(gradient(img.size, [(0, rgba("#eef7f1", 112)), (0.55, rgba("#eef7f1", 24)), (1, rgba("#f8fbf4", 245))]))
    draw = ImageDraw.Draw(img)
    common_text(draw, rgba("#133a2a"), rgba("#3f7159", 180), y0=88)
    panel(draw, (26 * SCALE, 642 * SCALE), (378 * SCALE, 218 * SCALE), rgba("#fffff8", 218), rgba("#264634", 30))
    draw.text((44 * SCALE, 666 * SCALE), "\u9009\u4e00\u4e2a\u7a7a\u95f4\uff0c\u628a\u5b83\u53d8\u5f97\u66f4\u53ef\u5f85", font=font(14, "bold"), fill=rgba("#173126"))
    y = draw_wrapped(draw, (44 * SCALE, 702 * SCALE), "\u7528\u66f4\u660e\u4eae\u7684\u57ce\u5e02\u82b1\u56ed\u4f5c\u4e3a\u9996\u5c4f\uff0c\u51cf\u5c11\u9ed1\u8272\u906e\u7f69\uff0c\u4fdd\u7559\u6c89\u9759\u7684\u4e13\u6ce8\u611f\u3002", font(12), rgba("#173126", 155), 326 * SCALE, 6)
    button(draw, (44 * SCALE, max(y + 18 * SCALE, 786 * SCALE)), 342 * SCALE, "\u5f00\u59cb\u4f53\u9a8c", rgba("#3b8a66"), rgba("#ffffff"))
    return save(img, "concept-03-soft-garden.png")


def concept_paper():
    base = cover_image(IMAGES / "light-bamboo-paper.png", focus_y=0.5)
    base = Image.blend(Image.new("RGBA", base.size, "#fafcf6"), base, 0.38)
    draw = ImageDraw.Draw(base)
    draw.ellipse((260 * SCALE, 72 * SCALE, 520 * SCALE, 332 * SCALE), fill=rgba("#dcefe4", 115))
    draw.ellipse((-80 * SCALE, 560 * SCALE, 210 * SCALE, 850 * SCALE), fill=rgba("#f0dfb8", 98))
    common_text(draw, rgba("#173126"), rgba("#426853", 165), y0=138)
    draw.line((28 * SCALE, 312 * SCALE, 92 * SCALE, 312 * SCALE), fill=rgba("#2f7b58", 170), width=2 * SCALE)
    draw_wrapped(draw, (28 * SCALE, 342 * SCALE), "\u4e0d\u7528\u592a\u591a\u89c6\u89c9\u523a\u6fc0\uff0c\u50cf\u6253\u5f00\u4e00\u9875\u6e05\u723d\u7684\u7ec3\u4e60\u7eb8\u3002", font(14), rgba("#173126", 165), 350 * SCALE, 7)
    panel(draw, (28 * SCALE, 730 * SCALE), (374 * SCALE, 124 * SCALE), rgba("#fffdf4", 192), rgba("#264634", 28))
    draw.text((48 * SCALE, 750 * SCALE), "Start a session", font=font(12, "bold"), fill=rgba("#2f7b58"))
    button(draw, (48 * SCALE, 784 * SCALE), 334 * SCALE, "\u5f00\u59cb\u4f53\u9a8c", rgba("#2f7b58"), rgba("#ffffff"))
    return save(base, "concept-04-paper-minimal.png")


def sheet(paths: list[Path]):
    thumb_w, thumb_h = 258, 559
    gap = 28
    margin = 36
    canvas = Image.new("RGB", (margin * 2 + thumb_w * 2 + gap, margin * 2 + thumb_h * 2 + gap + 48), "#f7f8f2")
    draw = ImageDraw.Draw(canvas)
    labels = ["01 Morning Bamboo", "02 Lakeside Breath", "03 Soft Garden", "04 Paper Minimal"]
    for i, path in enumerate(paths):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = margin + (i % 2) * (thumb_w + gap)
        y = margin + (i // 2) * (thumb_h + gap + 24)
        canvas.paste(im, (x, y))
        draw.rounded_rectangle((x, y, x + thumb_w, y + thumb_h), radius=8, outline="#d9ded3", width=1)
        draw.text((x, y + thumb_h + 8), labels[i], font=font(12, "bold"), fill="#243528")
    canvas.save(OUT / "cover-concepts-sheet.png")


def main():
    paths = [concept_bamboo(), concept_lake(), concept_garden(), concept_paper()]
    sheet(paths)
    for path in paths:
        print(path)
    print(OUT / "cover-concepts-sheet.png")


if __name__ == "__main__":
    main()
