/**
 * SketchAnalyzer — 手绘笔迹分析器（形状语义版 v2）
 *
 * 核心架构：形状语义优先 + 颜色作为色调修饰
 *   1. _classifyShape()   — 将笔迹归类为9种基础语义形状
 *   2. SHAPE_ZONE_ELEMENTS — 形状×区域矩阵，决定元素候选列表
 *   3. COLOR_ELEMENT_PREFERENCE — 颜色从候选列表中选出最终元素
 *   4. COLOR_TINT_LABEL  — 颜色注入色调描述词，传给 Prompt
 *   5. _resolveElement() — 统一入口
 *   6. _findNearestColorPref() — 自定义颜色模糊匹配到最近预设色
 */
window.SketchAnalyzer = (function () {
  'use strict';

  // ─── 区域常量 ────────────────────────────────────────────────
  var ZONE_SKY = 'sky';
  var ZONE_MID = 'midground';
  var ZONE_GND = 'ground';

  function _getZone(yPct) {
    if (yPct < 32) return ZONE_SKY;
    if (yPct < 68) return ZONE_MID;
    return ZONE_GND;
  }

  // ─── 形状语义类型（9 种）─────────────────────────────────────
  var SHAPE_ROUND     = 'round';
  var SHAPE_TALL      = 'tall';
  var SHAPE_WIDE      = 'wide';
  var SHAPE_DOT       = 'dot';
  var SHAPE_WAVE      = 'wave';
  var SHAPE_ENCLOSURE = 'enclosure';
  var SHAPE_ZIGZAG    = 'zigzag';
  var SHAPE_SPIRAL    = 'spiral';
  var SHAPE_FREE      = 'free';

  function _isEnclosed(pts) {
    if (!pts || pts.length < 8) return false;
    var first = pts[0], last = pts[pts.length - 1];
    var xs = pts.map(function (p) { return p.x; });
    var ys = pts.map(function (p) { return p.y; });
    var span = Math.max(
      Math.max.apply(null, xs) - Math.min.apply(null, xs),
      Math.max.apply(null, ys) - Math.min.apply(null, ys)
    );
    if (span < 10) return false;
    var dist = Math.sqrt(Math.pow(last.x - first.x, 2) + Math.pow(last.y - first.y, 2));
    return dist / span < 0.38;
  }

  /**
   * 计算方向变化频率（用于 zigzag 检测）
   * 返回每单位路径长度的方向反转次数
   */
  function _directionChangeRate(pts) {
    if (pts.length < 5) return 0;
    var reversals = 0;
    var prevDy = 0;
    for (var i = 2; i < pts.length; i++) {
      var dy = pts[i].y - pts[i - 2].y;
      if (prevDy !== 0 && dy !== 0 && ((prevDy > 0 && dy < 0) || (prevDy < 0 && dy > 0))) {
        reversals++;
      }
      if (dy !== 0) prevDy = dy;
    }
    return reversals / (pts.length / 10);
  }

  /**
   * 检测螺旋：累积角度变化超过 2π 且非封闭
   */
  function _isSpiralLike(pts, f) {
    if (pts.length < 15) return false;
    var totalAngle = 0;
    for (var i = 2; i < pts.length; i++) {
      var dx1 = pts[i - 1].x - pts[i - 2].x;
      var dy1 = pts[i - 1].y - pts[i - 2].y;
      var dx2 = pts[i].x - pts[i - 1].x;
      var dy2 = pts[i].y - pts[i - 1].y;
      var cross = dx1 * dy2 - dy1 * dx2;
      var dot = dx1 * dx2 + dy1 * dy2;
      var len1 = Math.sqrt(dx1 * dx1 + dy1 * dy1);
      var len2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
      if (len1 > 0.5 && len2 > 0.5) {
        totalAngle += Math.atan2(cross, dot);
      }
    }
    return Math.abs(totalAngle) > Math.PI * 1.6;
  }

  /**
   * 将笔迹特征归类为9种形状语义
   */
  function _classifyShape(f, pts, canvasW) {
    var maxDim = Math.max(f.bboxW, f.bboxH);
    if (f.pointCount < 20 || maxDim < (canvasW || 400) * 0.07) {
      return SHAPE_DOT;
    }

    if (_isEnclosed(pts)) {
      return SHAPE_ENCLOSURE;
    }

    if (_isSpiralLike(pts, f) && f.aspectRatio > 0.4 && f.aspectRatio < 2.5) {
      return SHAPE_SPIRAL;
    }

    var dcr = _directionChangeRate(pts);
    if (dcr > 0.8 && f.waviness > 0.25 && f.straightness < 0.5) {
      return SHAPE_ZIGZAG;
    }

    if (f.horizontalness > 2.0 && f.waviness > 0.2) {
      return SHAPE_WAVE;
    }

    if (f.horizontalness > 2.0 && f.waviness <= 0.2) {
      return SHAPE_WIDE;
    }

    if (f.aspectRatio < 0.55) {
      return SHAPE_TALL;
    }

    if (f.circularity > 0.22 && f.aspectRatio > 0.45 && f.aspectRatio < 2.2) {
      return SHAPE_ROUND;
    }

    return SHAPE_FREE;
  }

  // ─── 形状语义 × 区域 → 候选元素列表（扩充版）──────────────────
  var SHAPE_ZONE_ELEMENTS = {
    round: {
      sky:        [{ name: '太阳', icon: '☀️' }, { name: '月亮', icon: '🌙' }, { name: '热气球', icon: '🎈' }, { name: '云团', icon: '☁️' }],
      midground:  [{ name: '大树', icon: '🌳' }, { name: '树冠', icon: '🌲' }, { name: '灌木球', icon: '🌿' }, { name: '花坛', icon: '🌸' }],
      ground:     [{ name: '花坛', icon: '🌸' }, { name: '池塘', icon: '🏞️' }, { name: '石头', icon: '🪨' }, { name: '蘑菇', icon: '🍄' }],
    },
    tall: {
      sky:        [{ name: '树梢', icon: '🌲' }, { name: '塔尖', icon: '🗼' }],
      midground:  [{ name: '树干', icon: '🌲' }, { name: '路灯', icon: '🔦' }, { name: '竹子', icon: '🎋' }, { name: '立柱', icon: '🏛️' }],
      ground:     [{ name: '树桩', icon: '🌲' }, { name: '路灯', icon: '🔦' }, { name: '栅栏柱', icon: '🏗️' }],
    },
    wide: {
      sky:        [{ name: '远山', icon: '🏔️' }, { name: '云带', icon: '☁️' }, { name: '天际线', icon: '🌅' }],
      midground:  [{ name: '草坪', icon: '🌿' }, { name: '灌木带', icon: '🌿' }, { name: '矮墙', icon: '🧱' }],
      ground:     [{ name: '水面', icon: '🌊' }, { name: '草坪', icon: '🌿' }, { name: '铺装路面', icon: '🛤️' }, { name: '台阶', icon: '🪜' }],
    },
    dot: {
      sky:        [{ name: '飞鸟', icon: '🕊️' }, { name: '星点', icon: '✨' }, { name: '蝴蝶', icon: '🦋' }],
      midground:  [{ name: '花点', icon: '🌺' }, { name: '叶片', icon: '🍃' }, { name: '萤火虫', icon: '✨' }],
      ground:     [{ name: '花朵', icon: '🌺' }, { name: '石子', icon: '🪨' }, { name: '落叶', icon: '🍂' }, { name: '蘑菇', icon: '🍄' }],
    },
    wave: {
      sky:        [{ name: '彩云', icon: '🌤️' }, { name: '飘带云', icon: '☁️' }],
      midground:  [{ name: '小溪', icon: '🌊' }, { name: '藤蔓', icon: '🌿' }, { name: '树根', icon: '🌿' }],
      ground:     [{ name: '小溪', icon: '🌊' }, { name: '小径', icon: '🛤️' }, { name: '溪流', icon: '💧' }],
    },
    enclosure: {
      sky:        [{ name: '圆形云', icon: '☁️' }, { name: '光环', icon: '💫' }],
      midground:  [{ name: '树丛', icon: '🌳' }, { name: '灌木围合', icon: '🌿' }, { name: '花圃', icon: '🌸' }],
      ground:     [{ name: '池塘', icon: '🏞️' }, { name: '花坛', icon: '🌸' }, { name: '喷泉池', icon: '⛲' }],
    },
    zigzag: {
      sky:        [{ name: '远山', icon: '🏔️' }, { name: '山脉轮廓', icon: '⛰️' }, { name: '闪电', icon: '⚡' }],
      midground:  [{ name: '栅栏', icon: '🏗️' }, { name: '屋顶', icon: '🏠' }, { name: '灌木丛', icon: '🌿' }],
      ground:     [{ name: '碎石路', icon: '🪨' }, { name: '栅栏', icon: '🏗️' }, { name: '台阶', icon: '🪜' }],
    },
    spiral: {
      sky:        [{ name: '漩涡云', icon: '🌀' }, { name: '太阳光芒', icon: '☀️' }],
      midground:  [{ name: '花朵', icon: '🌸' }, { name: '藤蔓', icon: '🌿' }, { name: '装饰雕塑', icon: '🎨' }],
      ground:     [{ name: '花朵', icon: '🌺' }, { name: '喷泉', icon: '⛲' }, { name: '螺旋花坛', icon: '🌸' }],
    },
    free: {
      sky:        [{ name: '天空氛围', icon: '🌤️' }, { name: '晚霞', icon: '🌇' }],
      midground:  [{ name: '植被', icon: '🌿' }, { name: '绿化带', icon: '🌱' }],
      ground:     [{ name: '地面氛围', icon: '🌱' }, { name: '野草', icon: '🌾' }],
    },
  };

  // ─── 预设颜色偏好 ─────────────────────────────────────────────
  var PRESET_COLORS = [
    { hex: '#2D6A4F', h: 153, s: 39, l: 31 },
    { hex: '#52B788', h: 153, s: 38, l: 52 },
    { hex: '#3A86FF', h: 218, s: 100, l: 61 },
    { hex: '#E76F51', h: 13,  s: 77,  l: 61 },
    { hex: '#8B5CF6', h: 263, s: 90,  l: 66 },
    { hex: '#1A1A2E', h: 240, s: 26,  l: 14 },
  ];

  var COLOR_ELEMENT_PREFERENCE = {
    '#2D6A4F': { prefer: ['大树', '树干', '草坪', '灌木带', '树丛', '植被', '树冠', '竹子', '灌木球'] },
    '#52B788': { prefer: ['大树', '草坪', '灌木带', '树丛', '花朵', '花点', '灌木球', '蘑菇', '藤蔓'] },
    '#3A86FF': { prefer: ['小溪', '水面', '池塘', '云带', '彩云', '喷泉', '飘带云', '溪流', '喷泉池'] },
    '#E76F51': { prefer: ['花朵', '花坛', '花点', '太阳', '落叶', '太阳光芒', '热气球', '晚霞'] },
    '#8B5CF6': { prefer: ['花朵', '花坛', '飞鸟', '花点', '灌木围合', '蝴蝶', '漩涡云', '装饰雕塑', '花圃'] },
    '#1A1A2E': { prefer: ['飞鸟', '树梢', '远山', '小径', '山脉轮廓', '栅栏', '台阶'] },
  };

  // ─── 颜色 → 色调描述词（扩充版）──────────────────────────────
  var COLOR_TINT_LABEL = {
    '#2D6A4F': '深绿葱郁',
    '#52B788': '清新翠绿',
    '#3A86FF': '清澈蓝色',
    '#E76F51': '暖橙秋色',
    '#8B5CF6': '浪漫紫调',
    '#1A1A2E': '深色剪影',
    '#E9C46A': '温暖金黄',
    '#F4A261': '柔和橘调',
    '#FFB4A2': '柔粉暖色',
    '#A8DADC': '浅碧清透',
    '#457B9D': '深蓝沉静',
    '#F1FAEE': '素白清雅',
    '#D4A373': '大地棕调',
    '#CCD5AE': '灰绿柔和',
  };

  // ─── 颜色模糊匹配（支持自定义颜色）────────────────────────────

  function _hexToHsl(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    var r = parseInt(hex.substring(0, 2), 16) / 255;
    var g = parseInt(hex.substring(2, 4), 16) / 255;
    var b = parseInt(hex.substring(4, 6), 16) / 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h = 0, s = 0, l = (max + min) / 2;
    if (max !== min) {
      var d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
      else if (max === g) h = ((b - r) / d + 2) * 60;
      else h = ((r - g) / d + 4) * 60;
    }
    return { h: Math.round(h), s: Math.round(s * 100), l: Math.round(l * 100) };
  }

  function _hslDistance(a, b) {
    var dh = Math.min(Math.abs(a.h - b.h), 360 - Math.abs(a.h - b.h));
    return dh * 1.0 + Math.abs(a.s - b.s) * 0.6 + Math.abs(a.l - b.l) * 0.8;
  }

  function _findNearestColorPref(hex) {
    if (COLOR_ELEMENT_PREFERENCE[hex]) return hex;
    var hsl = _hexToHsl(hex);
    var bestHex = PRESET_COLORS[0].hex;
    var bestDist = Infinity;
    for (var i = 0; i < PRESET_COLORS.length; i++) {
      var d = _hslDistance(hsl, PRESET_COLORS[i]);
      if (d < bestDist) { bestDist = d; bestHex = PRESET_COLORS[i].hex; }
    }
    return bestHex;
  }

  function _getTintLabel(hex) {
    if (COLOR_TINT_LABEL[hex]) return COLOR_TINT_LABEL[hex];
    var hsl = _hexToHsl(hex);
    if (hsl.s < 10) return hsl.l > 60 ? '素白清雅' : '深灰沉稳';
    if (hsl.h < 30 || hsl.h >= 345) return hsl.l > 55 ? '柔粉暖色' : '深红沉郁';
    if (hsl.h < 50) return hsl.l > 55 ? '温暖金黄' : '深棕质朴';
    if (hsl.h < 80) return hsl.l > 55 ? '嫩黄明亮' : '橄榄沉稳';
    if (hsl.h < 170) return hsl.l > 45 ? '清新翠绿' : '深绿葱郁';
    if (hsl.h < 250) return hsl.l > 50 ? '清澈蓝色' : '深蓝沉静';
    if (hsl.h < 300) return hsl.l > 50 ? '浪漫紫调' : '深紫神秘';
    return hsl.l > 50 ? '玫粉柔美' : '酒红深沉';
  }

  // ─── 颜色偏好匹配函数 ─────────────────────────────────────────

  function _pickByColor(candidates, strokeColor) {
    if (!strokeColor) return candidates[0];
    var prefKey = _findNearestColorPref(strokeColor);
    var prefs = COLOR_ELEMENT_PREFERENCE[prefKey];
    if (!prefs) return candidates[0];
    var prefList = prefs.prefer;
    for (var i = 0; i < prefList.length; i++) {
      for (var j = 0; j < candidates.length; j++) {
        if (candidates[j].name === prefList[i]) return candidates[j];
      }
    }
    return candidates[0];
  }

  // ─── 形状质量得分 ─────────────────────────────────────────────

  function _scoreShape(f, shapeType) {
    switch (shapeType) {
      case SHAPE_ROUND:
        return Math.min(1, f.circularity * 1.5 + (1 - Math.abs(f.aspectRatio - 1)) * 0.3);
      case SHAPE_TALL:
        return Math.min(1, (1 - f.aspectRatio) * 0.8 + f.straightness * 0.2);
      case SHAPE_WIDE:
        return Math.min(1, (f.horizontalness - 2) * 0.3 + 0.5);
      case SHAPE_DOT:
        return 0.7;
      case SHAPE_WAVE:
        return Math.min(1, f.waviness * 0.6 + (f.horizontalness - 2) * 0.2 + 0.3);
      case SHAPE_ENCLOSURE:
        return Math.min(1, f.circularity * 0.8 + 0.3);
      case SHAPE_ZIGZAG:
        return Math.min(1, f.waviness * 0.5 + 0.45);
      case SHAPE_SPIRAL:
        return Math.min(1, f.circularity * 0.4 + f.waviness * 0.3 + 0.35);
      default:
        return 0.45;
    }
  }

  // ─── 核心：形状语义解析 ────────────────────────────────────────

  function _resolveElement(f, pts, strokeColor, canvasW) {
    var shapeType = _classifyShape(f, pts, canvasW);
    var zone = f.zone || ZONE_MID;

    var zoneMap = SHAPE_ZONE_ELEMENTS[shapeType];
    if (!zoneMap) return null;

    var candidates = zoneMap[zone];
    if (!candidates || candidates.length === 0) {
      candidates = zoneMap[ZONE_MID];
    }
    if (!candidates || candidates.length === 0) return null;

    var chosen = _pickByColor(candidates, strokeColor);
    var confidence = _scoreShape(f, shapeType);
    var tint = strokeColor ? _getTintLabel(strokeColor) : '';

    return {
      elemName: chosen.name,
      icon: chosen.icon,
      confidence: confidence,
      shapeType: shapeType,
      tint: tint,
    };
  }

  // ─── 单笔特征提取 ───────────────────────────────────────────

  function _extractFeatures(pts) {
    if (!pts || pts.length < 3) return null;

    var xs = pts.map(function (p) { return p.x; });
    var ys = pts.map(function (p) { return p.y; });

    var minX = Math.min.apply(null, xs);
    var maxX = Math.max.apply(null, xs);
    var minY = Math.min.apply(null, ys);
    var maxY = Math.max.apply(null, ys);
    var bboxW = maxX - minX || 1;
    var bboxH = maxY - minY || 1;
    var bboxArea = bboxW * bboxH;

    var aspectRatio = bboxW / bboxH;

    var perimeter = 0;
    for (var i = 1; i < pts.length; i++) {
      var dx = pts[i].x - pts[i - 1].x;
      var dy = pts[i].y - pts[i - 1].y;
      perimeter += Math.sqrt(dx * dx + dy * dy);
    }
    if (perimeter < 1) perimeter = 1;
    var circularity = Math.min(1, (4 * Math.PI * bboxArea) / (perimeter * perimeter));

    var firstLast = Math.sqrt(
      Math.pow(pts[pts.length - 1].x - pts[0].x, 2) +
      Math.pow(pts[pts.length - 1].y - pts[0].y, 2)
    );
    var straightness = Math.min(1, firstLast / perimeter);
    var horizontalness = bboxW / bboxH;
    var waviness = Math.min(1, Math.max(0, 1 - firstLast / (perimeter * 0.5 + 1)));

    var topQuarterCount = pts.filter(function (p) { return p.y < minY + bboxH * 0.25; }).length;
    var topSharpness = topQuarterCount / pts.length;

    var topPts = pts.filter(function (p) { return p.y < minY + bboxH * 0.33; });
    var topSpread = 0;
    if (topPts.length > 1) {
      var topXs = topPts.map(function (p) { return p.x; });
      topSpread = (Math.max.apply(null, topXs) - Math.min.apply(null, topXs)) / bboxW;
    }

    return {
      minX: minX, maxX: maxX, minY: minY, maxY: maxY,
      bboxW: bboxW, bboxH: bboxH,
      aspectRatio: aspectRatio,
      circularity: circularity,
      straightness: straightness,
      horizontalness: horizontalness,
      waviness: waviness,
      topSharpness: topSharpness,
      topSpread: topSpread,
      pointCount: pts.length,
      relativeHeight: 0,
      centerX: (minX + maxX) / 2,
      centerY: (minY + maxY) / 2,
      zone: null,
    };
  }

  // ─── 情绪参数分析 ──────────────────────────────────────────────

  function _analyzeMood(strokes, canvasW, canvasH) {
    if (!strokes || strokes.length === 0) {
      return { green: 50, urban: 50, vitality: 50, light: 50 };
    }

    var totalLength = 0;
    var coveredArea = 0;
    var allDx = [], allDy = [];

    strokes.forEach(function (pts) {
      if (pts.length < 2) return;
      for (var i = 1; i < pts.length; i++) {
        var dx = pts[i].x - pts[i - 1].x;
        var dy = pts[i].y - pts[i - 1].y;
        var len = Math.sqrt(dx * dx + dy * dy);
        totalLength += len;
        if (len > 0) { allDx.push(dx / len); allDy.push(dy / len); }
      }
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      coveredArea += (Math.max.apply(null, xs) - Math.min.apply(null, xs) + 10) *
                     (Math.max.apply(null, ys) - Math.min.apply(null, ys) + 10);
    });

    var canvasArea = (canvasW || 400) * (canvasH || 300);
    var coverageRatio = Math.min(1, coveredArea / (canvasArea * 1.5));
    var avgDx = allDx.reduce(function (s, v) { return s + v; }, 0) / (allDx.length || 1);
    var avgDy = allDy.reduce(function (s, v) { return s + v; }, 0) / (allDy.length || 1);
    var directionConsistency = Math.sqrt(avgDx * avgDx + avgDy * avgDy);
    var avgStrokeLen = totalLength / (strokes.length || 1);
    var strokeIntensity = Math.min(1, avgStrokeLen / 200);
    var activityScore = Math.min(1, strokes.length / 12);

    var green    = Math.round(40 + coverageRatio * 35 + (1 - activityScore) * 15);
    var urban    = Math.round(25 + activityScore * 25 + directionConsistency * 20);
    var vitality = Math.round(30 + activityScore * 40 + strokeIntensity * 20);
    var light    = Math.round(35 + directionConsistency * 35 + (1 - strokeIntensity) * 15);
    var moodLabel = _inferMoodLabel(green, urban, vitality, light);

    return {
      green:    Math.min(100, Math.max(10, green)),
      urban:    Math.min(100, Math.max(10, urban)),
      vitality: Math.min(100, Math.max(10, vitality)),
      light:    Math.min(100, Math.max(10, light)),
      moodLabel: moodLabel,
      coverageRatio: coverageRatio,
      strokeCount: strokes.length,
      directionConsistency: directionConsistency,
    };
  }

  function _inferMoodLabel(green, urban, vitality, light) {
    if (vitality > 75 && light > 60)  return { label: '盛夏活力', color: '#E76F51', emoji: '🔥' };
    if (vitality > 65 && urban > 50)  return { label: '活跃律动', color: '#E76F51', emoji: '⚡' };
    if (green > 70 && light > 60)     return { label: '春日暖阳', color: '#E9C46A', emoji: '🌸' };
    if (green > 60 && vitality < 45)  return { label: '自然静谧', color: '#2D6A4F', emoji: '🌿' };
    if (light > 65 && green > 50)     return { label: '温暖治愈', color: '#E9C46A', emoji: '☀️' };
    if (light < 35 && green > 45)     return { label: '清冷幽静', color: '#457B9D', emoji: '🌙' };
    if (urban < 35 && green > 55)     return { label: '野趣放松', color: '#40916C', emoji: '🍃' };
    if (vitality > 60 && green > 55)  return { label: '生机勃勃', color: '#52B788', emoji: '🌱' };
    if (urban > 60 && vitality > 50)  return { label: '都市花园', color: '#3A86FF', emoji: '🏙️' };
    return { label: '自由发散', color: '#9B8FD4', emoji: '✨' };
  }

  // ─── 单笔快速识别 ────────────────────────────────────────────

  function quickMatchStroke(pts, canvasW, canvasH, strokeColor) {
    if (!pts || pts.length < 3) return null;
    var f = _extractFeatures(pts);
    if (!f) return null;

    f.relativeHeight = f.bboxH / (canvasH || 400);
    var yPct = (f.centerY / (canvasH || 400)) * 100;
    f.zone = _getZone(yPct);

    var result = _resolveElement(f, pts, strokeColor, canvasW);
    if (!result) return null;

    return {
      elemName: result.elemName,
      icon: result.icon,
      confidence: result.confidence,
      tint: result.tint,
      zone: f.zone,
      x: Math.round((f.centerX / (canvasW || 400)) * 1000) / 10,
      y: Math.round(yPct * 10) / 10,
    };
  }

  // ─── 主分析入口 ───────────────────────────────────────────────

  function analyzeStrokes(strokes, canvasW, canvasH) {
    if (!strokes || strokes.length === 0) {
      return { type: 'mood', results: [], moodParams: _analyzeMood([], canvasW, canvasH), strokesWithZone: [] };
    }

    var recognizedElements = [];
    var strokesWithZone = [];
    var rawStrokes = strokes.map(function (s) {
      return Array.isArray(s) ? s : (s.pts || []);
    });

    strokes.forEach(function (strokeObj) {
      var pts         = Array.isArray(strokeObj) ? strokeObj : (strokeObj.pts || []);
      var strokeColor = Array.isArray(strokeObj) ? null : (strokeObj.color || null);

      if (!pts || pts.length < 3) return;

      var f = _extractFeatures(pts);
      if (!f) return;

      f.relativeHeight = f.bboxH / (canvasH || 400);
      var yPct        = (f.centerY / (canvasH || 400)) * 100;
      f.zone          = _getZone(yPct);
      var xPct        = Math.round((f.centerX / (canvasW || 400)) * 1000) / 10;
      var yPctRounded = Math.round(yPct * 10) / 10;

      strokesWithZone.push({ pts: pts, zone: f.zone, centerX: xPct, centerY: yPctRounded, color: strokeColor });

      var result = _resolveElement(f, pts, strokeColor, canvasW);
      if (result) {
        recognizedElements.push({
          elemName:   result.elemName,
          icon:       result.icon,
          confidence: result.confidence,
          shapeType:  result.shapeType,
          tint:       result.tint,
          zone:       f.zone,
          x:          xPct,
          y:          yPctRounded,
          color:      strokeColor,
        });
      }
    });

    var deduped = [];
    recognizedElements.forEach(function (el) {
      var dup = deduped.find(function (d) {
        return d.elemName === el.elemName &&
               Math.abs(d.x - el.x) < 15 && Math.abs(d.y - el.y) < 15;
      });
      if (!dup) {
        deduped.push(el);
      } else if (el.confidence > dup.confidence) {
        dup.x          = el.x;
        dup.y          = el.y;
        dup.confidence = el.confidence;
        dup.tint       = el.tint;
      }
    });

    if (deduped.length > 0) {
      return {
        type:            'element',
        results:         deduped,
        moodParams:      null,
        strokesWithZone: strokesWithZone,
      };
    }

    var moodParams = _analyzeMood(rawStrokes, canvasW, canvasH);
    return {
      type:            'mood',
      results:         [],
      moodParams:      moodParams,
      strokesWithZone: strokesWithZone,
    };
  }

  // ─── 坐标转换工具 ─────────────────────────────────────────────

  function extractPathPoints(fabricPath) {
    var pts = [];
    if (!fabricPath || !fabricPath.path) return pts;
    fabricPath.path.forEach(function (cmd) {
      if (cmd.length >= 3) {
        pts.push({ x: cmd[cmd.length - 2], y: cmd[cmd.length - 1] });
      }
    });
    return pts;
  }

  return {
    analyzeStrokes:    analyzeStrokes,
    extractPathPoints: extractPathPoints,
    quickMatchStroke:  quickMatchStroke,
    _analyzeMood:      _analyzeMood,
    _extractFeatures:  _extractFeatures,
    _classifyShape:    _classifyShape,
    _resolveElement:   _resolveElement,
    _getZone:          _getZone,
    _getTintLabel:     _getTintLabel,
    _findNearestColorPref: _findNearestColorPref,
    ZONE_SKY:          ZONE_SKY,
    ZONE_MID:          ZONE_MID,
    ZONE_GND:          ZONE_GND,
    COLOR_TINT_LABEL:  COLOR_TINT_LABEL,
  };
})();
