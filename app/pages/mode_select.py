"""模式选择页面 - 高级 UI"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE
from app.state import get_session
from app.components.icons import get_svg


def create_mode_select_page():
    @ui.page('/mode-select')
    def mode_select_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/camera')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('选择改造模式').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:16px; width:100%'):
                # 缩略图预览
                if sid:
                    session = get_session(sid)
                    if session.uploaded_image_path:
                        from pathlib import Path
                        fname = Path(session.uploaded_image_path).name
                        with ui.element('div').classes('animate-in').style(
                            'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                            'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                        ):
                            ui.image(f'/api/image/{fname}').style(
                                'width:100%; height:180px; object-fit:cover;'
                            )
                            # 毛玻璃蒙版
                            ui.element('div').style(
                                'position:absolute; bottom:0; left:0; width:100%; padding:14px 16px;'
                                'background:linear-gradient(to top, rgba(27,67,50,0.7), transparent);'
                            )
                            ui.label('选择你的改造方式').style(
                                'position:absolute; bottom:14px; left:16px;'
                                'font-size:15px; font-weight:600; color:white;'
                                'text-shadow:0 1px 4px rgba(0,0,0,0.2);'
                            )

                # 说明文字
                ui.label('不同模式对应不同的控制程度。研究表明，对环境的感知控制能有效提升心理恢复效果。').classes(
                    'animate-in animate-in-delay-1'
                ).style(
                    f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                # 三种模式卡片
                modes = [
                    ('🎚️', f'linear-gradient(135deg, {COLORS["primary_dark"]}, {COLORS["primary"]})',
                     '参数调节模式',
                     '通过滑杆精确控制绿化程度、人造元素等参数，AI根据参数生成改造场景',
                     f'/slider-mode?sid={sid}'),
                    ('✏️', f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]})',
                     '自由创作模式',
                     '在照片上自由添加树木、长椅等元素，AI自动融合生成自然效果',
                     f'/drag-mode?sid={sid}'),
                    ('✨', f'linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["primary_ultra_light"]})',
                     '智能推荐模式',
                     '基于环境心理学研究结论，AI为你推荐最佳疗愈环境方案',
                     f'/ai-mode?sid={sid}'),
                ]

                for idx, (icon, bg, title, desc, href) in enumerate(modes):
                    card = ui.card().classes(
                        f'glass-card hover-lift card-press animate-in animate-in-delay-{idx+1}'
                    ).style(
                        'width:100%; padding:0; cursor:pointer; border:none !important; overflow:hidden;'
                    ).on('click', lambda h=href: ui.navigate.to(h))

                    with card:
                        with ui.row().style('width:100%; align-items:center; gap:16px; padding:20px;'):
                            # 图标区域
                            with ui.element('div').style(
                                f'width:60px; height:60px; border-radius:18px; display:flex;'
                                f'align-items:center; justify-content:center; background:{bg};'
                                'flex-shrink:0; box-shadow:0 4px 16px rgba(27,67,50,0.2);'
                            ):
                                svg = get_svg(icon, 32)
                                if svg:
                                    ui.html(svg).style('width:32px; height:32px;')
                                else:
                                    ui.label(icon).style('font-size:28px;')
                            with ui.column().style('gap:6px; flex:1'):
                                ui.label(title).style(
                                    f'font-size:16px; font-weight:600; color:{COLORS["text"]};'
                                    'letter-spacing:0.3px;'
                                )
                                ui.label(desc).style(
                                    f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.6;'
                                    'font-weight:300;'
                                )
                            # 箭头
                            ui.icon('chevron_right').style(
                                f'font-size:20px; color:{COLORS["primary_light"]}; flex-shrink:0;'
                            )

                # 理论说明
                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:14px 18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:4px'):
                        ui.html(get_svg('💡', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('感知控制理论').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '当你主动参与环境改造过程时，对环境的"控制感"会增强心理恢复效果。'
                        '选择适合你的参与程度，每种模式都是有效的。'
                    ).style(f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300')
