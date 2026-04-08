"""首页 / 引导页 - 自然沉浸式设计"""
from nicegui import ui, app
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, NATURE_BG_CSS, GLASS_CARD_STYLE, BOTTOM_NAV_STYLE, PRIMARY_BTN_STYLE
from app.components.nav import bottom_nav
from app.components.icons import get_svg


def create_home_page():
    @ui.page('/')
    def home_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        # 检查登录
        user = app.storage.user.get('user', None)
        if not user:
            ui.navigate.to('/login')
            return

        with ui.column().classes('mobile-page').style('min-height:100vh; background:#F8FAF5'):

            # ===== Hero 区域 =====
            with ui.column().classes('nature-hero').style(
                'padding:56px 28px 48px 28px; text-align:center; position:relative; z-index:1;'
                'border-radius:0 0 36px 36px;'
            ):
                # 浮动装饰
                ui.html(get_svg('🌿hero', 72)).classes('float-animation').style(
                    'width:72px; height:72px; margin-bottom:16px;'
                    'filter:drop-shadow(0 8px 16px rgba(0,0,0,0.15));'
                )
                ui.label('环境疗愈工坊').classes('animate-in').style(
                    'font-size:30px; font-weight:700; color:white;'
                    'letter-spacing:3px; margin-bottom:8px;'
                    'text-shadow:0 2px 12px rgba(0,0,0,0.2);'
                )
                # 装饰分隔线
                ui.element('div').style(
                    'width:48px; height:2px; background:rgba(255,255,255,0.5);'
                    'border-radius:1px; margin:8px auto 16px auto;'
                )
                ui.label('拍摄你身边的环境\n用科学的方式重新设计它\n发现属于你的疗愈空间').classes('animate-in animate-in-delay-1').style(
                    'font-size:14px; color:rgba(255,255,255,0.88);'
                    'line-height:2; white-space:pre-line; max-width:300px; margin:0 auto;'
                    'letter-spacing:0.5px; font-weight:300;'
                )

            # ===== 主内容区域 =====
            with ui.column().style('flex:1; padding:28px 20px; gap:24px; margin-top:-20px; position:relative; z-index:2'):

                # 功能卡片组
                with ui.row().style('gap:12px; justify-content:center; width:100%'):
                    features = [
                        ('📷', '拍照', f'linear-gradient(135deg, {COLORS["primary_dark"]}, {COLORS["primary"]})'),
                        ('🎨', '改造', f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]})'),
                        ('💚', '疗愈', f'linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["primary_ultra_light"]})'),
                    ]
                    for idx, (icon, label, bg) in enumerate(features):
                        with ui.card().classes(f'glass-card hover-lift card-press animate-in animate-in-delay-{idx+1}').style(
                            'padding:20px 16px; width:100px; align-items:center; text-align:center;'
                            'cursor:pointer; border:none;'
                        ):
                            with ui.element('div').style(
                                f'width:52px; height:52px; border-radius:16px; display:flex;'
                                f'align-items:center; justify-content:center; background:{bg};'
                                'margin-bottom:10px; box-shadow:0 4px 12px rgba(27,67,50,0.2);'
                            ):
                                svg = get_svg(icon, 30)
                                if svg:
                                    ui.html(svg).style('width:30px; height:30px;')
                                else:
                                    ui.label(icon).style('font-size:28px;')
                            ui.label(label).style(
                                f'font-size:13px; color:{COLORS["text"]}; font-weight:600; letter-spacing:0.5px'
                            )

                # 开始按钮
                ui.button('开始体验 →', on_click=lambda: ui.navigate.to('/camera')).classes(
                    'animate-in animate-in-delay-3 pulse-glow'
                ).style(PRIMARY_BTN_STYLE).props('flat no-caps')

                # 理论说明卡片
                with ui.card().classes('glass-card animate-in animate-in-delay-4').style(
                    'width:100%; padding:16px 20px; border:none;'
                ):
                    with ui.row().style('align-items:center; gap:10px'):
                        with ui.element('div').style(
                            f'width:36px; height:36px; border-radius:10px;'
                            f'background:linear-gradient(135deg, {COLORS["primary"]}20, {COLORS["primary_light"]}30);'
                            'display:flex; align-items:center; justify-content:center; flex-shrink:0;'
                        ):
                            ui.html(get_svg('💡', 18)).style('width:18px; height:18px;')
                        ui.label('基于环境心理学与感知控制理论').style(
                            f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.6;'
                            'font-weight:400;'
                        )

            # ===== 底部导航 =====
            bottom_nav('首页')
