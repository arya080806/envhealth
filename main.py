"""环境疗愈工坊 - 主入口"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)

from nicegui import ui, app

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
from app.pages.result import create_result_page
from app.pages.immerse import create_immerse_page
from app.pages.survey import create_survey_page
from app.pages.report import create_report_page
from app.pages.records import create_records_page
from app.pages.about import create_about_page
from app.pages.export import create_export_page

create_login_page()
create_home_page()
create_camera_page()
create_mode_select_page()
create_slider_page()
create_drag_page()
create_ai_mode_page()
create_result_page()
create_immerse_page()
create_survey_page()
create_report_page()
create_records_page()
create_about_page()
create_export_page()

ui.run(
    title='环境疗愈工坊',
    host='0.0.0.0',
    port=6420,
    reload=False,
    favicon='🌿',
    dark=False,
    language='zh-CN',
    storage_secret='healing-environment-2024-secret',
)
