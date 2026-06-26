"""应用全局状态管理 - SQLite 持久化 + 兼容层"""
import uuid
import time
import base64
import binascii
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional
from urllib.parse import quote

from PIL import Image, UnidentifiedImageError

from app.db import (
    init_db,
    create_session as db_create_session,
    get_session as db_get_session,
    update_session as db_update_session,
    get_all_sessions as db_get_all_sessions,
    export_csv,
    export_json,
    log_interaction,
)
from app.services.image_variants import warm_image_variants

UPLOAD_DIR = Path(__file__).parent.parent / 'uploads'
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs'
PRESET_DIR = Path(__file__).parent / 'static' / 'images' / 'presets'
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
MEDIA_ROOTS = tuple(path.resolve() for path in (UPLOAD_DIR, OUTPUT_DIR, PRESET_DIR))
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_CANVAS_JSON_BYTES = 2 * 1024 * 1024
MAX_IMAGE_PIXELS = 24_000_000
IMAGE_EXTENSIONS = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'WEBP': '.webp',
}

# 初始化数据库
init_db()


def media_filename(path_value: str | Path | None) -> str:
    """Return a basename from paths saved on either Windows or Linux."""
    if not path_value:
        return ''
    raw = str(path_value).strip()
    if not raw:
        return ''
    for path_cls in (Path, PurePosixPath, PureWindowsPath):
        try:
            name = path_cls(raw).name
            if name:
                return name
        except Exception:
            pass
    return raw.replace('\\', '/').rstrip('/').rsplit('/', 1)[-1]


def _is_within_media_roots(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except Exception:
        return False
    return any(resolved == root or root in resolved.parents for root in MEDIA_ROOTS)


def resolve_media_path(path_value: str | Path | None) -> Path | None:
    """Resolve stored media paths after moving the app between machines."""
    if not path_value:
        return None
    raw = str(path_value).strip()
    if raw:
        direct_path = Path(raw)
        if direct_path.exists() and _is_within_media_roots(direct_path):
            return direct_path

    name = media_filename(path_value)
    if not name:
        return None
    if name != Path(name).name or name != PureWindowsPath(name).name:
        return None
    for directory in (UPLOAD_DIR, OUTPUT_DIR, PRESET_DIR):
        candidate = directory / name
        if candidate.exists() and _is_within_media_roots(candidate):
            return candidate
    return None


def media_url(path_value: str | Path | None, *, thumb: bool = False, display: bool = False) -> str:
    path = resolve_media_path(path_value)
    if not path:
        return ''
    params = []
    if thumb:
        params.append('thumb=1')
    elif display:
        params.append('display=1')
    try:
        stat = path.stat()
        params.append(f'v={stat.st_size:x}-{stat.st_mtime_ns:x}')
    except OSError:
        pass
    suffix = '?' + '&'.join(params) if params else ''
    return f'/api/image/{quote(path.name)}{suffix}'


class SessionProxy:
    """对 DB session dict 的属性代理，保持原有 session.xxx = yyy 的用法"""

    def __init__(self, data: dict):
        object.__setattr__(self, '_data', data)
        object.__setattr__(self, '_sid', data['id'])

    def __getattr__(self, name):
        data = object.__getattribute__(self, '_data')
        # 映射 session_id -> id
        if name == 'session_id':
            return data['id']
        if name in data:
            return data[name]
        # 兼容旧的 computed properties
        if name == 'experiment_condition':
            parts = []
            if data.get('scene_type'):
                parts.append(data['scene_type'])
            if data.get('mode_used'):
                parts.append(data['mode_used'])
            return '_'.join(parts)
        if name == 'interaction_duration_seconds':
            if data.get('survey_completed_at') and data.get('created_at'):
                return round(data['survey_completed_at'] - data['created_at'], 1)
            return 0.0
        if name == 'prs_mean':
            answers = data.get('survey_answers', {})
            scores = [answers.get(f'prs{i}', 0) for i in range(1, 6)]
            valid = [s for s in scores if s > 0]
            return round(sum(valid) / len(valid), 2) if valid else 0.0
        if name == 'emo_mean':
            answers = data.get('survey_answers', {})
            scores = [answers.get(f'emo{i}', 0) for i in range(1, 5)]
            valid = [s for s in scores if s > 0]
            return round(sum(valid) / len(valid), 2) if valid else 0.0
        raise AttributeError(f"SessionProxy has no attribute '{name}'")

    def __setattr__(self, name, value):
        data = object.__getattribute__(self, '_data')
        sid = object.__getattribute__(self, '_sid')
        if name == 'session_id':
            return
        data[name] = value
        db_update_session(sid, **{name: value})

    def to_dict(self):
        return dict(object.__getattribute__(self, '_data'))


def get_session(session_id: str) -> SessionProxy | None:
    """获取 session，不存在则返回 None"""
    data = db_get_session(session_id)
    if data:
        return SessionProxy(data)
    return None


def create_session(user_id: int | None = None) -> str:
    """创建新 session，返回 session_id"""
    sid = uuid.uuid4().hex[:12]
    db_create_session(sid, user_id=user_id)
    return sid


def _verified_image_format(file_bytes: bytes) -> str:
    if not file_bytes or len(file_bytes) > MAX_IMAGE_BYTES:
        raise ValueError('invalid image size')
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
            image_format = (img.format or '').upper()
            width, height = img.size
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise ValueError('invalid image data') from exc
    if image_format not in IMAGE_EXTENSIONS:
        raise ValueError('unsupported image format')
    if width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS:
        raise ValueError('image dimensions out of range')
    return image_format


def save_upload(session_id: str, file_bytes: bytes, filename: str) -> str:
    """保存上传的图片，返回路径"""
    if not db_get_session(session_id):
        raise ValueError('invalid session')
    image_format = _verified_image_format(file_bytes)
    ext = IMAGE_EXTENSIONS[image_format]
    safe_name = f"{session_id}_{uuid.uuid4().hex[:6]}{ext}"
    path = UPLOAD_DIR / safe_name
    path.write_bytes(file_bytes)
    warm_image_variants(path)
    db_update_session(session_id, uploaded_image_path=str(path))
    return str(path)


def save_output(session_id: str, image_bytes: bytes, suffix: str = '.png') -> str:
    """保存AI生成的输出图片，返回路径"""
    session = db_get_session(session_id)
    if not session:
        raise ValueError('invalid session')
    _verified_image_format(image_bytes)
    suffix = suffix.lower()
    if suffix not in IMAGE_EXTENSIONS.values():
        suffix = '.png'
    safe_name = f"{session_id}_out_{uuid.uuid4().hex[:6]}{suffix}"
    path = OUTPUT_DIR / safe_name
    path.write_bytes(image_bytes)
    warm_image_variants(path)
    history = session.get('generation_history') or []
    if not isinstance(history, list):
        history = []
    history.append({
        'path': str(path),
        'created_at': time.time(),
        'mode': session.get('mode_used', ''),
        'prompt': session.get('llm_prompt', ''),
        'canvas_path': session.get('canvas_snapshot_path', ''),
        'elements': _canvas_element_snapshot(session),
        'safety_policy_version': session.get('safety_policy_version', ''),
        'safety_actions': session.get('safety_actions', []),
        'blocked_or_reframed_items': session.get('blocked_or_reframed_items', []),
        'risk_text_detected': bool(session.get('risk_text_detected')),
        'risk_text_reframed': session.get('risk_text_reframed', ''),
        'final_safe_prompt': session.get('final_safe_prompt') or session.get('llm_prompt', ''),
        'image_input_mode': session.get('image_input_mode') or 'original_image_edit',
        'mask_used': bool(session.get('mask_used')),
        'guide_image_used': bool(session.get('guide_image_used')),
    })
    db_update_session(
        session_id,
        generated_image_path=str(path),
        generation_history=history[-20:],
        generation_status='done',
        generation_error='',
        generation_finished_at=time.time(),
    )
    return str(path)


SNAPSHOT_DIR = Path(__file__).parent.parent / 'outputs'


def save_canvas_snapshot(session_id: str, data_url: str) -> str:
    """保存画布快照（base64 data URL），返回路径"""
    session = db_get_session(session_id)
    if not session:
        raise ValueError('invalid session')
    if not isinstance(data_url, str) or ',' not in data_url:
        raise ValueError('invalid canvas snapshot')
    header, encoded = data_url.split(',', 1)
    if not header.startswith('data:image/'):
        raise ValueError('invalid canvas snapshot type')
    if len(encoded) > MAX_IMAGE_BYTES * 2:
        raise ValueError('canvas snapshot is too large')
    try:
        img_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError('invalid canvas snapshot encoding') from exc
    _verified_image_format(img_bytes)
    safe_name = f"{session_id}_canvas_{uuid.uuid4().hex[:6]}.png"
    path = SNAPSHOT_DIR / safe_name
    path.write_bytes(img_bytes)
    warm_image_variants(path)
    history = session.get('canvas_history') or []
    if not isinstance(history, list):
        history = []
    elements = _canvas_element_snapshot(session)
    history.append({
        'path': str(path),
        'created_at': time.time(),
        'mode': session.get('mode_used', ''),
        'elements': elements,
        'element_count': len(elements),
    })
    db_update_session(session_id, canvas_snapshot_path=str(path), canvas_history=history[-30:])
    return str(path)


def _canvas_element_snapshot(session: dict) -> list[dict]:
    """Return the elements that belong to the canvas state being saved."""
    mode = session.get('mode_used', '')
    if mode == 'inspire':
        sketch_data = session.get('sketch_data') or {}
        if isinstance(sketch_data, dict):
            annotation_elements = _inspire_annotation_elements(sketch_data)
            if annotation_elements:
                return annotation_elements[:40]
            results = sketch_data.get('results')
            if isinstance(results, list) and results:
                return [item for item in results if isinstance(item, dict)][:40]
    placed = session.get('placed_elements') or []
    if isinstance(placed, list):
        return [item for item in placed if isinstance(item, dict)][:40]
    return []


def _inspire_annotation_elements(sketch_data: dict) -> list[dict]:
    """Return user-guided sketch labels as displayable element snapshots."""
    items: list[dict] = []
    annotations = sketch_data.get('userAnnotations')
    if isinstance(annotations, list):
        for item in annotations:
            if not isinstance(item, dict):
                continue
            label = str(
                item.get('safe_userLabel')
                or item.get('userLabel')
                or item.get('original_userLabel')
                or item.get('label')
                or ''
            ).strip()
            if not label:
                continue
            element = dict(item)
            element['elemName'] = label
            element.setdefault('source', 'user')
            items.append(element)
    if items:
        return _dedupe_canvas_elements(items)

    stroke_log = sketch_data.get('strokeLog')
    if isinstance(stroke_log, list):
        for item in stroke_log:
            if not isinstance(item, dict):
                continue
            label = str(
                item.get('safe_userLabel')
                or item.get('userLabel')
                or item.get('autoLabel')
                or item.get('label')
                or ''
            ).strip()
            if not label:
                continue
            element = dict(item)
            element['elemName'] = label
            element.setdefault('source', 'user' if item.get('userLabel') else 'auto')
            items.append(element)
    return _dedupe_canvas_elements(items)


def _dedupe_canvas_elements(items: list[dict]) -> list[dict]:
    seen = set()
    unique: list[dict] = []
    for item in items:
        name = str(item.get('elemName') or item.get('name') or item.get('label') or '').strip()
        key = (name, str(item.get('x') or ''), str(item.get('y') or ''))
        if not name or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique[:40]


def save_canvas_json(session_id: str, json_str: str) -> str:
    """保存画布 Fabric.js 对象 JSON（用于恢复编辑状态），返回路径"""
    if not db_get_session(session_id):
        raise ValueError('invalid session')
    if not isinstance(json_str, str):
        raise ValueError('invalid canvas json')
    if len(json_str.encode('utf-8')) > MAX_CANVAS_JSON_BYTES:
        raise ValueError('canvas json is too large')
    parsed = json.loads(json_str)
    if not isinstance(parsed, (dict, list)):
        raise ValueError('invalid canvas json shape')
    safe_name = f"{session_id}_canvas_objs_{uuid.uuid4().hex[:6]}.json"
    path = OUTPUT_DIR / safe_name
    path.write_text(json_str, encoding='utf-8')
    db_update_session(session_id, canvas_json_path=str(path))
    return str(path)


def get_all_sessions():
    return db_get_all_sessions()


def export_sessions_csv() -> str:
    return export_csv()


def export_sessions_json() -> list[dict]:
    return export_json()
