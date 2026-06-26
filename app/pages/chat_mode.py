"""对话改造模式页面。"""
from __future__ import annotations

import base64
import json

from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session, media_url
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


def _mood_icon_data_url(body: str, color: str) -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36" '
        f'fill="none" stroke="{color}" stroke-width="1.85" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


MOOD_CARDS = [
    (
        _mood_icon_data_url(
            '<path d="M6 13c3.2-2.4 6.1-2.4 9.3 0s6.2 2.4 9.4 0 4.1-2.4 5.3-1.6"/>'
            '<path d="M6 19c3.2-2.4 6.1-2.4 9.3 0s6.2 2.4 9.4 0 4.1-2.4 5.3-1.6"/>'
            '<path d="M8 25c2.6-1.6 5.2-1.6 7.8 0s5.2 1.6 7.8 0"/>',
            '#2F8FA0',
        ),
        '平静放松',
        '清透、安静、留白感',
        '#EEF9F4',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="M18 5v5M18 26v5M5 18h5M26 18h5M8.8 8.8l3.5 3.5M23.7 23.7l3.5 3.5M27.2 8.8l-3.5 3.5M12.3 23.7l-3.5 3.5"/>'
            '<circle cx="18" cy="18" r="5"/>',
            '#D79A36',
        ),
        '充满活力',
        '明亮、有生命力',
        '#FFF7E8',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="M18 29s-9-5.5-9-12.1c0-3.4 2.4-5.9 5.6-5.9 1.8 0 3.2.9 4.4 2.5 1.2-1.6 2.6-2.5 4.4-2.5 3.2 0 5.6 2.5 5.6 5.9C29 23.5 18 29 18 29Z"/>'
            '<path d="M13.5 19.5h2.8l1.6-3.2 2.1 5 1.4-2.6h2.6"/>',
            '#C98252',
        ),
        '治愈温暖',
        '柔和、亲近、被包围',
        '#FFF3EA',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<circle cx="18" cy="18" r="10"/><circle cx="18" cy="18" r="4"/>'
            '<path d="M18 5v4M18 27v4M5 18h4M27 18h4"/>',
            '#3D8A68',
        ),
        '清醒专注',
        '干净、秩序、少干扰',
        '#EEF8F1',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="M18 29c-5-4-8-8.2-8-12.2 0-3.3 2.1-5.8 5.2-5.8 1.4 0 2.5.6 3.4 1.7.9-1.1 2-1.7 3.4-1.7 3.1 0 5.2 2.5 5.2 5.8 0 4-4.2 8.2-9.2 12.2Z"/>'
            '<path d="M7 9l1.2 2.3L10.5 12l-2.3 1.2L7 15.5l-1.2-2.3L3.5 12l2.3-.7Z"/>',
            '#B16C88',
        ),
        '浪漫诗意',
        '轻雾、柔光、朦胧',
        '#FFF1F6',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="M5 21c2.8-3 5.8-3 8.7 0s5.8 3 8.7 0 5.8-3 8.6 0"/>'
            '<path d="M8 15c2.2-2.1 4.4-2.1 6.6 0s4.4 2.1 6.6 0 4.4-2.1 6.6 0"/>'
            '<path d="M11 27c1.6-1.3 3.2-1.3 4.8 0s3.2 1.3 4.8 0 3.2-1.3 4.8 0"/>',
            '#7896A0',
        ),
        '神秘探索',
        '层次、光影、未知感',
        '#EEF4F5',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="M18 30V14"/><path d="M18 19c-5.8 0-9.5-3.2-10-8 5.5-.5 9.5 2.3 10 8Z"/>'
            '<path d="M18 23c5.8 0 9.5-3.2 10-8-5.5-.5-9.5 2.3-10 8Z"/>',
            '#4D9360',
        ),
        '自然野趣',
        '原生、松弛、有呼吸',
        '#EFF8EA',
        '#F8FBF3',
    ),
    (
        _mood_icon_data_url(
            '<path d="m18 5 3.3 8.1 8.7.6-6.7 5.7 2.2 8.5-7.5-4.6-7.5 4.6 2.2-8.5L6 13.7l8.7-.6Z"/>',
            '#D69A39',
        ),
        '欢乐轻盈',
        '开阔、明快、低负担',
        '#FFF9E8',
        '#F8FBF3',
    ),
]


CHAT_MODE_CSS = '''
<style>
.chat-mode-bg {
    --chat-ink: #10251A;
    --chat-muted: rgba(16,37,26,.62);
    --chat-faint: rgba(16,37,26,.42);
    --chat-green: #2F7B58;
    background:
        radial-gradient(circle at 50% 4%, rgba(183,242,126,.18), transparent 30%),
        linear-gradient(180deg, rgba(255,255,248,.88) 0%, rgba(243,248,238,.96) 52%, rgba(232,240,227,.98) 100%),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.chat-mode-bg::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.06), transparent 26%),
        linear-gradient(90deg, rgba(47,123,88,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.04) 1px, transparent 1px) !important;
    background-size: auto, 34px 34px, 34px 34px !important;
    opacity: .46 !important;
}
.chat-shell {
    width: 100%;
    padding: 18px 20px 108px;
    gap: 18px;
}
.chat-main-column,
.chat-side-column {
    width: 100%;
    display: grid;
    gap: 18px;
}
.chat-source {
    position: relative;
    width: 100%;
    min-height: 0;
    overflow: hidden;
    border-radius: 24px;
    border: 1px solid rgba(31,72,50,.10);
    background: rgba(255,255,248,.58);
    box-shadow: 0 18px 38px rgba(38,70,52,.10);
    display: flex;
    align-items: center;
    justify-content: center;
}
.chat-source img {
    max-width: 100%;
    max-height: min(42vh, 380px);
    width: auto;
    height: auto;
    object-fit: contain;
    display: block;
}
.chat-source::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 58%, rgba(16,37,26,.28));
    pointer-events: none;
}
.chat-source-badge {
    position: absolute;
    left: 14px;
    bottom: 12px;
    z-index: 1;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(255,255,248,.76);
    color: var(--chat-ink);
    font-size: 11px;
    font-weight: 800;
    border: 1px solid rgba(255,255,248,.52);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}
.chat-empty-source {
    min-height: 86px;
    border-radius: 24px;
    border: 1px solid rgba(47,123,88,.14);
    background: linear-gradient(135deg, rgba(255,255,248,.72), rgba(236,246,232,.62));
    box-shadow: 0 18px 38px rgba(38,70,52,.08);
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 16px;
}
.chat-empty-orb {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    color: #F8FAF2;
    background: linear-gradient(135deg, #2F7B58, #7FA38D);
    box-shadow: 0 12px 26px rgba(47,123,88,.22);
    flex: 0 0 auto;
    font-size: 12px;
    font-weight: 900;
}
.chat-hero {
    gap: 7px;
}
.chat-kicker {
    color: var(--chat-green);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .08em;
}
.chat-title {
    color: var(--chat-ink);
    font-size: 29px;
    line-height: 1.14;
    font-weight: 900;
    letter-spacing: 0;
}
.chat-subtitle {
    color: var(--chat-muted);
    font-size: 14px;
    line-height: 1.65;
    font-weight: 500;
}
.chat-input-panel {
    position: relative;
    overflow: hidden;
    width: 100%;
    border-radius: 24px;
    padding: 16px;
    background:
        linear-gradient(180deg, rgba(255,255,248,.88), rgba(246,250,242,.68)),
        rgba(255,255,248,.74);
    border: 1px solid rgba(47,123,88,.16);
    box-shadow: 0 18px 42px rgba(38,70,52,.10);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
}
.chat-input-panel::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(90deg, rgba(47,123,88,.04) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.035) 1px, transparent 1px);
    background-size: 22px 22px;
    mask-image: linear-gradient(180deg, black, transparent 78%);
}
.chat-input-head {
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.chat-input-title {
    color: var(--chat-ink);
    font-size: 14px;
    font-weight: 900;
}
.chat-input-hint {
    color: var(--chat-faint);
    font-size: 11px;
    font-weight: 800;
    white-space: nowrap;
}
#chat-extra {
    position: relative;
    z-index: 1;
    width: 100%;
    min-height: 132px;
    resize: vertical;
    border: 1px solid rgba(47,123,88,.20);
    outline: none;
    border-radius: 20px;
    padding: 17px 18px;
    color: var(--chat-ink);
    background: rgba(255,255,248,.70);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.75);
    font: 700 15px/1.72 -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}
#chat-extra::placeholder {
    color: rgba(16,37,26,.34);
    font-weight: 650;
}
#chat-extra:focus {
    border-color: rgba(47,123,88,.48);
    background: rgba(255,255,248,.88);
    box-shadow: 0 0 0 4px rgba(47,123,88,.08), inset 0 1px 0 rgba(255,255,255,.86);
}
.chat-section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    margin-top: 2px;
}
.chat-section-title {
    color: var(--chat-ink);
    font-size: 16px;
    font-weight: 900;
}
.chat-section-meta {
    color: var(--chat-faint);
    font-size: 12px;
    font-weight: 800;
}
.mood-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    width: 100%;
}
.mood-card {
    position: relative;
    min-width: 0;
    min-height: 92px;
    padding: 14px 12px;
    border: 1px solid rgba(47,123,88,.12);
    border-radius: 18px;
    background: linear-gradient(135deg, var(--mood-start), var(--mood-end));
    box-shadow: 0 12px 28px rgba(38,70,52,.07);
    cursor: pointer;
    text-align: left;
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease, background .18s ease;
}
.mood-card:active {
    transform: scale(.985);
}
.mood-card.selected {
    border-color: rgba(47,123,88,.55);
    background: linear-gradient(135deg, rgba(236,255,212,.92), rgba(255,255,248,.88));
    box-shadow: 0 14px 30px rgba(47,123,88,.16), 0 0 0 3px rgba(47,123,88,.08);
}
.mood-check {
    position: absolute;
    right: 10px;
    top: 10px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    color: #F8FAF2;
    background: var(--chat-green);
    font-size: 12px;
    font-weight: 900;
    opacity: 0;
    transform: scale(.84);
    transition: all .18s ease;
}
.mood-card.selected .mood-check {
    opacity: 1;
    transform: scale(1);
}
.mood-inner {
    display: grid;
    grid-template-columns: 32px minmax(0, 1fr);
    gap: 11px;
    align-items: start;
}
.mood-icon {
    width: 30px;
    height: 30px;
}
.mood-title {
    display: block;
    color: var(--chat-ink);
    font-size: 14px;
    font-weight: 900;
    line-height: 1.28;
    margin-bottom: 5px;
}
.mood-desc {
    display: block;
    color: var(--chat-muted);
    font-size: 11.5px;
    font-weight: 600;
    line-height: 1.5;
}
.selected-tags-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    min-height: 28px;
}
.selected-tag {
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(47,123,88,.10);
    color: var(--chat-green);
    border: 1px solid rgba(47,123,88,.14);
    font-size: 12px;
    font-weight: 850;
}
.chat-error {
    display: none;
    width: 100%;
    padding: 11px 13px;
    border-radius: 16px;
    color: #B94336;
    background: rgba(255,123,110,.10);
    border: 1px solid rgba(255,123,110,.20);
    font-size: 13px;
    font-weight: 700;
    line-height: 1.45;
}
.chat-action-wrap {
    width: 100%;
    padding-top: 2px;
    margin-top: 6px;
    margin-bottom: 18px;
}
.chat-generate-btn {
    width: 100%;
    min-height: 54px;
    border: none;
    border-radius: 999px;
    color: #F8FAF2;
    background: linear-gradient(135deg, #2F7B58, #245F46 68%, #173126);
    box-shadow: 0 18px 34px rgba(47,123,88,.24), 0 0 0 1px rgba(255,255,248,.10) inset;
    cursor: pointer;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0;
    transition: transform .18s ease, box-shadow .18s ease, opacity .18s ease;
}
.chat-generate-btn:active {
    transform: translateY(1px) scale(.992);
}
.chat-generate-btn[disabled] {
    cursor: wait;
    opacity: .72;
}
.chat-loading {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 9px;
}
.chat-spinner {
    width: 17px;
    height: 17px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,248,.32);
    border-top-color: #F8FAF2;
    animation: chatSpin .76s linear infinite;
}
.ai-progress-panel {
    display: none;
    width: 100%;
    margin-bottom: 10px;
    padding: 12px 14px;
    border-radius: 18px;
    background: rgba(255,255,248,.82);
    border: 1px solid rgba(47,123,88,.14);
    box-shadow: 0 14px 28px rgba(38,70,52,.10);
}
.ai-progress-head {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: #173126;
    font-size: 12px;
    font-weight: 900;
}
.ai-progress-note {
    margin-top: 5px;
    color: rgba(23,49,38,.58);
    font-size: 11px;
    line-height: 1.45;
    font-weight: 700;
}
.ai-progress-track {
    overflow: hidden;
    height: 8px;
    margin-top: 10px;
    border-radius: 999px;
    background: rgba(47,123,88,.13);
}
.ai-progress-fill {
    width: var(--progress, 0%);
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #2F7B58, #B7F27E);
    transition: width .42s ease;
}
@keyframes chatSpin {
    to { transform: rotate(360deg); }
}
@media (min-width: 900px) and (orientation: landscape) {
    .chat-shell {
        display: grid !important;
        grid-template-columns: minmax(390px, .92fr) minmax(470px, 1.08fr);
        gap: 22px 24px;
        align-items: start !important;
        padding: 24px 34px 124px;
    }

    .chat-main-column {
        position: sticky;
        top: 92px;
        gap: 16px;
    }

    .chat-side-column {
        gap: 10px;
    }

    .chat-source {
        border-radius: 24px;
    }

    .chat-source img {
        max-height: min(44vh, 420px);
    }

    .chat-empty-source {
        min-height: 170px;
    }

    .chat-title {
        font-size: 34px;
    }

    #chat-extra {
        min-height: 104px;
    }

    .mood-grid {
        gap: 10px;
    }

    .mood-card {
        min-height: 76px;
        padding: 11px 12px;
        border-radius: 20px;
    }

    .chat-action-wrap {
        margin-top: 4px;
        margin-bottom: 12px;
    }
}
@media (max-width: 360px) {
    .chat-shell { padding-left: 16px; padding-right: 16px; }
    .chat-title { font-size: 26px; }
    .mood-grid { gap: 8px; }
    .mood-card { padding: 13px 10px; }
}
</style>
'''


def _image_url(session) -> str:
    return media_url(getattr(session, 'uploaded_image_path', '') if session else '', display=True)


def _build_mood_grid() -> str:
    cards = []
    for icon_url, label, desc, start, end in MOOD_CARDS:
        cards.append(
            '<button type="button" class="mood-card" '
            f'data-mood="{label}" style="--mood-start:{start};--mood-end:{end}">'
            '<span class="mood-check">✓</span>'
            '<span class="mood-inner">'
            f'<img class="mood-icon" src="{icon_url}" alt="{label}">'
            '<span>'
            f'<span class="mood-title">{label}</span>'
            f'<span class="mood-desc">{desc}</span>'
            '</span>'
            '</span>'
            '</button>'
        )
    return '<div id="mood-grid" class="mood-grid">' + ''.join(cards) + '</div>'


def _build_chat_html(sid: str, img_url: str) -> str:
    preview = (
        '<div class="chat-source">'
        f'<img src="{img_url}" alt="原始场景">'
        '<div class="chat-source-badge">原始场景</div>'
        '</div>'
        if img_url
        else (
            '<div class="chat-empty-source">'
            '<div class="chat-empty-orb">AI</div>'
            '<div>'
            '<div class="chat-input-title">等待原始图片</div>'
            '<div class="chat-subtitle" style="font-size:12.5px;line-height:1.55;">'
            '上传图片后，系统会基于这段感受改造同一处空间。</div>'
            '</div>'
            '</div>'
        )
    )
    mood_grid = _build_mood_grid()
    return f'''
<div class="chat-shell nicegui-column">
    <div class="chat-main-column">
        {preview}
        <div class="chat-hero nicegui-column">
            <div class="chat-kicker">AI SPACE INTENT</div>
            <div class="chat-title">你希望这里带给你什么感受？</div>
            <div class="chat-subtitle">可以只写一句感觉，也可以叠加最多两个情绪标签，系统会把它们转译成空间光影、绿化和材质语言。</div>
        </div>
    </div>

    <div class="chat-side-column">
        <div class="chat-input-panel">
            <div class="chat-input-head">
                <div class="chat-input-title">输入你的感受</div>
                <div class="chat-input-hint">文字优先理解</div>
            </div>
            <textarea id="chat-extra" maxlength="220" placeholder="例如：希望这里安静一点，有清透的空气、柔和的光，不要太拥挤。"></textarea>
        </div>

        <div class="chat-section-head">
            <div class="chat-section-title">情绪标签</div>
            <div class="chat-section-meta">可选 · 最多 2 个</div>
        </div>
        {mood_grid}
        <div id="selected-tags-row" class="selected-tags-row"></div>
        <div id="chat-error" class="chat-error"></div>

        <div class="chat-action-wrap">
            <div id="chat-progress" class="ai-progress-panel" style="--progress:0%">
                <div class="ai-progress-head">
                    <span>AI 正在生成</span>
                    <span id="chat-progress-value">0%</span>
                </div>
                <div class="ai-progress-note" id="chat-progress-note">AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。</div>
                <div class="ai-progress-track"><div class="ai-progress-fill"></div></div>
            </div>
            <button id="chat-generate-btn" type="button" class="chat-generate-btn">
                <span class="chat-ready">生成我的空间</span>
                <span class="chat-loading"><span class="chat-spinner"></span>正在生成</span>
            </button>
        </div>
    </div>
</div>
'''


def _build_chat_script(sid: str) -> str:
    sid_json = json.dumps(sid, ensure_ascii=False)
    return f'''
<script>
(function() {{
    var sid = {sid_json};
    var selected = [];
    var maxTags = 2;
    var initAttempts = 0;
    var progressTimer = null;
    var progressValue = 0;

    function setError(message) {{
        var errorBox = document.getElementById('chat-error');
        if (!errorBox) return;
        errorBox.textContent = message || '';
        errorBox.style.display = message ? 'block' : 'none';
    }}

    function setProgress(value) {{
        progressValue = Math.max(0, Math.min(100, Math.round(value)));
        var panel = document.getElementById('chat-progress');
        var label = document.getElementById('chat-progress-value');
        if (panel) {{
            panel.style.setProperty('--progress', progressValue + '%');
            panel.style.display = 'block';
        }}
        if (label) label.textContent = progressValue + '%';
    }}

    function startProgress() {{
        if (progressTimer) clearInterval(progressTimer);
        setProgress(8);
        progressTimer = setInterval(function() {{
            var next = progressValue + Math.max(1, Math.round((92 - progressValue) * 0.07));
            setProgress(Math.min(92, next));
        }}, 760);
    }}

    function finishProgress() {{
        if (progressTimer) clearInterval(progressTimer);
        progressTimer = null;
        setProgress(100);
    }}

    function resetProgress() {{
        if (progressTimer) clearInterval(progressTimer);
        progressTimer = null;
        progressValue = 0;
        var panel = document.getElementById('chat-progress');
        if (panel) {{
            panel.style.setProperty('--progress', '0%');
            panel.style.display = 'none';
        }}
        var label = document.getElementById('chat-progress-value');
        if (label) label.textContent = '0%';
    }}

    function renderTags() {{
        var tagsRow = document.getElementById('selected-tags-row');
        if (!tagsRow) return;
        tagsRow.innerHTML = selected.map(function(tag) {{
            return '<span class="selected-tag">' + tag + '</span>';
        }}).join('');
    }}

    function initChatMode() {{
        initAttempts += 1;
        var button = document.getElementById('chat-generate-btn');
        var cards = document.querySelectorAll('.mood-card');
        if (!button || !cards.length) {{
            if (initAttempts < 60) setTimeout(initChatMode, 100);
            return;
        }}

        cards.forEach(function(card) {{
            if (card.dataset.chatBound === '1') return;
            card.dataset.chatBound = '1';
            card.addEventListener('click', function() {{
                var mood = card.dataset.mood;
                var idx = selected.indexOf(mood);
                setError('');
                if (idx >= 0) {{
                    selected.splice(idx, 1);
                    card.classList.remove('selected');
                }} else {{
                    if (selected.length >= maxTags) {{
                        var removed = selected.shift();
                        var oldCard = document.querySelector('.mood-card[data-mood="' + removed + '"]');
                        if (oldCard) oldCard.classList.remove('selected');
                    }}
                    selected.push(mood);
                    card.classList.add('selected');
                }}
                renderTags();
            }});
        }});

        if (button.dataset.chatBound !== '1') {{
        button.dataset.chatBound = '1';
        button.addEventListener('click', async function() {{
            var textEl = document.getElementById('chat-extra');
            var extraText = textEl ? textEl.value.trim() : '';
            if (!extraText && selected.length === 0) {{
                setError('请先输入一种感受，或选择至少一个情绪标签。');
                return;
            }}
            if (!sid) {{
                setError('请先上传图片，再进入对话改造。');
                return;
            }}
            setError('');
            button.disabled = true;
            button.querySelector('.chat-ready').style.display = 'none';
            button.querySelector('.chat-loading').style.display = 'inline-flex';
            startProgress();
            try {{
                var resp = await fetch('/api/generate/chat/background', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        session_id: sid,
                        mood_tags: selected,
                        extra_text: extraText
                    }})
                }});
                var data = await resp.json().catch(function() {{ return {{}}; }});
                if (!resp.ok || data.error) {{
                    throw new Error(data.error || '生成失败，请稍后再试。');
                }}
                if (progressTimer) clearInterval(progressTimer);
                progressTimer = null;
                setProgress(36);
                var note = document.getElementById('chat-progress-note');
                if (note) note.textContent = 'AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。';
                button.disabled = false;
                button.querySelector('.chat-ready').textContent = '后台生成中';
                button.querySelector('.chat-ready').style.display = 'inline';
                button.querySelector('.chat-loading').style.display = 'none';
            }} catch (err) {{
                setError(err && err.message ? err.message : '生成失败，请稍后再试。');
                button.disabled = false;
                button.querySelector('.chat-ready').style.display = 'inline';
                button.querySelector('.chat-loading').style.display = 'none';
                resetProgress();
            }}
        }});
        }}
    }}

    initChatMode();
}})();
</script>
'''


def create_chat_mode_page():
    @ui.page('/chat-mode')
    async def chat_mode_page(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(CHAT_MODE_CSS)

        session = get_session(sid) if sid else None

        img_url = _image_url(session)
        back_url = f'/result?sid={sid}&back=records' if back == 'result' else (
            '/records' if back == 'records' else f'/mode-select?sid={sid}'
        )

        with ui.column().classes('mobile-page light-page chat-mode-bg').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(back_url)).props('flat round dense').style(
                    'color:#2F7B58'
                )
                ui.label('对话改造').style('font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126')

            ui.html(_build_chat_html(sid, img_url), sanitize=False).style('width:100%')
            ui.add_body_html(_build_chat_script(sid))
