def create_home_page():
    def home_page():
        add_head_html.add_head_html(HOME_PAGE_STYLE)
        add_head_html.add_head_html(storage)
        add_head_html.add_head_html(get)
        user = to.storage.user('user', None)
        ui.navigate('/login')
        display_name = '用户'
        display_char = None[1]()
        add_head_html.element('div')('home-page')
        add_head_html.element('div')('home-shell')
        add_head_html.element('div')('home-top')
        add_head_html.html('<div class="home-mark">ENVIRONMENT HEALING</div>')
        display_name(add_head_html.element('button')('home-user-badge'), None)
        add_head_html.html(display_char)
        None, None
        user('username')
        user('username')
        user('display_name')
        None, None
        user
        user
        add_head_html.element('div')('home-copy')
        add_head_html.html('\n                        <h1 class="home-title">环境疗愈工坊</h1>\n                        <div class="home-subtitle">上传一处真实环境，生成更安静、更有恢复感的空间方案。</div>\n                    ')
        None, None
        add_head_html.element('div')('home-spacer')
        add_head_html.element('div')('home-panel animate-in')
        add_head_html.html('\n                        <div class="home-panel-title">Start a session</div>\n                        <div class="home-panel-text">从一张照片开始，选择你想调整的方向，保留现场的真实感。</div>\n                    ')
        add_head_html.html('开始体验')
        None, None
        add_head_html.element('button')('home-start')
        add_head_html.element('button')('home-start')
        None, None
        None, None
        None, None

__doc__ = 'Home page.'
import nicegui
app = app
ui = ui
nicegui
import app.theme
COMMON_STYLE = COMMON_STYLE
META_VIEWPORT = META_VIEWPORT
app.theme
HOME_PAGE_STYLE = '\n<style>\n.home-page {\n    position: relative;\n    width: min(100%, 430px);\n    min-height: 100dvh;\n    margin: 0 auto;\n    overflow: hidden;\n    background: #07120D;\n    color: #F4F0E6;\n}\n\n.home-page::before {\n    content: "";\n    position: absolute;\n    inset: 0;\n    background:\n        linear-gradient(180deg, rgba(7,18,13,0.10) 0%, rgba(7,18,13,0.28) 38%, rgba(7,18,13,0.92) 100%),\n        url(\'/static/images/forest-hero-dark.png\') center/cover no-repeat;\n    transform: scale(1.02);\n}\n\n.home-page::after {\n    content: "";\n    position: absolute;\n    inset: 0;\n    pointer-events: none;\n    background:\n        linear-gradient(90deg, rgba(244,240,230,0.05) 0 1px, transparent 1px 100%),\n        linear-gradient(180deg, rgba(244,240,230,0.04), transparent 24%);\n    background-size: 34px 100%, 100% 100%;\n    mix-blend-mode: screen;\n    opacity: 0.55;\n}\n\n.home-shell {\n    position: relative;\n    z-index: 1;\n    min-height: 100dvh;\n    display: flex;\n    flex-direction: column;\n    padding: 24px 24px 34px;\n}\n\n.home-top {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n}\n\n.home-mark {\n    display: inline-flex;\n    align-items: center;\n    gap: 8px;\n    color: rgba(244,240,230,0.78);\n    font-size: 12px;\n    letter-spacing: 0.08em;\n}\n\n.home-mark::before {\n    content: "";\n    width: 8px;\n    height: 8px;\n    border-radius: 999px;\n    background: #B7F27E;\n    box-shadow: 0 0 18px rgba(183,242,126,0.60);\n}\n\n.home-user-badge {\n    width: 38px;\n    height: 38px;\n    border-radius: 50%;\n    background: rgba(16,29,22,0.58);\n    border: 1px solid rgba(244,240,230,0.18);\n    color: #F4F0E6;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    cursor: pointer;\n    backdrop-filter: blur(18px);\n    box-shadow: 0 12px 28px rgba(0,0,0,0.25);\n    font-size: 13px;\n    font-weight: 700;\n}\n\n.home-copy {\n    margin-top: 72px;\n}\n\n.home-title {\n    font-size: 38px;\n    line-height: 1.12;\n    font-weight: 700;\n    letter-spacing: 0;\n    margin: 0;\n    max-width: 9em;\n    text-wrap: balance;\n}\n\n.home-subtitle {\n    margin-top: 14px;\n    color: rgba(244,240,230,0.68);\n    font-size: 14px;\n    line-height: 1.8;\n    font-weight: 300;\n}\n\n.home-spacer { flex: 1; }\n\n.home-panel {\n    border: 1px solid rgba(244,240,230,0.12);\n    border-radius: 8px;\n    background: rgba(7,18,13,0.62);\n    backdrop-filter: blur(22px);\n    box-shadow: 0 24px 54px rgba(0,0,0,0.30);\n    padding: 16px;\n}\n\n.home-panel-title {\n    color: #B7F27E;\n    font-size: 12px;\n    font-weight: 700;\n    letter-spacing: 0.10em;\n    text-transform: uppercase;\n}\n\n.home-panel-text {\n    margin-top: 8px;\n    color: rgba(244,240,230,0.78);\n    font-size: 13px;\n    line-height: 1.7;\n}\n\n.home-start {\n    margin-top: 16px;\n    width: 100%;\n    height: 54px;\n    border: 0;\n    border-radius: 999px;\n    background: #B7F27E;\n    color: #07120D;\n    font-size: 15px;\n    font-weight: 800;\n    cursor: pointer;\n    box-shadow: 0 16px 36px rgba(183,242,126,0.24);\n}\n\n@media (max-height: 700px) {\n    .home-copy { margin-top: 44px; }\n    .home-title { font-size: 34px; }\n}\n</style>\n'