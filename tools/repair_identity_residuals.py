"""Repair residual downstream identity mismatches after canonical participant repair."""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import _get_conn  # noqa: E402
from app.services.feishu_sync import FeishuClient, SYNC_TARGETS  # noqa: E402


UPDATES: list[tuple[str, str, dict[str, Any]]] = [
    ('session_summary', 'recvmoArUYkQRe', {'参与者编号': '0002', '显示名': 'Arya'}),
    ('drag_element_summary', 'recvlAoOiSMpZ9', {'参与者编号': '0006', '登记姓名': '用户9366'}),
    ('drag_element_summary', 'recvmcF9iXiQoW', {'参与者编号': 'ARCHIVED-UNKNOWN-DRAG-01', '登记姓名': '已归档-未知自由创作-01'}),
    ('drag_element_summary', 'recvmcF9iX8QKS', {'参与者编号': 'ARCHIVED-UNKNOWN-DRAG-02', '登记姓名': '已归档-未知自由创作-02'}),
    ('inspire_element_summary', 'recvlABRo9RsH6', {'参与者编号': '0006', '登记姓名': '用户9366'}),
    ('chat_mode_summary', 'recvmfKYb5WJhU', {'参与者编号': 'ARCHIVED-0123-CHAT-01', '登记姓名': '已归档-123-对话-01'}),
    ('chat_mode_summary', 'recvmfKYb5VHrw', {'参与者编号': 'ARCHIVED-0123-CHAT-02', '登记姓名': '已归档-123-对话-02'}),
    ('chat_mode_summary', 'recvmfKYb54ET7', {'参与者编号': 'ARCHIVED-0123-CHAT-03', '登记姓名': '已归档-123-对话-03'}),
    ('chat_mode_summary', 'recvmfKYb5dZoz', {'参与者编号': 'ARCHIVED-0123-CHAT-04', '登记姓名': '已归档-123-对话-04'}),
    ('chat_mode_summary', 'recvmfKYb5tGVn', {'参与者编号': 'ARCHIVED-0111-CHAT-01', '登记姓名': '已归档-111-对话-01'}),
    ('slider_mode_summary', 'recvmfLfv9gWnO', {'参与者编号': 'ARCHIVED-0111-SLIDER-01', '登记姓名': '已归档-111-智能参数-01'}),
    ('slider_mode_summary', 'recvmfLfv91FvS', {'参与者编号': 'ARCHIVED-0123-SLIDER-01', '登记姓名': '已归档-123-智能参数-01'}),
    ('mode_usage_count', 'recvmq5nC5IVPh', {'参与者编号': '0006', '登记姓名': '用户9366'}),
    ('mode_usage_count', 'recvmq5nC51kdo', {'参与者编号': 'ARCHIVED-P001-USAGE', '登记姓名': '已归档-你好-P001'}),
    ('mode_usage_count', 'recvmq5nC5hcd9', {'参与者编号': 'ARCHIVED-0001-USAGE', '登记姓名': '已归档-1-0001'}),
    ('mode_usage_count', 'recvmq5nC5JXOJ', {'参与者编号': 'ARCHIVED-P002-USAGE', '登记姓名': '已归档-你好-P002'}),
    ('mode_usage_count', 'recvmq5nC5ow0r', {'参与者编号': 'ARCHIVED-0123-USAGE', '登记姓名': '已归档-123-使用次数'}),
    ('mode_usage_count', 'recvmq5nC5zyp8', {'参与者编号': 'ARCHIVED-0111-USAGE', '登记姓名': '已归档-111-使用次数'}),
    ('work_count_summary', 'recvmq5ozImQBG', {'参与者编号': '0006', '登记姓名': '用户9366'}),
    ('work_count_summary', 'recvmq5ozIXab8', {'参与者编号': 'ARCHIVED-P001-WORK', '登记姓名': '已归档-你好-P001'}),
    ('work_count_summary', 'recvmq5ozIxo4x', {'参与者编号': 'ARCHIVED-0001-WORK', '登记姓名': '已归档-1-0001'}),
    ('work_count_summary', 'recvmq5ozI1PqY', {'参与者编号': 'ARCHIVED-P002-WORK', '登记姓名': '已归档-你好-P002'}),
    ('work_count_summary', 'recvmq5ozImPvy', {'参与者编号': 'ARCHIVED-0123-WORK', '登记姓名': '已归档-123-作品数量'}),
    ('work_count_summary', 'recvmq5ozILsN6', {'参与者编号': 'ARCHIVED-0111-WORK', '登记姓名': '已归档-111-作品数量'}),
]


def _table_id(target_key: str) -> str:
    import os

    target = SYNC_TARGETS[target_key]
    table_id = os.getenv(target.env_table_id, '').strip()
    if not table_id:
        raise RuntimeError(f'Missing table id for {target_key}')
    return table_id


def _repair_local_user9366() -> None:
    conn = _get_conn()
    try:
        conn.execute('BEGIN IMMEDIATE')
        conn.execute(
            '''
            UPDATE users
            SET participant_id = '0006',
                gender = CASE WHEN COALESCE(gender, '') = '' THEN '其他/未填写' ELSE gender END
            WHERE id = 6 AND participant_id = 'U93667270'
            '''
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> int:
    client = FeishuClient()
    _repair_local_user9366()
    grouped: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for target_key, record_id, fields in UPDATES:
        grouped[target_key].append((record_id, fields))

    log = []
    for target_key, items in grouped.items():
        table_id = _table_id(target_key)
        records = [{'record_id': record_id, 'fields': fields} for record_id, fields in items]
        log.append(f'{target_key} {table_id} updates={len(records)}')
        # Keep chunks small; Feishu batch update is faster than one request per record.
        for start in range(0, len(records), 50):
            client.batch_update_records(table_id, records[start:start + 50])
            time.sleep(0.5)

    out = ROOT / 'docs' / 'identity_residual_repair_log.txt'
    out.write_text('\n'.join(log) + '\n', encoding='utf-8')
    print(json.dumps(log, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
