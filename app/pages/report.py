"""疗愈报告页面 - 高级 UI"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE, NATURE_BG_CSS
from app.state import get_session
from app.components.icons import get_svg


def create_report_page():
    @ui.page('/report')
    def report_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        answers = session.survey_answers if session else {}

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('疗愈报告').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:16px; width:100%'):
                # 头部 - 自然渐变背景
                with ui.column().classes('nature-hero animate-in').style(
                    'width:100%; text-align:center; padding:32px 20px;'
                    'border-radius:24px; align-items:center; position:relative; z-index:1;'
                ):
                    ui.html(get_svg('🌿hero', 52)).classes('float-animation').style(
                        'width:52px; height:52px;'
                        'filter:drop-shadow(0 4px 8px rgba(0,0,0,0.15));'
                    )
                    ui.label('本次疗愈报告').style(
                        'font-size:22px; font-weight:700; color:white; margin-top:8px;'
                        'text-shadow:0 2px 8px rgba(0,0,0,0.15); letter-spacing:1px;'
                    )
                    ui.element('div').style(
                        'width:40px; height:2px; background:rgba(255,255,255,0.5);'
                        'border-radius:1px; margin-top:12px;'
                    )

                # 评分汇总
                ui.label('评估结果').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                )
                ui.element('div').classes('section-divider')

                # 计算分数
                prs_scores = [answers.get(f'prs{i}', 0) for i in range(1, 6)]
                prs_avg = sum(prs_scores) / max(len([s for s in prs_scores if s > 0]), 1)

                emo_scores = [answers.get(f'emo{i}', 0) for i in range(1, 5)]
                emo_avg = sum(emo_scores) / max(len([s for s in emo_scores if s > 0]), 1)

                overall = answers.get('overall', 0)

                with ui.row().classes('animate-in animate-in-delay-1').style(
                    'width:100%; gap:10px'
                ):
                    score_configs = [
                        ('恢复性感知', f'{prs_avg:.1f}' if prs_avg > 0 else '--', COLORS['primary'],
                         f'linear-gradient(135deg, {COLORS["primary_dark"]}, {COLORS["primary"]})'),
                        ('情绪改善', f'{emo_avg:.1f}' if emo_avg > 0 else '--', COLORS['accent'],
                         f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]})'),
                        ('整体满意', '★' * overall if overall > 0 else '--', COLORS['accent_light'],
                         f'linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["primary_ultra_light"]})'),
                    ]
                    for label, value, color, gradient in score_configs:
                        with ui.card().classes('glass-card').style(
                            'flex:1; padding:16px 8px; text-align:center; border:none !important;'
                            'overflow:hidden; position:relative;'
                        ):
                            # 顶部渐变色带
                            ui.element('div').style(
                                f'position:absolute; top:0; left:0; width:100%; height:3px; background:{gradient};'
                            )
                            ui.label(value).style(
                                f'font-size:22px; font-weight:700; color:{color}; margin-top:4px'
                            )
                            ui.label(label).style(
                                f'font-size:11px; color:{COLORS["text_secondary"]}; margin-top:6px; font-weight:400'
                            )

                # 环境偏好
                ui.label('你的环境偏好').classes('animate-in animate-in-delay-2').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}; margin-top:4px;'
                    'letter-spacing:0.5px;'
                )

                green = session.green_level if session else 50
                urban = session.urban_level if session else 50
                vitality = session.vitality_level if session else 50
                light = session.light_warmth if session else 50

                with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                    'width:100%; padding:18px; border:none !important;'
                ):
                    for icon_key, label, val, color in [
                        ('🌿', '绿化程度', green, COLORS['primary']),
                        ('🏗️', '人造元素', urban, COLORS['secondary']),
                        ('👥', '环境活力', vitality, COLORS['accent']),
                        ('☀️', '光线氛围', light, COLORS['accent_light']),
                    ]:
                        with ui.column().style('width:100%; gap:4px; margin-bottom:12px'):
                            with ui.row().style('width:100%; justify-content:space-between; align-items:center'):
                                with ui.row().style('align-items:center; gap:6px'):
                                    svg = get_svg(icon_key, 16)
                                    if svg:
                                        ui.html(svg).style('width:16px; height:16px; flex-shrink:0;')
                                    ui.label(label).style(
                                        f'font-size:13px; color:{COLORS["text"]}; font-weight:500'
                                    )
                                ui.label(f'{int(val)}%').style(
                                    f'font-size:14px; font-weight:700; color:{color}'
                                )
                            with ui.element('div').classes('progress-bar'):
                                ui.element('div').classes('progress-bar-fill').style(
                                    f'width:{int(val)}%; background:linear-gradient(90deg, {color}, {color}88);'
                                )

                # 疗愈建议
                with ui.row().classes('animate-in animate-in-delay-3').style(
                    'align-items:center; gap:6px'
                ):
                    ui.html(get_svg('💡', 18)).style('width:18px; height:18px; flex-shrink:0;')
                    ui.label('疗愈建议').style(
                        f'font-size:15px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                    )

                if green < 30:
                    advice = ('你当前的环境绿化程度偏低。建议在日常生活中增加接触自然的机会，'
                              '即使是简单的室内绿植或窗外绿景也有助于注意力恢复。')
                elif green <= 60:
                    advice = ('你选择了中等水平的绿化——这可能是最佳的"疗愈甜蜜点"。'
                              '适度的自然元素既能提供恢复性刺激，又不会造成信息过载。')
                else:
                    advice = ('你偏好高度自然化的环境。沉浸式的绿色空间对压力恢复特别有效，'
                              '建议定期前往公园或自然保护区进行"自然浴"。')

                with ui.card().classes('glass-card animate-in animate-in-delay-3').style(
                    'width:100%; padding:18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important;'
                ):
                    ui.label(advice).style(
                        f'font-size:14px; line-height:1.8; color:{COLORS["text"]}; font-weight:400'
                    )

                # 科学解读
                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:16px 18px; border:none !important;'
                    f'background:rgba(45,106,79,0.04) !important;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:6px'):
                        ui.html(get_svg('📚', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('科学解读').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '根据注意力恢复理论(Kaplan, 1989)，适度的自然环境能够通过"柔性注意力"机制'
                        '帮助恢复定向注意力。你选择的环境参数组合符合恢复性环境的核心特征。'
                    ).style(
                        f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.8; font-weight:300'
                    )

                # 按钮
                ui.button('回到首页', on_click=lambda: ui.navigate.to('/')).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:8px;')

                ui.button('再次体验', on_click=lambda: ui.navigate.to('/camera')).props(
                    'outline no-caps'
                ).style(
                    f'width:100%; border-radius:28px; color:{COLORS["primary"]};'
                    f'border:2px solid {COLORS["primary"]}40; padding:14px; font-weight:500;'
                    'transition:all 0.3s;'
                )
