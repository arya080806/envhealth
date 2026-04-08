"""智能推荐模式页面 - 高级 UI"""
import asyncio
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session, save_output
from app.components.icons import get_svg


def create_ai_mode_page():
    @ui.page('/ai-mode')
    def ai_mode_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'ai'
        state = {'selected': ''}

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/mode-select?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('智能推荐').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:14px; width:100%'):
                # 预览图
                if session and session.uploaded_image_path:
                    fname = Path(session.uploaded_image_path).name
                    with ui.element('div').classes('animate-in').style(
                        'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    ):
                        ui.image(f'/api/image/{fname}').style(
                            'width:100%; border-radius:20px; height:180px; object-fit:cover;'
                        )

                ui.label('AI推荐方案').classes('animate-in animate-in-delay-1').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                )
                ui.element('div').classes('section-divider')
                ui.label('基于环境心理学研究结论，以下方案经过科学验证，对心理恢复具有积极效果。').style(
                    f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                schemes = [
                    {
                        'id': 'nature', 'icon': '🌿', 'title': '自然和谐方案',
                        'desc': '中等绿化 + 低人造元素，模拟自然公园环境，最大化注意力恢复效果',
                        'green': 55, 'urban': 25, 'vitality': 40, 'light': 55,
                        'evidence': '注意力恢复理论(ART): 自然环境通过"柔性注意力"促进认知恢复',
                        'gradient': f'linear-gradient(135deg, {COLORS["primary_dark"]}, {COLORS["primary"]})',
                    },
                    {
                        'id': 'urban', 'icon': '🏙️', 'title': '活力都市方案',
                        'desc': '中等绿化 + 中等人造元素 + 适度活力，适合城市街区改造',
                        'green': 45, 'urban': 50, 'vitality': 55, 'light': 50,
                        'evidence': '倒U型效应: 中等复杂度的城市环境恢复性可能优于极简或极繁环境',
                        'gradient': f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]})',
                    },
                    {
                        'id': 'zen', 'icon': '🧘', 'title': '宁静禅意方案',
                        'desc': '高绿化 + 低人造元素 + 低活力，创造沉浸式宁静空间',
                        'green': 70, 'urban': 15, 'vitality': 20, 'light': 45,
                        'evidence': '压力恢复理论(SRT): 低唤醒的自然场景有助于降低生理应激水平',
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
                        # 顶部渐变色带
                        ui.element('div').style(
                            f'width:100%; height:4px; background:{scheme["gradient"]};'
                        )
                        with ui.column().style('padding:16px 18px; gap:8px'):
                            with ui.row().style('align-items:center; gap:8px'):
                                scheme_svg = get_svg(scheme['icon'], 20)
                                if scheme_svg:
                                    ui.html(scheme_svg).style('width:20px; height:20px; flex-shrink:0;')
                                ui.label(scheme['title']).style(
                                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}'
                                )
                            ui.label(scheme['desc']).style(
                                f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.6; font-weight:300'
                            )
                            # 参数药丸
                            with ui.row().style('gap:6px; flex-wrap:wrap'):
                                params = [
                                    (f'绿化 {scheme["green"]}%', COLORS['primary']),
                                    (f'人造 {scheme["urban"]}%', COLORS['accent']),
                                    (f'活力 {scheme["vitality"]}%', COLORS['secondary']),
                                ]
                                for plabel, pcolor in params:
                                    ui.label(plabel).classes('tag-pill').style(
                                        f'background:{pcolor}12; color:{pcolor}; font-weight:500;'
                                    )
                            # 理论依据
                            with ui.element('div').style(
                                f'width:100%; padding:8px 12px; border-radius:12px;'
                                f'background:{COLORS["primary"]}06; margin-top:4px;'
                            ):
                                ui.html(f'{get_svg("📚", 12)}<span style="margin-left:4px; font-size:11px; color:{COLORS["text_secondary"]}; line-height:1.5; font-weight:300">{scheme["evidence"]}</span>').style(
                                    'display:flex; align-items:flex-start;'
                                )

                def select_scheme(scheme):
                    state['selected'] = scheme['id']
                    for sid_key, c in scheme_cards.items():
                        if sid_key == scheme['id']:
                            c.style(
                                f'width:100%; padding:0; cursor:pointer; overflow:hidden;'
                                f'border:2px solid {COLORS["primary"]} !important;'
                                f'box-shadow:0 0 0 4px {COLORS["primary"]}15, 0 8px 32px rgba(27,67,50,0.12) !important;'
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

                # 错误提示
                error_label = ui.label().style(
                    f'display:none; padding:12px 16px; background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30; border-radius:14px;'
                    f'font-size:13px; color:{COLORS["error"]}; width:100%'
                )
                loading_card = ui.element('div').style('display:none;').classes('glass-card')
                with loading_card:
                    with ui.column().style('width:100%; padding:24px; text-align:center; align-items:center'):
                        ui.spinner('dots', size='lg', color=COLORS['primary'])
                        ui.label('AI 正在生成推荐场景...').style(
                            f'font-size:15px; color:{COLORS["text"]}; margin-top:12px; font-weight:500'
                        )

                gen_btn = ui.button('✨ 一键生成推荐场景', on_click=lambda: generate()).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:8px;')
                gen_btn.set_visibility(False)

                async def generate():
                    if not session or not session.uploaded_image_path:
                        ui.notify('请先上传图片', type='warning')
                        return

                    gen_btn.set_visibility(False)
                    loading_card.style('display:block; width:100%; border-radius:20px;')
                    error_label.style('display:none')

                    try:
                        from app.services.sd_service import generate_from_sliders
                        result_bytes = await asyncio.to_thread(
                            generate_from_sliders,
                            session.uploaded_image_path,
                            session.green_level, session.urban_level,
                            session.vitality_level, session.light_warmth,
                        )
                        save_output(sid, result_bytes)
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

                # 理论说明
                with ui.card().classes('glass-card').style(
                    'width:100%; padding:14px 18px; border:none !important;'
                    f'border-left:3px solid {COLORS["primary"]} !important; margin-top:8px;'
                ):
                    with ui.row().style('align-items:center; gap:6px; margin-bottom:4px'):
                        ui.html(get_svg('🔬', 14)).style('width:14px; height:14px; flex-shrink:0;')
                        ui.label('方案依据').style(
                            f'font-size:12px; font-weight:600; color:{COLORS["primary_dark"]};'
                        )
                    ui.label(
                        '推荐参数将基于2×3×3实验（场景类型×绿化程度×人造元素丰富度）的结论动态更新。'
                        '当前为初始预设值，实验完成后将替换为实际最优参数组合。'
                    ).style(f'font-size:12px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300')
