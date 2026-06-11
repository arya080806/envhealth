"""Account page."""
import time

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.db import get_user_sessions
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


ACCOUNT_CSS = '''
<style>
.account-wrap {
    width: 100%;
    padding: 18px 20px 104px;
    gap: 14px;
}
.account-hero {
    width: 100%;
    border-radius: 28px;
    padding: 22px 18px;
    background:
        linear-gradient(145deg, rgba(47,123,88,.16), rgba(255,255,248,.78) 58%, rgba(231,240,226,.82)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    border: 1px solid rgba(38,70,52,.12);
    box-shadow: 0 18px 36px rgba(38,70,52,.10);
}
.account-avatar-lg {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    margin: 0 auto 12px;
    background: #2F7B58;
    color: #FFFDF4;
    font-size: 30px;
    font-weight: 900;
    box-shadow: 0 18px 34px rgba(47,123,88,.22);
}
.account-name {
    text-align: center;
    color: #173126;
    font-size: 22px;
    line-height: 1.2;
    font-weight: 900;
}
.account-phone {
    margin-top: 6px;
    text-align: center;
    color: rgba(23,49,38,.58);
    font-size: 13px;
}
.account-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 18px;
}
.account-stat {
    border-radius: 18px;
    padding: 11px 8px;
    text-align: center;
    background: rgba(255,255,248,.62);
    border: 1px solid rgba(38,70,52,.10);
}
.account-stat strong {
    display: block;
    color: #173126;
    font-size: 18px;
    line-height: 1.1;
}
.account-stat span {
    display: block;
    margin-top: 5px;
    color: rgba(23,49,38,.52);
    font-size: 10px;
    font-weight: 700;
}
.account-panel {
    width: 100%;
    border-radius: 24px;
    padding: 18px;
    background: linear-gradient(180deg, rgba(255,255,248,.86), rgba(246,250,241,.74));
    border: 1px solid rgba(38,70,52,.12);
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
}
.account-panel-title {
    color: #173126;
    font-size: 15px;
    font-weight: 900;
    margin-bottom: 12px;
}
.account-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-height: 34px;
    border-top: 1px solid rgba(38,70,52,.10);
    padding-top: 11px;
    margin-top: 11px;
}
.account-row:first-of-type {
    border-top: 0;
    padding-top: 0;
    margin-top: 0;
}
.account-row-label {
    color: rgba(23,49,38,.56);
    font-size: 12px;
}
.account-row-value {
    color: #173126;
    font-size: 13px;
    font-weight: 800;
    text-align: right;
    word-break: break-all;
}
.account-action {
    width: 100%;
    min-height: 48px;
    border-radius: 999px;
    border: 1px solid rgba(47,123,88,.18);
    background: rgba(47,123,88,.08);
    color: #2F7B58;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 850;
    cursor: pointer;
}
.account-action.danger {
    background: rgba(202,86,72,.08);
    border-color: rgba(202,86,72,.18);
    color: #A8463E;
}
</style>
'''


def _initial(display_name: str) -> str:
    return (display_name or '鐢ㄦ埛')[:1].upper()


def _masked_phone(phone: str) -> str:
    return f'{phone[:3]}****{phone[-4:]}' if len(phone or '') == 11 else (phone or '鏈粦瀹氭墜鏈哄彿')


def create_account_page():
    @ui.page('/account')
    def account_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(ACCOUNT_CSS)

        user = app.storage.user.get('user')
        if not user:
            smooth_navigate('/login')
            return

        sessions = get_user_sessions(user['id'])
        finished = [s for s in sessions if s.get('generated_image_path')]
        evaluated = [s for s in sessions if s.get('survey_completed_at')]
        drafts = [s for s in sessions if not s.get('generated_image_path')]

        display_name = user.get('display_name') or user.get('username') or '鐢ㄦ埛'
        phone = user.get('phone', '')
        reg_time = time.strftime('%Y-%m-%d', time.localtime(user.get('created_at', 0))) if user.get('created_at') else '鏈煡'

        def logout():
            app.storage.user.clear()
            smooth_navigate('/login')

        with ui.column().classes('mobile-page light-page').style('min-height:100vh'):
            bottom_nav(light=True)

            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/about')).props('flat round dense').style(
                    'color:#2F7B58;'
                )
                ui.label('鎴戠殑璐﹀彿').style('font-size:18px; font-weight:900; margin-left:4px; color:#173126;')

            with ui.column().classes('account-wrap'):
                with ui.element('section').classes('account-hero animate-in'):
                    ui.html(f'''
                        <div class="account-avatar-lg">{_initial(display_name)}</div>
                        <div class="account-name">{display_name}</div>
                        <div class="account-phone">{_masked_phone(phone)}</div>
                        <div class="account-stats">
                            <div class="account-stat"><strong>{len(finished)}</strong><span>宸茬敓鎴?/span></div>
                            <div class="account-stat"><strong>{len(evaluated)}</strong><span>宸茶瘎浼?/span></div>
                            <div class="account-stat"><strong>{len(drafts)}</strong><span>鑽夌</span></div>
                        </div>
                    ''')

                with ui.element('section').classes('account-panel animate-in animate-in-delay-1'):
                    ui.html(f'''
                        <div class="account-panel-title">璐﹀彿淇℃伅</div>
                        <div class="account-row">
                            <div class="account-row-label">鐮旂┒缂栧彿</div>
                            <div class="account-row-value">{user.get('participant_id', '-')}</div>
                        </div>
                        <div class="account-row">
                            <div class="account-row-label">娉ㄥ唽鏃堕棿</div>
                            <div class="account-row-value">{reg_time}</div>
                        </div>
                        <div class="account-row">
                            <div class="account-row-label">褰撳墠韬唤</div>
                            <div class="account-row-value">浣撻獙鍙備笌鑰?/div>
                        </div>
                    ''')

                with ui.element('section').classes('account-panel animate-in animate-in-delay-2'):
                    ui.html('<div class="account-panel-title">蹇嵎鎿嶄綔</div>')
                    with ui.column().style('gap:10px;width:100%;'):
                        with ui.element('button').classes('account-action').on('click', lambda: smooth_navigate('/records')):
                            ui.icon('description').style('font-size:18px;')
                            ui.label('鏌ョ湅鎴戠殑鏀归€犺褰?)
                        with ui.element('button').classes('account-action').on('click', lambda: smooth_navigate('/camera')):
                            ui.icon('add_photo_alternate').style('font-size:18px;')
                            ui.label('寮€濮嬫柊鐨勭幆澧冧綋楠?)
                        with ui.element('button').classes('account-action').on('click', lambda: smooth_navigate('/export')):
                            ui.icon('analytics').style('font-size:18px;')
                            ui.label('鐮旂┒鑰呮暟鎹潰鏉?)
                        with ui.element('button').classes('account-action danger').on('click', logout):
                            ui.icon('logout').style('font-size:18px;')
                            ui.label('閫€鍑虹櫥褰?)
