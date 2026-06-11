"""鏅鸿兘鎺ㄨ崘妯″紡椤甸潰 - 楂樼骇 UI"""
import asyncio
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session, save_output
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate


def create_ai_mode_page():
    @ui.page('/ai-mode')
    def ai_mode_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'ai'
        state = {'selected': ''}

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            # 椤堕儴鏍?            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(f'/mode-select?sid={sid}')).props(
                    'flat round dense'
                ).style('color:#2F7B58')
                ui.label('鏅鸿兘鎺ㄨ崘').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["primary_dark"]}'
                )

            with ui.column().style('padding:20px 20px 100px; gap:14px; width:100%'):
                # 棰勮鍥?                if session and session.uploaded_image_path:
                    fname = Path(session.uploaded_image_path).name
                    with ui.element('div').classes('animate-in').style(
                        'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    ):
                        ui.image(f'/api/image/{fname}').style(
                            'width:100%; border-radius:20px; height:180px; object-fit:cover;'
                        )

                ui.label('AI鎺ㄨ崘鏂规').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}; letter-spacing:0.5px'
                )
                ui.element('div').classes('section-divider')
                ui.label('鍩轰簬鐜蹇冪悊瀛︾爺绌剁粨璁猴紝浠ヤ笅鏂规缁忚繃绉戝楠岃瘉锛屽蹇冪悊鎭㈠鍏锋湁绉瀬鏁堟灉銆?).style(
                    f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                schemes = [
                    {
                        'id': 'nature', 'icon': '馃尶', 'title': '鑷劧鍜岃皭鏂规',
                        'desc': '涓瓑缁垮寲 + 浣庝汉閫犲厓绱狅紝妯℃嫙鑷劧鍏洯鐜锛屾渶澶у寲娉ㄦ剰鍔涙仮澶嶆晥鏋?,
                        'green': 55, 'urban': 25, 'vitality': 40, 'light': 55,
                        'evidence': '娉ㄦ剰鍔涙仮澶嶇悊璁?ART): 鑷劧鐜閫氳繃"鏌旀€ф敞鎰忓姏"淇冭繘璁ょ煡鎭㈠',
                        'gradient': 'linear-gradient(135deg, #2F7B58, #94C978)',
                    },
                    {
                        'id': 'urban', 'icon': '馃彊锔?, 'title': '娲诲姏閮藉競鏂规',
                        'desc': '涓瓑缁垮寲 + 涓瓑浜洪€犲厓绱?+ 閫傚害娲诲姏锛岄€傚悎鍩庡競琛楀尯鏀归€?,
                        'green': 45, 'urban': 50, 'vitality': 55, 'light': 50,
                        'evidence': '鍊扷鍨嬫晥搴? 涓瓑澶嶆潅搴︾殑鍩庡競鐜鎭㈠鎬у彲鑳戒紭浜庢瀬绠€鎴栨瀬绻佺幆澧?,
                        'gradient': f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]})',
                    },
                    {
                        'id': 'zen', 'icon': '馃', 'title': '瀹侀潤绂呮剰鏂规',
                        'desc': '楂樼豢鍖?+ 浣庝汉閫犲厓绱?+ 浣庢椿鍔涳紝鍒涢€犳矇娴稿紡瀹侀潤绌洪棿',
                        'green': 70, 'urban': 15, 'vitality': 20, 'light': 45,
                        'evidence': '鍘嬪姏鎭㈠鐞嗚(SRT): 浣庡敜閱掔殑鑷劧鍦烘櫙鏈夊姪浜庨檷浣庣敓鐞嗗簲婵€姘村钩',
                        'gradient': f'linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["primary_ultra_light"]})',
                    },
                ]

                scheme_cards = {}
                for idx, scheme in enumerate(schemes):
                    card = ui.card().classes(
                        f'glass-card hover-lift card-press animate-in animate-in-delay-{idx+1}'
                    ).style(
                        'width:100%; padding:0; cursor:pointer; border:2px solid transparent !important;'
                        'overflow:hidden; transition:all 0.3s;'
                    ).on('click', lambda s=scheme: select_scheme(s))

                    scheme_cards[scheme['id']] = card

                    with card:
                        # 椤堕儴娓愬彉鑹插甫
                        ui.element('div').style(
                            f'width:100%; height:4px; background:{scheme["gradient"]};'
                        )
                        with ui.column().style('padding:16px 18px; gap:8px'):
                            with ui.row().style('align-items:center; gap:8px'):
                                scheme_svg = get_svg(scheme['icon'], 20)
                                if scheme_svg:
                                    ui.html(scheme_svg).style('width:20px; height:20px; flex-shrink:0;')
                                ui.label(scheme['title']).style(
                                    f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}'
                                )
                            ui.label(scheme['desc']).style(
                                f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.6; font-weight:300'
                            )
                            # 鍙傛暟鑽父
                            with ui.row().style('gap:6px; flex-wrap:wrap'):
                                params = [
                                    (f'缁垮寲 {scheme["green"]}%', '#2F7B58'),
                                    (f'浜洪€?{scheme["urban"]}%', COLORS['accent']),
                                    (f'娲诲姏 {scheme["vitality"]}%', COLORS['secondary']),
                                ]
                                for plabel, pcolor in params:
                                    ui.label(plabel).classes('tag-pill').style(
                                        f'background:{pcolor}12; color:{pcolor}; font-weight:500;'
                                    )
                            # 鐞嗚渚濇嵁
                            with ui.element('div').style(
                                f'width:100%; padding:8px 12px; border-radius:12px;'
                                f'background:{COLORS["primary"]}06; margin-top:4px;'
                            ):
                                ui.html(f'{get_svg("馃摎", 12)}<span style="margin-left:4px; font-size:11px; color:{COLORS["text_secondary"]}; line-height:1.5; font-weight:300">{scheme["evidence"]}</span>').style(
                                    'display:flex; align-items:flex-start;'
                                )

                def select_scheme(scheme):
                    state['selected'] = scheme['id']
                    for sid_key, c in scheme_cards.items():
                        if sid_key == scheme['id']:
                            c.style(
                                f'width:100%; padding:0; cursor:pointer; overflow:hidden;'
                                'border:2px solid #2F7B58 !important;'
                                'box-shadow:0 0 0 4px rgba(47,123,88,0.12), 0 8px 32px rgba(27,67,50,0.12) !important;'
                                'transform:scale(1.01);'
                            )
                        else:
                            c.style(
                                'width:100%; padding:0; cursor:pointer; overflow:hidden;'
                                'border:2px solid transparent !important;'
                            )
                    gen_btn.set_visibility(True)
                    if session:
                        session.green_level = scheme['green']
                        session.urban_level = scheme['urban']
                        session.vitality_level = scheme['vitality']
                        session.light_warmth = scheme['light']
                        session.selected_recommend = scheme['id']

                # 閿欒鎻愮ず
                error_label = ui.label().style(
                    f'display:none; padding:12px 16px; background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                    f'font-size:13px; color:{COLORS["error"]}; width:100%'
                )
                loading_card = ui.element('div').style('display:none;').classes('glass-card')
                with loading_card:
                    with ui.column().style('width:100%; padding:24px; text-align:center; align-items:center'):
                        ui.spinner('dots', size='lg', color=COLORS['primary'])
                        ui.label('AI 姝ｅ湪鐢熸垚鎺ㄨ崘鍦烘櫙...').style(
                            f'font-size:15px; color:{COLORS["primary_dark"]}; margin-top:12px; font-weight:500'
                        )

                gen_btn = ui.button('鉁?涓€閿敓鎴愭帹鑽愬満鏅?, on_click=lambda: generate()).props(
                    'no-caps unelevated'
                ).style(LIGHT_PRIMARY_BTN_STYLE + 'margin-top:8px;')
                gen_btn.set_visibility(False)

                async def generate():
                    if not session or not session.uploaded_image_path:
                        ui.notify('璇峰厛涓婁紶鍥剧墖', type='warning')
                        return

                    gen_btn.set_visibility(False)
                    loading_card.style('display:block; width:100%; border-radius:20px;')
                    error_label.style('display:none')

                    try:
                        from app.services.sd_service import generate_from_sliders
                        result_bytes, used_prompt = await asyncio.to_thread(
                            generate_from_sliders,
                            session.uploaded_image_path,
                            session.green_level, session.urban_level,
                            session.vitality_level, session.light_warmth,
                        )
                        session.llm_prompt = used_prompt
                        save_output(sid, result_bytes)
                        smooth_navigate(f'/result?sid={sid}')
                    except Exception as e:
                        error_label.set_text(f'鐢熸垚澶辫触: {str(e)}')
                        error_label.style(
                            f'display:block; padding:12px 16px; background:{COLORS["error"]}10;'
                            f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                            f'font-size:13px; color:{COLORS["error"]}; width:100%'
                        )
                        gen_btn.set_visibility(True)
                        loading_card.style('display:none')

                # 鐞嗚璇存槑
                with ui.card().classes('glass-card').style(
                    'width:100%; padding:14px 18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important; margin-top:8px;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:4px'):
                        ui.html(get_svg('馃敩', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('鏂规渚濇嵁').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '鎺ㄨ崘鍙傛暟灏嗗熀浜?脳3脳3瀹為獙锛堝満鏅被鍨嬅楃豢鍖栫▼搴γ椾汉閫犲厓绱犱赴瀵屽害锛夌殑缁撹鍔ㄦ€佹洿鏂般€?
                        '褰撳墠涓哄垵濮嬮璁惧€硷紝瀹為獙瀹屾垚鍚庡皢鏇挎崲涓哄疄闄呮渶浼樺弬鏁扮粍鍚堛€?
                    ).style(f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300')
