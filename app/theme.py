"""全局主题配置 - 自然沉浸式高级 UI 设计系统"""

COLORS = {
    # 自然深绿色系
    'primary': '#2D6A4F',
    'primary_light': '#52B788',
    'primary_dark': '#1B4332',
    'primary_ultra_light': '#95D5B2',
    # 辅助色
    'secondary': '#40916C',
    'accent': '#D4A373',
    'accent_light': '#E9C46A',
    # 中性色
    'background': '#F8FAF5',
    'surface': '#FFFFFF',
    'text': '#1A1A2E',
    'text_secondary': '#6B7280',
    'text_light': 'rgba(255,255,255,0.9)',
    # 功能色
    'success': '#52B788',
    'warning': '#E9C46A',
    'error': '#E76F51',
    'border': 'rgba(45,106,79,0.12)',
    # 毛玻璃
    'glass': 'rgba(255,255,255,0.72)',
    'glass_border': 'rgba(255,255,255,0.35)',
    'glass_dark': 'rgba(27,67,50,0.65)',
    # 渐变
    'gradient_start': '#1B4332',
    'gradient_mid': '#2D6A4F',
    'gradient_end': '#52B788',
}

# 自然背景渐变（用于 Hero 区域）
NATURE_BG_CSS = (
    'background: linear-gradient(160deg, #1B4332 0%, #2D6A4F 35%, #40916C 65%, #52B788 100%);'
)

# 毛玻璃卡片标准样式
GLASS_CARD_STYLE = (
    'background: rgba(255,255,255,0.72); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);'
    'border: 1px solid rgba(255,255,255,0.35); border-radius: 20px;'
    'box-shadow: 0 8px 32px rgba(27,67,50,0.08);'
)

# 顶部导航栏样式
TOP_BAR_STYLE = (
    'width:100%; display:flex; align-items:center; padding:14px 20px;'
    'background:rgba(255,255,255,0.85); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);'
    'border-bottom:1px solid rgba(45,106,79,0.08);'
)

# 底部导航栏样式
BOTTOM_NAV_STYLE = (
    'width:100%; display:flex; justify-content:space-around; padding:10px 0 18px 0;'
    'background:rgba(255,255,255,0.88); backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);'
    'border-top:1px solid rgba(45,106,79,0.08);'
)

# 主操作按钮样式
PRIMARY_BTN_STYLE = (
    'width:100%; background:linear-gradient(135deg, #2D6A4F 0%, #52B788 100%);'
    'color:white; border:none; border-radius:28px; padding:16px 32px;'
    'font-size:16px; font-weight:600; letter-spacing:0.5px;'
    'box-shadow:0 8px 24px rgba(45,106,79,0.25);'
    'transition:all 0.3s ease;'
)

COMMON_STYLE = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

body {
    font-family: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif !important;
    overscroll-behavior: none;
    background: linear-gradient(160deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
    -webkit-font-smoothing: antialiased;
}

.nicegui-content { padding: 0 !important; }

/* ===== 移动页面容器 ===== */
.mobile-page {
    max-width: 480px;
    margin: 0 auto;
    min-height: 100vh;
    background: #F8FAF5;
    position: relative;
    overflow-x: hidden;
}

/* ===== 毛玻璃效果 ===== */
.glass-card {
    background: rgba(255,255,255,0.72) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(27,67,50,0.08) !important;
}

.glass-dark {
    background: rgba(27,67,50,0.65) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(82,183,136,0.2) !important;
    border-radius: 20px !important;
}

/* ===== 动画 ===== */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 8px 24px rgba(45,106,79,0.25); }
    50% { box-shadow: 0 8px 40px rgba(82,183,136,0.4); }
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

.animate-in {
    animation: fadeInUp 0.6s ease-out both;
}

.animate-in-delay-1 { animation-delay: 0.1s; }
.animate-in-delay-2 { animation-delay: 0.2s; }
.animate-in-delay-3 { animation-delay: 0.3s; }
.animate-in-delay-4 { animation-delay: 0.4s; }

.float-animation {
    animation: float 4s ease-in-out infinite;
}

.pulse-glow {
    animation: pulse-glow 2.5s ease-in-out infinite;
}

/* ===== 自然 Hero 背景 ===== */
.nature-hero {
    background: linear-gradient(160deg, #1B4332 0%, #2D6A4F 35%, #40916C 65%, #52B788 100%);
    position: relative;
    overflow: hidden;
}

.nature-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 20%, rgba(82,183,136,0.3) 0%, transparent 50%),
                radial-gradient(ellipse at 70% 80%, rgba(149,213,178,0.2) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(64,145,108,0.15) 0%, transparent 60%);
    animation: float 8s ease-in-out infinite;
    pointer-events: none;
}

.nature-hero::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 80px;
    background: linear-gradient(to top, #F8FAF5, transparent);
    pointer-events: none;
}

/* ===== 药丸导航 ===== */
.pill-nav {
    display: inline-flex;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 25px;
    padding: 4px;
    gap: 4px;
}

.pill-nav-item {
    padding: 8px 20px;
    border-radius: 22px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    color: rgba(255,255,255,0.7);
    border: none;
    background: transparent;
}

.pill-nav-item.active {
    background: rgba(255,255,255,0.9);
    color: #2D6A4F;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* ===== 卡片交互 ===== */
.hover-lift {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.hover-lift:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(27,67,50,0.12);
}

.card-press {
    transition: all 0.15s ease;
}
.card-press:active {
    transform: scale(0.97);
}

/* ===== 进度条 ===== */
.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(45,106,79,0.08);
    border-radius: 4px;
    overflow: hidden;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== 自定义滚动条 ===== */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(45,106,79,0.2);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(45,106,79,0.35); }

/* ===== Quasar 组件覆盖 ===== */
.q-slider__track-container { height: 6px !important; }
.q-slider__track { border-radius: 3px !important; }
.q-slider__thumb {
    width: 22px !important;
    height: 22px !important;
    border: 3px solid white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}

.q-field--outlined .q-field__control {
    border-radius: 16px !important;
    border-color: rgba(45,106,79,0.15) !important;
}

.q-btn { text-transform: none !important; }

/* ===== 标签药丸 ===== */
.tag-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
}

/* ===== 分割线 ===== */
.section-divider {
    width: 40px;
    height: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, #2D6A4F, #52B788);
    margin: 4px 0 12px 0;
}

/* ===== 加载 Spinner 覆盖 ===== */
.loading-overlay {
    position: fixed;
    inset: 0;
    background: rgba(27,67,50,0.75);
    backdrop-filter: blur(8px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

</style>
'''

META_VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
