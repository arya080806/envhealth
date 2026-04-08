"""数据导出页面 - 研究者管理面板（密码保护）"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.db import get_export_summary
from app.routers.api import EXPORT_KEY


def create_export_page():
    @ui.page('/export')
    def export_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        auth_state = {'authed': False}

        with ui.column().classes('mobile-page').style('min-height:100vh') as page_container:
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('数据导出').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            # 密码输入区域
            auth_section = ui.column().style('padding:40px 24px; gap:16px; width:100%; align-items:center;')
            with auth_section:
                ui.label('研究者入口').style(
                    f'font-size:18px; font-weight:600; color:{COLORS["text"]}'
                )
                ui.label('请输入研究者密码以查看和导出数据').style(
                    f'font-size:13px; color:{COLORS["text_secondary"]};'
                )
                pwd_input = ui.input(
                    label='密码', password=True, password_toggle_button=True
                ).props('outlined dense').style('width:100%; max-width:300px;')
                pwd_error = ui.label().style('display:none;')

                def check_pwd():
                    if pwd_input.value == EXPORT_KEY:
                        auth_state['authed'] = True
                        auth_section.style('display:none')
                        data_section.style('display:block; padding:20px; width:100%;')
                        show_data()
                    else:
                        pwd_error.set_text('密码错误')
                        pwd_error.style(f'display:block; font-size:12px; color:{COLORS["error"]};')

                ui.button('验证', on_click=check_pwd).props('no-caps unelevated').style(
                    f'width:100%; max-width:300px; border-radius:28px;'
                    f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                    'color:white; font-weight:600;'
                )

            # 数据区域（初始隐藏）
            data_section = ui.column().style('display:none; gap:16px;')

            def show_data():
                with data_section:
                    summary = get_export_summary()
                    total = summary['total_sessions']
                    completed = summary['completed_surveys']
                    with_image = summary['with_uploads']
                    with_generated = summary['with_generated']

                    ui.label('数据概览').classes('animate-in').style(
                        f'font-size:16px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.row().classes('animate-in animate-in-delay-1').style('width:100%; gap:10px'):
                        stats = [
                            ('总会话', str(total), COLORS['primary']),
                            ('完成问卷', str(completed), COLORS['accent']),
                            ('有上传', str(with_image), COLORS['secondary']),
                            ('有生成', str(with_generated), COLORS['accent_light']),
                        ]
                        for label, value, color in stats:
                            with ui.card().classes('glass-card').style(
                                'flex:1; padding:14px 8px; text-align:center; border:none !important;'
                            ):
                                ui.label(value).style(f'font-size:24px; font-weight:700; color:{color};')
                                ui.label(label).style(
                                    f'font-size:11px; color:{COLORS["text_secondary"]}; margin-top:4px'
                                )

                    # 完成率
                    if total > 0:
                        rate = round(completed / total * 100, 1)
                        with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                            'width:100%; padding:16px 18px; border:none !important;'
                        ):
                            with ui.row().style('width:100%; justify-content:space-between; align-items:center'):
                                ui.label('问卷完成率').style(
                                    f'font-size:14px; font-weight:500; color:{COLORS["text"]}'
                                )
                                ui.label(f'{rate}%').style(
                                    f'font-size:16px; font-weight:700; color:{COLORS["primary"]}'
                                )
                            with ui.element('div').classes('progress-bar').style('margin-top:8px'):
                                ui.element('div').classes('progress-bar-fill').style(
                                    f'width:{rate}%; background:linear-gradient(90deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                                )

                    # 模式分布
                    modes = summary.get('mode_distribution', {})
                    if modes:
                        with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                            'width:100%; padding:16px 18px; border:none !important;'
                        ):
                            ui.label('模式使用分布').style(
                                f'font-size:14px; font-weight:600; color:{COLORS["text"]}; margin-bottom:8px'
                            )
                            mode_labels = {'slider': '参数调节', 'drag': '自由创作', 'ai': '智能推荐'}
                            mode_colors = {'slider': COLORS['primary'], 'drag': COLORS['accent'], 'ai': COLORS['secondary']}
                            for mode, count in modes.items():
                                pct = round(count / total * 100, 1) if total > 0 else 0
                                color = mode_colors.get(mode, COLORS['text_secondary'])
                                with ui.row().style(
                                    'width:100%; justify-content:space-between; align-items:center; margin-bottom:6px'
                                ):
                                    ui.label(mode_labels.get(mode, mode)).style(
                                        f'font-size:13px; color:{COLORS["text"]}'
                                    )
                                    ui.label(f'{count} ({pct}%)').style(
                                        f'font-size:13px; font-weight:600; color:{color}'
                                    )

                    # 导出按钮
                    ui.label('导出数据').classes('animate-in animate-in-delay-3').style(
                        f'font-size:16px; font-weight:600; color:{COLORS["text"]}; margin-top:8px;'
                        'letter-spacing:0.5px'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.row().classes('animate-in animate-in-delay-4').style('width:100%; gap:12px'):
                        ui.link(
                            '下载 CSV', f'/api/export/csv?key={EXPORT_KEY}'
                        ).style(
                            f'flex:1; text-align:center; padding:14px; border-radius:28px; text-decoration:none;'
                            f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                            'color:white; font-weight:600; font-size:15px;'
                            f'box-shadow:0 6px 20px rgba(45,106,79,0.25);'
                        )
                        ui.link(
                            '下载 JSON', f'/api/export/json?key={EXPORT_KEY}'
                        ).style(
                            f'flex:1; text-align:center; padding:14px; border-radius:28px; text-decoration:none;'
                            f'border:2px solid {COLORS["primary"]}40; color:{COLORS["primary"]};'
                            'font-weight:600; font-size:15px;'
                        )

                    # CSV字段说明
                    with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                        'width:100%; padding:16px 18px; border:none !important; margin-top:8px;'
                        f'border-left:3px solid {COLORS["primary"]} !important;'
                    ):
                        ui.label('CSV 字段说明').style(
                            f'font-size:13px; font-weight:600; color:{COLORS["primary_dark"]}; margin-bottom:6px'
                        )
                        fields_desc = (
                            'session_id: 会话ID\n'
                            'participant_id: 被试编号\n'
                            'display_name: 被试昵称\n'
                            'scene_type: 场景类型 (park/urban)\n'
                            'mode_used: 使用模式 (slider/drag/ai)\n'
                            'experiment_condition: 实验条件标签\n'
                            'green/urban/vitality/light: 环境参数 (0-100)\n'
                            'prs1-prs5: PRS恢复性感知各题得分 (1-5)\n'
                            'prs_mean: PRS均值\n'
                            'emo1-emo4: 情绪评分各题 (1-5)\n'
                            'emo_mean: 情绪均值\n'
                            'overall_satisfaction: 整体满意度 (1-5)\n'
                            'feedback_text: 开放性反馈\n'
                            'interaction_log_count: 交互操作次数\n'
                            'created_at/survey_completed_at: 时间戳\n'
                            'interaction_duration_seconds: 交互时长(秒)'
                        )
                        ui.label(fields_desc).style(
                            f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.8;'
                            'white-space:pre-line; font-weight:300;'
                        )
