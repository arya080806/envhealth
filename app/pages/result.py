"""Result detail page with compact comparison, history, and downloads."""
from __future__ import annotations

import json
import re
import time
from html import escape

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.services.layout_snapshot import recover_drag_layout_snapshot
from app.state import get_session, media_filename, media_url, resolve_media_path
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
.compare-heading-row {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}
.original-view-btn {
    flex: 0 0 auto;
    min-height: 34px;
    padding: 7px 12px;
    border-radius: 999px;
    color: #2F7B58;
    background: rgba(47,123,88,.08);
    border: 1px solid rgba(47,123,88,.16);
    text-decoration: none;
    font-size: 12px;
    line-height: 1.35;
    font-weight: 900;
}
.compare-hero {
    --compare-pos: 24%;
    width: 100%;
    display: grid;
    gap: 10px;
}
.compare-stage {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    min-height: 210px;
    max-height: 68vh;
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid rgba(47,123,88,.12);
    background: rgba(47,123,88,.07);
    cursor: zoom-in;
    -webkit-touch-callout: default;
}
.compare-stage img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
    background: rgba(47,123,88,.05);
}
.compare-stage.single img {
    position: static;
}
.compare-after-img {
    z-index: 1;
}
.compare-before-img {
    z-index: 2;
    clip-path: inset(0 calc(100% - var(--compare-pos)) 0 0);
}
.compare-divider {
    position: absolute;
    top: 0;
    bottom: 0;
    left: var(--compare-pos);
    z-index: 3;
    width: 2px;
    background: rgba(255,255,248,.92);
    box-shadow: 0 0 0 1px rgba(47,123,88,.22);
    pointer-events: none;
}
.compare-divider::after {
    content: none;
}
.compare-range {
    width: 100%;
    accent-color: #2F7B58;
}
.compare-caption-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    color: rgba(23,49,38,.64);
    font-size: 12px;
    line-height: 1.35;
    font-weight: 850;
}
.compare-download-proxy {
    display: none;
}
.compare-mini-grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.compare-mini-card,
.history-card {
    position: relative;
    min-width: 0;
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid rgba(47,123,88,.12);
    background: rgba(255,255,248,.72);
}
.history-card[data-history-kind="canvas"] {
    cursor: pointer;
}
.history-card[data-history-kind="canvas"].is-selected {
    border-color: rgba(47,123,88,.38);
    box-shadow: 0 0 0 2px rgba(47,123,88,.12);
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
    grid-auto-flow: row dense;
    gap: 10px;
}
.history-card img {
    width: 100%;
    height: 118px;
    object-fit: contain;
    display: block;
    background: rgba(47,123,88,.08);
}
.history-delete-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 4;
    min-width: 34px;
    min-height: 34px;
    padding: 0 10px;
    border: 0;
    border-radius: 999px;
    color: #FFFFFF;
    background: rgba(146, 42, 42, .88);
    box-shadow: 0 8px 20px rgba(48, 19, 19, .18);
    font-size: 12px;
    line-height: 1;
    font-weight: 950;
    cursor: pointer;
}
.history-delete-btn:active {
    transform: translateY(1px);
}
.result-confirm-overlay {
    position: fixed;
    inset: 0;
    z-index: 12000;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(20, 35, 26, .36);
}
.result-confirm-overlay.open {
    display: flex;
}
.result-confirm-card {
    width: min(92vw, 420px);
    padding: 18px;
    border-radius: 8px;
    background: #FFFFF8;
    border: 1px solid rgba(47,123,88,.16);
    box-shadow: 0 22px 60px rgba(18, 44, 30, .22);
}
.result-confirm-title {
    color: #173126;
    font-size: 17px;
    line-height: 1.35;
    font-weight: 950;
}
.result-confirm-actions {
    margin-top: 18px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.result-confirm-actions button {
    min-height: 42px;
    border-radius: 999px;
    border: 1px solid rgba(47,123,88,.16);
    font-size: 14px;
    line-height: 1;
    font-weight: 950;
    cursor: pointer;
}
.result-confirm-cancel {
    color: #2F7B58;
    background: rgba(47,123,88,.08);
}
.result-confirm-delete {
    color: #FFFFFF;
    background: #9D3434;
}
.canvas-snapshot {
    width: min(100%, 760px);
    max-height: min(58vh, 460px);
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
.canvas-elements-empty {
    color: rgba(23,49,38,.50);
    font-size: 12px;
    line-height: 1.35;
    font-weight: 750;
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
.canvas-element-index {
    width: 20px;
    height: 20px;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    flex: 0 0 auto;
    color: #FFFFFF;
    background: #2F7B58;
    font-size: 11px;
    line-height: 1;
    font-weight: 950;
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
    .compare-hero {
        justify-self: center;
        max-width: min(100%, 1120px);
    }
    .compare-stage {
        min-height: clamp(420px, 58vh, 650px);
        max-height: 70vh;
    }
    .compare-stage img {
        object-fit: cover;
    }
    .compare-stage.single img {
        width: 100%;
        height: 100%;
        object-fit: cover;
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
    .slider-list {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
    .canvas-snapshot {
        width: min(100%, 980px);
        max-height: min(64vh, 620px);
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
    .compare-stage {
        min-height: 178px;
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
        box.innerHTML = '<button class="result-lightbox-close" type="button" aria-label="close">×</button><img alt="preview">';
        document.body.appendChild(box);
        box.addEventListener('click', function (event) {
            if (event.target === box || event.target.classList.contains('result-lightbox-close')) {
                box.classList.remove('open');
            }
        });
        return box;
    }

    function openLightbox(src) {
        if (!src) return;
        var box = ensureLightbox();
        var img = box.querySelector('img');
        img.src = src;
        box.classList.add('open');
    }

    function ensureConfirmDialog() {
        var overlay = document.getElementById('result-delete-confirm');
        if (overlay) return overlay;
        overlay = document.createElement('div');
        overlay.id = 'result-delete-confirm';
        overlay.className = 'result-confirm-overlay';
        overlay.innerHTML = [
            '<div class="result-confirm-card" role="dialog" aria-modal="true">',
            '<div class="result-confirm-title">\u786e\u8ba4\u5220\u9664\u8fd9\u6761\u64cd\u4f5c\u8bb0\u5f55\u5417\uff1f</div>',
            '<div class="result-confirm-actions">',
            '<button class="result-confirm-cancel" type="button">\u53d6\u6d88</button>',
            '<button class="result-confirm-delete" type="button">\u5220\u9664</button>',
            '</div></div>',
        ].join('');
        document.body.appendChild(overlay);
        return overlay;
    }

    function confirmDeleteRecord() {
        return new Promise(function (resolve) {
            var overlay = ensureConfirmDialog();
            var cancel = overlay.querySelector('.result-confirm-cancel');
            var del = overlay.querySelector('.result-confirm-delete');
            function finish(value) {
                overlay.classList.remove('open');
                cancel.removeEventListener('click', onCancel);
                del.removeEventListener('click', onDelete);
                overlay.removeEventListener('click', onOverlay);
                resolve(value);
            }
            function onCancel() { finish(false); }
            function onDelete() { finish(true); }
            function onOverlay(event) { if (event.target === overlay) finish(false); }
            cancel.addEventListener('click', onCancel);
            del.addEventListener('click', onDelete);
            overlay.addEventListener('click', onOverlay);
            overlay.classList.add('open');
        });
    }

    function reindexCanvasHistory(section) {
        if (!section) return;
        var labels = Array.from(section.querySelectorAll('.history-card[data-history-kind="canvas"] .history-label'));
        var total = labels.length;
        labels.forEach(function (label, index) {
            var stamp = label.dataset.stamp || '';
            label.innerHTML = '\u7b2c ' + (total - index) + ' \u6b21\u64cd\u4f5c' + (stamp ? '<br>' + stamp : '');
        });
        var grid = section.querySelector('.history-grid');
        if (grid) {
            grid.style.display = 'none';
            void grid.offsetHeight;
            grid.style.display = 'grid';
        }
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
            return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch];
        });
    }

    function elementLabel(item) {
        return String(
            item.elemName || item.name || item.label || item.title || item.type || '\u5143\u7d20'
        ).trim();
    }

    function elementMeta(item) {
        var parts = [];
        var zone = item.zone || item.category;
        if (zone) parts.push(String(zone));
        var confidence = item.confidence;
        if (typeof confidence === 'number' && isFinite(confidence)) {
            var value = confidence >= 0 && confidence <= 1 ? confidence * 100 : confidence;
            parts.push(String(Math.round(value)) + '%');
        }
        var x = item.x;
        var y = item.y;
        if (typeof x === 'number' && typeof y === 'number' && isFinite(x) && isFinite(y)) {
            parts.push(String(Math.round(x)) + '%, ' + String(Math.round(y)) + '%');
        }
        return parts.join(' / ');
    }

    function parseCanvasElements(card) {
        if (!card) return [];
        try {
            var parsed = JSON.parse(card.dataset.elements || '[]');
            return Array.isArray(parsed) ? parsed : [];
        } catch (err) {
            return [];
        }
    }

    function renderCanvasElements(section, elements) {
        var list = section && section.querySelector('.canvas-element-list');
        if (!list) return;
        if (!Array.isArray(elements) || !elements.length) {
            list.innerHTML = '<div class="canvas-elements-empty">\u6682\u65e0\u521b\u4f5c\u5143\u7d20</div>';
            return;
        }
        list.innerHTML = elements.map(function (item, index) {
            item = item || {};
            var icon = String(item.icon || item.emoji || '').trim();
            var meta = elementMeta(item);
            return [
                '<span class="canvas-element-pill">',
                '<span class="canvas-element-index">', index + 1, '</span>',
                icon ? '<span>' + escapeHtml(icon) + '</span>' : '',
                '<span>', escapeHtml(elementLabel(item)), '</span>',
                meta ? '<span class="canvas-element-meta">' + escapeHtml(meta) + '</span>' : '',
                '</span>'
            ].join('');
        }).join('');
    }

    function selectCanvasCard(card) {
        if (!card) return;
        var section = card.closest('.result-section');
        if (!section) return;
        section.querySelectorAll('.history-card[data-history-kind="canvas"].is-selected').forEach(function (node) {
            node.classList.remove('is-selected');
        });
        card.classList.add('is-selected');
        renderCanvasElements(section, parseCanvasElements(card));
    }

    function removeHistoryGridItem(card, section) {
        if (!card) return;
        var grid = section && section.querySelector('.history-grid');
        if (!grid) {
            card.remove();
            return;
        }
        var gridItem = card;
        while (gridItem && gridItem.parentElement !== grid) {
            gridItem = gridItem.parentElement;
        }
        if (gridItem && gridItem.parentElement === grid) {
            gridItem.remove();
        } else {
            card.remove();
        }
    }

    document.addEventListener('click', function (event) {
        var deleteButton = event.target.closest('.history-delete-btn');
        if (deleteButton) {
            event.preventDefault();
            event.stopPropagation();
            confirmDeleteRecord().then(function (confirmed) {
                if (!confirmed) return;
                deleteButton.disabled = true;
                fetch('/api/canvas-history/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: deleteButton.dataset.sessionId || '',
                        filename: deleteButton.dataset.filename || ''
                    })
                }).then(function (resp) {
                    if (!resp.ok) throw new Error('delete failed');
                    var card = deleteButton.closest('.history-card');
                    var section = card && card.closest('.result-section');
                    removeHistoryGridItem(card, section);
                    reindexCanvasHistory(section);
                    var nextCard = section && section.querySelector('.history-card[data-history-kind="canvas"]');
                    if (nextCard) {
                        selectCanvasCard(nextCard);
                    } else {
                        renderCanvasElements(section, []);
                    }
                }).catch(function () {
                    deleteButton.disabled = false;
                    window.alert('\u5220\u9664\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002');
                });
            });
            return;
        }
        var canvasCard = event.target.closest('.history-card[data-history-kind="canvas"]');
        if (canvasCard && !event.target.closest('a.result-image-link, button, input')) {
            event.preventDefault();
            selectCanvasCard(canvasCard);
            return;
        }
        var link = event.target.closest('a.result-image-link');
        if (link) {
            event.preventDefault();
            openLightbox(link.getAttribute('href') || link.dataset.fullImage || '');
            return;
        }
        var stage = event.target.closest('.compare-stage[data-full-image]');
        if (!stage || event.target.closest('input, a, button')) return;
        openLightbox(stage.dataset.fullImage || '');
    });

    document.addEventListener('input', function (event) {
        var range = event.target.closest('.compare-range');
        if (!range) return;
        var hero = range.closest('.compare-hero');
        if (!hero) return;
        hero.style.setProperty('--compare-pos', String(range.value || 0) + '%');
    });

    var longPressTimer = null;
    var longPressStart = null;

    function clearLongPress() {
        if (longPressTimer) window.clearTimeout(longPressTimer);
        longPressTimer = null;
        longPressStart = null;
    }

    function downloadFromHero(hero) {
        var url = hero.dataset.downloadUrl || '';
        if (!url) return;
        var link = hero.querySelector('.compare-download-proxy');
        if (!link) {
            link = document.createElement('a');
            link.className = 'compare-download-proxy';
            hero.appendChild(link);
        }
        link.href = url;
        link.download = hero.dataset.downloadName || '';
        link.click();
    }

    document.addEventListener('pointerdown', function (event) {
        var hero = event.target.closest('.compare-hero[data-download-url]');
        if (!hero || event.target.closest('input, a, button')) return;
        longPressStart = {x: event.clientX, y: event.clientY};
        longPressTimer = window.setTimeout(function () {
            downloadFromHero(hero);
            clearLongPress();
        }, 760);
    });

    document.addEventListener('pointermove', function (event) {
        if (!longPressStart) return;
        var dx = Math.abs(event.clientX - longPressStart.x);
        var dy = Math.abs(event.clientY - longPressStart.y);
        if (dx > 12 || dy > 12) clearLongPress();
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (name) {
        document.addEventListener(name, clearLongPress);
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var box = document.getElementById('result-image-lightbox');
        if (box) box.classList.remove('open');
        var confirm = document.getElementById('result-delete-confirm');
        if (confirm) confirm.classList.remove('open');
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


def _dedupe_elements(items: list[dict]) -> list[dict]:
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


def _label_from_item(item: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = str(item.get(key) or '').strip()
        if value:
            return value
    return ''


def _element_from_label(label: str, source: str = 'user', base: dict | None = None) -> dict:
    element = dict(base or {})
    element['elemName'] = label
    element.setdefault('source', source)
    return element


def _inspire_annotation_elements(sketch_data: dict) -> list[dict]:
    annotation_items: list[dict] = []
    annotations = _json_value(sketch_data.get('userAnnotations'), [])
    if isinstance(annotations, list):
        for item in annotations:
            if not isinstance(item, dict):
                continue
            label = _label_from_item(item, ('safe_userLabel', 'userLabel', 'original_userLabel', 'label'))
            if label:
                annotation_items.append(_element_from_label(label, 'user', item))
    if annotation_items:
        return _dedupe_elements(annotation_items)

    stroke_items: list[dict] = []
    stroke_log = _json_value(sketch_data.get('strokeLog'), [])
    if isinstance(stroke_log, list):
        for item in stroke_log:
            if not isinstance(item, dict):
                continue
            label = _label_from_item(item, ('safe_userLabel', 'userLabel', 'autoLabel', 'label'))
            if label:
                source = 'user' if item.get('userLabel') else 'auto'
                stroke_items.append(_element_from_label(label, source, item))
    return _dedupe_elements(stroke_items)


def _history_generated_elements(history_item: dict) -> list[dict]:
    """Infer per-operation canvas elements from the matching generation record."""
    auto_items: list[dict] = []
    user_items: list[dict] = []
    for action in _json_value(history_item.get('safety_actions'), []):
        if not isinstance(action, dict):
            continue
        kind = action.get('kind')
        if kind == 'inspire_auto_label':
            label = _label_from_item(action, ('safe_name', 'original_name'))
            if label:
                auto_items.append(_element_from_label(label, 'auto', {
                    'confidence': action.get('confidence'),
                }))
        elif kind == 'inspire_user_annotation':
            label = _label_from_item(action, ('safe_text', 'original_text'))
            if label:
                user_items.append(_element_from_label(label, 'user'))

    prompt_text = str(history_item.get('final_safe_prompt') or history_item.get('prompt') or '')
    for label in re.findall(r'按照用户指定内容生成([^，,\n；;。]+)', prompt_text):
        clean = label.strip(' 「」"\'')
        if clean:
            user_items.append(_element_from_label(clean, 'user'))

    direct = _json_value(history_item.get('elements'), [])
    direct_items = _dedupe_elements([entry for entry in direct if isinstance(entry, dict)]) if isinstance(direct, list) else []

    if user_items:
        base_items = direct_items or _dedupe_elements(auto_items)
        user_items = _dedupe_elements(user_items)
        if not base_items or len(user_items) >= len(base_items):
            return user_items
        unchanged_count = max(0, len(base_items) - len(user_items))
        return _dedupe_elements(base_items[:unchanged_count] + user_items)

    auto_items = _dedupe_elements(auto_items)
    if auto_items:
        return auto_items

    if direct_items:
        return direct_items
    return []


def _canvas_elements(session) -> list[dict]:
    sketch_data = _json_value(getattr(session, 'sketch_data', {}) or {}, {})
    placed_elements = _json_value(getattr(session, 'placed_elements', []) or [], [])
    items: list[dict] = []

    if isinstance(sketch_data, dict):
        items = _inspire_annotation_elements(sketch_data)
        if items:
            return items
        results = _json_value(sketch_data.get('results'), [])
        if isinstance(results, list):
            items.extend(item for item in results if isinstance(item, dict))

    if not items and isinstance(placed_elements, list):
        items.extend(item for item in placed_elements if isinstance(item, dict))

    return _dedupe_elements(items)


def _canvas_item_elements(session, item: dict) -> list[dict]:
    item_path = str(item.get('path') or '')
    for history_item in _history(session):
        if not isinstance(history_item, dict):
            continue
        if str(history_item.get('canvas_path') or '') != item_path:
            continue
        history_elements = _history_generated_elements(history_item)
        if history_elements:
            return history_elements

    direct = _json_value(item.get('elements'), [])
    if isinstance(direct, list) and direct:
        return _dedupe_elements([entry for entry in direct if isinstance(entry, dict)])

    return _canvas_elements(session)


def _elements_data_attr(elements: list[dict]) -> str:
    return escape(json.dumps(elements or [], ensure_ascii=False, separators=(',', ':')), quote=True)


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
    pills = []
    for index, item in enumerate(elements, start=1):
        icon = escape(str(item.get('icon') or item.get('emoji') or '').strip())
        label = escape(_element_label(item))
        meta = escape(_element_meta(item))
        meta_html = f'<span class="canvas-element-meta">{meta}</span>' if meta else ''
        icon_html = f'<span>{icon}</span>' if icon else ''
        pills.append(
            f'<span class="canvas-element-pill"><span class="canvas-element-index">{index}</span>'
            f'{icon_html}<span>{label}</span>{meta_html}</span>'
        )
    list_html = ''.join(pills) if pills else '<div class="canvas-elements-empty">暂无创作元素</div>'
    ui.html(
        '<div class="canvas-elements">'
        '<div class="canvas-elements-title">创作元素</div>'
        f'<div class="canvas-element-list">{list_html}</div>'
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


def _is_canvas_snapshot_path(path_value: str | None) -> bool:
    name = media_filename(path_value)
    if not name:
        return False
    return '_canvas_' in name and name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))


def _canvas_history(session) -> list[dict]:
    if getattr(session, 'mode_used', '') == 'drag':
        try:
            recover_drag_layout_snapshot(getattr(session, 'id', '') or '')
            session = get_session(getattr(session, 'id', '') or '') or session
        except Exception:
            pass
    raw = getattr(session, 'canvas_history', []) or []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = []
    items = [
        item for item in raw
        if isinstance(item, dict)
        and _is_canvas_snapshot_path(item.get('path') or '')
        and resolve_media_path(item.get('path') or '')
    ]
    for item in _history(session):
        canvas_path = item.get('canvas_path') if isinstance(item, dict) else ''
        if (
            canvas_path
            and _is_canvas_snapshot_path(canvas_path)
            and resolve_media_path(canvas_path)
            and not any(str(row.get('path') or '') == str(canvas_path) for row in items)
        ):
            items.append({
                'path': canvas_path,
                'created_at': item.get('created_at') or 0,
                'mode': item.get('mode') or getattr(session, 'mode_used', ''),
            })
    latest = getattr(session, 'canvas_snapshot_path', '') or ''
    if (
        latest
        and _is_canvas_snapshot_path(latest)
        and resolve_media_path(latest)
        and not any(str(item.get('path') or '') == str(latest) for item in items)
    ):
        items.append({'path': latest, 'created_at': getattr(session, 'generation_finished_at', 0) or time.time()})
    return sorted(items, key=lambda item: float(item.get('created_at') or 0), reverse=True)


def _format_time(value) -> str:
    try:
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(float(value)))
    except (TypeError, ValueError, OSError):
        return ''


def _render_compare(session) -> None:
    original_path = getattr(session, 'uploaded_image_path', '') if session else ''
    generated_path = getattr(session, 'generated_image_path', '') if session else ''
    original_url = _path_url(original_path)
    generated_url = _path_url(generated_path)
    original_display_url = _path_url(original_path, display=True)
    generated_display_url = _path_url(generated_path, display=True)
    if not original_url and not generated_url:
        ui.html('<div class="result-empty">暂无可显示的结果图片。</div>', sanitize=False)
        return

    download_path = resolve_media_path(generated_path)
    download_url = f'/api/download/{download_path.name}' if download_path else generated_url
    download_name = download_path.name if download_path else media_filename(generated_path)
    main_full_url = generated_url or original_url
    main_src = generated_display_url or generated_url or original_display_url or original_url
    original_src = original_display_url or original_url

    with ui.column().classes('result-section').style('gap:0'):
        original_button = (
            f'<a class="original-view-btn result-image-link" href="{escape(original_url, quote=True)}">查看原图</a>'
            if original_url else ''
        )
        ui.html(
            '<div class="compare-heading-row">'
            '<div class="result-heading">改造详情</div>'
            f'{original_button}'
            '</div>',
            sanitize=False,
        )
        if original_url and generated_url:
            ui.html(
                '<div class="compare-hero" '
                f'data-download-url="{escape(download_url, quote=True)}" '
                f'data-download-name="{escape(download_name, quote=True)}">'
                f'<div class="compare-stage" data-full-image="{escape(generated_url, quote=True)}">'
                f'<img class="compare-after-img" src="{escape(main_src, quote=True)}" alt="改造后" loading="eager" decoding="async">'
                f'<img class="compare-before-img" src="{escape(original_src, quote=True)}" alt="改造前" loading="eager" decoding="async">'
                '<div class="compare-divider" aria-hidden="true"></div>'
                '</div>'
                '<input class="compare-range" type="range" min="0" max="100" value="24" aria-label="滑动查看原图">'
                '<div class="compare-caption-row"><span>改造后</span><span>滑动查看原图</span></div>'
                f'<a class="compare-download-proxy" href="{escape(download_url, quote=True)}" '
                f'download="{escape(download_name, quote=True)}"></a>'
                '</div>',
                sanitize=False,
            )
            return

        label = '改造后' if generated_url else '改造前'
        ui.html(
            '<div class="compare-hero" '
            f'data-download-url="{escape(download_url, quote=True)}" '
            f'data-download-name="{escape(download_name, quote=True)}">'
            f'<div class="compare-stage single" data-full-image="{escape(main_full_url, quote=True)}">'
            f'<img src="{escape(main_src, quote=True)}" alt="{label}" loading="eager" decoding="async">'
            '</div>'
            f'<div class="compare-caption-row"><span>{label}</span></div>'
            f'<a class="compare-download-proxy" href="{escape(download_url, quote=True)}" '
            f'download="{escape(download_name, quote=True)}"></a>'
            '</div>',
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
    elements = _canvas_item_elements(session, items[0]) if items else _canvas_elements(session)
    if not items and not elements:
        return
    title = '\u5143\u7d20\u5e03\u5c40' if mode == 'drag' else '\u521b\u4f5c\u753b\u5e03'
    session_id = getattr(session, 'id', '') or ''

    def _delete_button(path_value: str) -> str:
        filename = media_filename(path_value or '')
        if not filename:
            return ''
        return (
            '<button class="history-delete-btn" type="button" '
            f'data-session-id="{escape(session_id, quote=True)}" '
            f'data-filename="{escape(filename, quote=True)}">\u5220\u9664</button>'
        )

    with ui.column().classes('result-section').style('gap:0'):
        ui.html(f'<div class="detail-section-title">{escape(title)}</div>', sanitize=False)
        if len(items) == 1:
            item = items[0]
            path_value = item.get('path')
            snap_url = _path_url(path_value)
            item_elements = _canvas_item_elements(session, item)
            ui.html(
                '<div class="history-card is-selected" data-history-kind="canvas" '
                f"data-elements=\"{_elements_data_attr(item_elements)}\">"
                f'<a class="history-link result-image-link" href="{snap_url}">'
                f'<img class="canvas-snapshot" src="{snap_url}" alt="{escape(title)}" '
                'loading="lazy" decoding="async"></a>'
                f'<div class="history-label" data-stamp="{escape(_format_time(item.get("created_at")), quote=True)}">'
                f'{escape(title)}</div>'
                f'{_delete_button(path_value)}'
                '</div>',
                sanitize=False,
            )
            _render_canvas_elements(elements)
            return
        if items:
            with ui.element('div').classes('history-grid'):
                total = len(items)
                for index, item in enumerate(items):
                    path_value = item.get('path')
                    full_url = _path_url(path_value)
                    display_url = _path_url(path_value, display=True)
                    label = f'\u7b2c {total - index} \u6b21\u64cd\u4f5c'
                    stamp = _format_time(item.get('created_at'))
                    item_elements = _canvas_item_elements(session, item)
                    selected_class = ' is-selected' if index == 0 else ''
                    ui.html(
                        f'<div class="history-card{selected_class}" data-history-kind="canvas" '
                        f'data-elements="{_elements_data_attr(item_elements)}">'
                        f'<a class="history-link result-image-link" href="{full_url}">'
                        f'<img src="{display_url or full_url}" alt="{escape(label)}"></a>'
                        f'<div class="history-label" data-stamp="{escape(stamp, quote=True)}">{escape(label)}<br>{escape(stamp)}</div>'
                        f'{_delete_button(path_value)}'
                        '</div>',
                        sanitize=False,
                    )
        _render_canvas_elements(elements)

def _render_slider_detail(session) -> None:
    configs = [
        ('绿化程度', getattr(session, 'green_level', 50) or 50),
        ('人造元素', getattr(session, 'urban_level', 50) or 50),
        ('环境活力', getattr(session, 'vitality_level', 50) or 50),
        ('光线冷暖', getattr(session, 'light_warmth', 50) or 50),
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

