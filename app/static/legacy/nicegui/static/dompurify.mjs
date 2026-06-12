/*! @license DOMPurify 3.3.1 | (c) Cure53 and other contributors | Released under the Apache license 2.0 and Mozilla Public License 2.0 | github.com/cure53/DOMPurify/blob/3.3.1/LICENSE */
const { entries, setPrototypeOf, isFrozen, getPrototypeOf, getOwnPropertyDescriptor } = Object;
let { freeze, seal, create } = Object, { apply, construct } = "undefined" != typeof Reflect && Reflect;
freeze || (freeze = function(e) {
  return e;
}), seal || (seal = function(e) {
  return e;
}), apply || (apply = function(e, t) {
  for (var n = arguments.length, r = new Array(n > 2 ? n - 2 : 0), o = 2; o < n; o++) r[o - 2] = arguments[o];
  return e.apply(t, r);
}), construct || (construct = function(e) {
  for (var t = arguments.length, n = new Array(t > 1 ? t - 1 : 0), r = 1; r < t; r++) n[r - 1] = arguments[r];
  return new e(...n);
});
const arrayForEach = unapply(Array.prototype.forEach), arrayLastIndexOf = unapply(Array.prototype.lastIndexOf), arrayPop = unapply(Array.prototype.pop), arrayPush = unapply(Array.prototype.push), arraySplice = unapply(Array.prototype.splice), stringToLowerCase = unapply(String.prototype.toLowerCase), stringToString = unapply(String.prototype.toString), stringMatch = unapply(String.prototype.match), stringReplace = unapply(String.prototype.replace), stringIndexOf = unapply(String.prototype.indexOf), stringTrim = unapply(String.prototype.trim), objectHasOwnProperty = unapply(Object.prototype.hasOwnProperty), regExpTest = unapply(RegExp.prototype.test), typeErrorCreate = unconstruct(TypeError);
function unapply(e) {
  return function(t) {
    t instanceof RegExp && (t.lastIndex = 0);
    for (var n = arguments.length, r = new Array(n > 1 ? n - 1 : 0), o = 1; o < n; o++) r[o - 1] = arguments[o];
    return apply(e, t, r);
  };
}
function unconstruct(e) {
  return function() {
    for (var t = arguments.length, n = new Array(t), r = 0; r < t; r++) n[r] = arguments[r];
    return construct(e, n);
  };
}
function addToSet(e, t) {
  let n = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : stringToLowerCase;
  setPrototypeOf && setPrototypeOf(e, null);
  let r = t.length;
  for (; r--; ) {
    let o = t[r];
    if ("string" == typeof o) {
      const e2 = n(o);
      e2 !== o && (isFrozen(t) || (t[r] = e2), o = e2);
    }
    e[o] = true;
  }
  return e;
}
function cleanArray(e) {
  for (let t = 0; t < e.length; t++) {
    objectHasOwnProperty(e, t) || (e[t] = null);
  }
  return e;
}
function clone(e) {
  const t = create(null);
  for (const [n, r] of entries(e)) {
    objectHasOwnProperty(e, n) && (Array.isArray(r) ? t[n] = cleanArray(r) : r && "object" == typeof r && r.constructor === Object ? t[n] = clone(r) : t[n] = r);
  }
  return t;
}
function lookupGetter(e, t) {
  for (; null !== e; ) {
    const n = getOwnPropertyDescriptor(e, t);
    if (n) {
      if (n.get) return unapply(n.get);
      if ("function" == typeof n.value) return unapply(n.value);
    }
    e = getPrototypeOf(e);
  }
  return function() {
    return null;
  };
}
const html$1 = freeze(["a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "bdi", "bdo", "big", "blink", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "content", "data", "datalist", "dd", "decorator", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "fieldset", "figcaption", "figure", "font", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "img", "input", "ins", "kbd", "label", "legend", "li", "main", "map", "mark", "marquee", "menu", "menuitem", "meter", "nav", "nobr", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "search", "section", "select", "shadow", "slot", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "tt", "u", "ul", "var", "video", "wbr"]), svg$1 = freeze(["svg", "a", "altglyph", "altglyphdef", "altglyphitem", "animatecolor", "animatemotion", "animatetransform", "circle", "clippath", "defs", "desc", "ellipse", "enterkeyhint", "exportparts", "filter", "font", "g", "glyph", "glyphref", "hkern", "image", "inputmode", "line", "lineargradient", "marker", "mask", "metadata", "mpath", "part", "path", "pattern", "polygon", "polyline", "radialgradient", "rect", "stop", "style", "switch", "symbol", "text", "textpath", "title", "tref", "tspan", "view", "vkern"]), svgFilters = freeze(["feBlend", "feColorMatrix", "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA", "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode", "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight", "feTile", "feTurbulence"]), svgDisallowed = freeze(["animate", "color-profile", "cursor", "discard", "font-face", "font-face-format", "font-face-name", "font-face-src", "font-face-uri", "foreignobject", "hatch", "hatchpath", "mesh", "meshgradient", "meshpatch", "meshrow", "missing-glyph", "script", "set", "solidcolor", "unknown", "use"]), mathMl$1 = freeze(["math", "menclose", "merror", "mfenced", "mfrac", "mglyph", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover", "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msup", "msubsup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "mprescripts"]), mathMlDisallowed = freeze(["maction", "maligngroup", "malignmark", "mlongdiv", "mscarries", "mscarry", "msgroup", "mstack", "msline", "msrow", "semantics", "annotation", "annotation-xml", "mprescripts", "none"]), text = freeze(["#text"]), html = freeze(["accept", "action", "align", "alt", "autocapitalize", "autocomplete", "autopictureinpicture", "autoplay", "background", "bgcolor", "border", "capture", "cellpadding", "cellspacing", "checked", "cite", "class", "clear", "color", "cols", "colspan", "controls", "controlslist", "coords", "crossorigin", "datetime", "decoding", "default", "dir", "disabled", "disablepictureinpicture", "disableremoteplayback", "download", "draggable", "enctype", "enterkeyhint", "exportparts", "face", "for", "headers", "height", "hidden", "high", "href", "hreflang", "id", "inert", "inputmode", "integrity", "ismap", "kind", "label", "lang", "list", "loading", "loop", "low", "max", "maxlength", "media", "method", "min", "minlength", "multiple", "muted", "name", "nonce", "noshade", "novalidate", "nowrap", "open", "optimum", "part", "pattern", "placeholder", "playsinline", "popover", "popovertarget", "popovertargetaction", "poster", "preload", "pubdate", "radiogroup", "readonly", "rel", "required", "rev", "reversed", "role", "rows", "rowspan", "spellcheck", "scope", "selected", "shape", "size", "sizes", "slot", "span", "srclang", "start", "src", "srcset", "step", "style", "summary", "tabindex", "title", "translate", "type", "usemap", "valign", "value", "width", "wrap", "xmlns", "slot"]), svg = freeze(["accent-height", "accumulate", "additive", "alignment-baseline", "amplitude", "ascent", "attributename", "attributetype", "azimuth", "basefrequency", "baseline-shift", "begin", "bias", "by", "class", "clip", "clippathunits", "clip-path", "clip-rule", "color", "color-interpolation", "color-interpolation-filters", "color-profile", "color-rendering", "cx", "cy", "d", "dx", "dy", "diffuseconstant", "direction", "display", "divisor", "dur", "edgemode", "elevation", "end", "exponent", "fill", "fill-opacity", "fill-rule", "filter", "filterunits", "flood-color", "flood-opacity", "font-family", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-variant", "font-weight", "fx", "fy", "g1", "g2", "glyph-name", "glyphref", "gradientunits", "gradienttransform", "height", "href", "id", "image-rendering", "in", "in2", "intercept", "k", "k1", "k2", "k3", "k4", "kerning", "keypoints", "keysplines", "keytimes", "lang", "lengthadjust", "letter-spacing", "kernelmatrix", "kernelunitlength", "lighting-color", "local", "marker-end", "marker-mid", "marker-start", "markerheight", "markerunits", "markerwidth", "maskcontentunits", "maskunits", "max", "mask", "mask-type", "media", "method", "mode", "min", "name", "numoctaves", "offset", "operator", "opacity", "order", "orient", "orientation", "origin", "overflow", "paint-order", "path", "pathlength", "patterncontentunits", "patterntransform", "patternunits", "points", "preservealpha", "preserveaspectratio", "primitiveunits", "r", "rx", "ry", "radius", "refx", "refy", "repeatcount", "repeatdur", "restart", "result", "rotate", "scale", "seed", "shape-rendering", "slope", "specularconstant", "specularexponent", "spreadmethod", "startoffset", "stddeviation", "stitchtiles", "stop-color", "stop-opacity", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke", "stroke-width", "style", "surfacescale", "systemlanguage", "tabindex", "tablevalues", "targetx", "targety", "transform", "transform-origin", "text-anchor", "text-decoration", "text-rendering", "textlength", "type", "u1", "u2", "unicode", "values", "viewbox", "visibility", "version", "vert-adv-y", "vert-origin-x", "vert-origin-y", "width", "word-spacing", "wrap", "writing-mode", "xchannelselector", "ychannelselector", "x", "x1", "x2", "xmlns", "y", "y1", "y2", "z", "zoomandpan"]), mathMl = freeze(["accent", "accentunder", "align", "bevelled", "close", "columnsalign", "columnlines", "columnspan", "denomalign", "depth", "dir", "display", "displaystyle", "encoding", "fence", "frame", "height", "href", "id", "largeop", "length", "linethickness", "lspace", "lquote", "mathbackground", "mathcolor", "mathsize", "mathvariant", "maxsize", "minsize", "movablelimits", "notation", "numalign", "open", "rowalign", "rowlines", "rowspacing", "rowspan", "rspace", "rquote", "scriptlevel", "scriptminsize", "scriptsizemultiplier", "selection", "separator", "separators", "stretchy", "subscriptshift", "supscriptshift", "symmetric", "voffset", "width", "xmlns"]), xml = freeze(["xlink:href", "xml:id", "xlink:title", "xml:space", "xmlns:xlink"]), MUSTACHE_EXPR = seal(/\{\{[\w\W]*|[\w\W]*\}\}/gm), ERB_EXPR = seal(/<%[\w\W]*|[\w\W]*%>/gm), TMPLIT_EXPR = seal(/\$\{[\w\W]*/gm), DATA_ATTR = seal(/^data-[\-\w.\u00B7-\uFFFF]+$/), ARIA_ATTR = seal(/^aria-[\-\w]+$/), IS_ALLOWED_URI = seal(/^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|matrix):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i), IS_SCRIPT_OR_DATA = seal(/^(?:\w+script|data):/i), ATTR_WHITESPACE = seal(/[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g), DOCTYPE_NAME = seal(/^html$/i), CUSTOM_ELEMENT = seal(/^[a-z][.\w]*(-[.\w]+)+$/i);
var EXPRESSIONS = Object.freeze({ __proto__: null, ARIA_ATTR, ATTR_WHITESPACE, CUSTOM_ELEMENT, DATA_ATTR, DOCTYPE_NAME, ERB_EXPR, IS_ALLOWED_URI, IS_SCRIPT_OR_DATA, MUSTACHE_EXPR, TMPLIT_EXPR });
const NODE_TYPE = { element: 1, attribute: 2, text: 3, cdataSection: 4, entityReference: 5, entityNode: 6, progressingInstruction: 7, comment: 8, document: 9, documentType: 10, documentFragment: 11, notation: 12 }, getGlobal = function() {
  return "undefined" == typeof window ? null : window;
}, _createTrustedTypesPolicy = function(e, t) {
  if ("object" != typeof e || "function" != typeof e.createPolicy) return null;
  let n = null;
  const r = "data-tt-policy-suffix";
  t && t.hasAttribute(r) && (n = t.getAttribute(r));
  const o = "dompurify" + (n ? "#" + n : "");
  try {
    return e.createPolicy(o, { createHTML: (e2) => e2, createScriptURL: (e2) => e2 });
  } catch (e2) {
    return console.warn("TrustedTypes policy " + o + " could not be created."), null;
  }
}, _createHooksMap = function() {
  return { afterSanitizeAttributes: [], afterSanitizeElements: [], afterSanitizeShadowDOM: [], beforeSanitizeAttributes: [], beforeSanitizeElements: [], beforeSanitizeShadowDOM: [], uponSanitizeAttribute: [], uponSanitizeElement: [], uponSanitizeShadowNode: [] };
};
function createDOMPurify() {
  let e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : getGlobal();
  const t = (e2) => createDOMPurify(e2);
  if (t.version = "3.3.1", t.removed = [], !e || !e.document || e.document.nodeType !== NODE_TYPE.document || !e.Element) return t.isSupported = false, t;
  let { document: n } = e;
  const r = n, o = r.currentScript, { DocumentFragment: a, HTMLTemplateElement: i, Node: l, Element: s, NodeFilter: c, NamedNodeMap: p = e.NamedNodeMap || e.MozNamedAttrMap, HTMLFormElement: u, DOMParser: m, trustedTypes: d } = e, f = s.prototype, T = lookupGetter(f, "cloneNode"), g = lookupGetter(f, "remove"), h = lookupGetter(f, "nextSibling"), y = lookupGetter(f, "childNodes"), E = lookupGetter(f, "parentNode");
  if ("function" == typeof i) {
    const e2 = n.createElement("template");
    e2.content && e2.content.ownerDocument && (n = e2.content.ownerDocument);
  }
  let S, _ = "";
  const { implementation: A, createNodeIterator: b, createDocumentFragment: N, getElementsByTagName: O } = n, { importNode: R } = r;
  let D = _createHooksMap();
  t.isSupported = "function" == typeof entries && "function" == typeof E && A && void 0 !== A.createHTMLDocument;
  const { MUSTACHE_EXPR: w, ERB_EXPR: C, TMPLIT_EXPR: x, DATA_ATTR: v, ARIA_ATTR: I, IS_SCRIPT_OR_DATA: L, ATTR_WHITESPACE: M, CUSTOM_ELEMENT: P } = EXPRESSIONS;
  let { IS_ALLOWED_URI: k } = EXPRESSIONS, z = null;
  const H = addToSet({}, [...html$1, ...svg$1, ...svgFilters, ...mathMl$1, ...text]);
  let U = null;
  const F = addToSet({}, [...html, ...svg, ...mathMl, ...xml]);
  let G = Object.seal(create(null, { tagNameCheck: { writable: true, configurable: false, enumerable: true, value: null }, attributeNameCheck: { writable: true, configurable: false, enumerable: true, value: null }, allowCustomizedBuiltInElements: { writable: true, configurable: false, enumerable: true, value: false } })), W = null, B = null;
  const j = Object.seal(create(null, { tagCheck: { writable: true, configurable: false, enumerable: true, value: null }, attributeCheck: { writable: true, configurable: false, enumerable: true, value: null } }));
  let Y = true, X = true, $ = false, q = true, K = false, V = true, Z = false, J = false, Q = false, ee = false, te = false, ne = false, re = true, oe = false;
  let ae = true, ie = false, le = {}, se = null;
  const ce = addToSet({}, ["annotation-xml", "audio", "colgroup", "desc", "foreignobject", "head", "iframe", "math", "mi", "mn", "mo", "ms", "mtext", "noembed", "noframes", "noscript", "plaintext", "script", "style", "svg", "template", "thead", "title", "video", "xmp"]);
  let pe = null;
  const ue = addToSet({}, ["audio", "video", "img", "source", "image", "track"]);
  let me = null;
  const de = addToSet({}, ["alt", "class", "for", "id", "label", "name", "pattern", "placeholder", "role", "summary", "title", "value", "style", "xmlns"]), fe = "http://www.w3.org/1998/Math/MathML", Te = "http://www.w3.org/2000/svg", ge = "http://www.w3.org/1999/xhtml";
  let he = ge, ye = false, Ee = null;
  const Se = addToSet({}, [fe, Te, ge], stringToString);
  let _e = addToSet({}, ["mi", "mo", "mn", "ms", "mtext"]), Ae = addToSet({}, ["annotation-xml"]);
  const be = addToSet({}, ["title", "style", "font", "a", "script"]);
  let Ne = null;
  const Oe = ["application/xhtml+xml", "text/html"];
  let Re = null, De = null;
  const we = n.createElement("form"), Ce = function(e2) {
    return e2 instanceof RegExp || e2 instanceof Function;
  }, xe = function() {
    let e2 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
    if (!De || De !== e2) {
      if (e2 && "object" == typeof e2 || (e2 = {}), e2 = clone(e2), Ne = -1 === Oe.indexOf(e2.PARSER_MEDIA_TYPE) ? "text/html" : e2.PARSER_MEDIA_TYPE, Re = "application/xhtml+xml" === Ne ? stringToString : stringToLowerCase, z = objectHasOwnProperty(e2, "ALLOWED_TAGS") ? addToSet({}, e2.ALLOWED_TAGS, Re) : H, U = objectHasOwnProperty(e2, "ALLOWED_ATTR") ? addToSet({}, e2.ALLOWED_ATTR, Re) : F, Ee = objectHasOwnProperty(e2, "ALLOWED_NAMESPACES") ? addToSet({}, e2.ALLOWED_NAMESPACES, stringToString) : Se, me = objectHasOwnProperty(e2, "ADD_URI_SAFE_ATTR") ? addToSet(clone(de), e2.ADD_URI_SAFE_ATTR, Re) : de, pe = objectHasOwnProperty(e2, "ADD_DATA_URI_TAGS") ? addToSet(clone(ue), e2.ADD_DATA_URI_TAGS, Re) : ue, se = objectHasOwnProperty(e2, "FORBID_CONTENTS") ? addToSet({}, e2.FORBID_CONTENTS, Re) : ce, W = objectHasOwnProperty(e2, "FORBID_TAGS") ? addToSet({}, e2.FORBID_TAGS, Re) : clone({}), B = objectHasOwnProperty(e2, "FORBID_ATTR") ? addToSet({}, e2.FORBID_ATTR, Re) : clone({}), le = !!objectHasOwnProperty(e2, "USE_PROFILES") && e2.USE_PROFILES, Y = false !== e2.ALLOW_ARIA_ATTR, X = false !== e2.ALLOW_DATA_ATTR, $ = e2.ALLOW_UNKNOWN_PROTOCOLS || false, q = false !== e2.ALLOW_SELF_CLOSE_IN_ATTR, K = e2.SAFE_FOR_TEMPLATES || false, V = false !== e2.SAFE_FOR_XML, Z = e2.WHOLE_DOCUMENT || false, ee = e2.RETURN_DOM || false, te = e2.RETURN_DOM_FRAGMENT || false, ne = e2.RETURN_TRUSTED_TYPE || false, Q = e2.FORCE_BODY || false, re = false !== e2.SANITIZE_DOM, oe = e2.SANITIZE_NAMED_PROPS || false, ae = false !== e2.KEEP_CONTENT, ie = e2.IN_PLACE || false, k = e2.ALLOWED_URI_REGEXP || IS_ALLOWED_URI, he = e2.NAMESPACE || ge, _e = e2.MATHML_TEXT_INTEGRATION_POINTS || _e, Ae = e2.HTML_INTEGRATION_POINTS || Ae, G = e2.CUSTOM_ELEMENT_HANDLING || {}, e2.CUSTOM_ELEMENT_HANDLING && Ce(e2.CUSTOM_ELEMENT_HANDLING.tagNameCheck) && (G.tagNameCheck = e2.CUSTOM_ELEMENT_HANDLING.tagNameCheck), e2.CUSTOM_ELEMENT_HANDLING && Ce(e2.CUSTOM_ELEMENT_HANDLING.attributeNameCheck) && (G.attributeNameCheck = e2.CUSTOM_ELEMENT_HANDLING.attributeNameCheck), e2.CUSTOM_ELEMENT_HANDLING && "boolean" == typeof e2.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements && (G.allowCustomizedBuiltInElements = e2.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements), K && (X = false), te && (ee = true), le && (z = addToSet({}, text), U = [], true === le.html && (addToSet(z, html$1), addToSet(U, html)), true === le.svg && (addToSet(z, svg$1), addToSet(U, svg), addToSet(U, xml)), true === le.svgFilters && (addToSet(z, svgFilters), addToSet(U, svg), addToSet(U, xml)), true === le.mathMl && (addToSet(z, mathMl$1), addToSet(U, mathMl), addToSet(U, xml))), e2.ADD_TAGS && ("function" == typeof e2.ADD_TAGS ? j.tagCheck = e2.ADD_TAGS : (z === H && (z = clone(z)), addToSet(z, e2.ADD_TAGS, Re))), e2.ADD_ATTR && ("function" == typeof e2.ADD_ATTR ? j.attributeCheck = e2.ADD_ATTR : (U === F && (U = clone(U)), addToSet(U, e2.ADD_ATTR, Re))), e2.ADD_URI_SAFE_ATTR && addToSet(me, e2.ADD_URI_SAFE_ATTR, Re), e2.FORBID_CONTENTS && (se === ce && (se = clone(se)), addToSet(se, e2.FORBID_CONTENTS, Re)), e2.ADD_FORBID_CONTENTS && (se === ce && (se = clone(se)), addToSet(se, e2.ADD_FORBID_CONTENTS, Re)), ae && (z["#text"] = true), Z && addToSet(z, ["html", "head", "body"]), z.table && (addToSet(z, ["tbody"]), delete W.tbody), e2.TRUSTED_TYPES_POLICY) {
        if ("function" != typeof e2.TRUSTED_TYPES_POLICY.createHTML) throw typeErrorCreate('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');
        if ("function" != typeof e2.TRUSTED_TYPES_POLICY.createScriptURL) throw typeErrorCreate('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');
        S = e2.TRUSTED_TYPES_POLICY, _ = S.createHTML("");
      } else void 0 === S && (S = _createTrustedTypesPolicy(d, o)), null !== S && "string" == typeof _ && (_ = S.createHTML(""));
      freeze && freeze(e2), De = e2;
    }
  }, ve = addToSet({}, [...svg$1, ...svgFilters, ...svgDisallowed]), Ie = addToSet({}, [...mathMl$1, ...mathMlDisallowed]), Le = function(e2) {
    arrayPush(t.removed, { element: e2 });
    try {
      E(e2).removeChild(e2);
    } catch (t2) {
      g(e2);
    }
  }, Me = function(e2, n2) {
    try {
      arrayPush(t.removed, { attribute: n2.getAttributeNode(e2), from: n2 });
    } catch (e3) {
      arrayPush(t.removed, { attribute: null, from: n2 });
    }
    if (n2.removeAttribute(e2), "is" === e2) if (ee || te) try {
      Le(n2);
    } catch (e3) {
    }
    else try {
      n2.setAttribute(e2, "");
    } catch (e3) {
    }
  }, Pe = function(e2) {
    let t2 = null, r2 = null;
    if (Q) e2 = "<remove></remove>" + e2;
    else {
      const t3 = stringMatch(e2, /^[\r\n\t ]+/);
      r2 = t3 && t3[0];
    }
    "application/xhtml+xml" === Ne && he === ge && (e2 = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>' + e2 + "</body></html>");
    const o2 = S ? S.createHTML(e2) : e2;
    if (he === ge) try {
      t2 = new m().parseFromString(o2, Ne);
    } catch (e3) {
    }
    if (!t2 || !t2.documentElement) {
      t2 = A.createDocument(he, "template", null);
      try {
        t2.documentElement.innerHTML = ye ? _ : o2;
      } catch (e3) {
      }
    }
    const a2 = t2.body || t2.documentElement;
    return e2 && r2 && a2.insertBefore(n.createTextNode(r2), a2.childNodes[0] || null), he === ge ? O.call(t2, Z ? "html" : "body")[0] : Z ? t2.documentElement : a2;
  }, ke = function(e2) {
    return b.call(e2.ownerDocument || e2, e2, c.SHOW_ELEMENT | c.SHOW_COMMENT | c.SHOW_TEXT | c.SHOW_PROCESSING_INSTRUCTION | c.SHOW_CDATA_SECTION, null);
  }, ze = function(e2) {
    return e2 instanceof u && ("string" != typeof e2.nodeName || "string" != typeof e2.textContent || "function" != typeof e2.removeChild || !(e2.attributes instanceof p) || "function" != typeof e2.removeAttribute || "function" != typeof e2.setAttribute || "string" != typeof e2.namespaceURI || "function" != typeof e2.insertBefore || "function" != typeof e2.hasChildNodes);
  }, He = function(e2) {
    return "function" == typeof l && e2 instanceof l;
  };
  function Ue(e2, n2, r2) {
    arrayForEach(e2, (e3) => {
      e3.call(t, n2, r2, De);
    });
  }
  const Fe = function(e2) {
    let n2 = null;
    if (Ue(D.beforeSanitizeElements, e2, null), ze(e2)) return Le(e2), true;
    const r2 = Re(e2.nodeName);
    if (Ue(D.uponSanitizeElement, e2, { tagName: r2, allowedTags: z }), V && e2.hasChildNodes() && !He(e2.firstElementChild) && regExpTest(/<[/\w!]/g, e2.innerHTML) && regExpTest(/<[/\w!]/g, e2.textContent)) return Le(e2), true;
    if (e2.nodeType === NODE_TYPE.progressingInstruction) return Le(e2), true;
    if (V && e2.nodeType === NODE_TYPE.comment && regExpTest(/<[/\w]/g, e2.data)) return Le(e2), true;
    if (!(j.tagCheck instanceof Function && j.tagCheck(r2)) && (!z[r2] || W[r2])) {
      if (!W[r2] && We(r2)) {
        if (G.tagNameCheck instanceof RegExp && regExpTest(G.tagNameCheck, r2)) return false;
        if (G.tagNameCheck instanceof Function && G.tagNameCheck(r2)) return false;
      }
      if (ae && !se[r2]) {
        const t2 = E(e2) || e2.parentNode, n3 = y(e2) || e2.childNodes;
        if (n3 && t2) {
          for (let r3 = n3.length - 1; r3 >= 0; --r3) {
            const o2 = T(n3[r3], true);
            o2.__removalCount = (e2.__removalCount || 0) + 1, t2.insertBefore(o2, h(e2));
          }
        }
      }
      return Le(e2), true;
    }
    return e2 instanceof s && !(function(e3) {
      let t2 = E(e3);
      t2 && t2.tagName || (t2 = { namespaceURI: he, tagName: "template" });
      const n3 = stringToLowerCase(e3.tagName), r3 = stringToLowerCase(t2.tagName);
      return !!Ee[e3.namespaceURI] && (e3.namespaceURI === Te ? t2.namespaceURI === ge ? "svg" === n3 : t2.namespaceURI === fe ? "svg" === n3 && ("annotation-xml" === r3 || _e[r3]) : Boolean(ve[n3]) : e3.namespaceURI === fe ? t2.namespaceURI === ge ? "math" === n3 : t2.namespaceURI === Te ? "math" === n3 && Ae[r3] : Boolean(Ie[n3]) : e3.namespaceURI === ge ? !(t2.namespaceURI === Te && !Ae[r3]) && !(t2.namespaceURI === fe && !_e[r3]) && !Ie[n3] && (be[n3] || !ve[n3]) : !("application/xhtml+xml" !== Ne || !Ee[e3.namespaceURI]));
    })(e2) ? (Le(e2), true) : "noscript" !== r2 && "noembed" !== r2 && "noframes" !== r2 || !regExpTest(/<\/no(script|embed|frames)/i, e2.innerHTML) ? (K && e2.nodeType === NODE_TYPE.text && (n2 = e2.textContent, arrayForEach([w, C, x], (e3) => {
      n2 = stringReplace(n2, e3, " ");
    }), e2.textContent !== n2 && (arrayPush(t.removed, { element: e2.cloneNode() }), e2.textContent = n2)), Ue(D.afterSanitizeElements, e2, null), false) : (Le(e2), true);
  }, Ge = function(e2, t2, r2) {
    if (re && ("id" === t2 || "name" === t2) && (r2 in n || r2 in we)) return false;
    if (X && !B[t2] && regExpTest(v, t2)) ;
    else if (Y && regExpTest(I, t2)) ;
    else if (j.attributeCheck instanceof Function && j.attributeCheck(t2, e2)) ;
    else if (!U[t2] || B[t2]) {
      if (!(We(e2) && (G.tagNameCheck instanceof RegExp && regExpTest(G.tagNameCheck, e2) || G.tagNameCheck instanceof Function && G.tagNameCheck(e2)) && (G.attributeNameCheck instanceof RegExp && regExpTest(G.attributeNameCheck, t2) || G.attributeNameCheck instanceof Function && G.attributeNameCheck(t2, e2)) || "is" === t2 && G.allowCustomizedBuiltInElements && (G.tagNameCheck instanceof RegExp && regExpTest(G.tagNameCheck, r2) || G.tagNameCheck instanceof Function && G.tagNameCheck(r2)))) return false;
    } else if (me[t2]) ;
    else if (regExpTest(k, stringReplace(r2, M, ""))) ;
    else if ("src" !== t2 && "xlink:href" !== t2 && "href" !== t2 || "script" === e2 || 0 !== stringIndexOf(r2, "data:") || !pe[e2]) {
      if ($ && !regExpTest(L, stringReplace(r2, M, ""))) ;
      else if (r2) return false;
    } else ;
    return true;
  }, We = function(e2) {
    return "annotation-xml" !== e2 && stringMatch(e2, P);
  }, Be = function(e2) {
    Ue(D.beforeSanitizeAttributes, e2, null);
    const { attributes: n2 } = e2;
    if (!n2 || ze(e2)) return;
    const r2 = { attrName: "", attrValue: "", keepAttr: true, allowedAttributes: U, forceKeepAttr: void 0 };
    let o2 = n2.length;
    for (; o2--; ) {
      const a2 = n2[o2], { name: i2, namespaceURI: l2, value: s2 } = a2, c2 = Re(i2), p2 = s2;
      let u2 = "value" === i2 ? p2 : stringTrim(p2);
      if (r2.attrName = c2, r2.attrValue = u2, r2.keepAttr = true, r2.forceKeepAttr = void 0, Ue(D.uponSanitizeAttribute, e2, r2), u2 = r2.attrValue, !oe || "id" !== c2 && "name" !== c2 || (Me(i2, e2), u2 = "user-content-" + u2), V && regExpTest(/((--!?|])>)|<\/(style|title|textarea)/i, u2)) {
        Me(i2, e2);
        continue;
      }
      if ("attributename" === c2 && stringMatch(u2, "href")) {
        Me(i2, e2);
        continue;
      }
      if (r2.forceKeepAttr) continue;
      if (!r2.keepAttr) {
        Me(i2, e2);
        continue;
      }
      if (!q && regExpTest(/\/>/i, u2)) {
        Me(i2, e2);
        continue;
      }
      K && arrayForEach([w, C, x], (e3) => {
        u2 = stringReplace(u2, e3, " ");
      });
      const m2 = Re(e2.nodeName);
      if (Ge(m2, c2, u2)) {
        if (S && "object" == typeof d && "function" == typeof d.getAttributeType) if (l2) ;
        else switch (d.getAttributeType(m2, c2)) {
          case "TrustedHTML":
            u2 = S.createHTML(u2);
            break;
          case "TrustedScriptURL":
            u2 = S.createScriptURL(u2);
        }
        if (u2 !== p2) try {
          l2 ? e2.setAttributeNS(l2, i2, u2) : e2.setAttribute(i2, u2), ze(e2) ? Le(e2) : arrayPop(t.removed);
        } catch (t2) {
          Me(i2, e2);
        }
      } else Me(i2, e2);
    }
    Ue(D.afterSanitizeAttributes, e2, null);
  }, je = function e2(t2) {
    let n2 = null;
    const r2 = ke(t2);
    for (Ue(D.beforeSanitizeShadowDOM, t2, null); n2 = r2.nextNode(); ) Ue(D.uponSanitizeShadowNode, n2, null), Fe(n2), Be(n2), n2.content instanceof a && e2(n2.content);
    Ue(D.afterSanitizeShadowDOM, t2, null);
  };
  return t.sanitize = function(e2) {
    let n2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {}, o2 = null, i2 = null, s2 = null, c2 = null;
    if (ye = !e2, ye && (e2 = "<!-->"), "string" != typeof e2 && !He(e2)) {
      if ("function" != typeof e2.toString) throw typeErrorCreate("toString is not a function");
      if ("string" != typeof (e2 = e2.toString())) throw typeErrorCreate("dirty is not a string, aborting");
    }
    if (!t.isSupported) return e2;
    if (J || xe(n2), t.removed = [], "string" == typeof e2 && (ie = false), ie) {
      if (e2.nodeName) {
        const t2 = Re(e2.nodeName);
        if (!z[t2] || W[t2]) throw typeErrorCreate("root node is forbidden and cannot be sanitized in-place");
      }
    } else if (e2 instanceof l) o2 = Pe("<!---->"), i2 = o2.ownerDocument.importNode(e2, true), i2.nodeType === NODE_TYPE.element && "BODY" === i2.nodeName || "HTML" === i2.nodeName ? o2 = i2 : o2.appendChild(i2);
    else {
      if (!ee && !K && !Z && -1 === e2.indexOf("<")) return S && ne ? S.createHTML(e2) : e2;
      if (o2 = Pe(e2), !o2) return ee ? null : ne ? _ : "";
    }
    o2 && Q && Le(o2.firstChild);
    const p2 = ke(ie ? e2 : o2);
    for (; s2 = p2.nextNode(); ) Fe(s2), Be(s2), s2.content instanceof a && je(s2.content);
    if (ie) return e2;
    if (ee) {
      if (te) for (c2 = N.call(o2.ownerDocument); o2.firstChild; ) c2.appendChild(o2.firstChild);
      else c2 = o2;
      return (U.shadowroot || U.shadowrootmode) && (c2 = R.call(r, c2, true)), c2;
    }
    let u2 = Z ? o2.outerHTML : o2.innerHTML;
    return Z && z["!doctype"] && o2.ownerDocument && o2.ownerDocument.doctype && o2.ownerDocument.doctype.name && regExpTest(DOCTYPE_NAME, o2.ownerDocument.doctype.name) && (u2 = "<!DOCTYPE " + o2.ownerDocument.doctype.name + ">\n" + u2), K && arrayForEach([w, C, x], (e3) => {
      u2 = stringReplace(u2, e3, " ");
    }), S && ne ? S.createHTML(u2) : u2;
  }, t.setConfig = function() {
    xe(arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}), J = true;
  }, t.clearConfig = function() {
    De = null, J = false;
  }, t.isValidAttribute = function(e2, t2, n2) {
    De || xe({});
    const r2 = Re(e2), o2 = Re(t2);
    return Ge(r2, o2, n2);
  }, t.addHook = function(e2, t2) {
    "function" == typeof t2 && arrayPush(D[e2], t2);
  }, t.removeHook = function(e2, t2) {
    if (void 0 !== t2) {
      const n2 = arrayLastIndexOf(D[e2], t2);
      return -1 === n2 ? void 0 : arraySplice(D[e2], n2, 1)[0];
    }
    return arrayPop(D[e2]);
  }, t.removeHooks = function(e2) {
    D[e2] = [];
  }, t.removeAllHooks = function() {
    D = _createHooksMap();
  }, t;
}
var purify = createDOMPurify();
export { purify as default };
