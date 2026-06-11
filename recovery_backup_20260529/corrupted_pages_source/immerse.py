"""娌夋蹈寮忕枟鎰堝睍绀洪〉闈?- 鍏ㄥ睆鐜闊?+ 鍛煎惛寮曞"""
from nicegui import ui, app
from pathlib import Path
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT
from app.state import get_session
from app.db import log_interaction
from app.components.nav import bottom_nav, smooth_navigate


def create_immerse_page():
    @ui.page('/immerse')
    def immerse_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        if not session or not session.generated_image_path:
            smooth_navigate(f'/result?sid={sid}')
            return

        log_interaction(sid, 'immerse_enter')
        bottom_nav()

        # 鍏ㄥ睆娌夋蹈寮忔牱寮?        ui.add_head_html('''
        <style>
            .immerse-page {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #000; display: flex; flex-direction: column;
                align-items: center; justify-content: center; z-index: 9999;
                overflow: hidden;
            }
            .immerse-bg {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                object-fit: cover; opacity: 0;
                animation: immerseFadeIn 3s ease-out forwards;
            }
            @keyframes immerseFadeIn {
                to { opacity: 1; }
            }
            .breath-circle {
                width: 80px; height: 80px; border-radius: 50%;
                border: 3px solid rgba(255,255,255,0.6);
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(8px);
                animation: breathe 8s ease-in-out infinite;
                position: relative; z-index: 2;
            }
            @keyframes breathe {
                0%, 100% { transform: scale(0.6); opacity: 0.5; }
                50% { transform: scale(1.4); opacity: 1; }
            }
            .breath-text {
                position: relative; z-index: 2; color: rgba(255,255,255,0.85);
                font-size: 15px; font-weight: 300; letter-spacing: 1px;
                text-shadow: 0 2px 8px rgba(0,0,0,0.5);
                animation: breatheText 8s ease-in-out infinite;
            }
            @keyframes breatheText {
                0%, 100% { opacity: 0.6; }
                25% { opacity: 1; }
                50% { opacity: 0.6; }
                75% { opacity: 1; }
            }
            .immerse-overlay {
                position: relative; z-index: 2; display: flex; flex-direction: column;
                align-items: center; gap: 24px; padding: 20px;
            }
            .immerse-guide {
                color: rgba(255,255,255,0.7); font-size: 13px; font-weight: 300;
                text-shadow: 0 1px 6px rgba(0,0,0,0.4); letter-spacing: 0.5px;
                animation: immerseFadeIn 4s ease-out forwards;
            }
            .immerse-btn {
                opacity: 0; pointer-events: none;
                transition: opacity 0.8s ease;
            }
            .immerse-btn.show {
                opacity: 1; pointer-events: auto;
            }
        </style>
        ''')

        # 鑾峰彇鍥剧墖URL
        fname = Path(session.generated_image_path).name
        img_url = f'/api/image/{fname}'

        # 鏍规嵁鍙傛暟閫夋嫨鐜闊?        green = session.green_level
        # 浣跨敤鍏嶈垂鐨勮嚜鐒堕煶鏁堬紙鐭惊鐜級
        audio_sources = []
        if green > 50:
            audio_sources.append('https://cdn.freesound.org/previews/531/531947_6456385-lq.mp3')  # birds
        audio_sources.append('https://cdn.freesound.org/previews/402/402735_1415754-lq.mp3')  # nature ambient

        with ui.element('div').classes('immerse-page'):
            # 鑳屾櫙鍥?            ui.image(img_url).classes('immerse-bg')

            # 閬僵灞?            with ui.element('div').style(
                'position:absolute; top:0; left:0; width:100%; height:100%;'
                'background:radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.3) 100%);'
                'z-index:1;'
            ):
                pass

            # 鍛煎惛寮曞
            with ui.element('div').classes('immerse-overlay'):
                ui.label('璇锋敞瑙嗙敾闈紝璺熼殢鍦嗗湀娣卞懠鍚?).classes('breath-text')
                ui.element('div').classes('breath-circle')

                # 鍛煎惛鎻愮ず鏂囧瓧
                breath_label = ui.label('鍚告皵...').classes('immerse-guide').style(
                    'animation: breatheText 8s ease-in-out infinite;'
                )

                # 缁х画鎸夐挳锛堝欢杩熸樉绀猴級
                continue_btn = ui.button(
                    '缁х画璇勪及 鈫?,
                    on_click=lambda: go_survey()
                ).props('no-caps unelevated').style(
                    'border-radius:28px; padding:12px 32px;'
                    'background:rgba(255,255,255,0.2); backdrop-filter:blur(12px);'
                    'color:white; font-weight:500; border:1px solid rgba(255,255,255,0.3);'
                ).classes('immerse-btn')

            # 闊抽鎾斁
            for src in audio_sources:
                ui.add_body_html(
                    f'<audio autoplay loop style="display:none">'
                    f'<source src="{src}" type="audio/mpeg"></audio>'
                )

        # 30绉掑悗鏄剧ず缁х画鎸夐挳
        ui.timer(30.0, lambda: continue_btn.classes('show', remove=''), once=True)

        # 鍛煎惛鏂囧瓧鍒囨崲
        breath_state = {'phase': 0}

        def update_breath():
            phases = ['鍚告皵...', '淇濇寔...', '鍛兼皵...', '淇濇寔...']
            breath_state['phase'] = (breath_state['phase'] + 1) % 4
            breath_label.set_text(phases[breath_state['phase']])

        ui.timer(2.0, update_breath)

        def go_survey():
            log_interaction(sid, 'immerse_exit')
            smooth_navigate(f'/survey?sid={sid}')
