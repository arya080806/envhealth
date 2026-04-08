"""应用全局状态管理 - SQLite 持久化 + 兼容层"""
import uuid
import time
from pathlib import Path
from typing import Optional

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

UPLOAD_DIR = Path(__file__).parent.parent / 'uploads'
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs'
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 初始化数据库
init_db()


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


def save_upload(session_id: str, file_bytes: bytes, filename: str) -> str:
    """保存上传的图片，返回路径"""
    ext = Path(filename).suffix or '.jpg'
    safe_name = f"{session_id}_{uuid.uuid4().hex[:6]}{ext}"
    path = UPLOAD_DIR / safe_name
    path.write_bytes(file_bytes)
    db_update_session(session_id, uploaded_image_path=str(path))
    return str(path)


def save_output(session_id: str, image_bytes: bytes, suffix: str = '.png') -> str:
    """保存AI生成的输出图片，返回路径"""
    safe_name = f"{session_id}_out_{uuid.uuid4().hex[:6]}{suffix}"
    path = OUTPUT_DIR / safe_name
    path.write_bytes(image_bytes)
    db_update_session(session_id, generated_image_path=str(path))
    return str(path)


def get_all_sessions():
    return db_get_all_sessions()


def export_sessions_csv() -> str:
    return export_csv()


def export_sessions_json() -> list[dict]:
    return export_json()
