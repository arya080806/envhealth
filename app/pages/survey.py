"""心理评估问卷页面 - 高级 UI + 必答校验"""
import time
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session
from app.components.icons import get_svg


def _build_likert(item_id: str, labels: list[str], answers: dict, error_labels: dict):
    """构建 Likert 量表按钮组 - 胶囊形样式 + 校验提示"""
    container = ui.column().style('width:100%; gap:4px;')
    with container:
        with ui.row().style('width:100%; gap:4px'):
            btns = []
            for i, label in enumerate(labels, 1):
                btn = ui.button(label, on_click=lambda val=i: select(val)).props(
                    'outline dense no-caps'
                ).style(
                    f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                    f'border:1.5px solid {COLORS["border"]}; min-width:0;'
                    f'color:{COLORS["text_secondary"]}; font-weight:400;'
                    'transition:all 0.25s;'
                )
                btns.append((btn, i))

        # 校验提示标签
        err = ui.label('请选择一个选项').style(
            f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
        )
        error_labels[item_id] = err

        def select(val):
            answers[item_id] = val
            # 隐藏错误提示
            error_labels[item_id].style(
                f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
            )
            for b, v in btns:
                if v == val:
                    b.style(
                        f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                        f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                        f'color:white; border-color:{COLORS["primary"]}; min-width:0;'
                        'font-weight:600; box-shadow:0 4px 12px rgba(45,106,79,0.2);'
                    )
                else:
                    b.style(
                        f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                        f'border:1.5px solid {COLORS["border"]}; min-width:0;'
                        f'background:white; color:{COLORS["text_secondary"]}; font-weight:400;'
                    )


def create_survey_page():
    @ui.page('/survey')
    def survey_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        answers = {}
        error_labels = {}  # item_id -> error label element

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/result?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('心理评估').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:8px; width:100%'):
                ui.label('请根据刚才查看改造后环境的感受，回答以下问题。').classes('animate-in').style(
                    f'font-size:14px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                # PRS 恢复性感知量表
                with ui.card().classes('glass-card animate-in animate-in-delay-1').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('🧠', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('恢复性感知（PRS）').style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    prs_items = [
                        ('prs1', '这个环境让我感到放松'),
                        ('prs2', '这个环境能帮助我恢复注意力'),
                        ('prs3', '我愿意在这样的环境中停留'),
                        ('prs4', '这个环境让我暂时忘记日常烦恼'),
                        ('prs5', '这个环境给我一种"远离"的感觉'),
                    ]
                    prs_labels = ['完全不同意', '不同意', '一般', '同意', '完全同意']

                    for item_id, question in prs_items:
                        ui.label(question).style(
                            f'font-size:14px; line-height:1.5; margin-top:12px; color:{COLORS["text"]}'
                        )
                        _build_likert(item_id, prs_labels, answers, error_labels)

                # 情绪评分
                with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('💚', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('情绪状态').style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    emo_items = [
                        ('emo1', '平静的'),
                        ('emo2', '愉悦的'),
                        ('emo3', '充满活力的'),
                        ('emo4', '放松的'),
                    ]
                    emo_labels = ['很少', '较少', '一般', '较多', '很多']

                    for item_id, question in emo_items:
                        ui.label(question).style(
                            f'font-size:14px; margin-top:12px; color:{COLORS["text"]}'
                        )
                        _build_likert(item_id, emo_labels, answers, error_labels)

                # 整体满意度
                with ui.card().classes('glass-card animate-in animate-in-delay-3').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('⭐', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('整体满意度').style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    star_label = ui.label('☆☆☆☆☆').style(
                        f'font-size:32px; text-align:center; width:100%; letter-spacing:6px;'
                        f'color:{COLORS["accent"]};'
                    )

                    # 不设默认值 — 必须主动选择
                    star_btns = []
                    with ui.row().style('width:100%; justify-content:center; gap:8px; margin:8px 0;'):
                        for val in range(1, 6):
                            sbtn = ui.button(
                                str(val), on_click=lambda v=val: select_star(v)
                            ).props('outline round dense').style(
                                f'width:44px; height:44px; font-size:16px; font-weight:600;'
                                f'border:2px solid {COLORS["border"]}; color:{COLORS["text_secondary"]};'
                                'transition:all 0.2s;'
                            )
                            star_btns.append((sbtn, val))

                    star_err = ui.label('请选择满意度').style(
                        f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
                    )
                    error_labels['overall'] = star_err

                    def select_star(val):
                        answers['overall'] = val
                        star_label.set_text('★' * val + '☆' * (5 - val))
                        star_err.style(
                            f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
                        )
                        for b, v in star_btns:
                            if v <= val:
                                b.style(
                                    f'width:44px; height:44px; font-size:16px; font-weight:600;'
                                    f'background:linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]});'
                                    f'color:white; border-color:{COLORS["accent"]};'
                                    'box-shadow:0 3px 8px rgba(212,163,115,0.3);'
                                )
                            else:
                                b.style(
                                    f'width:44px; height:44px; font-size:16px; font-weight:600;'
                                    f'border:2px solid {COLORS["border"]}; color:{COLORS["text_secondary"]};'
                                    'background:white;'
                                )

                    with ui.row().style(
                        f'width:100%; justify-content:space-between; font-size:11px; color:{COLORS["text_secondary"]};'
                        'font-weight:300;'
                    ):
                        ui.label('不满意')
                        ui.label('一般')
                        ui.label('非常满意')

                # 开放反馈
                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('💬', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('其他想法或建议（选填）').style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}; margin-bottom:8px'
                        )
                    feedback = ui.textarea(placeholder='请输入你的想法...').style(
                        'width:100%; min-height:80px; border-radius:14px;'
                    )

                # 提交按钮
                submit_btn = ui.button('提交评估 →', on_click=lambda: submit()).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:12px;')

                def submit():
                    # 必答校验
                    required = [
                        'prs1', 'prs2', 'prs3', 'prs4', 'prs5',
                        'emo1', 'emo2', 'emo3', 'emo4',
                        'overall',
                    ]
                    missing = []
                    for key in required:
                        if key not in answers:
                            missing.append(key)
                            if key in error_labels:
                                error_labels[key].style(
                                    f'display:block; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
                                )
                    if missing:
                        ui.notify(f'请完成所有必答题（还有 {len(missing)} 题未作答）', type='warning')
                        return

                    answers['feedback'] = feedback.value
                    if session:
                        session.survey_answers = answers
                        session.survey_completed_at = time.time()
                    ui.navigate.to(f'/report?sid={sid}')
