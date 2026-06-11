"""Participant account page."""
from __future__ import annotations

import time
from html import escape

from nicegui import app, ui

from app.components.guide import guide_entry
from app.components.nav import smooth_navigate
from app.db import get_hci_participant_by_user_id, normalize_hci_participant_code
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


ACCOUNT_CSS = '''
<style>
.account-bg {
    --account-ink: #10251A;
    --account-muted: rgba(16,37,26,.62);
    --account-faint: rgba(16,37,26,.42);
    --account-green: #2F7B58;
    background:
        radial-gradient(circle at 50% 3%, rgba(183,242,126,.13), transparent 32%),
        linear-gradient(180deg, rgba(255,255,248,.90), rgba(243,248,238,.97) 54%, rgba(232,240,227,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
    color: var(--account-ink) !important;
}
.account-bg::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.05), transparent 24%),
        repeating-linear-gradient(90deg, rgba(38,70,52,.035) 0 1px, transparent 1px 42px) !important;
    opacity: .38 !important;
}
.account-shell {
    width: 100%;
    padding: 20px 20px 96px;
    gap: 16px;
}
.account-hero,
.account-section {
    width: 100%;
    border: 1px solid rgba(38,70,52,.12);
    border-radius: 8px;
    background:
        linear-gradient(180deg, rgba(255,255,248,.90), rgba(246,250,241,.78)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        rgba(255,255,248,.88);
    background-blend-mode: normal, soft-light, normal;
    color: var(--account-ink);
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
}
.account-hero {
    padding: 28px 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
}
.account-avatar {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: var(--account-green);
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 950;
    box-shadow: 0 18px 36px rgba(47,123,88,.20);
}
.account-name {
    margin-top: 8px;
    color: var(--account-ink);
    font-size: 24px;
    line-height: 1.2;
    font-weight: 950;
}
.account-subtitle {
    color: var(--account-muted);
    font-size: 13px;
    font-weight: 700;
}
.account-section {
    padding: 18px;
}
.account-section-title {
    color: var(--account-ink);
    font-size: 18px;
    line-height: 1.25;
    font-weight: 950;
    margin-bottom: 12px;
}
.account-info-grid {
    display: grid;
    gap: 0;
}
.account-row {
    min-height: 46px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr);
    align-items: center;
    gap: 16px;
    border-top: 1px solid rgba(38,70,52,.10);
}
.account-row:first-child {
    border-top: 0;
}
.account-label {
    color: var(--account-muted);
    font-size: 13px;
    line-height: 1.35;
    font-weight: 700;
}
.account-value {
    color: var(--account-ink);
    font-size: 14px;
    line-height: 1.35;
    font-weight: 900;
    text-align: right;
    overflow-wrap: anywhere;
}
.account-edit-btn,
.account-logout-btn {
    width: 100%;
    height: 50px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 900;
}
.account-edit-btn,
.account-bg .q-btn.account-edit-btn {
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    box-shadow: 0 14px 28px rgba(47,123,88,.18) !important;
}
.account-logout-btn,
.account-bg .q-btn.account-logout-btn {
    background: rgba(186,68,61,.08) !important;
    background-color: rgba(186,68,61,.08) !important;
    background-image: none !important;
    color: #BA443D !important;
    border: 1px solid rgba(186,68,61,.20) !important;
    box-shadow: none !important;
}
</style>
'''


def _display_date(timestamp: object) -> str:
    try:
        return time.strftime('%Y-%m-%d', time.localtime(float(timestamp)))
    except Exception:
        return '-'


def _display(value: object) -> str:
    text = str(value or '').strip()
    return text if text else '未填写'


def _initial(name: str) -> str:
    return (name or '用户')[:1].upper()


def create_account_page():
    @ui.page('/account')
    def account_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(ACCOUNT_CSS)

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        user_id = user.get('id')
        participant = get_hci_participant_by_user_id(user_id) or app.storage.user.get('hci_participant', {}) or {}
        participant_code = normalize_hci_participant_code(
            participant.get('participant_code') or user.get('participant_id')
        )
        display_name = (
            participant.get('registered_name')
            or user.get('display_name')
            or user.get('username')
            or '参与者'
        )
        registered_at = participant.get('created_at') or user.get('created_at')

        rows = [
            ('ID', participant_code or '未生成'),
            ('姓名 / 登记名', display_name),
            ('中心/社区编号', participant.get('site_id', '')),
            ('研究阶段', participant.get('study_phase', '')),
            ('诊断大类', participant.get('diagnosis_group', '')),
            ('出生日期', participant.get('birth_date', '')),
            ('性别', participant.get('gender', '')),
            ('教育层级', participant.get('education_band', '')),
            ('注册时间', _display_date(registered_at)),
            ('当前身份', '体验参与者'),
        ]

        def logout() -> None:
            app.storage.user.clear()
            smooth_navigate('/login')

        with ui.column().classes('mobile-page light-page account-bg').style('gap:0'):
            guide_entry(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style('color:#2F7B58')
                ui.label('我的账号').style(
                    'font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126'
                )

            with ui.column().classes('account-shell'):
                with ui.element('section').classes('account-hero'):
                    ui.html(f'<div class="account-avatar">{escape(_initial(display_name))}</div>', sanitize=False)
                    ui.html(f'<div class="account-name">{escape(display_name)}</div>', sanitize=False)
                    ui.html('<div class="account-subtitle">基本资料</div>', sanitize=False)

                with ui.element('section').classes('account-section'):
                    ui.html('<div class="account-section-title">基本信息</div>', sanitize=False)
                    with ui.element('div').classes('account-info-grid'):
                        for label, value in rows:
                            ui.html(
                                f'''
                                <div class="account-row">
                                    <div class="account-label">{escape(label)}</div>
                                    <div class="account-value">{escape(_display(value))}</div>
                                </div>
                                ''',
                                sanitize=False,
                            )

                ui.button(
                    '修改基本信息',
                    icon='edit',
                    on_click=lambda: smooth_navigate('/participant-info?next_path=/account'),
                    color=None,
                ).classes('account-edit-btn').props('unelevated no-caps')

                ui.button('退出登录', icon='logout', on_click=logout, color=None).classes(
                    'account-logout-btn'
                ).props('unelevated no-caps')
