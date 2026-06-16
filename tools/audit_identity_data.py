"""Read-only audit for local and Feishu participant identity data.

This script does not mutate SQLite or Feishu. It compares the local source
tables with the Feishu mirror and highlights duplicate participants, missing
identity fields, and downstream records that inherit conflicting codes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import DB_PATH, _get_conn, normalize_hci_participant_code  # noqa: E402
from app.services.feishu_sync import FeishuClient, SYNC_TARGETS, feishu_enabled  # noqa: E402


def _now_iso() -> str:
    return datetime.now().isoformat(timespec='seconds')


def _text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(int(value)) if float(value).is_integer() else str(value)
    if isinstance(value, list):
        return ''.join(_text(item) for item in value).strip()
    if isinstance(value, dict):
        for key in ('text', 'name', 'value'):
            if value.get(key) not in (None, ''):
                return _text(value.get(key))
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _name_key(name: str) -> str:
    return ' '.join(_text(name).lower().split())


def _code(value: Any) -> str:
    return normalize_hci_participant_code(_text(value))


def _dedupe_groups(rows: list[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = tuple(_text(row.get(k)) for k in keys)
        if any(key):
            buckets[key].append(row)
    groups = []
    for key, items in sorted(buckets.items()):
        if len(items) > 1:
            groups.append({'key': dict(zip(keys, key)), 'items': items})
    return groups


def _is_archived_identity(row: dict[str, Any]) -> bool:
    code = _text(row.get('participant_code'))
    name = _text(
        row.get('registered_name')
        or row.get('display_name')
        or row.get('name')
    )
    return code.startswith('ARCHIVED-') or name.startswith('已归档')


def _query_all(conn, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def audit_local(target_names: list[str]) -> dict[str, Any]:
    conn = _get_conn()
    users = _query_all(
        conn,
        '''
        SELECT id, participant_id, display_name, gender, created_at
        FROM users
        ORDER BY id
        ''',
    )
    participants = _query_all(
        conn,
        '''
        SELECT id, user_id, participant_code, registered_name, gender,
               created_at, updated_at
        FROM hci_participants
        ORDER BY id
        ''',
    )
    joined = _query_all(
        conn,
        '''
        SELECT u.id AS user_id, u.participant_id, u.display_name,
               COALESCE(u.gender, '') AS user_gender,
               u.created_at AS user_created_at,
               hp.id AS participant_row_id, hp.participant_code,
               hp.registered_name, COALESCE(hp.gender, '') AS participant_gender
        FROM users u
        LEFT JOIN hci_participants hp ON hp.user_id = u.id
        ORDER BY u.id, hp.id
        ''',
    )
    sessions = _query_all(
        conn,
        '''
        SELECT s.id AS session_id, s.user_id, s.mode_used, s.created_at,
               u.participant_id, u.display_name,
               hp.participant_code, hp.registered_name
        FROM sessions s
        LEFT JOIN users u ON u.id = s.user_id
        LEFT JOIN hci_participants hp ON hp.user_id = u.id
        ORDER BY s.created_at
        ''',
    )
    sequence = _query_all(conn, 'SELECT * FROM hci_participant_sequence ORDER BY id')
    conn.close()

    normalized_users = [
        {
            **row,
            'participant_id_normalized': _code(row.get('participant_id')),
            'display_name_key': _name_key(row.get('display_name')),
        }
        for row in users
    ]
    normalized_participants = [
        {
            **row,
            'participant_code_normalized': _code(row.get('participant_code')),
            'registered_name_key': _name_key(row.get('registered_name')),
        }
        for row in participants
    ]

    mismatched_user_participant = []
    missing_participant_rows = []
    legacy_missing_participant_rows = []
    for row in joined:
        if not row.get('participant_row_id'):
            if not _text(row.get('user_gender')):
                legacy_missing_participant_rows.append(row)
            else:
                missing_participant_rows.append(row)
            continue
        user_code = _code(row.get('participant_id'))
        participant_code = _code(row.get('participant_code'))
        if user_code and participant_code and user_code != participant_code:
            mismatched_user_participant.append(row)

    target_keys = {_name_key(name) for name in target_names if name}
    target_users = [row for row in normalized_users if row['display_name_key'] in target_keys]
    target_participants = [
        row for row in normalized_participants if row['registered_name_key'] in target_keys
    ]
    target_sessions = [
        row for row in sessions
        if _name_key(row.get('display_name')) in target_keys
        or _name_key(row.get('registered_name')) in target_keys
    ]

    return {
        'db_path': str(DB_PATH),
        'counts': {
            'users': len(users),
            'hci_participants': len(participants),
            'sessions': len(sessions),
        },
        'sequence': sequence,
        'target_users': target_users,
        'target_participants': target_participants,
        'target_sessions': target_sessions,
        'duplicates': {
            'users_by_name_gender': _dedupe_groups(
                normalized_users,
                'display_name_key',
                'gender',
            ),
            'users_by_participant_id': _dedupe_groups(
                normalized_users,
                'participant_id_normalized',
            ),
            'participants_by_name_gender': _dedupe_groups(
                normalized_participants,
                'registered_name_key',
                'gender',
            ),
            'participants_by_code': _dedupe_groups(
                normalized_participants,
                'participant_code_normalized',
            ),
        },
        'integrity_issues': {
            'mismatched_user_participant': mismatched_user_participant,
            'users_without_hci_participant': missing_participant_rows,
            'legacy_users_without_hci_participant': legacy_missing_participant_rows,
        },
    }


def _fetch_feishu_records(client: FeishuClient, table_id: str) -> list[dict[str, Any]]:
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


def _fetch_feishu_fields(client: FeishuClient, table_id: str) -> list[str]:
    fields: list[str] = []
    page_token = ''
    while True:
        data = client.get(
            f'/bitable/v1/apps/{client.app_token}/tables/{table_id}/fields',
            query={'page_size': 100, 'page_token': page_token},
        )
        fields.extend(str(item.get('field_name') or '') for item in data.get('items', []))
        if not data.get('has_more') or not data.get('page_token'):
            break
        page_token = data.get('page_token')
    return fields


def _remote_table_id(target_key: str) -> str:
    target = SYNC_TARGETS[target_key]
    return os.getenv(target.env_table_id, '').strip()


def audit_feishu(target_names: list[str]) -> dict[str, Any]:
    if not feishu_enabled():
        return {'enabled': False, 'error': 'Feishu environment variables are incomplete.'}

    client = FeishuClient()
    participant_target = SYNC_TARGETS['hci_participant']
    participant_table_id = _remote_table_id('hci_participant')
    if not participant_table_id:
        return {'enabled': True, 'error': 'Participant table id is not configured.'}

    participant_fields = _fetch_feishu_fields(client, participant_table_id)
    participant_records = _fetch_feishu_records(client, participant_table_id)
    participant_field_map = participant_target.field_map

    def participant_item(record: dict[str, Any]) -> dict[str, Any]:
        fields = record.get('fields') or {}
        return {
            'record_id': record.get('record_id', ''),
            'participant_code': _code(fields.get(participant_field_map['participant_code'])),
            'registered_name': _text(fields.get(participant_field_map['registered_name'])),
            'registered_name_key': _name_key(fields.get(participant_field_map['registered_name'])),
            'gender': _text(fields.get(participant_field_map['gender'])),
            'user_id': _text(fields.get(participant_field_map['user_id'])),
            'local_id': _text(fields.get(participant_field_map['local_id'])),
            'updated_at': fields.get(participant_field_map['updated_at']),
            'raw_fields': fields,
        }

    participant_items = [participant_item(record) for record in participant_records]
    participant_codes = {
        row['participant_code'] for row in participant_items if row.get('participant_code')
    }
    participant_names_by_code: dict[str, set[str]] = defaultdict(set)
    for row in participant_items:
        if row.get('participant_code') and row.get('registered_name_key'):
            participant_names_by_code[row['participant_code']].add(row['registered_name_key'])

    target_keys = {_name_key(name) for name in target_names if name}
    target_participants = [
        row for row in participant_items if row.get('registered_name_key') in target_keys
    ]
    active_participant_items = [
        row for row in participant_items if not _is_archived_identity(row)
    ]
    missing_identity = [
        row for row in participant_items
        if not _is_archived_identity(row)
        if not row.get('participant_code')
        or not row.get('registered_name')
        or not row.get('gender')
    ]

    expected_participant_fields = list(participant_target.field_map.values())
    participant_report = {
        'table_id': participant_table_id,
        'field_count': len(participant_fields),
        'record_count': len(participant_items),
        'unexpected_fields': [
            field for field in participant_fields if field not in expected_participant_fields
        ],
        'missing_expected_fields': [
            field for field in expected_participant_fields if field not in participant_fields
        ],
        'target_participants': target_participants,
        'duplicates': {
            'by_name': _dedupe_groups(active_participant_items, 'registered_name_key'),
            'by_name_gender': _dedupe_groups(
                active_participant_items,
                'registered_name_key',
                'gender',
            ),
            'by_code': _dedupe_groups(active_participant_items, 'participant_code'),
            'by_local_user_id': _dedupe_groups(active_participant_items, 'user_id'),
            'by_local_participant_id': _dedupe_groups(active_participant_items, 'local_id'),
        },
        'missing_identity_fields': missing_identity,
    }

    downstream: dict[str, Any] = {}
    for key, target in SYNC_TARGETS.items():
        if key == 'hci_participant':
            continue
        table_id = _remote_table_id(key)
        if not table_id:
            downstream[key] = {'configured': False}
            continue

        try:
            fields = _fetch_feishu_fields(client, table_id)
            records = _fetch_feishu_records(client, table_id)
        except Exception as exc:
            downstream[key] = {
                'configured': True,
                'table_id': table_id,
                'error': str(exc),
            }
            continue
        field_map = target.field_map
        code_field = field_map.get('participant_code')
        name_field = field_map.get('display_name') or field_map.get('registered_name')
        unique_field = target.unique_feishu_field
        items = []
        for record in records:
            raw_fields = record.get('fields') or {}
            code = _code(raw_fields.get(code_field)) if code_field else ''
            name = _text(raw_fields.get(name_field)) if name_field else ''
            item = {
                'record_id': record.get('record_id', ''),
                'unique_value': _text(raw_fields.get(unique_field)),
                'participant_code': code,
                'display_name': name,
                'display_name_key': _name_key(name),
            }
            items.append(item)

        code_mismatches = []
        for item in items:
            if _is_archived_identity(item):
                continue
            code = item.get('participant_code')
            name_key = item.get('display_name_key')
            if not code:
                code_mismatches.append({**item, 'issue': 'missing_participant_code'})
            elif code not in participant_codes:
                code_mismatches.append({**item, 'issue': 'code_not_in_participant_table'})
            elif name_key and name_key not in participant_names_by_code.get(code, set()):
                code_mismatches.append({**item, 'issue': 'code_name_mismatch'})

        downstream[key] = {
            'configured': True,
            'table_id': table_id,
            'field_count': len(fields),
            'record_count': len(items),
            'unexpected_fields': [
                field for field in fields if field not in list(target.field_map.values())
            ],
            'missing_expected_fields': [
                field for field in target.field_map.values() if field not in fields
            ],
            'duplicate_unique_values': _dedupe_groups(items, 'unique_value'),
            'identity_mismatches': code_mismatches,
            'target_records': [
                item for item in items if item.get('display_name_key') in target_keys
            ],
        }

    return {
        'enabled': True,
        'app_token': client.app_token,
        'participants': participant_report,
        'downstream': downstream,
    }


def _count_issue_items(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return sum(_count_issue_items(item) for item in value.values())
    return 0


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        '# Identity Audit Report',
        '',
        f'- Generated at: `{report["generated_at"]}`',
        f'- Local DB: `{report["local"]["db_path"]}`',
        f'- Feishu enabled: `{report["feishu"].get("enabled")}`',
        '',
        '## Local Summary',
        '',
        f'- Users: `{report["local"]["counts"]["users"]}`',
        f'- HCI participants: `{report["local"]["counts"]["hci_participants"]}`',
        f'- Sessions: `{report["local"]["counts"]["sessions"]}`',
        f'- Duplicate user name+gender groups: '
        f'`{len(report["local"]["duplicates"]["users_by_name_gender"])}`',
        f'- Duplicate participant name+gender groups: '
        f'`{len(report["local"]["duplicates"]["participants_by_name_gender"])}`',
        f'- Mismatched user/participant codes: '
        f'`{len(report["local"]["integrity_issues"]["mismatched_user_participant"])}`',
        f'- Users without HCI participant row: '
        f'`{len(report["local"]["integrity_issues"]["users_without_hci_participant"])}`',
        f'- Legacy non-HCI users without participant row: '
        f'`{len(report["local"]["integrity_issues"]["legacy_users_without_hci_participant"])}`',
        '',
        '### Local Target Participants',
        '',
        '```json',
        json.dumps(report['local']['target_participants'], ensure_ascii=False, indent=2),
        '```',
        '',
        '## Feishu Summary',
        '',
    ]
    feishu = report['feishu']
    if not feishu.get('enabled') or feishu.get('error'):
        lines.extend([f'- Feishu audit skipped/error: `{feishu.get("error", "")}`', ''])
        return '\n'.join(lines)

    participants = feishu['participants']
    lines.extend([
        f'- Participant table: `{participants["table_id"]}`',
        f'- Participant records: `{participants["record_count"]}`',
        f'- Duplicate name groups: `{len(participants["duplicates"]["by_name"])}`',
        f'- Duplicate name+gender groups: `{len(participants["duplicates"]["by_name_gender"])}`',
        f'- Duplicate code groups: `{len(participants["duplicates"]["by_code"])}`',
        f'- Missing identity rows: `{len(participants["missing_identity_fields"])}`',
        '',
        '### Feishu Target Participants',
        '',
        '```json',
        json.dumps(participants['target_participants'], ensure_ascii=False, indent=2),
        '```',
        '',
        '### Feishu Duplicate Name+Gender',
        '',
        '```json',
        json.dumps(participants['duplicates']['by_name_gender'], ensure_ascii=False, indent=2),
        '```',
        '',
        '### Feishu Missing Identity Fields',
        '',
        '```json',
        json.dumps(participants['missing_identity_fields'], ensure_ascii=False, indent=2),
        '```',
        '',
        '## Downstream Tables',
        '',
    ])
    for key, table in feishu['downstream'].items():
        if not table.get('configured'):
            lines.append(f'- `{key}`: not configured')
            continue
        if table.get('error'):
            lines.extend([
                f'### `{key}`',
                '',
                f'- Table: `{table["table_id"]}`',
                f'- Error: `{table["error"]}`',
                '',
            ])
            continue
        lines.extend([
            f'### `{key}`',
            '',
            f'- Table: `{table["table_id"]}`',
            f'- Records: `{table["record_count"]}`',
            f'- Duplicate unique values: `{len(table["duplicate_unique_values"])}`',
            f'- Identity mismatches: `{len(table["identity_mismatches"])}`',
            f'- Target records: `{len(table["target_records"])}`',
            '',
        ])
        if table['target_records'] or table['identity_mismatches']:
            lines.extend([
                '```json',
                json.dumps(
                    {
                        'target_records': table['target_records'],
                        'identity_mismatches': table['identity_mismatches'][:50],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                '```',
                '',
            ])
    lines.extend([
        '## Machine Summary',
        '',
        f'- Total local duplicate groups: `{_count_issue_items(report["local"]["duplicates"])}`',
        f'- Total Feishu participant duplicate groups: '
        f'`{_count_issue_items(participants["duplicates"])}`',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--target',
        action='append',
        default=['Arya', '20260612-1', '20260612-2'],
        help='Participant name to highlight. Can be passed multiple times.',
    )
    parser.add_argument('--no-feishu', action='store_true', help='Skip Feishu API audit.')
    parser.add_argument('--json-out', type=Path, help='Write full audit JSON to this path.')
    parser.add_argument('--md-out', type=Path, help='Write Markdown summary to this path.')
    args = parser.parse_args()

    report = {
        'generated_at': _now_iso(),
        'targets': args.target,
        'local': audit_local(args.target),
        'feishu': {'enabled': False, 'skipped': True}
        if args.no_feishu
        else audit_feishu(args.target),
    }
    markdown = render_markdown(report)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(markdown, encoding='utf-8')

    print(markdown)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
