"""鐏垫劅鍒涙兂妯″紡椤甸潰 鈥?涓夊眰鎰熺煡寮曟搸鐗?""
import asyncio
import json
import random
from pathlib import Path

from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT
from app.state import get_session, save_output, save_canvas_snapshot, save_canvas_json
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate

# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 椤甸潰涓撶敤 CSS
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
_INSPIRE_CSS = '''<style>
#inspire-canvas-wrapper {
  position: relative; width: 100%; overflow: hidden;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(27,67,50,0.15);
  background: #F0F7F4;
  touch-action: none;
  cursor: crosshair;
}
#inspire-canvas-wrapper.drawing-active {
  box-shadow: 0 8px 32px rgba(82,183,136,0.3);
  outline: 2.5px solid rgba(82,183,136,0.4);
  outline-offset: -2px;
}
#inspire-canvas {
  display: block; width: 100%;
}

/* 鍗虫椂璇嗗埆鍥炬爣娴眰 */
.stroke-icon-badge {
  position: absolute;
  pointer-events: none;
  display: flex; align-items: center; gap: 4px;
  padding: 4px 8px; border-radius: 12px;
  font-size: 13px; font-weight: 600;
  white-space: nowrap;
  transform: translate(-50%, -120%);
  transition: opacity 0.3s ease, transform 0.3s ease;
  z-index: 10;
}
.stroke-icon-badge.high {
  background: rgba(45,106,79,0.88);
  color: white;
  box-shadow: 0 2px 8px rgba(45,106,79,0.35);
}
.stroke-icon-badge.low {
  background: rgba(107,114,128,0.7);
  color: white;
}
.stroke-icon-badge.fade-out {
  opacity: 0;
  transform: translate(-50%, -160%);
}

/* 璇嗗埆缁撴灉鍖?*/
.inspire-result-area {
  width: 100%; min-height: 72px;
  border-radius: 18px;
  padding: 14px 16px;
  transition: all 0.3s ease;
}
.inspire-result-idle {
  background: rgba(45,106,79,0.05);
  border: 1.5px dashed rgba(45,106,79,0.2);
}
.inspire-result-analyzing {
  background: rgba(82,183,136,0.08);
  border: 1.5px solid rgba(82,183,136,0.3);
}
.inspire-result-element {
  background: rgba(45,106,79,0.06);
  border: 1.5px solid rgba(45,106,79,0.2);
}
.inspire-result-mood {
  background: rgba(233,196,106,0.08);
  border: 1.5px solid rgba(233,196,106,0.35);
}
.inspire-result-composer {
  background: rgba(58,134,255,0.06);
  border: 1.5px solid rgba(58,134,255,0.2);
}

/* 璇嗗埆鍒扮殑鍏冪礌鏍囩 */
.elem-tag {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 12px; border-radius: 20px;
  background: rgba(45,106,79,0.1);
  border: 1px solid rgba(45,106,79,0.2);
  font-size: 12px; font-weight: 500; color: #1B4332;
  margin: 3px; transition: all 0.2s;
}
.elem-tag.high-confidence {
  background: rgba(45,106,79,0.15);
  border-color: rgba(45,106,79,0.35);
}

/* 鎯呯华鍙傛暟鏉?*/
.mood-bar-row {
  display: flex; align-items: center; gap: 8px; margin: 4px 0;
}
.mood-bar-label {
  font-size: 11px; color: #6B7280; font-weight: 500; width: 36px; flex-shrink: 0;
}
.mood-bar-track {
  flex: 1; height: 5px; border-radius: 3px;
  background: rgba(45,106,79,0.1);
  overflow: hidden;
}
.mood-bar-fill {
  height: 100%; border-radius: 3px;
  background: linear-gradient(90deg, #2D6A4F, #52B788);
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}

/* 宸ュ叿鏍?*/
.sketch-toolbar {
  display: flex; gap: 8px; align-items: center; padding: 8px 0 2px;
}
.sketch-tool-btn {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 12px;
  background: white; border: 1.5px solid rgba(45,106,79,0.15);
  cursor: pointer; transition: all 0.15s; flex-shrink: 0;
  font-size: 15px;
}
.sketch-tool-btn.active {
  background: rgba(45,106,79,0.1);
  border-color: rgba(45,106,79,0.4);
  box-shadow: 0 0 0 2px rgba(45,106,79,0.12);
}
.sketch-tool-btn:active { transform: scale(0.91); }

.brush-size-row {
  display: flex; align-items: center; gap: 6px; flex: 1;
}
.brush-dot {
  border-radius: 50%; background: #2D6A4F; flex-shrink: 0;
  cursor: pointer; transition: transform 0.15s;
}
.brush-dot.selected { outline: 2px solid #2D6A4F; outline-offset: 2px; }

/* 鐢荤瑪棰滆壊閫夋嫨 */
.color-dot {
  width: 24px; height: 24px; border-radius: 50%;
  cursor: pointer; flex-shrink: 0; transition: transform 0.15s;
  border: 2px solid transparent;
}
.color-dot.selected {
  border-color: white;
  box-shadow: 0 0 0 2px #2D6A4F;
  transform: scale(1.1);
}

/* 鍒嗘瀽鎻愮ず */
.analyze-hint {
  font-size: 11px; color: #6B7280; font-weight: 300;
  text-align: center; padding: 4px 0 0;
}

/* 妯″紡鍒囨崲鏍囩 */
.mode-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
}
.mode-badge-element { background: rgba(45,106,79,0.12); color: #1B4332; }
.mode-badge-mood { background: rgba(233,196,106,0.2); color: #92400e; }
.mode-badge-composer { background: rgba(58,134,255,0.12); color: #1e3a8a; }

/* 鑷畾涔夐鑹茬偣 */
#inspire-custom-color-dot {
  width: 24px; height: 24px; border-radius: 50%;
  cursor: pointer; flex-shrink: 0;
  border: 1.5px dashed rgba(45,106,79,0.5);
  background: conic-gradient(from 0deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3, #ff6b6b);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; color: white; font-weight: 700;
  text-shadow: 0 0 3px rgba(0,0,0,0.5);
  transition: transform 0.15s;
  position: relative;
}
#inspire-custom-color-dot.selected {
  border: 2px solid white;
  box-shadow: 0 0 0 2px #2D6A4F;
  transform: scale(1.1);
}
#inspire-custom-color-dot:active { transform: scale(0.92); }

/* 绗斿埛绮楃粏婊戞潌 */
.brush-slider-row {
  display: flex; align-items: center; gap: 5px; flex-shrink: 0;
}
.brush-size-indicator {
  border-radius: 50%; background: #2D6A4F; flex-shrink: 0;
}
.brush-range {
  -webkit-appearance: none; appearance: none;
  width: 80px; height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, #2D6A4F 0%, rgba(45,106,79,0.2) 100%);
  outline: none; cursor: pointer;
}
.brush-range::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 16px; height: 16px; border-radius: 50%;
  background: #2D6A4F;
  box-shadow: 0 1px 4px rgba(45,106,79,0.4);
  cursor: pointer;
}
.brush-range::-moz-range-thumb {
  width: 16px; height: 16px; border-radius: 50%; border: none;
  background: #2D6A4F;
  box-shadow: 0 1px 4px rgba(45,106,79,0.4);
  cursor: pointer;
}

/* 缁樼敾鎻愮ず鍗＄墖 */
.hint-cards-row {
  display: flex; gap: 8px; overflow-x: auto; padding: 6px 0 2px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.hint-cards-row::-webkit-scrollbar { display: none; }
.hint-card {
  flex-shrink: 0;
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 7px 10px 6px;
  background: rgba(255,255,255,0.7);
  border: 1px solid rgba(45,106,79,0.12);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
  min-width: 68px;
}
.hint-card:active {
  background: rgba(45,106,79,0.08);
  border-color: rgba(45,106,79,0.3);
  transform: scale(0.95);
}
.hint-card span {
  font-size: 10px; color: #6B7280; font-weight: 400;
  text-align: center; line-height: 1.3; white-space: nowrap;
}

/* 妯″紡鍒囨崲鎸夐挳 */
.mode-switch-btn {
  display: flex; align-items: center; justify-content: center;
  padding: 5px 12px; border-radius: 10px;
  font-size: 12px; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
  border: 1.5px solid rgba(45,106,79,0.2);
  background: white; color: #2D6A4F;
  gap: 4px; white-space: nowrap;
}
.mode-switch-btn.active {
  background: #2D6A4F; color: white;
  border-color: #2D6A4F;
}
.mode-switch-btn:active { transform: scale(0.95); }

/* 绗旂敾閫変腑楂樹寒 - 鐜板湪閫氳繃 fabric 鐢诲竷鍐呰櫄绾挎瀹炵幇 */

/* 鐢ㄦ埛鏍囨敞 badge */
.user-label-badge {
  position: absolute;
  pointer-events: none;
  display: flex; align-items: center; gap: 3px;
  padding: 3px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
  white-space: nowrap;
  transform: translate(-50%, -120%);
  z-index: 11;
  background: rgba(139,92,246,0.9);
  color: white;
  box-shadow: 0 2px 8px rgba(139,92,246,0.3);
}

/* 鏍囨敞杈撳叆闈㈡澘 */
#annotation-panel {
  display: none;
  width: 100%;
  background: rgba(255,255,255,0.97);
  border: 1.5px solid rgba(139,92,246,0.3);
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: 0 4px 16px rgba(139,92,246,0.12);
  transition: all 0.2s;
}
#annotation-panel.visible { display: block; }
#annotation-input {
  width: 100%; border: 1.5px solid rgba(45,106,79,0.2);
  border-radius: 10px; padding: 8px 12px;
  font-size: 13px; color: #1B4332;
  outline: none; background: #F8FAF5;
  transition: border-color 0.15s;
}
#annotation-input:focus { border-color: #8B5CF6; }
#annotation-input::placeholder { color: #9CA3AF; }
.annotation-btn-row {
  display: flex; gap: 8px; margin-top: 8px; justify-content: flex-end;
}
.annotation-btn {
  padding: 6px 16px; border-radius: 10px;
  font-size: 12px; font-weight: 600;
  cursor: pointer; border: none; transition: all 0.15s;
}
.annotation-btn-cancel {
  background: rgba(107,114,128,0.1); color: #6B7280;
}
.annotation-btn-confirm {
  background: #8B5CF6; color: white;
}
.annotation-btn:active { transform: scale(0.95); }

/* 绗旂敾鎿嶄綔鎸夐挳 */
.stroke-op-btn {
  display: flex; align-items: center; gap: 3px;
  padding: 5px 10px; border-radius: 8px;
  font-size: 11px; font-weight: 600;
  cursor: pointer; border: 1.5px solid rgba(107,114,128,0.2);
  background: white; color: #374151;
  transition: all 0.15s;
}
.stroke-op-btn:hover {
  background: rgba(107,114,128,0.08);
  border-color: rgba(107,114,128,0.35);
}
.stroke-op-btn:active { transform: scale(0.95); }

/* 鍥惧眰闈㈡澘 */
#layer-panel {
  display: none;
  width: 100%;
  max-height: 220px;
  overflow-y: auto;
  background: rgba(255,255,255,0.97);
  border: 1.5px solid rgba(45,106,79,0.15);
  border-radius: 14px;
  padding: 8px;
  box-shadow: 0 4px 16px rgba(45,106,79,0.08);
  transition: all 0.2s ease;
}
#layer-panel.visible { display: block; }
#layer-panel::-webkit-scrollbar { width: 4px; }
#layer-panel::-webkit-scrollbar-thumb {
  background: rgba(45,106,79,0.2); border-radius: 2px;
}

.layer-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; border-radius: 10px;
  cursor: pointer; transition: all 0.15s;
  border: 1.5px solid transparent;
  margin-bottom: 4px;
}
.layer-item:last-child { margin-bottom: 0; }
.layer-item:hover { background: rgba(45,106,79,0.04); }
.layer-item:active { transform: scale(0.98); }
.layer-item.selected {
  background: rgba(58,134,255,0.08);
  border-color: rgba(58,134,255,0.4);
}

.layer-thumb {
  width: 36px; height: 36px;
  border-radius: 6px; border: 1px solid rgba(45,106,79,0.1);
  background: #F0F7F4;
  flex-shrink: 0;
  object-fit: contain;
}

.layer-info {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: 2px;
}
.layer-info-name {
  font-size: 11px; font-weight: 600; color: #1B4332;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.layer-info-meta {
  display: flex; align-items: center; gap: 4px;
  font-size: 10px; color: #6B7280;
}
.layer-color-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.layer-index {
  font-size: 10px; color: #9CA3AF; font-weight: 500;
  flex-shrink: 0; width: 20px; text-align: center;
}
.layer-actions {
  display: flex; gap: 4px; flex-shrink: 0; margin-left: auto;
}
.layer-act-btn {
  padding: 2px 6px; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1);
  background: white; font-size: 10px; color: #6B7280; cursor: pointer;
  transition: all 0.15s; line-height: 1.2;
}
.layer-act-btn:hover { background: #f3f4f6; }
.layer-act-btn.del:hover { color: #EF4444; border-color: rgba(239,68,68,0.3); }

.layer-toggle-btn {
  display: flex; align-items: center; justify-content: center;
  padding: 4px 10px; border-radius: 8px;
  font-size: 11px; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
  border: 1.5px solid rgba(45,106,79,0.2);
  background: white; color: #2D6A4F; gap: 4px;
}
.layer-toggle-btn.active {
  background: rgba(45,106,79,0.08);
  border-color: rgba(45,106,79,0.4);
}
.layer-toggle-btn:active { transform: scale(0.95); }

.layer-empty {
  text-align: center; padding: 16px 0;
  font-size: 11px; color: #9CA3AF;
}
</style>'''


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 椤甸潰娉ㄥ唽
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def create_inspire_page():

    @ui.page('/inspire-mode')
    def inspire_mode_page(sid: str = '', back: str = ''):

        # 鈹€鈹€ Head 娉ㄥ叆 鈹€鈹€
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"'
            ' crossorigin="anonymous"></script>'
        )
        ui.add_head_html('<script src="/static/sketch_analyzer.js"></script>')
        ui.add_head_html('<script src="/static/sketch_composer.js"></script>')
        ui.add_head_html(_INSPIRE_CSS)

        session = get_session(sid) if sid else None
        if session:
            session.mode_used = 'inspire'

        img_url = ''
        if session and session.uploaded_image_path:
            img_url = f'/api/image/{Path(session.uploaded_image_path).name}'

        # 妫€鏌ユ槸鍚︽湁宸蹭繚瀛樼殑鐢诲竷鐘舵€侊紙浠庤褰曢〉杩斿洖缂栬緫鏃朵娇鐢級
        canvas_json_url = ''
        if session:
            cjp = getattr(session, 'canvas_json_path', '') or ''
            if cjp and Path(cjp).exists():
                canvas_json_url = f'/api/image/{Path(cjp).name}'

        # 鈹€鈹€ 鍒濆鍖栬剼鏈?鈹€鈹€
        ui.add_head_html(f'''<script>
(function() {{
  var _canvas = null;
  var _strokes = [];
  var _analysisTimer = null;
  var _lastResult = null;
  var _lastSceneIntent = null;
  var _drawColor = '#2D6A4F';
  var _brushSize = 4;
  var _imgUrl = {json.dumps(img_url)};
  var _sid = {json.dumps(sid)};
  var _mode = 'draw';
  var _selectedStrokeIds = [];
  var _pathObjects = [];
  var _labelBadges = [];
  var _strokeIdCounter = 0;
  var _groupIdCounter = 0;
  var _interactionRound = 1;
  var _selectionBoxObjects = [];
  var _selectionHandles = {{}};

  function _findByStrokeId(id) {{
    for (var i = 0; i < _strokes.length; i++) {{
      if (_strokes[i].strokeId === id) return {{ stroke: _strokes[i], path: _pathObjects[i], index: i }};
    }}
    return null;
  }}

  function _getSelectedEntries() {{
    var entries = [];
    _selectedStrokeIds.forEach(function(id) {{
      var e = _findByStrokeId(id);
      if (e) entries.push(e);
    }});
    return entries;
  }}

  function _calcStrokeBounds(pts) {{
    if (!pts || pts.length < 1) return null;
    var xs = pts.map(function(p) {{ return p.x; }});
    var ys = pts.map(function(p) {{ return p.y; }});
    var minX = Math.min.apply(null, xs);
    var maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys);
    var maxY = Math.max.apply(null, ys);
    var rawW = maxX - minX;
    var rawH = maxY - minY;
    var pad = 16;
    var minSize = 56;
    var width = Math.max(rawW + pad * 2, minSize);
    var height = Math.max(rawH + pad * 2, minSize);
    var cx = (minX + maxX) / 2;
    var cy = (minY + maxY) / 2;
    return {{
      minX: minX,
      minY: minY,
      maxX: maxX,
      maxY: maxY,
      left: cx - width / 2,
      top: cy - height / 2,
      width: width,
      height: height,
    }};
  }}

  function _getPathBounds(idx) {{
    var p = _pathObjects[idx];
    if (!p) return _calcStrokeBounds(_strokes[idx] ? _strokes[idx].pts : null);
    var br = p.getBoundingRect();
    var pad = 12;
    var minSize = 56;
    var w = Math.max(br.width + pad * 2, minSize);
    var h = Math.max(br.height + pad * 2, minSize);
    var cx = br.left + br.width / 2;
    var cy = br.top + br.height / 2;
    return {{
      minX: br.left,
      minY: br.top,
      maxX: br.left + br.width,
      maxY: br.top + br.height,
      left: cx - w / 2,
      top: cy - h / 2,
      width: w,
      height: h,
    }};
  }}

  var _undoStack = [];
  var _maxUndo = 10;
  var _movingThrottleTimer = null;

  function _moveStrokeByDelta(strokeEntry, dx, dy) {{
    if (!strokeEntry || !strokeEntry.path || !strokeEntry.stroke) return;
    strokeEntry.path.set({{
      left: (strokeEntry.path.left || 0) + dx,
      top: (strokeEntry.path.top || 0) + dy,
    }});
    strokeEntry.path.setCoords();
    var movedPts = window.SketchAnalyzer.extractPathPoints(strokeEntry.path);
    if (movedPts && movedPts.length > 0) {{
      strokeEntry.stroke.pts = movedPts;
    }}
  }}

  function _markSelectedAsMoved() {{
    _getSelectedEntries().forEach(function(entry) {{
      if (!entry || !entry.stroke) return;
      var history = entry.stroke.editHistory || [];
      if (history[history.length - 1] !== 'moved') history.push('moved');
      entry.stroke.editHistory = history;
    }});
  }}

  window.InspireCanvas = {{

    _isValidStroke: function(pts) {{
      if (!pts || pts.length < 2) return false;
      var xs = pts.map(function(p) {{ return p.x; }});
      var ys = pts.map(function(p) {{ return p.y; }});
      var w = Math.max.apply(null, xs) - Math.min.apply(null, xs);
      var h = Math.max.apply(null, ys) - Math.min.apply(null, ys);
      if (w < 6 && h < 6) return false;
      return true;
    }},

    _pushUndo: function(action) {{
      _undoStack.push(action);
      if (_undoStack.length > _maxUndo) _undoStack.shift();
    }},

    undo: function() {{
      if (_undoStack.length === 0) return;
      var action = _undoStack.pop();
      if (action.type === 'add') {{
        var idx = action.index;
        if (idx >= 0 && idx < _strokes.length) {{
          var path = _pathObjects[idx];
          if (path) _canvas.remove(path);
          _pathObjects.splice(idx, 1);
          _strokes.splice(idx, 1);
        }}
      }} else if (action.type === 'delete') {{
        var path = action.path;
        var stroke = action.stroke;
        var idx = action.index;
        if (path && stroke) {{
          path.set({{ selectable: false, evented: false }});
          _canvas.add(path);
          _strokes.splice(idx, 0, stroke);
          _pathObjects.splice(idx, 0, path);
        }}
      }} else if (action.type === 'copy') {{
        var indices = action.indices || [];
        for (var i = indices.length - 1; i >= 0; i--) {{
          var ci = indices[i];
          if (ci >= 0 && ci < _strokes.length) {{
            var cp = _pathObjects[ci];
            if (cp) _canvas.remove(cp);
            _pathObjects.splice(ci, 1);
            _strokes.splice(ci, 1);
          }}
        }}
      }}
      _selectedStrokeIds = [];
      _canvas.discardActiveObject();
      _canvas.renderAll();
      window.InspireCanvas._removeSelectionBoxes();
      window.InspireCanvas._hideAnnotationPanel();
      window.InspireCanvas._renderLabelBadges();
      window.InspireCanvas.updateStrokeCount();
      window.InspireCanvas.renderLayerPanel();
      if (_strokes.length > 0) {{
        window.InspireCanvas.scheduleAnalysis();
      }}
    }},

    // 鈹€鈹€ 鍒濆鍖?鈹€鈹€
    init: function() {{
      if (_canvas) return;
      var wrapper = document.getElementById('inspire-canvas-wrapper');
      var canvasEl = document.getElementById('inspire-canvas');
      if (!wrapper || !canvasEl || typeof fabric === 'undefined') {{
        setTimeout(window.InspireCanvas.init, 80); return;
      }}
      var w = wrapper.clientWidth || 440;
      var h = Math.round(w * 0.72);

      _canvas = new fabric.Canvas('inspire-canvas', {{
        width: w, height: h,
        isDrawingMode: true,
        backgroundColor: '#F0F7F4',
        selection: false,
        stopContextMenu: true,
      }});
      _canvas.allowTouchScrolling = false;

      _canvas.freeDrawingBrush.color = _drawColor;
      _canvas.freeDrawingBrush.width = _brushSize;
      _canvas.freeDrawingBrush.decimate = 2;

      if (_imgUrl) {{
        fabric.Image.fromURL(_imgUrl, function(img, err) {{
          if (err || !img || !_canvas) return;
          var scale = w / img.width;
          var newH = Math.round(img.height * scale);
          _canvas.setHeight(newH);
          if (wrapper) wrapper.style.height = newH + 'px';
          img.set({{ left:0, top:0, scaleX:scale, scaleY:scale,
                     selectable:false, evented:false, opacity:0.88 }});
          _canvas.add(img); _canvas.sendToBack(img);
          _canvas.renderAll();
        }}, {{ crossOrigin: 'anonymous' }});
      }}

      _canvas.on('path:created', function(e) {{
        var pts = window.SketchAnalyzer.extractPathPoints(e.path);
        if (!window.InspireCanvas._isValidStroke(pts)) {{
          _canvas.remove(e.path);
          wrapper.classList.remove('drawing-active');
          return;
        }}
        _strokeIdCounter++;
        var cw = _canvas.getWidth(), ch = _canvas.getHeight();
        var f = window.SketchAnalyzer._extractFeatures(pts);
        var yPct = f ? (f.centerY / ch) * 100 : 50;
        var zone = f ? window.SketchAnalyzer._getZone(yPct) : 'midground';
        var shapeType = (f && pts) ? window.SketchAnalyzer._classifyShape(f, pts, cw) : 'free';
        var match = window.SketchAnalyzer.quickMatchStroke(pts, cw, ch, _drawColor);
        _strokes.push({{
          pts: pts,
          color: _drawColor,
          strokeId: 'sk_' + _strokeIdCounter,
          createdAt: Date.now(),
          shapeType: shapeType,
          zone: zone,
          autoLabel: match ? match.elemName : '',
          autoConfidence: match ? match.confidence : 0,
          userLabel: null,
          source: 'auto',
          groupId: null,
          interactionRound: _interactionRound,
          editHistory: ['created'],
        }});
        _pathObjects.push(e.path);
        window.InspireCanvas._pushUndo({{ type:'add', index: _strokes.length - 1 }});
        window.InspireCanvas.showInstantFeedback(pts, _drawColor);
        window.InspireCanvas.scheduleAnalysis();
        window.InspireCanvas.renderLayerPanel();
        window.InspireCanvas.updateStrokeCount();
        wrapper.classList.remove('drawing-active');
      }});
      _canvas.on('mouse:down', function(opt) {{
        if (_mode === 'draw') {{
          wrapper.classList.add('drawing-active');
        }} else if (_mode === 'select') {{
          window.InspireCanvas._handleSelectClick(opt);
        }}
      }});
      _canvas.on('mouse:up', function() {{
        wrapper.classList.remove('drawing-active');
      }});

      _canvas.on('object:moving', function(ev) {{
        if (_mode !== 'select') return;
        var obj = ev.target;
        if (!obj) return;
        var idx = _pathObjects.indexOf(obj);
        if (idx < 0 || !_strokes[idx]) return;
        if (!_movingThrottleTimer) {{
          _movingThrottleTimer = setTimeout(function() {{
            _movingThrottleTimer = null;
            window.InspireCanvas._updateSelectionHighlight();
          }}, 50);
        }}
      }});

      _canvas.on('object:modified', function(ev) {{
        if (_mode !== 'select') return;
        var obj = ev.target;
        if (!obj) return;
        var idx = _pathObjects.indexOf(obj);
        if (idx >= 0 && _strokes[idx]) {{
          var history = _strokes[idx].editHistory || [];
          if (history[history.length - 1] !== 'moved') history.push('moved');
          _strokes[idx].editHistory = history;
        }}
        window.InspireCanvas._updateSelectionHighlight();
        window.InspireCanvas._renderLabelBadges();
        window.InspireCanvas.scheduleAnalysis();
      }});

      window.InspireCanvas.updateStrokeCount();
    }},

    // 鈹€鈹€ 妯″紡鍒囨崲 鈹€鈹€
    setMode: function(mode) {{
      _mode = mode;
      var drawBtn = document.getElementById('mode-draw-btn');
      var selectBtn = document.getElementById('mode-select-btn');
      if (drawBtn) drawBtn.classList.toggle('active', mode === 'draw');
      if (selectBtn) selectBtn.classList.toggle('active', mode === 'select');

      if (_canvas) {{
        _canvas.isDrawingMode = (mode === 'draw');
        if (mode === 'draw') {{
          _canvas.defaultCursor = 'crosshair';
          window.InspireCanvas._clearSelection();
          window.InspireCanvas._hideAnnotationPanel();
        }} else {{
          _canvas.defaultCursor = 'pointer';
        }}
      }}
      var wrapper = document.getElementById('inspire-canvas-wrapper');
      if (wrapper) wrapper.style.cursor = (mode === 'draw') ? 'crosshair' : 'pointer';
    }},

    // 鈹€鈹€ 閫夋嫨妯″紡涓嬬偣鍑荤瑪鐢?鈹€鈹€
    _handleSelectClick: function(opt) {{
      if (!opt || !opt.pointer) return;
      var px = opt.pointer.x, py = opt.pointer.y;
      var hitId = null;
      var minDist = Infinity;

      for (var i = 0; i < _strokes.length; i++) {{
        var s = _strokes[i];
        if (!s.pts || s.pts.length < 1) continue;
        var bounds = _getPathBounds(i);
        if (!bounds) continue;
        var isSmall = (bounds.maxX - bounds.minX) < 40 || (bounds.maxY - bounds.minY) < 40;
        var extraPad = isSmall ? 28 : 12;
        if (px >= bounds.left - extraPad && px <= bounds.left + bounds.width + extraPad &&
            py >= bounds.top - extraPad && py <= bounds.top + bounds.height + extraPad) {{
          var cx = bounds.left + bounds.width / 2;
          var cy = bounds.top + bounds.height / 2;
          var d = Math.sqrt((px - cx) * (px - cx) + (py - cy) * (py - cy));
          if (d < minDist) {{ minDist = d; hitId = s.strokeId; }}
        }}
      }}

      if (!hitId) return;

      _selectedStrokeIds = [hitId];
      window.InspireCanvas._updateSelectionHighlight();
      window.InspireCanvas._showAnnotationPanel();
      window.InspireCanvas.renderLayerPanel();
      window.InspireCanvas._scrollLayerPanelToSelected(hitId);
    }},

    _removeSelectionBoxes: function() {{
      _selectionBoxObjects.forEach(function(obj) {{
        if (_canvas) _canvas.remove(obj);
      }});
      _selectionBoxObjects = [];
      _selectionHandles = {{}};
    }},

    _updateSelectionHighlight: function() {{
      window.InspireCanvas._removeSelectionBoxes();
      if (!_canvas) return;

      _pathObjects.forEach(function(p, i) {{
        if (!p || !p.set) return;
        var isSelected = _strokes[i] && _selectedStrokeIds.indexOf(_strokes[i].strokeId) >= 0;
        if (isSelected) {{
          var br = p.getBoundingRect();
          var isSmall = br.width < 40 || br.height < 40;
          var padSize = isSmall ? 36 : 24;
          p.set({{
            shadow: new fabric.Shadow({{ color: 'rgba(58,134,255,0.6)', blur: 12, offsetX: 0, offsetY: 0 }}),
            selectable: true,
            evented: true,
            hasControls: false,
            hasBorders: false,
            lockRotation: true,
            lockScalingX: true,
            lockScalingY: true,
            perPixelTargetFind: false,
            padding: padSize,
            cornerSize: 24,
          }});
        }} else {{
          p.set({{
            shadow: null,
            selectable: false,
            evented: false,
            padding: 0,
          }});
        }}
      }});

      _selectedStrokeIds.forEach(function(sid, num) {{
        var e = _findByStrokeId(sid);
        if (!e || !e.stroke.pts || e.stroke.pts.length < 1) return;
        var bounds = _getPathBounds(e.index);
        if (!bounds) return;
        var rect = new fabric.Rect({{
          left: bounds.left,
          top: bounds.top,
          width: bounds.width,
          height: bounds.height,
          fill: 'rgba(58,134,255,0.04)',
          stroke: 'rgba(58,134,255,0.7)',
          strokeWidth: 1.5,
          strokeDashArray: [5, 3],
          selectable: false,
          evented: false,
        }});
        _canvas.add(rect);
        _selectionBoxObjects.push(rect);
        _selectionHandles[sid] = rect;

        var label = new fabric.Text(String(num + 1), {{
          left: bounds.left + 2,
          top: bounds.top - 16,
          fontSize: 11,
          fontWeight: '700',
          fill: 'white',
          backgroundColor: 'rgba(58,134,255,0.85)',
          padding: 2,
          selectable: false,
          evented: false,
        }});
        _canvas.add(label);
        _selectionBoxObjects.push(label);
      }});

      _canvas.renderAll();
    }},

    _clearSelection: function() {{
      _selectedStrokeIds = [];
      window.InspireCanvas._removeSelectionBoxes();
      _pathObjects.forEach(function(p) {{
        if (p && p.set) p.set({{ shadow: null, selectable: false, evented: false }});
      }});
      if (_canvas) _canvas.renderAll();
    }},

    // 鈹€鈹€ 鏍囨敞闈㈡澘 鈹€鈹€
    _showAnnotationPanel: function() {{
      var panel = document.getElementById('annotation-panel');
      if (!panel) return;
      panel.classList.add('visible');
      var input = document.getElementById('annotation-input');
      if (input) {{
        var existing = '';
        if (_selectedStrokeIds.length === 1) {{
          var e = _findByStrokeId(_selectedStrokeIds[0]);
          if (e) existing = e.stroke.userLabel || '';
        }}
        input.value = existing;
      }}
      var hint = document.getElementById('annotation-hint');
      if (hint) hint.textContent = '宸查€夋嫨 ' + _selectedStrokeIds.length + ' 涓瑪鐢?;
      var groupBtn = document.getElementById('group-btn');
      if (groupBtn) groupBtn.style.display = _selectedStrokeIds.length > 1 ? 'inline-flex' : 'none';
    }},

    _hideAnnotationPanel: function() {{
      var panel = document.getElementById('annotation-panel');
      if (panel) panel.classList.remove('visible');
    }},

    confirmAnnotation: function() {{
      var input = document.getElementById('annotation-input');
      if (!input) return;
      var label = input.value.trim();
      if (!label) return;

      var entries = _getSelectedEntries();
      entries.forEach(function(e) {{
        e.stroke.userLabel = label;
        e.stroke.source = 'user';
        e.stroke.editHistory.push('labeled');
        if (!e.stroke.groupId) {{
          _groupIdCounter++;
          e.stroke.groupId = 'grp_' + _groupIdCounter;
        }}
      }});

      window.InspireCanvas._renderLabelBadges();
      window.InspireCanvas._clearSelection();
      window.InspireCanvas._hideAnnotationPanel();
      window.InspireCanvas.renderLayerPanel();
      window.InspireCanvas.scheduleAnalysis();
    }},

    groupSelected: function() {{
      if (_selectedStrokeIds.length < 2) return;
      _groupIdCounter++;
      var gid = 'grp_' + _groupIdCounter;
      var entries = _getSelectedEntries();
      entries.forEach(function(e) {{
        e.stroke.groupId = gid;
        e.stroke.editHistory.push('grouped');
      }});
      window.InspireCanvas._updateSelectionHighlight();
      var hint = document.getElementById('annotation-hint');
      if (hint) hint.textContent = '宸查€夋嫨 ' + _selectedStrokeIds.length + ' 涓瑪鐢伙紙宸茬兢缁勶級';
    }},

    cancelAnnotation: function() {{
      window.InspireCanvas._clearSelection();
      window.InspireCanvas._hideAnnotationPanel();
    }},

    deleteSelected: function() {{
      var entries = _getSelectedEntries();
      if (entries.length === 0) return;
      window.InspireCanvas._removeSelectionBoxes();
      entries.sort(function(a, b) {{ return b.index - a.index; }});
      entries.forEach(function(e) {{
        window.InspireCanvas._pushUndo({{ type:'delete', index: e.index, path: e.path, stroke: e.stroke }});
        if (e.path) _canvas.remove(e.path);
        _pathObjects.splice(e.index, 1);
        _strokes.splice(e.index, 1);
      }});
      _selectedStrokeIds = [];
      _canvas.discardActiveObject();
      _canvas.renderAll();
      window.InspireCanvas._hideAnnotationPanel();
      window.InspireCanvas._renderLabelBadges();
      window.InspireCanvas.updateStrokeCount();
      window.InspireCanvas.renderLayerPanel();
      if (_strokes.length > 0) {{
        window.InspireCanvas.scheduleAnalysis();
      }} else {{
        window.InspireCanvas.showIdle();
      }}
    }},

    copySelected: function() {{
      var entries = _getSelectedEntries();
      if (entries.length === 0 || !_canvas) return;
      window.InspireCanvas._removeSelectionBoxes();
      var copiedIds = [];
      var copiedIndices = [];
      entries.forEach(function(e) {{
        if (!e.path || !e.stroke) return;
        e.path.clone(function(cloned) {{
          cloned.set({{ left: (cloned.left || 0) + 20, top: (cloned.top || 0) + 20, selectable: false, evented: false }});
          _canvas.add(cloned);
          var pts = window.SketchAnalyzer.extractPathPoints(cloned);
          if (pts.length > 0) {{
            _strokeIdCounter++;
            var newStrokeId = 'sk_' + _strokeIdCounter;
            var newStroke = {{
              pts: pts,
              color: e.stroke.color,
              strokeId: newStrokeId,
              createdAt: Date.now(),
              shapeType: e.stroke.shapeType,
              zone: e.stroke.zone,
              autoLabel: e.stroke.autoLabel,
              autoConfidence: e.stroke.autoConfidence,
              userLabel: e.stroke.userLabel,
              source: e.stroke.source,
              groupId: null,
              interactionRound: _interactionRound,
              editHistory: ['copied'],
            }};
            _strokes.push(newStroke);
            _pathObjects.push(cloned);
            copiedIds.push(newStrokeId);
            copiedIndices.push(_strokes.length - 1);
          }}
        }});
      }});
      if (copiedIndices.length > 0) {{
        window.InspireCanvas._pushUndo({{ type:'copy', indices: copiedIndices }});
      }}
      _selectedStrokeIds = copiedIds;
      window.InspireCanvas._updateSelectionHighlight();
      window.InspireCanvas._showAnnotationPanel();
      window.InspireCanvas.updateStrokeCount();
      window.InspireCanvas._renderLabelBadges();
      window.InspireCanvas.scheduleAnalysis();
      window.InspireCanvas.renderLayerPanel();
    }},

    _renderLabelBadges: function() {{
      document.querySelectorAll('.user-label-badge').forEach(function(el) {{
        if (el.parentNode) el.parentNode.removeChild(el);
      }});
      if (!_canvas) return;
      var wrapper = document.getElementById('inspire-canvas-wrapper');
      if (!wrapper) return;
      var cw = _canvas.getWidth(), ch = _canvas.getHeight();
      var scaleX = wrapper.offsetWidth / cw;
      var scaleY = wrapper.offsetHeight / ch;

      _strokes.forEach(function(s, idx) {{
        if (!s.userLabel || !s.pts || s.pts.length < 3) return;
        var bounds = _getPathBounds(idx);
        if (!bounds) return;
        var cx = (bounds.left + bounds.width / 2) * scaleX;
        var cy = bounds.top * scaleY;
        var badge = document.createElement('div');
        badge.className = 'user-label-badge';
        badge.style.left = cx + 'px';
        badge.style.top = cy + 'px';
        var badgeLabel = s.userLabel.length > 6 ? s.userLabel.substring(0, 6) + '鈥? : s.userLabel;
        badge.innerHTML = '鉁?' + badgeLabel;
        wrapper.appendChild(badge);
      }});
    }},

    // 鈹€鈹€ 鍗虫椂鍙嶉锛氬湪绗旇抗涓績鏄剧ず璇嗗埆鍥炬爣 鈹€鈹€
    showInstantFeedback: function(pts, strokeColor) {{
      if (!pts || pts.length < 5) return;
      var cw = _canvas ? _canvas.getWidth() : 440;
      var ch = _canvas ? _canvas.getHeight() : 320;

      var match = window.SketchAnalyzer.quickMatchStroke(pts, cw, ch, strokeColor);
      if (!match) return;

      var wrapper = document.getElementById('inspire-canvas-wrapper');
      if (!wrapper) return;

      // 灏嗙敾甯冨潗鏍囪浆涓?wrapper 鐩稿鍧愭爣
      var canvasRect = wrapper.getBoundingClientRect();
      var scaleX = wrapper.offsetWidth / cw;
      var scaleY = wrapper.offsetHeight / ch;

      var xs = pts.map(function(p) {{ return p.x; }});
      var ys = pts.map(function(p) {{ return p.y; }});
      var cx = ((Math.min.apply(null,xs) + Math.max.apply(null,xs)) / 2) * scaleX;
      var cy = ((Math.min.apply(null,ys) + Math.max.apply(null,ys)) / 2) * scaleY;

      var badge = document.createElement('div');
      var isHigh = match.confidence >= 0.70;
      badge.className = 'stroke-icon-badge ' + (isHigh ? 'high' : 'low');
      badge.style.left = cx + 'px';
      badge.style.top  = cy + 'px';

      var confText = isHigh ? '' : ' <span style="font-size:10px;opacity:0.7;">?</span>';
      badge.innerHTML = match.icon + ' ' + match.elemName + confText;
      wrapper.appendChild(badge);

      // 2s 鍚庢贰鍑虹Щ闄?      setTimeout(function() {{
        badge.classList.add('fade-out');
        setTimeout(function() {{ if (badge.parentNode) badge.parentNode.removeChild(badge); }}, 350);
      }}, 2000);
    }},

    // 鈹€鈹€ 鐢荤瑪棰滆壊 鈹€鈹€
    setColor: function(color) {{
      _drawColor = color;
      if (_canvas) _canvas.freeDrawingBrush.color = color;
      document.querySelectorAll('.color-dot').forEach(function(el) {{
        el.classList.toggle('selected', el.style.background === color);
      }});
      // 鑷畾涔夎壊鐐癸細鍙栨秷 selected锛堥璁捐壊琚€変腑鏃讹級
      var customDot = document.getElementById('inspire-custom-color-dot');
      if (customDot) customDot.classList.remove('selected');
    }},

    // 鈹€鈹€ 鑷畾涔夐鑹诧紙鏉ヨ嚜 color picker锛夆攢鈹€
    setCustomColor: function(color) {{
      _drawColor = color;
      if (_canvas) _canvas.freeDrawingBrush.color = color;
      document.querySelectorAll('.color-dot').forEach(function(el) {{
        el.classList.remove('selected');
      }});
      var customDot = document.getElementById('inspire-custom-color-dot');
      if (customDot) {{
        customDot.style.background = color;
        customDot.style.borderStyle = 'solid';
        customDot.style.borderColor = 'white';
        customDot.style.boxShadow = '0 0 0 2px ' + color;
        customDot.classList.add('selected');
        customDot.innerHTML = '<span style="font-size:11px;mix-blend-mode:difference;color:white;">鉁?/span>';
      }}
    }},

    // 鈹€鈹€ 鐢荤瑪澶у皬 鈹€鈹€
    setBrushSize: function(size) {{
      _brushSize = size;
      if (_canvas) _canvas.freeDrawingBrush.width = size;
    }},

    // 鈹€鈹€ 鎾ら攢鏈€鍚庝竴绗?鈹€鈹€
    undo: function() {{
      if (!_canvas) return;
      var objs = _canvas.getObjects();
      for (var i = objs.length - 1; i >= 0; i--) {{
        if (objs[i].type === 'path') {{
          _canvas.remove(objs[i]);
          _canvas.renderAll();
          if (_strokes.length > 0) _strokes.pop();
          if (_pathObjects.length > 0) _pathObjects.pop();
          window.InspireCanvas._renderLabelBadges();
          window.InspireCanvas.updateStrokeCount();
          window.InspireCanvas.renderLayerPanel();
          if (_strokes.length > 0) {{
            window.InspireCanvas.scheduleAnalysis();
          }} else {{
            window.InspireCanvas.showIdle();
          }}
          return;
        }}
      }}
    }},

    // 鈹€鈹€ 娓呴櫎鍏ㄩ儴 鈹€鈹€
    clearAll: function() {{
      if (!_canvas) return;
      var toRemove = _canvas.getObjects().filter(function(o) {{ return o.type === 'path'; }});
      toRemove.forEach(function(o) {{ _canvas.remove(o); }});
      _canvas.renderAll();
      _strokes = [];
      _pathObjects = [];
      _selectedStrokeIds = [];
      _undoStack = [];
      _lastResult = null;
      _lastSceneIntent = null;
      document.querySelectorAll('.stroke-icon-badge,.user-label-badge').forEach(function(el) {{
        if (el.parentNode) el.parentNode.removeChild(el);
      }});
      window.InspireCanvas._hideAnnotationPanel();
      window.InspireCanvas.updateStrokeCount();
      window.InspireCanvas.renderLayerPanel();
      window.InspireCanvas.showIdle();
    }},

    // 鈹€鈹€ 寤惰繜鍒嗘瀽锛堝仠绗斿悗 0.8s锛夆攢鈹€
    scheduleAnalysis: function() {{
      if (_analysisTimer) clearTimeout(_analysisTimer);
      window.InspireCanvas.showAnalyzing();
      _analysisTimer = setTimeout(function() {{
        window.InspireCanvas.analyze();
      }}, 800);
    }},

    // 鈹€鈹€ 鎵ц鍒嗘瀽锛堜笁灞傛劅鐭ュ紩鎿庯級鈹€鈹€
    analyze: function() {{
      if (_strokes.length === 0) {{ window.InspireCanvas.showIdle(); return; }}
      var cw = _canvas ? _canvas.getWidth() : 440;
      var ch = _canvas ? _canvas.getHeight() : 320;

      // 绗竴灞傦細鍗曠瑪璇嗗埆
      var result = window.SketchAnalyzer.analyzeStrokes(_strokes, cw, ch);
      _lastResult = result;

      // 绗簩灞傦細缁勫悎璇箟
      var sceneIntent = window.SketchComposer.compose(result, cw, ch);
      _lastSceneIntent = sceneIntent;

      // 浼樺厛灞曠ず缁勫悎璇箟鍙欎簨锛涜嫢鏈夊叿浣撳厓绱犱篃鍚屾灞曠ず
      window.InspireCanvas.renderResult(result, sceneIntent);
      window.InspireCanvas.updateStrokeCount();
    }},

    // 鈹€鈹€ 娓叉煋缁撴灉鍒?DOM 鈹€鈹€
    renderResult: function(result, sceneIntent) {{
      var area = document.getElementById('inspire-result-area');
      if (!area) return;
      var labeledCount = _strokes.filter(function(s) {{ return !!s.userLabel; }}).length;
      var labeledHint = labeledCount > 0
        ? '<div style="font-size:11px;color:#7c3aed;font-weight:600;margin-bottom:6px;">宸查噰鐢?' + labeledCount + ' 涓敤鎴锋爣娉ㄧ瑪鐢伙紝浼樺厛瑕嗙洊鑷姩璇嗗埆</div>'
        : '';

      // 缁勫悎璇箟鍙欎簨锛堜紭鍏堢骇鏈€楂橈紝鏈夋槑纭剰鍥炬椂鏄剧ず锛?      var hasPatterns = sceneIntent && sceneIntent.spatialPatterns && sceneIntent.spatialPatterns.length > 0;

      if (hasPatterns) {{
        var displayText = window.SketchComposer.buildDisplayText(sceneIntent);
        area.className = 'inspire-result-area inspire-result-composer';
        var html = '<div>';
        html += labeledHint;
        html += '<div style="font-size:12px;font-weight:600;color:#1e40af;margin-bottom:6px;">' + displayText + '</div>';

        if (result.type === 'element' && result.results && result.results.length > 0) {{
          html += '<div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:4px;">';
          result.results.forEach(function(el) {{
            var conf = Math.round(el.confidence * 100);
            var cls = el.confidence >= 0.78 ? 'elem-tag high-confidence' : 'elem-tag';
            var source = el.source === 'user' ? '鎵嬪姩鏍囨敞' : '鑷姩璇嗗埆';
            html += '<span class="' + cls + '">' + el.icon + ' ' + el.elemName;
            html += ' <span style="opacity:0.75;font-size:10px;color:' + (el.source === 'user' ? '#7c3aed' : 'inherit') + ';">' + source + '</span>';
            html += ' <span style="opacity:0.55;font-size:10px;">' + conf + '%</span></span>';
          }});
          html += '</div>';
        }}
        html += '</div>';
        area.innerHTML = html;
        return;
      }}

      if (result.type === 'element' && result.results && result.results.length > 0) {{
        area.className = 'inspire-result-area inspire-result-element';
        var html = '<div style="display:flex;align-items:flex-start;gap:10px;flex-wrap:wrap;">';
        html += '<span style="font-size:12px;font-weight:600;color:#1B4332;margin-bottom:4px;width:100%;">';
        html += '鉁?璇嗗埆鍒颁互涓嬪厓绱狅紝灏嗕负浣犺瀺鍚堝埌鐢婚潰涓細</span>';
        html += labeledHint;
        result.results.forEach(function(el) {{
          var conf = Math.round(el.confidence * 100);
          var cls = el.confidence >= 0.78 ? 'elem-tag high-confidence' : 'elem-tag';
          var source = el.source === 'user' ? '鎵嬪姩鏍囨敞' : '鑷姩璇嗗埆';
          html += '<span class="' + cls + '">' + el.icon + ' ' + el.elemName;
          html += ' <span style="opacity:0.75;font-size:10px;color:' + (el.source === 'user' ? '#7c3aed' : 'inherit') + ';">' + source + '</span>';
          html += ' <span style="opacity:0.55;font-size:10px;">' + conf + '%</span></span>';
        }});
        html += '</div>';
        area.innerHTML = html;
      }} else if (result.type === 'mood' && result.moodParams) {{
        var mp = result.moodParams;
        area.className = 'inspire-result-area inspire-result-mood';
        var moodEmoji = mp.moodLabel ? mp.moodLabel.emoji : '鉁?;
        var moodText  = mp.moodLabel ? mp.moodLabel.label : '鑷敱鍙戞暎';
        var moodColor = mp.moodLabel ? mp.moodLabel.color : '#9B8FD4';
        var html = '<div>';
        html += labeledHint;
        html += '<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">';
        html += '<span style="font-size:12px;font-weight:600;color:#92400e;">鉁?鎰熺煡鍒颁綘鐨勫垱浣滄儏缁細</span>';
        html += '<span style="font-size:13px;font-weight:700;color:' + moodColor + ';">' + moodEmoji + ' ' + moodText + '</span>';
        html += '</div>';
        html += window.InspireCanvas._moodBar('缁挎剰', mp.green);
        html += window.InspireCanvas._moodBar('娲诲姏', mp.vitality);
        html += window.InspireCanvas._moodBar('鏆栧害', mp.light);
        html += window.InspireCanvas._moodBar('浜烘枃', mp.urban);
        html += '</div>';
        area.innerHTML = html;
      }} else {{
        window.InspireCanvas.showIdle();
      }}
    }},

    _moodBar: function(label, val) {{
      return '<div class="mood-bar-row">' +
        '<span class="mood-bar-label">' + label + '</span>' +
        '<div class="mood-bar-track"><div class="mood-bar-fill" style="width:' + val + '%;"></div></div>' +
        '<span style="font-size:10px;color:#6B7280;width:26px;text-align:right;">' + Math.round(val) + '</span>' +
        '</div>';
    }},

    showIdle: function() {{
      var area = document.getElementById('inspire-result-area');
      if (!area) return;
      area.className = 'inspire-result-area inspire-result-idle';
      area.innerHTML = '<div style="display:flex;align-items:center;gap:8px;">' +
        '<span style="font-size:18px;">馃帹</span>' +
        '<span style="font-size:12px;color:#6B7280;font-weight:300;">' +
        '鍦ㄧ敾甯冧笂鐢诲嚑绗旓紝AI 灏嗚瘑鍒綘鐨勬剰鍥惧苟鐢熸垚鏀归€犳晥鏋?/span></div>';
    }},

    showAnalyzing: function() {{
      var area = document.getElementById('inspire-result-area');
      if (!area) return;
      area.className = 'inspire-result-area inspire-result-analyzing';
      area.innerHTML = '<div style="display:flex;align-items:center;gap:8px;">' +
        '<span style="font-size:13px;">馃攳</span>' +
        '<span style="font-size:12px;color:#2D6A4F;font-weight:500;">姝ｅ湪鍒嗘瀽绗旇抗...</span></div>';
    }},

    updateStrokeCount: function() {{
      var el = document.getElementById('inspire-stroke-count');
      if (el) el.textContent = '宸茬粯鍒?' + _strokes.length + ' 绗?;
    }},

    // 鈹€鈹€ 鍥惧眰闈㈡澘 鈹€鈹€
    toggleLayerPanel: function() {{
      var panel = document.getElementById('layer-panel');
      var btn = document.getElementById('layer-toggle-btn');
      if (!panel) return;
      var visible = panel.classList.toggle('visible');
      if (btn) btn.classList.toggle('active', visible);
      if (visible) window.InspireCanvas.renderLayerPanel();
    }},

    _generateThumbnail: function(pathObj) {{
      if (!pathObj) return '';
      try {{
        var bounds = pathObj.getBoundingRect();
        if (!bounds || bounds.width < 1 || bounds.height < 1) return '';
        var tmpCanvas = document.createElement('canvas');
        var size = 36;
        tmpCanvas.width = size;
        tmpCanvas.height = size;
        var ctx = tmpCanvas.getContext('2d');
        ctx.fillStyle = '#F0F7F4';
        ctx.fillRect(0, 0, size, size);
        var scale = Math.min((size - 8) / bounds.width, (size - 8) / bounds.height);
        ctx.translate(size / 2, size / 2);
        ctx.scale(scale, scale);
        ctx.translate(-(bounds.left + bounds.width / 2), -(bounds.top + bounds.height / 2));
        pathObj.render(ctx);
        return tmpCanvas.toDataURL();
      }} catch (e) {{ return ''; }}
    }},

    renderLayerPanel: function() {{
      var panel = document.getElementById('layer-panel');
      if (!panel || !panel.classList.contains('visible')) return;
      if (_strokes.length === 0) {{
        panel.innerHTML = '<div class="layer-empty">鏆傛棤绗旂敾鍥惧眰</div>';
        return;
      }}
      var html = '';
      for (var i = _strokes.length - 1; i >= 0; i--) {{
        var s = _strokes[i];
        var isSelected = _selectedStrokeIds.indexOf(s.strokeId) >= 0;
        var thumb = window.InspireCanvas._generateThumbnail(_pathObjects[i]);
        var label = s.userLabel || s.autoLabel || ('绗旂敾 ' + (i + 1));
        var displayLabel = label.length > 6 ? label.substring(0, 6) + '鈥? : label;
        html += '<div class="layer-item' + (isSelected ? ' selected' : '') + '" onclick="InspireCanvas.selectFromLayer(\\\'' + s.strokeId + '\\\')">';
        html += '<span class="layer-index">' + (i + 1) + '</span>';
        if (thumb) {{
          html += '<img class="layer-thumb" src="' + thumb + '">';
        }} else {{
          html += '<div class="layer-thumb"></div>';
        }}
        html += '<div class="layer-info">';
        html += '<div class="layer-info-name">' + displayLabel + '</div>';
        html += '<div class="layer-info-meta">';
        html += '<div class="layer-color-dot" style="background:' + (s.color || '#2D6A4F') + ';"></div>';
        html += '<span>' + (s.shapeType || 'free') + '</span>';
        html += '</div></div>';
        html += '<div class="layer-actions">';
        html += '<button class="layer-act-btn" onclick="event.stopPropagation();InspireCanvas.copyLayer(' + i + ');">澶嶅埗</button>';
        html += '<button class="layer-act-btn del" onclick="event.stopPropagation();InspireCanvas.deleteLayer(' + i + ');">鍒犻櫎</button>';
        html += '</div></div>';
      }}
      panel.innerHTML = html;
    }},

    _scrollLayerPanelToSelected: function(strokeId) {{
      var panel = document.getElementById('layer-panel');
      if (!panel || !panel.classList.contains('visible')) return;
      var items = panel.querySelectorAll('.layer-item.selected');
      if (items.length === 0) return;
      var item = items[0];
      var panelRect = panel.getBoundingClientRect();
      var itemRect = item.getBoundingClientRect();
      if (itemRect.top < panelRect.top || itemRect.bottom > panelRect.bottom) {{
        item.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
      }}
    }},

    selectFromLayer: function(strokeId) {{
      _selectedStrokeIds = [strokeId];
      if (_mode !== 'select') {{
        window.InspireCanvas.setMode('select');
      }}
      window.InspireCanvas._updateSelectionHighlight();
      window.InspireCanvas._showAnnotationPanel();
      window.InspireCanvas.renderLayerPanel();
    }},

    deleteLayer: function(idx) {{
      if (idx < 0 || idx >= _strokes.length) return;
      var path = _pathObjects[idx];
      var stroke = _strokes[idx];
      window.InspireCanvas._pushUndo({{ type:'delete', index: idx, path: path, stroke: stroke }});
      if (path) _canvas.remove(path);
      _pathObjects.splice(idx, 1);
      _strokes.splice(idx, 1);
      _selectedStrokeIds = [];
      _canvas.discardActiveObject();
      _canvas.renderAll();
      window.InspireCanvas._removeSelectionBoxes();
      window.InspireCanvas._hideAnnotationPanel();
      window.InspireCanvas._renderLabelBadges();
      window.InspireCanvas.updateStrokeCount();
      window.InspireCanvas.renderLayerPanel();
      if (_strokes.length > 0) {{
        window.InspireCanvas.scheduleAnalysis();
      }} else {{
        window.InspireCanvas.showIdle();
      }}
    }},

    copyLayer: function(idx) {{
      if (idx < 0 || idx >= _strokes.length || !_canvas) return;
      var srcStroke = JSON.parse(JSON.stringify(_strokes[idx]));
      var srcPath = _pathObjects[idx];
      if (!srcPath || !srcStroke) return;
      srcPath.clone(function(cloned) {{
        cloned.set({{ left: (cloned.left || 0) + 20, top: (cloned.top || 0) + 20, selectable: false, evented: false }});
        _canvas.add(cloned);
        var pts = window.SketchAnalyzer.extractPathPoints(cloned);
        if (pts.length > 0) {{
          _strokeIdCounter++;
          var newStrokeId = 'sk_' + _strokeIdCounter;
          var newStroke = {{
            pts: pts,
            color: srcStroke.color,
            strokeId: newStrokeId,
            createdAt: Date.now(),
            shapeType: srcStroke.shapeType,
            zone: srcStroke.zone,
            autoLabel: srcStroke.autoLabel,
            autoConfidence: srcStroke.autoConfidence,
            userLabel: srcStroke.userLabel,
            source: srcStroke.source,
            groupId: null,
            interactionRound: _interactionRound,
            editHistory: ['copied'],
          }};
          var insertIdx = idx + 1;
          _strokes.splice(insertIdx, 0, newStroke);
          _pathObjects.splice(insertIdx, 0, cloned);
          window.InspireCanvas._pushUndo({{ type:'copy', indices: [insertIdx] }});
          _selectedStrokeIds = [newStrokeId];
          window.InspireCanvas._updateSelectionHighlight();
          window.InspireCanvas._renderLabelBadges();
          window.InspireCanvas.updateStrokeCount();
          window.InspireCanvas.renderLayerPanel();
          window.InspireCanvas.scheduleAnalysis();
        }}
      }});
    }},

    _advanceRound: function() {{
      _interactionRound++;
    }},

    // 鈹€鈹€ 鑾峰彇鎻愪氦鏁版嵁锛堝惈 SceneIntent锛夆攢鈹€
    getSubmitData: function() {{
      if (!_lastResult) return JSON.stringify(null);
      var cw = _canvas ? _canvas.getWidth() : 440;
      var ch = _canvas ? _canvas.getHeight() : 320;

      var strokeLog = [];
      var annotationMap = {{}};

      _strokes.forEach(function(s, idx) {{
        var bounds = _getPathBounds(idx);
        var minX, maxX, minY, maxY;
        if (bounds) {{
          minX = bounds.minX; maxX = bounds.maxX;
          minY = bounds.minY; maxY = bounds.maxY;
        }} else {{
          var xs = s.pts.map(function(p) {{ return p.x; }});
          var ys = s.pts.map(function(p) {{ return p.y; }});
          minX = Math.min.apply(null, xs); maxX = Math.max.apply(null, xs);
          minY = Math.min.apply(null, ys); maxY = Math.max.apply(null, ys);
        }}
        var xPct = Math.round(((minX + maxX) / 2 / cw) * 1000) / 10;
        var yPct = Math.round(((minY + maxY) / 2 / ch) * 1000) / 10;
        var bw = Math.round(((maxX - minX) / cw) * 1000) / 10;
        var bh = Math.round(((maxY - minY) / ch) * 1000) / 10;
        var ar = Math.round(((maxX - minX) / ((maxY - minY) || 1)) * 100) / 100;

        strokeLog.push({{
          strokeId: s.strokeId,
          shapeType: s.shapeType,
          zone: s.zone,
          autoLabel: s.autoLabel,
          autoConfidence: s.autoConfidence,
          userLabel: s.userLabel,
          source: s.source,
          groupId: s.groupId,
          interactionRound: s.interactionRound,
          color: s.color,
          createdAt: s.createdAt,
          editHistory: s.editHistory,
          x: xPct, y: yPct, bboxW: bw, bboxH: bh, aspectRatio: ar,
        }});

        if (s.userLabel && s.groupId) {{
          if (!annotationMap[s.groupId]) {{
            annotationMap[s.groupId] = {{
              userLabel: s.userLabel,
              groupId: s.groupId,
              strokeIds: [],
              minX: minX, minY: minY, maxX: maxX, maxY: maxY,
              color: s.color, shapeType: s.shapeType,
            }};
          }} else {{
            var g = annotationMap[s.groupId];
            if (minX < g.minX) g.minX = minX;
            if (minY < g.minY) g.minY = minY;
            if (maxX > g.maxX) g.maxX = maxX;
            if (maxY > g.maxY) g.maxY = maxY;
          }}
          annotationMap[s.groupId].strokeIds.push(s.strokeId);
        }}
      }});

      var userAnnotations = [];
      Object.keys(annotationMap).forEach(function(gid) {{
        var g = annotationMap[gid];
        var cx = (g.minX + g.maxX) / 2, cy = (g.minY + g.maxY) / 2;
        var w = g.maxX - g.minX, h = g.maxY - g.minY;
        userAnnotations.push({{
          userLabel: g.userLabel,
          groupId: g.groupId,
          isGroup: g.strokeIds.length > 1,
          strokeIds: g.strokeIds,
          x: Math.round((cx / cw) * 1000) / 10,
          y: Math.round((cy / ch) * 1000) / 10,
          bboxW: Math.round((w / cw) * 1000) / 10,
          bboxH: Math.round((h / ch) * 1000) / 10,
          aspectRatio: Math.round((w / (h || 1)) * 100) / 100,
          color: g.color,
          shapeType: g.shapeType,
        }});
      }});

      return JSON.stringify({{
        type: _lastResult.type,
        results: _lastResult.results || [],
        moodParams: _lastResult.moodParams || null,
        strokeCount: _strokes.length,
        sceneIntent: _lastSceneIntent || null,
        interactionRound: _interactionRound,
        strokeLog: strokeLog,
        userAnnotations: userAnnotations,
      }});
    }},

    getCanvasDataURL: function() {{
      if (!_canvas) return '';
      try {{
        var hadSelection = _selectedStrokeIds.length > 0;
        window.InspireCanvas._removeSelectionBoxes();
        _canvas.isDrawingMode = false;
        _canvas.discardActiveObject();
        _canvas.renderAll();
        var url = _canvas.toDataURL({{ format: 'png' }});
        _canvas.isDrawingMode = (_mode === 'draw');
        if (hadSelection && _mode === 'select') window.InspireCanvas._updateSelectionHighlight();
        return url;
      }} catch(e) {{
        _canvas.isDrawingMode = (_mode === 'draw');
        return 'ERROR:' + e.message;
      }}
    }},

    // 鈹€鈹€ 搴忓垪鍖栫敾甯冭矾寰勶紙鐢ㄤ簬鎸佷箙鍖栦繚瀛橈級鈹€鈹€
    getPathsJSON: function() {{
      if (!_canvas) return '[]';
      var selSet = new Set(_selectionBoxObjects);
      var paths = _canvas.getObjects().filter(function(o) {{ return o.type === 'path' && !selSet.has(o); }});
      return JSON.stringify(paths.map(function(p) {{ return p.toObject(); }}));
    }},

    // 鈹€鈹€ 浠?JSON 鎭㈠鐢诲竷璺緞锛堢敤浜庣户缁紪杈戯級鈹€鈹€
    restorePaths: function(jsonStr) {{
      if (!_canvas || !jsonStr) return;
      try {{
        var pathDataList = JSON.parse(jsonStr);
      }} catch(e) {{ return; }}
      if (!pathDataList || !pathDataList.length) return;

      fabric.util.enlivenObjects(pathDataList, function(objs) {{
        objs.forEach(function(obj) {{
          obj.set({{ selectable: false, evented: false }});
          var pts = (window.SketchAnalyzer && window.SketchAnalyzer.extractPathPoints)
            ? window.SketchAnalyzer.extractPathPoints(obj) : [];
          if (!window.InspireCanvas._isValidStroke(pts)) return;
          _canvas.add(obj);
          _strokeIdCounter++;
          var cw = _canvas.getWidth(), ch = _canvas.getHeight();
          var f = window.SketchAnalyzer._extractFeatures(pts);
          var yPct = f ? (f.centerY / ch) * 100 : 50;
          var zone = f ? window.SketchAnalyzer._getZone(yPct) : 'midground';
          var shapeType = (f && pts) ? window.SketchAnalyzer._classifyShape(f, pts, cw) : 'free';
          var match = window.SketchAnalyzer.quickMatchStroke(pts, cw, ch, obj.stroke || _drawColor);
          _strokes.push({{
            pts: pts,
            color: obj.stroke || _drawColor,
            strokeId: 'sk_' + _strokeIdCounter,
            createdAt: Date.now(),
            shapeType: shapeType,
            zone: zone,
            autoLabel: match ? match.elemName : '',
            autoConfidence: match ? match.confidence : 0,
            userLabel: null,
            source: 'auto',
            groupId: null,
            interactionRound: _interactionRound,
            editHistory: ['restored'],
          }});
          _pathObjects.push(obj);
        }});
        _canvas.renderAll();
        window.InspireCanvas.updateStrokeCount();
        if (_strokes.length > 0) {{
          window.InspireCanvas.analyze();
        }}
      }});
    }},
  }};

  document.addEventListener('DOMContentLoaded', function() {{
    setTimeout(function() {{ window.InspireCanvas.init(); }}, 50);
  }});
  setTimeout(function() {{
    if (!window._inspireInited) {{
      window._inspireInited = true;
      window.InspireCanvas.init();
    }}
  }}, 300);

  // 鎭㈠宸蹭繚瀛樼殑鐢诲竷璺緞鐘舵€?  var _canvasJsonUrl = {json.dumps(canvas_json_url)};
  if (_canvasJsonUrl) {{
    var _restoreAttempt = 0;
    function _tryRestore() {{
      _restoreAttempt++;
      if (_restoreAttempt > 30) return;
      if (!_canvas) {{
        setTimeout(_tryRestore, 200);
        return;
      }}
      fetch(_canvasJsonUrl).then(function(r) {{ return r.text(); }}).then(function(jsonStr) {{
        if (jsonStr && jsonStr !== '[]') {{
          window.InspireCanvas.restorePaths(jsonStr);
        }}
      }}).catch(function() {{}});
    }}
    setTimeout(_tryRestore, 800);
  }}
}})();
</script>''')

        # 鈹€鈹€ 椤甸潰甯冨眬 鈹€鈹€
        with ui.column().classes('mobile-page light-page').style('gap:0'):
            bottom_nav(light=True)
            with ui.row().style(LIGHT_TOP_BAR_STYLE + 'padding-right:60px;'):
                back_url = f'/result?sid={sid}&back=records' if back == 'result' else (
                    '/records' if back == 'records' else f'/mode-select?sid={sid}'
                )
                ui.button(
                    icon='arrow_back',
                    on_click=lambda: smooth_navigate(back_url),
                ).props('flat round dense').style(f'color:{COLORS["primary_dark"]}')
                ui.label('鐏垫劅鍒涙兂').style(
                    f'font-size:17px;font-weight:600;margin-left:4px;flex:1;color:{COLORS["primary_dark"]}'
                )
                ui.button(
                    '娓呴櫎',
                    on_click=lambda: ui.run_javascript('InspireCanvas.clearAll()'),
                ).props('flat dense no-caps').style(
                    f'color:{COLORS["error"]} !important;font-size:13px;font-weight:500'
                )
                save_btn = ui.button(
                    '淇濆瓨',
                    on_click=lambda: save_draft(),
                ).props('flat dense no-caps').style(
                    'color:#2F7B58 !important;font-size:13px;font-weight:600'
                )

            with ui.column().style('padding:16px 20px 0;gap:12px;width:100%'):

                # 鎵€鏈夋彁绀哄崱鐗囧畾涔夛紙姣忔闅忔満閫?7 寮犲睍绀猴級
                all_hint_cards = [
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#52B788\');" title="璇曡瘯鐢诲渾">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<circle cx="26" cy="17" r="11" fill="none" stroke="#52B788" stroke-width="2.5" stroke-linecap="round"/>'
                     '</svg><span>鐢诲渾 鈫?澶ф爲</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#2D6A4F\');" title="璇曡瘯鐢荤珫绾?>'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<line x1="26" y1="5" x2="26" y2="33" stroke="#2D6A4F" stroke-width="2.5" stroke-linecap="round"/>'
                     '</svg><span>鐢荤珫绾?鈫?鏍戝共</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#3A86FF\');" title="璇曡瘯鐢绘尝娴?>'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M4,22 Q13,10 22,22 Q31,34 40,22 Q45,16 48,20" fill="none" stroke="#3A86FF" stroke-width="2.5" stroke-linecap="round"/>'
                     '</svg><span>鐢绘尝娴?鈫?灏忔邯</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#1A1A2E\');" title="璇曡瘯鐢诲皬寮х嚎">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<line x1="8" y1="14" x2="16" y2="10" stroke="#1A1A2E" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="16" y1="10" x2="24" y2="14" stroke="#1A1A2E" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="28" y1="10" x2="36" y2="6" stroke="#1A1A2E" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="36" y1="6" x2="44" y2="10" stroke="#1A1A2E" stroke-width="2" stroke-linecap="round"/>'
                     '</svg><span>鐢荤偣/寮?鈫?椋為笩</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#3A86FF\');" title="璇曡瘯鐢婚棴鍚堝舰">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<ellipse cx="26" cy="22" rx="18" ry="10" fill="rgba(58,134,255,0.12)" stroke="#3A86FF" stroke-width="2.2"/>'
                     '</svg><span>鐢婚棴鍚堝舰 鈫?姹犲</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#E76F51\');" title="璇曡瘯鐢绘í绾?>'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M4,16 Q13,12 22,16 Q31,20 40,16 Q44,14 48,16" fill="none" stroke="#E76F51" stroke-width="3" stroke-linecap="round"/>'
                     '<path d="M4,24 Q14,20 24,24 Q34,28 48,24" fill="none" stroke="#E76F51" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
                     '</svg><span>鐢绘í绾?鈫?鑽夊潽</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#2D6A4F\');" title="璇曡瘯鐢婚敮榻跨嚎">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<polyline points="4,28 14,10 24,28 34,10 44,28" fill="none" stroke="#2D6A4F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
                     '</svg><span>鐢婚敮榻?鈫?杩滃北</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#E76F51\');" title="璇曡瘯鐢昏灪鏃?>'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M26,19 C26,15 30,12 33,15 C36,18 33,24 28,24 C22,24 18,18 20,13 C22,8 30,6 35,10" fill="none" stroke="#E76F51" stroke-width="2.2" stroke-linecap="round"/>'
                     '</svg><span>鐢昏灪鏃?鈫?鑺辨湹</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#8B5CF6\');" title="璇曡瘯鍦ㄩ《閮ㄧ敾寮х嚎">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M6,24 Q16,8 26,14 Q36,20 46,10" fill="none" stroke="#8B5CF6" stroke-width="2.5" stroke-linecap="round"/>'
                     '<path d="M10,30 Q22,16 34,22 Q42,26 48,18" fill="none" stroke="#8B5CF6" stroke-width="2" stroke-linecap="round" opacity="0.4"/>'
                     '</svg><span>鐢诲姬绾?鈫?浜戞湹</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#52B788\');" title="璇曡瘯娑傚ぇ闈㈢Н">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M4,14 Q14,10 26,14 Q38,18 48,12" fill="none" stroke="#52B788" stroke-width="3" stroke-linecap="round"/>'
                     '<path d="M4,20 Q16,16 28,20 Q40,24 48,18" fill="none" stroke="#52B788" stroke-width="3" stroke-linecap="round" opacity="0.6"/>'
                     '<path d="M4,26 Q18,22 30,26 Q42,30 48,24" fill="none" stroke="#52B788" stroke-width="3" stroke-linecap="round" opacity="0.3"/>'
                     '</svg><span>娑傛弧 鈫?鑽夊湴</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#E76F51\');" title="鐢荤煭灏忕嚎娈典唬琛ㄨ姳鏈?>'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<circle cx="12" cy="14" r="4" fill="none" stroke="#E76F51" stroke-width="1.5"/>'
                     '<circle cx="26" cy="10" r="5" fill="none" stroke="#E76F51" stroke-width="1.5"/>'
                     '<circle cx="40" cy="16" r="4" fill="none" stroke="#E76F51" stroke-width="1.5"/>'
                     '<line x1="12" y1="18" x2="12" y2="30" stroke="#52B788" stroke-width="1.5"/>'
                     '<line x1="26" y1="15" x2="26" y2="30" stroke="#52B788" stroke-width="1.5"/>'
                     '<line x1="40" y1="20" x2="40" y2="30" stroke="#52B788" stroke-width="1.5"/>'
                     '</svg><span>灏忓渾+绔栫嚎 鈫?鑺变笡</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#2D6A4F\');" title="鍦?绔栫嚎=瀹屾暣鐨勬爲">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<circle cx="26" cy="13" r="9" fill="rgba(82,183,136,0.15)" stroke="#52B788" stroke-width="2"/>'
                     '<line x1="26" y1="22" x2="26" y2="35" stroke="#2D6A4F" stroke-width="2.5" stroke-linecap="round"/>'
                     '</svg><span>鍦?绔栫嚎 鈫?鏍?/span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#3A86FF\');" title="娉㈡氮+妞渾=婧竟姹犲">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M2,16 Q12,8 22,16 Q30,22 38,16" fill="none" stroke="#3A86FF" stroke-width="2" stroke-linecap="round"/>'
                     '<ellipse cx="26" cy="28" rx="14" ry="7" fill="rgba(58,134,255,0.12)" stroke="#3A86FF" stroke-width="1.8"/>'
                     '</svg><span>娉㈡氮+鍦?鈫?婧</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#8B5CF6\');" title="澶氭潯绔栫嚎=鏍戞灄">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<line x1="10" y1="8" x2="10" y2="34" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="22" y1="5" x2="22" y2="34" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="34" y1="10" x2="34" y2="34" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round"/>'
                     '<line x1="44" y1="7" x2="44" y2="34" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round"/>'
                     '</svg><span>澶氱珫绾?鈫?鏍戞灄</span></div>'),
                    ('<div class="hint-card" onclick="InspireCanvas.setColor(\'#E76F51\');" title="妯嚎+绔栫嚎=灏忓緞璺伅">'
                     '<svg width="52" height="38" viewBox="0 0 52 38">'
                     '<path d="M4,28 Q16,22 28,26 Q40,30 48,24" fill="none" stroke="#8B5CF6" stroke-width="2.2" stroke-linecap="round"/>'
                     '<line x1="36" y1="8" x2="36" y2="24" stroke="#1A1A2E" stroke-width="2" stroke-linecap="round"/>'
                     '<circle cx="36" cy="7" r="3" fill="rgba(233,196,106,0.4)" stroke="#E9C46A" stroke-width="1.5"/>'
                     '</svg><span>璺?绔栫嚎 鈫?璺伅</span></div>'),
                ]
                selected_cards = random.sample(all_hint_cards, min(7, len(all_hint_cards)))
                hint_cards_html = ''.join(selected_cards)

                ui.html(f'''
                    <div id="inspire-hint-toggle" onclick="
                        var body = document.getElementById('inspire-hint-body');
                        var arrow = document.getElementById('inspire-hint-arrow');
                        if (body.style.display === 'none') {{
                            body.style.display = 'block';
                            arrow.style.transform = 'rotate(180deg)';
                        }} else {{
                            body.style.display = 'none';
                            arrow.style.transform = 'rotate(0deg)';
                        }}
                    " style="
                        background:rgba(45,106,79,0.06);border-radius:14px;
                        padding:10px 14px;border:1px solid rgba(45,106,79,0.1);
                        cursor:pointer;user-select:none;
                    ">
                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <span style="font-size:13px;font-weight:600;color:{COLORS['primary_dark']};">鉁?鍦ㄧ敾甯冧笂闅忔剰鐢诲嚑绗?/span>
                            <span id="inspire-hint-arrow" style="font-size:12px;color:{COLORS['text_secondary']};transition:transform 0.2s;">鈻?/span>
                        </div>
                        <div style="font-size:11px;color:{COLORS['text_secondary']};margin-top:4px;">鐐瑰嚮鏌ョ湅鐏垫劅鎻愮ず</div>
                        <div id="inspire-hint-body" style="display:none;margin-top:6px;">
                            <div style="font-size:10px;color:{COLORS['text_secondary']};font-weight:300;margin-bottom:6px;letter-spacing:0.3px;">
                                鐢诲湪涓婃柟 = 澶╃┖ 路 涓棿 = 妞嶈 路 涓嬫柟 = 鍦伴潰姘存櫙
                            </div>
                            <div class="hint-cards-row" style="flex-wrap:wrap;">{hint_cards_html}</div>
                        </div>
                    </div>
                ''', sanitize=False)

                with ui.element('div').style('position:relative;width:100%;'):
                    ui.html(
                        '<div id="inspire-canvas-wrapper">'
                        '<canvas id="inspire-canvas"></canvas>'
                        '</div>',
                        sanitize=False,
                    ).style('width:100%;')

                ui.html(
                    '<div style="display:flex;gap:6px;align-items:center;padding:4px 0 2px;">'
                    '<div id="mode-draw-btn" class="mode-switch-btn active" onclick="InspireCanvas.setMode(\'draw\')">鐢荤瑪</div>'
                    '<div id="mode-select-btn" class="mode-switch-btn" onclick="InspireCanvas.setMode(\'select\')">閫夋嫨鏍囨敞</div>'
                    '<div id="layer-toggle-btn" class="layer-toggle-btn" onclick="InspireCanvas.toggleLayerPanel()">鍥惧眰</div>'
                    '<div id="undo-btn" class="layer-toggle-btn" onclick="InspireCanvas.undo()" title="鎾ゅ洖">'
                    '<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 7h7a4 4 0 0 1 0 8H8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 4L3 7l3 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                    '</div>'
                    '<span style="font-size:10px;color:#9CA3AF;margin-left:auto;">閫夋嫨绗旂敾鍚庡彲杈撳叆鏂囧瓧鎻忚堪</span>'
                    '</div>',
                    sanitize=False,
                ).style('width:100%;')

                ui.html(
                    '<div id="layer-panel"></div>',
                    sanitize=False,
                ).style('width:100%;')

                ui.html(
                    '<div id="annotation-panel">'
                    '<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">'
                    '<span style="font-size:14px;">鉁?/span>'
                    '<span id="annotation-hint" style="font-size:12px;font-weight:600;color:#8B5CF6;">宸查€夋嫨 0 涓瑪鐢?/span>'
                    '</div>'
                    '<input id="annotation-input" type="text" placeholder="鎻忚堪浣犳兂瑕佺殑鍐呭锛屽锛氳寕瀵嗙殑闈掔豢鑹叉爲鏈? onkeydown="if(event.key===\'Enter\')InspireCanvas.confirmAnnotation();">'
                    '<div class="annotation-btn-row">'
                    '<button class="annotation-btn annotation-btn-cancel" onclick="InspireCanvas.cancelAnnotation();">鍙栨秷</button>'
                    '<button class="annotation-btn annotation-btn-confirm" onclick="InspireCanvas.confirmAnnotation();">纭鏍囨敞</button>'
                    '</div>'
                    '</div>',
                    sanitize=False,
                ).style('width:100%;')

                with ui.element('div').style(
                    'display:flex;gap:6px;align-items:center;padding:6px 0 2px;flex-wrap:nowrap;'
                ):
                    # 6 涓璁鹃鑹茬偣
                    colors = [
                        ('#2D6A4F', '娣辩豢'), ('#52B788', '娴呯豢'), ('#E76F51', '姗欑孩'),
                        ('#3A86FF', '钃濊壊'), ('#8B5CF6', '绱壊'), ('#1A1A2E', '榛戣壊'),
                    ]
                    for i, (color, label) in enumerate(colors):
                        selected = 'selected' if i == 0 else ''
                        ui.html(
                            f'<div class="color-dot {selected}" style="background:{color};" '
                            f'onclick="InspireCanvas.setColor(\'{color}\');"'
                            f'title="{label}"></div>',
                            sanitize=False,
                        ).style('display:inline-block;')

                    # 鑷畾涔夐鑹茬偣锛堝叏鑹茶氨 color picker锛?                    ui.html(
                        '<div style="position:relative;display:inline-block;">'
                        '  <input type="color" id="inspire-color-picker" value="#52B788"'
                        '    style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;"'
                        '    onchange="InspireCanvas.setCustomColor(this.value)">'
                        '  <div id="inspire-custom-color-dot"'
                        '    onclick="document.getElementById(\'inspire-color-picker\').click();"'
                        '    title="鑷畾涔夐鑹?>+</div>'
                        '</div>',
                        sanitize=False,
                    ).style('display:inline-block;')

                    ui.element('div').style('flex:1;')

                    # 鎾ら攢鎸夐挳
                    ui.html(
                        '<button class="sketch-tool-btn" onclick="InspireCanvas.undo();" title="鎾ら攢">鈫?/button>',
                        sanitize=False,
                    )

                    # 绗斿埛绮楃粏婊戞潌锛堟浛鎹㈠師 S/M/L 涓夋寜閽級
                    ui.html(
                        '<div class="brush-slider-row">'
                        '  <div class="brush-size-indicator" style="width:4px;height:4px;"></div>'
                        '  <input type="range" id="inspire-brush-slider"'
                        '    min="1" max="20" step="1" value="4"'
                        '    class="brush-range"'
                        '    oninput="InspireCanvas.setBrushSize(parseInt(this.value))">'
                        '  <div class="brush-size-indicator" style="width:12px;height:12px;"></div>'
                        '</div>',
                        sanitize=False,
                    )

                with ui.row().style(
                    'width:100%;justify-content:space-between;align-items:center;padding:2px 0;'
                ):
                    ui.html(
                        '<span id="inspire-stroke-count" '
                        'style="font-size:11px;color:#6B7280;">宸茬粯鍒?0 绗?/span>'
                    )
                    ui.label('鐢诲畬鍚庣郴缁熻嚜鍔ㄥ垎鏋?).style(
                        f'font-size:11px;color:{COLORS["text_secondary"]};font-weight:300;'
                    )

                ui.html(
                    '<div id="inspire-result-area" '
                    'class="inspire-result-area inspire-result-idle">'
                    '<div style="display:flex;align-items:center;gap:8px;">'
                    '<span style="font-size:18px;">馃帹</span>'
                    '<span style="font-size:12px;color:#6B7280;font-weight:300;">'
                    '鍦ㄧ敾甯冧笂鐢诲嚑绗旓紝AI 灏嗚瘑鍒綘鐨勬剰鍥惧苟鐢熸垚鏀归€犳晥鏋?
                    '</span></div></div>'
                ).style('width:100%;')

            with ui.column().style(
                'gap:8px;margin-top:auto;'
            ).classes('light-action-panel'):
                error_label = ui.label().style(
                    f'display:none;padding:10px 14px;background:{COLORS["error"]}10;'
                    f'border:1px solid {COLORS["error"]}30;border-radius:14px;'
                    f'font-size:13px;color:{COLORS["error"]};width:100%'
                )

                loading_row = ui.element('div').style('display:none;width:100%')
                with loading_row:
                    with ui.row().style('width:100%;align-items:center;gap:10px;padding:8px 0'):
                        ui.spinner('dots', size='sm', color=COLORS['primary'])
                        ui.label('AI 姝ｅ湪铻嶅悎浣犵殑鐏垫劅...').style(
                            f'font-size:14px;color:{COLORS["primary_dark"]};font-weight:500'
                        )

                gen_btn = ui.button(
                    '鉁?AI 鐢熸垚鏁堟灉鍥?,
                    on_click=lambda: generate_sketch(),
                ).props('no-caps unelevated').style(LIGHT_PRIMARY_BTN_STYLE)

        # 鈹€鈹€ 淇濆瓨鑽夌閫昏緫 鈹€鈹€
        _saving = False

        async def save_draft():
            nonlocal _saving
            if _saving:
                return
            _saving = True
            save_btn.disable()

            if not session:
                ui.notify('鏃犳晥鐨勪細璇?, type='warning')
                _saving = False
                save_btn.enable()
                return

            saved_anything = False

            # 鑾峰彇鍒嗘瀽鏁版嵁
            try:
                submit_json = await ui.run_javascript(
                    'InspireCanvas.getSubmitData()', timeout=5.0
                )
            except Exception:
                submit_json = None

            if submit_json and submit_json != 'null':
                try:
                    data = json.loads(submit_json)
                    if data:
                        if data.get('type') == 'element':
                            session.placed_elements = data.get('results', [])
                        elif data.get('type') == 'mood' and data.get('moodParams'):
                            mp = data['moodParams']
                            session.green_level = mp.get('green', 50)
                            session.urban_level = mp.get('urban', 50)
                            session.vitality_level = mp.get('vitality', 50)
                            session.light_warmth = mp.get('light', 50)
                        session.sketch_data = data
                except Exception:
                    pass

            # 淇濆瓨鐢诲竷璺緞 JSON锛堜紭鍏堬紝閫熷害蹇笖鏄仮澶嶇紪杈戠殑鍏抽敭鏁版嵁锛?            try:
                paths_json = await ui.run_javascript(
                    'InspireCanvas.getPathsJSON()', timeout=10.0
                )
                if paths_json and paths_json != '[]':
                    save_canvas_json(sid, paths_json)
                    saved_anything = True
            except Exception:
                pass

            # 淇濆瓨鐢诲竷蹇収
            try:
                canvas_data_url = await ui.run_javascript(
                    'InspireCanvas.getCanvasDataURL()', timeout=10.0
                )
                if canvas_data_url and not canvas_data_url.startswith('ERROR:'):
                    save_canvas_snapshot(sid, canvas_data_url)
            except Exception:
                pass

            if saved_anything:
                ui.notify('宸蹭繚瀛樿崏绋?鉁?, type='positive', position='top', timeout=2000)
            else:
                ui.notify('淇濆瓨澶辫触锛岃閲嶈瘯', type='negative')
            _saving = False
            save_btn.enable()

        # 鈹€鈹€ 鐢熸垚閫昏緫 鈹€鈹€
        async def generate_sketch():
            submit_json = await ui.run_javascript(
                'InspireCanvas.getSubmitData()', timeout=5.0
            )

            if not submit_json or submit_json == 'null':
                ui.notify('璇峰厛鍦ㄧ敾甯冧笂鐢诲嚑绗?, type='warning')
                return

            try:
                data = json.loads(submit_json)
            except Exception:
                ui.notify('鏁版嵁瑙ｆ瀽澶辫触锛岃閲嶈瘯', type='negative')
                return

            if not data:
                ui.notify('璇峰厛鍦ㄧ敾甯冧笂鐢诲嚑绗?, type='warning')
                return

            # 鎴彇鐢诲竷蹇収锛堝惈鍘熷浘 + 绗旇抗锛?            canvas_data_url = ''
            try:
                canvas_data_url = await ui.run_javascript(
                    'InspireCanvas.getCanvasDataURL()', timeout=10.0
                )
            except Exception:
                pass

            gen_btn.set_visibility(False)
            loading_row.style('display:block')
            error_label.style('display:none')

            if session:
                if data.get('type') == 'element':
                    session.placed_elements = data.get('results', [])
                elif data.get('type') == 'mood' and data.get('moodParams'):
                    mp = data['moodParams']
                    session.green_level = mp.get('green', 50)
                    session.urban_level = mp.get('urban', 50)
                    session.vitality_level = mp.get('vitality', 50)
                    session.light_warmth = mp.get('light', 50)
                session.generation_count = getattr(session, 'generation_count', 0) + 1
                session.sketch_data = data
                if canvas_data_url:
                    save_canvas_snapshot(sid, canvas_data_url)

            # 淇濆瓨鐢诲竷璺緞 JSON锛堢敤浜庡悗缁仮澶嶇紪杈戯級
            try:
                paths_json = await ui.run_javascript(
                    'InspireCanvas.getPathsJSON()', timeout=10.0
                )
                if paths_json and paths_json != '[]':
                    save_canvas_json(sid, paths_json)
            except Exception:
                pass

            try:
                from app.services.sd_service import generate_from_sketch
                result_bytes, used_prompt = await asyncio.to_thread(
                    generate_from_sketch,
                    session.uploaded_image_path if session else '',
                    data,
                )
                if session:
                    session.llm_prompt = used_prompt
                save_output(sid, result_bytes)
                await ui.run_javascript('InspireCanvas._advanceRound();', timeout=1.0)
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
