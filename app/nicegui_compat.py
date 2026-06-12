"""Compatibility hooks for NiceGUI's generated browser shell."""

from __future__ import annotations

from jinja2 import BaseLoader, TemplateNotFound
from nicegui import client as nicegui_client


_IMPORTMAP_ANCHOR = '    <script type="importmap">\n'
_POLYFILL_TAG = (
    '    <script async src="{{ prefix | safe }}/static/vendor/es-module-shims.js"></script>\n'
)


class _ImportMapPolyfillLoader(BaseLoader):
    def __init__(self, wrapped_loader: BaseLoader) -> None:
        self._wrapped_loader = wrapped_loader

    def get_source(self, environment, template: str):
        try:
            source, filename, uptodate = self._wrapped_loader.get_source(environment, template)
        except TemplateNotFound:
            raise

        if (
            template == 'index.html'
            and 'es-module-shims.js' not in source
            and _IMPORTMAP_ANCHOR in source
        ):
            source = source.replace(_IMPORTMAP_ANCHOR, _POLYFILL_TAG + _IMPORTMAP_ANCHOR, 1)

        return source, filename, uptodate


def install_importmap_polyfill() -> None:
    """Load an import-map polyfill before NiceGUI's generated import map."""

    loader = nicegui_client.templates.env.loader
    if isinstance(loader, _ImportMapPolyfillLoader):
        return
    nicegui_client.templates.env.loader = _ImportMapPolyfillLoader(loader)
