"""Shared navigation components."""

from nicegui import app, ui

from app.components.guide import guide_entry
from app.theme import BOTTOM_NAV_STYLE, COLORS, LIGHT_BOTTOM_NAV_STYLE


NAV_NOTIFY_CSS = '''
<style>
.draft-nav-item {
    position: relative;
}
.draft-ready-dot {
    position: absolute;
    top: 7px;
    right: 20px;
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: #1DB954;
    border: 2px solid rgba(247,249,241,0.96);
    box-shadow: 0 0 0 3px rgba(29,185,84,0.18), 0 4px 10px rgba(16,37,26,0.22);
    display: none;
}
.draft-nav-item.has-draft-ready .draft-ready-dot {
    display: block;
}
</style>
'''


NAV_NOTIFY_JS = '''
<script>
(function () {
    function setReadyDot(hasReady) {
        document.querySelectorAll('.draft-nav-item').forEach(function (item) {
            item.classList.toggle('has-draft-ready', !!hasReady);
        });
    }

    async function pollDraftNotifications() {
        try {
            var resp = await fetch('/api/generation/notifications', { cache: 'no-store' });
            if (!resp.ok) return;
            var data = await resp.json();
            setReadyDot((data.ready || []).length > 0);
        } catch (e) {}
    }

    if (!window.HealingDraftNotifier) {
        window.HealingDraftNotifier = { poll: pollDraftNotifications };
        pollDraftNotifications();
        setInterval(pollDraftNotifications, 4000);
        document.addEventListener('visibilitychange', pollDraftNotifications);
        window.addEventListener('focus', pollDraftNotifications);
    } else {
        window.HealingDraftNotifier.poll();
    }
})();
</script>
'''


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
    ui.add_head_html(NAV_NOTIFY_CSS)
    guide_entry(light=light)
    ui.element('div').classes('healing-bottom-spacer').style(
        'width:100%; min-height:92px; flex-shrink:0; order:9999; pointer-events:none;'
    )

    items = [
        ('home', '首页', '/camera'),
        ('description', '草稿箱', '/records'),
        ('person', '用户', '/account'),
    ]
    nav_classes = 'healing-bottom-nav healing-bottom-nav-light' if light else 'healing-bottom-nav'
    with ui.row().classes(nav_classes).style(LIGHT_BOTTOM_NAV_STYLE if light else BOTTOM_NAV_STYLE):
        for icon, label, path in items:
            is_active = label == active
            color = ('#2F7B58' if is_active else 'rgba(23,49,38,0.56)') if light else (
                COLORS['primary'] if is_active else COLORS['text_secondary']
            )
            bg = ('rgba(47,123,88,0.12)' if is_active else 'transparent') if light else (
                'rgba(183,242,126,0.12)' if is_active else 'transparent'
            )
            item_classes = 'draft-nav-item' if label == '草稿箱' else ''
            with ui.column().classes(item_classes).style(
                f'align-items:center; justify-content:center; gap:3px; cursor:pointer; min-width:68px;'
                f'padding:7px 8px; border-radius:999px; background:{bg}; transition:all 0.22s ease;'
            ).on('click', lambda p=path: smooth_navigate(p)):
                if label == '草稿箱':
                    ui.html('<span class="draft-ready-dot" aria-hidden="true"></span>', sanitize=False)
                ui.icon(icon).style(f'font-size:21px; color:{color};')
                ui.label(label).style(
                    f'font-size:11px; font-weight:{"700" if is_active else "500"}; color:{color}; line-height:1;'
                )
    ui.add_body_html(NAV_NOTIFY_JS)
