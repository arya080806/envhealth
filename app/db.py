"""SQLite 数据库层 - 持久化存储"""
import sqlite3
import json
import time
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'healing.db'


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = _get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL DEFAULT '',
            created_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            scene_type TEXT DEFAULT '',
            mode_used TEXT DEFAULT '',
            green_level REAL DEFAULT 50.0,
            urban_level REAL DEFAULT 50.0,
            vitality_level REAL DEFAULT 50.0,
            light_warmth REAL DEFAULT 50.0,
            placed_elements TEXT DEFAULT '[]',
            selected_recommend TEXT DEFAULT '',
            uploaded_image_path TEXT,
            generated_image_path TEXT,
            survey_answers TEXT DEFAULT '{}',
            created_at REAL NOT NULL,
            survey_completed_at REAL,
            generation_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            action TEXT NOT NULL,
            data TEXT DEFAULT '{}',
            timestamp REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    ''')
    conn.commit()

    # 迁移：为已有旧数据库补充新列
    for col, defn in [('generation_count', 'INTEGER DEFAULT 0')]:
        try:
            conn.execute(f'ALTER TABLE sessions ADD COLUMN {col} {defn}')
            conn.commit()
        except Exception:
            pass  # 列已存在，忽略

    conn.close()


# ── User 操作 ──────────────────────────────────────────

def create_or_get_user(participant_id: str, display_name: str = '') -> dict:
    """创建或获取用户，返回 {id, participant_id, display_name, created_at}"""
    conn = _get_conn()
    row = conn.execute(
        'SELECT * FROM users WHERE participant_id = ?', (participant_id,)
    ).fetchone()
    if row:
        if display_name and display_name != row['display_name']:
            conn.execute(
                'UPDATE users SET display_name = ? WHERE id = ?',
                (display_name, row['id'])
            )
            conn.commit()
            row = conn.execute('SELECT * FROM users WHERE id = ?', (row['id'],)).fetchone()
        conn.close()
        return dict(row)
    conn.execute(
        'INSERT INTO users (participant_id, display_name, created_at) VALUES (?, ?, ?)',
        (participant_id, display_name, time.time())
    )
    conn.commit()
    row = conn.execute(
        'SELECT * FROM users WHERE participant_id = ?', (participant_id,)
    ).fetchone()
    conn.close()
    return dict(row)


def get_user_by_id(user_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Session 操作 ──────────────────────────────────────

def create_session(session_id: str, user_id: int | None = None) -> dict:
    conn = _get_conn()
    conn.execute(
        'INSERT INTO sessions (id, user_id, created_at) VALUES (?, ?, ?)',
        (session_id, user_id, time.time())
    )
    conn.commit()
    row = conn.execute('SELECT * FROM sessions WHERE id = ?', (session_id,)).fetchone()
    conn.close()
    return dict(row)


def get_session(session_id: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute('SELECT * FROM sessions WHERE id = ?', (session_id,)).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['placed_elements'] = json.loads(result['placed_elements'] or '[]')
        result['survey_answers'] = json.loads(result['survey_answers'] or '{}')
        return result
    return None


def update_session(session_id: str, **kwargs):
    """更新 session 的任意字段"""
    conn = _get_conn()
    for key, value in kwargs.items():
        if key in ('placed_elements',) and isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)
        elif key in ('survey_answers',) and isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        conn.execute(f'UPDATE sessions SET {key} = ? WHERE id = ?', (value, session_id))
    conn.commit()
    conn.close()


def get_user_sessions(user_id: int) -> list[dict]:
    """获取某个用户的所有 session，按时间倒序"""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d['placed_elements'] = json.loads(d['placed_elements'] or '[]')
        d['survey_answers'] = json.loads(d['survey_answers'] or '{}')
        results.append(d)
    return results


def get_all_sessions() -> list[dict]:
    """获取所有 session（用于导出）"""
    conn = _get_conn()
    rows = conn.execute(
        'SELECT s.*, u.participant_id, u.display_name '
        'FROM sessions s LEFT JOIN users u ON s.user_id = u.id '
        'ORDER BY s.created_at DESC'
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d['placed_elements'] = json.loads(d['placed_elements'] or '[]')
        d['survey_answers'] = json.loads(d['survey_answers'] or '{}')
        results.append(d)
    return results


# ── Interaction Log 操作 ────────────────────────────────

def log_interaction(session_id: str, action: str, data: dict | None = None):
    """记录一条交互日志"""
    conn = _get_conn()
    conn.execute(
        'INSERT INTO interaction_logs (session_id, action, data, timestamp) VALUES (?, ?, ?, ?)',
        (session_id, action, json.dumps(data or {}, ensure_ascii=False), time.time())
    )
    conn.commit()
    conn.close()


def get_interaction_logs(session_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        'SELECT * FROM interaction_logs WHERE session_id = ? ORDER BY timestamp',
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_interaction_log_count(session_id: str) -> int:
    conn = _get_conn()
    row = conn.execute(
        'SELECT COUNT(*) as cnt FROM interaction_logs WHERE session_id = ?',
        (session_id,)
    ).fetchone()
    conn.close()
    return row['cnt'] if row else 0


def _count_action(session_id: str, action: str) -> int:
    """统计某 session 中某类操作的次数"""
    conn = _get_conn()
    row = conn.execute(
        'SELECT COUNT(*) as cnt FROM interaction_logs WHERE session_id = ? AND action = ?',
        (session_id, action)
    ).fetchone()
    conn.close()
    return row['cnt'] if row else 0


# ── 统计与导出 ────────────────────────────────────────

def get_export_summary() -> dict:
    """获取汇总统计"""
    conn = _get_conn()
    total = conn.execute('SELECT COUNT(*) as c FROM sessions').fetchone()['c']
    completed = conn.execute(
        'SELECT COUNT(*) as c FROM sessions WHERE survey_completed_at IS NOT NULL'
    ).fetchone()['c']
    with_upload = conn.execute(
        'SELECT COUNT(*) as c FROM sessions WHERE uploaded_image_path IS NOT NULL'
    ).fetchone()['c']
    with_gen = conn.execute(
        'SELECT COUNT(*) as c FROM sessions WHERE generated_image_path IS NOT NULL'
    ).fetchone()['c']

    modes = {}
    for row in conn.execute(
        "SELECT mode_used, COUNT(*) as c FROM sessions WHERE mode_used != '' GROUP BY mode_used"
    ).fetchall():
        modes[row['mode_used']] = row['c']

    conn.close()
    return {
        'total_sessions': total,
        'completed_surveys': completed,
        'with_uploads': with_upload,
        'with_generated': with_gen,
        'mode_distribution': modes,
    }


def export_csv() -> str:
    """导出 CSV 格式数据"""
    import csv
    import io

    sessions = get_all_sessions()
    columns = [
        'session_id', 'participant_id', 'display_name', 'scene_type', 'mode_used',
        'experiment_condition', 'green_level', 'urban_level', 'vitality_level', 'light_warmth',
        'prs1', 'prs2', 'prs3', 'prs4', 'prs5', 'prs_mean',
        'emo1', 'emo2', 'emo3', 'emo4', 'emo_mean',
        'overall_satisfaction', 'feedback_text',
        'generation_count', 'element_count_final', 'element_delete_count',
        'interaction_log_count',
        'created_at', 'survey_completed_at', 'interaction_duration_seconds',
    ]

    buf = io.StringIO()
    buf.write('\ufeff')  # BOM for Excel
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()

    for s in sessions:
        answers = s.get('survey_answers', {})
        prs_scores = [answers.get(f'prs{i}', 0) for i in range(1, 6)]
        emo_scores = [answers.get(f'emo{i}', 0) for i in range(1, 5)]
        prs_valid = [v for v in prs_scores if v > 0]
        emo_valid = [v for v in emo_scores if v > 0]

        duration = None
        if s.get('survey_completed_at') and s.get('created_at'):
            duration = round(s['survey_completed_at'] - s['created_at'], 1)

        row = {
            'session_id': s['id'],
            'participant_id': s.get('participant_id', ''),
            'display_name': s.get('display_name', ''),
            'scene_type': s.get('scene_type', ''),
            'mode_used': s.get('mode_used', ''),
            'experiment_condition': f"{s.get('scene_type', '')}_{s.get('mode_used', '')}",
            'green_level': s.get('green_level', 50),
            'urban_level': s.get('urban_level', 50),
            'vitality_level': s.get('vitality_level', 50),
            'light_warmth': s.get('light_warmth', 50),
            'overall_satisfaction': answers.get('overall', ''),
            'feedback_text': answers.get('feedback', ''),
            'generation_count': s.get('generation_count', 0),
            'element_count_final': len(s.get('placed_elements', [])),
            'element_delete_count': _count_action(s['id'], 'delete'),
            'interaction_log_count': get_interaction_log_count(s['id']),
            'created_at': s.get('created_at', ''),
            'survey_completed_at': s.get('survey_completed_at', ''),
            'interaction_duration_seconds': duration or '',
        }
        for i in range(1, 6):
            row[f'prs{i}'] = answers.get(f'prs{i}', '')
        row['prs_mean'] = round(sum(prs_valid) / len(prs_valid), 2) if prs_valid else ''
        for i in range(1, 5):
            row[f'emo{i}'] = answers.get(f'emo{i}', '')
        row['emo_mean'] = round(sum(emo_valid) / len(emo_valid), 2) if emo_valid else ''
        writer.writerow(row)

    return buf.getvalue()


def export_json() -> list[dict]:
    """导出 JSON 格式数据"""
    sessions = get_all_sessions()
    results = []
    for s in sessions:
        answers = s.get('survey_answers', {})
        prs_scores = [answers.get(f'prs{i}', 0) for i in range(1, 6)]
        emo_scores = [answers.get(f'emo{i}', 0) for i in range(1, 5)]
        prs_valid = [v for v in prs_scores if v > 0]
        emo_valid = [v for v in emo_scores if v > 0]

        duration = None
        if s.get('survey_completed_at') and s.get('created_at'):
            duration = round(s['survey_completed_at'] - s['created_at'], 1)

        results.append({
            'session_id': s['id'],
            'participant': {
                'participant_id': s.get('participant_id', ''),
                'display_name': s.get('display_name', ''),
            },
            'experiment': {
                'scene_type': s.get('scene_type', ''),
                'mode_used': s.get('mode_used', ''),
                'condition': f"{s.get('scene_type', '')}_{s.get('mode_used', '')}",
            },
            'parameters': {
                'green_level': s.get('green_level', 50),
                'urban_level': s.get('urban_level', 50),
                'vitality_level': s.get('vitality_level', 50),
                'light_warmth': s.get('light_warmth', 50),
            },
            'scores': {
                'prs': dict(zip([f'prs{i}' for i in range(1, 6)], prs_scores)),
                'prs_mean': round(sum(prs_valid) / len(prs_valid), 2) if prs_valid else None,
                'emotion': dict(zip([f'emo{i}' for i in range(1, 5)], emo_scores)),
                'emo_mean': round(sum(emo_valid) / len(emo_valid), 2) if emo_valid else None,
                'overall_satisfaction': answers.get('overall'),
            },
            'feedback': answers.get('feedback', ''),
            'behavior': {
                'generation_count': s.get('generation_count', 0),
                'element_count_final': len(s.get('placed_elements', [])),
                'element_delete_count': _count_action(s['id'], 'delete'),
                'element_place_count': _count_action(s['id'], 'place'),
                'element_move_count': _count_action(s['id'], 'move'),
                'element_scale_count': _count_action(s['id'], 'scale'),
                'interaction_log_count': get_interaction_log_count(s['id']),
            },
            'timestamps': {
                'created_at': s.get('created_at'),
                'survey_completed_at': s.get('survey_completed_at'),
                'interaction_duration_seconds': duration,
            },
        })
    return results
