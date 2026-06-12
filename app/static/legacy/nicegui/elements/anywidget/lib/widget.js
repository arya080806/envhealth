var __async = (__this, __arguments, generator) => {
  return new Promise((resolve, reject) => {
    var fulfilled = (value) => {
      try {
        step(generator.next(value));
      } catch (e) {
        reject(e);
      }
    };
    var rejected = (value) => {
      try {
        step(generator.throw(value));
      } catch (e) {
        reject(e);
      }
    };
    var step = (x) => x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected);
    step((generator = generator.apply(__this, __arguments)).next());
  });
};
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function is_href(str) {
  return str.startsWith("http://") || str.startsWith("https://");
}
function load_css_href(href, anywidget_id) {
  return __async(this, null, function* () {
    let prev = document.querySelector(`link[id='${anywidget_id}']`);
    if (prev) {
      let newLink = (
        /** @type {HTMLLinkElement} */
        prev.cloneNode()
      );
      newLink.href = href;
      newLink.addEventListener("load", () => prev == null ? void 0 : prev.remove());
      newLink.addEventListener("error", () => prev == null ? void 0 : prev.remove());
      prev.after(newLink);
      return;
    }
    return new Promise((resolve) => {
      let link = Object.assign(document.createElement("link"), {
        rel: "stylesheet",
        href,
        onload: resolve
      });
      document.head.appendChild(link);
    });
  });
}
function load_css_text(css_text, anywidget_id) {
  let prev = document.querySelector(`style[id='${anywidget_id}']`);
  if (prev) {
    prev.textContent = css_text;
    return;
  }
  let style = Object.assign(document.createElement("style"), {
    id: anywidget_id,
    type: "text/css"
  });
  style.appendChild(document.createTextNode(css_text));
  document.head.appendChild(style);
}
function load_css(css, anywidget_id) {
  return __async(this, null, function* () {
    if (!css || !anywidget_id) return;
    if (is_href(css)) return load_css_href(css, anywidget_id);
    return load_css_text(css, anywidget_id);
  });
}
function load_esm(esm) {
  return __async(this, null, function* () {
    if (is_href(esm)) {
      return yield import(
        /* webpackIgnore: true */
        /* @vite-ignore */
        esm
      );
    }
    let url = URL.createObjectURL(new Blob([esm], { type: "text/javascript" }));
    let mod = yield import(
      /* webpackIgnore: true */
      /* @vite-ignore */
      url
    );
    URL.revokeObjectURL(url);
    return mod;
  });
}
function warn_render_deprecation(anywidget_id) {
  console.warn(`[anywidget] Deprecation Warning for ${anywidget_id}: Direct export of a 'render' will likely be deprecated in the future. To migrate ...

Remove the 'export' keyword from 'render'
-----------------------------------------

export function render({ model, el }) { ... }
^^^^^^

Create a default export that returns an object with 'render'
------------------------------------------------------------

function render({ model, el }) { ... }
         ^^^^^^
export default { render }
                 ^^^^^^

Pin to anywidget>=0.9.0 in your pyproject.toml
----------------------------------------------

dependencies = ["anywidget>=0.9.0"]

To learn more, please see: https://github.com/manzt/anywidget/pull/395.
`);
}
function load_widget(esm, anywidget_id) {
  return __async(this, null, function* () {
    let mod = yield load_esm(esm);
    if (mod.render) {
      let _a;
      warn_render_deprecation(anywidget_id);
      return {
        initialize() {
          return __async(this, null, function* () {
          });
        },
        render: mod.render
      };
    }
    assert(
      mod.default,
      `[anywidget] module must export a default function or object.`
    );
    let widget = typeof mod.default === "function" ? yield mod.default() : mod.default;
    return widget;
  });
}
export { load_widget, load_css };
