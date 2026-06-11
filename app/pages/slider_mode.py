"""参数调节页面：合并智能推荐与手动滑杆。"""
from __future__ import annotations

import json

from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session, media_url
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


PRESETS = [
    {
        'id': 'natural_harmony',
        'icon': '●',
        'name': '自然和谐方案',
        'summary': '中等绿化 + 低人造元素，模拟自然公园环境，最大化注意力恢复效果。',
        'green': 55,
        'urban': 25,
        'vitality': 40,
        'light': 62,
        'evidence': '注意力恢复理论：自然环境通过柔性注意力促进认知恢复。',
        'accent': '#2F7B58',
    },
    {
        'id': 'urban_vitality',
        'icon': '▥',
        'name': '活力都市方案',
        'summary': '中等绿化 + 中等人造元素 + 适度活力，适合城市街区更新。',
        'green': 45,
        'urban': 50,
        'vitality': 55,
        'light': 64,
        'evidence': '倒 U 型效应：适度复杂度更可能优于极简或极繁环境。',
        'accent': '#D7B46A',
    },
    {
        'id': 'quiet_zen',
        'icon': '◌',
        'name': '宁静禅意方案',
        'summary': '高绿化 + 低活力 + 柔和冷光，营造安静、内聚、低干扰的恢复场。',
        'green': 72,
        'urban': 18,
        'vitality': 24,
        'light': 44,
        'evidence': '低刺激场景有助于降低认知负荷，适合放松和独处。',
        'accent': '#7FA38D',
    },
    {
        'id': 'sunlit_healing',
        'icon': '✦',
        'name': '暖光疗愈方案',
        'summary': '较高绿化 + 柔暖光照 + 温和活力，提升亲近感和安全感。',
        'green': 64,
        'urban': 34,
        'vitality': 42,
        'light': 78,
        'evidence': '温暖光线与自然材质共同强化舒适、亲和的空间体验。',
        'accent': '#C98252',
    },
]

SLIDERS = [
    {
        'key': 'green',
        'api': 'green_level',
        'name': '绿化程度',
        'icon': '●',
        'low': '低',
        'mid': '中',
        'high': '高',
        'desc': '树木、灌木、草坪与自然覆盖度',
        'accent': '#2F7B58',
    },
    {
        'key': 'urban',
        'api': 'urban_level',
        'name': '人造元素',
        'icon': '▥',
        'low': '自然',
        'mid': '适度',
        'high': '设施',
        'desc': '座椅、路灯、铺装、公共设施强度',
        'accent': '#9A6F5F',
    },
    {
        'key': 'vitality',
        'api': 'vitality_level',
        'name': '环境活力',
        'icon': '✣',
        'low': '宁静',
        'mid': '适度',
        'high': '热闹',
        'desc': '开放感、活动感、人与空间的互动强度',
        'accent': '#7896A0',
    },
    {
        'key': 'light',
        'api': 'light_warmth',
        'name': '光线温度',
        'icon': '☉',
        'low': '清冷',
        'mid': '自然',
        'high': '温暖',
        'desc': '光照明暗、冷暖色调与空气透明度',
        'accent': '#D7B46A',
    },
]


SLIDER_CSS = '''
<style>
.slider-mode-bg {
    --panel-ink: #10251A;
    --panel-muted: rgba(16,37,26,.62);
    --panel-faint: rgba(16,37,26,.40);
    --panel-green: #2F7B58;
    background:
        radial-gradient(circle at 50% 4%, rgba(183,242,126,.18), transparent 30%),
        linear-gradient(180deg, rgba(255,255,248,.88), rgba(243,248,238,.96) 52%, rgba(232,240,227,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.slider-mode-bg::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.06), transparent 28%),
        linear-gradient(90deg, rgba(47,123,88,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.04) 1px, transparent 1px) !important;
    background-size: auto, 34px 34px, 34px 34px !important;
    opacity: .46 !important;
}
.param-shell {
    width: 100%;
    padding: 14px 18px 108px;
    gap: 14px;
    align-items: stretch !important;
}
.param-left-stack,
.param-control-stack {
    width: 100%;
    display: grid;
    gap: 14px;
}
.param-source {
    position: relative;
    width: 100%;
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(47,123,88,.13);
    background: rgba(255,255,248,.64);
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
    display: flex;
    align-items: center;
    justify-content: center;
}
.param-source img {
    max-width: 100%;
    max-height: min(34vh, 260px);
    width: auto;
    height: auto;
    display: block;
    object-fit: contain;
}
.param-source-badge {
    position: absolute;
    left: 12px;
    bottom: 10px;
    padding: 6px 10px;
    border-radius: 999px;
    color: var(--panel-ink);
    background: rgba(255,255,248,.78);
    border: 1px solid rgba(255,255,248,.55);
    font-size: 11px;
    font-weight: 850;
}
.param-hero {
    position: relative;
    overflow: hidden;
    width: 100%;
    border-radius: 26px;
    padding: 16px;
    background:
        linear-gradient(145deg, rgba(255,255,248,.82), rgba(235,245,231,.68)),
        rgba(255,255,248,.72);
    border: 1px solid rgba(47,123,88,.14);
    box-shadow: 0 18px 42px rgba(38,70,52,.10);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
}
.param-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(47,123,88,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.04) 1px, transparent 1px);
    background-size: 26px 26px;
    mask-image: linear-gradient(180deg, black, transparent 78%);
    pointer-events: none;
}
.param-hero-content {
    position: relative;
    z-index: 1;
}
.param-kicker {
    color: var(--panel-green);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .08em;
}
.param-title {
    margin-top: 7px;
    color: var(--panel-ink);
    font-size: 24px;
    line-height: 1.15;
    font-weight: 900;
    letter-spacing: 0;
}
.param-subtitle {
    margin-top: 9px;
    color: var(--panel-muted);
    font-size: 13px;
    line-height: 1.62;
    font-weight: 600;
}
.section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
}
.section-title {
    color: var(--panel-ink);
    font-size: 17px;
    font-weight: 950;
}
.section-meta {
    color: var(--panel-faint);
    font-size: 12px;
    font-weight: 850;
}
.preset-strip {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
    width: 100%;
}
.preset-card {
    position: relative;
    width: 100%;
    min-height: 118px;
    padding: 13px;
    border-radius: 18px;
    border: 1px solid rgba(47,123,88,.13);
    background: linear-gradient(180deg, rgba(255,255,248,.86), rgba(247,250,242,.70));
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
    text-align: left;
    cursor: pointer;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.preset-card:active {
    transform: scale(.99);
}
.preset-card.selected {
    border-color: color-mix(in srgb, var(--preset-accent), transparent 24%);
    box-shadow: 0 18px 38px rgba(47,123,88,.14), 0 0 0 3px rgba(47,123,88,.07);
}
.preset-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
    background: linear-gradient(90deg, var(--preset-accent), rgba(183,242,126,.72));
}
.preset-top {
    display: flex;
    gap: 9px;
    align-items: center;
}
.preset-icon {
    width: 28px;
    height: 28px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    color: #F8FAF2;
    background: var(--preset-accent);
    box-shadow: 0 12px 24px color-mix(in srgb, var(--preset-accent), transparent 72%);
    font-weight: 900;
}
.preset-name {
    color: var(--panel-ink);
    font-size: 13.5px;
    font-weight: 950;
    line-height: 1.28;
}
.preset-summary {
    margin-top: 9px;
    color: var(--panel-muted);
    font-size: 11.5px;
    line-height: 1.5;
    font-weight: 650;
}
.preset-evidence {
    margin-top: 8px;
    color: rgba(16,37,26,.48);
    font-size: 10.5px;
    line-height: 1.45;
    font-weight: 650;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.control-grid {
    display: grid;
    gap: 9px;
    width: 100%;
}
.control-card {
    position: relative;
    overflow: hidden;
    width: 100%;
    border-radius: 18px;
    padding: 12px 13px;
    border: 1px solid rgba(47,123,88,.13);
    background:
        linear-gradient(180deg, rgba(255,255,248,.86), rgba(247,250,242,.70)),
        rgba(255,255,248,.70);
    box-shadow: 0 14px 30px rgba(38,70,52,.075);
}
.control-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.control-title {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--panel-ink);
    font-size: 14px;
    font-weight: 950;
}
.control-icon {
    width: 24px;
    height: 24px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    color: #F8FAF2;
    background: var(--slider-accent);
    font-size: 13px;
    font-weight: 900;
}
.control-value {
    color: var(--slider-accent);
    font-size: 17px;
    font-weight: 950;
}
.control-desc {
    margin-top: 5px;
    color: var(--panel-faint);
    font-size: 10.5px;
    font-weight: 700;
}
.range-wrap {
    position: relative;
    padding-top: 12px;
}
.param-range {
    width: 100%;
    appearance: none;
    height: 6px;
    border-radius: 999px;
    outline: none;
    background: linear-gradient(90deg, var(--slider-accent) var(--value), rgba(16,37,26,.14) var(--value));
}
.param-range::-webkit-slider-thumb {
    appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #F8FAF2;
    border: 7px solid var(--slider-accent);
    box-shadow: 0 8px 18px rgba(38,70,52,.18);
    cursor: pointer;
}
.param-range::-moz-range-thumb {
    width: 24px;
    height: 24px;
    border: 7px solid var(--slider-accent);
    border-radius: 50%;
    background: #F8FAF2;
    box-shadow: 0 8px 18px rgba(38,70,52,.18);
    cursor: pointer;
}
.range-scale {
    display: flex;
    justify-content: space-between;
    margin-top: 9px;
    color: rgba(16,37,26,.38);
    font-size: 11.5px;
    font-weight: 800;
}
.generate-panel {
    position: sticky;
    bottom: 92px;
    z-index: 42;
    width: 100%;
}
.generate-btn {
    width: 100%;
    min-height: 54px;
    border: none;
    border-radius: 999px;
    color: #F8FAF2;
    background: linear-gradient(135deg, #2F7B58, #245F46 68%, #173126);
    box-shadow: 0 18px 34px rgba(47,123,88,.24), 0 0 0 1px rgba(255,255,248,.10) inset;
    cursor: pointer;
    font-size: 15px;
    font-weight: 950;
}
.generate-btn[disabled] {
    cursor: wait;
    opacity: .72;
}
.generate-loading {
    display: none;
    align-items: center;
    justify-content: center;
    gap: 9px;
}
.generate-spinner {
    width: 17px;
    height: 17px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,248,.32);
    border-top-color: #F8FAF2;
    animation: paramSpin .76s linear infinite;
}
.param-error {
    display: none;
    width: 100%;
    margin-bottom: 10px;
    padding: 11px 13px;
    border-radius: 16px;
    color: #B94336;
    background: rgba(255,123,110,.10);
    border: 1px solid rgba(255,123,110,.20);
    font-size: 13px;
    font-weight: 700;
    line-height: 1.45;
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
    position: relative;
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
@keyframes paramSpin {
    to { transform: rotate(360deg); }
}
@media (min-width: 900px) and (orientation: landscape) {
    .param-shell {
        display: grid !important;
        grid-template-columns: minmax(360px, .9fr) minmax(440px, 1.1fr);
        grid-template-areas:
            "left controls"
            "generate generate";
        gap: 20px 24px;
        align-items: start !important;
        padding: 24px 34px 124px;
    }

    .param-left-stack {
        grid-area: left;
        position: sticky;
        top: 92px;
    }

    .param-control-stack {
        grid-area: controls;
    }

    .param-hero {
        padding: 22px;
        border-radius: 24px;
    }

    .param-title {
        font-size: 32px;
    }

    .preset-strip,
    .control-grid {
        gap: 12px;
    }

    .preset-card {
        min-height: 118px;
        border-radius: 20px;
        padding: 14px;
    }

    .param-source img {
        max-height: min(34vh, 280px);
    }

    .control-card {
        border-radius: 20px;
        padding: 16px;
    }

    .control-desc {
        font-size: 11.5px;
    }

    .generate-panel {
        grid-area: generate;
        position: sticky;
        bottom: 98px;
        justify-self: center;
        width: min(760px, 100%);
    }
}
@media (max-width: 360px) {
    .param-shell { padding-left: 16px; padding-right: 16px; }
    .param-title { font-size: 22px; }
    .preset-strip { grid-template-columns: 1fr; }
}
</style>
'''


def _clamp(value: float | int | None) -> int:
    try:
        numeric = int(round(float(value)))
    except (TypeError, ValueError):
        numeric = 50
    return max(0, min(100, numeric))


def _initial_values(session) -> dict[str, int]:
    return {
        'green': _clamp(getattr(session, 'green_level', 50) if session else 50),
        'urban': _clamp(getattr(session, 'urban_level', 50) if session else 50),
        'vitality': _clamp(getattr(session, 'vitality_level', 50) if session else 50),
        'light': _clamp(getattr(session, 'light_warmth', 50) if session else 50),
    }


def _image_url(session) -> str:
    return media_url(getattr(session, 'uploaded_image_path', '') if session else '')


def _build_preset_html() -> str:
    cards = []
    for preset in PRESETS:
        cards.append(
            '<button type="button" class="preset-card" '
            f'data-preset="{preset["id"]}" style="--preset-accent:{preset["accent"]}">'
            '<div class="preset-top">'
            f'<div class="preset-icon">{preset["icon"]}</div>'
            f'<div class="preset-name">{preset["name"]}</div>'
            '</div>'
            f'<div class="preset-summary">{preset["summary"]}</div>'
            '</button>'
        )
    return '<div class="preset-strip" id="preset-strip">' + ''.join(cards) + '</div>'


def _build_controls_html(values: dict[str, int]) -> str:
    controls = []
    for item in SLIDERS:
        value = values[item['key']]
        controls.append(
            '<div class="control-card" style="--slider-accent:{accent}">'.format(accent=item['accent'])
            + '<div class="control-top">'
            + '<div>'
            + f'<div class="control-title"><span class="control-icon">{item["icon"]}</span>{item["name"]}</div>'
            + f'<div class="control-desc">{item["desc"]}</div>'
            + '</div>'
            + f'<div class="control-value" id="{item["key"]}-value">{value}%</div>'
            + '</div>'
            + '<div class="range-wrap">'
            + f'<input class="param-range" id="{item["key"]}-range" data-key="{item["key"]}" '
            + f'type="range" min="0" max="100" value="{value}" style="--value:{value}%">'
            + f'<div class="range-scale"><span>{item["low"]}</span><span>{item["mid"]}</span><span>{item["high"]}</span></div>'
            + '</div>'
            + '</div>'
        )
    return '<div class="control-grid">' + ''.join(controls) + '</div>'


def _build_page_html(values: dict[str, int], img_url: str = '') -> str:
    preview = (
        '<section class="param-source">'
        f'<img src="{img_url}" alt="原始场景">'
        '<div class="param-source-badge">原始场景</div>'
        '</section>'
        if img_url else ''
    )
    return f'''
<div class="param-shell nicegui-column">
    <div class="param-left-stack">
        {preview}
        <section class="param-hero">
            <div class="param-hero-content">
                <div>
                    <div class="param-kicker">AI PARAMETER CONSOLE</div>
                    <div class="param-title">智能参数</div>
                    <div class="param-subtitle">选择推荐预设会自动调整下方滑杆；你也可以直接拖动滑杆微调。</div>
                </div>
            </div>
        </section>

        <div class="section-head">
            <div class="section-title">推荐预设</div>
            <div class="section-meta">点击套用</div>
        </div>
        {_build_preset_html()}
    </div>

    <div class="param-control-stack">
        <div class="section-head">
            <div class="section-title">调节环境参数</div>
            <div class="section-meta">生成前可继续微调</div>
        </div>
        {_build_controls_html(values)}
    </div>

    <div class="generate-panel">
        <div id="param-error" class="param-error"></div>
        <div id="slider-progress" class="ai-progress-panel" style="--progress:0%">
            <div class="ai-progress-head">
                <span>AI 正在生成</span>
                <span id="slider-progress-value">0%</span>
            </div>
            <div class="ai-progress-note" id="slider-progress-note">AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。</div>
            <div class="ai-progress-track"><div class="ai-progress-fill"></div></div>
        </div>
        <button id="generate-slider-btn" type="button" class="generate-btn">
            <span class="generate-ready">生成改造方案</span>
            <span class="generate-loading"><span class="generate-spinner"></span>正在生成</span>
        </button>
    </div>
</div>
'''


def _build_script(sid: str, values: dict[str, int]) -> str:
    presets_json = json.dumps(PRESETS, ensure_ascii=False)
    values_json = json.dumps(values, ensure_ascii=False)
    sid_json = json.dumps(sid, ensure_ascii=False)
    return f'''
<script>
(function() {{
    var sid = {sid_json};
    var presets = {presets_json};
    var values = {values_json};
    var selectedPreset = '';
    var initAttempts = 0;
    var progressTimer = null;
    var progressValue = 0;

    function clamp(value) {{
        value = Math.round(Number(value) || 0);
        return Math.max(0, Math.min(100, value));
    }}

    function setError(message) {{
        var box = document.getElementById('param-error');
        if (!box) return;
        box.textContent = message || '';
        box.style.display = message ? 'block' : 'none';
    }}

    function setProgress(value) {{
        progressValue = Math.max(0, Math.min(100, Math.round(value)));
        var panel = document.getElementById('slider-progress');
        var label = document.getElementById('slider-progress-value');
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
        var panel = document.getElementById('slider-progress');
        if (panel) {{
            panel.style.setProperty('--progress', '0%');
            panel.style.display = 'none';
        }}
        var label = document.getElementById('slider-progress-value');
        if (label) label.textContent = '0%';
    }}

    function updateRange(key, value) {{
        value = clamp(value);
        values[key] = value;
        var input = document.getElementById(key + '-range');
        var label = document.getElementById(key + '-value');
        if (input) {{
            input.value = String(value);
            input.style.setProperty('--value', value + '%');
        }}
        if (label) label.textContent = value + '%';
    }}

    function updateRadar() {{
        var avg = Math.round((values.green + values.urban + values.vitality + values.light) / 4);
        var el = document.getElementById('radar-value');
        if (el) el.textContent = String(avg);
    }}

    function syncAll() {{
        ['green', 'urban', 'vitality', 'light'].forEach(function(key) {{
            updateRange(key, values[key]);
        }});
        updateRadar();
    }}

    function markPreset(id) {{
        selectedPreset = id || '';
        document.querySelectorAll('.preset-card').forEach(function(card) {{
            card.classList.toggle('selected', card.dataset.preset === selectedPreset);
        }});
    }}

    function initSliderPage() {{
        initAttempts += 1;
        var button = document.getElementById('generate-slider-btn');
        var ranges = document.querySelectorAll('.param-range');
        var presetCards = document.querySelectorAll('.preset-card');
        if (!button || !ranges.length || !presetCards.length) {{
            if (initAttempts < 60) setTimeout(initSliderPage, 100);
            return;
        }}

        ranges.forEach(function(input) {{
            if (input.dataset.paramBound === '1') return;
            input.dataset.paramBound = '1';
            input.addEventListener('input', function() {{
                markPreset('');
                updateRange(input.dataset.key, input.value);
                updateRadar();
                setError('');
            }});
        }});

        presetCards.forEach(function(card) {{
            if (card.dataset.paramBound === '1') return;
            card.dataset.paramBound = '1';
            card.addEventListener('click', function() {{
                var preset = presets.find(function(item) {{ return item.id === card.dataset.preset; }});
                if (!preset) return;
                values.green = preset.green;
                values.urban = preset.urban;
                values.vitality = preset.vitality;
                values.light = preset.light;
                syncAll();
                markPreset(preset.id);
                setError('');
            }});
        }});

        if (button.dataset.paramBound !== '1') {{
        button.dataset.paramBound = '1';
        button.addEventListener('click', async function() {{
            if (!sid) {{
                setError('请先上传图片，再进入参数调节。');
                return;
            }}
            setError('');
            button.disabled = true;
            button.querySelector('.generate-ready').style.display = 'none';
            button.querySelector('.generate-loading').style.display = 'inline-flex';
            startProgress();
            try {{
                var preset = presets.find(function(item) {{ return item.id === selectedPreset; }});
                var resp = await fetch('/api/generate/slider/background', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        session_id: sid,
                        green_level: values.green,
                        urban_level: values.urban,
                        vitality_level: values.vitality,
                        light_warmth: values.light,
                        selected_recommend: preset ? preset.name : ''
                    }})
                }});
                var data = await resp.json().catch(function() {{ return {{}}; }});
                if (!resp.ok || data.error) {{
                    throw new Error(data.error || '生成失败，请稍后再试。');
                }}
                if (progressTimer) clearInterval(progressTimer);
                progressTimer = null;
                setProgress(36);
                var note = document.getElementById('slider-progress-note');
                if (note) note.textContent = 'AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。';
                button.disabled = false;
                button.querySelector('.generate-ready').textContent = '后台生成中';
                button.querySelector('.generate-ready').style.display = 'inline';
                button.querySelector('.generate-loading').style.display = 'none';
            }} catch (err) {{
                setError(err && err.message ? err.message : '生成失败，请稍后再试。');
                button.disabled = false;
                button.querySelector('.generate-ready').style.display = 'inline';
                button.querySelector('.generate-loading').style.display = 'none';
                resetProgress();
            }}
        }});
        }}

        syncAll();
    }}

    initSliderPage();
}})();
</script>
'''


def create_slider_page():
    @ui.page('/slider-mode')
    async def slider_page(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(SLIDER_CSS)

        session = get_session(sid) if sid else None

        values = _initial_values(session)
        img_url = _image_url(session)
        back_url = f'/result?sid={sid}&back=records' if back == 'result' else (
            '/records' if back == 'records' else f'/mode-select?sid={sid}'
        )

        with ui.column().classes('mobile-page light-page slider-mode-bg').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(back_url)).props('flat round dense').style(
                    'color:#2F7B58'
                )
                ui.label('参数调节').style('font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126')

            ui.html(_build_page_html(values, img_url), sanitize=False).style('width:100%')
            ui.add_body_html(_build_script(sid, values))
