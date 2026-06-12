function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function is_href(str) {
  return str.startsWith("http://") || str.startsWith("https://");
}
async function load_css_href(href, anywidget_id) {
  let prev = document.querySelector("link[id='".concat(anywidget_id, "']"));
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
}
function load_css_text(css_text, anywidget_id) {
  let prev = document.querySelector("style[id='".concat(anywidget_id, "']"));
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
async function load_css(css, anywidget_id) {
  if (!css || !anywidget_id) return;
  if (is_href(css)) return load_css_href(css, anywidget_id);
  return load_css_text(css, anywidget_id);
}
async function load_esm(esm) {
  if (is_href(esm)) {
    return await import(
      /* webpackIgnore: true */
      /* @vite-ignore */
      esm
    );
  }
  let url = URL.createObjectURL(new Blob([esm], { type: "text/javascript" }));
  let mod = await import(
    /* webpackIgnore: true */
    /* @vite-ignore */
    url
  );
  URL.revokeObjectURL(url);
  return mod;
}
function warn_render_deprecation(anywidget_id) {
  console.warn("[anywidget] Deprecation Warning for ".concat(anywidget_id, ": Direct export of a 'render' will likely be deprecated in the future. To migrate ...\n\nRemove the 'export' keyword from 'render'\n-----------------------------------------\n\nexport function render({ model, el }) { ... }\n^^^^^^\n\nCreate a default export that returns an object with 'render'\n------------------------------------------------------------\n\nfunction render({ model, el }) { ... }\n         ^^^^^^\nexport default { render }\n                 ^^^^^^\n\nPin to anywidget>=0.9.0 in your pyproject.toml\n----------------------------------------------\n\ndependencies = [\"anywidget>=0.9.0\"]\n\nTo learn more, please see: https://github.com/manzt/anywidget/pull/395.\n"));
}
async function load_widget(esm, anywidget_id) {
  let mod = await load_esm(esm);
  if (mod.render) {
    warn_render_deprecation(anywidget_id);
    return {
      async initialize() {
      },
      render: mod.render
    };
  }
  assert(
    mod.default,
    "[anywidget] module must export a default function or object."
  );
  let widget = typeof mod.default === "function" ? await mod.default() : mod.default;
  return widget;
}
export { load_widget, load_css };
