"""Login and registration page."""
from nicegui import app, ui

from app.components.nav import smooth_navigate

from app.db import login_user, register_user
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, PRIMARY_BTN_STYLE


LOGIN_STYLE = '''
<style>
.auth-page {
    width: min(100%, 430px);
    min-height: 100dvh;
    margin: 0 auto;
    position: relative;
    overflow: hidden;
    color: #F4F0E6;
    background: #07120D;
}

.auth-page::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg, rgba(7,18,13,0.24), rgba(7,18,13,0.82) 62%, rgba(7,18,13,0.98)),
        url('/static/images/forest-hero-dark.webp') center/cover no-repeat;
}

.auth-shell {
    position: relative;
    z-index: 1;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    padding: 42px 22px 22px;
}

.auth-brand {
    margin-top: 18px;
}

.auth-kicker {
    color: #B7F27E;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.14em;
}

.auth-title {
    margin: 12px 0 0;
    font-size: 34px;
    line-height: 1.18;
    font-weight: 750;
    letter-spacing: 0;
}

.auth-subtitle {
    margin-top: 12px;
    color: rgba(244,240,230,0.68);
    font-size: 13px;
    line-height: 1.75;
    max-width: 19em;
}

.auth-spacer {
    flex: 1;
    min-height: 28px;
}

.auth-card {
    background: rgba(16,29,22,0.76);
    border: 1px solid rgba(244,240,230,0.13);
    border-radius: 26px;
    box-shadow: 0 24px 60px rgba(0,0,0,0.32);
    backdrop-filter: blur(24px);
    overflow: hidden;
}

.auth-panel-pad {
    padding: 20px;
}

.auth-research-link {
    display: block;
    margin: 14px auto 0;
    text-align: center;
    color: rgba(244,240,230,0.46);
    text-decoration: none;
    font-size: 12px;
}
.auth-page .q-tabs {
    background: rgba(244,240,230,0.08) !important;
    border-color: rgba(244,240,230,0.16) !important;
}
.auth-page .q-tab {
    color: rgba(244,240,230,0.70) !important;
}
.auth-page .q-tab--active {
    background: rgba(183,242,126,0.20) !important;
    color: #D8FF9A !important;
}
.auth-page .q-field--outlined .q-field__control {
    min-height: 54px !important;
    background: rgba(244,240,230,0.10) !important;
    border: 1px solid rgba(244,240,230,0.18) !important;
    border-radius: 18px !important;
}
.auth-page .q-field--outlined.q-field--focused .q-field__control {
    background: rgba(244,240,230,0.14) !important;
    border-color: rgba(183,242,126,0.46) !important;
    box-shadow: 0 0 0 3px rgba(183,242,126,0.08) !important;
}
.auth-page .q-field__native,
.auth-page .q-field__input {
    color: #F4F0E6 !important;
    font-weight: 650 !important;
}
.auth-page .q-field__native::placeholder,
.auth-page .q-field__input::placeholder {
    color: rgba(244,240,230,0.52) !important;
    opacity: 1 !important;
}
.auth-page .q-field__label {
    color: rgba(244,240,230,0.66) !important;
}
.auth-page .q-field--focused .q-field__label,
.auth-page .q-field--float .q-field__label {
    color: #D8FF9A !important;
}
.auth-submit {
    background: #B7F27E !important;
    color: #07120D !important;
    box-shadow: 0 16px 36px rgba(183,242,126,0.26) !important;
}
.auth-submit .q-icon {
    color: #07120D !important;
}
</style>
'''


def create_login_page():
    @ui.page('/login')
    def login_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(LOGIN_STYLE)

        if app.storage.user.get('user'):
            smooth_navigate('/')
            return

        with ui.element('div').classes('auth-page'):
            with ui.element('div').classes('auth-shell'):
                with ui.element('div').classes('auth-brand animate-in'):
                    ui.html('''
                        <div class="auth-kicker">ENVIRONMENT HEALING</div>
                        <h1 class="auth-title">鐜鐤楁剤宸ュ潑</h1>
                        <div class="auth-subtitle">涓虹爺绌朵綋楠屽垱寤轰竴涓交閲忚处鍙凤紝缁х画浣犵殑绌洪棿鎭㈠鎬ф帰绱€?/div>
                    ''')

                ui.element('div').classes('auth-spacer')

                with ui.card().classes('auth-card animate-in animate-in-delay-1').style('width:100%; padding:0;'):
                    with ui.tabs().props('dense no-caps').style('margin:14px 14px 0;') as tabs:
                        tab_login = ui.tab('鐧诲綍')
                        tab_register = ui.tab('娉ㄥ唽')

                    with ui.tab_panels(tabs, value=tab_login).style(
                        'width:100%; background:transparent; color:#F4F0E6;'
                    ):
                        with ui.tab_panel(tab_login).classes('auth-panel-pad'):
                            with ui.column().style('width:100%; gap:14px;'):
                                login_phone = ui.input(label='鎵嬫満鍙?, placeholder='璇疯緭鍏ユ墜鏈哄彿').props(
                                    'outlined dense type=tel'
                                ).style('width:100%')
                                login_pwd = ui.input(label='瀵嗙爜', placeholder='璇疯緭鍏ュ瘑鐮?).props(
                                    'outlined dense type=password'
                                ).style('width:100%')
                                login_err = ui.label().style(
                                    f'display:none; font-size:12px; color:{COLORS["error"]};'
                                )

                                def do_login():
                                    phone = (login_phone.value or '').strip()
                                    pwd = login_pwd.value or ''
                                    if not phone or not pwd:
                                        login_err.set_text('璇峰～鍐欐墜鏈哄彿鍜屽瘑鐮?)
                                        login_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    user, err = login_user(phone, pwd)
                                    if err:
                                        login_err.set_text(err)
                                        login_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    app.storage.user['user'] = user
                                    smooth_navigate('/')

                                ui.button('杩涘叆宸ュ潑', icon='arrow_forward', on_click=do_login).props(
                                    'no-caps unelevated'
                                ).classes('auth-submit').style(PRIMARY_BTN_STYLE + 'margin-top:4px;')

                        with ui.tab_panel(tab_register).classes('auth-panel-pad'):
                            with ui.column().style('width:100%; gap:14px;'):
                                reg_phone = ui.input(label='鎵嬫満鍙?, placeholder='璇疯緭鍏ユ墜鏈哄彿').props(
                                    'outlined dense type=tel'
                                ).style('width:100%')
                                reg_pwd = ui.input(label='瀵嗙爜', placeholder='鑷冲皯 6 浣?).props(
                                    'outlined dense type=password'
                                ).style('width:100%')
                                reg_pwd2 = ui.input(label='纭瀵嗙爜', placeholder='鍐嶆杈撳叆瀵嗙爜').props(
                                    'outlined dense type=password'
                                ).style('width:100%')
                                reg_invite = ui.input(label='閭€璇风爜', placeholder='渚嬪锛欻E-XXXXXXXX').props(
                                    'outlined dense'
                                ).style('width:100%')
                                reg_err = ui.label().style(
                                    f'display:none; font-size:12px; color:{COLORS["error"]};'
                                )

                                def do_register():
                                    phone = (reg_phone.value or '').strip()
                                    pwd = reg_pwd.value or ''
                                    pwd2 = reg_pwd2.value or ''
                                    invite = (reg_invite.value or '').strip()

                                    if not phone or not pwd or not invite:
                                        reg_err.set_text('璇峰～鍐欐墍鏈夊繀濉」')
                                        reg_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    if len(phone) != 11 or not phone.isdigit():
                                        reg_err.set_text('璇疯緭鍏ユ纭殑 11 浣嶆墜鏈哄彿')
                                        reg_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    if len(pwd) < 6:
                                        reg_err.set_text('瀵嗙爜鑷冲皯 6 浣?)
                                        reg_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    if pwd != pwd2:
                                        reg_err.set_text('涓ゆ瀵嗙爜涓嶄竴鑷?)
                                        reg_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return

                                    user, err = register_user(phone, pwd, invite)
                                    if err:
                                        reg_err.set_text(err)
                                        reg_err.style(f'display:block; font-size:12px; color:{COLORS["error"]};')
                                        return
                                    app.storage.user['user'] = user
                                    smooth_navigate('/')

                                ui.button('鍒涘缓璐﹀彿', icon='arrow_forward', on_click=do_register).props(
                                    'no-caps unelevated'
                                ).classes('auth-submit').style(PRIMARY_BTN_STYLE + 'margin-top:4px;')

                ui.link('鐮旂┒鑰呮暟鎹潰鏉?, '/export').classes('auth-research-link')
