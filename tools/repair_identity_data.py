"""Repair known participant identity conflicts.

Default mode is dry-run. Pass --apply to write local SQLite and Feishu changes.
The repair follows docs/20260614_identity_audit_and_repair_plan.md.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import DB_PATH, _get_conn, normalize_hci_participant_code  # noqa: E402
from app.services.feishu_sync import FeishuClient, SYNC_TARGETS  # noqa: E402


F = {
    'code': '参与者编号',
    'name': '登记姓名',
    'gender': '性别',
    'user_id': '本地用户ID',
    'local_id': '本地参与者ID',
    'remark': '备注',
    'site': '中心编号',
    'study_phase': '研究阶段',
    'diagnosis_group': '诊断大类',
    'age_band': '年龄段',
    'birth_date': '出生日期',
    'education_band': '教育层级',
}


CANONICAL_IMPORTS = [
    {
        'participant_code': '0127',
        'registered_name': '20260612-1',
        'gender': '女',
        'remote_record_id': 'recvmj3AZ8ZEJx',
        'site_id': '浦江',
        'study_phase': '未填写',
        'diagnosis_group': '其他/未填写',
        'age_band': '50~59',
        'education_band': '本科',
    },
    {
        'participant_code': '0128',
        'registered_name': '20260612-2',
        'gender': '女',
        'remote_record_id': 'recvmkN4nwjW3a',
        'study_phase': '未填写',
        'diagnosis_group': '其他/未填写',
        'age_band': '60~69',
        'education_band': '未填写',
    },
]


ARCHIVE_PARTICIPANTS = [
    {
        'record_id': 'recvmf6LSaWLvN',
        'archive_code': 'ARCHIVED-0124',
        'archive_name': '已归档-Arya-0124',
        'gender': '女',
        'reason': '重复 Arya；canonical=0002',
    },
    {
        'record_id': 'recvmj3rIxfuJV',
        'archive_code': 'ARCHIVED-0126',
        'archive_name': '已归档-Arya-0126',
        'gender': '女',
        'reason': '重复 Arya；canonical=0002',
    },
    {
        'record_id': 'recvmj3nFumCPD',
        'archive_code': 'ARCHIVED-0125',
        'archive_name': '已归档-20260612-1-0125',
        'gender': '女',
        'reason': '重复 20260612-1；canonical=0127',
    },
    {
        'record_id': 'recvmk08Cu5qXs',
        'archive_code': 'ARCHIVED-BLANK-20260612-2',
        'archive_name': '已归档-20260612-2-空记录',
        'gender': '其他/未填写',
        'reason': '无编号空记录；备注已合并到 canonical=0128',
    },
    {
        'record_id': 'recvmfsOrLYTEZ',
        'archive_code': 'ARCHIVED-0004-DUP',
        'archive_name': '已归档-Codex虚拟测试06112308-重复',
        'gender': '其他/未填写',
        'reason': '重复 record；canonical=0004',
    },
    {
        'record_id': 'recvmiTqwXi9bN',
        'archive_code': 'ARCHIVED-0005-DUP',
        'archive_name': '已归档-ipad-debug-1781238168711-重复',
        'gender': '其他/未填写',
        'reason': '重复 record；canonical=0005',
    },
    {
        'record_id': 'recvmf8K3z7cjc',
        'archive_code': 'ARCHIVED-BLANK-01',
        'archive_name': '已归档-空记录-01',
        'gender': '其他/未填写',
        'reason': '空身份记录',
    },
    {
        'record_id': 'recvmfv25NSWmK',
        'archive_code': 'ARCHIVED-BLANK-02',
        'archive_name': '已归档-空记录-02',
        'gender': '其他/未填写',
        'reason': '空身份记录',
    },
    {
        'record_id': 'recvmk0o8WAoGf',
        'archive_code': 'ARCHIVED-BLANK-03',
        'archive_name': '已归档-空记录-03',
        'gender': '其他/未填写',
        'reason': '空身份记录',
    },
]


CANONICAL_PARTICIPANT_UPDATES = [
    {
        'record_id': 'recvmj3AZ8ZEJx',
        'participant_code': '0127',
        'registered_name': '20260612-1',
        'gender': '女',
        'remark': '0612 女 看起来五六十岁 更喜欢清静 刚刚好',
    },
    {
        'record_id': 'recvmkN4nwjW3a',
        'participant_code': '0128',
        'registered_name': '20260612-2',
        'gender': '女',
        'remark': '三处花朵；0612 女 白头发 70 及以上 喜欢热闹 桌椅 树木 花朵 与个人经历相关（父亲 花园工作）',
    },
]


CODE_REPLACEMENTS = {
    '0124': {'code': '0002', 'name': 'Arya'},
    '0126': {'code': '0002', 'name': 'Arya'},
    '0125': {'code': '0127', 'name': '20260612-1'},
}


def _now() -> float:
    return time.time()


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _field_text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _record_fields(client: FeishuClient, table_id: str, record_id: str) -> dict[str, Any]:
    data = client.get(
        f'/bitable/v1/apps/{client.app_token}/tables/{table_id}/records/{record_id}'
    )
    record = data.get('record') or data
    return dict(record.get('fields') or {})


def _append_remark(existing: str, addition: str) -> str:
    existing = _field_text(existing)
    if not existing:
        return addition
    if addition in existing:
        return existing
    return f'{existing}\n{addition}'


def _backup_db(log: list[str]) -> Path:
    backup_path = DB_PATH.with_name(f'{DB_PATH.stem}.identity_repair_{_timestamp()}{DB_PATH.suffix}')
    shutil.copy2(DB_PATH, backup_path)
    log.append(f'Backed up SQLite to {backup_path}')
    return backup_path


def _import_local_participants(apply: bool, log: list[str]) -> dict[str, dict[str, int]]:
    imported: dict[str, dict[str, int]] = {}
    conn = _get_conn()
    now = _now()
    try:
        conn.execute('BEGIN IMMEDIATE')
        for item in CANONICAL_IMPORTS:
            code = normalize_hci_participant_code(item['participant_code'])
            name = item['registered_name']
            gender = item['gender']
            existing_code = conn.execute(
                '''
                SELECT u.id AS user_id, hp.id AS participant_id
                FROM users u
                LEFT JOIN hci_participants hp ON hp.user_id = u.id
                WHERE u.participant_id = ?
                   OR hp.participant_code = ?
                LIMIT 1
                ''',
                (code, code),
            ).fetchone()
            existing_name = conn.execute(
                '''
                SELECT u.id, u.participant_id
                FROM users u
                WHERE u.display_name = ? AND COALESCE(u.gender, '') = ?
                LIMIT 1
                ''',
                (name, gender),
            ).fetchone()
            if existing_code:
                imported[code] = {
                    'user_id': int(existing_code['user_id']),
                    'participant_id': int(existing_code['participant_id'] or 0),
                }
                log.append(f'Local participant {code} already exists; skipped insert.')
                continue
            if existing_name:
                raise RuntimeError(
                    f'Cannot import {code}: local name/gender already exists as '
                    f'{existing_name["participant_id"]}'
                )
            log.append(f'Import local participant {code} {name} {gender}')
            if not apply:
                continue
            conn.execute(
                '''
                INSERT INTO users (participant_id, display_name, gender, created_at)
                VALUES (?, ?, ?, ?)
                ''',
                (code, name, gender, now),
            )
            user_id = int(conn.execute('SELECT last_insert_rowid() AS id').fetchone()['id'])
            conn.execute(
                '''
                INSERT INTO hci_participants
                    (user_id, participant_code, registered_name, site_id, study_phase,
                     diagnosis_group, age_band, birth_date, gender, education_band,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    user_id,
                    code,
                    name,
                    item.get('site_id', ''),
                    item.get('study_phase', ''),
                    item.get('diagnosis_group', ''),
                    item.get('age_band', ''),
                    item.get('birth_date', ''),
                    gender,
                    item.get('education_band', ''),
                    now,
                    now,
                ),
            )
            participant_id = int(conn.execute('SELECT last_insert_rowid() AS id').fetchone()['id'])
            imported[code] = {'user_id': user_id, 'participant_id': participant_id}
        max_code = max(int(item['participant_code']) for item in CANONICAL_IMPORTS) + 1
        current = conn.execute(
            'SELECT next_number FROM hci_participant_sequence WHERE id = 1'
        ).fetchone()
        next_number = max(int(current['next_number']) if current else 1, max_code)
        log.append(f'Ensure local participant sequence next_number >= {next_number}')
        if apply:
            conn.execute(
                '''
                INSERT INTO hci_participant_sequence (id, next_number)
                VALUES (1, ?)
                ON CONFLICT(id) DO UPDATE SET next_number = excluded.next_number
                ''',
                (next_number,),
            )
            conn.commit()
        else:
            conn.rollback()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return imported


def _update_feishu_record(
    client: FeishuClient,
    table_id: str,
    record_id: str,
    fields: dict[str, Any],
    apply: bool,
    log: list[str],
) -> None:
    log.append(f'Update Feishu {table_id}/{record_id}: {json.dumps(fields, ensure_ascii=False)}')
    if apply:
        client.update_record(table_id, record_id, fields)


def _repair_participant_table(
    client: FeishuClient,
    imported: dict[str, dict[str, int]],
    apply: bool,
    log: list[str],
) -> None:
    table_id = os_table_id('hci_participant')
    stamp = datetime.now().strftime('%Y-%m-%d')
    for item in CANONICAL_PARTICIPANT_UPDATES:
        existing = _record_fields(client, table_id, item['record_id']) if apply else {}
        remark = item.get('remark', '')
        if apply:
            remark = _append_remark(
                _field_text(existing.get(F['remark'])),
                f'[identity repair {stamp}] {remark}',
            )
        fields = {
            F['code']: item['participant_code'],
            F['name']: item['registered_name'],
            F['gender']: item['gender'],
            F['remark']: remark or f'[identity repair {stamp}] canonical record',
        }
        local_ids = imported.get(item['participant_code'])
        if local_ids:
            fields[F['user_id']] = local_ids['user_id']
            fields[F['local_id']] = local_ids['participant_id']
        _update_feishu_record(client, table_id, item['record_id'], fields, apply, log)

    for item in ARCHIVE_PARTICIPANTS:
        existing = _record_fields(client, table_id, item['record_id']) if apply else {}
        addition = f'[identity repair {stamp}] 已归档：{item["reason"]}'
        fields = {
            F['code']: item['archive_code'],
            F['name']: item['archive_name'],
            F['gender']: item['gender'],
            F['user_id']: None,
            F['local_id']: None,
            F['remark']: _append_remark(_field_text(existing.get(F['remark'])), addition)
            if apply
            else addition,
        }
        _update_feishu_record(client, table_id, item['record_id'], fields, apply, log)


def os_table_id(target_key: str) -> str:
    target = SYNC_TARGETS[target_key]
    table_id = __import__('os').getenv(target.env_table_id, '').strip()
    if not table_id:
        raise RuntimeError(f'Missing table id for {target_key}: {target.env_table_id}')
    return table_id


def _fetch_records(client: FeishuClient, table_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    page_token = ''
    while True:
        data = client.get(
            f'/bitable/v1/apps/{client.app_token}/tables/{table_id}/records',
            query={'page_size': 500, 'page_token': page_token},
        )
        records.extend(data.get('items') or [])
        if not data.get('has_more') or not data.get('page_token'):
            break
        page_token = data.get('page_token')
    return records


def _repair_downstream_tables(
    client: FeishuClient,
    apply: bool,
    log: list[str],
) -> None:
    for key, target in SYNC_TARGETS.items():
        if key == 'hci_participant':
            continue
        try:
            table_id = os_table_id(key)
            records = _fetch_records(client, table_id)
        except Exception as exc:
            log.append(f'Skip downstream {key}: {exc}')
            continue
        code_field = target.field_map.get('participant_code')
        name_field = target.field_map.get('display_name') or target.field_map.get('registered_name')
        if not code_field:
            continue
        for record in records:
            fields = record.get('fields') or {}
            old_code = normalize_hci_participant_code(fields.get(code_field))
            replacement = CODE_REPLACEMENTS.get(old_code)
            if not replacement:
                continue
            update_fields = {
                code_field: replacement['code'],
            }
            if name_field:
                update_fields[name_field] = replacement['name']
            _update_feishu_record(
                client,
                table_id,
                str(record.get('record_id') or ''),
                update_fields,
                apply,
                log,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Write changes. Default is dry-run.')
    parser.add_argument('--log-out', type=Path, default=ROOT / 'docs' / 'identity_repair_log_latest.txt')
    args = parser.parse_args()

    log: list[str] = [
        f'Identity repair started at {datetime.now().isoformat(timespec="seconds")}',
        f'Mode: {"APPLY" if args.apply else "DRY-RUN"}',
    ]
    if args.apply:
        _backup_db(log)
    else:
        log.append('Dry-run: SQLite backup will be created only with --apply.')

    imported = _import_local_participants(args.apply, log)
    client = FeishuClient()
    _repair_participant_table(client, imported, args.apply, log)
    _repair_downstream_tables(client, args.apply, log)

    args.log_out.parent.mkdir(parents=True, exist_ok=True)
    args.log_out.write_text('\n'.join(log) + '\n', encoding='utf-8')
    print('\n'.join(log))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
