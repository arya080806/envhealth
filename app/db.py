"""SQLite 数据库层 - 持久化存储"""
import sqlite3
import json
import time
import os
import hashlib
import secrets
import re
from pathlib import Path

# 100个预生成邀请码
_INVITE_CODES = [
    'HE-10Z3OTJR','HE-11GUW35P','HE-175PZTPI','HE-1IAOPL4F','HE-1RPO5NY7',
    'HE-1U2OABW2','HE-2GN3Y4FM','HE-2H36EKHR','HE-2I9UJ9XJ','HE-36OUI0XS',
    'HE-3OZTNZ9O','HE-3UGU3LFK','HE-42P2A2RP','HE-4E78AW4N','HE-4SQPLGRX',
    'HE-566UTPVG','HE-5JHKXOBQ','HE-5NBMNQ1A','HE-5Z11712N','HE-5Z6B64OV',
    'HE-66GU02HV','HE-66ZOKMCA','HE-6JC2BXOS','HE-7IR53B3Y','HE-7VYHHSMI',
    'HE-83SVLQYB','HE-94C517QY','HE-9P7Q0XJO','HE-AR0T0UNP','HE-B0EHI8SO',
    'HE-B28UA9ZA','HE-BOY8KXA7','HE-BUH6SOUR','HE-BVRYCA1S','HE-CPPXC17G',
    'HE-D4IJBJK0','HE-DDIEGBUL','HE-DVOUMP7A','HE-E713IANN','HE-EH0MCLV0',
    'HE-EMH7Z6GB','HE-EYE0ZM7G','HE-FNWV61XU','HE-FQTPZGXF','HE-FY96UT5R',
    'HE-FZPXY3YC','HE-GRAWZGKK','HE-HJ2JY5HE','HE-HSM1A9V6','HE-HZCRL70L',
    'HE-HZORHQ0H','HE-I9XCRTGN','HE-ISCD89DO','HE-J4H29Z4T','HE-JR3M35TK',
    'HE-LUIIEUSE','HE-MRK7L7EE','HE-N5TRDHEP','HE-N6SS9OJ7','HE-N8AHUT17',
    'HE-N9SQHNAD','HE-O30Q7U1R','HE-ONR2PQ3B','HE-OZGPO4X1','HE-P5QVWSJN',
    'HE-P7OY7457','HE-PP694IMA','HE-Q1UTQEPG','HE-Q1WTHUZQ','HE-Q6Z3A6WV',
    'HE-QLPFKZHP','HE-QQJOH4QL','HE-QR57JCTS','HE-QZSW4BB7','HE-R8RRDTW5',
    'HE-RAJ5VGT3','HE-RDLAAL6T','HE-RDUQYSO6','HE-RNZITTEG','HE-SIYO39MR',
    'HE-TD77HXO9','HE-TDO8XT5L','HE-UI5DKQDQ','HE-UK5F2ATW','HE-UOQ6BXP1',
    'HE-URJIKDOC','HE-UTTL532X','HE-UZ9H4ZSG','HE-V3VEC6TC','HE-V91LKRVZ',
    'HE-VE14IC6K','HE-W2KUKNF5','HE-W4HSK41C','HE-XT4WXF1G','HE-YKQOCJ9E',
    'HE-Z2A1XTGP','HE-Z6NSMCPG','HE-ZTZYHA7Q','HE-ZVHB1UXG','HE-ZYKNET2U',
]

DB_PATH = Path(__file__).parent.parent / 'data' / 'healing.db'
SESSION_COLUMNS = {
    'user_id',
    'scene_type',
    'mode_used',
    'green_level',
    'urban_level',
    'vitality_level',
    'light_warmth',
    'placed_elements',
    'selected_recommend',
    'uploaded_image_path',
    'generated_image_path',
    'survey_answers',
    'survey_completed_at',
    'generation_count',
    'generation_status',
    'generation_error',
    'generation_started_at',
    'generation_finished_at',
    'generation_seen_at',
    'generation_history',
    'chat_moods',
    'chat_extra',
    'llm_prompt',
    'sketch_data',
    'canvas_snapshot_path',
    'canvas_history',
    'canvas_json_path',
    'record_title',
}

HCI_PARTICIPANT_COLUMNS = {
    'user_id',
    'participant_code',
    'registered_name',
    'site_id',
    'study_phase',
    'diagnosis_group',
    'birth_date',
    'gender',
    'education_band',
}


def normalize_hci_participant_code(value: str | int | None) -> str:
    """Return the participant sequence as digits only, preserving leading zeroes."""
    text = str(value or '').strip().upper()
    match = re.fullmatch(r'(?:HCI-)?(\d+)', text)
    if not match:
        return text
    digits = match.group(1)
    return digits.zfill(4) if len(digits) < 4 else digits


def _legacy_hci_participant_code(value: str | int | None) -> str:
    code = normalize_hci_participant_code(value)
    return f'HCI-{code}' if code.isdigit() else ''


def _migrate_hci_participant_codes(conn: sqlite3.Connection) -> None:
    for table, key_col, code_col in [
        ('hci_participants', 'id', 'participant_code'),
        ('users', 'id', 'participant_id'),
    ]:
        try:
            rows = conn.execute(f'SELECT {key_col}, {code_col} FROM {table}').fetchall()
        except Exception:
            continue
        for row in rows:
            old_code = str(row[code_col] or '').strip()
            new_code = normalize_hci_participant_code(old_code)
            if old_code == new_code or not new_code.isdigit():
                continue
            conflict = conn.execute(
                f'SELECT {key_col} FROM {table} WHERE {code_col} = ? AND {key_col} <> ?',
                (new_code, row[key_col]),
            ).fetchone()
            if conflict:
                continue
            conn.execute(
                f'UPDATE {table} SET {code_col} = ? WHERE {key_col} = ?',
                (new_code, row[key_col]),
            )

    for table in [
        'hci_drag_element_summaries',
        'hci_inspire_element_summaries',
        'hci_mode_usage_counts',
        'hci_work_count_summaries',
    ]:
        try:
            rows = conn.execute(f'SELECT rowid AS rid, participant_code FROM {table}').fetchall()
        except Exception:
            continue
        for row in rows:
            old_code = str(row['participant_code'] or '').strip()
            new_code = normalize_hci_participant_code(old_code)
            if old_code != new_code and new_code.isdigit():
                conn.execute(
                    f'UPDATE {table} SET participant_code = ? WHERE rowid = ?',
                    (new_code, row['rid']),
                )

    try:
        rows = conn.execute('SELECT id, sync_type, target_key, payload FROM feishu_sync_jobs').fetchall()
    except Exception:
        return
    for row in rows:
        sync_type = str(row['sync_type'] or '').strip()
        target_key = str(row['target_key'] or '').strip()
        new_target_key = normalize_hci_participant_code(target_key) if sync_type == 'hci_participant' else target_key
        try:
            payload = json.loads(row['payload'] or '{}')
        except Exception:
            payload = {}
        if isinstance(payload, dict):
            for key in ['participant_code', 'participant_id']:
                if key in payload:
                    new_value = normalize_hci_participant_code(payload.get(key))
                    if new_value.isdigit():
                        payload[key] = new_value
        update_target = new_target_key != target_key and new_target_key.isdigit()
        if update_target:
            conflict = conn.execute(
                'SELECT id FROM feishu_sync_jobs WHERE sync_type = ? AND target_key = ? AND id <> ?',
                (sync_type, new_target_key, row['id']),
            ).fetchone()
            update_target = not bool(conflict)
        if update_target:
            conn.execute(
                'UPDATE feishu_sync_jobs SET target_key = ?, payload = ? WHERE id = ?',
                (new_target_key, json.dumps(payload, ensure_ascii=False), row['id']),
            )
        else:
            conn.execute(
                'UPDATE feishu_sync_jobs SET payload = ? WHERE id = ?',
                (json.dumps(payload, ensure_ascii=False), row['id']),
            )


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=30000')
    return conn


PASSWORD_HASH_PREFIX = 'pbkdf2_sha256'
PASSWORD_HASH_ITERATIONS = 260_000


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f'{PASSWORD_HASH_PREFIX}${PASSWORD_HASH_ITERATIONS}${salt}${digest}'


def _legacy_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, stored_hash: str | None) -> bool:
    stored_hash = str(stored_hash or '')
    if stored_hash.startswith(f'{PASSWORD_HASH_PREFIX}$'):
        try:
            _, iterations_text, salt, expected = stored_hash.split('$', 3)
            digest = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                int(iterations_text),
            ).hex()
            return secrets.compare_digest(digest, expected)
        except Exception:
            return False
    return secrets.compare_digest(stored_hash, _legacy_hash_password(password))


def init_db():
    """初始化数据库表结构"""
    conn = _get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL DEFAULT '',
            gender TEXT DEFAULT '',
            phone TEXT UNIQUE,
            password_hash TEXT,
            created_at REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS invite_codes (
            code TEXT PRIMARY KEY,
            used INTEGER DEFAULT 0,
            used_by_phone TEXT,
            used_at REAL
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
            generation_status TEXT DEFAULT '',
            generation_error TEXT DEFAULT '',
            generation_started_at REAL,
            generation_finished_at REAL,
            generation_seen_at REAL DEFAULT 0,
            generation_history TEXT DEFAULT '[]',
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

        CREATE TABLE IF NOT EXISTS hci_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            participant_code TEXT UNIQUE NOT NULL,
            registered_name TEXT DEFAULT '',
            site_id TEXT DEFAULT '',
            study_phase TEXT DEFAULT '',
            diagnosis_group TEXT DEFAULT '',
            birth_date TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            education_band TEXT DEFAULT '',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_hci_participants_user_id
            ON hci_participants(user_id);

        CREATE TABLE IF NOT EXISTS feishu_sync_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_type TEXT NOT NULL,
            target_key TEXT NOT NULL,
            payload TEXT DEFAULT '{}',
            error_message TEXT DEFAULT '',
            attempts INTEGER NOT NULL DEFAULT 0,
            next_retry_at REAL,
            status TEXT NOT NULL DEFAULT 'pending',
            remote_record_id TEXT DEFAULT '',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            UNIQUE(sync_type, target_key)
        );

        CREATE INDEX IF NOT EXISTS idx_feishu_sync_jobs_due
            ON feishu_sync_jobs(status, next_retry_at);

        CREATE TABLE IF NOT EXISTS hci_participant_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_number INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS hci_drag_element_summaries (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            participant_code TEXT DEFAULT '',
            display_name TEXT DEFAULT '',
            scene_type TEXT DEFAULT '',
            plant_element_count INTEGER NOT NULL DEFAULT 0,
            other_element_count INTEGER NOT NULL DEFAULT 0,
            total_custom_element_count INTEGER NOT NULL DEFAULT 0,
            generated_image_path TEXT DEFAULT '',
            updated_at REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS hci_inspire_element_summaries (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            participant_code TEXT DEFAULT '',
            display_name TEXT DEFAULT '',
            scene_type TEXT DEFAULT '',
            stroke_count INTEGER NOT NULL DEFAULT 0,
            auto_plant_count INTEGER NOT NULL DEFAULT 0,
            auto_other_count INTEGER NOT NULL DEFAULT 0,
            auto_total_count INTEGER NOT NULL DEFAULT 0,
            user_custom_label_count INTEGER NOT NULL DEFAULT 0,
            user_custom_plant_count INTEGER NOT NULL DEFAULT 0,
            user_custom_other_count INTEGER NOT NULL DEFAULT 0,
            user_custom_labels TEXT DEFAULT '',
            generated_image_path TEXT DEFAULT '',
            updated_at REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS hci_mode_usage_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            participant_code TEXT DEFAULT '',
            display_name TEXT DEFAULT '',
            mode_used TEXT NOT NULL,
            usage_count INTEGER NOT NULL DEFAULT 0,
            last_session_id TEXT DEFAULT '',
            updated_at REAL NOT NULL,
            UNIQUE(user_id, mode_used)
        );

        CREATE TABLE IF NOT EXISTS hci_work_count_summaries (
            user_id INTEGER PRIMARY KEY,
            participant_code TEXT DEFAULT '',
            display_name TEXT DEFAULT '',
            total_draft_work_count INTEGER NOT NULL DEFAULT 0,
            drag_work_count INTEGER NOT NULL DEFAULT 0,
            drag_revision_generation_count INTEGER NOT NULL DEFAULT 0,
            inspire_work_count INTEGER NOT NULL DEFAULT 0,
            inspire_revision_generation_count INTEGER NOT NULL DEFAULT 0,
            chat_work_count INTEGER NOT NULL DEFAULT 0,
            chat_revision_generation_count INTEGER NOT NULL DEFAULT 0,
            slider_work_count INTEGER NOT NULL DEFAULT 0,
            slider_revision_generation_count INTEGER NOT NULL DEFAULT 0,
            updated_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()

    # 迁移：为已有旧数据库补充新列（users 表）
    for col, defn in [
        ('generation_count', 'INTEGER DEFAULT 0'),
        ('phone', 'TEXT'),
        ('password_hash', 'TEXT'),
        ('gender', "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f'ALTER TABLE users ADD COLUMN {col} {defn}')
            conn.commit()
        except Exception:
            pass

    for col, defn in [
        ('registered_name', "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f'ALTER TABLE hci_participants ADD COLUMN {col} {defn}')
            conn.commit()
        except Exception:
            pass

    # 迁移：sessions 表新增列
    for col, defn in [
        ('chat_moods', "TEXT DEFAULT '[]'"),
        ('chat_extra', "TEXT DEFAULT ''"),
        ('llm_prompt', "TEXT DEFAULT ''"),
        ('sketch_data', "TEXT DEFAULT '{}'"),
        ('canvas_snapshot_path', "TEXT DEFAULT ''"),
        ('canvas_history', "TEXT DEFAULT '[]'"),
        ('canvas_json_path', "TEXT DEFAULT ''"),
        ('record_title', "TEXT DEFAULT ''"),
        ('generation_status', "TEXT DEFAULT ''"),
        ('generation_error', "TEXT DEFAULT ''"),
        ('generation_started_at', 'REAL'),
        ('generation_finished_at', 'REAL'),
        ('generation_seen_at', 'REAL DEFAULT 0'),
        ('generation_history', "TEXT DEFAULT '[]'"),
    ]:
        try:
            conn.execute(f'ALTER TABLE sessions ADD COLUMN {col} {defn}')
            conn.commit()
        except Exception:
            pass

    # 初始化邀请码（已存在的跳过）
    for code in _INVITE_CODES:
        try:
            conn.execute('INSERT OR IGNORE INTO invite_codes (code) VALUES (?)', (code,))
        except Exception:
            pass
    _migrate_hci_participant_codes(conn)
    conn.commit()
    conn.close()


# ── User 操作 ──────────────────────────────────────────

def register_user(phone: str, password: str, invite_code: str, display_name: str = '') -> tuple[dict | None, str]:
    """注册新用户，返回 (user_dict, error_msg)。成功时 error_msg 为空"""
    conn = _get_conn()

    # 验证邀请码
    row = conn.execute('SELECT * FROM invite_codes WHERE code = ?', (invite_code.strip().upper(),)).fetchone()
    if not row:
        conn.close()
        return None, '邀请码无效'
    if row['used']:
        conn.close()
        return None, '邀请码已被使用'

    # 检查手机号是否已注册
    existing = conn.execute('SELECT id FROM users WHERE phone = ?', (phone,)).fetchone()
    if existing:
        conn.close()
        return None, '该手机号已注册'

    # 创建用户
    participant_id = f'U{phone[-4:]}{int(time.time()) % 10000:04d}'
    name = display_name or f'用户{phone[-4:]}'
    password_hash = _hash_password(password)

    conn.execute(
        'INSERT INTO users (participant_id, display_name, phone, password_hash, created_at) VALUES (?, ?, ?, ?, ?)',
        (participant_id, name, phone, password_hash, time.time())
    )
    # 标记邀请码已使用
    conn.execute(
        'UPDATE invite_codes SET used=1, used_by_phone=?, used_at=? WHERE code=?',
        (phone, time.time(), invite_code.strip().upper())
    )
    conn.commit()

    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    return dict(user), ''


def login_user(phone: str, password: str) -> tuple[dict | None, str]:
    """登录，返回 (user_dict, error_msg)"""
    conn = _get_conn()
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    if not user:
        conn.close()
        return None, '手机号未注册'
    if not _verify_password(password, user['password_hash']):
        conn.close()
        return None, '密码错误'
    user_dict = dict(user)
    if not str(user['password_hash'] or '').startswith(f'{PASSWORD_HASH_PREFIX}$'):
        new_hash = _hash_password(password)
        conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user['id']))
        conn.commit()
        user_dict['password_hash'] = new_hash
    conn.close()
    return user_dict, ''


def _clean_registered_name(value: str) -> str:
    text = re.sub(r'[\x00-\x1f\x7f]', '', str(value or '').strip())
    return text[:40]


def _clean_gender(value: str) -> str:
    text = str(value or '').strip()
    return text if text in ('女', '男', '其他/未填写') else '其他/未填写'


def _next_hci_participant_code(conn: sqlite3.Connection) -> str:
    def occupied(code: str) -> bool:
        legacy_code = _legacy_hci_participant_code(code)
        return bool(
            conn.execute(
                'SELECT 1 FROM hci_participants WHERE participant_code IN (?, ?) LIMIT 1',
                (code, legacy_code),
            ).fetchone()
            or conn.execute(
                'SELECT 1 FROM users WHERE participant_id IN (?, ?) LIMIT 1',
                (code, legacy_code),
            ).fetchone()
        )

    row = conn.execute(
        'SELECT next_number FROM hci_participant_sequence WHERE id = 1'
    ).fetchone()
    if not row:
        max_number = 0
        for table, column in [
            ('hci_participants', 'participant_code'),
            ('users', 'participant_id'),
        ]:
            rows = conn.execute(f'SELECT {column} FROM {table}').fetchall()
            for item in rows:
                code = normalize_hci_participant_code(item[column])
                if code.isdigit():
                    max_number = max(max_number, int(code))
        next_number = max_number + 1
        conn.execute(
            'INSERT INTO hci_participant_sequence (id, next_number) VALUES (1, ?)',
            (next_number,),
        )
    else:
        next_number = int(row['next_number'])

    while True:
        participant_code = f'{next_number:04d}'
        if not occupied(participant_code):
            break
        next_number += 1

    conn.execute(
        'UPDATE hci_participant_sequence SET next_number = ? WHERE id = 1',
        (next_number + 1,),
    )
    return participant_code


def _participant_for_user(conn: sqlite3.Connection, user_id: int) -> dict | None:
    row = conn.execute(
        'SELECT * FROM hci_participants WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def research_login_or_register(
    registered_name: str,
    gender: str,
    *,
    force_new: bool = False,
) -> tuple[dict | None, dict | None, bool, str]:
    """Passwordless researcher-mediated login.

    Returns (user, participant, created, error_message).
    """
    name = _clean_registered_name(registered_name)
    gender = _clean_gender(gender)
    if not name:
        return None, None, False, '请填写姓名或研究登记名'

    conn = _get_conn()
    now = time.time()
    sync_payload: tuple[str, dict] | None = None

    try:
        conn.execute('BEGIN IMMEDIATE')

        if not force_new:
            existing = conn.execute(
                '''
                SELECT * FROM users
                WHERE display_name = ? AND COALESCE(gender, '') = ?
                ORDER BY id DESC
                LIMIT 1
                ''',
                (name, gender),
            ).fetchone()
            if existing:
                user = dict(existing)
                participant = _participant_for_user(conn, int(user['id']))
                if not participant:
                    user_code = normalize_hci_participant_code(user.get('participant_id'))
                    participant_code = user_code if user_code.isdigit() else _next_hci_participant_code(conn)
                    conn.execute(
                        '''
                        INSERT INTO hci_participants
                            (user_id, participant_code, registered_name, gender, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                        (user['id'], participant_code, name, gender, now, now),
                    )
                    participant = _participant_for_user(conn, int(user['id']))
                    sync_payload = (participant_code, _participant_sync_payload(participant))
                elif participant.get('registered_name') != name or participant.get('gender') != gender:
                    conn.execute(
                        '''
                        UPDATE hci_participants
                        SET registered_name = ?, gender = ?, updated_at = ?
                        WHERE id = ?
                        ''',
                        (name, gender, now, participant['id']),
                    )
                    participant = _participant_for_user(conn, int(user['id']))
                    sync_payload = (
                        participant['participant_code'],
                        _participant_sync_payload(participant),
                    )
                conn.commit()
                if sync_payload:
                    queue_feishu_sync('hci_participant', sync_payload[0], sync_payload[1])
                return user, participant, False, ''

        participant_code = _next_hci_participant_code(conn)
        conn.execute(
            '''
            INSERT INTO users (participant_id, display_name, gender, created_at)
            VALUES (?, ?, ?, ?)
            ''',
            (participant_code, name, gender, now),
        )
        user_id = conn.execute('SELECT last_insert_rowid() AS id').fetchone()['id']
        conn.execute(
            '''
            INSERT INTO hci_participants
                (user_id, participant_code, registered_name, gender, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (user_id, participant_code, name, gender, now, now),
        )
        user = dict(conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone())
        participant = _participant_for_user(conn, int(user_id))
        conn.commit()
        queue_feishu_sync('hci_participant', participant_code, _participant_sync_payload(participant))
        return user, participant, True, ''
    except sqlite3.IntegrityError:
        conn.rollback()
        return None, None, False, '参与者编号冲突，请重新点击一次'
    except sqlite3.OperationalError as exc:
        conn.rollback()
        if 'locked' in str(exc).lower():
            return None, None, False, '数据库正忙，请稍后重试'
        raise
    finally:
        conn.close()


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


# ---- HCI participant profile operations ----

def _iso_time(ts: float | None) -> str:
    if not ts:
        return ''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(ts)))


def _participant_sync_payload(row: dict) -> dict:
    return {
        'local_id': row.get('id'),
        'user_id': row.get('user_id'),
        'participant_code': normalize_hci_participant_code(row.get('participant_code', '')),
        'registered_name': row.get('registered_name', ''),
        'site_id': row.get('site_id', ''),
        'study_phase': row.get('study_phase', ''),
        'diagnosis_group': row.get('diagnosis_group', ''),
        'birth_date': row.get('birth_date', ''),
        'gender': row.get('gender', ''),
        'education_band': row.get('education_band', ''),
        'created_at': _iso_time(row.get('created_at')),
        'updated_at': _iso_time(row.get('updated_at')),
    }


def get_hci_participant_by_user_id(user_id: int | None) -> dict | None:
    if not user_id:
        return None
    conn = _get_conn()
    row = conn.execute(
        'SELECT * FROM hci_participants WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_hci_participant_by_code(participant_code: str) -> dict | None:
    participant_code = normalize_hci_participant_code(participant_code)
    conn = _get_conn()
    row = conn.execute(
        'SELECT * FROM hci_participants WHERE participant_code IN (?, ?)',
        (participant_code, _legacy_hci_participant_code(participant_code)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_hci_participant(**kwargs) -> dict:
    participant_code = normalize_hci_participant_code(kwargs.get('participant_code'))
    if not participant_code:
        raise ValueError('participant_code is required')
    if not participant_code.isdigit():
        raise ValueError('参与者编号只能包含数字')

    values = {
        'user_id': kwargs.get('user_id'),
        'participant_code': participant_code,
        'registered_name': str(kwargs.get('registered_name') or '').strip(),
        'site_id': str(kwargs.get('site_id') or '').strip(),
        'study_phase': str(kwargs.get('study_phase') or '').strip(),
        'diagnosis_group': str(kwargs.get('diagnosis_group') or '').strip(),
        'birth_date': str(kwargs.get('birth_date') or '').strip(),
        'gender': str(kwargs.get('gender') or '').strip(),
        'education_band': str(kwargs.get('education_band') or '').strip(),
    }

    conn = _get_conn()
    now = time.time()
    row = conn.execute(
        'SELECT id, created_at FROM hci_participants WHERE participant_code IN (?, ?)',
        (participant_code, _legacy_hci_participant_code(participant_code)),
    ).fetchone()
    if row:
        conn.execute(
            '''
            UPDATE hci_participants
            SET user_id = ?, participant_code = ?,
                registered_name = COALESCE(NULLIF(?, ''), registered_name),
                site_id = ?, study_phase = ?, diagnosis_group = ?,
                birth_date = ?, gender = ?, education_band = ?, updated_at = ?
            WHERE id = ?
            ''',
            (
                values['user_id'], participant_code, values['registered_name'], values['site_id'], values['study_phase'],
                values['diagnosis_group'], values['birth_date'], values['gender'],
                values['education_band'], now, row['id'],
            ),
        )
    else:
        conn.execute(
            '''
            INSERT INTO hci_participants
                (user_id, participant_code, registered_name, site_id, study_phase, diagnosis_group,
                 birth_date, gender, education_band, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                values['user_id'], values['participant_code'], values['registered_name'], values['site_id'],
                values['study_phase'], values['diagnosis_group'], values['birth_date'],
                values['gender'], values['education_band'], now, now,
            ),
        )
    conn.commit()
    saved = conn.execute(
        'SELECT * FROM hci_participants WHERE participant_code = ?',
        (participant_code,),
    ).fetchone()
    result = dict(saved)
    conn.close()
    queue_feishu_sync('hci_participant', participant_code, _participant_sync_payload(result))
    return result


# ---- Feishu sync queue operations ----

def queue_feishu_sync(sync_type: str, target_key: str, payload: dict) -> dict:
    sync_type = str(sync_type or '').strip()
    target_key = str(target_key or '').strip()
    payload = dict(payload or {})
    for key in ['participant_code', 'participant_id']:
        if key in payload:
            code = normalize_hci_participant_code(payload.get(key))
            if code.isdigit():
                payload[key] = code
    if sync_type == 'hci_participant':
        target_key = normalize_hci_participant_code(target_key)
    if not sync_type or not target_key:
        raise ValueError('sync_type and target_key are required')

    now = time.time()
    payload_text = json.dumps(payload or {}, ensure_ascii=False)
    conn = _get_conn()
    existing = conn.execute(
        'SELECT id, remote_record_id FROM feishu_sync_jobs WHERE sync_type = ? AND target_key = ?',
        (sync_type, target_key),
    ).fetchone()
    if existing:
        conn.execute(
            '''
            UPDATE feishu_sync_jobs
            SET payload = ?, error_message = '', status = 'pending',
                attempts = 0, next_retry_at = NULL, updated_at = ?
            WHERE id = ?
            ''',
            (payload_text, now, existing['id']),
        )
        job_id = existing['id']
    else:
        cur = conn.execute(
            '''
            INSERT INTO feishu_sync_jobs
                (sync_type, target_key, payload, attempts, status, created_at, updated_at)
            VALUES (?, ?, ?, 0, 'pending', ?, ?)
            ''',
            (sync_type, target_key, payload_text, now, now),
        )
        job_id = cur.lastrowid
    conn.commit()
    row = conn.execute('SELECT * FROM feishu_sync_jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    return dict(row)


def get_feishu_sync_job(job_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute('SELECT * FROM feishu_sync_jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_due_feishu_sync_jobs(limit: int = 20) -> list[dict]:
    now = time.time()
    conn = _get_conn()
    rows = conn.execute(
        '''
        SELECT * FROM feishu_sync_jobs
        WHERE status IN ('pending', 'failed')
          AND (next_retry_at IS NULL OR next_retry_at <= ?)
        ORDER BY updated_at ASC
        LIMIT ?
        ''',
        (now, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_feishu_sync_success(job_id: int, remote_record_id: str = ''):
    now = time.time()
    conn = _get_conn()
    conn.execute(
        '''
        UPDATE feishu_sync_jobs
        SET status = 'success', error_message = '', next_retry_at = NULL,
            remote_record_id = COALESCE(NULLIF(?, ''), remote_record_id),
            updated_at = ?
        WHERE id = ?
        ''',
        (remote_record_id or '', now, job_id),
    )
    conn.commit()
    conn.close()


def mark_feishu_sync_failed(job_id: int, error_message: str):
    now = time.time()
    conn = _get_conn()
    row = conn.execute(
        'SELECT attempts FROM feishu_sync_jobs WHERE id = ?',
        (job_id,),
    ).fetchone()
    attempts = int(row['attempts'] if row else 0) + 1
    delay = min(3600, 60 * (2 ** min(attempts - 1, 5)))
    conn.execute(
        '''
        UPDATE feishu_sync_jobs
        SET status = 'failed', attempts = ?, error_message = ?,
            next_retry_at = ?, updated_at = ?
        WHERE id = ?
        ''',
        (attempts, str(error_message or '')[:2000], now + delay, now, job_id),
    )
    conn.commit()
    conn.close()


def get_feishu_sync_summary() -> dict:
    conn = _get_conn()
    rows = conn.execute(
        'SELECT status, COUNT(*) AS count FROM feishu_sync_jobs GROUP BY status'
    ).fetchall()
    latest_failures = conn.execute(
        '''
        SELECT sync_type, target_key, error_message, attempts, next_retry_at
        FROM feishu_sync_jobs
        WHERE status = 'failed'
        ORDER BY updated_at DESC
        LIMIT 10
        '''
    ).fetchall()
    conn.close()
    return {
        'counts': {row['status']: row['count'] for row in rows},
        'latest_failures': [dict(row) for row in latest_failures],
    }


def _json_loads_safe(value, fallback):
    try:
        return json.loads(value or '')
    except Exception:
        return fallback


def _session_summary_payload(session_id: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        '''
        SELECT s.*, u.participant_id, u.display_name
        FROM sessions s LEFT JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
        ''',
        (session_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None

    data = dict(row)
    placed_elements = _json_loads_safe(data.get('placed_elements'), [])
    survey_answers = _json_loads_safe(data.get('survey_answers'), {})
    sketch_data = _json_loads_safe(data.get('sketch_data'), {})
    return {
        'session_id': data.get('id', ''),
        'user_id': data.get('user_id'),
        'participant_id': normalize_hci_participant_code(data.get('participant_id', '')),
        'display_name': data.get('display_name', ''),
        'scene_type': data.get('scene_type', ''),
        'mode_used': data.get('mode_used', ''),
        'green_level': data.get('green_level'),
        'urban_level': data.get('urban_level'),
        'vitality_level': data.get('vitality_level'),
        'light_warmth': data.get('light_warmth'),
        'generation_count': data.get('generation_count', 0),
        'element_count_final': len(placed_elements) if isinstance(placed_elements, list) else 0,
        'survey_completed': bool(data.get('survey_completed_at')),
        'overall_satisfaction': survey_answers.get('overall', '') if isinstance(survey_answers, dict) else '',
        'feedback_text': survey_answers.get('feedback', '') if isinstance(survey_answers, dict) else '',
        'sketch_stroke_count': sketch_data.get('strokeCount', '') if isinstance(sketch_data, dict) else '',
        'uploaded_image_path': data.get('uploaded_image_path', ''),
        'generated_image_path': data.get('generated_image_path', ''),
        'created_at': _iso_time(data.get('created_at')),
        'survey_completed_at': _iso_time(data.get('survey_completed_at')),
    }


def queue_session_summary_sync(session_id: str):
    payload = _session_summary_payload(session_id)
    if payload:
        queue_feishu_sync('session_summary', session_id, payload)


PLANT_KEYWORDS = (
    '树', '草', '花', '竹', '灌木', '植被', '绿化', '藤', '叶', '苔',
    '芦苇', '棕榈', '仙人掌', '荷花', '水草', '花坛', '花圃', '树冠',
    '树干', '树丛', '蘑菇', '野草',
)


def _element_group(name: str = '', category: str = '') -> str:
    category = str(category or '').strip()
    name = str(name or '').strip()
    if category in ('植被', '植物'):
        return 'plant'
    if any(keyword in name for keyword in PLANT_KEYWORDS):
        return 'plant'
    return 'other'


def _session_context(session_id: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        '''
        SELECT s.*, u.participant_id, u.display_name, hp.participant_code
        FROM sessions s
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN hci_participants hp ON hp.user_id = u.id
        WHERE s.id = ?
        ORDER BY hp.updated_at DESC
        LIMIT 1
        ''',
        (session_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _drag_element_summary_payload(session_id: str) -> dict | None:
    data = _session_context(session_id)
    if not data or data.get('mode_used') != 'drag':
        return None
    elements = _json_loads_safe(data.get('placed_elements'), [])
    if not isinstance(elements, list):
        elements = []

    plant_count = 0
    other_count = 0
    for item in elements:
        if not isinstance(item, dict):
            continue
        group = _element_group(item.get('name') or item.get('elemName'), item.get('category') or item.get('cat'))
        if group == 'plant':
            plant_count += 1
        else:
            other_count += 1

    return {
        'session_id': data.get('id', ''),
        'user_id': data.get('user_id'),
        'participant_code': normalize_hci_participant_code(
            data.get('participant_code') or data.get('participant_id') or ''
        ),
        'display_name': data.get('display_name', ''),
        'scene_type': data.get('scene_type', ''),
        'plant_element_count': plant_count,
        'other_element_count': other_count,
        'total_custom_element_count': plant_count + other_count,
        'generated_image_path': data.get('generated_image_path', ''),
        'updated_at': _iso_time(time.time()),
    }


def queue_drag_element_summary_sync(session_id: str):
    payload = _drag_element_summary_payload(session_id)
    if not payload:
        return
    now = time.time()
    conn = _get_conn()
    conn.execute(
        '''
        INSERT INTO hci_drag_element_summaries
            (session_id, user_id, participant_code, display_name, scene_type,
             plant_element_count, other_element_count, total_custom_element_count,
             generated_image_path, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            user_id = excluded.user_id,
            participant_code = excluded.participant_code,
            display_name = excluded.display_name,
            scene_type = excluded.scene_type,
            plant_element_count = excluded.plant_element_count,
            other_element_count = excluded.other_element_count,
            total_custom_element_count = excluded.total_custom_element_count,
            generated_image_path = excluded.generated_image_path,
            updated_at = excluded.updated_at
        ''',
        (
            payload['session_id'], payload['user_id'], payload['participant_code'],
            payload['display_name'], payload['scene_type'], payload['plant_element_count'],
            payload['other_element_count'], payload['total_custom_element_count'],
            payload['generated_image_path'], now,
        ),
    )
    conn.commit()
    conn.close()
    queue_feishu_sync('drag_element_summary', payload['session_id'], payload)


def _inspire_element_summary_payload(session_id: str) -> dict | None:
    data = _session_context(session_id)
    if not data or data.get('mode_used') != 'inspire':
        return None
    sketch_data = _json_loads_safe(data.get('sketch_data'), {})
    if not isinstance(sketch_data, dict):
        return None

    stroke_log = sketch_data.get('strokeLog') if isinstance(sketch_data.get('strokeLog'), list) else []
    user_annotations = (
        sketch_data.get('userAnnotations')
        if isinstance(sketch_data.get('userAnnotations'), list)
        else []
    )
    auto_plant = 0
    auto_other = 0
    for item in stroke_log:
        if not isinstance(item, dict):
            continue
        label = item.get('autoLabel') or ''
        if not label:
            continue
        if _element_group(label) == 'plant':
            auto_plant += 1
        else:
            auto_other += 1

    custom_labels: list[str] = []
    user_plant = 0
    user_other = 0
    for item in user_annotations:
        if not isinstance(item, dict):
            continue
        label = str(item.get('userLabel') or '').strip()
        if not label:
            continue
        group = _element_group(label)
        custom_labels.append(f'{label}:{"植物" if group == "plant" else "其他"}')
        if group == 'plant':
            user_plant += 1
        else:
            user_other += 1

    return {
        'session_id': data.get('id', ''),
        'user_id': data.get('user_id'),
        'participant_code': normalize_hci_participant_code(
            data.get('participant_code') or data.get('participant_id') or ''
        ),
        'display_name': data.get('display_name', ''),
        'scene_type': data.get('scene_type', ''),
        'stroke_count': int(sketch_data.get('strokeCount') or len(stroke_log) or 0),
        'auto_plant_count': auto_plant,
        'auto_other_count': auto_other,
        'auto_total_count': auto_plant + auto_other,
        'user_custom_label_count': len(custom_labels),
        'user_custom_plant_count': user_plant,
        'user_custom_other_count': user_other,
        'user_custom_labels': '; '.join(custom_labels)[:1000],
        'generated_image_path': data.get('generated_image_path', ''),
        'updated_at': _iso_time(time.time()),
    }


def queue_inspire_element_summary_sync(session_id: str):
    payload = _inspire_element_summary_payload(session_id)
    if not payload:
        return
    now = time.time()
    conn = _get_conn()
    conn.execute(
        '''
        INSERT INTO hci_inspire_element_summaries
            (session_id, user_id, participant_code, display_name, scene_type,
             stroke_count, auto_plant_count, auto_other_count, auto_total_count,
             user_custom_label_count, user_custom_plant_count, user_custom_other_count,
             user_custom_labels, generated_image_path, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            user_id = excluded.user_id,
            participant_code = excluded.participant_code,
            display_name = excluded.display_name,
            scene_type = excluded.scene_type,
            stroke_count = excluded.stroke_count,
            auto_plant_count = excluded.auto_plant_count,
            auto_other_count = excluded.auto_other_count,
            auto_total_count = excluded.auto_total_count,
            user_custom_label_count = excluded.user_custom_label_count,
            user_custom_plant_count = excluded.user_custom_plant_count,
            user_custom_other_count = excluded.user_custom_other_count,
            user_custom_labels = excluded.user_custom_labels,
            generated_image_path = excluded.generated_image_path,
            updated_at = excluded.updated_at
        ''',
        (
            payload['session_id'], payload['user_id'], payload['participant_code'],
            payload['display_name'], payload['scene_type'], payload['stroke_count'],
            payload['auto_plant_count'], payload['auto_other_count'], payload['auto_total_count'],
            payload['user_custom_label_count'], payload['user_custom_plant_count'],
            payload['user_custom_other_count'], payload['user_custom_labels'],
            payload['generated_image_path'], now,
        ),
    )
    conn.commit()
    conn.close()
    queue_feishu_sync('inspire_element_summary', payload['session_id'], payload)


def queue_mode_usage_sync_for_session(session_id: str):
    data = _session_context(session_id)
    if not data or not data.get('user_id') or not data.get('mode_used'):
        return
    user_id = int(data['user_id'])
    mode_used = str(data.get('mode_used') or '').strip()
    if not mode_used:
        return

    conn = _get_conn()
    count_row = conn.execute(
        '''
        SELECT COUNT(*) AS c
        FROM sessions
        WHERE user_id = ? AND mode_used = ?
        ''',
        (user_id, mode_used),
    ).fetchone()
    last_row = conn.execute(
        '''
        SELECT id
        FROM sessions
        WHERE user_id = ? AND mode_used = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''',
        (user_id, mode_used),
    ).fetchone()
    now = time.time()
    payload = {
        'usage_key': f'{user_id}:{mode_used}',
        'user_id': user_id,
        'participant_code': normalize_hci_participant_code(
            data.get('participant_code') or data.get('participant_id') or ''
        ),
        'display_name': data.get('display_name', ''),
        'mode_used': mode_used,
        'usage_count': int(count_row['c'] if count_row else 0),
        'last_session_id': last_row['id'] if last_row else session_id,
        'updated_at': _iso_time(now),
    }
    conn.execute(
        '''
        INSERT INTO hci_mode_usage_counts
            (user_id, participant_code, display_name, mode_used, usage_count, last_session_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, mode_used) DO UPDATE SET
            participant_code = excluded.participant_code,
            display_name = excluded.display_name,
            usage_count = excluded.usage_count,
            last_session_id = excluded.last_session_id,
            updated_at = excluded.updated_at
        ''',
        (
            user_id, payload['participant_code'], payload['display_name'], mode_used,
            payload['usage_count'], payload['last_session_id'], now,
        ),
    )
    conn.commit()
    conn.close()
    queue_feishu_sync('mode_usage_count', payload['usage_key'], payload)


WORK_SUMMARY_MODES = ('drag', 'inspire', 'chat', 'slider')


def _row_get(row: sqlite3.Row | dict, key: str, default=None):
    if isinstance(row, sqlite3.Row):
        return row[key] if key in row.keys() else default
    return row.get(key, default)


def _countable_work_session(row: sqlite3.Row | dict) -> bool:
    mode_used = str(_row_get(row, 'mode_used') or '').strip()
    if mode_used not in WORK_SUMMARY_MODES:
        return False
    if _row_get(row, 'generated_image_path'):
        return True
    if _row_get(row, 'canvas_snapshot_path'):
        return True
    if _row_get(row, 'canvas_json_path'):
        return True
    try:
        generation_count = int(_row_get(row, 'generation_count') or 0)
    except (TypeError, ValueError):
        generation_count = 0
    if generation_count > 0:
        return True
    status = str(_row_get(row, 'generation_status') or '')
    return status in ('queued', 'running', 'error', 'done')


def _revision_generation_count_for_session(row: sqlite3.Row | dict) -> int:
    try:
        generation_count = int(_row_get(row, 'generation_count') or 0)
    except (TypeError, ValueError):
        generation_count = 0
    raw_canvas_history = _row_get(row, 'canvas_history')
    canvas_history = _json_loads_safe(raw_canvas_history, [])
    canvas_save_count = len(canvas_history) if isinstance(canvas_history, list) else 0
    # A generation in drag/inspire may save a canvas snapshot for reproducibility.
    # max() avoids double-counting that snapshot as both a save and a generation.
    return max(generation_count, canvas_save_count)


def _work_count_summary_payload(user_id: int) -> dict | None:
    if not user_id:
        return None
    conn = _get_conn()
    participant = conn.execute(
        '''
        SELECT hp.participant_code, COALESCE(NULLIF(hp.registered_name, ''), u.display_name) AS display_name
        FROM users u
        LEFT JOIN hci_participants hp ON hp.user_id = u.id
        WHERE u.id = ?
        ORDER BY hp.updated_at DESC
        LIMIT 1
        ''',
        (user_id,),
    ).fetchone()
    rows = conn.execute(
        '''
        SELECT id, mode_used, generated_image_path, canvas_snapshot_path, canvas_json_path,
               generation_count, generation_status, canvas_history
        FROM sessions
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchall()
    conn.close()

    if not participant:
        return None

    counts = {
        'total_draft_work_count': 0,
        'drag_work_count': 0,
        'drag_revision_generation_count': 0,
        'inspire_work_count': 0,
        'inspire_revision_generation_count': 0,
        'chat_work_count': 0,
        'chat_revision_generation_count': 0,
        'slider_work_count': 0,
        'slider_revision_generation_count': 0,
    }
    for row in rows:
        if not _countable_work_session(row):
            continue
        mode = str(row['mode_used'] or '').strip()
        if mode not in WORK_SUMMARY_MODES:
            continue
        counts['total_draft_work_count'] += 1
        counts[f'{mode}_work_count'] += 1
        counts[f'{mode}_revision_generation_count'] += _revision_generation_count_for_session(row)

    now = time.time()
    return {
        'summary_key': str(user_id),
        'user_id': user_id,
        'participant_code': normalize_hci_participant_code(participant['participant_code'] or ''),
        'display_name': participant['display_name'] or '',
        **counts,
        'updated_at': _iso_time(now),
        '_updated_at_ts': now,
    }


def queue_work_count_summary_sync_for_user(user_id: int | None):
    if not user_id:
        return
    payload = _work_count_summary_payload(int(user_id))
    if not payload:
        return
    now = float(payload.pop('_updated_at_ts', time.time()))
    conn = _get_conn()
    conn.execute(
        '''
        INSERT INTO hci_work_count_summaries
            (user_id, participant_code, display_name, total_draft_work_count,
             drag_work_count, drag_revision_generation_count,
             inspire_work_count, inspire_revision_generation_count,
             chat_work_count, chat_revision_generation_count,
             slider_work_count, slider_revision_generation_count, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            participant_code = excluded.participant_code,
            display_name = excluded.display_name,
            total_draft_work_count = excluded.total_draft_work_count,
            drag_work_count = excluded.drag_work_count,
            drag_revision_generation_count = excluded.drag_revision_generation_count,
            inspire_work_count = excluded.inspire_work_count,
            inspire_revision_generation_count = excluded.inspire_revision_generation_count,
            chat_work_count = excluded.chat_work_count,
            chat_revision_generation_count = excluded.chat_revision_generation_count,
            slider_work_count = excluded.slider_work_count,
            slider_revision_generation_count = excluded.slider_revision_generation_count,
            updated_at = excluded.updated_at
        ''',
        (
            payload['user_id'], payload['participant_code'], payload['display_name'],
            payload['total_draft_work_count'], payload['drag_work_count'],
            payload['drag_revision_generation_count'], payload['inspire_work_count'],
            payload['inspire_revision_generation_count'], payload['chat_work_count'],
            payload['chat_revision_generation_count'], payload['slider_work_count'],
            payload['slider_revision_generation_count'], now,
        ),
    )
    conn.commit()
    conn.close()
    queue_feishu_sync('work_count_summary', payload['summary_key'], payload)


def queue_work_count_summary_sync_for_session(session_id: str):
    data = _session_context(session_id)
    if data and data.get('user_id'):
        queue_work_count_summary_sync_for_user(int(data['user_id']))


def queue_hci_core_summaries(session_id: str):
    queue_mode_usage_sync_for_session(session_id)
    queue_drag_element_summary_sync(session_id)
    queue_inspire_element_summary_sync(session_id)
    queue_work_count_summary_sync_for_session(session_id)


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
    result = dict(row)
    queue_session_summary_sync(session_id)
    return result


def get_session(session_id: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute('SELECT * FROM sessions WHERE id = ?', (session_id,)).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['placed_elements'] = json.loads(result.get('placed_elements') or '[]')
        result['chat_moods'] = json.loads(result.get('chat_moods') or '[]')
        result['survey_answers'] = json.loads(result.get('survey_answers') or '{}')
        result['sketch_data'] = json.loads(result.get('sketch_data') or '{}')
        result['generation_history'] = json.loads(result.get('generation_history') or '[]')
        result['canvas_history'] = json.loads(result.get('canvas_history') or '[]')
        return result
    return None


def update_session(session_id: str, **kwargs):
    """更新 session 的任意字段"""
    conn = _get_conn()
    for key, value in kwargs.items():
        if key not in SESSION_COLUMNS:
            conn.close()
            raise ValueError(f'unsupported session field: {key}')
        if key in ('placed_elements', 'chat_moods', 'generation_history', 'canvas_history') and isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)
        elif key in ('survey_answers',) and isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        elif key == 'sketch_data' and isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        conn.execute(f'UPDATE sessions SET {key} = ? WHERE id = ?', (value, session_id))
    conn.commit()
    conn.close()
    queue_session_summary_sync(session_id)
    queue_hci_core_summaries(session_id)


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
        d['placed_elements'] = json.loads(d.get('placed_elements') or '[]')
        d['chat_moods'] = json.loads(d.get('chat_moods') or '[]')
        d['survey_answers'] = json.loads(d.get('survey_answers') or '{}')
        d['sketch_data'] = json.loads(d.get('sketch_data') or '{}')
        d['generation_history'] = json.loads(d.get('generation_history') or '[]')
        d['canvas_history'] = json.loads(d.get('canvas_history') or '[]')
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
        d['placed_elements'] = json.loads(d.get('placed_elements') or '[]')
        d['chat_moods'] = json.loads(d.get('chat_moods') or '[]')
        d['survey_answers'] = json.loads(d.get('survey_answers') or '{}')
        d['sketch_data'] = json.loads(d.get('sketch_data') or '{}')
        d['generation_history'] = json.loads(d.get('generation_history') or '[]')
        d['canvas_history'] = json.loads(d.get('canvas_history') or '[]')
        results.append(d)
    return results


# ── Interaction Log 操作 ────────────────────────────────

def delete_session(session_id: str):
    """删除一条 session 及其交互日志"""
    conn = _get_conn()
    row = conn.execute('SELECT user_id FROM sessions WHERE id = ?', (session_id,)).fetchone()
    user_id = int(row['user_id']) if row and row['user_id'] else None
    conn.execute('DELETE FROM interaction_logs WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM hci_drag_element_summaries WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM hci_inspire_element_summaries WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    queue_work_count_summary_sync_for_user(user_id)


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
        'interaction_log_count', 'sketch_stroke_count', 'sketch_auto_recognized_count',
        'sketch_user_annotation_count', 'sketch_correction_count', 'sketch_round',
        'creative_lens', 'ai_agency', 'scene_intent_mood', 'scene_intent_complexity',
        'chat_moods', 'chat_extra', 'canvas_snapshot_path', 'canvas_json_path', 'llm_prompt',
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

        sketch = s.get('sketch_data') or {}
        scene_intent = sketch.get('sceneIntent') or {}
        hci_metrics = sketch.get('hciMetrics') or {}

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
            'sketch_stroke_count': sketch.get('strokeCount', ''),
            'sketch_auto_recognized_count': hci_metrics.get('autoRecognizedCount', ''),
            'sketch_user_annotation_count': hci_metrics.get('userAnnotationCount', ''),
            'sketch_correction_count': hci_metrics.get('correctionCount', ''),
            'sketch_round': sketch.get('interactionRound', ''),
            'creative_lens': hci_metrics.get('creativeLens') or scene_intent.get('creativeLens', ''),
            'ai_agency': hci_metrics.get('aiAgency') or scene_intent.get('aiAgency', ''),
            'scene_intent_mood': scene_intent.get('dominantMood', ''),
            'scene_intent_complexity': scene_intent.get('complexityLevel', ''),
            'chat_moods': json.dumps(s.get('chat_moods', []), ensure_ascii=False),
            'chat_extra': s.get('chat_extra', ''),
            'canvas_snapshot_path': s.get('canvas_snapshot_path', ''),
            'canvas_json_path': s.get('canvas_json_path', ''),
            'llm_prompt': s.get('llm_prompt', ''),
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

        sketch = s.get('sketch_data') or {}
        scene_intent = sketch.get('sceneIntent') or {}
        hci_metrics = sketch.get('hciMetrics') or {}
        interaction_logs = get_interaction_logs(s['id'])

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
                'inspire_stroke_count': sketch.get('strokeCount'),
                'inspire_auto_recognized_count': hci_metrics.get('autoRecognizedCount'),
                'inspire_user_annotation_count': hci_metrics.get('userAnnotationCount'),
                'inspire_correction_count': hci_metrics.get('correctionCount'),
            },
            'creative_process': {
                'creative_lens': hci_metrics.get('creativeLens') or scene_intent.get('creativeLens'),
                'ai_agency': hci_metrics.get('aiAgency') or scene_intent.get('aiAgency'),
                'interaction_round': sketch.get('interactionRound'),
                'scene_intent': scene_intent,
                'chat_moods': s.get('chat_moods', []),
                'chat_extra': s.get('chat_extra', ''),
                'stroke_log': sketch.get('strokeLog', []),
                'user_annotations': sketch.get('userAnnotations', []),
                'hci_metrics': hci_metrics,
                'llm_prompt': s.get('llm_prompt', ''),
                'canvas_snapshot_path': s.get('canvas_snapshot_path', ''),
                'canvas_json_path': s.get('canvas_json_path', ''),
                'interaction_logs': interaction_logs,
            },
            'timestamps': {
                'created_at': s.get('created_at'),
                'survey_completed_at': s.get('survey_completed_at'),
                'interaction_duration_seconds': duration,
            },
        })
    return results
