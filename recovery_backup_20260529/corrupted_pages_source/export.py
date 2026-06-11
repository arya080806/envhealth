"""鏁版嵁瀵煎嚭椤甸潰 - 鐮旂┒鑰呯鐞嗛潰鏉匡紙瀵嗙爜淇濇姢锛?""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.db import get_export_summary
from app.routers.api import EXPORT_KEY
from app.components.nav import bottom_nav, smooth_navigate


def create_export_page():
    @ui.page('/export')
    def export_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        auth_state = {'authed': False}

        with ui.column().classes('mobile-page').style('min-height:100vh') as page_container:
            bottom_nav()
            # 椤堕儴鏍?            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('鏁版嵁瀵煎嚭').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            # 瀵嗙爜杈撳叆鍖哄煙
            auth_section = ui.column().style('padding:40px 24px 100px; gap:16px; width:100%; align-items:center;')
            with auth_section:
                ui.label('鐮旂┒鑰呭叆鍙?).style(
                    f'font-size:18px; font-weight:600; color:{COLORS["text"]}'
                )
                ui.label('璇疯緭鍏ョ爺绌惰€呭瘑鐮佷互鏌ョ湅鍜屽鍑烘暟鎹?).style(
                    f'font-size:13px; color:{COLORS["text_secondary"]};'
                )
                pwd_input = ui.input(
                    label='瀵嗙爜', password=True, password_toggle_button=True
                ).props('outlined dense').style('width:100%; max-width:300px;')
                pwd_error = ui.label().style('display:none;')

                def check_pwd():
                    if pwd_input.value == EXPORT_KEY:
                        auth_state['authed'] = True
                        auth_section.style('display:none')
                        data_section.style('display:block; padding:20px; width:100%;')
                        show_data()
                    else:
                        pwd_error.set_text('瀵嗙爜閿欒')
                        pwd_error.style(f'display:block; font-size:12px; color:{COLORS["error"]};')

                ui.button('楠岃瘉', on_click=check_pwd).props('no-caps unelevated').style(
                    f'width:100%; max-width:300px; border-radius:28px;'
                    f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                    'color:white; font-weight:600;'
                )

            # 鏁版嵁鍖哄煙锛堝垵濮嬮殣钘忥級
            data_section = ui.column().style('display:none; gap:16px; padding-bottom:100px;')

            def show_data():
                with data_section:
                    summary = get_export_summary()
                    total = summary['total_sessions']
                    completed = summary['completed_surveys']
                    with_image = summary['with_uploads']
                    with_generated = summary['with_generated']

                    ui.label('鏁版嵁姒傝').classes('animate-in').style(
                        f'font-size:16px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.row().classes('animate-in animate-in-delay-1').style('width:100%; gap:10px'):
                        stats = [
                            ('鎬讳細璇?, str(total), COLORS['primary']),
                            ('瀹屾垚闂嵎', str(completed), COLORS['accent']),
                            ('鏈変笂浼?, str(with_image), COLORS['secondary']),
                            ('鏈夌敓鎴?, str(with_generated), COLORS['accent_light']),
                        ]
                        for label, value, color in stats:
                            with ui.card().classes('glass-card').style(
                                'flex:1; padding:14px 8px; text-align:center; border:none !important;'
                            ):
                                ui.label(value).style(f'font-size:24px; font-weight:700; color:{color};')
                                ui.label(label).style(
                                    f'font-size:11px; color:{COLORS["text_secondary"]}; margin-top:4px'
                                )

                    # 瀹屾垚鐜?                    if total > 0:
                        rate = round(completed / total * 100, 1)
                        with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                            'width:100%; padding:16px 18px; border:none !important;'
                        ):
                            with ui.row().style('width:100%; justify-content:space-between; align-items:center'):
                                ui.label('闂嵎瀹屾垚鐜?).style(
                                    f'font-size:14px; font-weight:500; color:{COLORS["text"]}'
                                )
                                ui.label(f'{rate}%').style(
                                    f'font-size:16px; font-weight:700; color:{COLORS["primary"]}'
                                )
                            with ui.element('div').classes('progress-bar').style('margin-top:8px'):
                                ui.element('div').classes('progress-bar-fill').style(
                                    f'width:{rate}%; background:linear-gradient(90deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                                )

                    # 妯″紡鍒嗗竷
                    modes = summary.get('mode_distribution', {})
                    if modes:
                        with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                            'width:100%; padding:16px 18px; border:none !important;'
                        ):
                            ui.label('妯″紡浣跨敤鍒嗗竷').style(
                                f'font-size:14px; font-weight:600; color:{COLORS["text"]}; margin-bottom:8px'
                            )
                            mode_labels = {'slider': '鍙傛暟璋冭妭', 'drag': '鑷敱鍒涗綔', 'ai': '鏅鸿兘鎺ㄨ崘'}
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

                    # 瀵煎嚭鎸夐挳
                    ui.label('瀵煎嚭鏁版嵁').classes('animate-in animate-in-delay-3').style(
                        f'font-size:16px; font-weight:600; color:{COLORS["text"]}; margin-top:8px;'
                        'letter-spacing:0.5px'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.row().classes('animate-in animate-in-delay-4').style('width:100%; gap:12px'):
                        ui.link(
                            '涓嬭浇 CSV', f'/api/export/csv?key={EXPORT_KEY}'
                        ).style(
                            f'flex:1; text-align:center; padding:14px; border-radius:28px; text-decoration:none;'
                            f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                            'color:white; font-weight:600; font-size:15px;'
                            f'box-shadow:0 6px 20px rgba(45,106,79,0.25);'
                        )
                        ui.link(
                            '涓嬭浇 JSON', f'/api/export/json?key={EXPORT_KEY}'
                        ).style(
                            f'flex:1; text-align:center; padding:14px; border-radius:28px; text-decoration:none;'
                            f'border:2px solid {COLORS["primary"]}40; color:{COLORS["primary"]};'
                            'font-weight:600; font-size:15px;'
                        )

                    # CSV瀛楁璇存槑
                    with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                        'width:100%; padding:16px 18px; border:none !important; margin-top:8px;'
                        f'border-left:3px solid {COLORS["primary"]} !important;'
                    ):
                        ui.label('CSV 瀛楁璇存槑').style(
                            f'font-size:13px; font-weight:600; color:{COLORS["primary_dark"]}; margin-bottom:6px'
                        )
                        fields_desc = (
                            'session_id: 浼氳瘽ID\n'
                            'participant_id: 琚瘯缂栧彿\n'
                            'display_name: 琚瘯鏄电О\n'
                            'scene_type: 鍦烘櫙绫诲瀷 (park/urban)\n'
                            'mode_used: 浣跨敤妯″紡 (slider/drag/ai)\n'
                            'experiment_condition: 瀹為獙鏉′欢鏍囩\n'
                            'green/urban/vitality/light: 鐜鍙傛暟 (0-100)\n'
                            'prs1-prs5: PRS鎭㈠鎬ф劅鐭ュ悇棰樺緱鍒?(1-5)\n'
                            'prs_mean: PRS鍧囧€糪n'
                            'emo1-emo4: 鎯呯华璇勫垎鍚勯 (1-5)\n'
                            'emo_mean: 鎯呯华鍧囧€糪n'
                            'overall_satisfaction: 鏁翠綋婊℃剰搴?(1-5)\n'
                            'feedback_text: 寮€鏀炬€у弽棣圽n'
                            'interaction_log_count: 浜や簰鎿嶄綔娆℃暟\n'
                            'created_at/survey_completed_at: 鏃堕棿鎴砛n'
                            'interaction_duration_seconds: 浜や簰鏃堕暱(绉?'
                        )
                        ui.label(fields_desc).style(
                            f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.8;'
                            'white-space:pre-line; font-weight:300;'
                        )
