"""自由创作模式页面 — Fabric.js 画布编辑器"""
import asyncio
import base64
import json
from pathlib import Path

from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session, save_output
from app.components.icons import get_svg

# ──────────────────────────────────────────────
# 元素分类数据
# ──────────────────────────────────────────────
CATEGORIES = [
    ('植被', '🌳', [
        ('🌳', '大树'), ('🌲', '松树'), ('🌿', '灌木'),
        ('🪷', '花草'), ('🌺', '花朵'), ('🍀', '草坪'), ('🌱', '嫩芽'),
    ]),
    ('设施', '🪑', [
        ('🪑', '长椅'), ('🔦', '路灯'), ('⛲', '喷泉'),
        ('🗿', '雕塑'), ('🛤️', '小径'), ('🏗️', '围栏'),
    ]),
    ('水景', '🌊', [
        ('🌊', '小溪'), ('🏞️', '池塘'), ('💧', '水面'),
    ]),
    ('氛围', '☀️', [
        ('☀️', '阳光'), ('🌫️', '薄雾'), ('🍂', '落叶'),
        ('🌸', '花瓣'), ('🦅', '飞鸟'),
    ]),
]

# ──────────────────────────────────────────────
# 模块加载时预生成 SVG 数据 URL（只执行一次）
# ──────────────────────────────────────────────
def _build_elements_data() -> tuple:
    items = []
    for cat_name, cat_icon, elems in CATEGORIES:
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


# ──────────────────────────────────────────────
# 构建元素选择面板 HTML（onclick 直调 JS，无服务器往返）
# ──────────────────────────────────────────────
def _build_picker_html() -> str:
    cats: dict = {}
    for el in _ALL_ELEMENTS:
        cats.setdefault(el['cat'], []).append(el)

    tabs = ''
    for i, (cat_name, items) in enumerate(cats.items()):
        active = 'cat-tab-active' if i == 0 else ''
        cat_icon = items[0]['catIcon']
        tabs += (
            f'<button class="cat-tab {active}" '
            f'data-catidx="{i}">'
            f'{cat_icon} {cat_name}</button>'
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


# ──────────────────────────────────────────────
# 画布 HTML（含浮动工具栏）
# ──────────────────────────────────────────────
_CANVAS_HTML = (
    '<div id="canvas-wrapper">'
    '<canvas id="env-canvas"></canvas>'
    '<div id="canvas-toolbar">'
    '<button class="tb-btn tb-delete" onclick="EnvCanvas.deleteSelected()">'
    '<svg width="11" height="11" viewBox="0 0 11 11" fill="none">'
    '<path d="M1 1L10 10M10 1L1 10" stroke="white" stroke-width="2" stroke-linecap="round"/>'
    '</svg> 删除</button>'
    '<button class="tb-btn" onclick="EnvCanvas.duplicateSelected()">'
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
    '<rect x="3" y="3" width="7" height="7" rx="1.5" stroke="white" stroke-width="1.5"/>'
    '<rect x="1" y="1" width="7" height="7" rx="1.5" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>'
    '</svg> 复制</button>'
    '<button class="tb-btn" onclick="EnvCanvas.bringToFront()">'
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
    '<path d="M6 1v8M3 4l3-3 3 3" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg> 置顶</button>'
    '</div>'
    '</div>'
)

# ──────────────────────────────────────────────
# 画布专用 CSS（注入 <head>）
# ──────────────────────────────────────────────
_CANVAS_CSS = '''<style>
#canvas-wrapper {
  position: relative; width: 100%; overflow: hidden;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(27,67,50,0.15);
  background: #e8f0ea;
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
  width: 100%;
  background: rgba(248,250,245,0.97);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(45,106,79,0.08);
}
.picker-handle {
  width: 36px; height: 4px; background: rgba(45,106,79,0.18);
  border-radius: 2px; margin: 10px auto 2px;
}
.cat-tabs-row {
  display: flex; gap: 6px; padding: 6px 16px 4px;
  overflow-x: auto; scrollbar-width: none;
}
.cat-tabs-row::-webkit-scrollbar { display: none; }
.cat-tab {
  flex-shrink: 0; padding: 6px 14px; border-radius: 20px;
  border: 1.5px solid rgba(45,106,79,0.15); background: white;
  font-size: 13px; font-weight: 500; cursor: pointer; color: #6B7280;
  transition: all 0.2s; white-space: nowrap;
}
.cat-tab-active { background: #2D6A4F; color: white; border-color: #2D6A4F; }
.cat-content {
  padding: 4px 16px 16px; overflow-y: auto; max-height: 215px;
  scrollbar-width: thin; scrollbar-color: rgba(45,106,79,0.2) transparent;
}
.cat-content::-webkit-scrollbar { width: 3px; }
.cat-content::-webkit-scrollbar-thumb { background: rgba(45,106,79,0.2); border-radius: 2px; }
.elem-card {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 4px 8px; background: white; border-radius: 14px;
  border: 2px solid transparent; cursor: pointer;
  transition: all 0.18s; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  -webkit-tap-highlight-color: transparent;
}
.elem-card:active { transform: scale(0.91); }
.elem-selected {
  border-color: #2D6A4F !important;
  background: rgba(45,106,79,0.06) !important;
  box-shadow: 0 0 0 3px rgba(45,106,79,0.12) !important;
}
.elem-name {
  font-size: 11px; color: #1A1A2E; font-weight: 500;
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
</style>'''


# ──────────────────────────────────────────────
# 页面注册
# ──────────────────────────────────────────────
def create_drag_page():
    picker_html = _build_picker_html()

    @ui.page('/drag-mode')
    def drag_mode_page(sid: str = ''):

        # ── 基础 head 注入 ──
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"'
            ' crossorigin="anonymous"></script>'
        )
        ui.add_head_html('<script src="/static/canvas_editor.js"></script>')
        ui.add_head_html(_CANVAS_CSS)

        # ── 提前获取会话数据，供 init script 使用 ──
        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'drag'

        img_url = ''
        if session and session.uploaded_image_path:
            img_url = f'/api/image/{Path(session.uploaded_image_path).name}'

        # ── 关键：init script 必须放在 add_head_html，不能用 ui.html() ──
        # ui.html() 底层通过 Vue v-html 渲染，script 标签不会被执行。
        # add_head_html 直接注入 <head>，脚本正常执行。
        ui.add_head_html(f'''<script>
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

  // 事件委托：分类标签切换
  document.addEventListener('click', function(e) {{
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

        # ── 页面布局 ──
        with ui.column().classes('mobile-page').style('background:#F8FAF5; gap:0'):

            # 顶部导航栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(
                    icon='arrow_back',
                    on_click=lambda: ui.navigate.to(f'/mode-select?sid={sid}'),
                ).props('flat round dense').style(f'color:{COLORS["primary_dark"]}')
                ui.label('自由创作').style(
                    f'font-size:17px;font-weight:600;margin-left:4px;flex:1;color:{COLORS["text"]}'
                )
                ui.button(
                    '清空',
                    on_click=lambda: ui.run_javascript('EnvCanvas.clearAll()'),
                ).props('flat dense no-caps').style(
                    f'color:{COLORS["primary"]};font-size:13px;font-weight:500'
                )

            # 主内容区
            with ui.column().style('padding:16px 20px 0;gap:10px;width:100%'):

                # Fabric.js 画布容器（纯 HTML，含浮动工具栏）
                ui.html(_CANVAS_HTML).style('width:100%')

                # 状态栏
                with ui.row().style(
                    'width:100%;justify-content:space-between;align-items:center;padding:2px 0'
                ):
                    ui.html(
                        '<span id="element-count" style="font-size:12px;color:#6B7280;">'
                        '已放置: 0 个</span>'
                    )
                    ui.html(
                        '<span id="selected-label" '
                        'style="font-size:12px;color:#6B7280;font-weight:500;'
                        'padding:4px 12px;border-radius:12px;'
                        'background:rgba(107,114,128,0.08)">未选中</span>'
                    )

                ui.label('点击添加或拖拽元素到画布，选中后可缩放 · 旋转').style(
                    f'font-size:11px;color:{COLORS["text_secondary"]};'
                    'font-weight:300;text-align:center;padding-bottom:2px'
                )

            # 元素选择面板（纯 HTML + onclick 直调 EnvCanvas.addByIndex）
            ui.html(picker_html).style('width:100%;flex-shrink:0')

            # 底部操作区
            with ui.column().style(
                'width:100%;padding:10px 20px 20px;gap:8px;'
                'background:rgba(248,250,245,0.97);'
                'border-top:1px solid rgba(45,106,79,0.06);'
            ):
                error_label = ui.label().style(
                    f'display:none;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )

                loading_row = ui.element('div').style('display:none;width:100%')
                with loading_row:
                    with ui.row().style('width:100%;align-items:center;gap:10px;padding:8px 0'):
                        ui.spinner('dots', size='sm', color=COLORS['primary'])
                        ui.label('AI 正在融合元素...').style(
                            f'font-size:14px;color:{COLORS["text"]};font-weight:500'
                        )

                gen_btn = ui.button(
                    '✦ AI 融合生成',
                    on_click=lambda: generate_inpaint(),
                ).props('no-caps unelevated').style(PRIMARY_BTN_STYLE)

        # ── 生成处理逻辑 ──
        async def generate_inpaint():
            layout_json = await ui.run_javascript(
                'EnvCanvas.getLayoutJSON()', timeout=5.0
            )
            elements = json.loads(layout_json) if layout_json else []

            if not elements:
                ui.notify('请先放置至少一个元素', type='warning')
                return

            gen_btn.set_visibility(False)
            loading_row.style('display:block')
            error_label.style('display:none')

            if session:
                session.placed_elements = elements
                session.generation_count = getattr(session, 'generation_count', 0) + 1

            try:
                from app.services.sd_service import generate_inpainting
                result_bytes = await asyncio.to_thread(
                    generate_inpainting,
                    session.uploaded_image_path,
                    elements,
                )
                save_output(sid, result_bytes)
                ui.navigate.to(f'/result?sid={sid}')
            except Exception as e:
                error_label.set_text(f'生成失败: {str(e)}')
                error_label.style(
                    f'display:block;padding:12px 16px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )
                gen_btn.set_visibility(True)
                loading_row.style('display:none')
