"""Mode selection page."""
from pathlib import Path

from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session
from app.theme import COLORS, COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


MODE_SELECT_CSS = '''
<style>
.mode-intro {
    padding: 18px;
    border: 1px solid rgba(38,70,52,0.12);
    border-radius: 22px;
    background: rgba(255,255,248,0.72);
    backdrop-filter: blur(18px);
}
.mode-kicker {
    color: #2F7B58;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.mode-copy {
    margin-top: 8px;
    color: rgba(23,49,38,.70);
    font-size: 13px;
    line-height: 1.75;
}
.mode-preview {
    position: relative;
    width: 100%;
    height: 168px;
    overflow: hidden;
    border-radius: 24px;
    border: 1px solid rgba(244,240,230,0.12);
    box-shadow: 0 18px 44px rgba(0,0,0,.24);
}
.mode-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.mode-preview::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 30%, rgba(7,18,13,.78));
}
.mode-preview-title {
    position: absolute;
    left: 16px;
    right: 16px;
    bottom: 14px;
    z-index: 1;
    color: #F4F0E6;
    font-size: 15px;
    font-weight: 700;
}
.mode-group-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 2px;
    color: rgba(23,49,38,.86);
    font-size: 13px;
    font-weight: 700;
}
.mode-group-title::before {
    content: "";
    width: 28px;
    height: 1px;
    background: rgba(47,123,88,.62);
}
.mode-card {
    width: 100%;
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) 24px;
    gap: 14px;
    align-items: center;
    padding: 18px 16px;
    cursor: pointer;
    border-radius: 22px;
    border: 1px solid rgba(38,70,52,0.12);
    background: rgba(255,255,248,0.74);
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
    backdrop-filter: blur(18px);
    transition: transform .2s ease, border-color .2s ease, background .2s ease;
}
.mode-card:active {
    transform: scale(.985);
}
.mode-card:hover {
    border-color: rgba(47,123,88,.24);
    background: rgba(255,255,248,.92);
}
.mode-index {
    width: 42px;
    height: 42px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #F8FAF2;
    background: #2F7B58;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: .04em;
}
.mode-index.secondary {
    color: #2F7B58;
    background: rgba(47,123,88,.10);
    border: 1px solid rgba(47,123,88,.16);
}
.mode-title {
    color: #173126;
    font-size: 17px;
    line-height: 1.25;
    font-weight: 800;
}
.mode-desc {
    margin-top: 6px;
    color: rgba(23,49,38,.62);
    font-size: 12px;
    line-height: 1.6;
}
.mode-arrow {
    color: #2F7B58;
    opacity: .86;
}
.theory-note {
    border-radius: 22px;
    border: 1px solid rgba(47,123,88,.14);
    background: rgba(255,255,248,.64);
    padding: 15px 16px;
    color: rgba(23,49,38,.70);
    font-size: 12px;
    line-height: 1.7;
}
</style>
'''


def create_mode_select_page():
    @ui.page('/mode-select')
    def mode_select_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(MODE_SELECT_CSS)

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/camera')).props(
                    'flat round dense'
                ).style('color:#2F7B58')
                ui.label('閫夋嫨鏀归€犳ā寮?).style(
                    'font-size:18px; font-weight:800; margin-left:4px; color:#173126'
                )

            with ui.column().style('padding:18px 20px 104px; gap:16px; width:100%'):
                if sid:
                    session = get_session(sid)
                    if session and session.uploaded_image_path:
                        fname = Path(session.uploaded_image_path).name
                        with ui.element('div').classes('mode-preview animate-in'):
                            ui.html(f'<img src="/api/image/{fname}" alt="uploaded environment">')
                            ui.html('<div class="mode-preview-title">鍩轰簬杩欏紶鐜鐓х墖缁х画璁捐</div>')

                with ui.element('div').classes('mode-intro animate-in animate-in-delay-1'):
                    ui.html('''
                        <div class="mode-kicker">Choose a workflow</div>
                        <div class="mode-copy">涓嶅悓妯″紡瀵瑰簲涓嶅悓鐨勫弬涓庢繁搴︺€備綘鍙互鐩存帴鎽嗘斁鍏冪礌锛屼篃鍙互鐢ㄦ儏缁€佸弬鏁版垨鎺ㄨ崘鏂规鏉ュ紩瀵肩敓鎴愩€?/div>
                    ''')

                ui.html('<div class="mode-group-title animate-in animate-in-delay-2">涓诲姩鍒涗綔</div>')
                creative_modes = [
                    ('01', '鑷敱鍒涗綔', '鐩存帴鍦ㄧ収鐗囦笂鎽嗘斁鏍戞湪銆佸骇妞呫€佹按鏅瓑鍏冪礌锛岄€傚悎鏄庣‘鐭ラ亾鎯冲姞浠€涔堛€?, f'/drag-mode?sid={sid}'),
                    ('02', '鐏垫劅鍒涙兂', '闅忔墜鐢诲嚑绗旓紝绯荤粺璇嗗埆浣犵殑鑽夊浘鎰忓浘锛屽啀鐢熸垚绌洪棿鏂规銆?, f'/inspire-mode?sid={sid}'),
                    ('03', '瀵硅瘽鏀归€?, '璇村嚭鎯宠鐨勬劅鍙楋紝璁╃郴缁熸妸鎯呯华杞瘧涓虹┖闂淬€?, f'/chat-mode?sid={sid}'),
                ]
                for idx, (num, title, desc, href) in enumerate(creative_modes):
                    _mode_card(num, title, desc, href, idx)

                ui.html('<div class="mode-group-title animate-in animate-in-delay-3">杈呭姪鐢熸垚</div>')
                assisted_modes = [
                    ('04', '鍙傛暟璋冭妭', '鐢ㄦ粦鏉嗘帶鍒剁豢鍖栥€佷汉閫犲厓绱犮€佹椿鍔涘拰鍏夌嚎姘涘洿銆?, f'/slider-mode?sid={sid}'),
                    ('05', '鏅鸿兘鎺ㄨ崘', '鍩轰簬鐜蹇冪悊瀛︾粰鍑轰竴缁勬洿绋冲Ε鐨勭枟鎰堝弬鏁般€?, f'/ai-mode?sid={sid}'),
                ]
                for idx, (num, title, desc, href) in enumerate(assisted_modes):
                    _mode_card(num, title, desc, href, idx + 3, secondary=True)

                ui.html('''
                    <div class="theory-note animate-in animate-in-delay-4">
                        涓诲姩鍙備笌浼氬寮哄鐜鐨勬帶鍒舵劅锛涘鏋滀綘鍙兂蹇€熷緱鍒扮粨鏋滐紝杈呭姪鐢熸垚涔熻兘瀹屾垚瀹屾暣鏀归€犮€?                    </div>
                ''')


def _mode_card(num: str, title: str, desc: str, href: str, idx: int, secondary: bool = False):
    delay = min(idx + 1, 4)
    cls = 'mode-index secondary' if secondary else 'mode-index'
    with ui.element('div').classes(f'mode-card animate-in animate-in-delay-{delay}').on(
        'click', lambda h=href: smooth_navigate(h)
    ):
        ui.html(f'<div class="{cls}">{num}</div>')
        ui.html(f'<div><div class="mode-title">{title}</div><div class="mode-desc">{desc}</div></div>')
        ui.icon('chevron_right').classes('mode-arrow').style('font-size:22px;')
