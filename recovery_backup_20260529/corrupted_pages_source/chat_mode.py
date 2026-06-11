"""瀵硅瘽鏀归€犳ā寮忛〉闈?- 鎯呯华寮曞寮忕┖闂存敼閫?""
import json
import asyncio
import base64
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT
from app.state import get_session, save_output
from app.components.icons import (
    get_svg, icon_stream, icon_sparkle, icon_sun, icon_vine,
    icon_petals, icon_fog, icon_bush, icon_star,
)
from app.components.nav import bottom_nav, smooth_navigate

# 鎯呯华寮曞鍗＄墖瀹氫箟锛?icon_fn, 鏍囩鍚? 寮曞璇? tint_start, tint_end)
_MOOD_DEFS = [
    (icon_stream,   '骞抽潤鏀炬澗', '鍍忔箹闈㈠€掑奖鑸殑瀹侀潤',      'rgba(82,183,136,0.12)',  'rgba(149,213,178,0.18)'),
    (icon_sparkle,  '鍏呮弧娲诲姏', '鎯虫劅鍙楁竻鏅ㄧ┖姘旈噷鐨勭敓鍛藉姏', 'rgba(233,196,106,0.15)', 'rgba(233,196,106,0.08)'),
    (icon_sun,      '娌绘剤娓╂殩', '鍍忛槼鍏夌┛杩囨爲鍙剁殑閭ｇ娓╂煍', 'rgba(212,163,115,0.15)', 'rgba(233,196,106,0.10)'),
    (icon_vine,     '娓呴啋涓撴敞', '绌烘皵娓呴€忥紝鎬濈华涔熻窡鐫€骞插噣', 'rgba(45,106,79,0.10)',   'rgba(82,183,136,0.14)'),
    (icon_petals,   '娴极璇楁剰', '鏈変簺鏈﹁儳锛屾湁浜涜交鏌旂殑缇?,   'rgba(212,163,115,0.12)', 'rgba(149,213,178,0.10)'),
    (icon_fog,      '绁炵鎺㈢储', '鍏夊奖鏂戦┏锛岃棌鐫€璁稿鍙兘',   'rgba(27,67,50,0.10)',    'rgba(45,106,79,0.06)'),
    (icon_bush,     '鑷劧閲庤叮', '涓嶄慨杈瑰箙鐨勮嚜鐒舵湰鏉ョ殑鏍峰瓙', 'rgba(64,145,108,0.12)',  'rgba(82,183,136,0.10)'),
    (icon_star,     '娆箰杞荤泩', '杞绘澗鎰夊揩锛屼笉甯︿换浣曡礋鎷?,   'rgba(149,213,178,0.15)', 'rgba(212,163,115,0.10)'),
]

def _svg_data_url(fn) -> str:
    svg = fn(48)
    b64 = base64.b64encode(svg.encode()).decode()
    return f'data:image/svg+xml;base64,{b64}'

MOOD_CARDS = [
    (_svg_data_url(fn), label, desc, ts, te)
    for fn, label, desc, ts, te in _MOOD_DEFS
]

_CHAT_CSS = '''<style>
/* 鈹€鈹€ 瀵硅瘽鏀归€犳ā寮忎笓灞炴牱寮?鈹€鈹€ */
.chat-mode-bg {
  background: #F7F9F1 !important;
  min-height: 100vh;
}
.chat-preview {
  width: 100%;
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 12px 28px rgba(27,67,50,0.11);
  flex-shrink: 0;
}
.chat-preview img {
  width: 100% !important;
  height: 118px !important;
  object-fit: cover !important;
  display: block !important;
}
.chat-intro {
  padding: 2px 2px 0;
}

/* 鎯呯华鍗＄墖缃戞牸 */
.mood-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  width: 100%;
}

.mood-card {
  border-radius: 18px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(.34,1.56,.64,1);
  border: 1px solid rgba(255,255,255,0.5);
  position: relative;
  overflow: hidden;
  min-height: 62px;
  display: flex;
  user-select: none;
  -webkit-user-select: none;
  background: rgba(255,255,248,0.68);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 2px 12px rgba(27,67,50,0.06);
}
.mood-card-tint {
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: 16px;
}
.mood-card .mood-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  width: 100%;
}
.mood-card.selected {
  border-color: rgba(45,106,79,0.45);
  box-shadow: 0 4px 18px rgba(45,106,79,0.14);
  transform: scale(1.03);
}
.mood-card.selected::after {
  content: '鉁?;
  position: absolute;
  top: 7px;
  right: 9px;
  font-size: 11px;
  font-weight: 700;
  color: #2D6A4F;
  z-index: 2;
}
.mood-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
  pointer-events: none;
}
.mood-title {
  font-size: 13px;
  font-weight: 850;
  color: #1A1A2E;
  margin-bottom: 2px;
}
.mood-desc {
  font-size: 10.5px;
  color: #6B7280;
  line-height: 1.3;
  font-weight: 300;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 鎻愮ず鏍囪 */
.chat-hero-label {
  font-size: 22px;
  font-weight: 900;
  color: #1A1A2E;
  letter-spacing: 0;
  line-height: 1.28;
}
.chat-sub-label {
  font-size: 13px;
  color: rgba(23,49,38,.58);
  font-weight: 400;
  line-height: 1.65;
  margin-top: 7px;
}

/* 杈撳叆妗?*/
.chat-compose-card {
  width: 100%;
  border-radius: 22px;
  padding: 14px;
  border: 1px solid rgba(47,123,88,.16);
  background: linear-gradient(180deg, rgba(255,255,248,.90), rgba(244,250,240,.78));
  box-shadow: 0 12px 28px rgba(38,70,52,.08);
}
.compose-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #173126;
  font-size: 13px;
  font-weight: 900;
  margin-bottom: 9px;
}
.compose-label span {
  color: rgba(23,49,38,.46);
  font-size: 10.5px;
  font-weight: 700;
}
.mood-textarea {
  width: 100%;
  min-height: 96px;
  border: 1.5px solid rgba(47,123,88,0.22);
  border-radius: 18px;
  padding: 13px 14px;
  font-size: 14px;
  font-family: inherit;
  color: #1A1A2E;
  background: rgba(255,255,248,0.86);
  backdrop-filter: blur(8px);
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  line-height: 1.6;
}
.mood-textarea:focus {
  border-color: rgba(45,106,79,0.45);
  box-shadow: 0 0 0 3px rgba(45,106,79,0.07);
}
.mood-textarea::placeholder {
  color: rgba(23,49,38,.40);
  font-weight: 400;
}

/* 宸查€夋爣绛捐 */
.selected-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 28px;
}
.tag-chip {
  background: rgba(47,123,88,.12);
  color: #2F7B58;
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 800;
}

/* 鎻愮ず琛?*/
.mood-hint {
  font-size: 11px;
  color: #9CA3AF;
  text-align: center;
  margin-top: -4px;
}
</style>'''


def create_chat_mode_page():
    @ui.page('/chat-mode')
    def chat_mode_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(_CHAT_CSS)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'chat'

        # 椤甸潰鐘舵€?        state = {
            'selected_moods': [],   # 宸查€夋儏缁爣绛惧垪琛紙鏈€澶?涓級
            'extra_text': '',
        }

        # 鈹€鈹€ 椤甸潰甯冨眬 鈹€鈹€
        with ui.column().classes('mobile-page light-page chat-mode-bg').style('gap:0'):
            bottom_nav(light=True)
            # 椤堕儴瀵艰埅
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(
                    icon='arrow_back',
                    on_click=lambda: smooth_navigate(f'/mode-select?sid={sid}'),
                ).props('flat round dense').style(f'color:{COLORS["primary_dark"]}')
                ui.label('瀵硅瘽鏀归€?).style(
                    f'font-size:17px;font-weight:600;margin-left:4px;flex:1;color:{COLORS["primary_dark"]}'
                )

            # 鍙粴鍔ㄤ富浣?            with ui.column().style('flex:1;overflow-y:auto;padding:16px 20px 18px;gap:14px;width:100%;'):

                # 鍘熷浘棰勮
                if session and session.uploaded_image_path:
                    fname = Path(session.uploaded_image_path).name
                    with ui.element('div').classes('chat-preview'):
                        ui.image(f'/api/image/{fname}').style(
                            'width:100%;height:118px;object-fit:cover;display:block;'
                        )

                # 寮曞鏍囪
                with ui.column().classes('chat-intro').style('gap:2px;'):
                    ui.html(
                        '<div class="chat-hero-label">浣犲笇鏈涜繖閲屽甫缁欎綘浠€涔堟劅鍙楋紵</div>'
                        '<div class="chat-sub-label">涓嶅繀鎻忚堪鍏蜂綋鐨勭敾闈紝鍙鍑哄績閲屾兂瑕佺殑閭ｇ鎰熻</div>',
                        sanitize=False,
                    )

                # 涓昏杈撳叆妗?                with ui.element('section').classes('chat-compose-card'):
                    ui.html(
                        '<div class="compose-label">杈撳叆浣犵殑鎰熷彈 <span>绯荤粺浼氫紭鍏堢悊瑙ｈ繖娈垫枃瀛?/span></div>'
                        '<textarea id="mood-extra-text" class="mood-textarea" rows="4" '
                        'placeholder="渚嬪锛氭垜甯屾湜杩欓噷瀹夐潤涓€鐐癸紝鏈夋竻閫忕殑绌烘皵銆佹煍鍜岀殑鍏夛紝涓嶈澶嫢鎸ゃ€? '
                        'oninput="ChatMode.onTextInput(this.value)"></textarea>',
                        sanitize=False,
                    )

                # 鎯呯华鍗＄墖鍖?                with ui.column().style('gap:8px;width:100%;'):
                    with ui.row().style('align-items:center;justify-content:space-between;'):
                        ui.label('涔熷彲浠ラ€夋嫨鎯呯华鏍囩').style(
                            f'font-size:14px;font-weight:600;color:{COLORS["primary_dark"]};'
                        )
                        hint_label = ui.label('鏈€澶氶€?2 涓?).style(
                            'font-size:11px;color:#9CA3AF;'
                        )

                    # 鍗＄墖缃戞牸锛堢函 HTML + onclick锛岄伩鍏?NiceGUI 浜嬩欢缁戝畾闂锛?                    cards_html = '<div class="mood-grid" id="mood-grid">'
                    for data_url, label, desc, tint_start, tint_end in MOOD_CARDS:
                        cards_html += (
                            f'<div class="mood-card" '
                            f'data-mood="{label}" '
                            f'onclick="ChatMode.toggleMood(this,\'{label}\')">'
                            f'<div class="mood-card-tint" style="background:linear-gradient(135deg,{tint_start},{tint_end});"></div>'
                            f'<div class="mood-inner">'
                            f'<img src="{data_url}" class="mood-icon" alt="{label}">'
                            f'<div class="mood-title">{label}</div>'
                            f'<div class="mood-desc">{desc}</div>'
                            f'</div></div>'
                        )
                    cards_html += '</div>'
                    cards_html += '<div class="selected-tags-row" id="selected-tags-row"></div>'
                    ui.html(cards_html, sanitize=False)

            # 鈹€鈹€ 搴曢儴鎿嶄綔鍖?鈹€鈹€
            with ui.column().style(
                'gap:8px;'
            ).classes('light-action-panel'):
                error_label = ui.label().style('display:none;')

                loading_row = ui.element('div').style('display:none;width:100%;')
                with loading_row:
                    with ui.row().style('width:100%;align-items:center;gap:10px;padding:8px 0'):
                        ui.spinner('dots', size='sm', color=COLORS['primary'])
                        ui.label('AI 姝ｅ湪鐞嗚В浣犵殑鎰熷彈鈥?).style(
                            f'font-size:14px;color:{COLORS["primary_dark"]};font-weight:500'
                        )

                gen_btn = ui.button(
                    '鉁?鐢熸垚鎴戠殑绌洪棿',
                    on_click=lambda: generate(),
                ).props('no-caps unelevated').style(LIGHT_PRIMARY_BTN_STYLE)

                ui.label('璇疯嚦灏戦€夋嫨涓€绉嶆劅鍙?).style(
                    'font-size:11px;color:#9CA3AF;text-align:center;'
                ).bind_visibility_from(gen_btn, 'visible')

        # 鈹€鈹€ JavaScript 鐘舵€佺鐞?鈹€鈹€
        ui.add_head_html(f'''<script>
(function() {{
  var _moods = [];
  var _extraText = '';
  var _sid = {json.dumps(sid)};
  var MAX_MOODS = 2;

  window.ChatMode = {{
    toggleMood: function(el, mood) {{
      var idx = _moods.indexOf(mood);
      if (idx >= 0) {{
        _moods.splice(idx, 1);
        el.classList.remove('selected');
      }} else {{
        if (_moods.length >= MAX_MOODS) {{
          // 鍙栨秷鏈€鏃╅€夌殑
          var oldest = _moods.shift();
          var oldEl = document.querySelector('.mood-card[data-mood="' + oldest + '"]');
          if (oldEl) oldEl.classList.remove('selected');
        }}
        _moods.push(mood);
        el.classList.add('selected');
      }}
      window.ChatMode.syncState();
    }},

    onTextInput: function(val) {{
      _extraText = val;
      window.ChatMode.syncState();
    }},

    syncState: function() {{
      // 鏇存柊宸查€夋爣绛惧睍绀?      var row = document.getElementById('selected-tags-row');
      if (row) {{
        if (_moods.length === 0) {{
          row.innerHTML = '<span style="font-size:12px;color:#9CA3AF;font-weight:300;">鐐瑰嚮鍗＄墖閫夋嫨鎰熷彈鈥?/span>';
        }} else {{
          row.innerHTML = _moods.map(function(m) {{
            return '<span class="tag-chip">' + m + '</span>';
          }}).join('');
        }}
      }}
      // 鏆撮湶缁?Python 绔鍙?      window._chatMoodState = {{moods: _moods.slice(), extra: _extraText}};
    }},

    getState: function() {{
      return JSON.stringify(window._chatMoodState || {{moods:[], extra:''}});
    }},
  }};

  // 鍒濆鍖栫┖鎻愮ず
  window.ChatMode.syncState();
}})();
</script>''')

        # 鈹€鈹€ 鐢熸垚閫昏緫 鈹€鈹€
        async def generate():
            raw = await ui.run_javascript('ChatMode.getState()', timeout=5.0)
            try:
                data = json.loads(raw) if raw else {}
            except Exception:
                data = {}

            moods = data.get('moods', [])
            extra = data.get('extra', '')

            if not moods:
                error_label.set_text('璇疯嚦灏戦€夋嫨涓€绉嶆劅鍙?)
                error_label.style(
                    f'display:block;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%;'
                )
                return

            if not session or not session.uploaded_image_path:
                error_label.set_text('璇峰厛涓婁紶鍥剧墖')
                error_label.style(
                    f'display:block;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%;'
                )
                return

            error_label.style('display:none;')
            gen_btn.set_visibility(False)
            loading_row.style('display:block;')

            try:
                import json as _json
                session.chat_moods = _json.dumps(moods, ensure_ascii=False)
                session.chat_extra = extra
                from app.services.chat_service import generate_from_chat
                result_bytes, used_prompt = await asyncio.to_thread(
                    generate_from_chat,
                    session.uploaded_image_path, moods, extra,
                )
                session.llm_prompt = used_prompt
                save_output(sid, result_bytes)
                smooth_navigate(f'/result?sid={sid}')
            except Exception as e:
                error_label.set_text(f'鐢熸垚澶辫触: {str(e)[:80]}')
                error_label.style(
                    f'display:block;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%;'
                )
                gen_btn.set_visibility(True)
                loading_row.style('display:none;')
