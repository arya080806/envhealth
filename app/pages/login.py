"""Passwordless researcher-mediated login page."""
from __future__ import annotations

import asyncio

from nicegui import app, ui

from app.components.nav import smooth_navigate
from app.db import research_login_or_register
from app.theme import COMMON_STYLE, META_VIEWPORT


LOGIN_CSS = '''
<style>
.research-login-page {
    --ink: #10251A;
    --muted: rgba(16,37,26,.62);
    --green: #2F7B58;
    min-height: 100vh;
    width: 100%;
    background:
        linear-gradient(180deg, rgba(255,255,248,.94), rgba(238,247,235,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF;
}
.mobile-page.research-login-page {
    color: var(--ink) !important;
    background:
        linear-gradient(180deg, rgba(255,255,248,.94), rgba(238,247,235,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.mobile-page.research-login-page::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.04), transparent 22%),
        repeating-linear-gradient(90deg, rgba(38,70,52,.035) 0 1px, transparent 1px 42px);
    opacity: .42;
}
.research-login-shell {
    width: 100%;
    min-height: 100vh;
    padding: 48px 22px 34px;
    display: flex;
    flex-direction: column;
    gap: 18px;
}
.research-login-brand {
    color: var(--green);
    font-size: 12px;
    line-height: 1;
    font-weight: 900;
    letter-spacing: .08em;
}
.research-login-title {
    color: var(--ink);
    font-size: 31px;
    line-height: 1.18;
    font-weight: 950;
    margin-top: 8px;
}
.research-login-copy {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.62;
    font-weight: 680;
}
.research-login-form {
    width: 100%;
    margin-top: 10px;
    gap: 12px;
}
.research-login-form .q-field,
.research-login-form .q-select {
    width: 100%;
}
.research-login-form .q-field--outlined .q-field__control {
    background: rgba(255,255,248,.88) !important;
    border: 1px solid rgba(16,37,26,.16) !important;
    color: var(--ink) !important;
}
.research-login-form .q-field__native,
.research-login-form .q-field__input {
    color: var(--ink) !important;
    font-size: 15px !important;
    font-weight: 650 !important;
}
.research-login-form .q-field__label {
    color: rgba(16,37,26,.62) !important;
    font-weight: 650 !important;
}
.research-login-form .q-field__marginal,
.research-login-form .q-icon {
    color: rgba(16,37,26,.70) !important;
}
.research-login-submit {
    width: 100%;
    height: 54px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 900;
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    box-shadow: 0 16px 30px rgba(47,123,88,.20);
}
.research-login-page .q-btn.research-login-submit,
.research-login-page .q-btn.bg-primary.research-login-submit {
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    background-image: none !important;
    color: #FFFFFF !important;
}
.research-login-secondary {
    width: 100%;
    height: 54px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 900;
    background: rgba(47,123,88,.12) !important;
    background-color: rgba(47,123,88,.12) !important;
    background-image: none !important;
    color: #2F7B58 !important;
    box-shadow: 0 12px 26px rgba(47,123,88,.10);
}
.research-login-page .q-btn.research-login-secondary,
.research-login-page .q-btn.bg-primary.research-login-secondary {
    background: rgba(47,123,88,.12) !important;
    background-color: rgba(47,123,88,.12) !important;
    background-image: none !important;
    color: #2F7B58 !important;
}
.research-login-select-menu {
    background: #FFFDF4 !important;
    color: #10251A !important;
    border: 1px solid rgba(16,37,26,.12) !important;
    box-shadow: 0 18px 44px rgba(38,70,52,.18) !important;
}
.research-login-select-menu .q-item {
    min-height: 44px !important;
    color: #10251A !important;
}
.research-login-select-menu .q-item__label {
    color: #10251A !important;
    font-weight: 650 !important;
}
.research-login-select-menu .q-item--active,
.research-login-select-menu .q-item.q-manual-focusable--focused {
    background: rgba(47,123,88,.10) !important;
    color: #2F7B58 !important;
}
.research-login-code {
    width: 100%;
    min-height: 54px;
    border-radius: 20px;
    padding: 12px 14px;
    border: 1px solid rgba(47,123,88,.14);
    background: rgba(255,255,248,.68);
    color: var(--ink);
    font-size: 13px;
    line-height: 1.45;
    display: none;
}
.research-login-code strong {
    color: var(--green);
    font-size: 17px;
    letter-spacing: .03em;
}
.research-login-spacer {
    flex: 1;
}
.research-login-note {
    color: rgba(16,37,26,.46);
    font-size: 11px;
    line-height: 1.55;
    text-align: center;
}
</style>
'''


GENDERS = ['女', '男', '其他/未填写']


def _store_user(user: dict, participant: dict | None) -> None:
    app.storage.user['user'] = user
    if participant:
        app.storage.user['hci_participant'] = participant


def create_login_page():
    @ui.page('/login')
    async def login_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(LOGIN_CSS)

        async def submit(force_new: bool = False):
            submit_btn.disable()
            new_btn.disable()
            try:
                user, participant, created, error = research_login_or_register(
                    registered_name=name_input.value,
                    gender=gender_select.value,
                    force_new=force_new,
                )
                if error or not user:
                    ui.notify(error or '登记失败，请重试', type='negative')
                    return
                _store_user(user, participant)
                code = (participant or {}).get('participant_code') or user.get('participant_id', '')
                code_box.style('display:block')
                code_box.set_content(
                    f'<div>参与者编号</div><strong>{code}</strong>'
                )
                try:
                    from app.services.feishu_sync import sync_due_jobs_once
                    asyncio.create_task(sync_due_jobs_once(limit=5))
                except Exception:
                    pass
                ui.notify('已新建参与者' if created else '已登录已有参与者', type='positive')
                target = '/participant-info?next_path=/camera' if created else '/'
                ui.timer(0.65, lambda: smooth_navigate(target), once=True)
            finally:
                submit_btn.enable()
                new_btn.enable()

        with ui.element('div').classes('mobile-page research-login-page'):
            with ui.element('div').classes('research-login-shell'):
                ui.html('<div class="research-login-brand">RESEARCH ACCESS</div>', sanitize=False)
                ui.html('<div class="research-login-title">参与者登记</div>', sanitize=False)
                ui.html(
                    '<div class="research-login-copy">由研究人员代为登记。系统会自动生成顺序编号，患者无需记忆密码。</div>',
                    sanitize=False,
                )

                with ui.column().classes('research-login-form'):
                    name_input = ui.input('姓名 / 研究登记名').props('outlined dense clearable')
                    gender_select = ui.select(
                        GENDERS,
                        label='性别',
                        value='其他/未填写',
                    ).props('outlined dense popup-content-class=research-login-select-menu')
                    code_box = ui.html('', sanitize=False).classes('research-login-code')

                    submit_btn = ui.button(
                        '登录',
                        on_click=lambda: submit(False),
                        color=None,
                    ).classes('research-login-submit').props('unelevated no-caps')
                    new_btn = ui.button(
                        '注册',
                        on_click=lambda: submit(True),
                        color=None,
                    ).classes('research-login-secondary').props('unelevated no-caps')

                ui.element('div').classes('research-login-spacer')
                ui.html(
                    '<div class="research-login-note">同名同性会优先登录已有记录；确认为另一位参与者时使用“注册”。</div>',
                    sanitize=False,
                )
