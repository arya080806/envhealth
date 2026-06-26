/**
 * SketchComposer — 多笔组合语义引擎 v2
 *
 * 在 SketchAnalyzer 单笔识别的基础上，对所有笔迹进行整体分析，
 * 识别"围合/线性/散点/垂直堆叠/大面积涂抹"5种组合模式，
 * 新增笔迹间空间关系分析（邻近组合），
 * 输出 SceneIntent JSON，供后端构建更精准的 Prompt。
 */
window.SketchComposer = (function () {
  'use strict';

  var PATTERN_ENCLOSURE = 'enclosure';
  var PATTERN_LINEAR    = 'linear';
  var PATTERN_SCATTER   = 'scatter';
  var PATTERN_VERTICAL  = 'vertical';
  var PATTERN_WASH      = 'wash';

  // ─── 组合模式 → 场景意图映射（扩充版，每格 2-3 个候选）────────
  var PATTERN_INTENT_MAP = {
    enclosure: {
      ground:    [{ element: '花坛或池塘', mood: '宁静精致' }, { element: '喷泉水池', mood: '典雅中心' }],
      midground: [{ element: '灌木围合', mood: '层次丰富' }, { element: '花圃', mood: '精致规整' }],
      sky:       [{ element: '圆形构图', mood: '开阔通透' }],
    },
    linear: {
      ground:    [{ element: '小径或小溪', mood: '引导深远' }, { element: '碎石小路', mood: '自然朴实' }],
      midground: [{ element: '树篱或水渠', mood: '延伸感' }, { element: '灌木带', mood: '线条有序' }],
      sky:       [{ element: '地平线', mood: '开阔壮丽' }, { element: '远山轮廓', mood: '层叠辽远' }],
    },
    scatter: {
      ground:    [{ element: '花卉点缀或落叶', mood: '自然野趣' }, { element: '鹅卵石散落', mood: '质朴天然' }],
      midground: [{ element: '灌木群落', mood: '生机勃勃' }, { element: '花丛点缀', mood: '缤纷活泼' }],
      sky:       [{ element: '飘散云彩', mood: '轻盈自由' }, { element: '飞鸟群', mood: '灵动开阔' }],
    },
    vertical: {
      ground:    [{ element: '植被丛', mood: '茂密生机' }, { element: '栅栏柱列', mood: '节奏秩序' }],
      midground: [{ element: '树林或竹林', mood: '幽深静谧' }, { element: '路灯排列', mood: '都市花园感' }],
      sky:       [{ element: '参天大树', mood: '壮阔雄伟' }],
    },
    wash: {
      ground:    [{ element: '大面积草坪或植被覆盖', mood: '自然丰盈' }, { element: '落叶铺地', mood: '秋日沉静' }],
      midground: [{ element: '整体环境氛围改造', mood: '沉浸感' }],
      sky:       [{ element: '光线氛围', mood: '戏剧性光影' }, { element: '晚霞渲染', mood: '绚丽壮美' }],
    },
  };

  function _pickIntent(intentList, strokeCount) {
    if (!intentList || intentList.length === 0) return { element: '', mood: '' };
    if (intentList.length === 1) return intentList[0];
    var count = Math.max(1, Number(strokeCount || 1));
    var idx = (count - 1) % intentList.length;
    return intentList[idx];
  }

  // ─── 组合模式识别规则 ────────────────────────────────────────

  function _detectEnclosure(strokesInfo) {
    var enclosures = [];
    strokesInfo.forEach(function (s) {
      var pts = s.pts;
      if (pts.length < 8) return;
      var first = pts[0], last = pts[pts.length - 1];
      var dist = Math.sqrt(Math.pow(last.x - first.x, 2) + Math.pow(last.y - first.y, 2));
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var span = Math.max(
        Math.max.apply(null, xs) - Math.min.apply(null, xs),
        Math.max.apply(null, ys) - Math.min.apply(null, ys)
      );
      if (span > 10 && dist / span < 0.4) {
        enclosures.push({ zone: s.zone, centerX: s.centerX, centerY: s.centerY });
      }
    });
    return enclosures;
  }

  function _detectLinear(strokesInfo) {
    var linears = [];
    strokesInfo.forEach(function (s) {
      var pts = s.pts;
      if (pts.length < 10) return;
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var bboxW = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
      var bboxH = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
      var ratio = bboxW / bboxH;
      if (ratio > 3 || ratio < 0.33) {
        linears.push({
          zone: s.zone,
          direction: ratio > 3 ? 'horizontal' : 'vertical',
          centerX: s.centerX,
          centerY: s.centerY,
        });
      }
    });
    return linears;
  }

  function _detectScatter(strokesInfo, canvasW, canvasH) {
    var byZone = {};
    strokesInfo.forEach(function (s) {
      var pts = s.pts;
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var bboxW = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
      var bboxH = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
      var relSize = Math.max(bboxW, bboxH) / Math.max(canvasW, canvasH);
      if (relSize < 0.3) {
        if (!byZone[s.zone]) byZone[s.zone] = [];
        byZone[s.zone].push(s);
      }
    });

    var scatters = [];
    Object.keys(byZone).forEach(function (zone) {
      if (byZone[zone].length >= 3) {
        var avgX = byZone[zone].reduce(function (s, v) { return s + v.centerX; }, 0) / byZone[zone].length;
        var avgY = byZone[zone].reduce(function (s, v) { return s + v.centerY; }, 0) / byZone[zone].length;
        scatters.push({ zone: zone, count: byZone[zone].length, centerX: avgX, centerY: avgY });
      }
    });
    return scatters;
  }

  function _detectVertical(strokesInfo) {
    var verticals = strokesInfo.filter(function (s) {
      var pts = s.pts;
      if (pts.length < 5) return false;
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var bboxW = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
      var bboxH = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
      return bboxH / bboxW > 1.5;
    });

    if (verticals.length < 2) return [];

    var avgX = verticals.reduce(function (s, v) { return s + v.centerX; }, 0) / verticals.length;
    var avgY = verticals.reduce(function (s, v) { return s + v.centerY; }, 0) / verticals.length;
    var dominantZone = _dominantZone(verticals);
    return [{ zone: dominantZone, count: verticals.length, centerX: avgX, centerY: avgY }];
  }

  function _detectWash(strokesInfo, canvasW, canvasH) {
    var canvasArea = canvasW * canvasH;
    var washStrokes = [];

    strokesInfo.forEach(function (s) {
      var pts = s.pts;
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var bboxW = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
      var bboxH = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
      var singleCoverage = (bboxW * bboxH) / canvasArea;
      if (singleCoverage > 0.20 && bboxW / bboxH >= 2) {
        washStrokes.push(s);
      }
    });

    if (washStrokes.length === 0) return [];

    var dominantZone = _dominantZone(washStrokes);
    var maxCoverage = washStrokes.reduce(function (max, s) {
      var pts = s.pts;
      var xs = pts.map(function (p) { return p.x; });
      var ys = pts.map(function (p) { return p.y; });
      var bboxW = Math.max.apply(null, xs) - Math.min.apply(null, xs) || 1;
      var bboxH = Math.max.apply(null, ys) - Math.min.apply(null, ys) || 1;
      return Math.max(max, (bboxW * bboxH) / canvasArea);
    }, 0);

    return [{ zone: dominantZone, coverage: maxCoverage }];
  }

  // ─── 笔迹间空间关系分析（新增）─────────────────────────────────

  /**
   * 检测相邻笔迹（中心距 < 画布 20%）的组合关系
   * 返回如「树旁小溪」「花坛环绕步道」等复合意图
   */
  function _detectProximityRelations(elementResults, canvasW, canvasH) {
    if (!elementResults || elementResults.length < 2) return [];
    var threshold = Math.max(canvasW, canvasH) * 0.20;
    var thresholdPct = 20;
    var relations = [];
    var usedPairs = {};

    var RELATION_MAP = {
      '大树+小溪':   '树旁流水',
      '小溪+大树':   '树旁流水',
      '花坛+池塘':   '花映水池',
      '池塘+花坛':   '花映水池',
      '草坪+小径':   '草间步道',
      '小径+草坪':   '草间步道',
      '路灯+小径':   '路灯小径',
      '小径+路灯':   '路灯小径',
      '大树+花朵':   '树下花开',
      '花朵+大树':   '树下花开',
      '竹子+小溪':   '竹影溪畔',
      '小溪+竹子':   '竹影溪畔',
      '大树+草坪':   '林荫草地',
      '草坪+大树':   '林荫草地',
      '花朵+灌木带': '花篱相伴',
      '灌木带+花朵': '花篱相伴',
      '栅栏+花朵':   '篱笆花墙',
      '花朵+栅栏':   '篱笆花墙',
      '池塘+树丛':   '掩映池塘',
      '树丛+池塘':   '掩映池塘',
      '喷泉+花坛':   '喷泉花园',
      '花坛+喷泉':   '喷泉花园',
      '远山+云带':   '山云相接',
      '云带+远山':   '山云相接',
    };

    for (var i = 0; i < elementResults.length; i++) {
      for (var j = i + 1; j < elementResults.length; j++) {
        var a = elementResults[i];
        var b = elementResults[j];
        var dx = Math.abs((a.x || 50) - (b.x || 50));
        var dy = Math.abs((a.y || 50) - (b.y || 50));
        if (dx < thresholdPct && dy < thresholdPct) {
          var key = (a.elemName || '') + '+' + (b.elemName || '');
          if (RELATION_MAP[key] && !usedPairs[key]) {
            usedPairs[key] = true;
            relations.push({
              label: RELATION_MAP[key],
              elements: [a.elemName, b.elemName],
              zone: a.zone || b.zone || 'midground',
            });
          }
        }
      }
    }
    return relations;
  }

  // ─── 工具函数 ────────────────────────────────────────────────

  function _dominantZone(strokesInfo) {
    var counts = {};
    strokesInfo.forEach(function (s) {
      counts[s.zone] = (counts[s.zone] || 0) + 1;
    });
    var best = 'ground', bestN = 0;
    Object.keys(counts).forEach(function (z) {
      if (counts[z] > bestN) { bestN = counts[z]; best = z; }
    });
    return best;
  }

  function _zoneLabel(zone) {
    return { sky: '天空', midground: '中景', ground: '地面' }[zone] || '画面';
  }

  // ─── 叙事摘要生成（升级版）────────────────────────────────────

  function _buildNarrativeSummary(patterns, elementHints, relations) {
    if (patterns.length === 0 && elementHints.length === 0) {
      return '用户进行了自由涂抹，希望对整体环境氛围进行改造';
    }

    var parts = [];

    patterns.forEach(function (p) {
      var intentList = PATTERN_INTENT_MAP[p.type];
      if (!intentList) return;
      var zoneList = intentList[p.zone] || intentList['ground'];
      var intent = Array.isArray(zoneList) ? zoneList[0] : zoneList;
      if (intent) {
        parts.push('在' + _zoneLabel(p.zone) + '区域添加' + intent.element);
      }
    });

    elementHints.forEach(function (h) {
      if (parts.length < 3) {
        parts.push('在' + _zoneLabel(h.zone) + '添加' + h.elemName);
      }
    });

    if (parts.length === 0) return '对场景进行整体环境改造';

    var narrative = '用户希望' + parts[0];
    for (var i = 1; i < parts.length; i++) {
      var connectors = ['，同时', '，并', '，还想'];
      narrative += connectors[i % connectors.length] + parts[i];
    }

    if (relations && relations.length > 0) {
      var relLabels = relations.map(function (r) { return r.label; });
      narrative += '，营造「' + relLabels.join('·') + '」的和谐意境';
    } else {
      narrative += '，整体营造自然和谐的空间感';
    }

    return narrative;
  }

  // ─── 主入口 ─────────────────────────────────────────────────

  function compose(analyzerResult, canvasW, canvasH) {
    var strokesWithZone = analyzerResult.strokesWithZone || [];
    var elementResults  = analyzerResult.results || [];
    var totalStrokes    = strokesWithZone.length;

    if (totalStrokes === 0) {
      return {
        zones: {},
        spatialPatterns: [],
        proximityRelations: [],
        dominantMood: '自由创想',
        complexityLevel: 'simple',
        narrativeSummary: '暂无笔迹',
      };
    }

    // ── 1. 区域覆盖统计 ──
    var zoneCounts = { sky: 0, midground: 0, ground: 0 };
    var zoneHints  = { sky: [], midground: [], ground: [] };
    strokesWithZone.forEach(function (s) {
      zoneCounts[s.zone] = (zoneCounts[s.zone] || 0) + 1;
    });
    elementResults.forEach(function (el) {
      var z = el.zone || 'ground';
      if (!zoneHints[z]) zoneHints[z] = [];
      if (zoneHints[z].indexOf(el.elemName) === -1) zoneHints[z].push(el.elemName);
    });

    var zones = {};
    ['sky', 'midground', 'ground'].forEach(function (z) {
      zones[z] = {
        coverage: Math.round(((zoneCounts[z] || 0) / (totalStrokes || 1)) * 100) / 100,
        hints: zoneHints[z] || [],
      };
    });

    // ── 2. 组合模式识别 ──
    var enclosures = _detectEnclosure(strokesWithZone);
    var linears    = _detectLinear(strokesWithZone);
    var scatters   = _detectScatter(strokesWithZone, canvasW, canvasH);
    var verticals  = _detectVertical(strokesWithZone);
    var washes     = _detectWash(strokesWithZone, canvasW, canvasH);

    var spatialPatterns = [];

    enclosures.forEach(function (e) {
      var intentList = PATTERN_INTENT_MAP.enclosure[e.zone] || PATTERN_INTENT_MAP.enclosure.ground;
      var intent = _pickIntent(intentList, totalStrokes);
      spatialPatterns.push({
        type: PATTERN_ENCLOSURE, zone: e.zone, element: intent.element,
        centerX: e.centerX, centerY: e.centerY,
      });
    });

    linears.forEach(function (l) {
      var intentList = PATTERN_INTENT_MAP.linear[l.zone] || PATTERN_INTENT_MAP.linear.ground;
      var intent = _pickIntent(intentList, totalStrokes);
      spatialPatterns.push({
        type: PATTERN_LINEAR, zone: l.zone, direction: l.direction, element: intent.element,
        centerX: l.centerX, centerY: l.centerY,
      });
    });

    scatters.forEach(function (s) {
      var intentList = PATTERN_INTENT_MAP.scatter[s.zone] || PATTERN_INTENT_MAP.scatter.ground;
      var intent = _pickIntent(intentList, totalStrokes);
      spatialPatterns.push({
        type: PATTERN_SCATTER, zone: s.zone, count: s.count, element: intent.element,
        centerX: s.centerX, centerY: s.centerY,
      });
    });

    verticals.forEach(function (v) {
      var intentList = PATTERN_INTENT_MAP.vertical[v.zone] || PATTERN_INTENT_MAP.vertical.midground;
      var intent = _pickIntent(intentList, totalStrokes);
      spatialPatterns.push({
        type: PATTERN_VERTICAL, zone: v.zone, count: v.count, element: intent.element,
        centerX: v.centerX, centerY: v.centerY,
      });
    });

    washes.forEach(function (w) {
      var intentList = PATTERN_INTENT_MAP.wash[w.zone] || PATTERN_INTENT_MAP.wash.ground;
      var intent = _pickIntent(intentList, totalStrokes);
      spatialPatterns.push({
        type: PATTERN_WASH, zone: w.zone, coverage: w.coverage, element: intent.element,
      });
    });

    // ── 3. 笔迹间空间关系 ──
    var proximityRelations = _detectProximityRelations(elementResults, canvasW, canvasH);

    // ── 4. 推断主导情绪 ──
    var dominantMood = _inferDominantMood(spatialPatterns, analyzerResult, proximityRelations);

    // ── 5. 复杂度 ──
    var complexityLevel = totalStrokes <= 2 ? 'simple'
                        : totalStrokes <= 6 ? 'medium' : 'rich';

    // ── 6. 叙事摘要 ──
    var narrativeSummary = _buildNarrativeSummary(spatialPatterns, elementResults, proximityRelations);

    return {
      zones: zones,
      spatialPatterns: spatialPatterns,
      proximityRelations: proximityRelations,
      dominantMood: dominantMood,
      complexityLevel: complexityLevel,
      narrativeSummary: narrativeSummary,
    };
  }

  function _inferDominantMood(patterns, analyzerResult, relations) {
    if (analyzerResult.moodParams && analyzerResult.moodParams.moodLabel) {
      return analyzerResult.moodParams.moodLabel.label;
    }

    var hasWash      = patterns.some(function (p) { return p.type === PATTERN_WASH; });
    var hasVertical  = patterns.some(function (p) { return p.type === PATTERN_VERTICAL; });
    var hasLinear    = patterns.some(function (p) { return p.type === PATTERN_LINEAR; });
    var hasEnclosure = patterns.some(function (p) { return p.type === PATTERN_ENCLOSURE; });
    var hasScatter   = patterns.some(function (p) { return p.type === PATTERN_SCATTER; });
    var hasRelations = relations && relations.length > 0;

    if (hasWash && hasVertical) return '森林秘境';
    if (hasWash) return '沉浸自然';
    if (hasVertical && hasLinear) return '幽深静谧';
    if (hasVertical) return '林间生机';
    if (hasEnclosure && hasScatter) return '温馨精致';
    if (hasEnclosure && hasRelations) return '水园雅韵';
    if (hasLinear && hasScatter) return '花径漫步';
    if (hasLinear) return '引导深远';
    if (hasEnclosure) return '宁静内聚';
    if (hasScatter) return '自然野趣';
    if (hasRelations) return '和谐共生';
    return '自由创想';
  }

  // ─── 展示用叙事文本 ──────────────────────────────────────────

  function buildDisplayText(sceneIntent) {
    var patterns = sceneIntent.spatialPatterns;
    var mood = sceneIntent.dominantMood;
    var complexity = sceneIntent.complexityLevel;
    var relations = sceneIntent.proximityRelations || [];

    if (patterns.length === 0 && relations.length === 0) {
      return '感知到你的创作意图，将以「' + mood + '」风格整体改造场景';
    }

    var mainElements = patterns.slice(0, 2).map(function (p) { return p.element; });

    if (relations.length > 0) {
      var relLabels = relations.slice(0, 2).map(function (r) { return r.label; });
      mainElements = mainElements.concat(relLabels);
    }

    var levelText = { simple: '简约', medium: '丰富', rich: '层次繁茂' }[complexity] || '自然';

    var uniqueElements = [];
    mainElements.forEach(function (e) {
      if (uniqueElements.indexOf(e) === -1) uniqueElements.push(e);
    });

    return '✦ 识别到你想在场景中融入' + uniqueElements.slice(0, 3).join('、') +
           '，整体营造「' + mood + '」的' + levelText + '氛围';
  }

  return {
    compose: compose,
    buildDisplayText: buildDisplayText,
  };
})();
