"""共享导航组件"""
from nicegui import ui
from app.theme import COLORS, BOTTOM_NAV_STYLE


def bottom_nav(active: str = '首页'):
    """底部导航组件"""
    with ui.row().style(BOTTOM_NAV_STYLE):
        for icon, label, path in [
            ('home', '首页', '/'),
            ('description', '记录', '/records'),
            ('info', '关于', '/about'),
        ]:
            is_active = label == active
            color = COLORS['primary'] if is_active else COLORS['text_secondary']
            with ui.column().style(
                'align-items:center; gap:3px; cursor:pointer; transition:all 0.3s;'
            ).on('click', lambda p=path: ui.navigate.to(p)):
                ui.icon(icon).style(
                    f'font-size:22px; color:{color};'
                    f'{"font-weight:600" if is_active else ""}'
                )
                ui.label(label).style(
                    f'font-size:11px; font-weight:{"600" if is_active else "400"}; color:{color}'
                )
                if is_active:
                    ui.element('div').style(
                        f'width:20px; height:3px; border-radius:2px;'
                        f'background:linear-gradient(90deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                        'margin-top:2px;'
                    )
