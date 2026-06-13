/**
 * EnvCanvas — 环境画布编辑器
 * 基于 Fabric.js，支持元素拖拽、缩放、旋转、删除
 */
window.EnvCanvas = (function () {
  'use strict';

  let _canvas = null;
  let _bgImage = null;
  let _bgLoaded = false;
  let _origW = 0, _origH = 0, _bgScale = 1, _bgLeft = 0, _bgTop = 0;
  let _elements = [];
  let _sessionId = '';
  let _toolbar = null;
  let _suppressClick = false;
  let _lastSelected = null;  // 缓存最后一次选中的对象，防止toolbar操作时已被deselect
  let _dragWrapper = null;
  let _globalTouchBound = false;
  let _touchGhost = null;
  let _touchDragIdx = -1;
  let _touchDragging = false;
  let _touchStartX = 0, _touchStartY = 0;
  let _touchDragCard = null;
  const MAX_ELEMENTS = 20;
  const TOUCH_DRAG_THRESHOLD = 12;

  // ───────────────── 初始化 ─────────────────

  function init(canvasId, imgUrl, sessionId) {
    const wrapper = document.getElementById('canvas-wrapper');
    const canvasEl = document.getElementById(canvasId);
    if (!wrapper || !canvasEl || typeof fabric === 'undefined') {
      setTimeout(function () { init(canvasId, imgUrl, sessionId); }, 60);
      return;
    }

    if (_canvas && _canvas.lowerCanvasEl === canvasEl && _sessionId === (sessionId || '')) {
      return;
    }

    _disposeCanvas();
    _sessionId = sessionId || '';

    const w = wrapper.clientWidth || 440;
    const initialH = Math.round(Math.min(w * 0.58, window.innerHeight * 0.32));

    _canvas = new fabric.Canvas(canvasId, {
      width: w,
      height: Math.max(198, initialH),
      backgroundColor: '#e8f0ea',
      selection: true,
      preserveObjectStacking: true,
      stopContextMenu: true,
      perPixelTargetFind: false,
      targetFindTolerance: 14,
    });

    var fallback = document.getElementById('drag-canvas-fallback');
    if (fallback) fallback.style.display = 'none';

    _canvas.allowTouchScrolling = false;
    _toolbar = document.getElementById('canvas-toolbar');

    // 阻止工具栏点击/触摸导致canvas失去焦点取消选中
    if (_toolbar && !_toolbar.dataset.envToolbarBound) {
      _toolbar.dataset.envToolbarBound = '1';
      _toolbar.addEventListener('mousedown', function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
      _toolbar.addEventListener('touchstart', function (e) {
        e.preventDefault();
        e.stopPropagation();
      }, { passive: false });
    }

    _bindEvents();
    if (imgUrl) _loadBackground(imgUrl);
    _log('canvas_init', { imgUrl: imgUrl });
  }

  function _disposeCanvas() {
    if (_canvas) {
      try { _canvas.dispose(); } catch (e) {}
    }
    _canvas = null;
    _bgImage = null;
    _bgLoaded = false;
    _origW = 0;
    _origH = 0;
    _bgScale = 1;
    _bgLeft = 0;
    _bgTop = 0;
    _elements = [];
    _lastSelected = null;
    _suppressClick = false;
    var toolbar = document.getElementById('canvas-toolbar');
    if (toolbar) toolbar.style.display = 'none';
    _updateCount();
  }

  // ───────────────── 背景图加载 ─────────────────

  function _loadBackground(url) {
    fabric.Image.fromURL(url, function (img, isError) {
      if (isError || !img || !img.width || !_canvas) {
        console.warn('[EnvCanvas] background image failed to load:', url);
        var fallback = document.getElementById('drag-canvas-fallback');
        if (fallback) {
          fallback.textContent = '图片加载失败，请返回重新上传';
          fallback.style.display = 'grid';
          fallback.style.zIndex = '2';
        }
        return;
      }

      var wrapper = document.getElementById('canvas-wrapper');
      var stage = wrapper && wrapper.parentElement ? wrapper.parentElement : wrapper;
      var availableW = (stage && stage.clientWidth) || (wrapper && wrapper.clientWidth) || _canvas.getWidth() || 440;
      var isTabletLandscape = window.matchMedia && window.matchMedia('(min-width: 900px) and (orientation: landscape)').matches;
      var maxHByViewport = Math.round(window.innerHeight * (isTabletLandscape ? 0.56 : 0.38));
      var maxH = Math.max(170, Math.min(maxHByViewport, window.innerHeight - (isTabletLandscape ? 270 : 330)));
      var scale = Math.min(availableW / img.width, maxH / img.height);
      if (!isFinite(scale) || scale <= 0) scale = availableW / img.width;
      var targetW = Math.max(80, Math.round(img.width * scale));
      var targetH = Math.max(80, Math.round(img.height * scale));
      targetW = Math.min(Math.round(availableW), targetW);
      targetH = Math.round(targetW * img.height / img.width);
      if (targetH > maxH) {
        targetH = maxH;
        targetW = Math.max(80, Math.round(targetH * img.width / img.height));
      }

      _canvas.setWidth(targetW);
      _canvas.setHeight(targetH);

      if (wrapper) {
        wrapper.style.width = targetW + 'px';
        wrapper.style.height = targetH + 'px';
        wrapper.style.maxWidth = '100%';
        wrapper.style.marginLeft = 'auto';
        wrapper.style.marginRight = 'auto';
      }

      _bgLeft = 0;
      _bgTop = 0;

      img.set({
        left: _bgLeft, top: _bgTop,
        scaleX: scale, scaleY: scale,
        selectable: false, evented: false,
        hasBorders: false, hasControls: false,
      });

      _canvas.add(img);
      _canvas.sendToBack(img);
      _bgImage = img;
      _origW = img.width;
      _origH = img.height;
      _bgScale = scale;
      _bgLoaded = true;
      img.setCoords();
      _canvas.renderAll();
    }, { crossOrigin: 'anonymous' });
  }

  // ───────────────── 事件绑定 ─────────────────

  function _bindEvents() {
    _canvas.on('selection:created', function (e) {
      _onSelect(e.selected && e.selected[0]);
    });
    _canvas.on('selection:updated', function (e) {
      _onSelect(e.selected && e.selected[0]);
    });
    _canvas.on('selection:cleared', _onDeselect);

    _canvas.on('mouse:down', function (e) {
      if (e.target && e.target !== _bgImage) {
        _lastSelected = e.target;
        _canvas.setActiveObject(e.target);
        _onSelect(e.target);
      }
    });
    _canvas.on('object:moving', function (e) {
      if (e.target !== _bgImage) {
        e.target.__envAction = 'move';
        _refreshObject(e.target);
        _updateToolbarPos(e.target);
      }
    });
    _canvas.on('object:scaling', function (e) {
      if (e.target !== _bgImage) {
        e.target.__envAction = 'scale';
        _refreshObject(e.target);
        _updateToolbarPos(e.target);
      }
    });
    _canvas.on('object:rotating', function (e) {
      if (e.target !== _bgImage) {
        e.target.__envAction = 'rotate';
        _refreshObject(e.target);
        _updateToolbarPos(e.target);
      }
    });
    _canvas.on('object:modified', function (e) {
      if (e.target !== _bgImage) {
        var action = e.target.__envAction || 'modify';
        delete e.target.__envAction;
        _refreshObject(e.target);
        _updateToolbarPos(e.target);
        _log(action, _getData(e.target));
      }
    });
  }

  function _refreshObject(obj) {
    if (!obj || !_canvas) return;
    if (typeof obj.setCoords === 'function') obj.setCoords();
    if (typeof _canvas.requestRenderAll === 'function') {
      _canvas.requestRenderAll();
    } else {
      _canvas.renderAll();
    }
  }

  function _applyInteractiveDefaults(obj) {
    if (!obj) return obj;
    obj.set({
      selectable: true,
      evented: true,
      hasControls: true,
      hasBorders: true,
      lockScalingFlip: true,
      perPixelTargetFind: false,
      padding: 8,
      hoverCursor: 'move',
      moveCursor: 'grabbing',
      cornerColor: '#2D6A4F',
      cornerStrokeColor: '#ffffff',
      cornerStyle: 'circle',
      cornerSize: 18,
      touchCornerSize: 28,
      transparentCorners: false,
      borderColor: '#52B788',
      borderDashArray: [5, 3],
      borderScaleFactor: 1.5,
    });
    if (typeof obj.setCoords === 'function') obj.setCoords();
    return obj;
  }

  function _onSelect(obj) {
    if (!obj || obj === _bgImage) return;
    _lastSelected = obj;
    var label = document.getElementById('selected-label');
    if (label) {
      label.textContent = '\u2713 ' + (obj.elemName || '\u5143\u7d20');
      label.style.color = '#2D6A4F';
      label.style.background = 'rgba(45,106,79,0.08)';
    }
    if (_toolbar) {
      _updateToolbarPos(obj);
      _toolbar.style.display = 'flex';
    }
  }

  function _onDeselect() {
    var label = document.getElementById('selected-label');
    if (label) {
      label.textContent = '\u672a\u9009\u4e2d';
      label.style.color = '#6B7280';
      label.style.background = 'rgba(107,114,128,0.08)';
    }
    if (_toolbar) _toolbar.style.display = 'none';
  }

  function _updateToolbarPos(obj) {
    if (!_toolbar || !obj || !_canvas) return;
    var b = obj.getBoundingRect();
    var top = b.top - 52;
    var left = b.left + b.width / 2;
    if (top < 4) top = b.top + b.height + 8;
    var cw = _canvas.getWidth();
    if (left < 64) left = 64;
    if (left > cw - 64) left = cw - 64;
    _toolbar.style.top = top + 'px';
    _toolbar.style.left = left + 'px';
  }

  // ───────────────── 元素操作 ─────────────────

  function addByIndex(idx) {
    if (_suppressClick) return;
    var data = (window._ELEMENTS || [])[idx];
    if (!data) return;

    document.querySelectorAll('.elem-card').forEach(function (c) {
      c.classList.remove('elem-selected');
    });
    var card = document.querySelector('.elem-card[data-idx="' + idx + '"]');
    if (card) card.classList.add('elem-selected');

    addElement(data.dataUrl, data.icon, data.name, data.cat);
  }

  function addAtPosition(idx, canvasX, canvasY) {
    var data = (window._ELEMENTS || [])[idx];
    if (!data) return;

    document.querySelectorAll('.elem-card').forEach(function (c) {
      c.classList.remove('elem-selected');
    });
    var card = document.querySelector('.elem-card[data-idx="' + idx + '"]');
    if (card) card.classList.add('elem-selected');

    addElement(data.dataUrl, data.icon, data.name, data.cat, canvasX, canvasY);
  }

  function addElement(svgDataUrl, icon, name, cat, atX, atY) {
    if (!_canvas) {
      _toast('画布尚未准备好，请稍后再试', 'warn');
      return;
    }
    if (!_bgLoaded) {
      _toast('图片仍在加载，请稍后放置元素', 'warn');
      return;
    }
    if (_elements.length >= MAX_ELEMENTS) {
      _toast('\u6700\u591a\u653e\u7f6e ' + MAX_ELEMENTS + ' \u4e2a\u5143\u7d20', 'warn');
      return;
    }
    if (!svgDataUrl) return;

    var cw = _canvas ? _canvas.getWidth() : 440;
    var ch = _canvas ? _canvas.getHeight() : 330;
    var cx = (atX !== undefined) ? atX : cw / 2 + (Math.random() - 0.5) * cw * 0.35;
    var cy = (atY !== undefined) ? atY : ch * 0.4 + (Math.random() - 0.5) * ch * 0.3;

    fabric.loadSVGFromURL(svgDataUrl, function (objs, opts) {
      if (!objs || !objs.length) return;
      var g = fabric.util.groupSVGElements(objs, opts);

      var targetSize = cw * 0.13;
      var srcSize = Math.max(g.width || 60, g.height || 60);
      var s = targetSize / srcSize;

      g.set({
        left: cx, top: cy,
        scaleX: s, scaleY: s,
        originX: 'center', originY: 'center',
        elemIcon: icon,
        elemName: name,
        elemCat: cat || '',
        elemId: 'el_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
      });
      _applyInteractiveDefaults(g);

      _canvas.add(g);
      _canvas.setActiveObject(g);
      _lastSelected = g;
      _elements.push(g);
      _updateCount();
      _animateIn(g);
      _log('place', _getData(g));
    });
  }

  function _animateIn(obj) {
    var tx = obj.scaleX, ty = obj.scaleY;
    obj.set({ scaleX: tx * 0.4, scaleY: ty * 0.4, opacity: 0 });
    obj.animate({ scaleX: tx * 1.12, scaleY: ty * 1.12, opacity: 1 }, {
      duration: 180,
      easing: fabric.util.ease.easeOutCubic,
      onChange: function () { _refreshObject(obj); },
      onComplete: function () {
        obj.animate({ scaleX: tx, scaleY: ty }, {
          duration: 100,
          onChange: function () { _refreshObject(obj); },
          onComplete: function () {
            _refreshObject(obj);
            _canvas && _canvas.setActiveObject(obj);
            _onSelect(obj);
          },
        });
      },
    });
  }

  function deleteSelected() {
    var a = (_canvas && _canvas.getActiveObject()) || _lastSelected;
    if (!a || a === _bgImage) return;
    _log('delete', _getData(a));
    var i = _elements.indexOf(a);
    if (i !== -1) _elements.splice(i, 1);
    _canvas.remove(a);
    _lastSelected = null;
    _canvas.discardActiveObject();
    _canvas.renderAll();
    _updateCount();
    if (_toolbar) _toolbar.style.display = 'none';
  }

  function duplicateSelected() {
    var a = (_canvas && _canvas.getActiveObject()) || _lastSelected;
    if (!a || a === _bgImage) return;
    if (_elements.length >= MAX_ELEMENTS) {
      _toast('\u5df2\u8fbe\u6700\u5927\u5143\u7d20\u6570', 'warn');
      return;
    }
    a.clone(function (c) {
      c.set({
        left: a.left + 28, top: a.top + 28,
        elemIcon: a.elemIcon, elemName: a.elemName, elemCat: a.elemCat,
        elemId: 'el_' + Date.now() + '_dup',
      });
      _applyInteractiveDefaults(c);
      _canvas.add(c);
      _canvas.setActiveObject(c);
      _lastSelected = c;
      _elements.push(c);
      _refreshObject(c);
      _updateCount();
      _log('duplicate', _getData(c));
    });
  }

  function bringToFront() {
    var a = (_canvas && _canvas.getActiveObject()) || _lastSelected;
    if (a && a !== _bgImage) {
      _canvas.bringToFront(a);
      _canvas.renderAll();
    }
  }

  function clearAll() {
    if (!_canvas) return;
    _elements.forEach(function (o) { _canvas.remove(o); });
    _elements = [];
    _canvas.discardActiveObject();
    _canvas.renderAll();
    _updateCount();
    if (_toolbar) _toolbar.style.display = 'none';
    document.querySelectorAll('.elem-card').forEach(function (c) {
      c.classList.remove('elem-selected');
    });
    _log('clear_all', {});
  }

  function _ensureClearModal() {
    var modal = document.getElementById('drag-clear-confirm');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'drag-clear-confirm';
    modal.className = 'drag-clear-confirm';
    modal.innerHTML = [
      '<div class="drag-clear-sheet" role="dialog" aria-modal="true">',
      '<div class="drag-clear-title">确认清除当前画布？</div>',
      '<div class="drag-clear-text">画布上的元素会被全部移除，此操作不会删除原始环境照片。</div>',
      '<div class="drag-clear-actions">',
      '<button type="button" class="secondary" data-action="cancel">取消</button>',
      '<button type="button" class="danger" data-action="confirm">清除</button>',
      '</div>',
      '</div>',
    ].join('');
    modal.addEventListener('click', function (e) {
      if (e.target === modal || (e.target && e.target.getAttribute('data-action') === 'cancel')) {
        modal.classList.remove('visible');
      }
      if (e.target && e.target.getAttribute('data-action') === 'confirm') {
        modal.classList.remove('visible');
        clearAll();
      }
    });
    document.body.appendChild(modal);
    return modal;
  }

  function requestClearAll() {
    if (!_canvas) return;
    _ensureClearModal().classList.add('visible');
  }

  // ───────────────── 布局序列化（提交给AI生成）─────────────────

  function getLayoutJSON() {
    return JSON.stringify(_buildLayout());
  }

  function _buildLayout() {
    if (!_canvas || !_bgLoaded) return [];
    var bW = _origW * _bgScale || 1;
    var bH = _origH * _bgScale || 1;
    return _elements.map(function (o) {
      var b = o.getBoundingRect();
      var cx = b.left + b.width / 2;
      var cy = b.top + b.height / 2;
      return {
        icon: o.elemIcon || '',
        name: o.elemName || '',
        category: o.elemCat || '',
        x: Math.round((cx - _bgLeft) / bW * 1000) / 10,
        y: Math.round((cy - _bgTop) / bH * 1000) / 10,
        scale: Math.round((o.scaleX || 1) * 100) / 100,
        scaleToBg: Math.round(((o.scaleX || 1) / (_bgScale || 1)) * 1000) / 1000,
        widthPct: Math.round((b.width / bW) * 1000) / 10,
        heightPct: Math.round((b.height / bH) * 1000) / 10,
        rotation: Math.round(o.angle || 0),
        elemId: o.elemId || '',
        stackIndex: index,
      };
    });
  }

  function getElementCount() { return _elements.length; }

  // ───────────────── 内部工具 ─────────────────

  function _getData(o) {
    if (!o) return {};
    var b = o.getBoundingRect();
    var bW = _origW * _bgScale || 1;
    var bH = _origH * _bgScale || 1;
    return {
      elemId: o.elemId || '', icon: o.elemIcon || '', name: o.elemName || '', category: o.elemCat || '',
      x_pct: Math.round((b.left + b.width / 2 - _bgLeft) / bW * 1000) / 10,
      y_pct: Math.round((b.top + b.height / 2 - _bgTop) / bH * 1000) / 10,
      scale: Math.round((o.scaleX || 1) * 100) / 100,
      rotation: Math.round(o.angle || 0),
      ts_ms: Date.now(),
    };
  }

  function _updateCount() {
    var el = document.getElementById('element-count');
    if (el) el.textContent = '\u5df2\u653e\u7f6e: ' + _elements.length + ' \u4e2a';
  }

  function _clearRestoredElements() {
    if (!_canvas) return;
    _elements.forEach(function (o) {
      try { _canvas.remove(o); } catch (e) {}
    });
    _elements = [];
    _canvas.discardActiveObject();
    if (_toolbar) _toolbar.style.display = 'none';
    _updateCount();
  }

  function _findElementAsset(item) {
    var list = window._ELEMENTS || [];
    if (!item || !list.length) return null;
    return list.find(function (el) {
      return (item.name && el.name === item.name) ||
             (item.icon && el.icon === item.icon && (!item.category || el.cat === item.category));
    }) || null;
  }

  function _clampPct(value) {
    value = Number(value);
    if (!isFinite(value)) return 50;
    return Math.max(0, Math.min(100, value));
  }

  function _keepObjectInsideCanvas(obj) {
    if (!obj || !_canvas) return;
    obj.setCoords();
    var b = obj.getBoundingRect();
    var pad = 4;
    var dx = 0, dy = 0;
    if (b.left < pad) dx = pad - b.left;
    if (b.top < pad) dy = pad - b.top;
    if (b.left + b.width > _canvas.getWidth() - pad) dx = (_canvas.getWidth() - pad) - (b.left + b.width);
    if (b.top + b.height > _canvas.getHeight() - pad) dy = (_canvas.getHeight() - pad) - (b.top + b.height);
    if (dx || dy) obj.set({ left: (obj.left || 0) + dx, top: (obj.top || 0) + dy });
    obj.setCoords();
  }

  function _restoreFromLayout(layout) {
    if (!_canvas || !_bgLoaded || !Array.isArray(layout) || !layout.length) return false;
    var bW = _origW * _bgScale || _canvas.getWidth();
    var bH = _origH * _bgScale || _canvas.getHeight();
    var pending = 0;
    var restored = 0;
    var restoredItems = [];
    var source = layout.slice(0, MAX_ELEMENTS);
    source.forEach(function (item, i) {
      var data = _findElementAsset(item);
      if (!data || !data.dataUrl) return;
      pending += 1;
      fabric.loadSVGFromURL(data.dataUrl, function (objs, opts) {
        pending -= 1;
        if (!objs || !objs.length || !_canvas) return;
        var g = fabric.util.groupSVGElements(objs, opts);
        var cx = _bgLeft + _clampPct(item.x) / 100 * bW;
        var cy = _bgTop + _clampPct(item.y) / 100 * bH;
        var srcSize = Math.max(g.width || 60, g.height || 60);
        var defaultScale = (_canvas.getWidth() * 0.13) / srcSize;
        var hasRelativeScale = Number(item.scaleToBg) > 0 || Number(item.widthPct) > 0 || Number(item.scale) > 0;
        var targetScale = Number(item.scaleToBg) > 0
          ? Number(item.scaleToBg) * _bgScale
          : (Number(item.scale) > 0 ? Number(item.scale) : defaultScale);
        if (Number(item.widthPct) > 0 && g.width) {
          targetScale = Math.max(0.03, (Number(item.widthPct) / 100 * bW) / g.width);
        }
        if (!hasRelativeScale) {
          targetScale = Math.min(targetScale, defaultScale * 2.35);
        }
        g.set({
          left: cx,
          top: cy,
          scaleX: targetScale,
          scaleY: targetScale,
          angle: Math.round(Number(item.rotation) || 0),
          originX: 'center',
          originY: 'center',
          elemIcon: item.icon || data.icon || '',
          elemName: item.name || data.name || '',
          elemCat: item.category || data.cat || '',
          elemId: item.elemId || ('el_r_' + Date.now() + '_' + i),
        });
        _applyInteractiveDefaults(g);
        _keepObjectInsideCanvas(g);
        restoredItems.push({ index: i, item: item, object: g });
        restored += 1;
        if (!pending) {
          restoredItems.sort(function (a, b) {
            var stackA = Number(a.item && a.item.stackIndex);
            var stackB = Number(b.item && b.item.stackIndex);
            if (!isFinite(stackA)) stackA = a.index;
            if (!isFinite(stackB)) stackB = b.index;
            return stackA - stackB;
          });
          restoredItems.forEach(function (row) {
            _canvas.add(row.object);
            _elements.push(row.object);
          });
          _canvas.renderAll();
          _updateCount();
        }
      });
    });
    return pending > 0 || restored > 0;
  }

  function _parseFallbackLayout(fallbackLayout) {
    if (Array.isArray(fallbackLayout)) return fallbackLayout;
    if (typeof fallbackLayout === 'string' && fallbackLayout) {
      try {
        var parsed = JSON.parse(fallbackLayout);
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        return [];
      }
    }
    return [];
  }

  function _log(action, data) {
    if (!_sessionId) return;
    fetch('/api/log/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: _sessionId, action: action, data: data, ts_ms: Date.now() }),
      keepalive: true,
    }).catch(function () {});
  }

  function _toast(msg, type) {
    var t = document.createElement('div');
    t.textContent = msg;
    t.style.cssText = [
      'position:fixed;top:72px;left:50%;transform:translateX(-50%);',
      'background:' + (type === 'warn' ? '#D4A373' : '#2D6A4F') + ';color:white;',
      'padding:8px 18px;border-radius:20px;font-size:13px;z-index:9999;',
      'box-shadow:0 4px 16px rgba(0,0,0,0.15);pointer-events:none;',
    ].join('');
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  }

  // ───────────────── 拖拽放置（桌面 + 移动端）─────────────────

  function initDragDrop() {
    var wrapper = document.getElementById('canvas-wrapper');
    if (!wrapper || !_canvas) return;
    _dragWrapper = wrapper;

    // --- HTML5 Drag & Drop (desktop) ---
    if (!wrapper.dataset.envDropBound) {
      wrapper.dataset.envDropBound = '1';
      wrapper.addEventListener('dragover', function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        wrapper.classList.add('canvas-drag-over');
      });
      wrapper.addEventListener('dragleave', function () {
        wrapper.classList.remove('canvas-drag-over');
      });
      wrapper.addEventListener('drop', function (e) {
        e.preventDefault();
        wrapper.classList.remove('canvas-drag-over');
        var idx = parseInt(e.dataTransfer.getData('text/plain'), 10);
        if (isNaN(idx)) return;
        var p = _clientToCanvasPoint(e.clientX, e.clientY);
        addAtPosition(idx, p.x, p.y);
      });
    }

    document.querySelectorAll('.elem-card').forEach(function (card) {
      card.setAttribute('draggable', 'true');
      if (card.dataset.envDragBound) return;
      card.dataset.envDragBound = '1';
      card.addEventListener('dragstart', function (e) {
        e.dataTransfer.setData('text/plain', card.getAttribute('data-idx'));
        e.dataTransfer.effectAllowed = 'copy';
        card.classList.add('elem-dragging');
      });
      card.addEventListener('dragend', function () {
        card.classList.remove('elem-dragging');
      });
    });

    // --- Touch Drag (mobile) ---
    document.querySelectorAll('.elem-card').forEach(function (card) {
      if (card.dataset.envTouchBound) return;
      card.dataset.envTouchBound = '1';
      card.addEventListener('touchstart', function (e) {
        var t = e.touches[0];
        _touchDragIdx = parseInt(card.getAttribute('data-idx'), 10);
        _touchStartX = t.clientX;
        _touchStartY = t.clientY;
        _touchDragging = false;
        _touchDragCard = card;
      }, { passive: true });
    });

    _bindGlobalTouchDrag();
  }

  function _clientToCanvasPoint(clientX, clientY) {
    var el = _canvas && (_canvas.upperCanvasEl || _canvas.getElement());
    if (!el) return { x: clientX, y: clientY };
    var rect = el.getBoundingClientRect();
    var scaleX = rect.width ? _canvas.getWidth() / rect.width : 1;
    var scaleY = rect.height ? _canvas.getHeight() / rect.height : 1;
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  }

  function _bindGlobalTouchDrag() {
    if (_globalTouchBound) return;
    _globalTouchBound = true;

    document.addEventListener('touchmove', function (e) {
      if (_touchDragIdx < 0 || !_dragWrapper) return;
      var t = e.touches[0];

      if (!_touchDragging) {
        var dx = t.clientX - _touchStartX, dy = t.clientY - _touchStartY;
        if (Math.sqrt(dx * dx + dy * dy) < TOUCH_DRAG_THRESHOLD) return;
        _touchDragging = true;
        _suppressClick = true;
        if (_touchDragCard) _touchDragCard.classList.add('elem-dragging');

        var data = (window._ELEMENTS || [])[_touchDragIdx];
        _touchGhost = document.createElement('div');
        _touchGhost.className = 'drag-ghost';
        _touchGhost.innerHTML = data && data.dataUrl
          ? '<img src="' + data.dataUrl + '" style="width:48px;height:48px;object-fit:contain;">'
          : '<span style="font-size:32px;">' + (data ? data.icon : '') + '</span>';
        document.body.appendChild(_touchGhost);
      }

      if (_touchDragging && _touchGhost) {
        e.preventDefault();
        _touchGhost.style.left = t.clientX + 'px';
        _touchGhost.style.top = t.clientY + 'px';

        var wr = _dragWrapper.getBoundingClientRect();
        var over = t.clientX >= wr.left && t.clientX <= wr.right &&
                   t.clientY >= wr.top && t.clientY <= wr.bottom;
        _dragWrapper.classList.toggle('canvas-drag-over', over);
      }
    }, { passive: false });

    document.addEventListener('touchend', function () {
      if (_touchDragIdx < 0) return;

      if (_touchDragging && _touchGhost && _canvas) {
        var last = _touchGhost.getBoundingClientRect();
        var cx = last.left + last.width / 2;
        var cy = last.top + last.height / 2;
        var rect = (_canvas.upperCanvasEl || _canvas.getElement()).getBoundingClientRect();

        if (cx >= rect.left && cx <= rect.right && cy >= rect.top && cy <= rect.bottom) {
          var p = _clientToCanvasPoint(cx, cy);
          addAtPosition(_touchDragIdx, p.x, p.y);
        }

        _touchGhost.remove();
        _touchGhost = null;
        if (_dragWrapper) _dragWrapper.classList.remove('canvas-drag-over');
        if (_touchDragCard) _touchDragCard.classList.remove('elem-dragging');
        setTimeout(function () { _suppressClick = false; }, 100);
      } else {
        _suppressClick = false;
      }

      _touchDragIdx = -1;
      _touchDragging = false;
      _touchDragCard = null;
    });
  }

  return {
    init: init,
    addByIndex: addByIndex,
    addAtPosition: addAtPosition,
    addElement: addElement,
    deleteSelected: deleteSelected,
    duplicateSelected: duplicateSelected,
    bringToFront: bringToFront,
    clearAll: clearAll,
    requestClearAll: requestClearAll,
    getLayoutJSON: getLayoutJSON,
    getElementCount: getElementCount,
    isBackgroundLoaded: function() { return _bgLoaded; },
    initDragDrop: initDragDrop,
    getCanvasDataURL: function(maxMultiplier) {
      if (!_canvas) return '';
      _canvas.discardActiveObject();
      _canvas.renderAll();
      maxMultiplier = Number(maxMultiplier || 4);
      if (!isFinite(maxMultiplier) || maxMultiplier <= 0) maxMultiplier = 4;
      var multiplier = 1;
      if (_origW && _canvas.getWidth && _canvas.getWidth() > 0) {
        multiplier = Math.max(1, Math.min(maxMultiplier, _origW / _canvas.getWidth()));
      } else if (_bgScale > 0) {
        multiplier = Math.max(1, Math.min(maxMultiplier, 1 / _bgScale));
      }
      return _canvas.toDataURL({ format: 'png', multiplier: multiplier });
    },
    uploadCanvasSnapshot: async function(sessionId, maxMultiplier) {
      var dataUrl = this.getCanvasDataURL(maxMultiplier);
      if (!dataUrl) return JSON.stringify({ ok: false, error: 'empty canvas' });
      var resp = await fetch('/api/canvas-snapshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, data_url: dataUrl }),
      });
      var data = await resp.json().catch(function() { return {}; });
      if (!resp.ok) {
        return JSON.stringify({ ok: false, error: data.error || ('HTTP ' + resp.status) });
      }
      return JSON.stringify(data);
    },
    getObjectsJSON: function() {
      if (!_canvas) return '[]';
      return JSON.stringify({
        version: 2,
        background: {
          width: _canvas.getWidth(),
          height: _canvas.getHeight(),
          imageWidth: _origW,
          imageHeight: _origH,
          scale: _bgScale,
          left: _bgLeft,
          top: _bgTop,
        },
        layout: _buildLayout(),
        objects: _elements.map(function(o) {
          return o.toObject(['elemIcon', 'elemName', 'elemCat', 'elemId']);
        }),
      });
    },
    restoreObjects: function(jsonStr, fallbackLayout) {
      if (!_canvas) return;
      var fallback = _parseFallbackLayout(fallbackLayout);
      if (!jsonStr && fallback.length) {
        _clearRestoredElements();
        _restoreFromLayout(fallback);
        return;
      }
      if (!jsonStr) return;
      try {
        var parsed = JSON.parse(jsonStr);
      } catch(e) { return; }
      var layout = [];
      var objDataList = [];
      if (parsed && parsed.version === 2) {
        layout = Array.isArray(parsed.layout) ? parsed.layout : [];
        objDataList = Array.isArray(parsed.objects) ? parsed.objects : [];
      } else if (Array.isArray(parsed)) {
        objDataList = parsed;
      }

      if (fallback.length) layout = fallback;
      if (layout.length) {
        _clearRestoredElements();
        if (_restoreFromLayout(layout)) return;
      }
      if (!objDataList || !objDataList.length) return;

      _clearRestoredElements();
      fabric.util.enlivenObjects(objDataList, function(objs) {
        objs.forEach(function(obj, i) {
          var raw = objDataList[i] || {};
          obj.set({
            elemIcon: raw.elemIcon || '',
            elemName: raw.elemName || '',
            elemCat: raw.elemCat || '',
            elemId: raw.elemId || ('el_r_' + Date.now() + '_' + i),
          });
          _applyInteractiveDefaults(obj);
          _canvas.add(obj);
          _elements.push(obj);
          _refreshObject(obj);
        });
        _canvas.renderAll();
        _updateCount();
      });
    },
    _debugCanvas: function() { return _canvas; },
  };
})();
