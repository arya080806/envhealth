/**
 * InspireCanvas — 灵感创想画布控制器。
 *
 * 负责手绘、自动识别、解释反馈、用户标注、研究数据序列化。
 */
window.InspireCanvas = (function () {
  'use strict';

  var canvas = null;
  var strokes = [];
  var paths = [];
  var undoStack = [];
  var selectedIndex = -1;
  var selectedIndices = [];
  var multiSelectMode = false;
  var drawColor = '#2D6A4F';
  var brushSize = 4;
  var analyzeTimer = null;
  var lastResult = null;
  var lastSceneIntent = null;
  var sessionId = '';
  var imageUrl = '';
  var restoreUrl = '';
  var strokeCounter = 0;
  var interactionRound = 1;
  var creativeLens = 'restorative';
  var aiAgency = 70;
  var layersVisible = true;
  var customColor = '#2D6A4F';
  var currentMode = 'draw';
  var isRestoringHistory = false;
  var inlineLabel = null;
  var skipNextSingleSelection = false;
  var isUpdatingSelection = false;

  var LENS_META = {
    restorative: {
      label: '疗愈自然',
      prompt: '优先营造恢复性环境：把用户画出的区域转化为清晰可见的自然介入，增加植被、水景、柔和光影、可停留感与心理安全感。',
    },
    playful: {
      label: '自由灵感',
      prompt: '鼓励更发散的空间创想：把手绘轨迹当作主要设计线索，沿笔触生成更大胆、更有探索感和野趣的自然场景。',
    },
    minimal: {
      label: '克制写实',
      prompt: '保持原图结构和真实可落地性，但仍要在笔触覆盖范围内做出可见、精细、写实的低干预更新。',
    },
  };

  function $(id) {
    return document.getElementById(id);
  }

  function normalizeHex(hex) {
    if (!hex || typeof hex !== 'string') return drawColor;
    var value = hex.trim();
    if (value.charAt(0) !== '#') value = '#' + value;
    if (/^#[0-9a-fA-F]{6}$/.test(value)) return value.toUpperCase();
    return drawColor;
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      }[ch];
    });
  }

  function cloneStroke(stroke) {
    return JSON.parse(JSON.stringify(stroke || {}));
  }

  function selectedIndexSet() {
    return selectedIndices.reduce(function (acc, idx) {
      acc[idx] = true;
      return acc;
    }, {});
  }

  function normalizeIndices(indices) {
    var seen = {};
    return (indices || [])
      .map(function (idx) { return Number(idx); })
      .filter(function (idx) {
        if (!Number.isInteger(idx) || idx < 0 || idx >= paths.length || seen[idx]) return false;
        seen[idx] = true;
        return true;
      })
      .sort(function (a, b) { return a - b; });
  }

  function currentSelectedIndices() {
    if (selectedIndices.length) return normalizeIndices(selectedIndices);
    return selectedIndex >= 0 ? normalizeIndices([selectedIndex]) : [];
  }

  function serializeObjectState(obj) {
    if (!obj) return null;
    return {
      left: obj.left,
      top: obj.top,
      scaleX: obj.scaleX,
      scaleY: obj.scaleY,
      angle: obj.angle,
      skewX: obj.skewX,
      skewY: obj.skewY,
      flipX: obj.flipX,
      flipY: obj.flipY,
    };
  }

  function applyObjectState(obj, state) {
    if (!obj || !state) return;
    obj.set({
      left: state.left,
      top: state.top,
      scaleX: state.scaleX,
      scaleY: state.scaleY,
      angle: state.angle,
      skewX: state.skewX || 0,
      skewY: state.skewY || 0,
      flipX: !!state.flipX,
      flipY: !!state.flipY,
    });
    obj.setCoords();
    if (canvas) canvas.requestRenderAll();
  }

  function preparePathObject(obj, selectable) {
    if (!obj) return obj;
    obj.selectable = !!selectable;
    obj.evented = !!selectable;
    obj.stroke = obj.stroke || drawColor;
    obj.strokeWidth = obj.strokeWidth || brushSize;
    obj.hasControls = true;
    obj.hasBorders = true;
    obj.cornerColor = '#2D6A4F';
    obj.cornerStrokeColor = '#ffffff';
    obj.cornerStyle = 'circle';
    obj.cornerSize = 12;
    obj.transparentCorners = false;
    return obj;
  }

  function removeInlineLabel() {
    var label = inlineLabel || $('inspire-inline-label');
    if (label) {
      label.style.display = 'none';
      label.textContent = '';
    }
    inlineLabel = label || null;
  }

  function inlineLabelText(stroke) {
    if (!stroke) return '';
    var label = stroke.userLabel || stroke.autoLabel || '待识别笔画';
    var confidence = Math.round((stroke.autoConfidence || 0) * 100);
    if (stroke.userLabel) return label;
    return label + (confidence > 0 ? ' ' + confidence + '%' : '');
  }

  function showInlineLabel(stroke, path) {
    if (!canvas || !stroke || !path) return;
    removeInlineLabel();
    var text = inlineLabelText(stroke);
    if (!text) return;
    var label = inlineLabel || $('inspire-inline-label');
    var wrap = $('inspire-canvas-wrapper');
    if (!label || !wrap) return;
    var rect = path.getBoundingRect ? path.getBoundingRect() : null;
    var x = rect ? rect.left + rect.width / 2 : path.left || 20;
    var y = rect ? rect.top - 12 : (path.top || 20) - 12;
    var maxLeft = Math.max(8, wrap.clientWidth - 128);
    var left = Math.max(8, Math.min(maxLeft, x - 56));
    var top = Math.max(8, y);
    label.textContent = text;
    label.style.left = left + 'px';
    label.style.top = top + 'px';
    label.style.display = 'block';
    inlineLabel = label;
  }

  function updateLayerButton() {
    var btn = $('layer-toggle-btn');
    if (btn) btn.classList.toggle('active', layersVisible);
  }

  function hasGroupedSelection(indices) {
    return normalizeIndices(indices || currentSelectedIndices()).some(function (idx) {
      return !!(strokes[idx] && strokes[idx].groupId);
    });
  }

  function updateSelectionControls() {
    var multiBtn = $('multi-select-btn');
    var groupBtn = $('group-selected-btn');
    var ungroupBtn = $('ungroup-selected-btn');
    var selectMode = currentMode === 'select';
    var selected = currentSelectedIndices();
    if (multiBtn) {
      multiBtn.disabled = !selectMode;
      multiBtn.classList.toggle('active', selectMode && multiSelectMode);
    }
    if (groupBtn) groupBtn.disabled = !selectMode || selected.length < 2;
    if (ungroupBtn) ungroupBtn.disabled = !selectMode || !hasGroupedSelection(selected);
  }

  function setSelectedIndices(indices, activate) {
    selectedIndices = normalizeIndices(indices);
    selectedIndex = selectedIndices.length ? selectedIndices[0] : -1;
    if (canvas && activate !== false) {
      isUpdatingSelection = true;
      canvas.discardActiveObject();
      var objects = selectedIndices.map(function (idx) { return paths[idx]; }).filter(Boolean);
      if (objects.length === 1) {
        canvas.setActiveObject(objects[0]);
      } else if (objects.length > 1 && window.fabric && fabric.ActiveSelection) {
        canvas.setActiveObject(new fabric.ActiveSelection(objects, { canvas: canvas }));
      }
      canvas.requestRenderAll();
      isUpdatingSelection = false;
    }
    updateSelectionControls();
  }

  function clearSelectionState() {
    selectedIndex = -1;
    selectedIndices = [];
    updateSelectionControls();
  }

  function selectionIndicesFromFabricEvent(ev) {
    var objects = [];
    if (ev && Array.isArray(ev.selected) && ev.selected.length) {
      objects = ev.selected;
    } else if (ev && ev.target && Array.isArray(ev.target._objects)) {
      objects = ev.target._objects;
    } else if (ev && ev.target) {
      objects = [ev.target];
    }
    return normalizeIndices(objects.map(function (obj) { return paths.indexOf(obj); }));
  }

  function toggleSelectionIndex(idx) {
    var next = selectedIndices.slice();
    var existing = next.indexOf(idx);
    if (existing >= 0) next.splice(existing, 1);
    else next.push(idx);
    setSelectedIndices(next, true);
    renderAnnotationBox();
    renderLayers();
  }

  function removeStrokeAt(index) {
    if (!canvas || index < 0 || index >= paths.length) return null;
    removeInlineLabel();
    var path = paths[index];
    var stroke = strokes[index];
    if (path) canvas.remove(path);
    paths.splice(index, 1);
    strokes.splice(index, 1);
    if (selectedIndex === index) selectedIndex = -1;
    else if (selectedIndex > index) selectedIndex -= 1;
    selectedIndices = selectedIndices
      .filter(function (idx) { return idx !== index; })
      .map(function (idx) { return idx > index ? idx - 1 : idx; });
    updateSelectionControls();
    return {
      path: path,
      stroke: stroke,
      pathData: path ? path.toObject(['strokeId']) : null,
    };
  }

  function insertStrokeAt(index, stroke, pathData, callback) {
    if (!canvas || !pathData) {
      if (callback) callback(null);
      return false;
    }
    fabric.util.enlivenObjects([pathData], function (objects) {
      var obj = preparePathObject(objects[0], currentMode === 'select');
      if (!obj) {
        if (callback) callback(null);
        return;
      }
      var safeIndex = Math.max(0, Math.min(index, paths.length));
      paths.splice(safeIndex, 0, obj);
      strokes.splice(safeIndex, 0, cloneStroke(stroke));
      if (typeof canvas.insertAt === 'function') {
        canvas.insertAt(obj, safeIndex, false);
      } else {
        canvas.add(obj);
      }
      obj.__lastState = serializeObjectState(obj);
      selectedIndex = safeIndex;
      canvas.setActiveObject(obj);
      canvas.requestRenderAll();
      updateCount();
      renderAnnotationBox();
      renderLayers();
      analyze();
      if (callback) callback(obj);
    });
    return true;
  }

  function strokeThumbnail(stroke, idx) {
    var pts = stroke && stroke.pts ? stroke.pts : [];
    if ((!pts || !pts.length) && paths[idx]) pts = getPathPoints(paths[idx]);
    if (!pts || !pts.length) {
      return '<svg viewBox="0 0 44 32"><path d="M9 20 C16 9, 28 9, 36 18" stroke="#2F7B58" stroke-width="3" fill="none" stroke-linecap="round"/></svg>';
    }
    var b = boundsForPoints(pts) || { minX: 0, maxX: 1, minY: 0, maxY: 1 };
    var bw = Math.max(1, b.maxX - b.minX);
    var bh = Math.max(1, b.maxY - b.minY);
    var sampleStep = Math.max(1, Math.ceil(pts.length / 28));
    var points = [];
    for (var i = 0; i < pts.length; i += sampleStep) {
      var x = 5 + ((pts[i].x - b.minX) / bw) * 34;
      var y = 5 + ((pts[i].y - b.minY) / bh) * 22;
      points.push(Math.round(x * 10) / 10 + ',' + Math.round(y * 10) / 10);
    }
    var color = escapeHtml((stroke && stroke.color) || '#2F7B58');
    if (points.length <= 2) {
      var p = points[0] || '22,16';
      return '<svg viewBox="0 0 44 32"><circle cx="' + p.split(',')[0] + '" cy="' + p.split(',')[1] + '" r="3.5" fill="' + color + '"/></svg>';
    }
    return '<svg viewBox="0 0 44 32"><polyline points="' + points.join(' ') + '" stroke="' + color + '" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  function logAction(action, data) {
    if (!sessionId) return;
    try {
      fetch('/api/log/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, action: action, data: data || {} }),
      }).catch(function () {});
    } catch (e) {}
  }

  function setStatus(text) {
    var el = $('inspire-analyze-state');
    if (el) el.textContent = text;
  }

  function zoneLabel(zone) {
    return { sky: '天空区域', midground: '中景区域', ground: '地面前景' }[zone] || '画面区域';
  }

  function shapeLabel(shape) {
    return {
      round: '圆润/团簇笔迹',
      tall: '竖向生长笔迹',
      wide: '横向延展笔迹',
      dot: '点状笔迹',
      wave: '波浪曲线',
      enclosure: '围合形态',
      zigzag: '折线形态',
      spiral: '旋转形态',
      free: '自由曲线',
    }[shape] || '自由曲线';
  }

  function colorLabel(hex) {
    if (window.SketchAnalyzer && window.SketchAnalyzer._getTintLabel) {
      try { return window.SketchAnalyzer._getTintLabel(hex); } catch (e) {}
    }
    return hex;
  }

  function getCanvasSize() {
    return {
      w: canvas ? canvas.getWidth() : 390,
      h: canvas ? canvas.getHeight() : 280,
    };
  }

  function getPathPoints(path) {
    if (window.SketchAnalyzer && window.SketchAnalyzer.extractPathPoints) {
      return window.SketchAnalyzer.extractPathPoints(path);
    }
    var pts = [];
    if (!path || !path.path) return pts;
    path.path.forEach(function (cmd) {
      if (cmd.length >= 3) pts.push({ x: cmd[cmd.length - 2], y: cmd[cmd.length - 1] });
    });
    return pts;
  }

  function boundsForPoints(pts) {
    if (!pts || !pts.length) return null;
    var xs = pts.map(function (p) { return p.x; });
    var ys = pts.map(function (p) { return p.y; });
    return {
      minX: Math.min.apply(null, xs),
      maxX: Math.max.apply(null, xs),
      minY: Math.min.apply(null, ys),
      maxY: Math.max.apply(null, ys),
    };
  }

  function isValidStroke(pts) {
    var b = boundsForPoints(pts);
    if (!b) return false;
    return Math.max(b.maxX - b.minX, b.maxY - b.minY) >= 6;
  }

  function strokeGeometry(stroke, idx) {
    var size = getCanvasSize();
    var pts = stroke.pts || [];
    var b;
    if (paths[idx] && paths[idx].getBoundingRect) {
      var rect = paths[idx].getBoundingRect();
      b = { minX: rect.left, maxX: rect.left + rect.width, minY: rect.top, maxY: rect.top + rect.height };
    } else {
      b = boundsForPoints(pts) || { minX: 0, maxX: 1, minY: 0, maxY: 1 };
    }
    var cx = (b.minX + b.maxX) / 2;
    var cy = (b.minY + b.maxY) / 2;
    var bw = b.maxX - b.minX;
    var bh = b.maxY - b.minY;
    return {
      x: Math.round((cx / size.w) * 1000) / 10,
      y: Math.round((cy / size.h) * 1000) / 10,
      bboxW: Math.round((bw / size.w) * 1000) / 10,
      bboxH: Math.round((bh / size.h) * 1000) / 10,
      aspectRatio: Math.round((bw / (bh || 1)) * 100) / 100,
    };
  }

  function updateCount() {
    var el = $('inspire-stroke-count');
    if (el) el.textContent = '已绘制 ' + strokes.length + ' 笔';
  }

  function updateSettingsSummary() {
    var lens = LENS_META[creativeLens] || LENS_META.restorative;
    var summary = $('settings-summary');
    if (summary) summary.textContent = '创意方向：' + lens.label + ' · AI 采纳 ' + aiAgency + '%';
    var value = $('agency-value');
    if (value) value.textContent = aiAgency + '%';
    var slider = $('agency-slider');
    if (slider) slider.value = String(aiAgency);
    document.querySelectorAll('.lens-card').forEach(function (el) {
      el.classList.toggle('active', el.getAttribute('data-lens') === creativeLens);
    });
  }

  function hideClearConfirm() {
    var modal = $('clear-confirm-modal');
    if (modal) modal.classList.remove('visible');
  }

  function resetRuntimeState() {
    removeInlineLabel();
    if (canvas) {
      try { canvas.dispose(); } catch (e) {}
    }
    canvas = null;
    strokes = [];
    paths = [];
    undoStack = [];
    selectedIndex = -1;
    selectedIndices = [];
    multiSelectMode = false;
    if (analyzeTimer) clearTimeout(analyzeTimer);
    analyzeTimer = null;
    lastResult = null;
    lastSceneIntent = null;
    strokeCounter = 0;
    interactionRound = 1;
    layersVisible = true;
    currentMode = 'draw';
    isRestoringHistory = false;
  }

  function performClear() {
    if (!canvas) return;
    removeInlineLabel();
    paths.forEach(function (p) { canvas.remove(p); });
    strokes = [];
    paths = [];
    undoStack = [];
    selectedIndex = -1;
    selectedIndices = [];
    lastResult = null;
    lastSceneIntent = null;
    updateCount();
    renderAnnotationBox();
    renderLayers();
    renderResult();
    canvas.renderAll();
    logAction('inspire_clear', {});
  }

  function setSelectable(selectable) {
    paths.forEach(function (p) {
      p.selectable = selectable;
      p.evented = selectable;
      if (selectable && !p.__lastState) p.__lastState = serializeObjectState(p);
    });
    if (canvas) {
      canvas.selection = selectable;
      canvas.isDrawingMode = !selectable;
      canvas.discardActiveObject();
      canvas.renderAll();
    }
    updateSelectionControls();
  }

  function updateModeButtons(mode) {
    var drawBtn = $('mode-draw-btn');
    var selectBtn = $('mode-select-btn');
    if (drawBtn) drawBtn.classList.toggle('active', mode === 'draw');
    if (selectBtn) selectBtn.classList.toggle('active', mode === 'select');
    updateSelectionControls();
  }

  function selectedStroke() {
    if (selectedIndex < 0 || selectedIndex >= strokes.length) return null;
    return strokes[selectedIndex];
  }

  function renderAnnotationBox() {
    var box = $('annotation-box');
    var input = $('annotation-input');
    var s = selectedStroke();
    var groupSelection = selectedIndices.length > 1;
    if (!box) return;
    box.classList.toggle('visible', !!s || groupSelection);
    if (groupSelection && input) {
      var labels = selectedIndices.map(function (idx) { return strokes[idx] && strokes[idx].userLabel; }).filter(Boolean);
      input.value = labels.length && labels.every(function (label) { return label === labels[0]; }) ? labels[0] : '';
      input.placeholder = '为选中的一组笔画标注，例如：竹林、花坛、溪流';
    } else if (s && input) {
      input.value = s.userLabel || '';
      input.placeholder = '修正 AI 理解，例如：竹林、小溪、圆形花坛';
    }
  }

  function renderLayers() {
    var panel = $('layer-panel');
    if (!panel) return;
    updateLayerButton();
    panel.style.display = layersVisible ? 'flex' : 'none';
    if (!layersVisible) return;
    var head = '<div class="layer-panel-head">'
      + '<span class="layer-panel-title">图层</span>'
      + '<span class="layer-panel-count">' + strokes.length + ' 层</span>'
      + '</div>';
    if (!strokes.length) {
      panel.innerHTML = head + '<div class="layer-list"><div class="layer-item"><div class="layer-thumb"></div><div class="layer-main"><div class="layer-name">暂无笔画图层</div><div class="layer-sub">画布上的笔画会出现在这里</div></div><span class="layer-zone">空</span></div></div>';
      return;
    }
    var items = strokes.map(function (s, i) {
      var label = s.userLabel || s.autoLabel || '未识别笔画';
      var activeMap = selectedIndexSet();
      var active = (i === selectedIndex || activeMap[i]) ? ' active' : '';
      var groupText = s.groupId ? ' · 已组合' : '';
      return '<div class="layer-item' + active + '" onclick="InspireCanvas.selectStroke(' + i + ')">'
        + '<div class="layer-thumb">' + strokeThumbnail(s, i) + '</div>'
        + '<div class="layer-main">'
        + '<div class="layer-name">' + (i + 1) + '. ' + escapeHtml(label) + '</div>'
        + '<div class="layer-sub">' + escapeHtml(shapeLabel(s.shapeType) + groupText) + '</div>'
        + '</div>'
        + '<span class="layer-zone">' + escapeHtml(zoneLabel(s.zone)) + '</span></div>';
    }).join('');
    panel.innerHTML = head + '<div class="layer-list">' + items + '</div>';
  }

  function explainStroke(s, idx) {
    var label = s.userLabel || s.autoLabel || '整体氛围';
    var source = s.userLabel ? '你手动标注为' : 'AI 暂时理解为';
    var confidence = Math.round((s.autoConfidence || 0) * 100);
    return source + '「' + label + '」：' + shapeLabel(s.shapeType)
      + '位于' + zoneLabel(s.zone) + '，颜色倾向' + colorLabel(s.color)
      + (s.userLabel ? '，用户标注优先于自动识别。' : '，置信度约 ' + confidence + '%。');
  }

  function renderResult() {
    var area = $('inspire-result-area');
    if (!area) return;
    if (!strokes.length) {
      area.innerHTML = '<div class="result-title">🎨 等待你的笔迹</div>'
        + '<div style="font-size:12px;line-height:1.55">在画布上画几笔，AI 将识别你的意图；切换到“选择标注”可以修正它。</div>';
      return;
    }

    var results = (lastResult && lastResult.results) || [];
    var title = '✦ AI 已形成可解释的创作意图';
    var tags = results.slice(0, 8).map(function (el) {
      var conf = Math.round((el.confidence || 0) * 100);
      return '<span class="elem-tag">' + (el.icon || '✦') + ' ' + (el.elemName || '元素')
        + ' <small>' + conf + '%</small></span>';
    }).join('');
    if (!tags) {
      var mood = lastSceneIntent && lastSceneIntent.dominantMood ? lastSceneIntent.dominantMood : '自由创想';
      tags = '<span class="elem-tag">✦ ' + mood + '</span>';
    }
    var explanations = strokes.slice(0, 4).map(function (s, i) {
      return '<span class="explain-chip">' + explainStroke(s, i) + '</span>';
    }).join('');
    var lens = LENS_META[creativeLens] || LENS_META.restorative;
    area.innerHTML = '<div class="result-title">' + title + '</div>'
      + '<div class="elem-tags">' + tags + '</div>'
      + '<div style="height:8px"></div>'
      + '<div class="explain-list">' + explanations + '</div>'
      + '<div style="font-size:11px;color:rgba(23,49,38,.58);margin-top:9px;line-height:1.45">'
      + '当前创意方向：' + lens.label + '；AI 采纳强度：' + aiAgency + '%。'
      + '</div>';
  }

  function analyze() {
    if (!canvas || !strokes.length) {
      lastResult = null;
      lastSceneIntent = null;
      setStatus('等待笔迹');
      renderResult();
      return;
    }
    setStatus('正在分析意图...');
    var size = getCanvasSize();
    if (window.SketchAnalyzer && window.SketchAnalyzer.analyzeStrokes) {
      lastResult = window.SketchAnalyzer.analyzeStrokes(strokes, size.w, size.h);
    } else {
      lastResult = { type: 'mood', results: [], moodParams: { green: 50, urban: 50, vitality: 50, light: 50 }, strokesWithZone: [] };
    }
    if (window.SketchComposer && window.SketchComposer.compose) {
      lastSceneIntent = window.SketchComposer.compose(lastResult, size.w, size.h);
    } else {
      lastSceneIntent = { dominantMood: '自由创想', complexityLevel: 'simple', spatialPatterns: [], proximityRelations: [] };
    }
    lastSceneIntent.creativeLens = creativeLens;
    lastSceneIntent.creativeLensLabel = (LENS_META[creativeLens] || LENS_META.restorative).label;
    lastSceneIntent.creativeLensPrompt = (LENS_META[creativeLens] || LENS_META.restorative).prompt;
    lastSceneIntent.aiAgency = aiAgency;
    setStatus('已分析，可标注修正');
    renderResult();
  }

  function scheduleAnalysis() {
    if (analyzeTimer) clearTimeout(analyzeTimer);
    setStatus('停笔后自动分析...');
    analyzeTimer = setTimeout(analyze, 650);
  }

  function attachCanvasEvents() {
    canvas.on('mouse:down', function (ev) {
      if (canvas && canvas.isDrawingMode) removeInlineLabel();
      if (currentMode === 'select' && multiSelectMode && ev && ev.target) {
        var target = ev.target;
        if (target && !Array.isArray(target._objects)) {
          var idx = paths.indexOf(target);
          if (idx >= 0) {
            toggleSelectionIndex(idx);
            skipNextSingleSelection = true;
            if (ev.e && ev.e.preventDefault) ev.e.preventDefault();
          }
        }
      }
    });

    canvas.on('path:created', function (e) {
      var pts = getPathPoints(e.path);
      if (!isValidStroke(pts)) {
        canvas.remove(e.path);
        removeInlineLabel();
        return;
      }
      strokeCounter += 1;
      var size = getCanvasSize();
      var match = window.SketchAnalyzer && window.SketchAnalyzer.quickMatchStroke
        ? window.SketchAnalyzer.quickMatchStroke(pts, size.w, size.h, drawColor)
        : null;
      var stroke = {
        strokeId: 'sk_' + strokeCounter,
        pts: pts,
        color: drawColor,
        createdAt: Date.now(),
        shapeType: match && match.shapeType ? match.shapeType : '',
        zone: match ? match.zone : 'midground',
        autoLabel: match ? match.elemName : '',
        autoConfidence: match ? match.confidence : 0,
        userLabel: '',
        source: 'auto',
        interactionRound: interactionRound,
        editHistory: ['created'],
      };
      if (window.SketchAnalyzer && window.SketchAnalyzer._extractFeatures && window.SketchAnalyzer._classifyShape) {
        try {
          var f = window.SketchAnalyzer._extractFeatures(pts);
          stroke.shapeType = f ? window.SketchAnalyzer._classifyShape(f, pts, size.w) : stroke.shapeType;
          stroke.zone = f ? window.SketchAnalyzer._getZone((f.centerY / size.h) * 100) : stroke.zone;
        } catch (err) {}
      }
      e.path.stroke = drawColor;
      e.path.strokeWidth = brushSize;
      e.path.strokeId = stroke.strokeId;
      e.path.selectable = false;
      e.path.evented = false;
      e.path.__lastState = serializeObjectState(e.path);
      strokes.push(stroke);
      paths.push(e.path);
      undoStack.push({
        type: 'add',
        index: strokes.length - 1,
        strokeId: stroke.strokeId,
        stroke: cloneStroke(stroke),
        pathData: e.path.toObject(['strokeId']),
      });
      logAction('inspire_stroke_created', {
        strokeId: stroke.strokeId,
        autoLabel: stroke.autoLabel,
        confidence: stroke.autoConfidence,
        color: drawColor,
        zone: stroke.zone,
      });
      updateCount();
      renderLayers();
      showInlineLabel(stroke, e.path);
      scheduleAnalysis();
    });

    canvas.on('selection:created', function (ev) {
      if (isUpdatingSelection) return;
      var indices = selectionIndicesFromFabricEvent(ev);
      if (multiSelectMode) {
        if (skipNextSingleSelection && indices.length <= 1) {
          skipNextSingleSelection = false;
          setSelectedIndices(selectedIndices, false);
        } else {
          skipNextSingleSelection = false;
          setSelectedIndices(indices.length ? indices : selectedIndices, false);
        }
      } else {
        skipNextSingleSelection = false;
        setSelectedIndices(indices.slice(0, 1), false);
      }
      var obj = paths[selectedIndex];
      if (obj) obj.__lastState = serializeObjectState(obj);
      renderAnnotationBox();
      renderLayers();
    });
    canvas.on('selection:updated', function (ev) {
      if (isUpdatingSelection) return;
      var indices = selectionIndicesFromFabricEvent(ev);
      if (multiSelectMode) {
        if (skipNextSingleSelection && indices.length <= 1) {
          skipNextSingleSelection = false;
          setSelectedIndices(selectedIndices, false);
        } else {
          skipNextSingleSelection = false;
          setSelectedIndices(indices.length ? indices : selectedIndices, false);
        }
      } else {
        skipNextSingleSelection = false;
        setSelectedIndices(indices.slice(0, 1), false);
      }
      var obj = paths[selectedIndex];
      if (obj) obj.__lastState = serializeObjectState(obj);
      renderAnnotationBox();
      renderLayers();
    });
    canvas.on('selection:cleared', function () {
      if (isUpdatingSelection) return;
      clearSelectionState();
      renderAnnotationBox();
      renderLayers();
    });
    canvas.on('object:modified', function (ev) {
      if (isRestoringHistory) return;
      var obj = ev && ev.target ? ev.target : null;
      var idx = paths.indexOf(obj);
      if (idx < 0 && obj && Array.isArray(obj._objects)) {
        renderLayers();
        scheduleAnalysis();
        return;
      }
      if (idx >= 0) setSelectedIndices([idx], false);
      var s = selectedStroke();
      var before = obj ? obj.__lastState : null;
      var after = obj ? serializeObjectState(obj) : null;
      if (obj && before && after && JSON.stringify(before) !== JSON.stringify(after)) {
        undoStack.push({ type: 'modify', index: idx, strokeId: s && s.strokeId, before: before, after: after });
        obj.__lastState = after;
      }
      if (s && s.editHistory.indexOf('moved') === -1) s.editHistory.push('moved');
      renderLayers();
      scheduleAnalysis();
    });
  }

  function loadBackground() {
    if (!imageUrl || !window.fabric || !canvas) return;
    fabric.Image.fromURL(imageUrl, function (img) {
      if (!img || !canvas) return;
      var wrap = $('inspire-canvas-wrapper');
      var stage = wrap && wrap.parentElement ? wrap.parentElement : wrap;
      var availableW = (stage && stage.clientWidth) || canvas.getWidth() || 390;
      var isLandscape = window.matchMedia && window.matchMedia('(min-width: 900px) and (orientation: landscape)').matches;
      var maxHByViewport = Math.round(window.innerHeight * (isLandscape ? 0.56 : 0.42));
      var maxH = Math.max(190, Math.min(maxHByViewport, window.innerHeight - (isLandscape ? 280 : 350)));
      var scale = Math.min(availableW / img.width, maxH / img.height);
      if (!isFinite(scale) || scale <= 0) scale = availableW / img.width;
      var w = Math.max(80, Math.min(Math.round(availableW), Math.round(img.width * scale)));
      var h = Math.max(80, Math.round(w * img.height / img.width));
      if (h > maxH) {
        h = maxH;
        w = Math.max(80, Math.round(h * img.width / img.height));
      }
      scale = w / img.width;
      canvas.setWidth(w);
      canvas.setHeight(h);
      if (wrap) {
        wrap.style.width = w + 'px';
        wrap.style.height = h + 'px';
        wrap.style.maxWidth = '100%';
        wrap.style.marginLeft = 'auto';
        wrap.style.marginRight = 'auto';
      }
      img.set({
        left: 0, top: 0, scaleX: scale, scaleY: scale,
        selectable: false, evented: false, opacity: 0.88,
      });
      canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
    }, { crossOrigin: 'anonymous' });
  }

  function restoreFromUrl() {
    if (!restoreUrl) return;
    fetch(restoreUrl).then(function (r) { return r.text(); }).then(function (text) {
      if (text && text !== '[]') window.InspireCanvas.restorePaths(text);
    }).catch(function () {});
  }

  return {
    init: function (opts) {
      opts = opts || {};
      var wrap = $('inspire-canvas-wrapper');
      var canvasEl = $('inspire-canvas');
      var fallback = $('inspire-fallback');
      if (!wrap || !canvasEl) return;
      var nextImageUrl = opts.imageUrl || '';
      var nextSessionId = opts.sessionId || '';
      var nextRestoreUrl = opts.restoreUrl || '';
      if (canvas && canvas.lowerCanvasEl === canvasEl && sessionId === nextSessionId) return;
      if (canvas) resetRuntimeState();
      imageUrl = nextImageUrl;
      sessionId = nextSessionId;
      restoreUrl = nextRestoreUrl;
      if (typeof fabric === 'undefined') {
        if (fallback) fallback.style.display = 'block';
        return;
      }
      var w = wrap.clientWidth || 390;
      canvas = new fabric.Canvas('inspire-canvas', {
        width: w,
        height: Math.round(w * 0.64),
        backgroundColor: '#F3F8EF',
        isDrawingMode: true,
        selection: false,
      });
      canvas.freeDrawingBrush.color = drawColor;
      canvas.freeDrawingBrush.width = brushSize;
      canvas.freeDrawingBrush.decimate = 2;
      attachCanvasEvents();
      loadBackground();
      restoreFromUrl();
      updateCount();
      updateSettingsSummary();
      renderLayers();
      renderResult();
      updateSelectionControls();
      logAction('inspire_enter', { hasImage: !!imageUrl });
    },

    openSettings: function () {
      var modal = $('settings-modal');
      if (modal) modal.classList.add('visible');
      updateSettingsSummary();
      logAction('inspire_settings_open', { lens: creativeLens, aiAgency: aiAgency });
    },

    closeSettings: function (event) {
      if (event && event.target && event.currentTarget && event.target !== event.currentTarget) return;
      var modal = $('settings-modal');
      if (modal) modal.classList.remove('visible');
      updateSettingsSummary();
    },

    openStrokeGuide: function () {
      var modal = $('stroke-guide-modal');
      if (modal) modal.classList.add('visible');
      logAction('inspire_stroke_guide_open', {});
    },

    closeStrokeGuide: function (event) {
      if (event && event.target && event.currentTarget && event.target !== event.currentTarget) return;
      var modal = $('stroke-guide-modal');
      if (modal) modal.classList.remove('visible');
    },

    toggleBrief: function () {
      var card = document.querySelector('.inspire-brief');
      var btn = $('brief-toggle-btn');
      if (!card) return;
      var collapsed = card.classList.toggle('collapsed');
      if (btn) btn.textContent = collapsed ? '展开' : '收起';
    },

    setMode: function (mode) {
      if (!canvas) return;
      removeInlineLabel();
      currentMode = mode === 'select' ? 'select' : 'draw';
      if (mode === 'select') {
        setSelectable(true);
      } else {
        multiSelectMode = false;
        clearSelectionState();
        setSelectable(false);
      }
      updateModeButtons(currentMode);
      renderAnnotationBox();
      renderLayers();
      logAction('inspire_mode_change', { mode: currentMode });
    },

    setColor: function (hex, isCustom) {
      var nextColor = normalizeHex(hex);
      drawColor = nextColor;
      if (isCustom) customColor = nextColor;
      if (canvas && canvas.freeDrawingBrush) canvas.freeDrawingBrush.color = nextColor;

      var presetSelected = false;
      document.querySelectorAll('.color-dot[data-color]').forEach(function (el) {
        var isSelected = normalizeHex(el.getAttribute('data-color')) === nextColor;
        el.classList.toggle('selected', isSelected);
        if (isSelected) presetSelected = true;
      });

      var customInput = $('custom-color-input');
      var customDot = $('custom-color-dot');
      if (customInput) customInput.value = customColor;
      if (customDot) {
        customDot.style.background = customColor;
        customDot.classList.toggle('selected', !presetSelected);
      }
    },

    setBrushSize: function (size) {
      brushSize = size || 4;
      if (canvas && canvas.freeDrawingBrush) canvas.freeDrawingBrush.width = brushSize;
    },

    setLens: function (lens) {
      creativeLens = LENS_META[lens] ? lens : 'restorative';
      updateSettingsSummary();
      analyze();
      logAction('inspire_lens_change', { lens: creativeLens });
    },

    setAgency: function (value) {
      aiAgency = Math.max(20, Math.min(100, value || 70));
      updateSettingsSummary();
      analyze();
    },

    selectStroke: function (idx) {
      if (!canvas || idx < 0 || idx >= paths.length) return;
      if (multiSelectMode) {
        toggleSelectionIndex(idx);
        return;
      }
      setSelectedIndices([idx], false);
      canvas.setActiveObject(paths[idx]);
      canvas.renderAll();
      renderAnnotationBox();
      renderLayers();
    },

    toggleMultiSelect: function () {
      if (!canvas) return;
      if (currentMode !== 'select') this.setMode('select');
      multiSelectMode = !multiSelectMode;
      if (!multiSelectMode && selectedIndices.length > 1) {
        setSelectedIndices([selectedIndex], true);
      } else {
        setSelectedIndices(currentSelectedIndices(), true);
      }
      updateSelectionControls();
      renderAnnotationBox();
      renderLayers();
      setStatus(multiSelectMode ? '多选已开启，可连续点选笔画' : '多选已关闭');
      logAction('inspire_multi_select_toggle', { enabled: multiSelectMode });
    },

    groupSelected: function () {
      var indices = currentSelectedIndices();
      if (!canvas || indices.length < 2) {
        setStatus('请先多选至少两笔');
        return;
      }
      var before = indices.map(function (idx) {
        return { index: idx, strokeId: strokes[idx].strokeId, stroke: cloneStroke(strokes[idx]) };
      });
      var groupId = 'grp_' + Date.now().toString(36);
      indices.forEach(function (idx) {
        strokes[idx].groupId = groupId;
        strokes[idx].isGroup = true;
        strokes[idx].groupSize = indices.length;
        if (strokes[idx].editHistory.indexOf('grouped') === -1) strokes[idx].editHistory.push('grouped');
      });
      undoStack.push({ type: 'group', before: before, afterGroupId: groupId });
      setSelectedIndices(indices, true);
      renderAnnotationBox();
      renderLayers();
      analyze();
      setStatus('已组合 ' + indices.length + ' 笔，可为这组补充标注');
      logAction('inspire_group_selected', { groupId: groupId, strokeIds: indices.map(function (idx) { return strokes[idx].strokeId; }) });
    },

    ungroupSelected: function () {
      var indices = currentSelectedIndices();
      var groupIds = {};
      indices.forEach(function (idx) {
        if (strokes[idx] && strokes[idx].groupId) groupIds[strokes[idx].groupId] = true;
      });
      var targetIndices = [];
      strokes.forEach(function (s, idx) {
        if (s && s.groupId && groupIds[s.groupId]) targetIndices.push(idx);
      });
      if (!targetIndices.length) {
        setStatus('当前选择没有可解组的组合');
        return;
      }
      var before = targetIndices.map(function (idx) {
        return { index: idx, strokeId: strokes[idx].strokeId, stroke: cloneStroke(strokes[idx]) };
      });
      targetIndices.forEach(function (idx) {
        delete strokes[idx].groupId;
        delete strokes[idx].isGroup;
        delete strokes[idx].groupSize;
        if (strokes[idx].editHistory.indexOf('ungrouped') === -1) strokes[idx].editHistory.push('ungrouped');
      });
      undoStack.push({ type: 'group', before: before, afterGroupId: null });
      setSelectedIndices(targetIndices, true);
      renderAnnotationBox();
      renderLayers();
      analyze();
      setStatus('已解组');
      logAction('inspire_ungroup_selected', { count: targetIndices.length });
    },

    confirmAnnotation: function () {
      var s = selectedStroke();
      var input = $('annotation-input');
      if (!input) return;
      var value = (input.value || '').trim();
      if (!value) return;
      if (selectedIndices.length > 1) {
        var indices = currentSelectedIndices();
        var beforeItems = indices.map(function (idx) {
          return {
            index: idx,
            strokeId: strokes[idx].strokeId,
            userLabel: strokes[idx].userLabel || '',
            source: strokes[idx].source || 'auto',
          };
        });
        indices.forEach(function (idx) {
          strokes[idx].userLabel = value;
          strokes[idx].source = 'user';
          if (strokes[idx].editHistory.indexOf('annotated') === -1) strokes[idx].editHistory.push('annotated');
        });
        undoStack.push({ type: 'multiAnnotate', items: beforeItems, after: value });
        logAction('inspire_group_annotation_confirmed', {
          strokeIds: indices.map(function (idx) { return strokes[idx].strokeId; }),
          userLabel: value,
        });
        renderLayers();
        analyze();
        return;
      }
      if (!s) return;
      var before = s.userLabel || '';
      s.userLabel = value;
      s.source = 'user';
      if (s.editHistory.indexOf('annotated') === -1) s.editHistory.push('annotated');
      undoStack.push({ type: 'annotate', index: selectedIndex, strokeId: s.strokeId, before: before, after: value });
      logAction('inspire_annotation_confirmed', { strokeId: s.strokeId, userLabel: value, autoLabel: s.autoLabel });
      if (paths[selectedIndex]) showInlineLabel(s, paths[selectedIndex]);
      renderLayers();
      analyze();
    },

    duplicateSelected: function () {
      if (!canvas || selectedIndex < 0 || selectedIndex >= paths.length) return;
      removeInlineLabel();
      var sourcePath = paths[selectedIndex];
      var sourceStroke = strokes[selectedIndex];
      if (!sourcePath || !sourceStroke || !sourcePath.clone) return;
      sourcePath.clone(function (copy) {
        strokeCounter += 1;
        var newStroke = cloneStroke(sourceStroke);
        newStroke.strokeId = 'sk_' + strokeCounter;
        newStroke.createdAt = Date.now();
        newStroke.source = 'copy';
        newStroke.editHistory = (newStroke.editHistory || []).concat(['duplicated']);
        copy.set({
          left: (copy.left || 0) + 16,
          top: (copy.top || 0) + 16,
          strokeId: newStroke.strokeId,
        });
        preparePathObject(copy, currentMode === 'select');
        copy.__lastState = serializeObjectState(copy);
        canvas.add(copy);
        paths.push(copy);
        strokes.push(newStroke);
        selectedIndex = paths.length - 1;
        canvas.setActiveObject(copy);
        undoStack.push({
          type: 'add',
          index: selectedIndex,
          strokeId: newStroke.strokeId,
          stroke: cloneStroke(newStroke),
          pathData: copy.toObject(['strokeId']),
        });
        updateCount();
        renderAnnotationBox();
        renderLayers();
        analyze();
        logAction('inspire_duplicate', { strokeId: newStroke.strokeId, fromStrokeId: sourceStroke.strokeId });
      });
    },

    deleteSelected: function () {
      if (!canvas || selectedIndex < 0 || selectedIndex >= paths.length) return;
      var idx = selectedIndex;
      var removed = removeStrokeAt(idx);
      if (!removed) return;
      undoStack.push({
        type: 'delete',
        index: idx,
        strokeId: removed.stroke && removed.stroke.strokeId,
        stroke: cloneStroke(removed.stroke),
        pathData: removed.pathData,
      });
      canvas.discardActiveObject();
      canvas.requestRenderAll();
      updateCount();
      renderAnnotationBox();
      renderLayers();
      analyze();
      logAction('inspire_delete', { strokeId: removed.stroke && removed.stroke.strokeId });
    },

    toggleLayers: function () {
      layersVisible = !layersVisible;
      updateLayerButton();
      renderLayers();
    },

    undo: function () {
      if (!canvas || !undoStack.length) return;
      var action = undoStack.pop();
      var finishUndo = function () {
        updateCount();
        renderAnnotationBox();
        renderLayers();
        analyze();
        logAction('inspire_undo', { type: action.type, strokeId: action.strokeId });
      };
      isRestoringHistory = true;
      if (action.type === 'add') {
        var addIndex = paths.findIndex(function (p, idx) {
          return (p && p.strokeId === action.strokeId) || (strokes[idx] && strokes[idx].strokeId === action.strokeId);
        });
        if (addIndex < 0) addIndex = Math.min(action.index, paths.length - 1);
        removeStrokeAt(addIndex);
        canvas.discardActiveObject();
        canvas.requestRenderAll();
        clearSelectionState();
      } else if (action.type === 'delete') {
        insertStrokeAt(action.index, action.stroke, action.pathData, function () {
          isRestoringHistory = false;
          finishUndo();
        });
        return;
      } else if (action.type === 'modify') {
        var modPath = paths[action.index];
        if ((!modPath || (action.strokeId && strokes[action.index] && strokes[action.index].strokeId !== action.strokeId))) {
          var found = paths.findIndex(function (p, idx) {
            return (p && p.strokeId === action.strokeId) || (strokes[idx] && strokes[idx].strokeId === action.strokeId);
          });
          modPath = found >= 0 ? paths[found] : modPath;
          selectedIndex = found;
        } else {
          selectedIndex = action.index;
        }
        applyObjectState(modPath, action.before);
        if (modPath) {
          modPath.__lastState = serializeObjectState(modPath);
          canvas.setActiveObject(modPath);
        }
      } else if (action.type === 'annotate') {
        var annIdx = action.index;
        if (!strokes[annIdx] || strokes[annIdx].strokeId !== action.strokeId) {
          annIdx = strokes.findIndex(function (s) { return s.strokeId === action.strokeId; });
        }
        if (annIdx >= 0 && strokes[annIdx]) {
          strokes[annIdx].userLabel = action.before || '';
          strokes[annIdx].source = strokes[annIdx].userLabel ? 'user' : 'auto';
          selectedIndex = annIdx;
          if (paths[annIdx]) canvas.setActiveObject(paths[annIdx]);
        }
      } else if (action.type === 'multiAnnotate') {
        (action.items || []).forEach(function (item) {
          var idx = strokes.findIndex(function (s) { return s.strokeId === item.strokeId; });
          if (idx >= 0 && strokes[idx]) {
            strokes[idx].userLabel = item.userLabel || '';
            strokes[idx].source = item.source || (strokes[idx].userLabel ? 'user' : 'auto');
          }
        });
        setSelectedIndices((action.items || []).map(function (item) { return item.index; }), true);
      } else if (action.type === 'group') {
        (action.before || []).forEach(function (item) {
          var idx = strokes.findIndex(function (s) { return s.strokeId === item.strokeId; });
          if (idx >= 0 && item.stroke) strokes[idx] = cloneStroke(item.stroke);
        });
        setSelectedIndices((action.before || []).map(function (item) { return item.index; }), true);
      }
      isRestoringHistory = false;
      finishUndo();
    },

    clear: function () {
      if (!canvas) return;
      var modal = $('clear-confirm-modal');
      if (modal) {
        modal.classList.add('visible');
        return;
      }
      if (window.confirm('确认清除目前所有的笔画吗？')) performClear();
    },

    confirmClear: function () {
      hideClearConfirm();
      performClear();
    },

    cancelClear: function (event) {
      if (event && event.target && event.currentTarget && event.target !== event.currentTarget) return;
      hideClearConfirm();
    },

    advanceRound: function () {
      interactionRound += 1;
    },

    getSubmitData: function () {
      if (!strokes.length) return JSON.stringify(null);
      analyze();
      var strokeLog = strokes.map(function (s, idx) {
        return Object.assign({}, s, strokeGeometry(s, idx), {
          explanation: explainStroke(s, idx),
        });
      });
      var groupBuckets = {};
      var userAnnotations = [];
      strokeLog.forEach(function (s) {
        if (!s.userLabel) return;
        if (s.groupId) {
          if (!groupBuckets[s.groupId]) {
            groupBuckets[s.groupId] = {
              userLabel: s.userLabel,
              strokeId: s.strokeId,
              strokeIds: [],
              isGroup: true,
              groupId: s.groupId,
              minX: 100,
              minY: 100,
              maxX: 0,
              maxY: 0,
              color: s.color,
              shapeType: 'free',
              zone: s.zone,
            };
          }
          var bucket = groupBuckets[s.groupId];
          bucket.strokeIds.push(s.strokeId);
          bucket.userLabel = bucket.userLabel || s.userLabel;
          bucket.minX = Math.min(bucket.minX, s.x - (s.bboxW || 0) / 2);
          bucket.minY = Math.min(bucket.minY, s.y - (s.bboxH || 0) / 2);
          bucket.maxX = Math.max(bucket.maxX, s.x + (s.bboxW || 0) / 2);
          bucket.maxY = Math.max(bucket.maxY, s.y + (s.bboxH || 0) / 2);
          return;
        }
        userAnnotations.push({
          userLabel: s.userLabel,
          strokeId: s.strokeId,
          strokeIds: [s.strokeId],
          groupId: '',
          isGroup: false,
          x: s.x,
          y: s.y,
          bboxW: s.bboxW,
          bboxH: s.bboxH,
          aspectRatio: s.aspectRatio,
          color: s.color,
          shapeType: s.shapeType,
          zone: s.zone,
        });
      });
      Object.keys(groupBuckets).forEach(function (groupId) {
        var bucket = groupBuckets[groupId];
        var bboxW = Math.max(0, Math.min(100, bucket.maxX - bucket.minX));
        var bboxH = Math.max(0, Math.min(100, bucket.maxY - bucket.minY));
        userAnnotations.push({
          userLabel: bucket.userLabel,
          strokeId: bucket.strokeId,
          strokeIds: bucket.strokeIds,
          groupId: bucket.groupId,
          isGroup: true,
          x: Math.round(((bucket.minX + bucket.maxX) / 2) * 10) / 10,
          y: Math.round(((bucket.minY + bucket.maxY) / 2) * 10) / 10,
          bboxW: Math.round(bboxW * 10) / 10,
          bboxH: Math.round(bboxH * 10) / 10,
          aspectRatio: Math.round((bboxW / (bboxH || 1)) * 100) / 100,
          color: bucket.color,
          shapeType: bucket.shapeType,
          zone: bucket.zone,
        });
      });
      var hciMetrics = {
        autoRecognizedCount: strokeLog.filter(function (s) { return !!s.autoLabel; }).length,
        userAnnotationCount: userAnnotations.length,
        correctionCount: strokeLog.filter(function (s) { return s.userLabel && s.userLabel !== s.autoLabel; }).length,
        creativeLens: creativeLens,
        aiAgency: aiAgency,
        explanationCount: strokeLog.length,
      };
      return JSON.stringify({
        type: lastResult ? lastResult.type : 'mood',
        results: lastResult ? (lastResult.results || []) : [],
        moodParams: lastResult ? (lastResult.moodParams || null) : null,
        strokeCount: strokes.length,
        sceneIntent: lastSceneIntent || {
          dominantMood: '自由创想',
          complexityLevel: 'simple',
          spatialPatterns: [],
          creativeLens: creativeLens,
          creativeLensLabel: (LENS_META[creativeLens] || LENS_META.restorative).label,
          creativeLensPrompt: (LENS_META[creativeLens] || LENS_META.restorative).prompt,
          aiAgency: aiAgency,
        },
        interactionRound: interactionRound,
        strokeLog: strokeLog,
        userAnnotations: userAnnotations,
        hciMetrics: hciMetrics,
      });
    },

    getCanvasDataURL: function () {
      if (!canvas) return '';
      try {
        removeInlineLabel();
        canvas.discardActiveObject();
        canvas.renderAll();
        return canvas.toDataURL({ format: 'png' });
      } catch (e) {
        return '';
      }
    },

    getPathsJSON: function () {
      var data = strokes.map(function (s, idx) {
        return {
          stroke: s,
          path: paths[idx] ? paths[idx].toObject(['strokeId']) : null,
        };
      });
      return JSON.stringify(data);
    },

    restorePaths: function (jsonStr) {
      if (!canvas || !jsonStr) return;
      try {
        var data = JSON.parse(jsonStr);
        if (!Array.isArray(data)) return;
        data.forEach(function (entry) {
          if (!entry || !entry.path) return;
          fabric.util.enlivenObjects([entry.path], function (objects) {
            var obj = objects[0];
            if (!obj) return;
            preparePathObject(obj, currentMode === 'select');
            if (entry.stroke && entry.stroke.strokeId) obj.strokeId = entry.stroke.strokeId;
            obj.__lastState = serializeObjectState(obj);
            canvas.add(obj);
            paths.push(obj);
            strokes.push(entry.stroke || {
              strokeId: 'sk_restore_' + (paths.length),
              pts: getPathPoints(obj),
              color: obj.stroke || drawColor,
              createdAt: Date.now(),
              zone: 'midground',
              autoLabel: '',
              autoConfidence: 0,
              userLabel: '',
              source: 'auto',
              editHistory: ['restored'],
            });
            strokeCounter += 1;
            updateCount();
            renderLayers();
            analyze();
          });
        });
      } catch (e) {}
    },
  };
})();
