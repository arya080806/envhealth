"""Reusable onboarding guide entry and modal."""
from __future__ import annotations

from html import escape

from nicegui import ui


GUIDE_STEPS = [
    {
        'path': '/',
        'title': '从这里开始',
        'summary': '点击“开始体验”进入照片选择页。应用会围绕一张真实环境照片，帮助你尝试更舒适、更有恢复感的空间变化。',
        'tips': ['“开始体验”进入上传或模板选择。', '右上角用户按钮进入账号信息。', '新手指引入口可随时再次打开。'],
    },
    {
        'path': '/camera',
        'title': '选择一张环境照片',
        'summary': '你可以拍摄、上传照片，也可以直接选择系统提供的环境场景。照片会作为后续改造的基础。',
        'tips': ['上传真实场景适合改造自己的空间。', '系统模板适合快速体验完整流程。', '下方场景卡片可直接点击进入下一步。'],
    },
    {
        'path': '/mode-select',
        'title': '选择参与方式',
        'summary': '这里展示当前选择的环境图像，并提供不同参与深度的改造方式。',
        'tips': ['自由创作适合直接摆放树木、座椅、水景等元素。', '灵感创想适合用草图表达想法。', '对话改造和智能参数适合快速引导生成。'],
    },
    {
        'path': '/drag-mode',
        'title': '把元素放进环境里',
        'summary': '点击或拖拽下方元素到画布中，选中后可以缩放、旋转、删除、复制或置顶。',
        'tips': ['先选择元素分类，再点击具体元素。', '元素放好后点击“AI 融合生成”。', '画布中的图片会铺满编辑区域，生成时以当前布局为参考。'],
    },
    {
        'path': '/inspire-mode',
        'title': '画出你的想法',
        'summary': '用简单线条或涂抹表达想加入的空间感觉，系统会结合原图理解你的创作意图。',
        'tips': ['不需要画得精确，表达大概区域和方向即可。', '可以用不同工具表达植物、水景、路径或氛围。', '完成后提交生成空间方案。'],
    },
    {
        'path': '/chat-mode',
        'title': '用语言描述期待',
        'summary': '你可以告诉系统希望空间更安静、更开放、更自然，或描述一个具体场景。',
        'tips': ['描述感受比描述技术细节更重要。', '可以补充“不想要”的元素。', '系统会把文字转化为改造方向。'],
    },
    {
        'path': '/slider-mode',
        'title': '用参数快速调整',
        'summary': '通过滑杆调整绿化程度、人造元素、光线氛围和空间活力，适合想快速得到结果的用户。',
        'tips': ['参数越高不一定越好，适度变化更容易带来舒适感。', '可以多次尝试不同组合。', '提交后生成对应方案。'],
    },
    {
        'path': '/result',
        'title': '查看生成方案',
        'summary': '结果页展示生成后的环境图像，并提供保存、继续调整或记录评估的入口。',
        'tips': ['不满意可以返回上一步继续调整。', '满意后保存到草稿箱或记录。', '建议记录当前方案带来的感受。'],
    },
    {
        'path': '/records',
        'title': '回看你的空间变化',
        'summary': '草稿箱保存未完成方案，记录页用于查看历史生成和评估结果。',
        'tips': ['草稿适合继续编辑。', '记录适合比较不同方案。', '可作为后续研究或个人复盘依据。'],
    },
]


GUIDE_CSS = '''
<style>
.guide-entry-btn {
    position: fixed;
    top: var(--guide-top, 14px);
    right: calc(50% - min(50vw, 215px) + var(--guide-right, 14px));
    z-index: 998;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 1px solid rgba(244,240,230,0.20);
    background: rgba(16,29,22,0.62);
    color: #F4F0E6;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 12px 26px rgba(0,0,0,0.24);
    font-size: 17px;
    font-weight: 900;
}
.guide-entry-btn.guide-entry-light {
    border-color: rgba(38,70,52,0.16);
    background: rgba(247,249,241,0.86);
    color: #2F7B58;
    box-shadow: 0 12px 26px rgba(38,70,52,0.14);
}
.guide-entry-btn:active {
    transform: scale(.96);
}
@media (min-width: 900px) and (orientation: landscape) {
    .guide-entry-btn {
        right: max(calc(28px + var(--guide-right, 24px)), calc(50% - 590px + var(--guide-right, 24px)));
    }

    .guide-modal-card {
        width: min(620px, calc(100vw - 56px));
    }
}
.guide-overlay {
    position: fixed;
    inset: 0;
    z-index: 1400;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 18px;
    background: rgba(7,18,13,0.54);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
.guide-overlay.open {
    display: flex;
}
.guide-modal-card {
    width: min(390px, calc(100vw - 32px));
    max-height: min(78vh, 680px);
    overflow: hidden;
    border-radius: 8px;
    border: 1px solid rgba(38,70,52,0.14);
    background:
        linear-gradient(180deg, rgba(255,255,248,0.96), rgba(244,248,239,0.96)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    color: #173126;
    box-shadow: 0 28px 70px rgba(0,0,0,0.28);
    display: flex;
    flex-direction: column;
}
.q-card.guide-modal-card,
.q-dialog__inner > .q-card.guide-modal-card {
    background:
        linear-gradient(180deg, rgba(255,255,248,0.97), rgba(244,248,239,0.97)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #FFFDF4 !important;
    background-blend-mode: normal, soft-light, normal !important;
    color: #173126 !important;
    border: 1px solid rgba(38,70,52,0.14) !important;
    box-shadow: 0 28px 70px rgba(0,0,0,0.28) !important;
}
.q-card.guide-modal-card *,
.q-dialog__inner > .q-card.guide-modal-card * {
    color: inherit;
}
.guide-head {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 16px 12px;
    border-bottom: 1px solid rgba(38,70,52,0.10);
}
.q-card.guide-modal-card .guide-kicker {
    color: #2F7B58 !important;
}
.q-card.guide-modal-card .guide-title-main,
.q-card.guide-modal-card .guide-step-title,
.q-card.guide-modal-card .guide-flow-btn.active {
    color: #10251A !important;
}
.q-card.guide-modal-card .guide-step-meta,
.q-card.guide-modal-card .guide-step-summary,
.q-card.guide-modal-card .guide-tip-list li,
.q-card.guide-modal-card .guide-flow-title,
.q-card.guide-modal-card .guide-flow-btn {
    color: rgba(16,37,26,.72) !important;
}
.q-card.guide-modal-card .guide-close {
    background: rgba(47,123,88,0.10) !important;
    color: #173126 !important;
}
.q-card.guide-modal-card .guide-close .q-icon,
.q-dialog__inner > .q-card.guide-modal-card .guide-close .q-icon {
    color: #2F7B58 !important;
}
.q-card.guide-modal-card .guide-nav-btn.primary {
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    color: #F8FAF2 !important;
}
.guide-head-main {
    min-width: 0;
    flex: 1;
}
.guide-kicker {
    color: #2F7B58;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .10em;
}
.guide-title-main {
    margin-top: 3px;
    font-size: 19px;
    line-height: 1.25;
    font-weight: 950;
}
.guide-close {
    width: 34px;
    height: 34px;
    border: 0;
    border-radius: 50%;
    background: rgba(47,123,88,0.10);
    color: #173126;
    font-size: 20px;
    font-weight: 800;
    cursor: pointer;
}
.guide-body {
    overflow: auto;
    padding: 16px;
}
.guide-step-card {
    border: 1px solid rgba(47,123,88,0.12);
    border-radius: 8px;
    background: rgba(255,255,248,0.74);
    padding: 16px;
}
.guide-step-card.active {
    border-color: rgba(47,123,88,0.34);
    background: rgba(47,123,88,0.10);
}
.guide-step-meta {
    color: rgba(23,49,38,0.56);
    font-size: 12px;
    font-weight: 800;
}
.guide-step-title {
    margin-top: 6px;
    color: #10251A;
    font-size: 20px;
    line-height: 1.28;
    font-weight: 950;
}
.guide-step-summary {
    margin-top: 10px;
    color: rgba(23,49,38,0.72);
    font-size: 13px;
    line-height: 1.72;
    font-weight: 600;
}
.guide-tip-list {
    margin: 12px 0 0;
    padding: 0;
    display: grid;
    gap: 8px;
    list-style: none;
}
.guide-tip-list li {
    position: relative;
    padding-left: 14px;
    color: rgba(16,37,26,0.72);
    font-size: 12.5px;
    line-height: 1.55;
}
.guide-tip-list li::before {
    content: "";
    position: absolute;
    left: 0;
    top: .65em;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #2F7B58;
}
.guide-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 14px;
}
.guide-nav-btn {
    min-height: 38px;
    border: 1px solid rgba(47,123,88,0.16);
    border-radius: 999px;
    background: rgba(47,123,88,0.08);
    color: #2F7B58;
    font-size: 13px;
    font-weight: 900;
    cursor: pointer;
    padding: 0 16px;
}
.guide-nav-btn.primary {
    background: #2F7B58;
    color: #F8FAF2;
}
.guide-flow {
    display: grid;
    gap: 8px;
    margin-top: 14px;
}
.guide-flow-title {
    color: rgba(16,37,26,0.58);
    font-size: 12px;
    font-weight: 900;
}
.guide-flow-list {
    display: grid;
    gap: 7px;
}
.guide-flow-btn {
    width: 100%;
    border: 1px solid rgba(47,123,88,0.10);
    border-radius: 8px;
    background: rgba(255,255,248,0.55);
    color: rgba(16,37,26,0.72);
    padding: 9px 11px;
    text-align: left;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
}
.guide-flow-btn.active {
    border-color: rgba(47,123,88,0.32);
    background: rgba(47,123,88,0.12);
    color: #10251A;
}
@media (max-width: 520px) {
    .guide-entry-btn {
        right: var(--guide-right, 14px);
    }
}
</style>
'''


def guide_entry(*, light: bool = False, right_offset: int = 14, top_offset: int = 14) -> None:
    """Render a floating guide entry that opens an onboarding dialog."""
    light_class = ' guide-entry-light' if light else ''
    ui.add_head_html(GUIDE_CSS)

    try:
        current_path = ui.context.client.request.url.path
    except Exception:
        current_path = '/'

    if current_path == '/ai-mode':
        current_path = '/slider-mode'
    if current_path in {'/survey', '/report', '/export'}:
        current_path = '/result'
    if current_path in {'/about', '/account'}:
        current_path = '/records'

    active_index = next(
        (index for index, step in enumerate(GUIDE_STEPS) if step['path'] == current_path),
        0,
    )

    with ui.dialog() as guide_dialog, ui.card().classes('guide-modal-card'):
        with ui.element('div').classes('guide-head'):
            with ui.element('div').classes('guide-head-main'):
                ui.html('<div class="guide-kicker">GET STARTED</div>', sanitize=False)
                ui.html('<div class="guide-title-main">新手指引</div>', sanitize=False)
            ui.button(icon='close', on_click=guide_dialog.close).props('flat round dense').classes('guide-close')

        with ui.element('div').classes('guide-body'):
            ui.html('<div class="guide-flow-title">当前页面提示</div>', sanitize=False)
            _render_step(GUIDE_STEPS[active_index], active_index, active=True)

            ui.html('<div class="guide-flow-title" style="margin-top:14px">完整流程</div>', sanitize=False)
            with ui.element('div').classes('guide-flow-list'):
                for index, step in enumerate(GUIDE_STEPS):
                    _render_step(step, index, active=index == active_index)

            with ui.element('div').classes('guide-actions'):
                ui.button('我知道了', on_click=guide_dialog.close).props('unelevated no-caps').classes(
                    'guide-nav-btn primary'
                )

    with ui.element('button').classes(f'guide-entry-btn{light_class}').style(
        f'--guide-right:{right_offset}px;--guide-top:{top_offset}px'
    ).on('click', guide_dialog.open):
        ui.html('?')


def _render_step(step: dict, index: int, *, active: bool) -> None:
    active_class = ' active' if active else ''
    tips = ''.join(f'<li>{escape(tip)}</li>' for tip in step['tips'])
    ui.html(
        f'''
        <div class="guide-step-card{active_class}">
            <div class="guide-step-meta">步骤 {index + 1} / {len(GUIDE_STEPS)}</div>
            <div class="guide-step-title">{escape(step['title'])}</div>
            <div class="guide-step-summary">{escape(step['summary'])}</div>
            <ul class="guide-tip-list">{tips}</ul>
        </div>
        ''',
        sanitize=False,
    )
