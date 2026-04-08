"""滑杆调参模式页面 - 高级 UI"""
import asyncio
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session, save_output
from app.components.icons import get_svg


def create_slider_page():
    @ui.page('/slider-mode')
    def slider_mode_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'slider'

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/mode-select?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('参数调节').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:12px; width:100%; padding-bottom:100px'):
                # 预览图
                if session and session.uploaded_image_path:
                    fname = Path(session.uploaded_image_path).name
                    with ui.element('div').classes('animate-in').style(
                        'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    ):
                        ui.image(f'/api/image/{fname}').style(
                            'width:100%; border-radius:20px; aspect-ratio:4/3; object-fit:cover;'
                        )

                # 生成中遮罩
                loading_card = ui.element('div').style(
                    'display:none; width:100%; padding:28px; text-align:center;'
                    f'border-radius:20px;'
                ).classes('glass-card')
                with loading_card:
                    ui.spinner('dots', size='lg', color=COLORS['primary'])
                    ui.label('AI 生成中...').style(
                        f'font-size:15px; color:{COLORS["text"]}; margin-top:12px; font-weight:500'
                    )
                    ui.label('首次生成需加载模型，可能需要1-3分钟').style(
                        f'font-size:12px; color:{COLORS["text_secondary"]}; margin-top:4px; font-weight:300'
                    )

                # 参数滑杆组
                ui.label('调节环境参数').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}; margin-top:8px;'
                    'letter-spacing:0.5px;'
                )
                ui.element('div').classes('section-divider')

                sliders_config = [
                    ('green', '🌿', '绿化程度', '低', '中', '高', '控制植被覆盖率', COLORS['primary']),
                    ('urban', '🏗️', '人造元素', '低', '中', '高', '控制人工设施密度', COLORS['secondary']),
                    ('vitality', '👥', '环境活力', '宁静', '适度', '热闹', '控制人流与活动感', COLORS['accent']),
                    ('light', '☀️', '光线氛围', '冷色', '自然', '暖色', '调节色温与光线', COLORS['accent_light']),
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

                # 错误提示
                error_label = ui.label().style(
                    f'display:none; padding:12px 16px; background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                    f'font-size:13px; color:{COLORS["error"]}; width:100%'
                )

                # 理论依据
                with ui.card().classes('glass-card').style(
                    'width:100%; padding:14px 18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important; margin-top:8px;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:4px'):
                        ui.html(get_svg('🔬', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('倒U型效应假设').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '研究假设中等水平的绿化和人造元素可能具有最佳的心理恢复效果——'
                        '过少缺乏自然疗愈元素，过多则信息过载。滑杆中间区域可能是"甜蜜点"。'
                    ).style(f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300')

            # 固定底部生成按钮
            with ui.row().style(
                'position:fixed; bottom:0; left:50%; transform:translateX(-50%);'
                'width:100%; max-width:480px; padding:12px 20px 24px 20px;'
                'background:rgba(248,250,245,0.9); backdrop-filter:blur(20px);'
                '-webkit-backdrop-filter:blur(20px); border-top:1px solid rgba(45,106,79,0.08);'
                'z-index:50;'
            ):
                gen_btn = ui.button('生成改造场景', on_click=lambda: generate()).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE)

            async def generate():
                if not session or not session.uploaded_image_path:
                    ui.notify('请先上传图片', type='warning')
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
                    result_bytes = await asyncio.to_thread(
                        generate_from_sliders,
                        session.uploaded_image_path, green, urban, vitality, light,
                    )
                    out_path = save_output(sid, result_bytes)
                    ui.navigate.to(f'/result?sid={sid}')
                except Exception as e:
                    error_label.set_text(f'生成失败: {str(e)}')
                    error_label.style(
                        f'display:block; padding:12px 16px; background:{COLORS["error"]}10;'
                        f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                        f'font-size:13px; color:{COLORS["error"]}; width:100%'
                    )
                    gen_btn.set_visibility(True)
                    loading_card.style('display:none')
