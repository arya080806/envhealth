"""About page."""
from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.theme import COLORS, COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


ABOUT_CSS = '''
<style>
.about-wrap {
    padding: 18px 20px 104px;
    gap: 14px;
    width: 100%;
}
.about-hero {
    position: relative;
    width: 100%;
    min-height: 0;
    overflow: hidden;
    border-radius: 28px;
    padding: 22px 20px;
    border: 1px solid rgba(38,70,52,.12);
    background:
        linear-gradient(145deg, rgba(47,123,88,.16), rgba(255,255,248,.82) 56%, rgba(232,240,227,.88)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    box-shadow: 0 18px 42px rgba(38,70,52,.10);
}
.about-hero-content {
    position: relative;
}
.about-kicker {
    color: #2F7B58;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: .14em;
}
.about-title {
    margin-top: 10px;
    color: #173126;
    font-size: 29px;
    line-height: 1.14;
    font-weight: 850;
}
.about-version {
    margin-top: 10px;
    color: rgba(23,49,38,.56);
    font-size: 12px;
}
.about-hero-note {
    margin-top: 14px;
    color: rgba(23,49,38,.68);
    font-size: 13px;
    line-height: 1.75;
}
.about-hero-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 16px;
}
.about-hero-chip {
    border-radius: 16px;
    padding: 10px 8px;
    text-align: center;
    color: #173126;
    background: rgba(255,255,248,.62);
    border: 1px solid rgba(38,70,52,.10);
    font-size: 11px;
    font-weight: 800;
}
.about-panel {
    width: 100%;
    border-radius: 26px;
    border: 1px solid rgba(38,70,52,.12);
    background:
        linear-gradient(180deg, rgba(255,255,248,.84), rgba(246,250,241,.72)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
    background-blend-mode: normal, soft-light;
    backdrop-filter: blur(18px);
    padding: 18px 18px 20px;
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
}
.about-panel.light {
    background:
        linear-gradient(180deg, rgba(244,240,230,.92), rgba(230,237,226,.86)),
        url('/static/images/bamboo-mist-texture.webp') center/cover no-repeat;
    background-blend-mode: normal, soft-light;
    color: #14231A;
    border-color: rgba(7,18,13,.08);
}
.about-label {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(47,123,88,.10);
    color: #2F7B58;
    font-size: 11px;
    font-weight: 800;
}
.about-panel.light .about-label {
    background: rgba(16,67,44,.10);
    color: #1B4332;
}
.about-body {
    margin-top: 14px;
    color: rgba(20,35,26,.72);
    font-size: 13.5px;
    line-height: 1.85;
}
.about-panel.light .about-body {
    color: rgba(20,35,26,.72);
}
.about-theory-list {
    display: grid;
    gap: 10px;
    margin-top: 14px;
}
.about-theory-item {
    padding: 12px 0 0;
    border-top: 1px solid rgba(20,35,26,.12);
}
.about-theory-title {
    color: #14231A;
    font-size: 13px;
    font-weight: 850;
}
.about-theory-text {
    margin-top: 5px;
    color: rgba(20,35,26,.66);
    font-size: 12px;
    line-height: 1.75;
}
</style>
'''


def create_about_page():
    @ui.page('/about')
    def about_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(ABOUT_CSS)

        with ui.column().classes('mobile-page light-page').style('min-height:100vh'):
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.label('鍏充簬').style(
                    'font-size:18px; font-weight:800; margin-left:8px; color:#173126'
                )

            with ui.column().classes('about-wrap'):
                with ui.element('section').classes('about-hero animate-in'):
                    ui.html('''
                        <div class="about-hero-content">
                            <div class="about-kicker">ENVIRONMENT HEALING</div>
                            <div class="about-title">鐜鐤楁剤宸ュ潑</div>
                            <div class="about-version">v0.1.0 路 research prototype</div>
                            <div class="about-hero-note">鐢ㄧ湡瀹炵幆澧冪収鐗囦綔涓鸿捣鐐癸紝鎺㈢储绌洪棿璋冩暣濡備綍褰卞搷鎭㈠鎰熴€佹帶鍒舵劅涓庢儏缁姸鎬併€?/div>
                            <div class="about-hero-grid">
                                <div class="about-hero-chip">涓婁紶鐓х墖</div>
                                <div class="about-hero-chip">鐢熸垚鏂规</div>
                                <div class="about-hero-chip">璁板綍璇勪及</div>
                            </div>
                        </div>
                    ''')

                with ui.element('section').classes('about-panel animate-in animate-in-delay-1'):
                    ui.html('''
                        <div class="about-label">椤圭洰绠€浠?/div>
                        <div class="about-body">
                            杩欐槸涓€娆惧熀浜庣幆澧冨績鐞嗗鐨勬暟瀛楀寲骞查宸ュ叿銆備綘鍙互涓婁紶鐪熷疄鐜鐓х墖锛?                            閫氳繃鎽嗘斁銆佺粯鍒躲€佸璇濇垨鍙傛暟璋冭妭鐨勬柟寮忛噸鏂扮粍缁囩┖闂达紝瑙傚療鎬庢牱鐨勭幆澧冩洿鑳藉甫鏉ユ仮澶嶆劅銆?                        </div>
                    ''')

                with ui.element('section').classes('about-panel light animate-in animate-in-delay-2'):
                    ui.html('''
                        <div class="about-label">鐞嗚鍩虹</div>
                        <div class="about-theory-list">
                            <div class="about-theory-item">
                                <div class="about-theory-title">娉ㄦ剰鍔涙仮澶嶇悊璁?ART</div>
                                <div class="about-theory-text">鑷劧鐜閫氳繃鏌旀€ф敞鎰忓姏甯姪鎭㈠瀹氬悜娉ㄦ剰鍔涖€?/div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">鍘嬪姏鎭㈠鐞嗚 SRT</div>
                                <div class="about-theory-text">鑷劧鍦烘櫙鑳藉府鍔╅檷浣庣敓鐞嗗簲婵€姘村钩锛屼績杩涙儏缁紦鍜屻€?/div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">鎰熺煡鎺у埗鐞嗚</div>
                                <div class="about-theory-text">涓诲姩鍙備笌鐜鏀归€犳湰韬細澧炲己鎺у埗鎰熶笌鎭㈠浣撻獙銆?/div>
                            </div>
                            <div class="about-theory-item">
                                <div class="about-theory-title">鍊?U 鍨嬫晥搴?/div>
                                <div class="about-theory-text">閫傚害澶嶆潅搴﹂€氬父姣旇繃灏戞垨杩囧鍒烘縺鏇村埄浜庡績鐞嗘仮澶嶃€?/div>
                            </div>
                        </div>
                    ''')

            bottom_nav('鍏充簬', light=True)
