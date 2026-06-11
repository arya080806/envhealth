"""HCI participant information page."""
from __future__ import annotations

import asyncio
from datetime import date

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.db import get_hci_participant_by_user_id, normalize_hci_participant_code, upsert_hci_participant
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


PARTICIPANT_INFO_CSS = '''
<style>
.participant-bg {
    --ink: #10251A;
    --muted: rgba(16,37,26,.64);
    --green: #2F7B58;
    background:
        linear-gradient(180deg, rgba(255,255,248,.94), rgba(239,247,235,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.mobile-page.participant-bg .q-field--outlined .q-field__control {
    background: rgba(255,255,248,.90) !important;
    border: 1px solid rgba(16,37,26,.16) !important;
    color: var(--ink) !important;
}
.mobile-page.participant-bg .q-field__native,
.mobile-page.participant-bg .q-field__input,
.mobile-page.participant-bg .q-field__prefix,
.mobile-page.participant-bg .q-field__suffix {
    color: var(--ink) !important;
    font-size: 15px !important;
    font-weight: 650 !important;
}
.mobile-page.participant-bg .q-field__label {
    color: rgba(16,37,26,.62) !important;
    font-weight: 650 !important;
}
.mobile-page.participant-bg .q-field__marginal,
.mobile-page.participant-bg .q-field__append,
.mobile-page.participant-bg .q-icon {
    color: rgba(16,37,26,.70) !important;
}
.participant-select-menu {
    background: #FFFDF4 !important;
    color: #10251A !important;
    border: 1px solid rgba(16,37,26,.12) !important;
    box-shadow: 0 18px 44px rgba(38,70,52,.18) !important;
}
.participant-select-menu .q-item {
    color: #10251A !important;
    min-height: 44px !important;
}
.participant-select-menu .q-item__label {
    color: #10251A !important;
    font-weight: 650 !important;
}
.participant-select-menu .q-item--active,
.participant-select-menu .q-item.q-manual-focusable--focused {
    background: rgba(47,123,88,.10) !important;
    color: #2F7B58 !important;
}
.participant-shell {
    width: 100%;
    padding: 18px 20px 108px;
    gap: 16px;
}
.participant-title {
    color: var(--ink);
    font-size: 27px;
    line-height: 1.18;
    font-weight: 950;
}
.participant-subtitle {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
    font-weight: 650;
}
.participant-form {
    width: 100%;
    gap: 12px;
}
.participant-form .q-field,
.participant-form .q-select {
    width: 100%;
}
.participant-submit {
    width: 100%;
    height: 52px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 850;
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    box-shadow: 0 16px 30px rgba(47,123,88,.20);
}
.participant-bg .q-btn.participant-submit,
.participant-bg .q-btn.bg-primary.participant-submit {
    background: #2F7B58 !important;
    background-color: #2F7B58 !important;
    background-image: none !important;
    color: #FFFFFF !important;
}
</style>
'''


STUDY_PHASES = ['未填写', 'pilot', 'study2', 'study3']
DIAGNOSIS_GROUPS = [
    'jf',
    '自定义',
]
GENDERS = ['女', '男', '其他/未填写']
EDUCATION_BANDS = ['小学及以下', '初中', '高中/中专', '大专', '本科', '研究生及以上', '未填写']


def _safe_next_path(path: str) -> str:
    path = str(path or '').strip()
    if not path.startswith('/') or path.startswith('//'):
        return '/camera'
    return path


def _validate_birth_date(value: str) -> str:
    text = str(value or '').strip()
    if not text:
        return ''
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError('出生日期格式需要为 YYYY-MM-DD') from exc


def create_participant_info_page():
    @ui.page('/participant-info')
    async def participant_info_page(next_path: str = '/camera'):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(PARTICIPANT_INFO_CSS)

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        user_id = user.get('id')
        existing = get_hci_participant_by_user_id(user_id) or {}
        candidate_code = existing.get('participant_code') or user.get('participant_id')
        default_code = normalize_hci_participant_code(candidate_code)
        if not default_code.isdigit():
            try:
                default_code = f'{int(user_id):04d}'
            except Exception:
                default_code = '0000'
        default_name = existing.get('registered_name') or user.get('display_name') or ''
        existing_diagnosis = str(existing.get('diagnosis_group') or '').strip()
        existing_diagnosis_is_custom = bool(
            existing_diagnosis
            and existing_diagnosis not in DIAGNOSIS_GROUPS
            and existing_diagnosis != '其他/未填写'
        )
        initial_diagnosis = (
            '自定义'
            if existing_diagnosis_is_custom
            else (existing_diagnosis if existing_diagnosis in DIAGNOSIS_GROUPS else 'jf')
        )
        initial_custom_diagnosis = existing_diagnosis if existing_diagnosis_is_custom else ''

        async def save_profile():
            selected_diagnosis = diagnosis_group.value
            if selected_diagnosis == '自定义':
                selected_diagnosis = str(custom_diagnosis.value or '').strip()
                if not selected_diagnosis:
                    ui.notify('请填写自定义诊断大类', type='warning')
                    return
            try:
                participant = upsert_hci_participant(
                    user_id=user_id,
                    participant_code=participant_code.value,
                    registered_name=registered_name.value,
                    site_id=site_id.value,
                    study_phase=study_phase.value,
                    diagnosis_group=selected_diagnosis,
                    birth_date=_validate_birth_date(birth_date.value),
                    gender=gender.value,
                    education_band=education_band.value,
                )
            except Exception as exc:
                ui.notify(str(exc), type='negative')
                return

            app.storage.user['hci_participant'] = participant
            try:
                from app.services.feishu_sync import sync_due_jobs_once
                asyncio.create_task(sync_due_jobs_once(limit=5))
            except Exception:
                pass
            ui.notify('已保存研究信息', type='positive')
            smooth_navigate(_safe_next_path(next_path))

        with ui.column().classes('mobile-page light-page participant-bg').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style('color:#2F7B58')
                ui.label('研究信息').style(
                    'font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126'
                )

            with ui.column().classes('participant-shell'):
                ui.html('<div class="participant-title">参与者信息</div>', sanitize=False)
                ui.html(
                    '<div class="participant-subtitle">由研究人员确认基础资料；ID 由系统按顺序生成。</div>',
                    sanitize=False,
                )

                with ui.column().classes('participant-form'):
                    participant_code = ui.input(
                        'ID',
                        value=default_code,
                    ).props('outlined dense readonly')
                    registered_name = ui.input(
                        '姓名 / 登记名',
                        value=default_name,
                    ).props('outlined dense readonly')
                    site_id = ui.input(
                        '中心/社区编号',
                        value=existing.get('site_id', ''),
                    ).props('outlined dense')
                    study_phase = ui.select(
                        STUDY_PHASES,
                        label='研究阶段',
                        value=existing.get('study_phase') or '未填写',
                    ).props('outlined dense popup-content-class=participant-select-menu')
                    diagnosis_group = ui.select(
                        DIAGNOSIS_GROUPS,
                        label='诊断大类',
                        value=initial_diagnosis,
                    ).props('outlined dense popup-content-class=participant-select-menu')
                    custom_diagnosis = ui.input(
                        '自定义诊断大类',
                        value=initial_custom_diagnosis,
                    ).props('outlined dense')
                    custom_diagnosis.bind_visibility_from(
                        diagnosis_group,
                        'value',
                        backward=lambda value: value == '自定义',
                    )
                    birth_date = ui.input(
                        '出生日期',
                        value=existing.get('birth_date', ''),
                    ).props('outlined dense type=date')
                    gender = ui.select(
                        GENDERS,
                        label='性别',
                        value=existing.get('gender') or '其他/未填写',
                    ).props('outlined dense popup-content-class=participant-select-menu')
                    education_band = ui.select(
                        EDUCATION_BANDS,
                        label='教育层级',
                        value=existing.get('education_band') or '未填写',
                    ).props('outlined dense popup-content-class=participant-select-menu')

                ui.button('保存并继续', on_click=save_profile, color=None).classes('participant-submit').props('unelevated')
