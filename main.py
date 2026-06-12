"""灵感世界 - 主入口"""
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)

from nicegui import ui, app

from app.nicegui_compat import install_importmap_polyfill


install_importmap_polyfill()


_navigate_to = ui.navigate.to


def _smooth_navigate_to(target, *args, **kwargs):
    """Keep route changes visually continuous while NiceGUI rebuilds pages."""
    try:
        ui.run_javascript('window.HealingMotion && window.HealingMotion.showRouteTransition();')
        ui.timer(0.08, lambda: _navigate_to(target, *args, **kwargs), once=True)
    except Exception:
        _navigate_to(target, *args, **kwargs)


ui.navigate.to = _smooth_navigate_to

MAX_UPLOAD_BODY_BYTES = int(os.getenv('MAX_UPLOAD_BODY_BYTES', str(24 * 1024 * 1024)))


class UploadBodyPreReadMiddleware:
    """ASGI middleware: pre-read the full body for /api/upload before it
    reaches NiceGUI's BaseHTTPMiddleware, which is known to deadlock
    the ASGI receive channel for browser-initiated multipart uploads."""

    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        if (
            scope['type'] == 'http'
            and scope.get('method', '') == 'POST'
            and scope.get('path', '') == '/api/upload'
        ):
            chunks = []
            total_size = 0
            while True:
                msg = await receive()
                chunk = msg.get('body', b'')
                if chunk:
                    chunks.append(chunk)
                    total_size += len(chunk)
                    if total_size > MAX_UPLOAD_BODY_BYTES:
                        await send({
                            'type': 'http.response.start',
                            'status': 413,
                            'headers': [
                                (b'content-type', b'application/json; charset=utf-8'),
                                (b'cache-control', b'no-store'),
                            ],
                        })
                        await send({
                            'type': 'http.response.body',
                            'body': '{"error":"文件过大，请选择小于20MB的图片"}'.encode('utf-8'),
                        })
                        return
                if not msg.get('more_body', False):
                    break
            body = b''.join(chunks)
            body_sent = False

            async def cached_receive():
                nonlocal body_sent
                if not body_sent:
                    body_sent = True
                    return {'type': 'http.request', 'body': body, 'more_body': False}
                return await receive()

            await self.app(scope, cached_receive, send)
        else:
            await self.app(scope, receive, send)


app.add_middleware(UploadBodyPreReadMiddleware)


class StaticCacheHeaderMiddleware:
    """Add browser cache headers for static assets loaded on every page."""

    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        is_static = scope.get('type') == 'http' and scope.get('path', '').startswith('/static/')

        async def cached_send(message):
            if is_static and message.get('type') == 'http.response.start':
                headers = list(message.get('headers') or [])
                has_cache_control = any(k.lower() == b'cache-control' for k, _ in headers)
                if not has_cache_control:
                    headers.append((b'cache-control', b'public, max-age=604800, stale-while-revalidate=86400'))
                    message['headers'] = headers
            await send(message)

        await self.app(scope, receive, cached_send if is_static else send)


app.add_middleware(StaticCacheHeaderMiddleware)

# 静态文件服务（canvas_editor.js 等前端资源）
app.add_static_files('/static', 'app/static')

# 初始化数据库
from app.db import init_db
init_db()

# 注册后端 API 路由
from app.routers.api import register_api_routes
register_api_routes()

# 注册前端页面路由
from app.pages.login import create_login_page
from app.pages.home import create_home_page
from app.pages.camera import create_camera_page
from app.pages.mode_select import create_mode_select_page
from app.pages.slider_mode import create_slider_page
from app.pages.drag_mode import create_drag_page
from app.pages.ai_mode import create_ai_mode_page
from app.pages.inspire_mode import create_inspire_page
from app.pages.chat_mode import create_chat_mode_page
from app.pages.result import create_result_page
from app.pages.immerse import create_immerse_page
from app.pages.survey import create_survey_page
from app.pages.report import create_report_page
from app.pages.records import create_records_page
from app.pages.about import create_about_page
from app.pages.account import create_account_page
from app.pages.participant_info import create_participant_info_page
from app.pages.export import create_export_page

create_login_page()
create_home_page()
create_camera_page()
create_mode_select_page()
create_slider_page()
create_drag_page()
create_ai_mode_page()
create_inspire_page()
create_chat_mode_page()
create_result_page()
create_immerse_page()
create_survey_page()
create_report_page()
create_records_page()
create_about_page()
create_account_page()
create_participant_info_page()
create_export_page()

ui.run(
    title='灵感世界',
    host='0.0.0.0',
    port=int(os.getenv('PORT', '6420')),
    reload=False,
    favicon='🌿',
    dark=False,
    language='zh-CN',
    storage_secret=(
        os.getenv('HEALING_STORAGE_SECRET')
        or os.getenv('NICEGUI_STORAGE_SECRET')
        or 'healing-environment-2024-secret'
    ),
)
