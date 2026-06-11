"""Shared navigation components."""

from nicegui import app, ui

from app.theme import BOTTOM_NAV_STYLE, COLORS, LIGHT_BOTTOM_NAV_STYLE


def smooth_navigate(path: str, delay: float = 0.08) -> None:
    """Show a tiny route transition before NiceGUI rebuilds the next page."""
    ui.navigate.to(path)


def _initial(display_name: str) -> str:
    return (display_name or '用户')[:1].upper()


def user_avatar_btn():
    """Floating account button leading to the account page."""
    user = app.storage.user.get('user', {})
    display_name = user.get('display_name') or user.get('username') or '用户'

    with ui.element('div').style(
        'position:fixed; top:14px; right:calc(50% - min(50vw, 215px) + 14px); z-index:999;'
    ):
        avatar_btn = ui.element('button').style(
            'width:38px; height:38px; border-radius:50%; cursor:pointer; border:1px solid rgba(244,240,230,0.18);'
            'background:rgba(16,29,22,0.62); color:#F4F0E6;'
            'display:flex; align-items:center; justify-content:center;'
            'box-shadow:0 12px 26px rgba(0,0,0,0.24); backdrop-filter:blur(18px);'
        )
        with avatar_btn:
            ui.label(_initial(display_name)).style('font-size:14px; font-weight:700; line-height:1;')

        avatar_btn.on('click', lambda: smooth_navigate('/account'))


def bottom_nav(active: str = '首页', light: bool = False):
    """Bottom tab bar plus account entry."""
    user_avatar_btn()
    ui.element('div').style('width:100%; min-height:92px; flex-shrink:0; order:9999; pointer-events:none;')

    items = [
        ('home', '首页', '/camera'),
        ('description', '记录', '/records'),
        ('info', '关于', '/about'),
    ]
    with ui.row().style(LIGHT_BOTTOM_NAV_STYLE if light else BOTTOM_NAV_STYLE):
        for icon, label, path in items:
            is_active = label == active
            color = ('#2F7B58' if is_active else 'rgba(23,49,38,0.56)') if light else (
                COLORS['primary'] if is_active else COLORS['text_secondary']
            )
            bg = ('rgba(47,123,88,0.12)' if is_active else 'transparent') if light else (
                'rgba(183,242,126,0.12)' if is_active else 'transparent'
            )
            with ui.column().style(
                f'align-items:center; justify-content:center; gap:3px; cursor:pointer; min-width:68px;'
                f'padding:7px 8px; border-radius:999px; background:{bg}; transition:all 0.22s ease;'
            ).on('click', lambda p=path: smooth_navigate(p)):
                ui.icon(icon).style(f'font-size:21px; color:{color};')
                ui.label(label).style(
                    f'font-size:11px; font-weight:{"700" if is_active else "500"}; color:{color}; line-height:1;'
                )
