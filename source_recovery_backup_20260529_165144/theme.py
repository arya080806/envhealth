"""Global visual system for the mobile-first healing environment UI."""

COLORS = {
    'primary': '#B7F27E',
    'primary_light': '#D8FF9A',
    'primary_dark': '#10251A',
    'primary_ultra_light': '#ECFFD4',
    'secondary': '#7FA38D',
    'accent': '#D7B46A',
    'accent_light': '#F0D996',
    'background': '#07120D',
    'surface': '#101D16',
    'surface_2': '#17261D',
    'text': '#F4F0E6',
    'text_secondary': '#A9B5AA',
    'text_muted': '#6F7D72',
    'text_light': 'rgba(244,240,230,0.92)',
    'success': '#B7F27E',
    'warning': '#D7B46A',
    'error': '#FF7B6E',
    'border': 'rgba(244,240,230,0.12)',
    'glass': 'rgba(15,29,22,0.72)',
    'glass_border': 'rgba(244,240,230,0.12)',
    'glass_dark': 'rgba(7,18,13,0.78)',
    'gradient_start': '#07120D',
    'gradient_mid': '#12281C',
    'gradient_end': '#B7F27E',
}

NATURE_BG_CSS = (
    'background:linear-gradient(180deg, rgba(7,18,13,0.10), rgba(7,18,13,0.82)),'
    'url("/static/images/forest-hero-dark.webp") center/cover no-repeat;'
)

GLASS_CARD_STYLE = (
    'background:rgba(16,29,22,0.74); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);'
    'border:1px solid rgba(244,240,230,0.12); border-radius:18px;'
    'box-shadow:0 18px 44px rgba(0,0,0,0.22); color:#F4F0E6;'
)

TOP_BAR_STYLE = (
    'width:100%; display:flex; align-items:center; padding:14px 18px;'
    'background:rgba(7,18,13,0.70); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);'
    'border-bottom:1px solid rgba(244,240,230,0.10); color:#F4F0E6;'
    'position:sticky; top:0; z-index:60;'
)

BOTTOM_NAV_STYLE = (
    'width:min(100%,430px); display:flex; justify-content:space-around; padding:10px 14px 16px 14px;'
    'background:rgba(7,18,13,0.82); backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);'
    'border-top:1px solid rgba(244,240,230,0.10);'
    'position:fixed; bottom:0; left:50%; transform:translateX(-50%); z-index:100;'
    'box-shadow:0 -18px 44px rgba(0,0,0,0.28);'
)

LIGHT_BOTTOM_NAV_STYLE = (
    'width:min(100%,430px); display:flex; justify-content:space-around; padding:10px 14px 16px 14px;'
    'background:rgba(247,249,241,0.88); backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);'
    'border-top:1px solid rgba(38,70,52,0.10);'
    'position:fixed; bottom:0; left:50%; transform:translateX(-50%); z-index:100;'
    'box-shadow:0 -18px 44px rgba(38,70,52,0.12);'
)

PRIMARY_BTN_STYLE = (
    'width:100%; background:#B7F27E; color:#07120D; border:none; border-radius:999px;'
    'padding:15px 24px; font-size:15px; font-weight:700; letter-spacing:0;'
    'box-shadow:0 12px 30px rgba(183,242,126,0.24); transition:all 0.22s ease;'
)

LIGHT_TOP_BAR_STYLE = (
    'width:100%; display:flex; align-items:center; padding:14px 18px;'
    'background:rgba(247,249,241,0.82); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);'
    'border-bottom:1px solid rgba(38,70,52,0.10); color:#173126;'
    'position:sticky; top:0; z-index:60;'
)

LIGHT_PRIMARY_BTN_STYLE = (
    'width:100%; background:#2F7B58 !important; color:#F8FAF2 !important; border:none; border-radius:999px;'
    'padding:15px 24px; font-size:15px; font-weight:800; letter-spacing:0;'
    'box-shadow:0 14px 30px rgba(47,123,88,0.20); transition:all 0.22s ease;'
)

COMMON_STYLE = '''
<style>
:root {
    --bg: #07120D;
    --bg-2: #0B1811;
    --panel: rgba(16,29,22,0.74);
    --panel-solid: #101D16;
    --panel-2: #17261D;
    --line: rgba(244,240,230,0.12);
    --line-strong: rgba(244,240,230,0.20);
    --text: #F4F0E6;
    --text-2: #A9B5AA;
    --text-3: #6F7D72;
    --lime: #B7F27E;
    --lime-2: #D8FF9A;
    --gold: #D7B46A;
    --danger: #FF7B6E;
    --bluegray: #88A6A0;
    --radius: 18px;
    --shadow: 0 18px 44px rgba(0,0,0,0.22);
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
    --q-primary: #2F7B58;
}

* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

html, body {
    min-height: 100%;
    background:
        linear-gradient(90deg, rgba(7,18,13,0.92), rgba(7,18,13,0.74), rgba(7,18,13,0.92)),
        url('/static/images/nature-texture-dark.webp') center/cover fixed no-repeat,
        #07120D !important;
    color: var(--text);
    font-family: var(--font) !important;
    overscroll-behavior: none;
    -webkit-font-smoothing: antialiased;
}

body.body--light {
    background:
        linear-gradient(90deg, rgba(7,18,13,0.92), rgba(7,18,13,0.74), rgba(7,18,13,0.92)),
        url('/static/images/nature-texture-dark.webp') center/cover fixed no-repeat,
        #07120D !important;
    color: var(--text);
}

.nicegui-content {
    min-height: 100vh;
    padding: 0 !important;
    animation: pageEnter 0.26s ease-out both;
}

.mobile-page {
    width: min(100%, 430px) !important;
    max-width: 430px !important;
    min-height: 100dvh !important;
    margin: 0 auto !important;
    position: relative !important;
    overflow-x: hidden !important;
    color: var(--text) !important;
    background:
        linear-gradient(180deg, rgba(7,18,13,0.48) 0%, rgba(7,18,13,0.96) 58%, rgba(7,18,13,1) 100%),
        url('/static/images/nature-texture-dark.webp') center/cover no-repeat,
        var(--bg) !important;
    box-shadow: 0 0 0 1px rgba(244,240,230,0.06), 0 28px 90px rgba(0,0,0,0.36);
}

@media (max-width: 520px) {
    html, body, body.body--light {
        background: var(--bg) !important;
    }
    .mobile-page {
        width: 100% !important;
        max-width: none !important;
        box-shadow: none !important;
    }
}

.mobile-page::before {
    content: "";
    position: fixed;
    inset: 0;
    width: min(100%, 430px);
    margin: 0 auto;
    pointer-events: none;
    background:
        linear-gradient(180deg, rgba(244,240,230,0.045), transparent 18%),
        repeating-linear-gradient(90deg, rgba(244,240,230,0.018) 0 1px, transparent 1px 34px);
    opacity: 0.8;
    z-index: 0;
}

.mobile-page > * {
    position: relative;
    z-index: 1;
}

.mobile-page.light-page {
    --light-bg: #F6F8EF;
    --light-bg-2: #E8F0E3;
    --light-paper: rgba(255,255,248,0.82);
    --light-paper-solid: #FFFDF4;
    --light-panel: rgba(255,255,248,0.72);
    --light-ink: #173126;
    --light-ink-2: rgba(23,49,38,0.68);
    --light-ink-3: rgba(23,49,38,0.46);
    --light-green: #2F7B58;
    --light-green-soft: rgba(47,123,88,0.10);
    --q-primary: #2F7B58;
    color: var(--light-ink) !important;
    background:
        linear-gradient(180deg, rgba(255,255,248,0.80) 0%, rgba(244,248,239,0.94) 48%, rgba(232,240,227,0.98) 100%),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}

.mobile-page.light-page::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,0.045), transparent 22%),
        repeating-linear-gradient(90deg, rgba(38,70,52,0.035) 0 1px, transparent 1px 42px);
    opacity: 0.38;
}

.light-page .q-card,
.light-page .glass-card,
.light-page .detail-section,
.light-page .scheme-card-ro,
.light-page .slider-bar-ro,
.light-page .mood-card-ro,
.light-page .about-panel,
.light-page .mode-card,
.light-page .mode-intro,
.light-page .theory-note {
    background:
        linear-gradient(180deg, rgba(255,255,248,0.88), rgba(246,250,241,0.76)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        rgba(255,255,248,0.86) !important;
    background-blend-mode: normal, soft-light, normal !important;
    color: var(--light-ink) !important;
    border-color: rgba(38,70,52,0.12) !important;
    box-shadow: 0 16px 34px rgba(38,70,52,0.08) !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
}

.light-page .rec-card {
    background:
        linear-gradient(180deg, rgba(255,255,248,0.88), rgba(246,250,241,0.76)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        rgba(255,255,248,0.86) !important;
    background-blend-mode: normal, soft-light, normal !important;
    color: var(--light-ink) !important;
    border-color: rgba(38,70,52,0.12) !important;
    box-shadow: 0 16px 34px rgba(38,70,52,0.08) !important;
}

.light-page .q-card *,
.light-page .glass-card *,
.light-page .detail-section *,
.light-page .scheme-card-ro *,
.light-page .slider-bar-ro *,
.light-page .rec-card * {
    color: inherit;
}

.light-page label,
.light-page .q-field__native,
.light-page .q-field__input,
.light-page .q-field__label,
.light-page .q-item__label,
.light-page .q-checkbox__label,
.light-page .q-radio__label {
    color: var(--light-ink) !important;
}

.light-page .q-field--outlined .q-field__control,
.light-page .q-field--filled .q-field__control {
    background: rgba(255,255,248,0.78) !important;
    border-color: rgba(38,70,52,0.14) !important;
    color: var(--light-ink) !important;
}

.light-page .q-btn--standard,
.light-page .q-btn--rectangle.q-btn--unelevated {
    background: var(--light-green) !important;
    color: #F8FAF2 !important;
    box-shadow: 0 14px 30px rgba(47,123,88,0.20) !important;
}

.light-page .q-btn--flat,
.light-page .q-btn--outline {
    color: var(--light-green) !important;
}

.light-page .section-divider {
    background: rgba(47,123,88,0.62) !important;
}

.light-page .tag-pill {
    color: var(--light-green) !important;
    background: var(--light-green-soft) !important;
    border-color: rgba(47,123,88,0.16) !important;
}

.light-page .progress-bar {
    background: rgba(38,70,52,0.09) !important;
}

.light-page .progress-bar-fill,
.light-page .q-slider__selection {
    background: var(--light-green) !important;
}

.q-layout, .q-page-container, .q-page, .q-body--fullscreen-mixin {
    background: transparent !important;
    color: var(--text) !important;
}

.q-card,
.glass-card,
.detail-section,
.scheme-card-ro,
.slider-bar-ro,
.mood-card-ro,
.rec-card,
.record-card {
    background:
        linear-gradient(180deg, rgba(16,29,22,0.82), rgba(16,29,22,0.72)),
        url('/static/images/bamboo-mist-texture.webp') center/cover no-repeat,
        var(--panel-solid) !important;
    background-blend-mode: normal, soft-light, normal !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
    backdrop-filter: blur(22px) !important;
    -webkit-backdrop-filter: blur(22px) !important;
}

.q-card .q-card__section {
    color: inherit !important;
}

.glass-dark {
    background: rgba(7,18,13,0.78) !important;
    border: 1px solid rgba(183,242,126,0.14) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}

.nature-hero {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(180deg, rgba(7,18,13,0.10), rgba(7,18,13,0.86)),
        url('/static/images/forest-hero-dark.webp') center/cover no-repeat !important;
    border: 1px solid rgba(244,240,230,0.12) !important;
    border-radius: var(--radius) !important;
}

.nature-hero::before,
.nature-hero::after {
    content: none !important;
}

label,
.q-field__label,
.q-field__native,
.q-field__input,
.q-placeholder,
.q-tab__label,
.q-item__label,
.q-checkbox__label,
.q-radio__label {
    font-family: var(--font) !important;
}

.mobile-page .q-field--outlined .q-field__control,
.mobile-page .q-field--filled .q-field__control {
    min-height: 48px !important;
    border-radius: var(--radius) !important;
    background: rgba(244,240,230,0.06) !important;
    border: 1px solid var(--line) !important;
    color: var(--text) !important;
}

.mobile-page .q-field--outlined .q-field__control::before,
.mobile-page .q-field--outlined .q-field__control::after {
    border-color: transparent !important;
}

.mobile-page .q-field__native,
.mobile-page .q-field__input,
.mobile-page .q-field__label {
    color: var(--text) !important;
}

.mobile-page .q-field__label {
    color: var(--text-2) !important;
}

.mobile-page .q-field__marginal {
    color: var(--text-2) !important;
}

.q-btn {
    text-transform: none !important;
    letter-spacing: 0 !important;
    border-radius: 999px !important;
    font-weight: 650 !important;
    touch-action: manipulation;
    will-change: transform;
}

button,
[role="button"],
.mode-card,
.account-action,
.home-start,
.home-user-badge,
.rec-card,
.record-card {
    touch-action: manipulation;
    will-change: transform;
}

.q-btn--standard,
.q-btn--rectangle.q-btn--unelevated {
    background: var(--lime) !important;
    color: var(--bg) !important;
    box-shadow: 0 12px 30px rgba(183,242,126,0.22) !important;
}

.q-btn--outline::before {
    border-color: rgba(244,240,230,0.22) !important;
}

.q-btn--flat,
.q-btn--outline {
    color: var(--text) !important;
}

.q-btn:active,
.card-press:active {
    transform: scale(0.98);
}

.q-tabs {
    background: rgba(244,240,230,0.06) !important;
    border: 1px solid var(--line) !important;
    border-radius: 999px !important;
    padding: 3px !important;
    color: var(--text-2) !important;
}

.q-tab {
    border-radius: 999px !important;
    min-height: 38px !important;
    color: var(--text-2) !important;
}

.q-tab--active {
    background: rgba(183,242,126,0.16) !important;
    color: var(--lime) !important;
}

.q-tab__indicator {
    display: none !important;
}

.q-separator {
    background: var(--line) !important;
}

.q-slider__track-container { height: 5px !important; }
.q-slider__track { border-radius: 999px !important; }
.q-slider__selection {
    background: var(--lime) !important;
}
.q-slider__thumb {
    width: 22px !important;
    height: 22px !important;
    color: var(--lime) !important;
    border: 3px solid rgba(7,18,13,0.95) !important;
    box-shadow: 0 4px 16px rgba(183,242,126,0.28) !important;
}

.tag-pill,
.rec-element-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 11px !important;
    border-radius: 999px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: var(--lime) !important;
    background: rgba(183,242,126,0.10) !important;
    border: 1px solid rgba(183,242,126,0.16) !important;
    white-space: nowrap;
}

.section-divider {
    width: 32px !important;
    height: 1px !important;
    border-radius: 999px !important;
    background: rgba(183,242,126,0.64) !important;
    margin: 6px 0 12px 0 !important;
}

.progress-bar {
    width: 100%;
    height: 7px !important;
    background: rgba(244,240,230,0.08) !important;
    border-radius: 999px !important;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 999px !important;
    background: var(--lime) !important;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.loading-overlay {
    position: fixed;
    inset: 0;
    width: min(100%, 430px);
    margin: 0 auto;
    background: rgba(7,18,13,0.82) !important;
    backdrop-filter: blur(14px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

.q-notification {
    border-radius: var(--radius) !important;
    background: rgba(16,29,22,0.92) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow) !important;
}

.q-dialog__inner > .q-card {
    width: min(92vw, 390px) !important;
    background: rgba(16,29,22,0.92) !important;
    color: var(--text) !important;
}

.hover-lift {
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.hover-lift:hover {
    transform: translateY(-2px);
    border-color: rgba(183,242,126,0.22) !important;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes pageEnter {
    from { opacity: 0.01; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 12px 30px rgba(183,242,126,0.20); }
    50% { box-shadow: 0 12px 38px rgba(183,242,126,0.34); }
}

.animate-in { animation: fadeInUp 0.48s ease-out both; }
.animate-in-delay-1 { animation-delay: 0.06s; }
.animate-in-delay-2 { animation-delay: 0.12s; }
.animate-in-delay-3 { animation-delay: 0.18s; }
.animate-in-delay-4 { animation-delay: 0.24s; }
.float-animation { animation: float 4.2s ease-in-out infinite; }
.pulse-glow { animation: pulse-glow 2.8s ease-in-out infinite; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(244,240,230,0.18);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(244,240,230,0.28); }

.text-primary { color: var(--lime) !important; }
.text-secondary { color: var(--text-2) !important; }

.mobile-page.light-page,
.mobile-page.light-page .q-page,
.mobile-page.light-page .q-card,
.mobile-page.light-page .q-card__section {
    color: var(--light-ink) !important;
}

.mobile-page.light-page .q-field--outlined .q-field__control,
.mobile-page.light-page .q-field--filled .q-field__control {
    background: rgba(255,255,248,0.80) !important;
    border: 1px solid rgba(38,70,52,0.14) !important;
    color: var(--light-ink) !important;
}

.mobile-page.light-page .q-field__native,
.mobile-page.light-page .q-field__input,
.mobile-page.light-page .q-field__label,
.mobile-page.light-page .q-field__marginal {
    color: var(--light-ink-2) !important;
}

.mobile-page.light-page .q-tabs {
    background: rgba(255,255,248,0.64) !important;
    border-color: rgba(38,70,52,0.12) !important;
    color: var(--light-ink-2) !important;
}

.mobile-page.light-page .q-tab {
    color: var(--light-ink-2) !important;
}

.mobile-page.light-page .q-tab--active {
    background: rgba(47,123,88,0.12) !important;
    color: var(--light-green) !important;
}

.mobile-page.light-page .q-slider__track {
    background: rgba(38,70,52,0.10) !important;
}

.mobile-page.light-page .q-slider__selection,
.mobile-page.light-page .q-slider__thumb {
    color: var(--light-green) !important;
    background: var(--light-green) !important;
}

.mobile-page.light-page .q-slider__thumb {
    border-color: rgba(255,255,248,0.95) !important;
    box-shadow: 0 4px 14px rgba(47,123,88,0.20) !important;
}

.mobile-page.light-page .q-btn--standard,
.mobile-page.light-page .q-btn--rectangle.q-btn--unelevated {
    background: var(--light-green) !important;
    color: #F8FAF2 !important;
    box-shadow: 0 14px 30px rgba(47,123,88,0.20) !important;
}

.mobile-page.light-page .bg-primary {
    background: var(--light-green) !important;
    background-color: var(--light-green) !important;
    background-image: none !important;
}

.mobile-page.light-page .text-primary {
    color: var(--light-green) !important;
}

.mobile-page.light-page button.q-btn.text-primary,
.mobile-page.light-page .q-btn.text-primary,
.mobile-page.light-page .q-icon.text-primary {
    color: var(--light-green) !important;
}

.mobile-page.light-page .q-btn--outline::before {
    border-color: rgba(47,123,88,0.28) !important;
}

.mobile-page.light-page .q-btn--flat,
.mobile-page.light-page .q-btn--outline {
    color: var(--light-green) !important;
}

.light-action-panel {
    width: 100%;
    padding: 14px 20px 100px;
    background:
        linear-gradient(180deg, rgba(255,255,248,0.70), rgba(239,246,232,0.94)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat !important;
    background-blend-mode: normal, soft-light !important;
    border-top: 1px solid rgba(38,70,52,0.10) !important;
    box-shadow: 0 -18px 34px rgba(38,70,52,0.08) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}

.light-bottom-dock {
    position: fixed !important;
    bottom: 80px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: min(100%, 430px) !important;
    padding: 14px 20px 16px !important;
    z-index: 50 !important;
}

img {
    max-width: 100%;
}

#healing-route-transition {
    position: fixed;
    inset: 0;
    width: min(100%, 430px);
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(180deg, rgba(7,18,13,0.70), rgba(7,18,13,0.92)),
        url('/static/images/nature-texture-dark.webp') center/cover no-repeat;
    color: var(--text);
    opacity: 0;
    pointer-events: none;
    z-index: 5000;
    transition: opacity 0.16s ease;
}

#healing-route-transition::after {
    content: "";
    width: 34px;
    height: 34px;
    border-radius: 50%;
    border: 3px solid rgba(244,240,230,0.22);
    border-top-color: var(--lime);
    animation: routeSpin 0.72s linear infinite;
}

body.healing-route-leaving #healing-route-transition {
    opacity: 1;
    pointer-events: auto;
}

@keyframes routeSpin {
    to { transform: rotate(360deg); }
}
</style>
<script>
(function () {
    if (window.HealingMotion) return;

    function ensureOverlay() {
        if (document.getElementById('healing-route-transition')) return;
        var overlay = document.createElement('div');
        overlay.id = 'healing-route-transition';
        overlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(overlay);
    }

    function showRouteTransition() {
        ensureOverlay();
        document.body.classList.add('healing-route-leaving');
    }

    function hideRouteTransition() {
        document.body.classList.remove('healing-route-leaving');
    }

    window.HealingMotion = {
        showRouteTransition: showRouteTransition,
        hideRouteTransition: hideRouteTransition
    };

    document.addEventListener('DOMContentLoaded', function () {
        ensureOverlay();
        window.requestAnimationFrame(function () {
            document.body.classList.add('healing-page-ready');
            hideRouteTransition();
        });
    });

    window.addEventListener('pageshow', hideRouteTransition);
    window.addEventListener('beforeunload', showRouteTransition);
})();
</script>
'''

META_VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
