"""Recover or render element placement snapshots for old drag sessions."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.db import get_session as db_get_session, update_session as db_update_session
from app.services.image_variants import warm_image_variants
from app.state import OUTPUT_DIR, resolve_media_path


def _load_elements(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return []
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/arial.ttf',
    ]
    for candidate in candidates:
        try:
            path = Path(candidate)
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _draw_marker(draw: ImageDraw.ImageDraw, x: float, y: float, number: int, radius: int, font: ImageFont.ImageFont) -> None:
    fill = (47, 123, 88, 232)
    outline = (255, 255, 248, 245)
    shadow = (16, 37, 26, 90)
    draw.ellipse((x - radius + 3, y - radius + 4, x + radius + 3, y + radius + 4), fill=shadow)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=outline, width=max(3, radius // 6))
    text = str(number)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        tw, th = draw.textlength(text, font=font), radius
    draw.text((x - tw / 2, y - th / 2 - radius * 0.08), text, fill=(255, 255, 255), font=font)


def recover_drag_layout_snapshot(session_id: str) -> str:
    """Create a readable placement map when an old drag session lacks a snapshot."""
    session = db_get_session(session_id)
    if not session or session.get('mode_used') != 'drag':
        return ''
    history = session.get('canvas_history') or []
    if isinstance(history, list) and any(isinstance(item, dict) and item.get('layout_recovery_disabled') for item in history):
        return ''
    existing = resolve_media_path(session.get('canvas_snapshot_path'))
    if existing:
        return str(existing)

    elements = _load_elements(session.get('placed_elements'))
    if not elements:
        return ''
    original = resolve_media_path(session.get('uploaded_image_path'))
    if not original:
        return ''

    safe_name = f"{session_id}_canvas_recovered_{uuid.uuid4().hex[:6]}.png"
    output_path = OUTPUT_DIR / safe_name
    with Image.open(original) as opened:
        base = ImageOps.exif_transpose(opened).convert('RGBA')
    width, height = base.size
    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    radius = max(18, min(42, int(min(width, height) * 0.032)))
    font = _font(max(18, int(radius * 0.95)))

    for index, item in enumerate(elements, start=1):
        try:
            x = max(0.0, min(100.0, float(item.get('x') or 0))) / 100.0 * width
            y = max(0.0, min(100.0, float(item.get('y') or 0))) / 100.0 * height
        except (TypeError, ValueError):
            continue
        _draw_marker(draw, x, y, index, radius, font)

    composed = Image.alpha_composite(base, overlay).convert('RGB')
    composed.save(output_path, 'PNG', optimize=True)
    warm_image_variants(output_path)

    history = session.get('canvas_history') or []
    if not isinstance(history, list):
        history = []
    history.append({
        'path': str(output_path),
        'created_at': time.time(),
        'mode': 'drag',
        'recovered': True,
        'elements': elements[:40],
        'element_count': len(elements[:40]),
    })
    db_update_session(session_id, canvas_snapshot_path=str(output_path), canvas_history=history[-30:])
    return str(output_path)
