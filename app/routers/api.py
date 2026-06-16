"""后端API - 通过 NiceGUI 的 app 对象注册 FastAPI 路由"""
import logging
import json
import asyncio
import os
import re
import time
from datetime import date
from pathlib import Path

from nicegui import app
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

from app.services.image_variants import get_display_image, get_thumb
from app.state import (
    save_upload,
    save_output,
    save_canvas_snapshot,
    get_session,
    create_session,
    export_sessions_csv,
    export_sessions_json,
    resolve_media_path,
    media_url,
    media_filename,
)
from app.db import (
    get_export_summary,
    get_ready_generation_notifications,
    mark_ready_generation_notifications_seen,
)

logger = logging.getLogger(__name__)

MEDIA_CACHE_HEADERS = {
    'Cache-Control': 'private, max-age=31536000, immutable',
    'X-Content-Type-Options': 'nosniff',
}
PRESET_IMAGE_DIR = Path(__file__).resolve().parent.parent / 'static' / 'images' / 'presets'


def _cached_file_response(path: Path, *, media_type: str | None = None) -> FileResponse:
    return FileResponse(str(path), media_type=media_type, headers=MEDIA_CACHE_HEADERS)


def _safe_child_file(directory: Path, filename: str) -> Path | None:
    if not filename or filename != Path(filename).name:
        return None
    path = directory / filename
    if not path.exists() or not path.is_file():
        return None
    return path


def _load_dotenv_once() -> None:
    env_path = Path(__file__).resolve().parents[2] / '.env'
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip().lstrip('\ufeff')
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv_once()
EXPORT_KEY = os.getenv('HEALING_EXPORT_KEY', '')
if EXPORT_KEY == 'healing2024':
    EXPORT_KEY = ''
MAX_LOG_PAYLOAD_BYTES = 8192
_feishu_retry_task: asyncio.Task | None = None
_generation_tasks: dict[str, asyncio.Task] = {}


def _clean_text(value, max_len: int = 160) -> str:
    text = str(value or '').strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text[:max_len]


def _safe_error(message: str = '生成失败，请稍后再试') -> JSONResponse:
    return JSONResponse({'error': message}, status_code=500)


def _generation_error_response(exc: Exception) -> JSONResponse:
    message = str(exc)
    if 'HEALING_IMAGE_API_KEY' in message:
        return JSONResponse(
            {'error': '图像生成服务尚未配置，请设置 HEALING_IMAGE_API_KEY 后再生成。'},
            status_code=503,
        )
    if 'API 响应中未找到图片' in message or '图片数据格式无法识别' in message:
        return JSONResponse(
            {'error': '图像生成服务已响应，但未返回可用图片。请检查模型 API 返回格式。'},
            status_code=502,
        )
    return _safe_error()


def _public_generation_error(exc: Exception) -> str:
    message = str(exc)
    if 'timed out' in message.lower() or '超时' in message:
        return '图像生成服务响应超时，请稍后重试；已保留上一版结果。'
    if 'HEALING_IMAGE_API_KEY' in message:
        return '图像生成服务尚未配置，请联系管理员。'
    if 'API 响应中未找到图片' in message or '图片数据格式无法识别' in message:
        return '图像生成服务已响应，但未返回可用图片。'
    return message[:180] or '生成失败，请稍后再试。'


def _generation_running(session) -> bool:
    if not session:
        return False
    status = getattr(session, 'generation_status', '') or ''
    if status not in ('queued', 'running'):
        return False
    task = _generation_tasks.get(getattr(session, 'id', '') or getattr(session, 'session_id', ''))
    return bool(task and not task.done())


def _start_background_task(session_id: str, runner) -> None:
    old_task = _generation_tasks.get(session_id)
    if old_task and not old_task.done():
        return
    task = asyncio.create_task(runner())
    _generation_tasks[session_id] = task

    def _cleanup(done_task: asyncio.Task) -> None:
        if _generation_tasks.get(session_id) is done_task:
            _generation_tasks.pop(session_id, None)

    task.add_done_callback(_cleanup)


def _mark_generation_start(session, mode: str) -> None:
    session.mode_used = mode
    session.generation_status = 'running'
    session.generation_error = ''
    session.generation_started_at = time.time()
    session.generation_finished_at = None
    session.generation_count = int(getattr(session, 'generation_count', 0) or 0) + 1


def _mark_generation_failure(session_id: str, exc: Exception) -> None:
    session = get_session(session_id)
    if not session:
        return
    session.generation_status = 'error'
    session.generation_error = _public_generation_error(exc)
    session.generation_finished_at = time.time()


def start_slider_generation_job(
    session_id: str,
    image_path: str,
    green: float,
    urban: float,
    vitality: float,
    light: float,
    selected_recommend: str = '',
) -> bool:
    session = get_session(session_id)
    if not session or _generation_running(session):
        return False
    session.green_level = green
    session.urban_level = urban
    session.vitality_level = vitality
    session.light_warmth = light
    session.selected_recommend = selected_recommend
    _mark_generation_start(session, 'slider')

    async def _runner() -> None:
        try:
            from app.services.sd_service import generate_from_sliders
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_from_sliders,
                str(image_path), green, urban, vitality, light,
            )
            latest = get_session(session_id)
            if latest:
                latest.llm_prompt = used_prompt
            save_output(session_id, result_bytes)
        except Exception as exc:
            logger.exception("后台滑杆生成失败")
            _mark_generation_failure(session_id, exc)

    _start_background_task(session_id, _runner)
    return True


def start_chat_generation_job(
    session_id: str,
    image_path: str,
    mood_tags: list[str],
    extra_text: str = '',
) -> bool:
    session = get_session(session_id)
    if not session or _generation_running(session):
        return False
    session.chat_moods = mood_tags
    session.chat_extra = extra_text
    _mark_generation_start(session, 'chat')

    async def _runner() -> None:
        try:
            from app.services.chat_service import generate_from_chat
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_from_chat,
                str(image_path), mood_tags, extra_text,
            )
            latest = get_session(session_id)
            if latest:
                latest.llm_prompt = used_prompt
            save_output(session_id, result_bytes)
        except Exception as exc:
            logger.exception("后台对话生成失败")
            _mark_generation_failure(session_id, exc)

    _start_background_task(session_id, _runner)
    return True


def start_inpaint_generation_job(session_id: str, image_path: str, elements: list[dict]) -> bool:
    session = get_session(session_id)
    if not session or _generation_running(session):
        return False
    session.placed_elements = elements
    _mark_generation_start(session, 'drag')

    async def _runner() -> None:
        try:
            from app.services.sd_service import generate_inpainting
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_inpainting,
                str(image_path), elements,
            )
            latest = get_session(session_id)
            if latest:
                latest.llm_prompt = used_prompt
            save_output(session_id, result_bytes)
        except Exception as exc:
            logger.exception("后台元素生成失败")
            _mark_generation_failure(session_id, exc)

    _start_background_task(session_id, _runner)
    return True


def start_sketch_generation_job(session_id: str, image_path: str, sketch_data: dict) -> bool:
    session = get_session(session_id)
    if not session or _generation_running(session):
        return False
    session.sketch_data = sketch_data
    if sketch_data.get('type') == 'element':
        session.placed_elements = sketch_data.get('results', [])
    if sketch_data.get('moodParams'):
        mp = sketch_data['moodParams']
        session.green_level = mp.get('green', 50)
        session.urban_level = mp.get('urban', 50)
        session.vitality_level = mp.get('vitality', 50)
        session.light_warmth = mp.get('light', 50)
    _mark_generation_start(session, 'inspire')

    async def _runner() -> None:
        try:
            from app.services.sd_service import generate_from_sketch
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_from_sketch,
                str(image_path),
                sketch_data,
            )
            latest = get_session(session_id)
            if latest:
                latest.llm_prompt = used_prompt
            save_output(session_id, result_bytes)
        except Exception as exc:
            logger.exception("后台灵感生成失败")
            _mark_generation_failure(session_id, exc)

    _start_background_task(session_id, _runner)
    return True


async def _json_payload(request: Request) -> tuple[dict | None, JSONResponse | None]:
    try:
        data = await request.json()
    except Exception:
        return None, JSONResponse({'error': '无效 JSON'}, status_code=400)
    if not isinstance(data, dict):
        return None, JSONResponse({'error': 'JSON body 必须是对象'}, status_code=400)
    return data, None


def _allowed_inpaint_names() -> set[str]:
    try:
        from app.pages.drag_mode import _ALL_ELEMENTS
        return {str(item.get('name', '')).strip() for item in _ALL_ELEMENTS if item.get('name')}
    except Exception:
        return set()


def _looks_like_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    if re.search(r'[a-z]{8,}', lowered):
        return True
    risky_words = ('ignore', 'instruction', 'system', 'developer', 'assistant', 'prompt', 'jailbreak')
    return any(word in lowered for word in risky_words)


def _clean_birth_date(value) -> str:
    text = _clean_text(value, 16)
    if not text:
        return ''
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValueError('birth_date must be YYYY-MM-DD')


def _admin_key_ok(request: Request) -> bool:
    return bool(EXPORT_KEY) and request.query_params.get('key', '') == EXPORT_KEY


def _normalize_inpaint_elements(raw_elements, *, limit: int = 20) -> list[dict]:
    if not isinstance(raw_elements, list):
        raise ValueError('elements must be a list')

    def _text(value, max_len: int = 80) -> str:
        return _clean_text(value, max_len)

    def _number(value, default: float, min_value: float, max_value: float) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(min_value, min(max_value, number))

    normalized: list[dict] = []
    for item in raw_elements[:limit]:
        if not isinstance(item, dict):
            continue
        name = _text(item.get('name') or item.get('elemName'))
        icon = _text(item.get('icon') or item.get('elemIcon'), 32)
        category = _text(item.get('category') or item.get('cat') or item.get('elemCat'), 40)
        if _looks_like_prompt_injection(name):
            continue
        if not name and not icon:
            continue
        normalized.append({
            'icon': icon,
            'name': name,
            'category': category,
            'x': round(_number(item.get('x'), 50.0, 0.0, 100.0), 1),
            'y': round(_number(item.get('y'), 50.0, 0.0, 100.0), 1),
            'scale': round(_number(item.get('scale'), 1.0, 0.05, 8.0), 2),
            'rotation': round(_number(item.get('rotation'), 0.0, -360.0, 360.0)),
            'elemId': _text(item.get('elemId'), 80),
        })
    return normalized


def register_api_routes():
    """注册所有 API 路由到 NiceGUI 底层的 FastAPI app 上"""

    @app.on_event('startup')
    async def start_feishu_sync_retry_loop():
        global _feishu_retry_task
        if _feishu_retry_task is None or _feishu_retry_task.done():
            from app.services.feishu_sync import feishu_retry_loop
            _feishu_retry_task = asyncio.create_task(feishu_retry_loop())

    @app.get('/api/session')
    async def new_session():
        sid = create_session()
        return JSONResponse({'session_id': sid})

    @app.post('/api/upload')
    async def upload_image(request: Request):
        try:
            form = await request.form()
        except Exception:
            return JSONResponse({'error': '上传数据无效'}, status_code=400)
        file = form.get('file')
        session_id = _clean_text(form.get('session_id', ''), 64)
        scene_type = _clean_text(form.get('scene_type', ''), 80)

        if not file:
            return JSONResponse({'error': '未选择文件'}, status_code=400)
        if not session_id:
            session_id = create_session()
        elif not get_session(session_id):
            return JSONResponse({'error': '无效会话'}, status_code=400)

        file_bytes = await file.read()
        if len(file_bytes) > 20 * 1024 * 1024:
            return JSONResponse({'error': '文件过大，请选择小于20MB的图片'}, status_code=400)

        try:
            saved_path = save_upload(session_id, file_bytes, file.filename)
        except ValueError:
            return JSONResponse({'error': '请上传有效的 JPEG、PNG 或 WebP 图片'}, status_code=400)
        session = get_session(session_id)
        if session:
            session.scene_type = scene_type

        logger.info(f"图片上传成功: session={session_id}, path={saved_path}")
        return JSONResponse({
            'session_id': session_id,
            'image_url': f'/api/image/{Path(saved_path).name}',
            'display_url': media_url(saved_path, display=True),
            'thumbnail_url': media_url(saved_path, thumb=True),
        })

    @app.post('/api/canvas-snapshot')
    async def upload_canvas_snapshot(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        data_url = data.get('data_url', '')
        if not session_id or not get_session(session_id):
            return JSONResponse({'error': 'invalid session'}, status_code=400)
        if not isinstance(data_url, str) or not data_url.startswith('data:image/'):
            return JSONResponse({'error': 'invalid canvas snapshot'}, status_code=400)
        try:
            saved_path = save_canvas_snapshot(session_id, data_url)
        except ValueError as exc:
            return JSONResponse({'error': str(exc)[:160]}, status_code=400)
        except Exception:
            logger.exception("canvas snapshot upload failed")
            return JSONResponse({'error': 'canvas snapshot upload failed'}, status_code=500)
        return JSONResponse({
            'ok': True,
            'path': saved_path,
            'image_url': media_url(saved_path),
            'display_url': media_url(saved_path, display=True),
            'thumbnail_url': media_url(saved_path, thumb=True),
        })

    @app.post('/api/canvas-history/delete')
    async def delete_canvas_history_item(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        filename = _clean_text(data.get('filename', ''), 160)
        session = get_session(session_id) if session_id else None
        if not session:
            return JSONResponse({'error': 'invalid session'}, status_code=400)
        if not filename or filename != Path(filename).name:
            return JSONResponse({'error': 'invalid filename'}, status_code=400)

        history = getattr(session, 'canvas_history', []) or []
        if not isinstance(history, list):
            history = []
        kept = []
        removed = []
        for item in history:
            if isinstance(item, dict) and media_filename(item.get('path') or '') == filename:
                removed.append(item)
            else:
                kept.append(item)
        if not removed:
            return JSONResponse({'error': 'not found'}, status_code=404)

        generation_history = getattr(session, 'generation_history', []) or []
        if isinstance(generation_history, list):
            for item in generation_history:
                if isinstance(item, dict) and media_filename(item.get('canvas_path') or '') == filename:
                    item['canvas_path'] = ''
            session.generation_history = generation_history

        if kept:
            session.canvas_history = kept[-30:]
        else:
            session.canvas_history = [{
                'layout_recovery_disabled': True,
                'deleted_at': time.time(),
            }]
        latest = ''
        if kept:
            latest_item = sorted(
                [item for item in kept if isinstance(item, dict)],
                key=lambda item: float(item.get('created_at') or 0),
            )[-1]
            latest = str(latest_item.get('path') or '')
        session.canvas_snapshot_path = latest
        return JSONResponse({'ok': True, 'removed': len(removed), 'latest': media_url(latest) if latest else ''})

    @app.get('/api/image/{filename}')
    async def serve_image(filename: str, request: Request):
        thumb = request.query_params.get('thumb')
        display = request.query_params.get('display') or request.query_params.get('preview')
        path = resolve_media_path(filename)
        if path:
            if thumb:
                thumb_path = get_thumb(path)
                if thumb_path:
                    return _cached_file_response(thumb_path, media_type='image/jpeg')
            if display:
                display_path = get_display_image(path)
                if display_path:
                    return _cached_file_response(display_path, media_type='image/jpeg')
            return _cached_file_response(path)
        return JSONResponse({'error': '图片不存在'}, status_code=404)

    @app.get('/api/preset-image/{filename}')
    async def serve_preset_image(filename: str, request: Request):
        thumb = request.query_params.get('thumb')
        display = request.query_params.get('display') or request.query_params.get('preview')
        path = _safe_child_file(PRESET_IMAGE_DIR, filename)
        if path:
            if thumb:
                thumb_path = get_thumb(path)
                if thumb_path:
                    return _cached_file_response(thumb_path, media_type='image/jpeg')
            if display:
                display_path = get_display_image(path)
                if display_path:
                    return _cached_file_response(display_path, media_type='image/jpeg')
            return _cached_file_response(path)
        return JSONResponse({'error': '图片不存在'}, status_code=404)

    @app.get('/api/download/{filename}')
    async def download_image(filename: str):
        path = resolve_media_path(filename)
        if not path:
            return JSONResponse({'error': '图片不存在'}, status_code=404)
        return FileResponse(
            str(path),
            media_type='application/octet-stream',
            filename=path.name,
            headers={'Content-Disposition': f'attachment; filename="{path.name}"'},
        )

    @app.get('/api/generation/notifications')
    async def generation_notifications():
        rows, count = get_ready_generation_notifications(limit=20)
        ready = []
        for session in rows:
            ready.append({
                'session_id': session['id'],
                'title': session.get('record_title') or '未命名草稿',
                'mode': session.get('mode_used') or '',
                'finished_at': float(session.get('generation_finished_at') or 0),
                'image_url': media_url(session.get('generated_image_path') or '', thumb=True),
            })
        return JSONResponse({'ready': ready, 'count': count})

    @app.post('/api/generation/notifications/seen')
    async def mark_generation_notifications_seen():
        updated = mark_ready_generation_notifications_seen(time.time())
        return JSONResponse({'ok': True, 'updated': updated})

    @app.post('/api/generate/slider')
    async def generate_slider(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)

        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        def _param(name: str) -> float:
            try:
                return max(0.0, min(100.0, float(data.get(name, 50))))
            except (TypeError, ValueError):
                return 50.0

        green = _param('green_level')
        urban = _param('urban_level')
        vitality = _param('vitality_level')
        light = _param('light_warmth')
        selected_recommend = _clean_text(data.get('selected_recommend', ''), 80)

        session.green_level = green
        session.urban_level = urban
        session.vitality_level = vitality
        session.light_warmth = light
        session.mode_used = 'slider'
        session.selected_recommend = selected_recommend
        session.generation_count = getattr(session, 'generation_count', 0) + 1

        try:
            from app.services.sd_service import generate_from_sliders
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_from_sliders,
                str(upload_path), green, urban, vitality, light,
            )
            session.llm_prompt = used_prompt
            out_path = save_output(session_id, result_bytes)
            return JSONResponse({
                'generated_url': f'/api/image/{Path(out_path).name}',
                'params': {'green': green, 'urban': urban, 'vitality': vitality, 'light': light},
            })
        except Exception as e:
            logger.exception("滑杆模式生成失败")
            return _generation_error_response(e)

    @app.post('/api/generate/chat')
    async def generate_chat(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)

        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        mood_tags = data.get('mood_tags', [])
        extra_text = _clean_text(data.get('extra_text', ''), 220)
        if not isinstance(mood_tags, list):
            mood_tags = []
        from app.services.chat_service import MOOD_PROMPT_MAP
        allowed_moods = set(MOOD_PROMPT_MAP.keys())
        mood_tags = [_clean_text(tag, 32) for tag in mood_tags]
        mood_tags = [tag for tag in mood_tags if tag in allowed_moods][:2]

        if not mood_tags and not extra_text:
            return JSONResponse({'error': '请先输入一种感受，或选择至少一个情绪标签'}, status_code=400)

        session.mode_used = 'chat'
        session.chat_moods = mood_tags
        session.chat_extra = extra_text
        session.generation_count = getattr(session, 'generation_count', 0) + 1

        try:
            from app.services.chat_service import generate_from_chat
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_from_chat,
                str(upload_path), mood_tags, extra_text,
            )
            session.llm_prompt = used_prompt
            out_path = save_output(session_id, result_bytes)
            return JSONResponse({
                'generated_url': f'/api/image/{Path(out_path).name}',
                'mood_tags': mood_tags,
            })
        except Exception as e:
            logger.exception("对话改造模式生成失败")
            return _generation_error_response(e)

    @app.post('/api/generate/inpaint')
    async def generate_inpaint(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)

        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        try:
            elements = _normalize_inpaint_elements(data.get('elements', []))
        except ValueError:
            return JSONResponse({'error': 'elements 必须是数组'}, status_code=400)
        if not elements:
            return JSONResponse({'error': '请至少放置一个元素'}, status_code=400)

        session.placed_elements = elements
        session.mode_used = 'drag'
        session.generation_count = getattr(session, 'generation_count', 0) + 1

        try:
            from app.services.sd_service import generate_inpainting
            result_bytes, used_prompt = await asyncio.to_thread(
                generate_inpainting,
                str(upload_path), elements,
            )
            session.llm_prompt = used_prompt
            out_path = save_output(session_id, result_bytes)
            return JSONResponse({
                'generated_url': f'/api/image/{Path(out_path).name}',
                'element_count': len(elements),
            })
        except Exception as e:
            logger.exception("Inpainting 生成失败")
            return _generation_error_response(e)

    @app.post('/api/generate/slider/background')
    async def generate_slider_background(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)
        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        def _param(name: str) -> float:
            try:
                return max(0.0, min(100.0, float(data.get(name, 50))))
            except (TypeError, ValueError):
                return 50.0

        started = start_slider_generation_job(
            session_id,
            str(upload_path),
            _param('green_level'),
            _param('urban_level'),
            _param('vitality_level'),
            _param('light_warmth'),
            _clean_text(data.get('selected_recommend', ''), 80),
        )
        if not started:
            return JSONResponse({'error': 'AI 已在后台生成中，请稍候。'}, status_code=409)
        return JSONResponse({'ok': True, 'status': 'running'})

    @app.post('/api/generate/chat/background')
    async def generate_chat_background(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)
        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)

        mood_tags = data.get('mood_tags', [])
        extra_text = _clean_text(data.get('extra_text', ''), 220)
        if not isinstance(mood_tags, list):
            mood_tags = []
        from app.services.chat_service import MOOD_PROMPT_MAP
        allowed_moods = set(MOOD_PROMPT_MAP.keys())
        mood_tags = [_clean_text(tag, 32) for tag in mood_tags]
        mood_tags = [tag for tag in mood_tags if tag in allowed_moods][:2]
        if not mood_tags and not extra_text:
            return JSONResponse({'error': '请先输入一种感受，或选择至少一个情绪标签'}, status_code=400)

        started = start_chat_generation_job(session_id, str(upload_path), mood_tags, extra_text)
        if not started:
            return JSONResponse({'error': 'AI 已在后台生成中，请稍候。'}, status_code=409)
        return JSONResponse({'ok': True, 'status': 'running'})

    @app.post('/api/generate/inpaint/background')
    async def generate_inpaint_background(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)
        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)
        try:
            elements = _normalize_inpaint_elements(data.get('elements', []))
        except ValueError:
            return JSONResponse({'error': 'elements 必须是数组'}, status_code=400)
        if not elements:
            return JSONResponse({'error': '请至少放置一个元素'}, status_code=400)

        started = start_inpaint_generation_job(session_id, str(upload_path), elements)
        if not started:
            return JSONResponse({'error': 'AI 已在后台生成中，请稍候。'}, status_code=409)
        return JSONResponse({'ok': True, 'status': 'running'})

    @app.post('/api/generate/sketch/background')
    async def generate_sketch_background(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error
        session_id = _clean_text(data.get('session_id', ''), 64)
        session = get_session(session_id)
        upload_path = resolve_media_path(session.uploaded_image_path if session else '')
        if not session or not upload_path:
            return JSONResponse({'error': '请先上传图片'}, status_code=400)
        sketch_data = data.get('sketch_data')
        if not isinstance(sketch_data, dict) or int(sketch_data.get('strokeCount') or 0) <= 0:
            return JSONResponse({'error': '请先在画布上画几笔'}, status_code=400)

        started = start_sketch_generation_job(session_id, str(upload_path), sketch_data)
        if not started:
            return JSONResponse({'error': 'AI 已在后台生成中，请稍候。'}, status_code=409)
        return JSONResponse({'ok': True, 'status': 'running'})

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

        session_id = _clean_text(data.get('session_id', ''), 64)
        action = _clean_text(data.get('action', ''), 80)
        payload = data.get('data', {})
        if not isinstance(payload, dict):
            payload = {'value': payload}
        try:
            if len(json.dumps(payload, ensure_ascii=False)) > MAX_LOG_PAYLOAD_BYTES:
                payload = {'truncated': True}
        except Exception:
            payload = {'invalid': True}

        if session_id and action:
            from app.db import log_interaction
            if not get_session(session_id):
                return JSONResponse({'ok': True, 'skipped': True})
            try:
                log_interaction(session_id, action, payload)
            except Exception:
                logger.exception("前端行为日志写入失败")
                return JSONResponse({'ok': True, 'skipped': True})

        return JSONResponse({'ok': True})

    @app.post('/api/hci/participant')
    async def api_hci_participant(request: Request):
        data, error = await _json_payload(request)
        if error:
            return error

        try:
            user_id = data.get('user_id')
            user_id = int(user_id) if user_id not in (None, '') else None
            from app.db import normalize_hci_participant_code
            payload = {
                'user_id': user_id,
                'participant_code': normalize_hci_participant_code(_clean_text(data.get('participant_code', ''), 64)),
                'registered_name': _clean_text(data.get('registered_name', ''), 40),
                'site_id': _clean_text(data.get('site_id', ''), 64),
                'study_phase': _clean_text(data.get('study_phase', ''), 32),
                'diagnosis_group': _clean_text(data.get('diagnosis_group', ''), 80),
                'birth_date': _clean_birth_date(data.get('birth_date', '')),
                'gender': _clean_text(data.get('gender', ''), 32),
                'education_band': _clean_text(data.get('education_band', ''), 64),
            }
        except ValueError as exc:
            return JSONResponse({'error': str(exc)}, status_code=400)

        if not payload['participant_code']:
            return JSONResponse({'error': 'participant_code is required'}, status_code=400)

        try:
            from app.db import upsert_hci_participant
            participant = upsert_hci_participant(**payload)
            from app.services.feishu_sync import sync_due_jobs_once
            asyncio.create_task(sync_due_jobs_once(limit=5))
            return JSONResponse({'ok': True, 'participant': participant})
        except Exception as exc:
            logger.exception('HCI participant save failed')
            return JSONResponse({'error': str(exc)}, status_code=500)

    @app.get('/api/feishu/sync/status')
    async def api_feishu_sync_status(request: Request):
        if not _admin_key_ok(request):
            return JSONResponse({'error': 'admin key required'}, status_code=403)
        from app.db import get_feishu_sync_summary
        from app.services.feishu_sync import feishu_enabled
        return JSONResponse({
            'enabled': feishu_enabled(),
            'summary': get_feishu_sync_summary(),
        })

    @app.post('/api/feishu/sync/retry')
    async def api_feishu_sync_retry(request: Request):
        if not _admin_key_ok(request):
            return JSONResponse({'error': 'admin key required'}, status_code=403)
        from app.services.feishu_sync import sync_due_jobs_once
        result = await sync_due_jobs_once(limit=20)
        return JSONResponse({'ok': True, **result})

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
        if not EXPORT_KEY or key != EXPORT_KEY:
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
        if not EXPORT_KEY or key != EXPORT_KEY:
            return JSONResponse({'error': '需要研究者密码'}, status_code=403)
        data = export_sessions_json()
        return JSONResponse(data, headers={
            'Content-Disposition': 'attachment; filename="healing_environment_data.json"',
        })

    @app.get('/api/export/summary')
    async def api_export_summary(request: Request):
        key = request.query_params.get('key', '')
        if not EXPORT_KEY or key != EXPORT_KEY:
            return JSONResponse({'error': '需要研究者密码'}, status_code=403)
        return JSONResponse(get_export_summary())

    logger.info("API 路由注册完成")
