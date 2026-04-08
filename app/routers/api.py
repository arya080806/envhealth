"""后端API - 通过 NiceGUI 的 app 对象注册 FastAPI 路由"""
import logging
import json
import asyncio
from pathlib import Path

from nicegui import app
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

from app.state import save_upload, save_output, get_session, create_session, export_sessions_csv, export_sessions_json
from app.db import get_export_summary

logger = logging.getLogger(__name__)

# 研究者导出密码
EXPORT_KEY = 'healing2024'


def register_api_routes():
    """注册所有 API 路由到 NiceGUI 底层的 FastAPI app 上"""

    @app.get('/api/session')
    async def new_session():
        sid = create_session()
        return JSONResponse({'session_id': sid})

    @app.post('/api/upload')
    async def upload_image(request: Request):
        form = await request.form()
        file = form.get('file')
        session_id = form.get('session_id', '')
        scene_type = form.get('scene_type', '')

        if not file:
            return JSONResponse({'error': '未选择文件'}, status_code=400)
        if not session_id:
            session_id = create_session()

        file_bytes = await file.read()
        if len(file_bytes) > 20 * 1024 * 1024:
            return JSONResponse({'error': '文件过大，请选择小于20MB的图片'}, status_code=400)

        saved_path = save_upload(session_id, file_bytes, file.filename)
        session = get_session(session_id)
        if session:
            session.scene_type = scene_type

        logger.info(f"图片上传成功: session={session_id}, path={saved_path}")
        return JSONResponse({
            'session_id': session_id,
            'image_url': f'/api/image/{Path(saved_path).name}',
        })

    @app.get('/api/image/{filename}')
    async def serve_image(filename: str):
        from app.state import UPLOAD_DIR, OUTPUT_DIR
        for directory in [UPLOAD_DIR, OUTPUT_DIR]:
            path = directory / filename
            if path.exists():
                return FileResponse(str(path))
        return JSONResponse({'error': '图片不存在'}, status_code=404)

    @app.post('/api/generate/slider')
    async def generate_slider(request: Request):
        data = await request.json()
        session_id = data.get('session_id', '')
        session = get_session(session_id)

        if not session or not session.uploaded_image_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        green = float(data.get('green_level', 50))
        urban = float(data.get('urban_level', 50))
        vitality = float(data.get('vitality_level', 50))
        light = float(data.get('light_warmth', 50))

        session.green_level = green
        session.urban_level = urban
        session.vitality_level = vitality
        session.light_warmth = light

        try:
            from app.services.sd_service import generate_from_sliders
            result_bytes = await asyncio.to_thread(
                generate_from_sliders,
                session.uploaded_image_path, green, urban, vitality, light,
            )
            out_path = save_output(session_id, result_bytes)
            return JSONResponse({
                'generated_url': f'/api/image/{Path(out_path).name}',
                'params': {'green': green, 'urban': urban, 'vitality': vitality, 'light': light},
            })
        except Exception as e:
            logger.exception("滑杆模式生成失败")
            return JSONResponse({'error': f'生成失败: {str(e)}'}, status_code=500)

    @app.post('/api/generate/inpaint')
    async def generate_inpaint(request: Request):
        data = await request.json()
        session_id = data.get('session_id', '')
        session = get_session(session_id)

        if not session or not session.uploaded_image_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        elements = data.get('elements', [])
        if not elements:
            return JSONResponse({'error': '请至少放置一个元素'}, status_code=400)

        session.placed_elements = elements

        try:
            from app.services.sd_service import generate_inpainting
            result_bytes = await asyncio.to_thread(
                generate_inpainting,
                session.uploaded_image_path, elements,
            )
            out_path = save_output(session_id, result_bytes)
            return JSONResponse({
                'generated_url': f'/api/image/{Path(out_path).name}',
                'element_count': len(elements),
            })
        except Exception as e:
            logger.exception("Inpainting 生成失败")
            return JSONResponse({'error': f'生成失败: {str(e)}'}, status_code=500)

    @app.post('/api/preload')
    async def preload_models():
        try:
            from app.services.sd_service import is_model_loaded
            if is_model_loaded():
                return JSONResponse({'status': 'already_loaded'})
            return JSONResponse({'status': 'loaded'})
        except Exception as e:
            logger.exception("模型预加载失败")
            return JSONResponse({'error': str(e)}, status_code=500)

    @app.post('/api/log/action')
    async def api_log_action(request: Request):
        """接收前端行为事件（画布操作日志）"""
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({'error': '无效 JSON'}, status_code=400)

        session_id = data.get('session_id', '')
        action = data.get('action', '')
        payload = data.get('data', {})

        if session_id and action:
            from app.db import log_interaction
            log_interaction(session_id, action, payload)

        return JSONResponse({'ok': True})

    @app.get('/api/status')
    async def status():
        try:
            from app.services.sd_service import is_model_loaded
            model_ready = is_model_loaded()
        except Exception:
            model_ready = False
        return JSONResponse({'server': 'running', 'model_loaded': model_ready})

    @app.get('/api/export/csv')
    async def api_export_csv(request: Request):
        key = request.query_params.get('key', '')
        if key != EXPORT_KEY:
            return JSONResponse({'error': '需要研究者密码'}, status_code=403)
        csv_content = export_sessions_csv()
        return Response(
            content=csv_content,
            media_type='text/csv; charset=utf-8-sig',
            headers={'Content-Disposition': 'attachment; filename="healing_environment_data.csv"'},
        )

    @app.get('/api/export/json')
    async def api_export_json(request: Request):
        key = request.query_params.get('key', '')
        if key != EXPORT_KEY:
            return JSONResponse({'error': '需要研究者密码'}, status_code=403)
        data = export_sessions_json()
        return JSONResponse(data, headers={
            'Content-Disposition': 'attachment; filename="healing_environment_data.json"',
        })

    @app.get('/api/export/summary')
    async def api_export_summary(request: Request):
        key = request.query_params.get('key', '')
        if key != EXPORT_KEY:
            return JSONResponse({'error': '需要研究者密码'}, status_code=403)
        return JSONResponse(get_export_summary())

    logger.info("API 路由注册完成")
