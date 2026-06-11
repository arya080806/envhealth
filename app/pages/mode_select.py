"""模式选择页面。"""
from __future__ import annotations

from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session, media_url
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


MODE_SELECT_CSS = '''
<style>
.mode-select-bg {
    --mode-ink: #10251A;
    --mode-muted: rgba(16,37,26,.62);
    --mode-faint: rgba(16,37,26,.38);
    --mode-green: #2F7B58;
    background:
        radial-gradient(circle at 50% 4%, rgba(183,242,126,.16), transparent 30%),
        linear-gradient(180deg, rgba(255,255,248,.88), rgba(243,248,238,.96) 52%, rgba(232,240,227,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.mode-select-bg::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.055), transparent 26%),
        linear-gradient(90deg, rgba(47,123,88,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.04) 1px, transparent 1px) !important;
    background-size: auto, 34px 34px, 34px 34px !important;
    opacity: .46 !important;
}
.mode-shell {
    width: 100%;
    padding: 18px 20px 108px;
    gap: 18px;
    align-items: stretch !important;
}
.mode-image-preview {
    width: 100%;
    aspect-ratio: 1.82;
    overflow: hidden;
    border-radius: 24px;
    border: 1px solid rgba(47,123,88,.13);
    box-shadow: 0 16px 34px rgba(38,70,52,.10);
    background: rgba(255,255,248,.50);
}
.mode-image-preview img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.mode-hero {
    gap: 7px;
}
.mode-content-stack {
    width: 100%;
    display: grid;
    gap: 18px;
}
.mode-kicker {
    color: var(--mode-green);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .08em;
}
.mode-title {
    color: var(--mode-ink);
    font-size: 28px;
    line-height: 1.15;
    font-weight: 950;
}
.mode-copy {
    color: var(--mode-muted);
    font-size: 13px;
    line-height: 1.62;
    font-weight: 600;
}
.mode-section {
    width: 100%;
    display: grid;
    gap: 10px;
}
.mode-section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--mode-ink);
    font-size: 17px;
    font-weight: 950;
}
.mode-section-head::before {
    content: "";
    width: 34px;
    height: 2px;
    border-radius: 999px;
    background: rgba(47,123,88,.64);
}
.mode-card-link {
    width: 100%;
    min-height: 82px;
    border: 1px solid rgba(47,123,88,.12);
    border-radius: 24px;
    background: linear-gradient(180deg, rgba(255,255,248,.88), rgba(247,250,242,.72));
    box-shadow: 0 14px 30px rgba(38,70,52,.075);
    display: grid;
    grid-template-columns: 62px minmax(0,1fr) 24px;
    align-items: center;
    gap: 14px;
    padding: 16px;
    cursor: pointer;
    text-align: left;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.mode-card-link:active {
    transform: scale(.992);
}
.mode-card-link:hover {
    border-color: rgba(47,123,88,.24);
    box-shadow: 0 18px 34px rgba(38,70,52,.10);
}
.mode-index {
    width: 48px;
    height: 48px;
    border-radius: 18px;
    display: grid;
    place-items: center;
    color: var(--mode-green);
    background: rgba(47,123,88,.10);
    border: 1px solid rgba(47,123,88,.16);
    font-size: 15px;
    font-weight: 950;
}
.mode-card-title {
    color: var(--mode-ink);
    font-size: 18px;
    line-height: 1.25;
    font-weight: 950;
}
.mode-chevron {
    color: var(--mode-green);
    font-size: 26px;
    line-height: 1;
}
.mode-note {
    width: 100%;
    padding: 14px 16px;
    border-radius: 20px;
    color: var(--mode-muted);
    background: rgba(255,255,248,.58);
    border: 1px solid rgba(47,123,88,.10);
    font-size: 12px;
    line-height: 1.6;
    font-weight: 650;
}
@media (min-width: 900px) and (orientation: landscape) {
    .mode-shell {
        display: grid !important;
        grid-template-columns: minmax(380px, .95fr) minmax(430px, 1.05fr);
        grid-template-areas:
            "image content"
            "note content";
        gap: 18px 24px;
        align-items: center !important;
        padding: 24px 34px 122px;
    }

    .mode-select-bg:not(:has(.mode-image-preview)) .mode-shell {
        grid-template-columns: minmax(360px, .78fr) minmax(430px, 1fr);
        grid-template-areas:
            "content content";
    }

    .mode-image-preview {
        grid-area: image;
        aspect-ratio: 4 / 3;
        border-radius: 24px;
        position: sticky;
        top: 92px;
    }

    .mode-content-stack {
        grid-area: content;
        align-self: center;
        gap: 22px;
    }

    .mode-hero {
        padding-top: 0;
    }

    .mode-title {
        font-size: 36px;
    }

    .mode-copy {
        max-width: 54ch;
    }

    .mode-section {
        gap: 12px;
    }

    .mode-card-link {
        min-height: 78px;
        border-radius: 20px;
        grid-template-columns: 58px minmax(0,1fr) 24px;
        padding: 14px 18px;
    }

    .mode-note {
        grid-area: note;
        border-radius: 18px;
    }
}
@media (max-width: 360px) {
    .mode-shell { padding-left: 16px; padding-right: 16px; }
    .mode-title { font-size: 25px; }
    .mode-card-link { grid-template-columns: 56px minmax(0,1fr) 20px; padding: 14px; }
}
</style>
'''


def _image_url(session) -> str:
    return media_url(getattr(session, 'uploaded_image_path', '') if session else '')


def create_mode_select_page():
    @ui.page('/mode-select')
    async def mode_select_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(MODE_SELECT_CSS)

        session = get_session(sid) if sid else None
        img_url = _image_url(session)
        modes = [
            ('01', '自由创作', f'/drag-mode?sid={sid}'),
            ('02', '灵感创想', f'/inspire-mode?sid={sid}'),
            ('03', '对话改造', f'/chat-mode?sid={sid}'),
            ('04', '智能参数', f'/slider-mode?sid={sid}'),
        ]

        with ui.column().classes('mobile-page light-page mode-select-bg').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/camera')).props('flat round dense').style(
                    'color:#2F7B58'
                )
                ui.label('选择改造模式').style('font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126')

            with ui.column().classes('mode-shell'):
                if img_url:
                    ui.html(
                        f'<div class="mode-image-preview"><img src="{img_url}" alt="已选择的环境照片"></div>',
                        sanitize=False,
                    )

                with ui.column().classes('mode-content-stack'):
                    with ui.column().classes('mode-hero'):
                        ui.html('<div class="mode-kicker">CHOOSE A WORKFLOW</div>', sanitize=False)
                        ui.html('<div class="mode-title">选择你的改造方式</div>', sanitize=False)
                        ui.html(
                            '<div class="mode-copy">不同模式对应不同的参与深度。你可以主动创作，也可以用情绪和智能参数快速引导生成。</div>',
                            sanitize=False,
                        )

                    with ui.column().classes('mode-section'):
                        ui.html('<div class="mode-section-head">改造模式</div>', sanitize=False)
                        for index, title, path in modes:
                            ui.html(
                                '<button type="button" class="mode-card-link">'
                                f'<span class="mode-index">{index}</span>'
                                '<span>'
                                f'<span class="mode-card-title">{title}</span>'
                                '</span>'
                                '<span class="mode-chevron">›</span>'
                                '</button>',
                                sanitize=False,
                            ).on('click', lambda p=path: smooth_navigate(p))

                ui.html(
                    '<div class="mode-note">主动参与会增强对环境的控制感；如果你只想快速得到结果，智能参数也能完成完整改造。</div>',
                    sanitize=False,
                )
