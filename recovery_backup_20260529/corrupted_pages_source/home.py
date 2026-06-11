"""Home page."""
from nicegui import app, ui

from app.components.nav import smooth_navigate

from app.theme import COMMON_STYLE, META_VIEWPORT


HOME_PAGE_STYLE = '''
<style>
.home-page {
    position: relative;
    width: min(100%, 430px);
    min-height: 100dvh;
    margin: 0 auto;
    overflow: hidden;
    background: #07120D;
    color: #F4F0E6;
}

.home-page::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg, rgba(7,18,13,0.10) 0%, rgba(7,18,13,0.28) 38%, rgba(7,18,13,0.92) 100%),
        url('/static/images/forest-hero-dark.webp') center/cover no-repeat;
    transform: scale(1.02);
}

.home-page::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(90deg, rgba(244,240,230,0.05) 0 1px, transparent 1px 100%),
        linear-gradient(180deg, rgba(244,240,230,0.04), transparent 24%);
    background-size: 34px 100%, 100% 100%;
    mix-blend-mode: screen;
    opacity: 0.55;
}

.home-shell {
    position: relative;
    z-index: 1;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    padding: 24px 24px 34px;
}

.home-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.home-mark {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: rgba(244,240,230,0.78);
    font-size: 12px;
    letter-spacing: 0.08em;
}

.home-mark::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #B7F27E;
    box-shadow: 0 0 18px rgba(183,242,126,0.60);
}

.home-user-badge {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: rgba(16,29,22,0.58);
    border: 1px solid rgba(244,240,230,0.18);
    color: #F4F0E6;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    backdrop-filter: blur(18px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.25);
    font-size: 13px;
    font-weight: 700;
}

.home-copy {
    margin-top: 72px;
}

.home-title {
    font-size: 38px;
    line-height: 1.12;
    font-weight: 700;
    letter-spacing: 0;
    margin: 0;
    max-width: 9em;
    text-wrap: balance;
}

.home-subtitle {
    margin-top: 14px;
    color: rgba(244,240,230,0.68);
    font-size: 14px;
    line-height: 1.8;
    font-weight: 300;
}

.home-spacer { flex: 1; }

.home-panel {
    border: 1px solid rgba(244,240,230,0.12);
    border-radius: 8px;
    background: rgba(7,18,13,0.62);
    backdrop-filter: blur(22px);
    box-shadow: 0 24px 54px rgba(0,0,0,0.30);
    padding: 16px;
}

.home-panel-title {
    color: #B7F27E;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

.home-panel-text {
    margin-top: 8px;
    color: rgba(244,240,230,0.78);
    font-size: 13px;
    line-height: 1.7;
}

.home-start {
    margin-top: 16px;
    width: 100%;
    height: 54px;
    border: 0;
    border-radius: 999px;
    background: #B7F27E;
    color: #07120D;
    font-size: 15px;
    font-weight: 800;
    cursor: pointer;
    box-shadow: 0 16px 36px rgba(183,242,126,0.24);
}

@media (max-height: 700px) {
    .home-copy { margin-top: 44px; }
    .home-title { font-size: 34px; }
}
</style>
'''


def create_home_page():
    @ui.page('/')
    def home_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(HOME_PAGE_STYLE)

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        display_name = user.get('display_name') or user.get('username') or '鐢ㄦ埛'
        display_char = display_name[:1].upper()

        with ui.element('div').classes('home-page'):
            with ui.element('div').classes('home-shell'):
                with ui.element('div').classes('home-top'):
                    ui.html('<div class="home-mark">ENVIRONMENT HEALING</div>')
                    with ui.element('button').classes('home-user-badge').on('click', lambda: smooth_navigate('/account')):
                        ui.html(display_char)

                with ui.element('div').classes('home-copy'):
                    ui.html('''
                        <h1 class="home-title">鐜鐤楁剤宸ュ潑</h1>
                        <div class="home-subtitle">涓婁紶涓€澶勭湡瀹炵幆澧冿紝鐢熸垚鏇村畨闈欍€佹洿鏈夋仮澶嶆劅鐨勭┖闂存柟妗堛€?/div>
                    ''')

                ui.element('div').classes('home-spacer')

                with ui.element('div').classes('home-panel animate-in'):
                    ui.html('''
                        <div class="home-panel-title">Start a session</div>
                        <div class="home-panel-text">浠庝竴寮犵収鐗囧紑濮嬶紝閫夋嫨浣犳兂璋冩暣鐨勬柟鍚戯紝淇濈暀鐜板満鐨勭湡瀹炴劅銆?/div>
                    ''')
                    with ui.element('button').classes('home-start').on('click', lambda: smooth_navigate('/camera')):
                        ui.html('寮€濮嬩綋楠?)
