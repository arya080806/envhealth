"""Compatibility hooks for NiceGUI's generated browser shell."""

from __future__ import annotations

from pathlib import Path

from jinja2 import BaseLoader, TemplateNotFound
from nicegui import client as nicegui_client
from nicegui.dependencies import js_components, libraries, register_importmap_override


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_NICEGUI_ROOT = Path(nicegui_client.__file__).resolve().parent
_LEGACY_ROOT = _PROJECT_ROOT / 'app' / 'static' / 'legacy' / 'nicegui'
_ASSET_VERSION = '20260612-legacy1'
_IMPORTMAP_ANCHOR = '    <script type="importmap">\n'
_POLYFILL_TAG = (
    f'    <script src="{{{{ prefix | safe }}}}/static/vendor/es-module-shims.legacy.js?v={_ASSET_VERSION}"></script>\n'
)
_LEGACY_BOOTSTRAP = '''    <script>
      (function () {
        if (!String.prototype.replaceAll) {
          String.prototype.replaceAll = function (search, replacement) {
            return this.split(search).join(replacement);
          };
        }
        function showLoadError() {
          var app = document.getElementById('app');
          if (!app || app.childNodes.length > 0) return;
          app.innerHTML = '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:28px;text-align:center;color:#f6fbf4;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#123428;">'
            + '<div style="max-width:460px;line-height:1.65;">'
            + '<div style="font-size:18px;font-weight:700;margin-bottom:10px;">&#27491;&#22312;&#21551;&#29992; iPad &#20860;&#23481;&#21152;&#36733;</div>'
            + '<div style="font-size:14px;opacity:.88;">&#22914;&#26524;&#39029;&#38754;&#38271;&#26102;&#38388;&#20572;&#22312;&#36825;&#37324;&#65292;&#35831;&#21047;&#26032;&#19968;&#27425;&#65307;&#31995;&#32479;&#27491;&#22312;&#20351;&#29992;&#26087;&#29256; Safari &#21487;&#35299;&#26512;&#30340;&#21069;&#31471;&#36816;&#34892;&#26102;&#12290;</div>'
            + '<button onclick="location.reload()" style="margin-top:18px;border:0;border-radius:999px;padding:10px 18px;background:#f6fbf4;color:#123428;font-weight:700;">&#21047;&#26032;&#39029;&#38754;</button>'
            + '</div></div>';
        }
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', function () { setTimeout(showLoadError, 9000); });
        } else {
          setTimeout(showLoadError, 9000);
        }
      })();
    </script>
'''
_TEMPLATE_REPLACEMENTS = {
    '    <script>\n      addStyle = (c) => document.head.append(Object.assign(document.createElement("style"), { textContent: c }));\n    </script>':
        '    <script>\n'
        '      window.addStyle = function (c) {\n'
        '        var style = document.createElement("style");\n'
        '        style.textContent = c;\n'
        '        document.head.appendChild(style);\n'
        '      };\n'
        '    </script>',
    '      document.getElementById("esm-fallback")?.remove();':
        '      var esmFallback = document.getElementById("esm-fallback");\n'
        '      if (esmFallback) esmFallback.remove();',
    '    <script defer src="{{ prefix | safe }}/_nicegui/{{version}}/static/quasar.umd.prod.js"></script>':
        f'    <script defer src="{{{{ prefix | safe }}}}/static/legacy/nicegui/static/quasar.umd.prod.js?v={_ASSET_VERSION}"></script>',
    '    <script defer src="{{ prefix | safe }}/_nicegui/{{version}}/static/nicegui.js"></script>':
        f'    <script defer src="{{{{ prefix | safe }}}}/static/legacy/nicegui/static/nicegui.js?v={_ASSET_VERSION}"></script>',
    '    <script defer src="{{ prefix | safe }}/_nicegui/{{version}}/static/lang/{{ language }}.umd.prod.js"></script>':
        f'    <script defer src="{{{{ prefix | safe }}}}/static/legacy/nicegui/static/lang/{{{{ language }}}}.umd.prod.js?v={_ASSET_VERSION}"></script>',
    '          (document.getElementById(fragment) || document.querySelector(`a[name="${fragment}"]`))?.scrollIntoView();':
        '          var fragmentTarget = document.getElementById(fragment) || document.querySelector(`a[name="${fragment}"]`);\n'
        '          if (fragmentTarget) fragmentTarget.scrollIntoView();',
}
_IMPORTMAP_OVERRIDES = {
    'vue': f'/static/legacy/nicegui/static/vue.esm-browser.prod.js?v={_ASSET_VERSION}',
    'dompurify': f'/static/legacy/nicegui/static/dompurify.mjs?v={_ASSET_VERSION}',
}
_IMPORTMAPS_PATCHED = False


class _ImportMapPolyfillLoader(BaseLoader):
    def __init__(self, wrapped_loader: BaseLoader) -> None:
        self._wrapped_loader = wrapped_loader

    def get_source(self, environment, template: str):
        try:
            source, filename, uptodate = self._wrapped_loader.get_source(environment, template)
        except TemplateNotFound:
            raise

        if template == 'index.html':
            for old, new in _TEMPLATE_REPLACEMENTS.items():
                source = source.replace(old, new)
            if 'es-module-shims.legacy.js' not in source and _IMPORTMAP_ANCHOR in source:
                source = source.replace(_IMPORTMAP_ANCHOR, _POLYFILL_TAG + _LEGACY_BOOTSTRAP + _IMPORTMAP_ANCHOR, 1)

        return source, filename, uptodate


def _legacy_path_for(path: Path) -> Path | None:
    try:
        relative = path.resolve().relative_to(_NICEGUI_ROOT)
    except ValueError:
        return None
    legacy_path = _LEGACY_ROOT / relative
    return legacy_path if legacy_path.exists() else None


def register_legacy_importmap_overrides() -> None:
    """Point import-map dependencies to transpiled assets."""

    global _IMPORTMAPS_PATCHED
    if _IMPORTMAPS_PATCHED:
        return
    for name, url in _IMPORTMAP_OVERRIDES.items():
        register_importmap_override(name, url)
    _IMPORTMAPS_PATCHED = True


def patch_legacy_component_paths() -> None:
    """Serve transpiled NiceGUI component shims when available."""

    for component in js_components.values():
        legacy_path = _legacy_path_for(component.path)
        if legacy_path is not None:
            component.path = legacy_path
    for library in libraries.values():
        legacy_path = _legacy_path_for(library.path)
        if legacy_path is not None:
            library.path = legacy_path


def install_legacy_runtime() -> None:
    """Install old-Safari compatible assets into NiceGUI's generated shell."""

    loader = nicegui_client.templates.env.loader
    if not isinstance(loader, _ImportMapPolyfillLoader):
        nicegui_client.templates.env.loader = _ImportMapPolyfillLoader(loader)
    register_legacy_importmap_overrides()
    patch_legacy_component_paths()
