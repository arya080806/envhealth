"""蹇冪悊璇勪及闂嵎椤甸潰 - 楂樼骇 UI + 蹇呯瓟鏍￠獙"""
import time
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT
from app.state import get_session
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate


def _build_likert(item_id: str, labels: list[str], answers: dict, error_labels: dict):
    """鏋勫缓 Likert 閲忚〃鎸夐挳缁?- 鑳跺泭褰㈡牱寮?+ 鏍￠獙鎻愮ず"""
    container = ui.column().style('width:100%; gap:4px;')
    with container:
        with ui.row().style('width:100%; gap:4px'):
            btns = []
            for i, label in enumerate(labels, 1):
                btn = ui.button(label, on_click=lambda val=i: select(val)).props(
                    'outline dense no-caps'
                ).style(
                    f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                    'border:1.5px solid rgba(47,123,88,0.18); min-width:0;'
                    'background:rgba(255,255,248,0.64); color:rgba(23,49,38,0.62); font-weight:500;'
                    'transition:all 0.25s;'
                )
                btns.append((btn, i))

        # 鏍￠獙鎻愮ず鏍囩
        err = ui.label('璇烽€夋嫨涓€涓€夐」').style(
            f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
        )
        error_labels[item_id] = err

        def select(val):
            answers[item_id] = val
            # 闅愯棌閿欒鎻愮ず
            error_labels[item_id].style(
                f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
            )
            for b, v in btns:
                if v == val:
                    b.style(
                        f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                        'background:#2F7B58;color:#F8FAF2;border-color:#2F7B58;min-width:0;'
                        'font-weight:700; box-shadow:0 4px 12px rgba(47,123,88,0.18);'
                    )
                else:
                    b.style(
                        f'flex:1; border-radius:14px; font-size:11px; padding:10px 2px;'
                        'border:1.5px solid rgba(47,123,88,0.18); min-width:0;'
                        'background:rgba(255,255,248,0.64); color:rgba(23,49,38,0.62); font-weight:500;'
                    )


def create_survey_page():
    @ui.page('/survey')
    def survey_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        answers = {}
        error_labels = {}  # item_id -> error label element

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            # 椤堕儴鏍?            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(f'/result?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('蹇冪悊璇勪及').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["primary_dark"]}'
                )

            with ui.column().style('padding:20px 20px 100px; gap:8px; width:100%'):
                ui.label('璇锋牴鎹垰鎵嶆煡鐪嬫敼閫犲悗鐜鐨勬劅鍙楋紝鍥炵瓟浠ヤ笅闂銆?).classes('animate-in').style(
                    f'font-size:14px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                # PRS 鎭㈠鎬ф劅鐭ラ噺琛?                with ui.card().classes('glass-card animate-in animate-in-delay-1').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('馃', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('鎭㈠鎬ф劅鐭ワ紙PRS锛?).style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    prs_items = [
                        ('prs1', '杩欎釜鐜璁╂垜鎰熷埌鏀炬澗'),
                        ('prs2', '杩欎釜鐜鑳藉府鍔╂垜鎭㈠娉ㄦ剰鍔?),
                        ('prs3', '鎴戞効鎰忓湪杩欐牱鐨勭幆澧冧腑鍋滅暀'),
                        ('prs4', '杩欎釜鐜璁╂垜鏆傛椂蹇樿鏃ュ父鐑︽伡'),
                        ('prs5', '杩欎釜鐜缁欐垜涓€绉?杩滅"鐨勬劅瑙?),
                    ]
                    prs_labels = ['瀹屽叏涓嶅悓鎰?, '涓嶅悓鎰?, '涓€鑸?, '鍚屾剰', '瀹屽叏鍚屾剰']

                    for item_id, question in prs_items:
                        ui.label(question).style(
                            f'font-size:14px; line-height:1.5; margin-top:12px; color:{COLORS["primary_dark"]}'
                        )
                        _build_likert(item_id, prs_labels, answers, error_labels)

                # 鎯呯华璇勫垎
                with ui.card().classes('glass-card animate-in animate-in-delay-2').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('馃挌', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('鎯呯华鐘舵€?).style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    emo_items = [
                        ('emo1', '骞抽潤鐨?),
                        ('emo2', '鎰夋偊鐨?),
                        ('emo3', '鍏呮弧娲诲姏鐨?),
                        ('emo4', '鏀炬澗鐨?),
                    ]
                    emo_labels = ['寰堝皯', '杈冨皯', '涓€鑸?, '杈冨', '寰堝']

                    for item_id, question in emo_items:
                        ui.label(question).style(
                            f'font-size:14px; margin-top:12px; color:{COLORS["primary_dark"]}'
                        )
                        _build_likert(item_id, emo_labels, answers, error_labels)

                # 鏁翠綋婊℃剰搴?                with ui.card().classes('glass-card animate-in animate-in-delay-3').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('猸?, 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('鏁翠綋婊℃剰搴?).style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}'
                        )
                    ui.element('div').classes('section-divider')

                    star_label = ui.label('鈽嗏槅鈽嗏槅鈽?).style(
                        f'font-size:32px; text-align:center; width:100%; letter-spacing:6px;'
                        f'color:{COLORS["accent"]};'
                    )

                    # 涓嶈榛樿鍊?鈥?蹇呴』涓诲姩閫夋嫨
                    star_btns = []
                    with ui.row().style('width:100%; justify-content:center; gap:8px; margin:8px 0;'):
                        for val in range(1, 6):
                            sbtn = ui.button(
                                str(val), on_click=lambda v=val: select_star(v)
                            ).props('outline round dense').style(
                                f'width:44px; height:44px; font-size:16px; font-weight:600;'
                                'border:1.5px solid rgba(47,123,88,0.20); color:rgba(23,49,38,0.62);'
                                'background:rgba(255,255,248,0.64);'
                                'transition:all 0.2s;'
                            )
                            star_btns.append((sbtn, val))

                    star_err = ui.label('璇烽€夋嫨婊℃剰搴?).style(
                        f'display:none; font-size:11px; color:{COLORS["error"]}; margin-top:2px;'
                    )
                    error_labels['overall'] = star_err

                    def select_star(val):
                        answers['overall'] = val
                        star_label.set_text('鈽? * val + '鈽? * (5 - val))
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
                                    'border:1.5px solid rgba(47,123,88,0.20); color:rgba(23,49,38,0.62);'
                                    'background:rgba(255,255,248,0.64);'
                                )

                    with ui.row().style(
                        f'width:100%; justify-content:space-between; font-size:11px; color:{COLORS["text_secondary"]};'
                        'font-weight:300;'
                    ):
                        ui.label('涓嶆弧鎰?)
                        ui.label('涓€鑸?)
                        ui.label('闈炲父婊℃剰')

                # 寮€鏀惧弽棣?                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:18px; border:none !important; margin-top:8px'
                ):
                    with ui.row().style('align-items:center; gap:6px'):
                        ui.html(get_svg('馃挰', 18)).style('width:18px; height:18px; flex-shrink:0;')
                        ui.label('鍏朵粬鎯虫硶鎴栧缓璁紙閫夊～锛?).style(
                            f'font-size:14px; font-weight:600; color:{COLORS["primary_dark"]}; margin-bottom:8px'
                        )
                    feedback = ui.textarea(placeholder='璇疯緭鍏ヤ綘鐨勬兂娉?..').style(
                        'width:100%; min-height:80px; border-radius:14px;'
                    )

                # 鎻愪氦鎸夐挳
                submit_btn = ui.button('鎻愪氦璇勪及 鈫?, on_click=lambda: submit()).props(
                    'no-caps unelevated'
                ).style(LIGHT_PRIMARY_BTN_STYLE + 'margin-top:12px;')

                def submit():
                    # 蹇呯瓟鏍￠獙
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
                        ui.notify(f'璇峰畬鎴愭墍鏈夊繀绛旈锛堣繕鏈?{len(missing)} 棰樻湭浣滅瓟锛?, type='warning')
                        return

                    answers['feedback'] = feedback.value
                    if session:
                        session.survey_answers = answers
                        session.survey_completed_at = time.time()
                    smooth_navigate(f'/report?sid={sid}')
