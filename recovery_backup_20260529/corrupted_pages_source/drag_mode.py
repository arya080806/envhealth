"""鑷敱鍒涗綔妯″紡椤甸潰 鈥?Fabric.js 鐢诲竷缂栬緫鍣?""
import asyncio
import base64
import json
from pathlib import Path

from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT
from app.state import get_session, save_output
from app.components.icons import get_svg, icon_tree, icon_bench, icon_pond, icon_sun, icon_cabin
from app.components.nav import bottom_nav, smooth_navigate

# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 鍏冪礌鍒嗙被鏁版嵁
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
CATEGORIES = [
    ('妞嶈', '馃尦', icon_tree, [
        ('馃尦', '澶ф爲'), ('馃尣', '鏉炬爲'), ('馃尶', '鐏屾湪'),
        ('馃帇', '绔规灄'), ('馃尯', '鑺辨湹'), ('馃崁', '鑽夊潽'), ('馃尡', '瀚╄娊'),
        ('馃尨', '妫曟'), ('馃尭tree', '妯辫姳鏍?), ('馃尵', '鑺﹁媷'),
        ('馃尩', '浠欎汉鎺?), ('馃moss', '鑻旇棑'),
    ]),
    ('璁炬柦', '馃獞', icon_bench, [
        ('馃獞', '闀挎'), ('馃敠', '璺伅'), ('鉀?, '鍠锋硥'),
        ('馃椏', '闆曞'), ('馃洡锔?, '灏忓緞'), ('馃毀', '鍥存爮'),
        ('馃獊', '绉嬪崈'), ('鉀╋笍', '鍑変涵'), ('馃', '鏈ㄦ爤閬?),
        ('馃帯', '椋庤溅'), ('馃棏锔?, '鍨冨溇妗?),
    ]),
    ('姘存櫙', '馃寠', icon_pond, [
        ('馃寠', '灏忔邯'), ('馃彏锔?, '姹犲'), ('馃挧', '姘撮潰'),
        ('馃挦', '鐎戝竷'), ('馃lotus', '鑽疯姳'), ('馃尶water', '姘磋崏'), ('馃', '绀佺煶'),
    ]),
    ('姘涘洿', '鈽€锔?, icon_sun, [
        ('鈽€锔?, '闃冲厜'), ('馃尗锔?, '钖勯浘'), ('馃崅', '钀藉彾'),
        ('馃尭', '鑺辩摚'), ('馃', '椋為笩'),
        ('馃寛', '褰╄櫣'), ('鉁╞ug', '钀ょ伀铏?), ('馃', '铦磋澏'), ('馃寵', '鏈堝厜'),
    ]),
    ('寤虹瓚', '馃彔', icon_cabin, [
        ('馃彔', '鏈ㄥ眿'), ('馃П', '鐭冲'), ('馃寜', '鎷辨ˉ'), ('馃尰', '鑺卞渻'),
    ]),
]

# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 妯″潡鍔犺浇鏃堕鐢熸垚 SVG 鏁版嵁 URL锛堝彧鎵ц涓€娆★級
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _svg_b64(fn, size=80) -> str:
    svg = fn(size)
    return base64.b64encode(svg.encode()).decode()

def _build_elements_data() -> tuple:
    items = []
    for cat_name, cat_icon, _tab_fn, elems in CATEGORIES:
        for icon, name in elems:
            svg = get_svg(icon, 80)
            b64 = base64.b64encode(svg.encode()).decode() if svg else ''
            items.append({
                'idx': len(items),
                'cat': cat_name,
                'catIcon': cat_icon,
                'icon': icon,
                'name': name,
                'dataUrl': f'data:image/svg+xml;base64,{b64}' if b64 else '',
            })
    return items, json.dumps(items, ensure_ascii=False)


_ALL_ELEMENTS, _ELEMENTS_JS = _build_elements_data()


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 鏋勫缓鍏冪礌閫夋嫨闈㈡澘 HTML锛坥nclick 鐩磋皟 JS锛屾棤鏈嶅姟鍣ㄥ線杩旓級
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _build_picker_html() -> str:
    cats: dict = {}
    for el in _ALL_ELEMENTS:
        cats.setdefault(el['cat'], []).append(el)

    # 鍒嗙被鍚?鈫?tab icon SVG data URL 鏄犲皠
    cat_tab_icons = {
        cat_name: f'data:image/svg+xml;base64,{_svg_b64(tab_fn, 32)}'
        for cat_name, _cat_emoji, tab_fn, _elems in CATEGORIES
    }

    tabs = ''
    for i, (cat_name, items) in enumerate(cats.items()):
        active = 'cat-tab-active' if i == 0 else ''
        img_url = cat_tab_icons.get(cat_name, '')
        tabs += (
            f'<button class="cat-tab {active}" '
            f'data-catidx="{i}">'
            f'{cat_name}</button>'
        )

    grids = ''
    for i, (cat_name, items) in enumerate(cats.items()):
        display = 'grid' if i == 0 else 'none'
        cards = ''
        for el in items:
            idx = el['idx']
            img_tag = (
                f'<img src="{el["dataUrl"]}" alt="{el["name"]}" '
                f'style="width:40px;height:40px;object-fit:contain;pointer-events:none;">'
                if el['dataUrl'] else
                f'<span style="font-size:28px;pointer-events:none;">{el["icon"]}</span>'
            )
            cards += (
                f'<div class="elem-card" data-idx="{idx}">'
                f'{img_tag}'
                f'<span class="elem-name">{el["name"]}</span>'
                f'</div>'
            )
        grids += (
            f'<div class="cat-grid" id="cat-grid-{i}" '
            f'style="display:{display};'
            f'grid-template-columns:repeat(4,1fr);gap:8px;padding:2px 0 8px;">'
            f'{cards}</div>'
        )

    return (
        '<div class="elem-picker" id="elem-picker">'
        '<div class="picker-handle"></div>'
        f'<div class="cat-tabs-row">{tabs}</div>'
        f'<div class="cat-content">{grids}</div>'
        '</div>'
    )


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 鐢诲竷 HTML锛堝惈娴姩宸ュ叿鏍忥級
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
_CANVAS_HTML = (
    '<div id="canvas-wrapper">'
    '<canvas id="env-canvas"></canvas>'
    '<div id="canvas-toolbar">'
    '<button class="tb-btn tb-delete"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.deleteSelected()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.deleteSelected()">'
    '<svg width="11" height="11" viewBox="0 0 11 11" fill="none">'
    '<path d="M1 1L10 10M10 1L1 10" stroke="white" stroke-width="2" stroke-linecap="round"/>'
    '</svg> 鍒犻櫎</button>'
    '<button class="tb-btn"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.duplicateSelected()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.duplicateSelected()">'
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
    '<rect x="3" y="3" width="7" height="7" rx="1.5" stroke="white" stroke-width="1.5"/>'
    '<rect x="1" y="1" width="7" height="7" rx="1.5" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>'
    '</svg> 澶嶅埗</button>'
    '<button class="tb-btn"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.bringToFront()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.bringToFront()">'
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
    '<path d="M6 1v8M3 4l3-3 3 3" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg> 缃《</button>'
    '</div>'
    '</div>'
)

# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 鐢诲竷涓撶敤 CSS锛堟敞鍏?<head>锛?# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
_CANVAS_CSS = '''<style>
#canvas-wrapper {
  position: relative; width: 100%; overflow: hidden;
  border-radius: 26px;
  box-shadow: 0 22px 48px rgba(0,0,0,0.24);
  background: #101D16;
  border: 1px solid rgba(244,240,230,0.12);
}
#canvas-toolbar {
  position: absolute; display: none;
  background: rgba(27,67,50,0.88);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(82,183,136,0.25);
  border-radius: 24px; padding: 5px 8px;
  gap: 4px; align-items: center; z-index: 100;
  box-shadow: 0 6px 20px rgba(0,0,0,0.25);
  transform: translateX(-50%);
}
.tb-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.12); border: none; border-radius: 16px;
  color: white; padding: 5px 11px; font-size: 12px; cursor: pointer;
  font-weight: 500; transition: background 0.15s; white-space: nowrap;
}
.tb-btn:active { background: rgba(255,255,255,0.28); }
.tb-btn.tb-delete { background: rgba(231,111,81,0.4); }
.tb-btn.tb-delete:active { background: rgba(231,111,81,0.6); }
.elem-picker {
  width: calc(100% - 24px);
  margin: 4px auto 0;
  background:
    linear-gradient(180deg, rgba(248,250,244,0.96), rgba(232,239,228,0.96)),
    url('/static/images/bamboo-mist-texture.webp') center/cover no-repeat;
  background-blend-mode: normal, soft-light;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(20,35,26,0.08);
  border-radius: 30px 30px 0 0;
  box-shadow: 0 -18px 44px rgba(0,0,0,0.18);
  overflow: hidden;
}
.picker-handle {
  width: 46px; height: 5px; background: rgba(20,35,26,0.16);
  border-radius: 999px; margin: 12px auto 8px;
}
.cat-tabs-row {
  display: flex; gap: 8px; padding: 6px 16px 8px;
  overflow-x: auto; scrollbar-width: none;
}
.cat-tabs-row::-webkit-scrollbar { display: none; }
.cat-tab {
  flex-shrink: 0; min-width: 68px; padding: 9px 16px; border-radius: 999px;
  border: 1px solid rgba(20,35,26,0.12); background: rgba(255,255,255,0.72);
  font-size: 13px; font-weight: 800; cursor: pointer; color: rgba(20,35,26,0.62);
  transition: all 0.2s; white-space: nowrap;
}
.cat-tab-active {
  background: #2D6A4F;
  color: #F4F0E6;
  border-color: #2D6A4F;
  box-shadow: 0 10px 22px rgba(45,106,79,0.18);
}
.cat-content {
  padding: 4px 16px 18px;
}
.elem-card {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  min-height: 96px;
  padding: 13px 4px 10px; background: rgba(255,255,255,0.76); border-radius: 22px;
  border: 1px solid rgba(20,35,26,0.08); cursor: pointer;
  transition: all 0.18s; text-align: center;
  box-shadow: 0 10px 24px rgba(20,35,26,0.07);
  -webkit-tap-highlight-color: transparent;
}
.elem-card:active { transform: scale(0.91); }
.elem-selected {
  border-color: rgba(45,106,79,0.45) !important;
  background: rgba(45,106,79,0.08) !important;
  box-shadow: 0 0 0 3px rgba(45,106,79,0.10), 0 10px 24px rgba(20,35,26,0.08) !important;
}
.elem-name {
  font-size: 12px; color: #14231A; font-weight: 800;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 62px;
}
.elem-card[draggable="true"] { cursor: grab; }
.elem-dragging {
  opacity: 0.4 !important; transform: scale(0.88) !important;
  box-shadow: none !important;
}
.drag-ghost {
  position: fixed; pointer-events: none; z-index: 10000;
  transform: translate(-50%, -50%);
  background: rgba(255,255,255,0.92); border-radius: 14px;
  padding: 8px; box-shadow: 0 8px 28px rgba(0,0,0,0.22);
  display: flex; align-items: center; justify-content: center;
}
#canvas-wrapper.canvas-drag-over {
  outline: 3px dashed #52B788 !important;
  outline-offset: -3px;
  box-shadow: 0 8px 32px rgba(82,183,136,0.3),
              inset 0 0 40px rgba(82,183,136,0.06) !important;
  transition: outline 0.15s, box-shadow 0.15s;
}
.drag-stage {
  background:
    linear-gradient(180deg, rgba(255,255,248,0.64), rgba(232,240,227,0.90)),
    url('/static/images/light-bamboo-paper.webp') center/cover no-repeat;
}
.drag-status-row {
  color: rgba(23,49,38,0.62);
}
.drag-soft-note {
  color: rgba(23,49,38,0.58) !important;
}
.drag-light-actions {
  width: calc(100% - 24px);
  margin: 0 auto;
  padding: 12px 18px 104px;
  gap: 9px;
  background: rgba(232,239,228,0.96);
  border: 1px solid rgba(20,35,26,0.08);
  border-top: 0;
  border-radius: 0 0 30px 30px;
  box-shadow: 0 22px 48px rgba(0,0,0,0.16);
}
</style>'''


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 椤甸潰娉ㄥ唽
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def create_drag_page():
    picker_html = _build_picker_html()

    @ui.page('/drag-mode')
    def drag_mode_page(sid: str = '', back: str = ''):

        # 鈹€鈹€ 鍩虹 head 娉ㄥ叆 鈹€鈹€
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"'
            ' crossorigin="anonymous"></script>'
        )
        ui.add_head_html('<script src="/static/canvas_editor.js"></script>')
        ui.add_head_html(_CANVAS_CSS)

        # 鈹€鈹€ 鎻愬墠鑾峰彇浼氳瘽鏁版嵁锛屼緵 init script 浣跨敤 鈹€鈹€
        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'drag'

        img_url = ''
        if session and session.uploaded_image_path:
            img_url = f'/api/image/{Path(session.uploaded_image_path).name}'

        # 妫€鏌ユ槸鍚︽湁宸蹭繚瀛樼殑鐢诲竷鐘舵€侊紙浠庤褰曢〉杩斿洖缂栬緫鏃朵娇鐢級
        canvas_json_url = ''
        if session:
            cjp = getattr(session, 'canvas_json_path', '') or ''
            if cjp and Path(cjp).exists():
                canvas_json_url = f'/api/image/{Path(cjp).name}'

        # 鈹€鈹€ 鍏抽敭锛歩nit script 蹇呴』鏀惧湪 add_head_html锛屼笉鑳界敤 ui.html() 鈹€鈹€
        # ui.html() 搴曞眰閫氳繃 Vue v-html 娓叉煋锛宻cript 鏍囩涓嶄細琚墽琛屻€?        # add_head_html 鐩存帴娉ㄥ叆 <head>锛岃剼鏈甯告墽琛屻€?        ui.add_head_html(f'''<script>
window._ELEMENTS = {_ELEMENTS_JS};

function envSwitchCat(idx) {{
  document.querySelectorAll('.cat-grid').forEach(function(g, i) {{
    g.style.display = (i === idx) ? 'grid' : 'none';
  }});
  document.querySelectorAll('.cat-tab').forEach(function(t, i) {{
    t.classList.toggle('cat-tab-active', i === idx);
  }});
}}

(function waitAndInit() {{
  var fabricOk = typeof fabric !== 'undefined';
  var envCanvasOk = typeof window.EnvCanvas !== 'undefined';
  var domOk = !!document.getElementById('env-canvas');
  if (!fabricOk || !envCanvasOk || !domOk) {{
    setTimeout(waitAndInit, 80);
    return;
  }}
  EnvCanvas.init('env-canvas', {json.dumps(img_url)}, {json.dumps(sid)});
  setTimeout(function() {{ EnvCanvas.initDragDrop(); }}, 200);

  // 鎭㈠宸蹭繚瀛樼殑鐢诲竷瀵硅薄鐘舵€?  var canvasJsonUrl = {json.dumps(canvas_json_url)};
  if (canvasJsonUrl) {{
    var _restoreAttempts = 0;
    function _tryRestoreDrag() {{
      _restoreAttempts++;
      if (_restoreAttempts > 50) return;
      if (!EnvCanvas.isBackgroundLoaded || !EnvCanvas.isBackgroundLoaded()) {{
        setTimeout(_tryRestoreDrag, 200);
        return;
      }}
      fetch(canvasJsonUrl).then(function(r) {{ return r.text(); }}).then(function(jsonStr) {{
        if (jsonStr && jsonStr !== '[]') {{
          EnvCanvas.restoreObjects(jsonStr);
        }}
      }}).catch(function() {{}});
    }}
    setTimeout(_tryRestoreDrag, 300);
  }}

  // 浜嬩欢濮旀墭锛氬垎绫绘爣绛惧垏鎹?  document.addEventListener('click', function(e) {{
    var tab = e.target.closest('.cat-tab');
    if (tab && tab.dataset.catidx !== undefined) {{
      envSwitchCat(parseInt(tab.dataset.catidx, 10));
    }}
    var card = e.target.closest('.elem-card');
    if (card && card.dataset.idx !== undefined) {{
      EnvCanvas.addByIndex(parseInt(card.dataset.idx, 10));
    }}
  }});
}})();
</script>''')

        # 鈹€鈹€ 椤甸潰甯冨眬 鈹€鈹€
        with ui.column().classes('mobile-page light-page').style('gap:0'):
            bottom_nav(light=True)
            # 椤堕儴瀵艰埅鏍?            with ui.row().style(LIGHT_TOP_BAR_STYLE):
                back_url = f'/result?sid={sid}&back=records' if back == 'result' else f'/mode-select?sid={sid}'
                ui.button(
                    icon='arrow_back',
                    on_click=lambda: smooth_navigate(back_url),
                ).props('flat round dense').style('color:#2F7B58')
                ui.label('鑷敱鍒涗綔').style(
                    'font-size:17px;font-weight:800;margin-left:4px;flex:1;color:#173126'
                )
                ui.button(
                    '娓呯┖',
                    on_click=lambda: ui.run_javascript('EnvCanvas.clearAll()'),
                ).props('flat dense no-caps').style(
                    'color:#2F7B58;font-size:13px;font-weight:700'
                )

            # 涓诲唴瀹瑰尯
            with ui.column().classes('drag-stage').style(
                'padding:18px 20px 18px;gap:12px;width:100%;'
                'border-bottom:1px solid rgba(244,240,230,0.08);'
            ):

                # Fabric.js 鐢诲竷瀹瑰櫒锛堢函 HTML锛屽惈娴姩宸ュ叿鏍忥級
                ui.html(_CANVAS_HTML, sanitize=False).style('width:100%')

                # 鐘舵€佹爮
                with ui.row().classes('drag-status-row').style(
                    'width:100%;justify-content:space-between;align-items:center;padding:2px 0'
                ):
                    ui.html(
                        '<span id="element-count" style="font-size:12px;color:rgba(23,49,38,0.62);">'
                        '宸叉斁缃? 0 涓?/span>'
                    )
                    ui.html(
                        '<span id="selected-label" '
                        'style="font-size:12px;color:rgba(23,49,38,0.70);font-weight:700;'
                        'padding:5px 12px;border-radius:999px;'
                        'background:rgba(47,123,88,0.09)">鏈€変腑</span>'
                    )

                ui.label('鐐瑰嚮娣诲姞鎴栨嫋鎷藉厓绱犲埌鐢诲竷锛岄€変腑鍚庡彲缂╂斁 路 鏃嬭浆').style(
                    f'font-size:11px;color:{COLORS["text_secondary"]};'
                    'font-weight:300;text-align:center;padding-bottom:2px'
                ).classes('drag-soft-note')

            # 鍏冪礌閫夋嫨闈㈡澘锛堢函 HTML + onclick 鐩磋皟 EnvCanvas.addByIndex锛?            ui.html(picker_html).style('width:100%;flex-shrink:0')

            # 搴曢儴鎿嶄綔鍖?            with ui.column().classes('drag-light-actions'):
                error_label = ui.label().style(
                    f'display:none;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )

                loading_row = ui.element('div').style('display:none;width:100%')
                with loading_row:
                    with ui.row().style('width:100%;align-items:center;gap:10px;padding:8px 0'):
                        ui.spinner('dots', size='sm', color=COLORS['primary'])
                        ui.label('AI 姝ｅ湪铻嶅悎鍏冪礌...').style(
                            f'font-size:14px;color:{COLORS["primary_dark"]};font-weight:500'
                        )

                gen_btn = ui.button(
                    '鉁?AI 铻嶅悎鐢熸垚',
                    on_click=lambda: generate_inpaint(),
                ).props('no-caps unelevated').style(LIGHT_PRIMARY_BTN_STYLE)

        # 鈹€鈹€ 鐢熸垚澶勭悊閫昏緫 鈹€鈹€
        async def generate_inpaint():
            layout_json = await ui.run_javascript(
                'EnvCanvas.getLayoutJSON()', timeout=5.0
            )
            elements = json.loads(layout_json) if layout_json else []

            if not elements:
                ui.notify('璇峰厛鏀剧疆鑷冲皯涓€涓厓绱?, type='warning')
                return

            # 鎴彇鐢诲竷蹇収
            canvas_data_url = ''
            try:
                canvas_data_url = await ui.run_javascript(
                    'EnvCanvas.getCanvasDataURL()', timeout=10.0
                )
            except Exception:
                pass

            gen_btn.set_visibility(False)
            loading_row.style('display:block')
            error_label.style('display:none')

            if session:
                session.placed_elements = elements
                session.generation_count = getattr(session, 'generation_count', 0) + 1
                if canvas_data_url:
                    from app.state import save_canvas_snapshot
                    save_canvas_snapshot(sid, canvas_data_url)

            # 淇濆瓨鐢诲竷 Fabric 瀵硅薄 JSON锛堢敤浜庡悗缁仮澶嶇紪杈戯級
            try:
                objects_json = await ui.run_javascript(
                    'EnvCanvas.getObjectsJSON()', timeout=10.0
                )
                if objects_json and objects_json != '[]':
                    from app.state import save_canvas_json
                    save_canvas_json(sid, objects_json)
            except Exception:
                pass

            try:
                from app.services.sd_service import generate_inpainting
                result_bytes, used_prompt = await asyncio.to_thread(
                    generate_inpainting,
                    session.uploaded_image_path,
                    elements,
                )
                if session:
                    session.llm_prompt = used_prompt
                save_output(sid, result_bytes)
                smooth_navigate(f'/result?sid={sid}')
            except Exception as e:
                error_label.set_text(f'鐢熸垚澶辫触: {str(e)}')
                error_label.style(
                    f'display:block;padding:12px 16px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )
                gen_btn.set_visibility(True)
                loading_row.style('display:none')
