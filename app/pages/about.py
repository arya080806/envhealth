"""关于页面 - 高级 UI"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, BOTTOM_NAV_STYLE, NATURE_BG_CSS
from app.components.nav import bottom_nav
from app.components.icons import get_svg


def create_about_page():
    @ui.page('/about')
    def about_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        with ui.column().classes('mobile-page').style('min-height:100vh'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.label('关于').style(
                    f'font-size:17px; font-weight:600; margin-left:8px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:16px; width:100%; flex:1'):
                # 头部 - 自然渐变背景
                with ui.column().classes('nature-hero animate-in').style(
                    'text-align:center; padding:32px 20px; border-radius:24px;'
                    'align-items:center; position:relative; z-index:1;'
                ):
                    ui.html(get_svg('🌿hero', 52)).classes('float-animation').style(
                        'width:52px; height:52px;'
                    )
                    ui.label('环境疗愈工坊').style(
                        'font-size:22px; font-weight:700; color:white; margin-top:8px;'
                        'text-shadow:0 2px 8px rgba(0,0,0,0.15); letter-spacing:1px;'
                    )
                    ui.label('v0.1.0').style(
                        'font-size:13px; color:rgba(255,255,255,0.7); margin-top:4px; font-weight:300'
                    )

                sections = [
                    ('📖', '项目简介',
                     '环境疗愈工坊是一款基于环境心理学的数字化干预工具。'
                     '通过拍摄真实环境照片，用户可以交互式地改造环境，'
                     '探索什么样的环境最能帮助自己恢复心理能量。'),
                    ('🔬', '理论基础',
                     '注意力恢复理论 (ART, Kaplan 1989): 自然环境通过"柔性注意力"帮助恢复定向注意力。\n\n'
                     '压力恢复理论 (SRT, Ulrich 1991): 自然场景能快速降低生理应激水平。\n\n'
                     '感知控制理论: 用户对环境的主动控制感本身就是疗愈机制。\n\n'
                     '倒U型效应: 中等水平的环境复杂度可能具有最佳恢复效果。'),
                    ('🧪', '研究设计',
                     '本程序同时作为研究工具，通过 2（场景类型）× 3（绿化程度）× 3（人造元素丰富度）'
                     '的实验设计，验证环境参数与心理恢复的关系，并将研究结论动态融入推荐算法。'),
                ]

                for idx, (icon, title, content) in enumerate(sections):
                    with ui.card().classes(f'glass-card animate-in animate-in-delay-{idx+1}').style(
                        'width:100%; padding:18px; border:none !important;'
                    ):
                        with ui.row().style('align-items:center; gap:8px; margin-bottom:4px;'):
                            svg = get_svg(icon, 18)
                            if svg:
                                ui.html(svg).style('width:18px; height:18px; flex-shrink:0;')
                            ui.label(title).style(
                                f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]};'
                            )
                        ui.element('div').classes('section-divider')
                        ui.label(content).style(
                            f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.8;'
                            'white-space:pre-line; font-weight:300;'
                        )

            # 底部导航
            bottom_nav('关于')
