"""记录页面 - 高级 UI"""
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, BOTTOM_NAV_STYLE, PRIMARY_BTN_STYLE
from app.components.nav import bottom_nav
from app.components.icons import get_svg


def create_records_page():
    @ui.page('/records')
    def records_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        with ui.column().classes('mobile-page').style('min-height:100vh'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.label('我的记录').style(
                    f'font-size:17px; font-weight:600; margin-left:8px; color:{COLORS["text"]}'
                )

            # 空状态
            with ui.column().classes('animate-in').style(
                'flex:1; padding:20px; align-items:center; justify-content:center; text-align:center;'
            ):
                # 装饰圆形背景
                with ui.element('div').style(
                    f'width:120px; height:120px; border-radius:50%;'
                    f'background:linear-gradient(135deg, {COLORS["primary"]}10, {COLORS["primary_light"]}15);'
                    'display:flex; align-items:center; justify-content:center; margin-bottom:20px;'
                ):
                    ui.html(get_svg('📋', 48)).classes('float-animation').style('width:48px; height:48px;')

                ui.label('暂无记录').style(
                    f'font-size:18px; color:{COLORS["text"]}; font-weight:600; letter-spacing:0.5px'
                )
                ui.label('完成一次环境改造体验后\n你的记录将显示在这里').style(
                    f'font-size:14px; color:{COLORS["text_secondary"]}; line-height:1.7;'
                    'white-space:pre-line; margin-top:8px; font-weight:300;'
                )
                ui.button('去体验 →', on_click=lambda: ui.navigate.to('/camera')).props(
                    'no-caps unelevated'
                ).style(
                    f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                    'color:white; border-radius:28px; padding:14px 36px; margin-top:24px;'
                    f'box-shadow:0 6px 20px rgba(45,106,79,0.25); font-weight:600;'
                )

            # 底部导航
            bottom_nav('记录')
