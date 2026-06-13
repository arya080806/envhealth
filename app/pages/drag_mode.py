"""自由创作模式页面 - Fabric.js 画布编辑器。"""
from __future__ import annotations

import asyncio
import base64
import json

from nicegui import ui

from app.components.icons import get_svg, icon_bench, icon_cabin, icon_pond, icon_sun, icon_tree
from app.components.nav import bottom_nav, smooth_navigate
from app.services.layout_snapshot import recover_drag_layout_snapshot
from app.state import get_session, media_url, resolve_media_path, save_canvas_json, save_output
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


CATEGORIES = [
    ('植被', '🌳', icon_tree, [
        ('🌳', '大树'),
        ('🌲', '松树'),
        ('🌿', '灌木'),
        ('🎋', '竹林'),
        ('🌺', '花朵'),
        ('🌱', '草坪'),
        ('🌴', '棕榈'),
        ('🌸tree', '樱花树'),
        ('🌾', '芦苇'),
        ('🌵', '仙人掌'),
        ('🪨moss', '苔藓'),
    ]),
    ('设施', '🪑', icon_bench, [
        ('🪑', '长椅'),
        ('🔦', '路灯'),
        ('⛲', '喷泉'),
        ('🗿', '雕塑'),
        ('🛤️', '小径'),
        ('🚧', '围栏'),
        ('🪁', '秋千'),
        ('⛩️', '凉亭'),
        ('🪵', '木栈道'),
        ('🎡', '风车'),
        ('🗑️', '垃圾桶'),
    ]),
    ('水景', '🌊', icon_pond, [
        ('💧', '小溪'),
        ('🏞️', '池塘'),
        ('🌊', '水面'),
        ('💦', '瀑布'),
        ('🪷lotus', '荷花'),
        ('🌿water', '水草'),
        ('🪨', '礁石'),
    ]),
    ('氛围', '☀️', icon_sun, [
        ('☀️', '阳光'),
        ('🌫️', '薄雾'),
        ('🍂', '落叶'),
        ('🌸', '花瓣'),
        ('🕊️', '飞鸟'),
        ('🌈', '彩虹'),
        ('✨bug', '萤火虫'),
        ('🦋', '蝴蝶'),
        ('🌙', '月光'),
    ]),
    ('建筑', '🏠', icon_cabin, [
        ('🏠', '木屋'),
        ('🧱', '石墙'),
        ('🌉', '拱桥'),
        ('🌻', '花圃'),
    ]),
]


def _svg_b64(fn, size: int = 80) -> str:
    svg = fn(size)
    return base64.b64encode(svg.encode('utf-8')).decode('ascii')


def _build_elements_data() -> tuple[list[dict], str]:
    items: list[dict] = []
    for cat_name, cat_icon, _tab_fn, elems in CATEGORIES:
        for icon, name in elems:
            svg = get_svg(icon, 80)
            b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii') if svg else ''
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


def _build_picker_html() -> str:
    cats: dict[str, list[dict]] = {}
    for el in _ALL_ELEMENTS:
        cats.setdefault(el['cat'], []).append(el)

    tabs = ''
    for i, cat_name in enumerate(cats.keys()):
        active = 'cat-tab-active' if i == 0 else ''
        tabs += f'<button type="button" class="cat-tab {active}" data-catidx="{i}">{cat_name}</button>'

    grids = ''
    for i, (cat_name, items) in enumerate(cats.items()):
        display = 'grid' if i == 0 else 'none'
        cards = ''
        for el in items:
            img_tag = (
                f'<img src="{el["dataUrl"]}" alt="{el["name"]}" '
                'style="width:40px;height:40px;object-fit:contain;pointer-events:none;">'
                if el['dataUrl']
                else f'<span style="font-size:28px;pointer-events:none;">{el["icon"]}</span>'
            )
            cards += (
                f'<button type="button" class="elem-card" data-idx="{el["idx"]}">'
                f'{img_tag}'
                f'<span class="elem-name">{el["name"]}</span>'
                '</button>'
            )
        grids += (
            f'<div class="cat-grid" id="cat-grid-{i}" '
            f'style="display:{display};grid-template-columns:repeat(4,1fr);gap:8px;padding:2px 0 8px;">'
            f'{cards}</div>'
        )

    return (
        '<div class="elem-picker" id="elem-picker">'
        '<div class="picker-handle"></div>'
        f'<div class="cat-tabs-row">{tabs}</div>'
        f'<div class="cat-content">{grids}</div>'
        '</div>'
    )


_CANVAS_HTML = (
    '<div id="canvas-wrapper">'
    '<div id="drag-canvas-fallback" class="drag-canvas-fallback">画布正在加载...</div>'
    '<canvas id="env-canvas"></canvas>'
    '<div id="canvas-toolbar">'
    '<button type="button" class="tb-btn tb-delete"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.deleteSelected()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.deleteSelected()">删除</button>'
    '<button type="button" class="tb-btn"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.duplicateSelected()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.duplicateSelected()">复制</button>'
    '<button type="button" class="tb-btn"'
    ' onmousedown="event.preventDefault();event.stopPropagation();EnvCanvas.bringToFront()"'
    ' ontouchstart="event.preventDefault();event.stopPropagation();EnvCanvas.bringToFront()">置顶</button>'
    '</div>'
    '</div>'
)


_CANVAS_CSS = '''<style>
.drag-workbench {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.drag-main-pane,
.drag-side-pane {
  width: 100%;
  min-width: 0;
}
#canvas-wrapper {
  position: relative; width: 100%; max-width: 100%; margin: 0 auto; overflow: hidden;
  border-radius: 26px;
  box-shadow: 0 22px 48px rgba(0,0,0,0.24);
  background: #101D16;
  border: 1px solid rgba(244,240,230,0.12);
  min-height: 198px;
}
.drag-canvas-fallback {
  position: absolute;
  inset: 0;
  z-index: 0;
  display: grid;
  place-items: center;
  color: rgba(244,240,230,0.74);
  font-size: 13px;
  background: rgba(16,29,22,0.86);
}
#env-canvas {
  position: relative;
  display: block;
}
.canvas-container .lower-canvas {
  z-index: 1;
  pointer-events: none;
}
.canvas-container .upper-canvas {
  z-index: 2;
  pointer-events: auto;
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
  pointer-events: none;
}
.tb-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.12); border: none; border-radius: 16px;
  color: white; padding: 5px 11px; font-size: 12px; cursor: pointer;
  font-weight: 700; transition: background 0.15s; white-space: nowrap;
  pointer-events: auto;
}
.tb-btn:active { background: rgba(255,255,255,0.28); }
.tb-btn.tb-delete { background: rgba(231,111,81,0.4); }
.tb-btn.tb-delete:active { background: rgba(231,111,81,0.6); }
.elem-picker {
  width: calc(100% - 24px);
  margin: 0 auto 0;
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
  border-radius: 999px; margin: 10px auto 7px;
}
.cat-tabs-row {
  display: flex; gap: 8px; padding: 5px 16px 7px;
  overflow-x: auto; scrollbar-width: none;
}
.cat-tabs-row::-webkit-scrollbar { display: none; }
.cat-tab {
  flex-shrink: 0; min-width: 68px; padding: 8px 15px; border-radius: 999px;
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
  padding: 2px 16px 14px;
}
.elem-card {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  min-height: 76px;
  padding: 8px 4px 7px; background: rgba(255,255,255,0.76); border-radius: 18px;
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
.drag-stage .q-column {
  min-height: 0 !important;
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
  padding: 12px 18px 92px;
  gap: 9px;
  background: rgba(232,239,228,0.96);
  border: 1px solid rgba(20,35,26,0.08);
  border-top: 0;
  border-radius: 0 0 30px 30px;
  box-shadow: 0 22px 48px rgba(0,0,0,0.16);
}
.drag-ai-progress {
  width: 100%;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255,255,248,.82);
  border: 1px solid rgba(47,123,88,.14);
  box-shadow: 0 14px 28px rgba(38,70,52,.10);
}
.drag-ai-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #173126;
  font-size: 12px;
  font-weight: 900;
}
.drag-ai-progress-note {
  margin-top: 5px;
  color: rgba(23,49,38,.58);
  font-size: 11px;
  line-height: 1.45;
  font-weight: 700;
}
.drag-ai-progress-track {
  overflow: hidden;
  height: 8px;
  margin-top: 10px;
  border-radius: 999px;
  background: rgba(47,123,88,.13);
}
.drag-ai-progress-fill {
  width: 72%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #2F7B58, #B7F27E);
  animation: dragAiProgress 2.6s ease-in-out infinite;
}
@keyframes dragAiProgress {
  0% { width: 12%; transform: translateX(-18%); }
  45% { width: 72%; transform: translateX(0); }
  100% { width: 92%; transform: translateX(6%); }
}
.drag-clear-confirm {
  position: fixed;
  inset: 0;
  z-index: 1240;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(7,18,13,.36);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.drag-clear-confirm.visible {
  display: flex;
}
.drag-clear-sheet {
  width: min(360px, calc(100vw - 48px));
  border-radius: 8px;
  padding: 18px;
  color: #173126;
  background: #FFFDF4;
  border: 1px solid rgba(47,123,88,.16);
  box-shadow: 0 22px 56px rgba(12,34,24,.24);
}
.drag-clear-title {
  font-size: 16px;
  line-height: 1.35;
  font-weight: 950;
  margin-bottom: 8px;
}
.drag-clear-text {
  color: rgba(23,49,38,.68);
  font-size: 13px;
  line-height: 1.55;
}
.drag-clear-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}
.drag-clear-actions button {
  border: 0;
  border-radius: 999px;
  min-width: 72px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
}
.drag-clear-actions .secondary {
  background: rgba(47,123,88,.10);
  color: #2F7B58;
}
.drag-clear-actions .danger {
  background: #E76F51;
  color: #FFFDF4;
}
.drag-save-card {
  width: min(340px, calc(100vw - 48px));
  border-radius: 8px;
  padding: 20px 18px 16px;
  color: #173126;
  background: #FFFDF4;
  border: 1px solid rgba(47,123,88,.16);
  box-shadow: 0 22px 56px rgba(12,34,24,.24);
}
.q-card.drag-save-card,
.q-dialog__inner > .q-card.drag-save-card {
  color: #173126 !important;
  background: #FFFDF4 !important;
  border: 1px solid rgba(47,123,88,.18) !important;
}
.q-card.drag-save-card *,
.q-dialog__inner > .q-card.drag-save-card * {
  color: inherit;
}
.q-card.drag-save-card .drag-save-copy,
.q-dialog__inner > .q-card.drag-save-card .drag-save-copy {
  color: rgba(23,49,38,.76) !important;
}
.drag-save-title {
  font-size: 17px;
  line-height: 1.35;
  font-weight: 950;
  text-align: center;
}
.drag-save-copy {
  margin-top: 8px;
  color: rgba(23,49,38,.68);
  font-size: 13px;
  line-height: 1.55;
  text-align: center;
}
.drag-save-action {
  margin-top: 16px;
}
.q-card.drag-save-card .q-btn.drag-save-action,
.q-dialog__inner > .q-card.drag-save-card .q-btn.drag-save-action {
  background: #2F7B58 !important;
  color: #F8FAF2 !important;
  border-radius: 999px !important;
}
@media (min-width: 900px) and (orientation: landscape) {
  .drag-workbench {
    display: grid;
    grid-template-columns: minmax(0, .62fr) minmax(390px, .38fr);
    gap: 18px;
    align-items: start;
    padding: 20px 28px 122px;
  }

  .drag-main-pane,
  .drag-side-pane {
    min-width: 0;
  }

  .drag-side-pane {
    display: grid;
    gap: 14px;
    position: sticky;
    top: 92px;
  }

  .drag-stage {
    width: 100% !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 18px 42px rgba(38,70,52,0.10);
  }

  #canvas-wrapper {
    min-height: 0;
    border-radius: 24px;
  }

  .drag-status-row {
    padding: 10px 16px !important;
  }

  .drag-soft-note {
    padding: 0 16px 14px !important;
  }

  .elem-picker {
    width: 100%;
    margin: 0;
    border-radius: 24px;
    box-shadow: 0 18px 42px rgba(38,70,52,0.10);
  }

  .cat-tabs-row {
    padding: 10px 14px 8px;
  }

  .cat-content {
    max-height: calc(100vh - 330px);
    overflow: auto;
    padding: 2px 14px 14px;
  }

  .cat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  }

  .drag-light-actions {
    width: 100%;
    margin: 0;
    padding: 14px;
    border-radius: 24px;
    border-top: 1px solid rgba(20,35,26,0.08);
  }
}
</style>'''


def _image_url(session) -> str:
    return media_url(getattr(session, 'uploaded_image_path', '') if session else '')


def _canvas_json_url(session) -> str:
    return media_url(getattr(session, 'canvas_json_path', '') if session else '')


def _build_drag_bootstrap(img_url: str, sid: str, canvas_json_url: str, placed_elements: list[dict] | None = None) -> str:
    img_json = json.dumps(img_url, ensure_ascii=False)
    sid_json = json.dumps(sid, ensure_ascii=False)
    canvas_json = json.dumps(canvas_json_url, ensure_ascii=False)
    placed_json = json.dumps(placed_elements or [], ensure_ascii=False)
    return f'''<script>
(function() {{
  window._ELEMENTS = {_ELEMENTS_JS};

  window.envSwitchCat = function(idx) {{
    document.querySelectorAll('.cat-grid').forEach(function(g, i) {{
      g.style.display = (i === idx) ? 'grid' : 'none';
    }});
    document.querySelectorAll('.cat-tab').forEach(function(t, i) {{
      t.classList.toggle('cat-tab-active', i === idx);
    }});
  }};

  function showCanvasFailure(message) {{
    var fallback = document.getElementById('drag-canvas-fallback');
    if (!fallback) return;
    fallback.textContent = message || '画布加载失败，请刷新页面';
    fallback.style.display = 'grid';
    fallback.style.zIndex = '2';
  }}

  function loadScriptOnce(src, globalName, marker) {{
    if (globalName && window[globalName]) return Promise.resolve();
    return new Promise(function(resolve, reject) {{
      var existing = document.querySelector('script[data-env-loader="' + marker + '"]');
      if (existing) {{
        if (globalName && window[globalName]) {{
          resolve();
          return;
        }}
        existing.remove();
      }}
      var script = document.createElement('script');
      script.src = src;
      script.dataset.envLoader = marker;
      script.onload = function() {{ resolve(); }};
      script.onerror = function() {{ reject(new Error(src)); }};
      document.head.appendChild(script);
    }});
  }}

  function bindPickerClicks() {{
    if (window.__envDragClickHandler) {{
      document.removeEventListener('click', window.__envDragClickHandler);
    }}
    window.__envDragClickHandler = function(e) {{
      var tab = e.target.closest('.cat-tab');
      if (tab && tab.dataset.catidx !== undefined) {{
        window.envSwitchCat(parseInt(tab.dataset.catidx, 10));
      }}
      var card = e.target.closest('.elem-card');
      if (card && card.dataset.idx !== undefined && window.EnvCanvas) {{
        window.EnvCanvas.addByIndex(parseInt(card.dataset.idx, 10));
      }}
    }};
    document.addEventListener('click', window.__envDragClickHandler);
  }}

  function restoreDraft() {{
    var canvasJsonUrl = {canvas_json};
    var fallbackLayout = {placed_json};
    if ((!canvasJsonUrl && (!fallbackLayout || !fallbackLayout.length)) || !window.EnvCanvas) return;
    var restoreKey = {sid_json} + '|' + (canvasJsonUrl || 'layout') + '|' + (fallbackLayout ? fallbackLayout.length : 0);
    if (window.__envDragRestoreKey === restoreKey) return;
    window.__envDragRestoreKey = restoreKey;
    var restoreAttempts = 0;
    function tryRestoreDrag() {{
      restoreAttempts += 1;
      if (restoreAttempts > 50) return;
      if (!EnvCanvas.isBackgroundLoaded || !EnvCanvas.isBackgroundLoaded()) {{
        setTimeout(tryRestoreDrag, 200);
        return;
      }}
      if (!canvasJsonUrl) {{
        EnvCanvas.restoreObjects('', fallbackLayout);
        return;
      }}
      fetch(canvasJsonUrl).then(function(r) {{ return r.text(); }}).then(function(jsonStr) {{
        if (jsonStr && jsonStr !== '[]') EnvCanvas.restoreObjects(jsonStr, fallbackLayout);
        else if (fallbackLayout && fallbackLayout.length) EnvCanvas.restoreObjects('', fallbackLayout);
      }}).catch(function() {{}});
    }}
    setTimeout(tryRestoreDrag, 300);
  }}

  function initDrag(attempt) {{
    var fabricOk = typeof window.fabric !== 'undefined';
    var envCanvasOk = typeof window.EnvCanvas !== 'undefined';
    var domOk = !!document.getElementById('env-canvas');
    if (fabricOk && envCanvasOk && domOk) {{
      EnvCanvas.init('env-canvas', {img_json}, {sid_json});
      setTimeout(function() {{ EnvCanvas.initDragDrop(); }}, 200);
      restoreDraft();
      bindPickerClicks();
      return;
    }}
    if (attempt < 100) {{
      setTimeout(function() {{ initDrag(attempt + 1); }}, 80);
      return;
    }}
    showCanvasFailure('画布加载失败，请刷新页面');
  }}

  loadScriptOnce('/static/vendor/fabric.min.js', 'fabric', 'fabric')
    .then(function() {{
      var envCanvasVersion = 'drag-layout-restore-20260613';
      var oldEnvScript = document.querySelector('script[data-env-loader="env-canvas"]');
      if (oldEnvScript && oldEnvScript.src.indexOf(envCanvasVersion) === -1) {{
        try {{ delete window.EnvCanvas; }} catch (e) {{ window.EnvCanvas = undefined; }}
        oldEnvScript.remove();
      }}
      if (window.EnvCanvas && (!window.EnvCanvas.requestClearAll || !window.EnvCanvas.uploadCanvasSnapshot)) {{
        try {{ delete window.EnvCanvas; }} catch (e) {{ window.EnvCanvas = undefined; }}
        oldEnvScript = document.querySelector('script[data-env-loader="env-canvas"]');
        if (oldEnvScript) oldEnvScript.remove();
      }}
      return loadScriptOnce('/static/canvas_editor.js?v=' + envCanvasVersion, 'EnvCanvas', 'env-canvas');
    }})
    .then(function() {{ initDrag(0); }})
    .catch(function() {{ showCanvasFailure('画布加载失败，请刷新页面'); }});
}})();
</script>'''


def create_drag_page():
    picker_html = _build_picker_html()

    @ui.page('/drag-mode')
    async def drag_mode_page(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(_CANVAS_CSS)

        session = get_session(sid) if sid else None

        img_url = _image_url(session)
        canvas_json_url = _canvas_json_url(session)
        back_url = f'/result?sid={sid}&back=records' if back == 'result' else (
            '/records' if back == 'records' else f'/mode-select?sid={sid}'
        )

        with ui.column().classes('mobile-page light-page').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE + 'padding-right:68px;gap:8px;'):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(back_url)).props('flat round dense').style(
                    'color:#2F7B58'
                )
                ui.label('自由创作').style('font-size:17px;font-weight:800;margin-left:4px;flex:1;color:#173126')
                ui.button('清除', on_click=lambda: ui.run_javascript('EnvCanvas.requestClearAll()')).props(
                    'unelevated dense no-caps'
                ).style(
                    'min-width:58px;height:34px;border-radius:12px;'
                    'background:rgba(47,123,88,.10);color:#2F7B58;'
                    'border:1px solid rgba(47,123,88,.18);font-size:13px;font-weight:900;box-shadow:none;'
                )
                save_btn = ui.button('保存').props(
                    'unelevated dense no-caps'
                ).style(
                    'min-width:58px;height:34px;border-radius:12px;'
                    'background:#2F7B58;color:#F8FAF2;'
                    'border:1px solid rgba(47,123,88,.28);font-size:13px;font-weight:900;box-shadow:none;'
                )

            with ui.element('div').classes('drag-workbench'):
                with ui.element('div').classes('drag-main-pane'):
                    with ui.column().classes('drag-stage').style(
                        'padding:16px 20px 12px;gap:10px;width:100%;'
                        'border-bottom:1px solid rgba(244,240,230,0.08);'
                    ):
                        ui.html(_CANVAS_HTML, sanitize=False).style('width:100%')

                        with ui.row().classes('drag-status-row').style(
                            'width:100%;justify-content:space-between;align-items:center;padding:2px 0'
                        ):
                            ui.html(
                                '<span id="element-count" style="font-size:12px;color:rgba(23,49,38,0.62);">'
                                '已放置: 0 个</span>',
                                sanitize=False,
                            )
                            ui.html(
                                '<span id="selected-label" '
                                'style="font-size:12px;color:rgba(23,49,38,0.70);font-weight:700;'
                                'padding:5px 12px;border-radius:999px;background:rgba(47,123,88,0.09)">未选中</span>',
                                sanitize=False,
                            )

                        ui.label('点击添加或拖拽元素到画布，选中后可缩放 · 旋转').style(
                            f'font-size:11px;color:{COLORS["text_secondary"]};'
                            'font-weight:300;text-align:center;padding-bottom:2px'
                        ).classes('drag-soft-note')

                with ui.element('div').classes('drag-side-pane'):
                    ui.html(picker_html, sanitize=False).style('width:100%;flex-shrink:0')

                    with ui.column().classes('drag-light-actions'):
                        error_label = ui.label().style(
                            f'display:none;padding:10px 14px;background:{COLORS["error"]}10;'
                            f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                            f'font-size:13px;color:{COLORS["error"]};width:100%'
                        )

                        loading_row = ui.element('div').style('display:none;width:100%')
                        with loading_row:
                            ui.html(
                                '<div class="drag-ai-progress">'
                                '<div class="drag-ai-progress-head">'
                                '<span>AI 正在生成</span><span>请稍候</span>'
                                '</div>'
                                '<div class="drag-ai-progress-note">'
                                'AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。'
                                '</div>'
                                '<div class="drag-ai-progress-track"><div class="drag-ai-progress-fill"></div></div>'
                                '</div>',
                                sanitize=False,
                            )

                        gen_btn = ui.button('✦ AI 融合生成', on_click=lambda: generate_inpaint()).props(
                            'no-caps unelevated'
                        ).style(LIGHT_PRIMARY_BTN_STYLE)

        ui.add_body_html(_build_drag_bootstrap(img_url, sid, canvas_json_url, getattr(session, 'placed_elements', []) if session else []))

        with ui.dialog() as save_dialog, ui.card().classes('drag-save-card'):
            save_dialog_title = ui.label('正在保存...').classes('drag-save-title')
            save_dialog_copy = ui.label('').classes('drag-save-copy').style('display:none')
            ui.button('知道了', on_click=save_dialog.close).props('unelevated no-caps').classes('drag-save-action').style(
                'width:100%;background:#2F7B58;color:#F8FAF2;font-weight:900;'
            )

        def _show_save_dialog(title: str, copy: str) -> None:
            save_dialog_title.set_text(title)
            if copy:
                save_dialog_copy.set_text(copy)
                save_dialog_copy.style('display:block')
            else:
                save_dialog_copy.set_text('')
                save_dialog_copy.style('display:none')
            save_dialog.open()

        async def save_draft():
            if not session:
                _show_save_dialog('\u65e0\u6cd5\u4fdd\u5b58', '\u5f53\u524d\u4f1a\u8bdd\u65e0\u6548\uff0c\u8bf7\u8fd4\u56de\u91cd\u65b0\u8fdb\u5165\u3002')
                return

            save_btn.disable()
            try:
                _show_save_dialog('\u6b63\u5728\u4fdd\u5b58...', '')
                await asyncio.sleep(0.05)
                session.mode_used = 'drag'
                saved_parts = []

                try:
                    layout_json = await ui.run_javascript('(window.EnvCanvas && EnvCanvas.getLayoutJSON()) || "[]"', timeout=5.0)
                    raw_elements = json.loads(layout_json) if layout_json else []
                    session.placed_elements = raw_elements if isinstance(raw_elements, list) else []
                    saved_parts.append('\u5143\u7d20\u5750\u6807')
                except Exception:
                    pass

                try:
                    objects_json = await ui.run_javascript('(window.EnvCanvas && EnvCanvas.getObjectsJSON()) || "[]"', timeout=8.0)
                    if objects_json is not None:
                        save_canvas_json(sid, objects_json or '[]')
                        saved_parts.append('\u753b\u5e03JSON')
                except Exception:
                    pass

                snapshot_saved = False
                snapshot_note = ''
                try:
                    upload_result = await ui.run_javascript(
                        f'(window.EnvCanvas && EnvCanvas.uploadCanvasSnapshot({json.dumps(sid)}, 4)) || ""',
                        timeout=45.0,
                    )
                    upload_data = json.loads(upload_result or '{}') if isinstance(upload_result, str) else {}
                    if upload_data.get('ok'):
                        snapshot_saved = True
                        saved_parts.append('\u5143\u7d20\u5e03\u5c40\u56fe')
                    elif upload_data.get('error'):
                        snapshot_note = str(upload_data.get('error'))[:120]
                except Exception as exc:
                    snapshot_note = str(exc)[:120]

                if not snapshot_saved:
                    try:
                        recovered_path = recover_drag_layout_snapshot(sid)
                        if recovered_path:
                            saved_parts.append('\u6062\u590d\u7248\u5143\u7d20\u5e03\u5c40\u56fe')
                    except Exception as exc:
                        snapshot_note = snapshot_note or str(exc)[:120]

                if not saved_parts:
                    raise RuntimeError('\u6ca1\u6709\u53ef\u4fdd\u5b58\u7684\u753b\u5e03\u6570\u636e')

                copy = ''
                if snapshot_note and not snapshot_saved:
                    copy = '\u9ad8\u6e05\u5feb\u7167\u5bfc\u51fa\u8d85\u65f6\uff0c\u5df2\u4fdd\u5b58\u7ed3\u6784\u5316\u8bb0\u5f55\u3002'
                _show_save_dialog('\u5df2\u4fdd\u5b58', copy)
            except Exception as exc:
                _show_save_dialog('\u4fdd\u5b58\u5931\u8d25', str(exc)[:160])
            finally:
                save_btn.enable()

        async def generate_inpaint():
            upload_path = resolve_media_path(session.uploaded_image_path if session else '')
            if not session or not upload_path:
                ui.notify('请先上传原始图片，再进入自由创作', type='warning')
                return

            try:
                layout_json = await ui.run_javascript('EnvCanvas.getLayoutJSON()', timeout=5.0)
                raw_elements = json.loads(layout_json) if layout_json else []
                from app.routers.api import _normalize_inpaint_elements
                elements = _normalize_inpaint_elements(raw_elements)
            except Exception:
                ui.notify('画布数据解析失败，请重试', type='negative')
                return
            if not elements:
                ui.notify('请先放置至少一个元素', type='warning')
                return

            snapshot_saved = False
            try:
                upload_result = await ui.run_javascript(
                    f'(window.EnvCanvas && EnvCanvas.uploadCanvasSnapshot({json.dumps(sid)}, 4)) || ""',
                    timeout=45.0,
                )
                upload_data = json.loads(upload_result or '{}') if isinstance(upload_result, str) else {}
                snapshot_saved = bool(upload_data.get('ok'))
            except Exception:
                pass

            gen_btn.disable()
            loading_row.style('display:block')
            error_label.style('display:none')

            session.mode_used = 'drag'
            session.placed_elements = elements
            if not snapshot_saved:
                try:
                    recover_drag_layout_snapshot(sid)
                except Exception:
                    pass

            try:
                objects_json = await ui.run_javascript('(window.EnvCanvas && EnvCanvas.getObjectsJSON()) || "[]"', timeout=10.0)
                if objects_json is not None:
                    save_canvas_json(sid, objects_json or '[]')
            except Exception:
                pass

            try:
                from app.routers.api import start_inpaint_generation_job
                started = start_inpaint_generation_job(
                    sid,
                    str(upload_path),
                    elements,
                )
                if not started:
                    raise RuntimeError('AI 已在后台生成中，请稍候。')
                _show_save_dialog('AI 会在后台生成', '可以前往其他页面，生成完成后会在草稿箱通知你。')
                gen_btn.set_text('后台生成中')
            except Exception as e:
                error_label.set_text(f'生成失败: {str(e)}')
                error_label.style(
                    f'display:block;padding:12px 16px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )
                gen_btn.enable()
                loading_row.style('display:none')

        save_btn.on('click', save_draft)
