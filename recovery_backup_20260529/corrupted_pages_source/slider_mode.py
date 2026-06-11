"""婊戞潌璋冨弬妯″紡椤甸潰 - 楂樼骇 UI"""
import asyncio
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session, save_output
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate


def create_slider_page():
    @ui.page('/slider-mode')
    def slider_mode_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'slider'

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            # 椤堕儴鏍?            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(f'/mode-select?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('鍙傛暟璋冭妭').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["primary_dark"]}'
                )

            with ui.column().style('padding:20px; gap:12px; width:100%; padding-bottom:100px'):
                # 棰勮鍥?                if session and session.uploaded_image_path:
                    fname = Path(session.uploaded_image_path).name
                    with ui.element('div').classes('animate-in').style(
                        'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    ):
                        ui.image(f'/api/image/{fname}').style(
                            'width:100%; border-radius:20px; aspect-ratio:4/3; object-fit:cover;'
                        )

                # 鐢熸垚涓伄缃?                loading_card = ui.element('div').style(
                    'display:none; width:100%; padding:28px; text-align:center;'
                    f'border-radius:20px;'
                ).classes('glass-card')
                with loading_card:
                    ui.spinner('dots', size='lg', color=COLORS['primary'])
                    ui.label('AI 鐢熸垚涓?..').style(
                        f'font-size:15px; color:{COLORS["primary_dark"]}; margin-top:12px; font-weight:500'
                    )
                    ui.label('棣栨鐢熸垚闇€鍔犺浇妯″瀷锛屽彲鑳介渶瑕?-3鍒嗛挓').style(
                        f'font-size:12px; color:{COLORS["text_secondary"]}; margin-top:4px; font-weight:300'
                    )

                # 鍙傛暟婊戞潌缁?                ui.label('璋冭妭鐜鍙傛暟').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["primary_dark"]}; margin-top:8px;'
                    'letter-spacing:0.5px;'
                )
                ui.element('div').classes('section-divider')

                sliders_config = [
                    ('green', '馃尶', '缁垮寲绋嬪害', '浣?, '涓?, '楂?, '鎺у埗妞嶈瑕嗙洊鐜?, '#2F7B58'),
                    ('urban', '馃彈锔?, '浜洪€犲厓绱?, '浣?, '涓?, '楂?, '鎺у埗浜哄伐璁炬柦瀵嗗害', COLORS['secondary']),
                    ('vitality', '馃懃', '鐜娲诲姏', '瀹侀潤', '閫傚害', '鐑椆', '鎺у埗浜烘祦涓庢椿鍔ㄦ劅', COLORS['accent']),
                    ('light', '鈽€锔?, '鍏夌嚎姘涘洿', '鍐疯壊', '鑷劧', '鏆栬壊', '璋冭妭鑹叉俯涓庡厜绾?, COLORS['accent_light']),
                ]

                slider_values = {}
                for idx, (key, icon, label, low, mid, high, desc, color) in enumerate(sliders_config):
                    with ui.card().classes(f'glass-card animate-in animate-in-delay-{idx+1}').style(
                        'width:100%; padding:16px 18px; border:none !important; margin-bottom:4px;'
                    ):
                        with ui.row().style('width:100%; justify-content:space-between; align-items:center'):
                            with ui.row().style('align-items:center; gap:6px'):
                                svg = get_svg(icon, 18)
                                if svg:
                                    ui.html(svg).style('width:18px; height:18px; flex-shrink:0;')
                                ui.label(label).style('font-size:14px; font-weight:600;')
                            val_label = ui.label('50%').style(
                                f'font-size:16px; font-weight:700; color:{color};'
                                'min-width:48px; text-align:right;'
                            )

                        s = ui.slider(min=0, max=100, value=50, step=1).style('width:100%').props(
                            f'color=green label'
                        )
                        slider_values[key] = s

                        def make_updater(lbl):
                            def updater(e):
                                lbl.set_text(f'{int(e.value)}%')
                            return updater
                        s.on('update:model-value', make_updater(val_label))

                        with ui.row().style(
                            f'width:100%; justify-content:space-between; font-size:11px; color:{COLORS["text_secondary"]};'
                            'font-weight:300;'
                        ):
                            ui.label(low)
                            ui.label(mid)
                            ui.label(high)

                # 閿欒鎻愮ず
                error_label = ui.label().style(
                    f'display:none; padding:12px 16px; background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                    f'font-size:13px; color:{COLORS["error"]}; width:100%'
                )

                # 鐞嗚渚濇嵁
                with ui.card().classes('glass-card').style(
                    'width:100%; padding:14px 18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important; margin-top:8px;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:4px'):
                        ui.html(get_svg('馃敩', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('鍊扷鍨嬫晥搴斿亣璁?).style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '鐮旂┒鍋囪涓瓑姘村钩鐨勭豢鍖栧拰浜洪€犲厓绱犲彲鑳藉叿鏈夋渶浣崇殑蹇冪悊鎭㈠鏁堟灉鈥斺€?
                        '杩囧皯缂轰箯鑷劧鐤楁剤鍏冪礌锛岃繃澶氬垯淇℃伅杩囪浇銆傛粦鏉嗕腑闂村尯鍩熷彲鑳芥槸"鐢滆湝鐐?銆?
                    ).style(f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300')

            # 鍥哄畾搴曢儴鐢熸垚鎸夐挳
            with ui.row().classes('light-action-panel light-bottom-dock'):
                gen_btn = ui.button('鐢熸垚鏀归€犲満鏅?, on_click=lambda: generate()).props(
                    'no-caps unelevated'
                ).style(LIGHT_PRIMARY_BTN_STYLE)

            async def generate():
                if not session or not session.uploaded_image_path:
                    ui.notify('璇峰厛涓婁紶鍥剧墖', type='warning')
                    return

                gen_btn.set_visibility(False)
                loading_card.style(
                    'display:block; width:100%; padding:28px; text-align:center; border-radius:20px;'
                )
                error_label.style('display:none')

                green = slider_values['green'].value
                urban = slider_values['urban'].value
                vitality = slider_values['vitality'].value
                light = slider_values['light'].value

                session.green_level = green
                session.urban_level = urban
                session.vitality_level = vitality
                session.light_warmth = light

                try:
                    from app.services.sd_service import generate_from_sliders
                    result_bytes, used_prompt = await asyncio.to_thread(
                        generate_from_sliders,
                        session.uploaded_image_path, green, urban, vitality, light,
                    )
                    session.llm_prompt = used_prompt
                    out_path = save_output(sid, result_bytes)
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
