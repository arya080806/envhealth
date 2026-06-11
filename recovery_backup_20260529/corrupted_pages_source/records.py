"""Records page."""
import json
import re
import time
from pathlib import Path

from nicegui import app, ui

from app.components.nav import bottom_nav, smooth_navigate
from app.db import delete_session
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


MODE_LABELS = {
    'slider': '鍙傛暟璋冭妭',
    'drag': '鑷敱鍒涗綔',
    'ai': '鏅鸿兘鎺ㄨ崘',
    'inspire': '鐏垫劅鍒涙兂',
    'chat': '瀵硅瘽鏀归€?,
}

SCENE_LABELS = {
    'park': '鍏洯/鑷劧',
    'urban': '鍩庡競琛楀尯',
}

RECOMMEND_LABELS = {
    'nature': '鑷劧鐤楁剤',
    'urban': '閮藉競娲诲姏',
    'zen': '绂呮剰瀹侀潤',
}

MODE_COLORS = {
    'slider': '#2F7B58',
    'ai': '#5F8E6E',
    'chat': '#A87C32',
    'inspire': '#7D5AA6',
    'drag': '#3B8874',
}

RECORDS_CSS = '''
<style>
.records-list {
    padding: 18px 14px 104px;
    gap: 12px;
    width: 100%;
}
.records-count {
    color: rgba(23,49,38,.62);
    font-size: 12px;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(47,123,88,.08);
}
.rec-card {
    position: relative;
    width: 100%;
    display: grid;
    grid-template-columns: 124px minmax(0, 1fr);
    gap: 12px;
    padding: 11px;
    min-height: 132px;
    border-radius: 26px !important;
    border: 1px solid rgba(38,70,52,.12) !important;
    background: linear-gradient(180deg, rgba(255,255,248,.84), rgba(246,250,241,.72)) !important;
    box-shadow: 0 16px 34px rgba(38,70,52,.08) !important;
    backdrop-filter: blur(18px) !important;
    cursor: pointer;
    overflow: hidden;
}
.rec-card:active {
    transform: scale(.988);
}
.rec-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 12px;
    bottom: 12px;
    width: 3px;
    border-radius: 999px;
    background: var(--mode-color, #B7F27E);
}
.rec-thumb {
    width: 124px;
    height: 110px;
    align-self: center;
    border-radius: 20px;
    overflow: hidden;
    background: rgba(47,123,88,.08);
    position: relative;
}
.rec-thumb > div {
    width: 100% !important;
    height: 100% !important;
}
.rec-thumb img {
    display: block;
    width: 100% !important;
    height: 100% !important;
    min-width: 100%;
    min-height: 100%;
    object-fit: cover !important;
    object-position: center !important;
}
.rec-body {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.rec-topline {
    display: flex;
    gap: 7px;
    align-items: center;
    min-width: 0;
    flex-wrap: wrap;
}
.rec-title {
    color: #173126;
    font-size: 15px;
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.rec-time {
    margin-left: 0;
    color: rgba(23,49,38,.56);
    font-size: 12px;
    white-space: nowrap;
}
.rec-meta {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}
.rec-pill {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    color: rgba(23,49,38,.64);
    background: rgba(47,123,88,.08);
}
.rec-pill.accent {
    color: var(--mode-color, #B7F27E);
    background: color-mix(in srgb, var(--mode-color, #B7F27E) 16%, transparent);
}
.rec-summary {
    color: rgba(23,49,38,.62);
    font-size: 12px;
    line-height: 1.55;
    min-height: 19px;
}
.rec-actions {
    margin-top: auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.rec-delete {
    opacity: .70;
}
.rec-delete .q-icon {
    color: rgba(23,49,38,.52) !important;
}
.rec-empty {
    flex: 1;
    min-height: 64vh;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 24px 22px 110px;
}
.rec-empty-panel {
    width: 100%;
    border: 1px solid rgba(38,70,52,.12);
    border-radius: 28px;
    padding: 28px 22px;
    background: linear-gradient(180deg, rgba(255,255,248,.84), rgba(246,250,241,.72));
    backdrop-filter: blur(18px);
}
@media (max-width: 370px) {
    .rec-card {
        grid-template-columns: 96px minmax(0, 1fr);
    }
    .rec-thumb {
        width: 96px;
        height: 102px;
    }
    .rec-time {
        display: none;
    }
}
</style>
'''


def create_records_page():
    @ui.page('/records')
    def records_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(RECORDS_CSS)

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        from app.db import get_user_sessions

        sessions = get_user_sessions(user['id'])
        records = [s for s in sessions if s.get('generated_image_path') or s.get('canvas_json_path')]

        with ui.column().classes('mobile-page light-page').style('min-height:100vh'):
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.label('鎴戠殑璁板綍').style(
                    f'font-size:18px; font-weight:800; margin-left:8px; color:{COLORS["primary_dark"]}'
                )
                ui.element('div').style('flex:1')
                if records:
                    ui.label(f'{len(records)} 鏉?).classes('records-count')

            if not records:
                with ui.column().classes('rec-empty animate-in'):
                    with ui.element('div').classes('rec-empty-panel'):
                        ui.label('鏆傛棤璁板綍').style(
                            f'font-size:20px; color:{COLORS["primary_dark"]}; font-weight:800;'
                        )
                        ui.label('瀹屾垚涓€娆＄幆澧冩敼閫犲悗锛屼綘鐨勮褰曚細淇濆瓨鍦ㄨ繖閲屻€?).style(
                            f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.7; margin-top:8px;'
                        )
                        ui.button('寮€濮嬩綋楠?, on_click=lambda: smooth_navigate('/camera')).props(
                            'no-caps unelevated'
                        ).style(LIGHT_PRIMARY_BTN_STYLE + 'margin-top:22px;')
            else:
                with ui.column().classes('records-list'):
                    for idx, s in enumerate(records):
                        _render_record_card(s, idx)

            bottom_nav('璁板綍', light=True)


def _render_record_card(s: dict, idx: int):
    sid = s['id']
    mode = s.get('mode_used', '')
    mode_label = MODE_LABELS.get(mode, mode or '鏈煡妯″紡')
    scene_label = SCENE_LABELS.get(s.get('scene_type', ''), '')
    created_at = s.get('created_at', 0)
    time_str = time.strftime('%m-%d %H:%M', time.localtime(created_at)) if created_at else ''
    surveyed = bool(s.get('survey_completed_at'))
    is_draft = not s.get('generated_image_path')

    img_path = s.get('generated_image_path') or s.get('canvas_snapshot_path') or s.get('uploaded_image_path', '')
    img_fname = Path(img_path).name if img_path else ''
    img_url = f'/api/image/{img_fname}' if img_fname else ''

    bar_color = MODE_COLORS.get(mode, COLORS['primary'])
    click_url = f'/inspire-mode?sid={sid}&back=records' if is_draft else f'/result?sid={sid}&back=records'
    delay_ms = min(idx * 45, 220)
    status_text = '鍒涗綔涓? if is_draft else ('宸茶瘎浼? if surveyed else '寰呰瘎浼?)

    with ui.element('div').classes('rec-card').style(
        f'--mode-color:{bar_color}; animation: fadeInUp .34s ease both; animation-delay:{delay_ms}ms;'
        'border-radius:24px !important;'
    ).on('click', lambda _url=click_url: smooth_navigate(_url)):
        with ui.element('div').classes('rec-thumb'):
            if img_url:
                with ui.element('div').style('width:100% !important;height:100% !important;'):
                    ui.image(img_url).style(
                        'display:block;width:100% !important;height:100% !important;'
                        'object-fit:cover !important;object-position:center !important;'
                    )
            else:
                ui.html('<div style="width:100%;height:100%;display:grid;place-items:center;color:rgba(23,49,38,.42);font-size:12px;">鏃犻瑙?/div>')

        with ui.element('div').classes('rec-body'):
            with ui.element('div').classes('rec-topline'):
                ui.html(f'<div class="rec-title">{mode_label}</div>')
                if time_str:
                    ui.html(f'<div class="rec-time">{time_str}</div>')

            with ui.element('div').classes('rec-meta'):
                if scene_label:
                    ui.html(f'<span class="rec-pill">{scene_label}</span>')
                ui.html(f'<span class="rec-pill accent">{status_text}</span>')

            ui.html(f'<div class="rec-summary">{_summary_text(s, mode)}</div>')

            with ui.element('div').classes('rec-actions'):
                ui.html('<span class="rec-pill">鏌ョ湅璇︽儏</span>')
                with ui.row().style('gap:2px; align-items:center;'):
                    del_btn = ui.button(icon='delete_outline').props('flat round dense').classes('rec-delete')
                    ui.icon('chevron_right').style('font-size:20px; color:rgba(23,49,38,.32);')

        with ui.dialog() as confirm_dialog, ui.card().style(
            'min-width:260px; border-radius:22px; padding:20px 20px 12px; border:none;'
        ):
            ui.label('纭鍒犻櫎').style(
                f'font-size:16px; font-weight:800; color:{COLORS["text"]}; margin-bottom:6px;'
            )
            ui.label('鍒犻櫎鍚庢棤娉曟仮澶嶏紝纭畾瑕佸垹闄よ繖鏉¤褰曞悧锛?).style(
                f'font-size:13px; color:{COLORS["text_secondary"]}; line-height:1.6;'
            )
            with ui.row().style('width:100%; gap:8px; margin-top:16px;'):
                ui.button('鍙栨秷', on_click=confirm_dialog.close).props('flat no-caps').style(
                    f'flex:1; color:{COLORS["text_secondary"]};'
                )

                def _do_delete(_sid=sid, _dlg=confirm_dialog):
                    delete_session(_sid)
                    _dlg.close()
                    smooth_navigate('/records')

                ui.button('鍒犻櫎', on_click=_do_delete).props('no-caps unelevated').style(
                    f'flex:1; background:{COLORS["error"]}; color:white;'
                )

        del_btn.on(
            'click',
            lambda _dlg=confirm_dialog: _dlg.open(),
            js_handler='(e) => { e.stopPropagation(); emit(e); }',
        )


def _summary_text(s: dict, mode: str) -> str:
    if mode in ('drag', 'inspire'):
        return _element_summary_text(s)
    if mode == 'chat':
        return _chat_summary_text(s)
    if mode in ('slider', 'ai'):
        return _parameter_summary_text(s, mode)
    return '鐜鏀归€犺褰?


def _parameter_summary_text(s: dict, mode: str) -> str:
    vals = [
        ('缁垮寲', s.get('green_level', 50)),
        ('浜洪€?, s.get('urban_level', 50)),
        ('娲诲姏', s.get('vitality_level', 50)),
        ('鍏夌嚎', s.get('light_warmth', 50)),
    ]
    prefix = ''
    if mode == 'ai':
        recommend = RECOMMEND_LABELS.get(s.get('selected_recommend', ''), '')
        prefix = f'{recommend} 路 ' if recommend else ''
    return prefix + ' / '.join(f'{label} {int(val or 0)}' for label, val in vals)


def _chat_summary_text(s: dict) -> str:
    raw_moods = s.get('chat_moods', '[]')
    try:
        moods = json.loads(raw_moods) if isinstance(raw_moods, str) else (raw_moods or [])
    except Exception:
        moods = []
    extra = (s.get('chat_extra', '') or '').strip()
    parts = moods[:2]
    if extra:
        parts.append(extra[:22] + ('...' if len(extra) > 22 else ''))
    return ' 路 '.join(parts) if parts else '瀵硅瘽鏀归€?


def _element_summary_text(s: dict) -> str:
    elements = s.get('placed_elements', [])
    if isinstance(elements, str):
        try:
            elements = json.loads(elements)
        except Exception:
            elements = []
    if not elements:
        return '淇濆瓨鐨勫垱浣滆崏绋?

    names = []
    seen = set()
    for el in elements:
        name = str(el.get('name') or '').strip()
        if not name:
            continue
        # Keep textual element names, drop emoji-only artifacts.
        if not re.search(r'[\u4e00-\u9fffA-Za-z0-9]', name):
            continue
        if name not in seen:
            seen.add(name)
            names.append(name)

    if names:
        shown = '銆?.join(names[:3])
        suffix = f' 绛?{len(names)} 椤? if len(names) > 3 else ''
        return f'宸叉斁缃細{shown}{suffix}'
    return f'宸叉斁缃?{len(elements)} 涓厓绱?
