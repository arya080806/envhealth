"""缁撴灉瀵规瘮椤甸潰 - 瀹屾暣鍒涗綔鏁版嵁灞曠ず锛堝惈鐢诲竷蹇収 / 妯″紡鍙傛暟澶嶅師锛?""
import json
import time
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE
from app.state import get_session
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate

MODE_LABELS = {
    'slider': '鍙傛暟璋冭妭', 'drag': '鑷敱鍒涗綔', 'ai': '鏅鸿兘鎺ㄨ崘',
    'inspire': '鐏垫劅鍒涙兂', 'chat': '瀵硅瘽鏀归€?,
}
MODE_ICONS = {
    'slider': '馃帤锔?, 'drag': '鉁?, 'ai': '馃', 'inspire': '馃帹', 'chat': '馃挰',
}
MODE_COLORS = {
    'slider': '#52B788', 'ai': '#4EA8DE', 'chat': '#E9C46A',
    'inspire': '#B47FE3', 'drag': '#64CCC5',
}
SCENE_LABELS = {'park': '鍏洯/鑷劧', 'urban': '鍩庡競琛楀尯'}
RECOMMEND_LABELS = {'nature': '鑷劧鐤楁剤', 'urban': '閮藉競娲诲姏', 'zen': '绂呮剰瀹侀潤'}
RECOMMEND_SCHEMES = {
    'nature': {'icon': '馃尶', 'title': '鑷劧鍜岃皭鏂规',
               'desc': '涓瓑缁垮寲 + 浣庝汉閫犲厓绱狅紝妯℃嫙鑷劧鍏洯鐜锛屾渶澶у寲娉ㄦ剰鍔涙仮澶嶆晥鏋?,
               'green': 55, 'urban': 25, 'vitality': 40},
    'urban':  {'icon': '馃彊锔?, 'title': '娲诲姏閮藉競鏂规',
               'desc': '涓瓑缁垮寲 + 涓瓑浜洪€犲厓绱?+ 閫傚害娲诲姏锛岄€傚悎鍩庡競琛楀尯鏀归€?,
               'green': 45, 'urban': 50, 'vitality': 55},
    'zen':    {'icon': '馃', 'title': '瀹侀潤绂呮剰鏂规',
               'desc': '楂樼豢鍖?+ 浣庝汉閫犲厓绱?+ 浣庢椿鍔涳紝鍒涢€犳矇娴稿紡瀹侀潤绌洪棿',
               'green': 70, 'urban': 15, 'vitality': 20},
}
MOOD_DISPLAY = {
    '骞抽潤鏀炬澗': ('馃寠', 'rgba(82,183,136,0.12)'),
    '鍏呮弧娲诲姏': ('鉁?, 'rgba(233,196,106,0.15)'),
    '娌绘剤娓╂殩': ('鈽€锔?, 'rgba(212,163,115,0.15)'),
    '娓呴啋涓撴敞': ('馃尶', 'rgba(45,106,79,0.10)'),
    '娴极璇楁剰': ('馃尭', 'rgba(212,163,115,0.12)'),
    '绁炵鎺㈢储': ('馃尗锔?, 'rgba(27,67,50,0.10)'),
    '鑷劧閲庤叮': ('馃尦', 'rgba(64,145,108,0.12)'),
    '娆箰杞荤泩': ('猸?, 'rgba(149,213,178,0.15)'),
}

_RESULT_EXTRA_CSS = '''<style>
.detail-section {
  width: 100%; padding: 16px 18px; border-radius: 18px;
  background: rgba(255,255,255,0.82);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(45,106,79,0.06);
  box-shadow: 0 2px 12px rgba(27,67,50,0.05);
}
.detail-section-title {
  font-size: 13px; font-weight: 600; letter-spacing: 0.3px;
  margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
}
.mood-card-ro {
  display: flex; flex-direction: column; gap: 4px;
  padding: 14px 16px; border-radius: 16px;
  border: 2px solid transparent; flex: 1; min-width: calc(50% - 6px);
}
.mood-card-ro.selected {
  border-color: #2D6A4F !important;
  box-shadow: 0 0 0 3px rgba(45,106,79,0.1);
}
.mood-card-ro .mood-icon { font-size: 22px; }
.mood-card-ro .mood-name { font-size: 13px; font-weight: 600; color: #1A1A2E; }
.mood-card-ro .mood-hint { font-size: 10px; color: #6B7280; font-weight: 300; line-height: 1.4; }
.slider-bar-ro {
  width: 100%; padding: 14px 16px; border-radius: 16px;
  background: white; border: 1px solid rgba(45,106,79,0.06);
}
.slider-track {
  width: 100%; height: 6px; border-radius: 3px;
  background: rgba(45,106,79,0.08); position: relative; margin: 8px 0 4px;
}
.slider-fill {
  height: 100%; border-radius: 3px;
  background: linear-gradient(90deg, #2D6A4F, #52B788);
}
.slider-thumb {
  width: 16px; height: 16px; border-radius: 50%;
  background: #2D6A4F; border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  position: absolute; top: 50%; transform: translate(-50%, -50%);
}
.scheme-card-ro {
  padding: 16px 18px; border-radius: 18px; border: 2px solid #2D6A4F;
  background: rgba(45,106,79,0.03);
}
.canvas-snapshot { width: 100%; border-radius: 16px; box-shadow: 0 4px 16px rgba(27,67,50,0.1); }
.compare-wrap {
  position: relative; width: 100%; overflow: hidden;
  border-radius: 20px; box-shadow: 0 8px 32px rgba(27,67,50,0.14);
  background: #e8f0ea; user-select: none; -webkit-user-select: none; cursor: col-resize;
}
.compare-wrap img { display: block; width: 100%; height: auto; object-fit: cover; pointer-events: none; }
.compare-before-clip { position: absolute; top: 0; left: 0; height: 100%; width: 50%; overflow: hidden; }
.compare-before-clip img { width: auto; min-width: 100%; max-width: none; position: absolute; top: 0; left: 0; }
.compare-divider {
  position: absolute; top: 0; left: 50%; height: 100%; width: 2px;
  background: white; box-shadow: 0 0 8px rgba(0,0,0,0.3);
  transform: translateX(-50%); pointer-events: none; z-index: 10;
}
.compare-handle {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 40px; height: 40px; border-radius: 50%; background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25); display: flex; align-items: center; justify-content: center;
}
.compare-label {
  position: absolute; top: 12px; padding: 4px 12px; border-radius: 20px;
  font-size: 12px; font-weight: 600; color: white; backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px); pointer-events: none; z-index: 11;
}
.compare-label-before { left: 12px; background: rgba(27,67,50,0.65); }
.compare-label-after { right: 12px; background: linear-gradient(135deg, rgba(45,106,79,0.8), rgba(82,183,136,0.8)); }
.compare-range { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: col-resize; z-index: 20; margin: 0; -webkit-appearance: none; }
.compare-hint { text-align: center; font-size: 11px; color: #6B7280; margin-top: 6px; font-weight: 300; }
.extra-text-box {
  padding: 12px 16px; border-radius: 14px;
  background: rgba(45,106,79,0.03); border: 1px dashed rgba(45,106,79,0.15);
  font-size: 13px; color: #374151; line-height: 1.6; font-style: italic;
}
</style>'''



def create_result_page():
    @ui.page('/result')
    def result_page(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(_RESULT_EXTRA_CSS)
        session = get_session(sid) if sid else None

        ui.add_head_html('''<script>
function cmpUpdate(v){var p=v+'%';var c=document.getElementById('cmp-before-clip');
var d=document.getElementById('cmp-divider');var i=document.getElementById('cmp-before-img');
var w=document.getElementById('cmp-wrap');if(c)c.style.width=p;if(d)d.style.left=p;
if(i&&w)i.style.width=w.offsetWidth+'px';}
function cmpBind(){var s=document.querySelector('.compare-range');if(!s||s._b)return;
s._b=1;s.addEventListener('input',function(){cmpUpdate(this.value);});
s.addEventListener('touchmove',function(){cmpUpdate(this.value);});cmpUpdate(s.value);}
window.addEventListener('load',cmpBind);
new MutationObserver(function(){cmpBind();}).observe(document.body,{childList:true,subtree:true});
</script>''')

        mode = (getattr(session, 'mode_used', '') or '') if session else ''

        with ui.column().classes('mobile-page light-page'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(
                    '/records' if back == 'records' else f'/mode-select?sid={sid}'
                )).props('flat round dense').style(f'color:{COLORS["primary_dark"]}')
                ui.label('鏀归€犺鎯? if back == 'records' else '鏀归€犵粨鏋?).style(
                    f'font-size:17px;font-weight:600;margin-left:4px;color:{COLORS["primary_dark"]}'
                )

            with ui.column().style('padding:20px;gap:14px;width:100%;padding-bottom:100px;'):

                # 鈹€鈹€ 妯″紡 & 鍦烘櫙淇℃伅鏍?鈹€鈹€
                if session:
                    _render_info_bar(session)

                # 鈹€鈹€ 鍓嶅悗瀵规瘮 鈹€鈹€
                _render_compare(session)

                # 鈹佲攣 鍒涗綔鐜板満澶嶅師锛堟寜妯″紡锛?鈹佲攣
                if session:
                    # 鐢诲竷蹇収锛坕nspire / drag锛?                    snapshot_path = getattr(session, 'canvas_snapshot_path', '') or ''
                    if snapshot_path and Path(snapshot_path).exists():
                        title = '馃枌锔?鍒涗綔鐢诲竷' if mode == 'inspire' else '馃幆 鍏冪礌甯冨眬'
                        with ui.element('div').classes('detail-section animate-in animate-in-delay-2'):
                            ui.html(f'<div class="detail-section-title" style="color:{COLORS["primary_dark"]};">{title}</div>')
                            snap_url = f'/api/image/{Path(snapshot_path).name}'
                            ui.image(snap_url).classes('canvas-snapshot')

                    # slider / ai 妯″紡锛氬鍘熸粦鏉?                    if mode in ('slider', 'ai'):
                        _render_slider_detail(session, mode)

                    # ai 妯″紡锛氬鍘熸帹鑽愭柟妗堝崱鐗?                    if mode == 'ai':
                        _render_recommend_card(session)

                    # chat 妯″紡锛氬鍘熸儏缁€夋嫨 + 鎻忚堪
                    if mode == 'chat':
                        _render_chat_detail(session)

                    # 鐜鍙傛暟锛堜粎闈為粯璁ゅ€兼椂鏄剧ず锛屾垨 slider/ai 妯″紡璺宠繃鍥犱负涓婇潰宸叉湁锛?                    if mode not in ('slider', 'ai'):
                        green = session.green_level or 50
                        urban = session.urban_level or 50
                        vitality = session.vitality_level or 50
                        light = session.light_warmth or 50
                        if any(abs(v - 50) > 0.5 for v in [green, urban, vitality, light]):
                            _render_param_cards(session)

                # 鈹€鈹€ 鎿嶄綔鎸夐挳 鈹€鈹€
                with ui.row().classes('animate-in animate-in-delay-4').style('width:100%;gap:12px;margin-top:8px'):
                    if mode in ('drag', 'inspire'):
                        edit_url = f'/drag-mode?sid={sid}&back=result' if mode == 'drag' else f'/inspire-mode?sid={sid}&back=result'
                        edit_label = '缁х画鍒涗綔 鉁? if mode == 'drag' else '缁х画缁樺埗 鉁?
                        ui.button(edit_label, on_click=lambda u=edit_url: smooth_navigate(u)).props(
                            'no-caps unelevated'
                        ).style(LIGHT_PRIMARY_BTN_STYLE + 'flex:1;')
                    ui.button('閲嶆柊璋冩暣', on_click=lambda: smooth_navigate(f'/mode-select?sid={sid}')).props(
                        'outline no-caps'
                    ).style(
                        'flex:1;border-radius:28px;color:#2F7B58;'
                        'border:1.5px solid rgba(47,123,88,0.28);padding:14px;font-weight:650;'
                        'background:rgba(255,255,248,0.62);'
                    )
                with ui.row().classes('animate-in animate-in-delay-4').style('width:100%;gap:12px'):
                    ui.button('杩涘叆璇勪及 鈫?, on_click=lambda: smooth_navigate(f'/survey?sid={sid}')).props(
                        'no-caps unelevated'
                    ).style(LIGHT_PRIMARY_BTN_STYLE)

                if session and session.generated_image_path:
                    gen_fname = Path(session.generated_image_path).name
                    ui.link('涓嬭浇缁撴灉鍥剧墖', f'/api/image/{gen_fname}', new_tab=True).style(
                        f'display:block;text-align:center;padding:14px;'
                        'border:1.5px solid rgba(47,123,88,0.24);border-radius:28px;'
                        'color:#2F7B58;text-decoration:none;font-size:14px;font-weight:650;'
                        'background:rgba(255,255,248,0.58);'
                    )


# 鈹€鈹€ 瀛愭覆鏌撳嚱鏁?鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def _render_info_bar(session):
    mode = getattr(session, 'mode_used', '') or ''
    scene = getattr(session, 'scene_type', '') or ''
    mc = MODE_COLORS.get(mode, COLORS['primary'])
    ts = getattr(session, 'created_at', 0) or 0
    gc = getattr(session, 'generation_count', 0) or 0
    with ui.element('div').classes('detail-section animate-in'):
        with ui.row().style('width:100%;align-items:center;gap:8px;flex-wrap:wrap;'):
            ui.html(
                f'<span style="display:inline-flex;align-items:center;gap:5px;'
                f'padding:5px 14px;border-radius:20px;font-size:13px;font-weight:600;'
                f'background:{mc}15;color:{mc};">'
                f'{MODE_ICONS.get(mode,"")} {MODE_LABELS.get(mode,mode or "鏈煡")}</span>'
            )
            sl = SCENE_LABELS.get(scene, '')
            if sl:
                ui.html(
                    f'<span style="display:inline-flex;align-items:center;gap:4px;padding:5px 12px;'
                    f'border-radius:20px;font-size:12px;font-weight:500;'
                    f'background:{COLORS["primary"]}08;color:{COLORS["primary_dark"]};">馃搷 {sl}</span>'
                )
            ui.element('div').style('flex:1')
            if ts:
                ui.label(time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))).style(
                    f'font-size:11px;color:{COLORS["text_secondary"]};font-weight:300;'
                )
        if gc > 1:
            ui.label(f'鍏辩敓鎴?{gc} 娆?).style(f'font-size:11px;color:{COLORS["text_secondary"]};margin-top:4px;font-weight:300;')


def _render_compare(session):
    with ui.row().classes('animate-in').style('align-items:center;gap:8px'):
        ui.label('鏀归€犲墠 vs 鏀归€犲悗').style(f'font-size:16px;font-weight:600;color:{COLORS["primary_dark"]};letter-spacing:0.5px')
    ui.element('div').classes('section-divider')
    orig_url = f'/api/image/{Path(session.uploaded_image_path).name}' if session and session.uploaded_image_path else ''
    gen_url = f'/api/image/{Path(session.generated_image_path).name}' if session and session.generated_image_path else ''
    if gen_url:
        ui.html(f'''
<div class="compare-wrap animate-in" id="cmp-wrap">
  <img src="{gen_url}" alt="鏀归€犲悗" id="cmp-after">
  <div class="compare-before-clip" id="cmp-before-clip">
    <img src="{orig_url}" alt="鏀归€犲墠" id="cmp-before-img" style="width:100%;position:static;">
  </div>
  <div class="compare-divider" id="cmp-divider"><div class="compare-handle">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M7 4L3 10L7 16" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M13 4L17 10L13 16" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg></div></div>
  <div class="compare-label compare-label-before">鏀归€犲墠</div>
  <div class="compare-label compare-label-after">鏀归€犲悗</div>
  <input type="range" min="0" max="100" value="50" class="compare-range">
</div><p class="compare-hint">鈫?鎷栧姩婊戝潡鏌ョ湅鍓嶅悗瀵规瘮 鈫?/p>''').classes('animate-in animate-in-delay-1').style('width:100%')
    elif orig_url:
        with ui.element('div').classes('animate-in animate-in-delay-1').style(
            'width:100%;position:relative;border-radius:20px;overflow:hidden;box-shadow:0 4px 20px rgba(27,67,50,0.08);'
        ):
            ui.image(orig_url).style('width:100%;border-radius:20px;object-fit:cover;')


def _render_slider_detail(session, mode):
    """澶嶅師婊戞潌鍙傛暟甯冨眬"""
    green = session.green_level or 50
    urban = session.urban_level or 50
    vitality = session.vitality_level or 50
    light = session.light_warmth or 50
    configs = [
        ('馃尶', '缁垮寲绋嬪害', green, '浣?, '楂?),
        ('馃彈锔?, '浜洪€犲厓绱?, urban, '浣?, '楂?),
        ('馃懃', '鐜娲诲姏', vitality, '瀹侀潤', '鐑椆'),
        ('鈽€锔?, '鍏夌嚎姘涘洿', light, '鍐疯壊', '鏆栬壊'),
    ]
    with ui.element('div').classes('detail-section animate-in animate-in-delay-2'):
        ui.html(f'<div class="detail-section-title" style="color:{COLORS["primary_dark"]};">馃帤锔?璋冭妭鍙傛暟</div>')
        with ui.column().style('gap:10px;width:100%'):
            for icon, label, val, lo, hi in configs:
                with ui.element('div').classes('slider-bar-ro'):
                    with ui.row().style('justify-content:space-between;align-items:center'):
                        ui.html(f'<span style="font-size:13px;font-weight:600;color:{COLORS["primary_dark"]}">{icon} {label}</span>')
                        ui.html(f'<span style="font-size:14px;font-weight:700;color:#2F7B58">{int(val)}%</span>')
                    ui.html(
                        f'<div class="slider-track">'
                        f'<div class="slider-fill" style="width:{int(val)}%"></div>'
                        f'<div class="slider-thumb" style="left:{int(val)}%"></div>'
                        f'</div>'
                    )
                    with ui.row().style('justify-content:space-between'):
                        ui.label(lo).style(f'font-size:10px;color:{COLORS["text_secondary"]}')
                        ui.label(hi).style(f'font-size:10px;color:{COLORS["text_secondary"]}')


def _render_recommend_card(session):
    """澶嶅師 AI 鎺ㄨ崘鏂规鍗＄墖"""
    rec_id = getattr(session, 'selected_recommend', '') or ''
    scheme = RECOMMEND_SCHEMES.get(rec_id)
    if not scheme:
        return
    with ui.element('div').classes('detail-section animate-in animate-in-delay-2'):
        ui.html(f'<div class="detail-section-title" style="color:{COLORS["primary_dark"]};">馃 閫夋嫨鐨勬柟妗?/div>')
        with ui.element('div').classes('scheme-card-ro'):
            with ui.row().style('align-items:center;gap:8px;margin-bottom:6px'):
                ui.html(f'<span style="font-size:22px">{scheme["icon"]}</span>')
                ui.label(scheme['title']).style(f'font-size:15px;font-weight:700;color:{COLORS["primary_dark"]}')
            ui.label(scheme['desc']).style(f'font-size:12px;color:{COLORS["text_secondary"]};line-height:1.5;margin-bottom:8px')
            with ui.row().style('gap:8px;flex-wrap:wrap'):
                for lbl, val in [('缁垮寲', scheme['green']), ('浜洪€?, scheme['urban']), ('娲诲姏', scheme['vitality'])]:
                    ui.html(
                        f'<span style="padding:4px 12px;border-radius:20px;font-size:12px;font-weight:500;'
                        f'background:rgba(47,123,88,0.09);color:#2F7B58">{lbl} {val}%</span>'
                    )


def _render_chat_detail(session):
    """澶嶅師瀵硅瘽妯″紡鐨勬儏缁€夋嫨鍗＄墖 + 鎻忚堪鏂囧瓧"""
    raw = getattr(session, 'chat_moods', '[]') or '[]'
    moods = json.loads(raw) if isinstance(raw, str) else (raw or [])
    extra = getattr(session, 'chat_extra', '') or ''
    if not moods and not extra:
        return
    with ui.element('div').classes('detail-section animate-in animate-in-delay-2'):
        ui.html(f'<div class="detail-section-title" style="color:{COLORS["primary_dark"]};">馃挰 閫夋嫨鐨勬劅鍙?/div>')
        if moods:
            with ui.row().style('gap:8px;flex-wrap:wrap;width:100%'):
                for mood_name in moods:
                    icon, bg = MOOD_DISPLAY.get(mood_name, ('馃挱', 'rgba(107,114,128,0.08)'))
                    ui.html(
                        f'<div class="mood-card-ro selected" style="background:{bg};">'
                        f'<span class="mood-icon">{icon}</span>'
                        f'<span class="mood-name">鉁?{mood_name}</span>'
                        f'</div>'
                    )
        if extra:
            ui.html(f'<div style="margin-top:10px;font-size:12px;color:{COLORS["text_secondary"]};font-weight:500;">琛ュ厖鎻忚堪</div>')
            ui.html(f'<div class="extra-text-box">"{extra}"</div>')



def _render_param_cards(session):
    green = session.green_level or 50
    urban = session.urban_level or 50
    vitality = session.vitality_level or 50
    light = session.light_warmth or 50
    cfgs = [
        ('馃尶', '缁垮寲', green, COLORS['primary']),
        ('馃彈锔?, '浜洪€?, urban, COLORS['secondary']),
        ('馃懃', '娲诲姏', vitality, COLORS['accent']),
        ('鈽€锔?, '鍏夌嚎', light, COLORS['accent_light']),
    ]
    with ui.element('div').classes('detail-section animate-in animate-in-delay-2'):
        ui.html(f'<div class="detail-section-title" style="color:{COLORS["primary_dark"]};">馃帤锔?鐜鍙傛暟</div>')
        with ui.row().style('width:100%;gap:8px;flex-wrap:wrap'):
            for ik, lb, val, cl in cfgs:
                with ui.card().style(
                    'flex:1;min-width:calc(50% - 6px);padding:12px 10px;text-align:center;'
                    'border:none !important;border-radius:14px;background:rgba(45,106,79,0.03);box-shadow:none !important;'
                ):
                    with ui.row().style('justify-content:center;align-items:center;gap:4px'):
                        svg = get_svg(ik, 14)
                        if svg:
                            ui.html(svg).style('width:14px;height:14px;')
                        ui.label(lb).style(f'font-size:11px;color:{COLORS["text_secondary"]};font-weight:400')
                    ui.label(f'{int(val)}%').style(f'font-size:20px;font-weight:700;color:{cl};margin:2px 0')
                    with ui.element('div').classes('progress-bar').style('height:6px'):
                        ui.element('div').classes('progress-bar-fill').style(f'width:{int(val)}%;background:linear-gradient(90deg,{cl},{cl}88);')

