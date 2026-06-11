"""鐤楁剤鎶ュ憡椤甸潰 - 楂樼骇 UI"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT
from app.state import get_session
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate


def create_report_page():
    @ui.page('/report')
    def report_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        answers = session.survey_answers if session else {}

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            # 椤堕儴鏍?            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('鐤楁剤鎶ュ憡').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["primary_dark"]}'
                )

            with ui.column().style('padding:20px 20px 100px; gap:16px; width:100%'):
                # 澶撮儴
                with ui.column().classes('glass-card animate-in').style(
                    'width:100%; text-align:center; padding:32px 20px;'
                    'border-radius:24px; align-items:center; position:relative; z-index:1;'
                    'background:linear-gradient(180deg,rgba(255,255,248,0.86),rgba(237,246,230,0.82)),'
                    'url("/static/images/light-bamboo-paper.webp") center/cover no-repeat !important;'
                ):
                    ui.html(get_svg('馃尶hero', 52)).classes('float-animation').style(
                        'width:52px; height:52px;'
                        'filter:drop-shadow(0 4px 8px rgba(47,123,88,0.16));'
                    )
                    ui.label('鏈鐤楁剤鎶ュ憡').style(
                        f'font-size:22px; font-weight:700; color:{COLORS["primary_dark"]}; margin-top:8px;'
                        'letter-spacing:1px;'
                    )
                    ui.element('div').style(
                        'width:40px; height:2px; background:rgba(47,123,88,0.42);'
                        'border-radius:1px; margin-top:12px;'
                    )

                # 璇勫垎姹囨€?                ui.label('璇勪及缁撴灉').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}; letter-spacing:0.5px'
                )
                ui.element('div').classes('section-divider')

                # 璁＄畻鍒嗘暟
                prs_scores = [answers.get(f'prs{i}', 0) for i in range(1, 6)]
                prs_avg = sum(prs_scores) / max(len([s for s in prs_scores if s > 0]), 1)

                emo_scores = [answers.get(f'emo{i}', 0) for i in range(1, 5)]
                emo_avg = sum(emo_scores) / max(len([s for s in emo_scores if s > 0]), 1)

                overall = answers.get('overall', 0)

                with ui.row().classes('animate-in animate-in-delay-1').style(
                    'width:100%; gap:10px'
                ):
                    score_configs = [
                        ('鎭㈠鎬ф劅鐭?, f'{prs_avg:.1f}' if prs_avg > 0 else '--', '#2F7B58',
                         'linear-gradient(135deg, #2F7B58, #94C978)'),
                        ('鎯呯华鏀瑰杽', f'{emo_avg:.1f}' if emo_avg > 0 else '--', COLORS['accent'],
                         f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]})'),
                        ('鏁翠綋婊℃剰', '鈽? * overall if overall > 0 else '--', COLORS['accent_light'],
                         f'linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["primary_ultra_light"]})'),
                    ]
                    for label, value, color, gradient in score_configs:
                        with ui.card().classes('glass-card').style(
                            'flex:1; padding:16px 8px; text-align:center; border:none !important;'
                            'overflow:hidden; position:relative;'
                        ):
                            # 椤堕儴娓愬彉鑹插甫
                            ui.element('div').style(
                                f'position:absolute; top:0; left:0; width:100%; height:3px; background:{gradient};'
                            )
                            ui.label(value).style(
                                f'font-size:22px; font-weight:700; color:{color}; margin-top:4px'
                            )
                            ui.label(label).style(
                                f'font-size:11px; color:{COLORS["text_secondary"]}; margin-top:6px; font-weight:400'
                            )

                # 鐜鍋忓ソ
                ui.label('浣犵殑鐜鍋忓ソ').classes('animate-in animate-in-delay-2').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}; margin-top:4px;'
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
                        ('馃尶', '缁垮寲绋嬪害', green, '#2F7B58'),
                        ('馃彈锔?, '浜洪€犲厓绱?, urban, COLORS['secondary']),
                        ('馃懃', '鐜娲诲姏', vitality, COLORS['accent']),
                        ('鈽€锔?, '鍏夌嚎姘涘洿', light, COLORS['accent_light']),
                    ]:
                        with ui.column().style('width:100%; gap:4px; margin-bottom:12px'):
                            with ui.row().style('width:100%; justify-content:space-between; align-items:center'):
                                with ui.row().style('align-items:center; gap:6px'):
                                    svg = get_svg(icon_key, 16)
                                    if svg:
                                        ui.html(svg).style('width:16px; height:16px; flex-shrink:0;')
                                    ui.label(label).style(
                                        f'font-size:13px; color:{COLORS["primary_dark"]}; font-weight:500'
                                    )
                                ui.label(f'{int(val)}%').style(
                                    f'font-size:14px; font-weight:700; color:{color}'
                                )
                            with ui.element('div').classes('progress-bar'):
                                ui.element('div').classes('progress-bar-fill').style(
                                    f'width:{int(val)}%; background:linear-gradient(90deg, {color}, {color}88);'
                                )

                # 鐤楁剤寤鸿
                with ui.row().classes('animate-in animate-in-delay-3').style(
                    'align-items:center; gap:6px'
                ):
                    ui.html(get_svg('馃挕', 18)).style('width:18px; height:18px; flex-shrink:0;')
                    ui.label('鐤楁剤寤鸿').style(
                        f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}; letter-spacing:0.5px'
                    )

                if green < 30:
                    advice = ('浣犲綋鍓嶇殑鐜缁垮寲绋嬪害鍋忎綆銆傚缓璁湪鏃ュ父鐢熸椿涓鍔犳帴瑙﹁嚜鐒剁殑鏈轰細锛?
                              '鍗充娇鏄畝鍗曠殑瀹ゅ唴缁挎鎴栫獥澶栫豢鏅篃鏈夊姪浜庢敞鎰忓姏鎭㈠銆?)
                elif green <= 60:
                    advice = ('浣犻€夋嫨浜嗕腑绛夋按骞崇殑缁垮寲鈥斺€旇繖鍙兘鏄渶浣崇殑"鐤楁剤鐢滆湝鐐?銆?
                              '閫傚害鐨勮嚜鐒跺厓绱犳棦鑳芥彁渚涙仮澶嶆€у埡婵€锛屽張涓嶄細閫犳垚淇℃伅杩囪浇銆?)
                else:
                    advice = ('浣犲亸濂介珮搴﹁嚜鐒跺寲鐨勭幆澧冦€傛矇娴稿紡鐨勭豢鑹茬┖闂村鍘嬪姏鎭㈠鐗瑰埆鏈夋晥锛?
                              '寤鸿瀹氭湡鍓嶅線鍏洯鎴栬嚜鐒朵繚鎶ゅ尯杩涜"鑷劧娴?銆?)

                with ui.card().classes('glass-card animate-in animate-in-delay-3').style(
                    'width:100%; padding:18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important;'
                ):
                    ui.label(advice).style(
                        f'font-size:14px; line-height:1.8; color:{COLORS["primary_dark"]}; font-weight:400'
                    )

                # 绉戝瑙ｈ
                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:16px 18px; border:none !important;'
                    f'background:rgba(45,106,79,0.04) !important;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:6px'):
                        ui.html(get_svg('馃摎', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('绉戝瑙ｈ').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '鏍规嵁娉ㄦ剰鍔涙仮澶嶇悊璁?Kaplan, 1989)锛岄€傚害鐨勮嚜鐒剁幆澧冭兘澶熼€氳繃"鏌旀€ф敞鎰忓姏"鏈哄埗'
                        '甯姪鎭㈠瀹氬悜娉ㄦ剰鍔涖€備綘閫夋嫨鐨勭幆澧冨弬鏁扮粍鍚堢鍚堟仮澶嶆€х幆澧冪殑鏍稿績鐗瑰緛銆?
                    ).style(
                        f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.8; font-weight:300'
                    )

                # 鎸夐挳
                ui.button('鍥炲埌棣栭〉', on_click=lambda: smooth_navigate('/')).props(
                    'no-caps unelevated'
                ).style(LIGHT_PRIMARY_BTN_STYLE + 'margin-top:8px;')

                ui.button('鍐嶆浣撻獙', on_click=lambda: smooth_navigate('/camera')).props(
                    'outline no-caps'
                ).style(
                    'width:100%; border-radius:28px; color:#2F7B58;'
                    'border:1.5px solid rgba(47,123,88,0.28); padding:14px; font-weight:650;'
                    'background:rgba(255,255,248,0.62);'
                    'transition:all 0.3s;'
                )
