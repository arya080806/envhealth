"""登录页面 - 被试编号录入"""
from nicegui import ui, app
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, PRIMARY_BTN_STYLE
from app.components.icons import get_svg
from app.db import create_or_get_user


def create_login_page():
    @ui.page('/login')
    def login_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        # 已登录则跳转首页
        if app.storage.user.get('user'):
            ui.navigate.to('/')
            return

        with ui.column().classes('mobile-page').style('min-height:100vh; justify-content:center'):
            with ui.column().style(
                'padding:32px 24px; gap:24px; width:100%; align-items:center;'
            ):
                # Logo
                ui.html(get_svg('🌿hero', 64)).classes('float-animation').style(
                    'width:64px; height:64px;'
                    'filter:drop-shadow(0 6px 12px rgba(0,0,0,0.12));'
                )
                ui.label('环境疗愈工坊').style(
                    f'font-size:24px; font-weight:700; color:{COLORS["primary_dark"]};'
                    'letter-spacing:2px;'
                )
                ui.label('请输入您的被试信息以开始体验').style(
                    f'font-size:13px; color:{COLORS["text_secondary"]}; font-weight:300;'
                )

                # 登录卡片
                with ui.card().classes('glass-card animate-in').style(
                    'width:100%; padding:28px 24px; border:none !important;'
                ):
                    with ui.column().style('width:100%; gap:20px'):
                        pid_input = ui.input(
                            label='被试编号',
                            placeholder='例如: P001',
                        ).props('outlined dense').style('width:100%')

                        name_input = ui.input(
                            label='昵称（选填）',
                            placeholder='您的称呼',
                        ).props('outlined dense').style('width:100%')

                        error_label = ui.label().style(
                            f'display:none; font-size:12px; color:{COLORS["error"]};'
                        )

                        def do_login():
                            pid = pid_input.value.strip()
                            if not pid:
                                error_label.set_text('请输入被试编号')
                                error_label.style(
                                    f'display:block; font-size:12px; color:{COLORS["error"]};'
                                )
                                return
                            name = name_input.value.strip() or pid
                            user = create_or_get_user(pid, name)
                            app.storage.user['user'] = user
                            ui.navigate.to('/')

                        ui.button('进入系统', on_click=do_login).props(
                            'no-caps unelevated'
                        ).style(PRIMARY_BTN_STYLE)

                # 研究者入口
                with ui.element('div').classes('animate-in animate-in-delay-2').style(
                    'margin-top:16px; text-align:center;'
                ):
                    ui.link('研究者数据面板 →', '/export').style(
                        f'font-size:12px; color:{COLORS["text_secondary"]}; text-decoration:none;'
                        f'opacity:0.6;'
                    )
