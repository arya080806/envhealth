from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design_references"
GEN = Path("C:/Users/Administrator/.codex/generated_images/019eab01-c712-7f53-83c6-2c2d189c8feb")

SCENE = GEN / "ig_0fa4db7263b18064016a27beaf5020819188d25278dd126f95.png"
LOGOS = GEN / "ig_0fa4db7263b18064016a27bcf067b88191a194474190ca94dc.png"

W, H = 1680, 945


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/georgia.ttf" if not bold else "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for item in candidates:
        path = Path(item)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.strip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def cover(path: Path, size=(W, H), focus_x=0.52, focus_y=0.5) -> Image.Image:
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = max(0, min(nw - sw, int((nw - sw) * focus_x)))
    y = max(0, min(nh - sh, int((nh - sh) * focus_y)))
    return im.crop((x, y, x + sw, y + sh)).convert("RGBA")


def rounded(draw: ImageDraw.ImageDraw, box, radius=12, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, xy, body, size, fill, bold=False, anchor=None):
    draw.text(xy, body, font=font(size, bold), fill=fill, anchor=anchor)


def leaf_logo(draw: ImageDraw.ImageDraw, cx, cy, scale=1.0, fill="#6f8c63"):
    r = int(12 * scale)
    draw.ellipse((cx - r * 2, cy - r, cx, cy + r), fill=fill)
    draw.ellipse((cx, cy - r, cx + r * 2, cy + r), fill=fill)
    draw.line((cx, cy + r * 2, cx, cy - r), fill=fill, width=max(2, int(3 * scale)))
    draw.arc((cx - r * 3, cy + r * 1, cx + r * 3, cy + r * 4), 195, 345, fill=fill, width=max(2, int(2 * scale)))


def simple_leaf(draw: ImageDraw.ImageDraw, cx, cy, scale=1.0, fill="#6f8c63"):
    r = int(12 * scale)
    draw.ellipse((cx - r * 2, cy - r, cx, cy + r), fill=fill)
    draw.ellipse((cx, cy - r, cx + r * 2, cy + r), fill=fill)
    draw.line((cx, cy + r * 2, cx, cy - r), fill=fill, width=max(2, int(3 * scale)))


def crop_logo_refs() -> list[Path]:
    OUT.mkdir(exist_ok=True)
    sheet = Image.open(LOGOS).convert("RGB")
    sheet_out = OUT / "logo-reference-sheet-imagegen.png"
    sheet.save(sheet_out, quality=96)
    # The generated sheet is five marks arranged evenly across a cream canvas.
    centers = [214, 560, 864, 1194, 1496]
    paths: list[Path] = []
    for idx, cx in enumerate(centers, start=1):
        box = (max(0, cx - 170), 260, min(sheet.width, cx + 170), 640)
        crop = sheet.crop(box)
        # Make a square presentation tile.
        tile = Image.new("RGB", (420, 420), "#fffdf4")
        crop.thumbnail((330, 330), Image.Resampling.LANCZOS)
        tile.paste(crop, ((420 - crop.width) // 2, (420 - crop.height) // 2))
        p = OUT / f"logo-ref-{idx:02d}.png"
        tile.save(p, quality=96)
        paths.append(p)
    return paths


def compose_cover() -> Path:
    OUT.mkdir(exist_ok=True)
    bg = cover(SCENE, (W, H), 0.50, 0.50)
    # Soften only enough to sit behind UI while preserving game-world richness.
    bg.alpha_composite(Image.new("RGBA", (W, H), rgba("#fff7df", 34)))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Left reading veil with a warm cream fade.
    for x in range(0, 760):
        t = x / 760
        a = int(238 * (1 - t) + 30 * t)
        od.line((x, 0, x, H), fill=rgba("#fffdf4", a))
    # Bottom quiet fade.
    for y in range(640, H):
        t = (y - 640) / (H - 640)
        od.line((0, y, W, y), fill=rgba("#f6f0df", int(20 + 115 * t)))
    bg.alpha_composite(overlay)
    d = ImageDraw.Draw(bg)

    # Minimal top shell.
    rounded(d, (0, 0, W, 112), 0, rgba("#fffdf4", 226), rgba("#dce2d6", 210))
    # Combination logo: AI logo reference mark + manually typeset wordmark.
    logo_mark = Image.open(OUT / "logo-ref-01.png").convert("RGBA").resize((66, 66), Image.Resampling.LANCZOS)
    bg.alpha_composite(logo_mark, (36, 24))
    text(d, (108, 37), "灵感世界", 32, "#315d38", True)
    text(d, (108, 74), "Inspiration World", 14, "#6f7967")

    # Main copy mirrors the current app's home text.
    text(d, (96, 250), "灵感世界", 78, "#315d38", True)
    text(d, (100, 354), "Inspiration World", 20, "#617363")
    text(d, (100, 412), "从一个温和的场景开始，慢慢把空间变得更可待。", 24, "#60745f")

    # Start panel: keep only current meaningful CTA.
    panel = (96, 512, 528, 644)
    rounded(d, panel, 14, rgba("#fffdf4", 226), rgba("#d7cdb8", 220))
    text(d, (128, 538), "Start a session", 15, "#6f8c63", True)
    rounded(d, (128, 574, 496, 622), 24, "#f2bd42", "#dca52e")
    text(d, (312, 584), "开始体验", 20, "#314932", True, anchor="ma")
    d.line((454, 598, 474, 598), fill="#314932", width=3)
    d.line((464, 588, 474, 598), fill="#314932", width=3)
    d.line((464, 608, 474, 598), fill="#314932", width=3)

    path = OUT / "homepage-minimal-imagegen-effect.png"
    bg.convert("RGB").save(path, quality=96)
    return path


def main():
    print("logo refs:")
    for p in crop_logo_refs():
        print(p)
    print("effect:")
    print(compose_cover())


if __name__ == "__main__":
    main()
