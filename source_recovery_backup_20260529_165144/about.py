"""About page."""
from nicegui import ui

from app.components.nav import bottom_nav
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


ABOUT_CSS = '''
<style>
.about-wrap {
    padding: 18px 20px 104px;
    gap: 14px;
    width: 100%;
}
.about-hero {
    position: relative;
    width: 100%;
    min-height: 0;
    overflow: hidden;
    border-radius: 28px;
    padding: 22px 20px;
    border: 1px solid rgba(38,70,52,.12);
    background:
        linear-gradient(145deg, rgba(47,123,88,.16), rgba(255,255,248,.82) 56%, rgba(232,240,227,.88)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    box-shadow: 0 18px 42px rgba(38,70,52,.10);
}
.about-kicker {
    color: #2F7B58;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .14em;
}
.about-title {
    margin-top: 10px;
    color: #173126;
    font-size: 29px;
    line-height: 1.14;
    font-weight: 850;
}
.about-version {
    margin-top: 10px;
    color: rgba(23,49,38,.56);
    font-size: 12px;
}
.about-hero-note {
    margin-top: 14px;
    color: rgba(23,49,38,.68);
    font-size: 13px;
    line-height: 1.75;
}
.about-hero-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 16px;
}
.about-hero-chip {
    border-radius: 16px;
    padding: 10px 8px;
    text-align: center;
    color: #173126;
    background: rgba(255,255,248,.62);
    border: 1px solid rgba(38,70,52,.10);
    font-size: 11px;
    font-weight: 800;
}
.about-panel {
    width: 100%;
    border-radius: 26px;
    border: 1px solid rgba(38,70,52,.12);
    background:
        linear-gradient(180deg, rgba(255,255,248,.84), rgba(246,250,241,.72)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    background-blend-mode: normal, soft-light;
    backdrop-filter: blur(18px);
    padding: 18px 18px 20px;
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
}
.about-panel.light {
    background:
        linear-gradient(180deg, rgba(244,240,230,.92), rgba(230,237,226,.86)),
        url('/static/images/bamboo-mist-texture.webp') center/cover no-repeat;
    background-blend-mode: normal, soft-light;
    color: #14231A;
    border-color: rgba(7,18,13,.08);
}
.about-label {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(47,123,88,.10);
    color: #2F7B58;
    font-size: 11px;
    font-weight: 800;
}
.about-panel.light .about-label {
    background: rgba(16,67,44,.10);
    color: #1B4332;
}
.about-body {
    margin-top: 14px;
    color: rgba(20,35,26,.72);
    font-size: 13.5px;
    line-height: 1.85;
}
.about-theory-list {
    display: grid;
    gap: 10px;
    margin-top: 14px;
}
.about-theory-item {
    padding: 12px 0 0;
    border-top: 1px solid rgba(20,35,26,.12);
}
.about-theory-title {
    color: #14231A;
    font-size: 13px;
    font-weight: 850;
}
.about-theory-text {
    margin-top: 5px;
    color: rgba(20,35,26,.66);
    font-size: 12px;
    line-height: 1.75;
}
</style>
'''


def create_about_page():
    @ui.page('/about')
    def about_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(ABOUT_CSS)

        with ui.column().classes('mobile-page light-page').style('min-height:100vh'):
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.label('关于').style(
                    'font-size:18px; font-weight:800; margin-left:8px; color:#173126'
                )

            with ui.column().classes('about-wrap'):
                with ui.element('section').classes('about-hero animate-in'):
                    ui.html('''
                        <div class="about-hero-content">
                            <div class="about-kicker">ENVIRONMENT HEALING</div>
                            <div class="about-title">环境疗愈工坊</div>
                            <div class="about-version">v0.1.0 · research prototype</div>
                            <div class="about-hero-note">用真实环境照片作为起点，探索空间调整如何影响恢复感、控制感与情绪状态。</div>
                            <div class="about-hero-grid">
                                <div class="about-hero-chip">上传照片</div>
                                <div class="about-hero-chip">生成方案</div>
                                <div class="about-hero-chip">记录评估</div>
                            </div>
                        </div>
                    ''')

                with ui.element('section').classes('about-panel animate-in animate-in-delay-1'):
                    ui.html('''
                        <div class="about-label">项目简介</div>
                        <div class="about-body">
                            这是一款基于环境心理学的数字化干预工具。你可以上传真实环境照片，
                            通过摆放、绘制、对话或参数调节的方式重新组织空间，观察怎样的环境更能带来恢复感。
                        </div>
                    ''')

                with ui.element('section').classes('about-panel light animate-in animate-in-delay-2'):
                    ui.html('''
                        <div class="about-label">理论基础</div>
                        <div class="about-theory-list">
                            <div class="about-theory-item">
                                <div class="about-theory-title">注意力恢复理论 ART</div>
                                <div class="about-theory-text">自然环境通过柔性注意力帮助恢复定向注意力。</div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">压力恢复理论 SRT</div>
                                <div class="about-theory-text">自然场景能帮助降低生理应激水平，促进情绪缓和。</div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">感知控制理论</div>
                                <div class="about-theory-text">主动参与环境改造本身会增强控制感与恢复体验。</div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">倒 U 型效应</div>
                                <div class="about-theory-text">适度复杂度通常比过少或过多刺激更利于心理恢复。</div>
                            </div>
                        </div>
                    ''')

            bottom_nav('关于', light=True)
