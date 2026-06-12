"""Result detail page with compact comparison, history, and downloads."""
from __future__ import annotations

import json
import time
from html import escape
from pathlib import Path

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session, media_url, resolve_media_path
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


MODE_LABELS = {
    'slider': '参数调节',
    'drag': '自由创作',
    'ai': '智能推荐',
    'inspire': '灵感创想',
    'chat': '对话改造',
}

RESULT_CSS = '''
<style>
.result-bg {
    height: 100dvh !important;
    min-height: 100dvh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    overscroll-behavior-y: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    background:
        radial-gradient(circle at 50% 4%, rgba(183,242,126,.16), transparent 30%),
        linear-gradient(180deg, rgba(255,255,248,.88), rgba(243,248,238,.96) 52%, rgba(232,240,227,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.result-shell {
    width: 100%;
    padding: 18px 18px 176px;
    gap: 16px;
}
.result-heading {
    color: #173126;
    font-size: 17px;
    line-height: 1.35;
    font-weight: 950;
    letter-spacing: 0;
}
.result-section {
    width: 100%;
    padding: 15px;
    border-radius: 8px;
    background: rgba(255,255,248,.78);
    border: 1px solid rgba(47,123,88,.12);
    box-shadow: 0 14px 30px rgba(38,70,52,.08);
}
.detail-section-title {
    color: #173126;
    font-size: 17px;
    line-height: 1.35;
    font-weight: 950;
    margin-bottom: 12px;
}
.compare-mini-grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.compare-mini-card,
.history-card {
    min-width: 0;
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid rgba(47,123,88,.12);
    background: rgba(255,255,248,.72);
}
.compare-mini-link,
.history-link {
    display: block;
    color: inherit;
    text-decoration: none;
    -webkit-touch-callout: default;
}
.result-image-link {
    cursor: zoom-in;
}
.compare-mini-card img {
    width: 100%;
    height: 176px;
    object-fit: contain;
    display: block;
    background: rgba(47,123,88,.08);
}
.compare-mini-label,
.history-label {
    padding: 8px 10px;
    color: rgba(23,49,38,.72);
    font-size: 12px;
    line-height: 1.35;
    font-weight: 850;
}
.history-grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.history-card img {
    width: 100%;
    height: 118px;
    object-fit: contain;
    display: block;
    background: rgba(47,123,88,.08);
}
.canvas-snapshot {
    width: min(100%, 520px);
    max-height: 240px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    border: 1px solid rgba(47,123,88,.10);
    background: rgba(47,123,88,.06);
}
.canvas-elements {
    margin-top: 12px;
    display: grid;
    gap: 8px;
}
.canvas-elements-title {
    color: rgba(23,49,38,.78);
    font-size: 12px;
    line-height: 1.35;
    font-weight: 950;
}
.canvas-element-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.canvas-element-pill {
    max-width: 100%;
    min-height: 34px;
    padding: 7px 10px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: #173126;
    background: rgba(47,123,88,.08);
    border: 1px solid rgba(47,123,88,.14);
    font-size: 12px;
    line-height: 1.3;
    font-weight: 850;
}
.canvas-element-meta {
    color: rgba(23,49,38,.56);
    font-size: 10px;
    font-weight: 750;
}
.slider-list {
    display: grid;
    gap: 10px;
}
.slider-row {
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(47,123,88,.10);
    background: rgba(255,255,248,.68);
}
.slider-row-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: #173126;
    font-size: 13px;
    font-weight: 900;
}
.slider-track {
    margin-top: 9px;
    height: 7px;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(47,123,88,.12);
}
.slider-fill {
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #2F7B58, #B7F27E);
}
.chat-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.chat-tag {
    padding: 7px 10px;
    border-radius: 999px;
    color: #2F7B58;
    background: rgba(47,123,88,.10);
    border: 1px solid rgba(47,123,88,.14);
    font-size: 12px;
    font-weight: 850;
}
.chat-extra {
    margin-top: 10px;
    padding: 11px 12px;
    border-radius: 8px;
    color: rgba(23,49,38,.70);
    background: rgba(47,123,88,.06);
    border: 1px dashed rgba(47,123,88,.18);
    font-size: 13px;
    line-height: 1.6;
}
.result-actions {
    width: 100%;
    display: grid;
    gap: 10px;
}
.download-link {
    display: block;
    width: 100%;
    text-align: center;
    padding: 14px 18px;
    border-radius: 999px;
    color: #2F7B58;
    text-decoration: none;
    border: 1.5px solid rgba(47,123,88,.24);
    background: rgba(255,255,248,.70);
    font-size: 14px;
    font-weight: 900;
}
.result-empty {
    width: 100%;
    padding: 22px 16px;
    border-radius: 8px;
    color: rgba(23,49,38,.68);
    background: rgba(255,255,248,.74);
    border: 1px solid rgba(47,123,88,.12);
    text-align: center;
    font-size: 13px;
    line-height: 1.6;
    font-weight: 750;
}
.result-lightbox {
    position: fixed;
    inset: 0;
    z-index: 6000;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 28px;
    background: rgba(7,18,13,.82);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}
.result-lightbox.open {
    display: flex;
}
.result-lightbox img {
    display: block;
    max-width: min(96vw, 1180px);
    max-height: 88vh;
    object-fit: contain;
    border-radius: 8px;
    background: rgba(255,255,248,.90);
    box-shadow: 0 28px 80px rgba(0,0,0,.42);
}
.result-lightbox-close {
    position: fixed;
    top: 18px;
    right: 18px;
    width: 42px;
    height: 42px;
    border: 1px solid rgba(255,255,248,.36);
    border-radius: 999px;
    color: #F8FAF2;
    background: rgba(16,37,26,.72);
    font-size: 26px;
    line-height: 38px;
    text-align: center;
    cursor: pointer;
}
@media (min-width: 900px) and (orientation: landscape) {
    .result-shell {
        padding: 24px 34px 190px;
    }
    .compare-mini-card img {
        height: 220px;
    }
    .history-grid {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
    .history-card img {
        height: 128px;
    }
}
@media (max-width: 360px) {
    .result-shell {
        padding-left: 14px;
        padding-right: 14px;
    }
    .compare-mini-card img {
        height: 142px;
    }
}
</style>
'''

RESULT_LIGHTBOX_JS = '''
<script>
(function () {
    if (window.ResultImageLightboxReady) return;
    window.ResultImageLightboxReady = true;

    function ensureLightbox() {
        var box = document.getElementById('result-image-lightbox');
        if (box) return box;
        box = document.createElement('div');
        box.id = 'result-image-lightbox';
        box.className = 'result-lightbox';
        box.innerHTML = '<button class="result-lightbox-close" type="button" aria-label="关闭大图">×</button><img alt="查看大图">';
        document.body.appendChild(box);
        box.addEventListener('click', function (event) {
            if (event.target === box || event.target.classList.contains('result-lightbox-close')) {
                box.classList.remove('open');
            }
        });
        return box;
    }

    document.addEventListener('click', function (event) {
        var link = event.target.closest('a.result-image-link');
        if (!link) return;
        event.preventDefault();
        var box = ensureLightbox();
        var img = box.querySelector('img');
        img.src = link.getAttribute('href') || link.dataset.fullImage || '';
        box.classList.add('open');
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var box = document.getElementById('result-image-lightbox');
        if (box) box.classList.remove('open');
    });
})();
</script>
'''


def _path_url(path_value: str | None, *, thumb: bool = False, display: bool = False) -> str:
    return media_url(path_value or '', thumb=thumb, display=display)


def _current_user_id() -> int | None:
    user = app.storage.user.get('user', {}) or {}
    try:
        return int(user.get('id')) if user.get('id') is not None else None
    except (TypeError, ValueError):
        return None


def _can_view_session(session, user_id: int) -> bool:
    owner_id = getattr(session, 'user_id', None)
    if owner_id in (None, ''):
        return True
    try:
        return int(owner_id) == int(user_id)
    except (TypeError, ValueError):
        return False


def _json_value(value, fallback):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return fallback
    return value if value is not None else fallback


def _canvas_elements(session) -> list[dict]:
    sketch_data = _json_value(getattr(session, 'sketch_data', {}) or {}, {})
    placed_elements = _json_value(getattr(session, 'placed_elements', []) or [], [])
    items: list[dict] = []

    if isinstance(sketch_data, dict):
        results = _json_value(sketch_data.get('results'), [])
        if isinstance(results, list):
            items.extend(item for item in results if isinstance(item, dict))

    if not items and isinstance(placed_elements, list):
        items.extend(item for item in placed_elements if isinstance(item, dict))

    seen = set()
    unique_items: list[dict] = []
    for item in items:
        name = str(item.get('elemName') or item.get('name') or item.get('label') or item.get('type') or '').strip()
        key = (name, str(item.get('x') or ''), str(item.get('y') or ''))
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)
    return unique_items[:32]


def _element_label(item: dict) -> str:
    return str(
        item.get('elemName')
        or item.get('name')
        or item.get('label')
        or item.get('title')
        or item.get('type')
        or '元素'
    ).strip()


def _element_meta(item: dict) -> str:
    parts: list[str] = []
    zone = item.get('zone') or item.get('category')
    if zone:
        parts.append(str(zone))
    confidence = item.get('confidence')
    if isinstance(confidence, (int, float)):
        confidence_value = confidence * 100 if 0 <= confidence <= 1 else confidence
        parts.append(f'{round(confidence_value)}%')
    x = item.get('x')
    y = item.get('y')
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        parts.append(f'{round(x)}%, {round(y)}%')
    return ' / '.join(parts)


def _render_canvas_elements(elements: list[dict]) -> None:
    if not elements:
        return
    pills = []
    for item in elements:
        icon = escape(str(item.get('icon') or item.get('emoji') or '').strip())
        label = escape(_element_label(item))
        meta = escape(_element_meta(item))
        meta_html = f'<span class="canvas-element-meta">{meta}</span>' if meta else ''
        icon_html = f'<span>{icon}</span>' if icon else ''
        pills.append(f'<span class="canvas-element-pill">{icon_html}<span>{label}</span>{meta_html}</span>')
    ui.html(
        '<div class="canvas-elements">'
        '<div class="canvas-elements-title">创作元素</div>'
        f'<div class="canvas-element-list">{"".join(pills)}</div>'
        '</div>',
        sanitize=False,
    )


def _history(session) -> list[dict]:
    raw = getattr(session, 'generation_history', []) or []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = []
    items = [item for item in raw if isinstance(item, dict) and resolve_media_path(item.get('path') or '')]
    latest = getattr(session, 'generated_image_path', '') or ''
    if latest and resolve_media_path(latest) and not any(str(item.get('path') or '') == str(latest) for item in items):
        items.append({'path': latest, 'created_at': getattr(session, 'generation_finished_at', 0) or time.time()})
    return sorted(items, key=lambda item: float(item.get('created_at') or 0), reverse=True)


def _canvas_history(session) -> list[dict]:
    raw = getattr(session, 'canvas_history', []) or []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = []
    items = [item for item in raw if isinstance(item, dict) and resolve_media_path(item.get('path') or '')]
    for item in _history(session):
        canvas_path = item.get('canvas_path') if isinstance(item, dict) else ''
        if canvas_path and resolve_media_path(canvas_path) and not any(str(row.get('path') or '') == str(canvas_path) for row in items):
            items.append({
                'path': canvas_path,
                'created_at': item.get('created_at') or 0,
                'mode': item.get('mode') or getattr(session, 'mode_used', ''),
            })
    latest = getattr(session, 'canvas_snapshot_path', '') or ''
    if latest and resolve_media_path(latest) and not any(str(item.get('path') or '') == str(latest) for item in items):
        items.append({'path': latest, 'created_at': getattr(session, 'generation_finished_at', 0) or time.time()})
    return sorted(items, key=lambda item: float(item.get('created_at') or 0), reverse=True)


def _format_time(value) -> str:
    try:
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(float(value)))
    except (TypeError, ValueError, OSError):
        return ''


def _render_compare(session) -> None:
    original_url = _path_url(getattr(session, 'uploaded_image_path', '') if session else '')
    generated_url = _path_url(getattr(session, 'generated_image_path', '') if session else '')
    original_display_url = _path_url(getattr(session, 'uploaded_image_path', '') if session else '', display=True)
    generated_display_url = _path_url(getattr(session, 'generated_image_path', '') if session else '', display=True)
    if not original_url and not generated_url:
        ui.html('<div class="result-empty">暂无可显示的结果图片。</div>', sanitize=False)
        return

    with ui.column().classes('result-section').style('gap:0'):
        ui.html('<div class="result-heading">改造前 vs 改造后</div>', sanitize=False)
        ui.element('div').classes('section-divider')
        with ui.element('div').classes('compare-mini-grid'):
            if original_url:
                ui.html(
                    f'<a class="compare-mini-card compare-mini-link result-image-link" href="{original_url}">'
                    f'<img src="{original_display_url or original_url}" alt="改造前">'
                    '<div class="compare-mini-label">改造前</div></a>',
                    sanitize=False,
                )
            if generated_url:
                ui.html(
                    f'<a class="compare-mini-card compare-mini-link result-image-link" href="{generated_url}">'
                    f'<img src="{generated_display_url or generated_url}" alt="改造后">'
                    '<div class="compare-mini-label">改造后</div></a>',
                    sanitize=False,
                )


def _render_history(session) -> None:
    items = _history(session)
    if len(items) <= 1:
        return
    with ui.column().classes('result-section').style('gap:0'):
        ui.html('<div class="detail-section-title">生成记录</div>', sanitize=False)
        with ui.element('div').classes('history-grid'):
            for index, item in enumerate(items):
                full_url = _path_url(item.get('path'))
                display_url = _path_url(item.get('path'), display=True)
                label = f'第 {len(items) - index} 次生成'
                stamp = _format_time(item.get('created_at'))
                ui.html(
                    f'<a class="history-card history-link result-image-link" href="{full_url}">'
                    f'<img src="{display_url or full_url}" alt="{escape(label)}">'
                    f'<div class="history-label">{escape(label)}<br>{escape(stamp)}</div></a>',
                    sanitize=False,
                )


def _render_canvas_snapshot(session, mode: str) -> None:
    items = _canvas_history(session)
    elements = _canvas_elements(session)
    if not items and not elements:
        return
    title = '元素布局' if mode == 'drag' else '创作画布'
    with ui.column().classes('result-section').style('gap:0'):
        ui.html(f'<div class="detail-section-title">{escape(title)}</div>', sanitize=False)
        if len(items) == 1:
            snap_url = _path_url(items[0].get('path'))
            snap_display_url = _path_url(items[0].get('path'), display=True)
            ui.html(
                f'<a class="history-link result-image-link" href="{snap_url}">'
                f'<img class="canvas-snapshot" src="{snap_display_url or snap_url}" alt="{escape(title)}"></a>',
                sanitize=False,
            )
            _render_canvas_elements(elements)
            return
        if items:
            with ui.element('div').classes('history-grid'):
                total = len(items)
                for index, item in enumerate(items):
                    full_url = _path_url(item.get('path'))
                    display_url = _path_url(item.get('path'), display=True)
                    label = f'第 {total - index} 次操作'
                    stamp = _format_time(item.get('created_at'))
                    ui.html(
                        f'<a class="history-card history-link result-image-link" href="{full_url}">'
                        f'<img src="{display_url or full_url}" alt="{escape(label)}">'
                        f'<div class="history-label">{escape(label)}<br>{escape(stamp)}</div></a>',
                        sanitize=False,
                    )
        _render_canvas_elements(elements)


def _render_slider_detail(session) -> None:
    configs = [
        ('绿化程度', getattr(session, 'green_level', 50) or 50),
        ('人造元素', getattr(session, 'urban_level', 50) or 50),
        ('环境活力', getattr(session, 'vitality_level', 50) or 50),
        ('光线温度', getattr(session, 'light_warmth', 50) or 50),
    ]
    with ui.column().classes('result-section').style('gap:0'):
        ui.html('<div class="detail-section-title">调节参数</div>', sanitize=False)
        with ui.element('div').classes('slider-list'):
            for label, raw_value in configs:
                value = max(0, min(100, int(round(float(raw_value)))))
                ui.html(
                    '<div class="slider-row">'
                    f'<div class="slider-row-top"><span>{escape(label)}</span><span>{value}%</span></div>'
                    f'<div class="slider-track"><div class="slider-fill" style="width:{value}%"></div></div>'
                    '</div>',
                    sanitize=False,
                )


def _render_chat_detail(session) -> None:
    moods = getattr(session, 'chat_moods', []) or []
    extra = getattr(session, 'chat_extra', '') or ''
    if not moods and not extra:
        return
    with ui.column().classes('result-section').style('gap:0'):
        ui.html('<div class="detail-section-title">对话意图</div>', sanitize=False)
        if moods:
            tags = ''.join(f'<span class="chat-tag">{escape(str(mood))}</span>' for mood in moods)
            ui.html(f'<div class="chat-tags">{tags}</div>', sanitize=False)
        if extra:
            ui.html(f'<div class="chat-extra">{escape(extra)}</div>', sanitize=False)


def _render_actions(session, sid: str, mode: str) -> None:
    with ui.column().classes('result-actions'):
        if mode in ('drag', 'inspire'):
            edit_url = f'/drag-mode?sid={sid}&back=result' if mode == 'drag' else f'/inspire-mode?sid={sid}&back=result'
            edit_label = '继续创作' if mode == 'drag' else '继续绘制'
            ui.button(edit_label, on_click=lambda u=edit_url: smooth_navigate(u)).props(
                'no-caps unelevated'
            ).style(LIGHT_PRIMARY_BTN_STYLE)

        generated_path = resolve_media_path(getattr(session, 'generated_image_path', '') or '')
        if generated_path:
            ui.html(
                f'<a class="download-link" href="/api/download/{generated_path.name}" download="{generated_path.name}">'
                '下载结果图片</a>',
                sanitize=False,
            )


def create_result_page():
    @ui.page('/result')
    def result_page(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(RESULT_CSS)
        ui.add_head_html(RESULT_LIGHTBOX_JS)

        user_id = _current_user_id()
        if not user_id:
            smooth_navigate('/login')
            return

        session = get_session(sid) if sid else None
        access_denied = bool(session and not _can_view_session(session, user_id))
        if access_denied:
            session = None
        mode = (getattr(session, 'mode_used', '') or '') if session else ''

        with ui.column().classes('mobile-page light-page result-bg').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(
                    icon='arrow_back',
                    on_click=lambda: smooth_navigate('/records' if back == 'records' else f'/mode-select?sid={sid}'),
                ).props('flat round dense').style(f'color:{COLORS["primary_dark"]}')
                title = '改造详情' if back == 'records' else '改造结果'
                ui.label(title).style(
                    f'font-size:17px;font-weight:850;margin-left:4px;color:{COLORS["primary_dark"]}'
                )

            with ui.column().classes('result-shell'):
                if access_denied:
                    ui.html('<div class="result-empty">没有权限查看这条创作记录。</div>', sanitize=False)
                    return

                if not session:
                    ui.html('<div class="result-empty">没有找到这条创作记录。</div>', sanitize=False)
                    return

                if (getattr(session, 'generation_status', '') or '') in ('queued', 'running'):
                    ui.html('<div class="result-empty">AI 仍在后台生成中，完成后草稿箱会出现绿色提示点。</div>', sanitize=False)
                    return

                if (getattr(session, 'generation_status', '') or '') == 'error' and not getattr(session, 'generated_image_path', ''):
                    error = escape(getattr(session, 'generation_error', '') or '生成失败，请稍后再试。')
                    ui.html(f'<div class="result-empty">{error}</div>', sanitize=False)
                    return

                _render_compare(session)
                _render_history(session)
                _render_canvas_snapshot(session, mode)
                if mode in ('slider', 'ai'):
                    _render_slider_detail(session)
                if mode == 'chat':
                    _render_chat_detail(session)
                _render_actions(session, sid, mode)
