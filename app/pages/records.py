"""记录页面：点击记录直接回到对应继续创作页面。"""
from __future__ import annotations

import time
import json
from html import escape

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.db import delete_session, get_user_sessions, update_session
from app.state import media_url, resolve_media_path
from app.theme import COMMON_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


RECORDS_CSS = '''
<style>
.records-bg {
    --record-ink: #10251A;
    --record-muted: rgba(16,37,26,.62);
    --record-faint: rgba(16,37,26,.40);
    --record-green: #2F7B58;
    background:
        radial-gradient(circle at 50% 4%, rgba(183,242,126,.16), transparent 30%),
        linear-gradient(180deg, rgba(255,255,248,.88), rgba(243,248,238,.96) 52%, rgba(232,240,227,.98)),
        url('/static/images/light-bamboo-paper.webp') center/cover no-repeat,
        #F6F8EF !important;
}
.records-bg::before {
    background:
        linear-gradient(180deg, rgba(47,123,88,.055), transparent 26%),
        linear-gradient(90deg, rgba(47,123,88,.05) 1px, transparent 1px),
        linear-gradient(180deg, rgba(47,123,88,.04) 1px, transparent 1px) !important;
    background-size: auto, 34px 34px, 34px 34px !important;
    opacity: .46 !important;
}
.records-shell {
    width: 100%;
    padding: 16px 16px 108px;
    gap: 12px;
}
.records-list {
    display: grid;
    gap: 14px;
    width: 100%;
}
.record-card-btn {
    width: 100%;
    border: 1px solid rgba(47,123,88,.13);
    border-radius: 24px;
    padding: 12px 10px 12px 12px;
    background:
        linear-gradient(90deg, rgba(47,123,88,.08), transparent 38%),
        linear-gradient(180deg, rgba(255,255,248,.91), rgba(247,250,242,.75));
    box-shadow: 0 14px 30px rgba(38,70,52,.075);
    display: grid;
    grid-template-columns: 170px minmax(0, 1fr) 30px;
    gap: 12px;
    align-items: stretch;
    text-align: left;
    cursor: pointer;
    min-height: 144px;
    overflow: hidden;
    transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.record-card-btn:active {
    transform: scale(.992);
}
.record-card-btn:hover {
    border-color: rgba(47,123,88,.24);
    box-shadow: 0 18px 34px rgba(38,70,52,.10);
}
.record-thumb {
    position: relative;
    display: block;
    width: 170px;
    height: 120px;
    align-self: center;
    border-radius: 20px 14px 14px 20px;
    overflow: hidden;
    background: linear-gradient(145deg, rgba(47,123,88,.10), rgba(255,255,248,.78));
    border: 1px solid rgba(47,123,88,.10);
    box-shadow: inset 0 0 0 1px rgba(255,255,248,.40), 0 12px 26px rgba(38,70,52,.12);
}
.record-thumb::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(90deg, transparent 62%, rgba(255,255,248,.18));
    pointer-events: none;
}
.record-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}
.record-thumb-empty {
    width: 100%;
    height: 100%;
    display: grid;
    place-items: center;
    color: var(--record-green);
    font-size: 20px;
    font-weight: 950;
}
.record-ready-pill,
.record-status-pill {
    position: absolute;
    left: 9px;
    top: 9px;
    z-index: 2;
    border-radius: 999px;
    padding: 4px 8px;
    color: #F8FAF2;
    background: #1DB954;
    border: 1px solid rgba(255,255,248,.62);
    font-size: 10px;
    line-height: 1;
    font-weight: 950;
    box-shadow: 0 8px 18px rgba(16,37,26,.18);
}
.record-status-pill {
    background: rgba(47,123,88,.84);
}
.record-main {
    min-width: 0;
    display: grid;
    grid-template-rows: 30px 18px 22px 20px;
    align-content: center;
    gap: 7px;
}
.record-row {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    align-items: center;
    gap: 8px;
    min-width: 0;
}
.record-mode {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 28px;
    padding: 0 10px;
    border-radius: 999px;
    color: var(--record-green);
    background: rgba(47,123,88,.10);
    border: 1px solid rgba(47,123,88,.13);
    font-size: 11px;
    font-weight: 900;
    line-height: 1;
    white-space: nowrap;
}
.record-title-edit {
    min-width: 0 !important;
    max-width: 100%;
    width: 100%;
    height: 30px !important;
    min-height: 30px !important;
    padding: 0 4px !important;
    color: var(--record-ink);
    background: transparent !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    text-decoration: none;
    justify-content: flex-start !important;
    margin: 0 !important;
}
.record-title-edit.untitled {
    color: rgba(47,123,88,.72) !important;
}
.record-title-edit .q-btn__content {
    display: block;
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: left;
    line-height: 30px;
}
.record-date {
    color: var(--record-faint);
    font-size: 12px;
    font-weight: 750;
    line-height: 18px;
}
.record-status {
    color: var(--record-muted);
    font-size: 14px;
    font-weight: 800;
    line-height: 22px;
}
.record-status.running {
    color: #2F7B58;
}
.record-status.error {
    color: #C94F4F;
}
.record-status.ready {
    color: #1F8F4D;
}
.record-hint {
    color: rgba(47,123,88,.74);
    font-size: 13px;
    font-weight: 850;
    line-height: 20px;
}
.record-chevron {
    color: var(--record-green);
    font-size: 24px;
    font-weight: 900;
    line-height: 1;
}
.record-card-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    min-height: 120px;
}
.record-delete {
    width: 30px !important;
    height: 30px !important;
    min-width: 30px !important;
    min-height: 30px !important;
    color: rgba(16,37,26,.50) !important;
}
.record-delete:hover {
    color: #C94F4F !important;
    background: rgba(201,79,79,.08) !important;
}
.record-confirm-card {
    width: min(300px, calc(100vw - 56px));
    border-radius: 22px;
    padding: 20px 18px 14px;
    border: 1px solid rgba(47,123,88,.12);
    background: rgba(255,255,248,.98);
}
.record-confirm-title {
    color: var(--record-ink);
    font-size: 16px;
    font-weight: 900;
}
.record-confirm-copy {
    margin-top: 8px;
    color: var(--record-muted);
    font-size: 13px;
    line-height: 1.6;
    font-weight: 650;
}
.record-confirm-actions {
    width: 100%;
    display: flex;
    gap: 8px;
    margin-top: 18px;
}
.record-confirm-actions .q-btn {
    flex: 1;
}
.record-name-input {
    margin-top: 12px;
    width: 100%;
}
.records-empty {
    width: 100%;
    padding: 28px 18px;
    border-radius: 24px;
    text-align: center;
    color: var(--record-muted);
    background: rgba(255,255,248,.70);
    border: 1px solid rgba(47,123,88,.12);
    font-size: 13px;
    line-height: 1.6;
    font-weight: 650;
}
.records-ready-banner {
    width: 100%;
    padding: 14px 16px;
    border-radius: 20px;
    background: rgba(29,185,84,.10);
    border: 1px solid rgba(29,185,84,.22);
    color: #173126;
    box-shadow: 0 14px 28px rgba(38,70,52,.08);
}
.records-ready-title {
    font-size: 14px;
    line-height: 1.35;
    font-weight: 950;
    color: #1F8F4D;
}
.records-ready-copy {
    margin-top: 4px;
    font-size: 12px;
    line-height: 1.5;
    color: rgba(23,49,38,.68);
    font-weight: 750;
}
@media (max-width: 360px) {
    .records-shell { padding-left: 12px; padding-right: 12px; }
    .record-card-btn { grid-template-columns: 132px minmax(0,1fr) 28px; padding: 10px; gap: 9px; min-height: 124px; }
    .record-thumb { width: 132px; height: 104px; border-radius: 18px 12px 12px 18px; }
    .record-main { grid-template-rows: 28px 16px 20px 18px; gap: 5px; }
    .record-mode { font-size: 10px; min-height: 26px; padding: 0 8px; }
    .record-title-edit { font-size: 13px !important; }
    .record-card-actions { min-height: 104px; gap: 14px; }
}
</style>
'''


MODE_LABELS = {
    'drag': '自由创作',
    'inspire': '灵感创想',
    'chat': '对话改造',
    'slider': '智能参数',
    'ai': '智能参数',
}

MODE_ROUTES = {
    'drag': '/drag-mode',
    'inspire': '/inspire-mode',
    'chat': '/chat-mode',
    'slider': '/slider-mode',
    'ai': '/slider-mode',
}


def _record_target(session: dict) -> str:
    mode = _record_mode(session)
    if resolve_media_path(session.get('generated_image_path') or ''):
        return f'/result?sid={session["id"]}&back=records'
    route = MODE_ROUTES.get(mode, '/mode-select')
    return f'{route}?sid={session["id"]}&back=records'


def _record_image(session: dict) -> str:
    for field in ('generated_image_path', 'canvas_snapshot_path', 'uploaded_image_path'):
        url = media_url(session.get(field) or '', thumb=True)
        if url:
            return url
    return ''


def _is_saved_record(session: dict) -> bool:
    saved_fields = ('generated_image_path', 'canvas_snapshot_path', 'canvas_json_path')
    if any(resolve_media_path(session.get(field) or '') for field in saved_fields):
        return True
    if session.get('generation_status') in ('queued', 'running', 'error', 'done'):
        return bool(resolve_media_path(session.get('uploaded_image_path') or ''))
    return False


def _format_time(value) -> str:
    try:
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(float(value)))
    except (TypeError, ValueError, OSError):
        return ''


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _record_title(session: dict) -> str:
    return (session.get('record_title') or '').strip()


def _is_generation_ready(session: dict) -> bool:
    try:
        finished_at = float(session.get('generation_finished_at') or 0)
        seen_at = float(session.get('generation_seen_at') or 0)
    except (TypeError, ValueError):
        return False
    return (
        session.get('generation_status') == 'done'
        and finished_at > seen_at
        and bool(resolve_media_path(session.get('generated_image_path') or ''))
    )


def _record_status_text(session: dict) -> tuple[str, str]:
    status = session.get('generation_status') or ''
    if status in ('queued', 'running'):
        return 'AI 正在后台生成中', 'running'
    if status == 'error':
        error_text = str(session.get('generation_error') or '')
        if 'timed out' in error_text.lower() or '超时' in error_text:
            return '上次生成超时，可继续编辑', 'error'
        return '生成失败，可继续编辑', 'error'
    if _is_generation_ready(session):
        return 'AI 已生成完成', 'ready'
    generations = _safe_int(session.get('generation_count') or 0)
    return f'已生成 {generations} 次', ''


def _record_hint(session: dict) -> str:
    if session.get('generation_status') in ('queued', 'running'):
        return '可离开页面，完成后会提示'
    if session.get('generation_status') == 'error':
        error_text = str(session.get('generation_error') or '')
        if 'timed out' in error_text.lower() or '超时' in error_text:
            return '图像服务响应超时，点击继续调整后可重试'
        return '点击卡片继续调整后再生成'
    if resolve_media_path(session.get('generated_image_path') or ''):
        return '点击查看上次生成结果'
    return '点击卡片继续创作'


def _has_nonempty_json(value) -> bool:
    if isinstance(value, (list, dict)):
        return bool(value)
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = json.loads(value)
    except Exception:
        return bool(value.strip() and value.strip() not in ('[]', '{}'))
    return bool(parsed)


def _record_mode(session: dict) -> str:
    """Infer the saved creation mode instead of trusting page-visit side effects."""
    sketch_data = session.get('sketch_data')
    placed_elements = session.get('placed_elements')
    mode = session.get('mode_used') or ''
    if _has_nonempty_json(sketch_data):
        return 'inspire'
    if mode not in ('inspire', 'chat', 'slider', 'ai') and _has_nonempty_json(placed_elements):
        return 'drag'
    if mode in ('slider', 'ai') and not session.get('generated_image_path'):
        if _has_nonempty_json(placed_elements):
            return 'drag'
        if session.get('canvas_snapshot_path') or session.get('canvas_json_path'):
            return 'inspire'
    return mode


def _load_sessions() -> list[dict]:
    user = app.storage.user.get('user', {}) or {}
    user_id = user.get('id')
    if user_id:
        return get_user_sessions(user_id)
    return []


def create_records_page():
    @ui.page('/records')
    async def records_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(RECORDS_CSS)

        if not (app.storage.user.get('user', {}) or {}).get('id'):
            smooth_navigate('/login')
            return

        sessions = [
            session for session in _load_sessions()
            if _is_saved_record(session)
        ]
        ready_sessions = [session for session in sessions if _is_generation_ready(session)]

        with ui.column().classes('mobile-page light-page records-bg').style('gap:0'):
            bottom_nav('草稿箱', light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/camera')).props('flat round dense').style(
                    'color:#2F7B58'
                )
                ui.label('草稿箱').style('font-size:17px;font-weight:850;margin-left:4px;flex:1;color:#173126')

            with ui.column().classes('records-shell'):
                if not sessions:
                    ui.html('<div class="records-empty">暂无草稿。点击保存后，创作会出现在这里。</div>', sanitize=False)
                    return

                if ready_sessions:
                    ready_names = '、'.join(
                        escape(_record_title(item) or MODE_LABELS.get(_record_mode(item), '未命名草稿'))
                        for item in ready_sessions[:3]
                    )
                    more = f' 等 {len(ready_sessions)} 条' if len(ready_sessions) > 3 else ''
                    ui.html(
                        '<div class="records-ready-banner">'
                        '<div class="records-ready-title">AI 生成好了</div>'
                        f'<div class="records-ready-copy">{ready_names}{more} 已生成完成，点击对应卡片查看结果。</div>'
                        '</div>',
                        sanitize=False,
                    )

                with ui.column().classes('records-list'):
                    for session in sessions:
                        sid = session['id']
                        mode_label = escape(MODE_LABELS.get(_record_mode(session), '选择模式'))
                        title = _record_title(session)
                        title_label = title or '点击命名'
                        created = escape(_format_time(session.get('created_at')))
                        generations = _safe_int(session.get('generation_count') or 0)
                        image_url = _record_image(session)
                        target = _record_target(session)
                        status_text, status_class = _record_status_text(session)
                        hint_text = _record_hint(session)
                        ready = _is_generation_ready(session)
                        running = (session.get('generation_status') or '') in ('queued', 'running')

                        with ui.element('div').classes('record-card-btn').on('click', lambda p=target: smooth_navigate(p)):
                            if image_url:
                                pill = '<span class="record-ready-pill">已完成</span>' if ready else (
                                    '<span class="record-status-pill">生成中</span>' if running else ''
                                )
                                ui.html(f'<span class="record-thumb">{pill}<img src="{image_url}" alt="record thumbnail"></span>', sanitize=False)
                            else:
                                ui.html('<span class="record-thumb"><span class="record-thumb-empty">AI</span></span>', sanitize=False)

                            with ui.element('span').classes('record-main'):
                                with ui.element('span').classes('record-row'):
                                    ui.html(f'<span class="record-mode">{mode_label}</span>', sanitize=False)
                                    title_btn = ui.button(title_label).props('flat dense no-caps').classes(
                                        'record-title-edit' + ('' if title else ' untitled')
                                    )
                                ui.html(f'<span class="record-date">{created}</span>', sanitize=False)
                                ui.html(f'<span class="record-status {status_class}">{escape(status_text)}</span>', sanitize=False)
                                ui.html(f'<span class="record-hint">{escape(hint_text)}</span>', sanitize=False)

                            with ui.element('span').classes('record-card-actions'):
                                delete_btn = ui.button(icon='delete_outline').props('flat round dense').classes('record-delete')
                                ui.html('<span class="record-chevron">›</span>', sanitize=False)

                        with ui.dialog() as rename_dialog, ui.card().classes('record-confirm-card'):
                            ui.html('<div class="record-confirm-title">命名草稿</div>', sanitize=False)
                            name_input = ui.input(
                                placeholder='输入草稿名称',
                                value=title,
                            ).props('outlined dense maxlength=24').classes('record-name-input')

                            with ui.row().classes('record-confirm-actions'):
                                ui.button('取消', on_click=rename_dialog.close).props('flat no-caps').style(
                                    'color:rgba(16,37,26,.62);font-weight:800;'
                                )

                                def _do_rename(record_id=sid, input_ref=name_input, dialog=rename_dialog):
                                    update_session(record_id, record_title=(input_ref.value or '').strip()[:24])
                                    dialog.close()
                                    smooth_navigate('/records')

                                ui.button('保存', on_click=_do_rename).props('unelevated no-caps').style(
                                    'background:#2F7B58;color:white;font-weight:900;'
                                )

                        with ui.dialog() as confirm_dialog, ui.card().classes('record-confirm-card'):
                            ui.html('<div class="record-confirm-title">确认删除</div>', sanitize=False)
                            ui.html(
                                '<div class="record-confirm-copy">删除后无法恢复，确定要删除这条创作记录吗？</div>',
                                sanitize=False,
                            )

                            with ui.row().classes('record-confirm-actions'):
                                ui.button('取消', on_click=confirm_dialog.close).props('flat no-caps').style(
                                    'color:rgba(16,37,26,.62);font-weight:800;'
                                )

                                def _do_delete(record_id=sid, dialog=confirm_dialog):
                                    delete_session(record_id)
                                    dialog.close()
                                    smooth_navigate('/records')

                                ui.button('删除', on_click=_do_delete).props('unelevated no-caps').style(
                                    'background:#C94F4F;color:white;font-weight:900;'
                                )

                        delete_btn.on(
                            'click',
                            lambda dialog=confirm_dialog: dialog.open(),
                            js_handler='(e) => { e.stopPropagation(); emit(e); }',
                        )
                        title_btn.on(
                            'click',
                            lambda dialog=rename_dialog: dialog.open(),
                            js_handler='(e) => { e.stopPropagation(); emit(e); }',
                        )

                if ready_sessions:
                    ui.add_body_html('''
<script>
setTimeout(function () {
    fetch('/api/generation/notifications/seen', { method: 'POST' })
        .then(function () {
            if (window.HealingDraftNotifier) window.HealingDraftNotifier.poll();
        })
        .catch(function () {});
}, 900);
</script>
''')
