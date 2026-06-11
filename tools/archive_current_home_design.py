from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "design_references" / "home_before_redesign_20260609"
STATIC = ROOT / "app" / "static" / "images"


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


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.strip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def cover(path: Path, size: tuple[int, int], focus_y: float = 0.5) -> Image.Image:
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    sw, sh = size
    scale = max(sw / iw, sh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - sw) // 2
    y = max(0, min(nh - sh, int((nh - sh) * focus_y)))
    return im.crop((x, y, x + sw, y + sh)).convert("RGBA")


def make_effect_record() -> Path:
    w, h = 430, 932
    bg_path = STATIC / "forest-hero-dark.png"
    image = cover(bg_path, (w, h), 0.42)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(h):
        t = y / (h - 1)
        alpha = int(26 + 210 * max(0, (t - 0.12) / 0.88))
        for x in range(w):
            px[x, y] = (7, 18, 13, alpha)
    image.alpha_composite(overlay)

    draw = ImageDraw.Draw(image)
    # Vertical subtle grid from the existing CSS.
    for x in range(0, w, 34):
        draw.line((x, 0, x, h), fill=(244, 240, 230, 13), width=1)

    draw.ellipse((28, 35, 36, 43), fill=rgba("#B7F27E"))
    draw.text((45, 31), "INSPIRATION WORLD", font=font(11, True), fill=(244, 240, 230, 184))
    draw.text((28, 138), "灵感世界", font=font(52, True), fill=rgba("#F4F0E6"))
    draw.text((30, 202), "INSPIRATION WORLD", font=font(14, True), fill=(244, 240, 230, 168))

    panel = (32, 722, 398, 858)
    draw.rounded_rectangle(panel, radius=8, fill=(7, 18, 13, 158), outline=(244, 240, 230, 32), width=1)
    draw.text((50, 746), "START A SESSION", font=font(12, True), fill=rgba("#B7F27E"))
    draw.rounded_rectangle((50, 794, 380, 848), radius=27, fill=rgba("#B7F27E"))
    draw.text((183, 811), "开始体验", font=font(15, True), fill=rgba("#07120D"))
    path = ARCHIVE / "current_home_effect_reconstruction.png"
    image.convert("RGB").save(path, quality=96)
    return path


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for filename in [
        "forest-hero-dark.png",
        "forest-hero-dark.webp",
        "nature-texture-dark.png",
        "nature-texture-dark.webp",
    ]:
        source = STATIC / filename
        if source.exists():
            shutil.copy2(source, ARCHIVE / filename)

    shutil.copy2(ROOT / "app" / "pages" / "home.py", ARCHIVE / "home.py.before_redesign")
    effect_path = make_effect_record()

    readme = ARCHIVE / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Home Page Before Redesign",
                "",
                f"Archived at: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## 背景图",
                "",
                "- `forest-hero-dark.png` / `forest-hero-dark.webp`: 旧版首页主背景。",
                "- `nature-texture-dark.*`: 旧版全局深色自然纹理背景。",
                "",
                "## 设计方法记录",
                "",
                "- 移动端优先：默认宽度约 430px，横屏桌面时扩展到 tablet 宽度。",
                "- 深色沉浸：暗森林背景叠加深绿色纵向渐变遮罩。",
                "- 玻璃面板：底部半透明深色面板承载 `Start a session` 与开始按钮。",
                "- 高对比标题：左上大字号白色中文标题，英文副标题采用大写字距。",
                "- 视觉纹理：使用细纵向网格和浅色高光线条增强沉浸感。",
                "",
                "## 当前效果记录",
                "",
                f"- 旧版效果复刻图：`{effect_path.name}`",
                "- 旧版源码快照：`home.py.before_redesign`",
                "",
                "说明：效果图为根据旧版 CSS 与背景素材生成的本地复刻记录，用于对比与回滚参考。",
            ]
        ),
        encoding="utf-8",
    )
    print(ARCHIVE)


if __name__ == "__main__":
    main()
