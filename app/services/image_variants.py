from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[2]
THUMB_SIZE = (176, 176)
DISPLAY_SIZE = (1920, 1920)
DISPLAY_QUALITY = 88
THUMB_DIR = PROJECT_ROOT / 'outputs' / 'thumbs'
DISPLAY_DIR = PROJECT_ROOT / 'outputs' / 'display'
THUMB_DIR.mkdir(parents=True, exist_ok=True)
DISPLAY_DIR.mkdir(parents=True, exist_ok=True)


def variant_name(original: Path, label: str) -> str:
    try:
        stat = original.stat()
        fingerprint = f'{stat.st_size:x}_{stat.st_mtime_ns:x}'
    except OSError:
        fingerprint = '0'
    return f'{original.stem}_{fingerprint}_{label}.jpg'


def _image_to_rgb(img: Image.Image) -> Image.Image:
    if img.mode == 'RGB':
        return img
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        base = Image.new('RGB', img.size, (255, 255, 248))
        rgba = img.convert('RGBA')
        base.paste(rgba, mask=rgba.split()[-1])
        return base
    return img.convert('RGB')


def get_thumb(original: Path) -> Path | None:
    thumb_path = THUMB_DIR / variant_name(original, 'thumb')
    if thumb_path.exists():
        return thumb_path
    try:
        with Image.open(original) as opened:
            img = ImageOps.exif_transpose(opened)
            img.thumbnail(THUMB_SIZE)
            img = _image_to_rgb(img)
            img.save(thumb_path, 'JPEG', quality=70, optimize=True)
        return thumb_path
    except Exception:
        return None


def get_display_image(original: Path) -> Path | None:
    display_path = DISPLAY_DIR / variant_name(original, 'display')
    if display_path.exists():
        return display_path
    try:
        with Image.open(original) as opened:
            img = ImageOps.exif_transpose(opened)
            img.thumbnail(DISPLAY_SIZE)
            img = _image_to_rgb(img)
            img.save(display_path, 'JPEG', quality=DISPLAY_QUALITY, optimize=True, progressive=True)
        return display_path
    except Exception:
        return None


def warm_image_variants(original: str | Path | None) -> None:
    if not original:
        return
    path = Path(original)
    if not path.exists() or not path.is_file():
        return
    get_thumb(path)
    get_display_image(path)
