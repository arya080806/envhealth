"""Feishu Bitable sync service.

Local SQLite remains the source of truth. Feishu is treated as an
operational mirror, so sync errors are captured in the local retry queue.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

from app.db import (
    get_due_feishu_sync_jobs,
    mark_feishu_sync_failed,
    mark_feishu_sync_success,
)

logger = logging.getLogger(__name__)

FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'
TEXT_FIELD_TYPE = 1
NUMBER_FIELD_TYPE = 2
SINGLE_SELECT_FIELD_TYPE = 3
DATE_FIELD_TYPE = 5
_ENV_LOADED = False


class FeishuSyncError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncTarget:
    sync_type: str
    env_table_id: str
    table_name: str
    unique_payload_key: str
    unique_feishu_field: str
    field_map: dict[str, str]
    field_types: dict[str, int]


@dataclass(frozen=True)
class PreparedSyncJob:
    job_id: int
    sync_type: str
    table_id: str
    fields: dict[str, Any]
    unique_field: str
    unique_value: str
    known_record_id: str
    legacy_unique_values: list[str]


SYNC_TARGETS: dict[str, SyncTarget] = {
    'hci_participant': SyncTarget(
        sync_type='hci_participant',
        env_table_id='FEISHU_BITABLE_PARTICIPANTS_TABLE_ID',
        table_name='hci_participants',
        unique_payload_key='participant_code',
        unique_feishu_field='参与者编号',
        field_map={
            'participant_code': '参与者编号',
            'registered_name': '登记姓名',
            'site_id': '中心编号',
            'study_phase': '研究阶段',
            'diagnosis_group': '诊断大类',
            'age_band': '年龄段',
            'birth_date': '出生日期',
            'gender': '性别',
            'education_band': '教育层级',
            'user_id': '本地用户ID',
            'local_id': '本地参与者ID',
            'created_at': '创建时间',
            'updated_at': '更新时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '本地参与者ID': NUMBER_FIELD_TYPE,
            '年龄段': SINGLE_SELECT_FIELD_TYPE,
            '出生日期': DATE_FIELD_TYPE,
            '创建时间': DATE_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'session_summary': SyncTarget(
        sync_type='session_summary',
        env_table_id='FEISHU_BITABLE_SESSIONS_TABLE_ID',
        table_name='session_summaries',
        unique_payload_key='session_id',
        unique_feishu_field='会话ID',
        field_map={
            'session_id': '会话ID',
            'user_id': '本地用户ID',
            'participant_code': '参与者编号',
            'display_name': '显示名',
            'scene_type': '场景类型',
            'mode_used': '使用模式',
            'green_level': '绿化强度',
            'urban_level': '城市化强度',
            'vitality_level': '活力强度',
            'light_warmth': '光照温暖度',
            'generation_count': '生成次数',
            'element_count_final': '最终元素数',
            'survey_completed': '是否完成问卷',
            'overall_satisfaction': '总体满意度',
            'feedback_text': '反馈文本',
            'sketch_stroke_count': '草图笔画数',
            'uploaded_image_path': '上传图片路径',
            'generated_image_path': '生成图片路径',
            'created_at': '创建时间',
            'survey_completed_at': '问卷完成时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '绿化强度': NUMBER_FIELD_TYPE,
            '城市化强度': NUMBER_FIELD_TYPE,
            '活力强度': NUMBER_FIELD_TYPE,
            '光照温暖度': NUMBER_FIELD_TYPE,
            '生成次数': NUMBER_FIELD_TYPE,
            '最终元素数': NUMBER_FIELD_TYPE,
            '总体满意度': NUMBER_FIELD_TYPE,
            '草图笔画数': NUMBER_FIELD_TYPE,
            '创建时间': DATE_FIELD_TYPE,
            '问卷完成时间': DATE_FIELD_TYPE,
        },
    ),
    'drag_element_summary': SyncTarget(
        sync_type='drag_element_summary',
        env_table_id='FEISHU_BITABLE_DRAG_ELEMENTS_TABLE_ID',
        table_name='drag_element_summaries',
        unique_payload_key='session_id',
        unique_feishu_field='会话ID',
        field_map={
            'session_id': '会话ID',
            'user_id': '本地用户ID',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'scene_type': '场景类型',
            'uploaded_image_path': '原图路径',
            'plant_element_count': '植物类摆放数',
            'other_element_count': '其他元素摆放数',
            'total_custom_element_count': '自定义元素总数',
            'canvas_snapshot_path': '元素布局图片路径',
            'canvas_json_path': '画布JSON路径',
            'placed_elements_json': '元素摆放明细JSON',
            'generated_image_path': '生成图片路径',
            'updated_at': '更新时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '植物类摆放数': NUMBER_FIELD_TYPE,
            '其他元素摆放数': NUMBER_FIELD_TYPE,
            '自定义元素总数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'inspire_element_summary': SyncTarget(
        sync_type='inspire_element_summary',
        env_table_id='FEISHU_BITABLE_INSPIRE_ELEMENTS_TABLE_ID',
        table_name='inspire_element_summaries',
        unique_payload_key='session_id',
        unique_feishu_field='会话ID',
        field_map={
            'session_id': '会话ID',
            'user_id': '本地用户ID',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'scene_type': '场景类型',
            'uploaded_image_path': '原图路径',
            'stroke_count': '总笔画数',
            'auto_plant_count': '自动识别植物类数',
            'auto_other_count': '自动识别其他类数',
            'auto_total_count': '自动识别总数',
            'user_custom_label_count': '用户自定义类别数',
            'user_custom_plant_count': '用户自定义植物类数',
            'user_custom_other_count': '用户自定义其他类数',
            'user_custom_labels': '用户自定义类别明细',
            'canvas_snapshot_path': '创作画布图片路径',
            'canvas_json_path': '画布JSON路径',
            'sketch_data_json': '创作画布明细JSON',
            'generated_image_path': '生成图片路径',
            'updated_at': '更新时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '总笔画数': NUMBER_FIELD_TYPE,
            '自动识别植物类数': NUMBER_FIELD_TYPE,
            '自动识别其他类数': NUMBER_FIELD_TYPE,
            '自动识别总数': NUMBER_FIELD_TYPE,
            '用户自定义类别数': NUMBER_FIELD_TYPE,
            '用户自定义植物类数': NUMBER_FIELD_TYPE,
            '用户自定义其他类数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'chat_mode_summary': SyncTarget(
        sync_type='chat_mode_summary',
        env_table_id='FEISHU_BITABLE_CHAT_SUMMARY_TABLE_ID',
        table_name='chat_mode_summaries',
        unique_payload_key='session_id',
        unique_feishu_field='会话ID',
        field_map={
            'session_id': '会话ID',
            'user_id': '本地用户ID',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'scene_type': '场景类型',
            'mood_tag_count': '情绪标签数',
            'mood_tags': '情绪标签明细',
            'user_prompt': '用户提示词',
            'feeling_text': '输入你的感受',
            'extra_text_length': '补充描述字数',
            'has_extra_text': '是否填写补充描述',
            'chat_green_level': '最终绿化程度',
            'chat_urban_level': '最终城市化程度',
            'chat_vitality_level': '最终活力程度',
            'chat_light_warmth': '最终光照温暖度',
            'generation_count': '生成次数',
            'generation_status': '生成状态',
            'generation_error': 'AI错误摘要',
            'llm_prompt': 'AI提示词',
            'uploaded_image_path': '原图路径',
            'generated_image_path': '生成图片路径',
            'updated_at': '更新时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '情绪标签数': NUMBER_FIELD_TYPE,
            '补充描述字数': NUMBER_FIELD_TYPE,
            '最终绿化程度': NUMBER_FIELD_TYPE,
            '最终城市化程度': NUMBER_FIELD_TYPE,
            '最终活力程度': NUMBER_FIELD_TYPE,
            '最终光照温暖度': NUMBER_FIELD_TYPE,
            '生成次数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'slider_mode_summary': SyncTarget(
        sync_type='slider_mode_summary',
        env_table_id='FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID',
        table_name='slider_mode_summaries',
        unique_payload_key='session_id',
        unique_feishu_field='会话ID',
        field_map={
            'session_id': '会话ID',
            'user_id': '本地用户ID',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'scene_type': '场景类型',
            'selected_recommend': '预设名称',
            'uploaded_image_path': '原图路径',
            'green_level': '绿化程度',
            'urban_level': '城市化程度',
            'vitality_level': '活力程度',
            'light_warmth': '光照温暖度',
            'generation_count': '生成次数',
            'generation_status': '生成状态',
            'generation_error': 'AI错误摘要',
            'generated_image_path': '生成图片路径',
            'updated_at': '更新时间',
        },
        field_types={
            '本地用户ID': NUMBER_FIELD_TYPE,
            '绿化程度': NUMBER_FIELD_TYPE,
            '城市化程度': NUMBER_FIELD_TYPE,
            '活力程度': NUMBER_FIELD_TYPE,
            '光照温暖度': NUMBER_FIELD_TYPE,
            '生成次数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'mode_usage_count': SyncTarget(
        sync_type='mode_usage_count',
        env_table_id='FEISHU_BITABLE_MODE_USAGE_TABLE_ID',
        table_name='mode_usage_counts',
        unique_payload_key='summary_key',
        unique_feishu_field='汇总键',
        field_map={
            'summary_key': '汇总键',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'total_usage_count': '总使用次数',
            'drag_usage_count': '自由创作使用次数',
            'inspire_usage_count': '灵感创想使用次数',
            'chat_usage_count': '对话改造使用次数',
            'slider_usage_count': '智能参数使用次数',
            'last_mode_used': '最近使用模式',
            'last_session_id': '最近会话ID',
            'updated_at': '更新时间',
        },
        field_types={
            '总使用次数': NUMBER_FIELD_TYPE,
            '自由创作使用次数': NUMBER_FIELD_TYPE,
            '灵感创想使用次数': NUMBER_FIELD_TYPE,
            '对话改造使用次数': NUMBER_FIELD_TYPE,
            '智能参数使用次数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
    'work_count_summary': SyncTarget(
        sync_type='work_count_summary',
        env_table_id='FEISHU_BITABLE_WORK_COUNTS_TABLE_ID',
        table_name='work_count_summaries',
        unique_payload_key='summary_key',
        unique_feishu_field='汇总键',
        field_map={
            'summary_key': '汇总键',
            'participant_code': '参与者编号',
            'display_name': '登记姓名',
            'total_draft_work_count': '草稿箱作品总数',
            'drag_work_count': '自由创作作品数',
            'drag_revision_generation_count': '自由创作修改/生成次数',
            'inspire_work_count': '灵感创想作品数',
            'inspire_revision_generation_count': '灵感创想修改/生成次数',
            'chat_work_count': '对话改造作品数',
            'chat_revision_generation_count': '对话改造修改/生成次数',
            'slider_work_count': '智能参数作品数',
            'slider_revision_generation_count': '智能参数修改/生成次数',
            'updated_at': '更新时间',
        },
        field_types={
            '草稿箱作品总数': NUMBER_FIELD_TYPE,
            '自由创作作品数': NUMBER_FIELD_TYPE,
            '自由创作修改/生成次数': NUMBER_FIELD_TYPE,
            '灵感创想作品数': NUMBER_FIELD_TYPE,
            '灵感创想修改/生成次数': NUMBER_FIELD_TYPE,
            '对话改造作品数': NUMBER_FIELD_TYPE,
            '对话改造修改/生成次数': NUMBER_FIELD_TYPE,
            '智能参数作品数': NUMBER_FIELD_TYPE,
            '智能参数修改/生成次数': NUMBER_FIELD_TYPE,
            '更新时间': DATE_FIELD_TYPE,
        },
    ),
}


def _load_dotenv_once() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True

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


def _env(name: str, default: str = '') -> str:
    _load_dotenv_once()
    return os.getenv(name, default).strip()


def feishu_enabled() -> bool:
    return bool(_env('FEISHU_APP_ID') and _env('FEISHU_APP_SECRET') and _env('FEISHU_BITABLE_APP_TOKEN'))


class FeishuClient:
    def __init__(self) -> None:
        self.app_id = _env('FEISHU_APP_ID')
        self.app_secret = _env('FEISHU_APP_SECRET')
        self.app_token = _env('FEISHU_BITABLE_APP_TOKEN')
        self._tenant_access_token = ''
        self._token_expire_at = 0.0
        self._field_cache: dict[str, set[str]] = {}
        self._record_lookup_cache: dict[tuple[str, str], dict[str, str]] = {}

    def _assert_base_config(self) -> None:
        missing = [
            name for name, value in [
                ('FEISHU_APP_ID', self.app_id),
                ('FEISHU_APP_SECRET', self.app_secret),
                ('FEISHU_BITABLE_APP_TOKEN', self.app_token),
            ] if not value
        ]
        if missing:
            raise FeishuSyncError(f'Missing Feishu config: {", ".join(missing)}')

    def tenant_access_token(self) -> str:
        self._assert_base_config()
        if self._tenant_access_token and time.time() < self._token_expire_at - 300:
            return self._tenant_access_token

        data = self._request_raw(
            'POST',
            '/auth/v3/tenant_access_token/internal',
            auth=False,
            body={'app_id': self.app_id, 'app_secret': self.app_secret},
        )
        token = data.get('tenant_access_token')
        if not token:
            raise FeishuSyncError('tenant_access_token missing in Feishu response')
        self._tenant_access_token = token
        self._token_expire_at = time.time() + int(data.get('expire') or 7200)
        return token

    def get(self, path: str, query: dict[str, Any] | None = None) -> dict:
        return self._request_raw('GET', path, query=query)

    def post(self, path: str, body: dict[str, Any] | None = None, query: dict[str, Any] | None = None) -> dict:
        return self._request_raw('POST', path, body=body or {}, query=query)

    def put(self, path: str, body: dict[str, Any] | None = None, query: dict[str, Any] | None = None) -> dict:
        return self._request_raw('PUT', path, body=body or {}, query=query)

    def patch(self, path: str, body: dict[str, Any] | None = None, query: dict[str, Any] | None = None) -> dict:
        return self._request_raw('PATCH', path, body=body or {}, query=query)

    def _request_raw(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict:
        url = f'{FEISHU_API_BASE}{path}'
        if query:
            url = f'{url}?{parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})}'

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if auth:
            headers['Authorization'] = f'Bearer {self.tenant_access_token()}'
        payload = None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
        req = request.Request(url, data=payload, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode('utf-8')
        except HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            raise FeishuSyncError(f'Feishu HTTP {exc.code}: {detail[:500]}') from exc
        except URLError as exc:
            raise FeishuSyncError(f'Feishu request failed: {exc.reason}') from exc

        try:
            decoded = json.loads(raw or '{}')
        except json.JSONDecodeError as exc:
            raise FeishuSyncError(f'Invalid Feishu JSON response: {raw[:300]}') from exc

        if decoded.get('code', 0) != 0:
            raise FeishuSyncError(f'Feishu API error {decoded.get("code")}: {decoded.get("msg")}')
        return decoded.get('data') or decoded

    def ensure_fields(self, table_id: str, field_names: list[str], field_types: dict[str, int] | None = None) -> None:
        if not table_id:
            raise FeishuSyncError('table_id is required')

        cached = self._field_cache.get(table_id)
        if cached is None:
            cached = set()
            page_token = ''
            while True:
                data = self.get(
                    f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/fields',
                    query={'page_size': 100, 'page_token': page_token},
                )
                cached.update(
                    str(item.get('field_name') or '')
                    for item in data.get('items', [])
                    if item.get('field_name')
                )
                if not data.get('has_more') or not data.get('page_token'):
                    break
                page_token = data.get('page_token')
            self._field_cache[table_id] = cached

        for field_name in field_names:
            if field_name in cached:
                continue
            try:
                self.post(
                    f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/fields',
                    body={'field_name': field_name, 'type': (field_types or {}).get(field_name, TEXT_FIELD_TYPE)},
                )
            except FeishuSyncError as exc:
                if 'FieldNameDuplicated' not in str(exc):
                    raise
                cached = set()
                page_token = ''
                while True:
                    data = self.get(
                        f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/fields',
                        query={'page_size': 100, 'page_token': page_token},
                    )
                    cached.update(
                        str(item.get('field_name') or '')
                        for item in data.get('items', [])
                        if item.get('field_name')
                    )
                    if not data.get('has_more') or not data.get('page_token'):
                        break
                    page_token = data.get('page_token')
                self._field_cache[table_id] = cached
                if field_name not in cached:
                    raise
            cached.add(field_name)

    def find_record_id(self, table_id: str, unique_field: str, unique_value: str) -> str:
        cache_key = (table_id, unique_field)
        lookup = self._record_lookup_cache.get(cache_key)
        if lookup is not None:
            return lookup.get(unique_value, '')

        lookup = {}
        duplicates: dict[str, list[str]] = {}
        page_token = ''
        while True:
            data = self.get(
                f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/records',
                query={'page_size': 500, 'page_token': page_token},
            )
            for item in data.get('items', []):
                fields = item.get('fields') or {}
                value = str(fields.get(unique_field) or '')
                record_id = str(item.get('record_id') or '')
                if value and record_id:
                    if value in lookup and lookup[value] != record_id:
                        duplicates.setdefault(value, [lookup[value]]).append(record_id)
                        continue
                    lookup[value] = record_id
            if not data.get('has_more') or not data.get('page_token'):
                if unique_value in duplicates:
                    record_ids = ', '.join(duplicates[unique_value])
                    raise FeishuSyncError(
                        f'Duplicate Feishu records for {unique_field}={unique_value}: {record_ids}'
                    )
                self._record_lookup_cache[cache_key] = lookup
                return lookup.get(unique_value, '')
            page_token = data.get('page_token')

    def insert_record(self, table_id: str, fields: dict[str, Any]) -> str:
        data = self.post(
            f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/records',
            body={'fields': fields},
        )
        record = data.get('record') or {}
        return str(record.get('record_id') or data.get('record_id') or '')

    def batch_insert_records(self, table_id: str, records: list[dict[str, Any]]) -> list[str]:
        if not records:
            return []
        data = self.post(
            f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/records/batch_create',
            body={'records': records},
        )
        saved_records = data.get('records') or data.get('items') or []
        return [str(item.get('record_id') or '') for item in saved_records]

    def update_record(self, table_id: str, record_id: str, fields: dict[str, Any]) -> str:
        data = self.put(
            f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/records/{parse.quote(record_id)}',
            body={'fields': fields},
        )
        record = data.get('record') or {}
        return str(record.get('record_id') or record_id)

    def batch_update_records(self, table_id: str, records: list[dict[str, Any]]) -> list[str]:
        if not records:
            return []
        data = self.post(
            f'/bitable/v1/apps/{parse.quote(self.app_token)}/tables/{parse.quote(table_id)}/records/batch_update',
            body={'records': records},
        )
        saved_records = data.get('records') or data.get('items') or []
        returned_ids = [str(item.get('record_id') or '') for item in saved_records]
        if len(returned_ids) == len(records):
            return returned_ids
        return [str(item.get('record_id') or '') for item in records]

    def upsert_record(
        self,
        table_id: str,
        fields: dict[str, Any],
        *,
        unique_field: str,
        unique_value: str,
        known_record_id: str = '',
        legacy_unique_values: list[str] | None = None,
    ) -> str:
        record_id = known_record_id or self.find_record_id(table_id, unique_field, unique_value)
        if not record_id:
            for legacy_value in legacy_unique_values or []:
                record_id = self.find_record_id(table_id, unique_field, legacy_value)
                if record_id:
                    break
        if record_id:
            try:
                saved_record_id = self.update_record(table_id, record_id, fields)
            except FeishuSyncError as exc:
                if not _is_record_not_found_error(exc):
                    raise
                saved_record_id = self.insert_record(table_id, fields)
        else:
            saved_record_id = self.insert_record(table_id, fields)
        lookup = self._record_lookup_cache.get((table_id, unique_field))
        if lookup is not None and saved_record_id:
            lookup[unique_value] = saved_record_id
        return saved_record_id


def _parse_datetime_ms(value: Any) -> int | None:
    if value in (None, ''):
        return None
    if isinstance(value, (int, float)):
        return int(value * 1000 if value < 10_000_000_000 else value)
    text = str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return int(datetime.strptime(text, fmt).timestamp() * 1000)
        except ValueError:
            pass
    return None


def _coerce_feishu_value(value: Any, field_type: int = TEXT_FIELD_TYPE) -> Any:
    if value is None:
        return None
    if field_type == NUMBER_FIELD_TYPE:
        if value == '':
            return None
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return None
    if field_type == DATE_FIELD_TYPE:
        return _parse_datetime_ms(value)
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _normalize_hci_participant_code(value: Any) -> str:
    text = str(value or '').strip().upper()
    match = re.fullmatch(r'(?:HCI-)?(\d+)', text)
    if not match:
        return text
    digits = match.group(1)
    return digits.zfill(4) if len(digits) < 4 else digits


def _legacy_hci_participant_values(value: Any) -> list[str]:
    code = _normalize_hci_participant_code(value)
    return [f'HCI-{code}'] if code.isdigit() else []


def _fields_for_target(target: SyncTarget, payload: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for payload_key, field_name in target.field_map.items():
        if payload_key not in payload:
            continue
        value = _coerce_feishu_value(
            payload.get(payload_key),
            target.field_types.get(field_name, TEXT_FIELD_TYPE),
        )
        if value is not None:
            fields[field_name] = value
        elif target.field_types.get(field_name, TEXT_FIELD_TYPE) == DATE_FIELD_TYPE:
            fields[field_name] = None
    return fields


def _prepare_sync_job(job: dict) -> tuple[SyncTarget, PreparedSyncJob]:
    target = SYNC_TARGETS.get(job.get('sync_type'))
    if not target:
        raise FeishuSyncError(f'Unsupported sync_type: {job.get("sync_type")}')

    table_id = _env(target.env_table_id)
    if not table_id:
        raise FeishuSyncError(f'Missing table id env: {target.env_table_id}')

    try:
        payload = json.loads(job.get('payload') or '{}')
    except json.JSONDecodeError as exc:
        raise FeishuSyncError('Invalid sync payload JSON') from exc

    payload = dict(payload or {})
    for key in ['participant_code', 'participant_id']:
        if key in payload:
            code = _normalize_hci_participant_code(payload.get(key))
            if code.isdigit():
                payload[key] = code

    unique_value = str(payload.get(target.unique_payload_key) or job.get('target_key') or '').strip()
    legacy_unique_values: list[str] = []
    if target.sync_type == 'hci_participant':
        unique_value = _normalize_hci_participant_code(unique_value)
        legacy_unique_values = _legacy_hci_participant_values(unique_value)
    if not unique_value:
        raise FeishuSyncError(f'Missing unique payload key: {target.unique_payload_key}')

    return target, PreparedSyncJob(
        job_id=int(job['id']),
        sync_type=target.sync_type,
        table_id=table_id,
        fields=_fields_for_target(target, payload),
        unique_field=target.unique_feishu_field,
        unique_value=unique_value,
        known_record_id=str(job.get('remote_record_id') or ''),
        legacy_unique_values=legacy_unique_values,
    )


def _sync_job_blocking(job: dict, client: FeishuClient | None = None) -> str:
    target, prepared = _prepare_sync_job(job)
    client = client or FeishuClient()
    field_names = list(target.field_map.values())
    client.ensure_fields(prepared.table_id, field_names, target.field_types)
    return client.upsert_record(
        prepared.table_id,
        prepared.fields,
        unique_field=prepared.unique_field,
        unique_value=prepared.unique_value,
        known_record_id=prepared.known_record_id,
        legacy_unique_values=prepared.legacy_unique_values,
    )


def _chunks(items: list[Any], size: int = 100) -> list[list[Any]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _is_record_not_found_error(exc: Exception) -> bool:
    message = str(exc)
    return '1254043' in message or 'record not found' in message.lower()


def _sync_jobs_batch_blocking(jobs: list[dict], client: FeishuClient) -> dict[int, tuple[bool, str]]:
    if not jobs:
        return {}

    results: dict[int, tuple[bool, str]] = {}
    prepared_jobs: list[tuple[SyncTarget, PreparedSyncJob]] = []
    for job in jobs:
        try:
            prepared_jobs.append(_prepare_sync_job(job))
        except Exception as exc:
            results[int(job.get('id') or 0)] = (False, str(exc))

    for sync_type in sorted({target.sync_type for target, _ in prepared_jobs}):
        group = [(target, prepared) for target, prepared in prepared_jobs if target.sync_type == sync_type]
        if not group:
            continue
        target = group[0][0]
        field_names = list(target.field_map.values())
        table_id = group[0][1].table_id
        try:
            client.ensure_fields(table_id, field_names, target.field_types)
        except Exception as exc:
            for _, prepared in group:
                results[prepared.job_id] = (False, str(exc))
            continue

        updates: list[tuple[PreparedSyncJob, dict[str, Any]]] = []
        inserts: list[PreparedSyncJob] = []
        for _, prepared in group:
            record_id = prepared.known_record_id or client.find_record_id(
                prepared.table_id,
                prepared.unique_field,
                prepared.unique_value,
            )
            if not record_id:
                for legacy_value in prepared.legacy_unique_values:
                    record_id = client.find_record_id(
                        prepared.table_id,
                        prepared.unique_field,
                        legacy_value,
                    )
                    if record_id:
                        break
            if record_id:
                updates.append((prepared, {'record_id': record_id, 'fields': prepared.fields}))
            else:
                inserts.append(prepared)

        for chunk in _chunks(updates):
            records = [record for _, record in chunk]
            try:
                record_ids = client.batch_update_records(table_id, records)
            except Exception as exc:
                if _is_record_not_found_error(exc):
                    for prepared, record in chunk:
                        try:
                            record_id = client.upsert_record(
                                table_id,
                                prepared.fields,
                                unique_field=prepared.unique_field,
                                unique_value=prepared.unique_value,
                                known_record_id='',
                                legacy_unique_values=prepared.legacy_unique_values,
                            )
                            results[prepared.job_id] = (True, record_id or str(record.get('record_id') or ''))
                        except Exception as fallback_exc:
                            results[prepared.job_id] = (False, str(fallback_exc))
                    continue
                for prepared, _ in chunk:
                    results[prepared.job_id] = (False, str(exc))
                continue
            for (prepared, record), saved_record_id in zip(chunk, record_ids):
                remote_record_id = saved_record_id or str(record.get('record_id') or '')
                lookup = client._record_lookup_cache.get((table_id, prepared.unique_field))
                if lookup is not None and remote_record_id:
                    lookup[prepared.unique_value] = remote_record_id
                results[prepared.job_id] = (True, remote_record_id)

        for chunk in _chunks(inserts):
            records = [{'fields': prepared.fields} for prepared in chunk]
            try:
                record_ids = client.batch_insert_records(table_id, records)
            except Exception as exc:
                for prepared in chunk:
                    results[prepared.job_id] = (False, str(exc))
                continue
            for prepared, remote_record_id in zip(chunk, record_ids):
                lookup = client._record_lookup_cache.get((table_id, prepared.unique_field))
                if lookup is not None and remote_record_id:
                    lookup[prepared.unique_value] = remote_record_id
                results[prepared.job_id] = (True, remote_record_id)

    return results


async def sync_job(job: dict, client: FeishuClient | None = None) -> bool:
    try:
        record_id = await asyncio.to_thread(_sync_job_blocking, job, client)
        mark_feishu_sync_success(int(job['id']), record_id)
        return True
    except Exception as exc:
        logger.warning('Feishu sync failed: %s %s', job.get('sync_type'), exc)
        mark_feishu_sync_failed(int(job['id']), str(exc))
        return False


async def sync_jobs_batch(jobs: list[dict], client: FeishuClient | None = None) -> dict[str, int]:
    if not jobs:
        return {'success': 0, 'failed': 0}
    client = client or FeishuClient()
    results = await asyncio.to_thread(_sync_jobs_batch_blocking, jobs, client)
    success = 0
    failed = 0
    for job in jobs:
        job_id = int(job['id'])
        ok, value = results.get(job_id, (False, 'Batch sync returned no result'))
        if ok:
            mark_feishu_sync_success(job_id, value)
            success += 1
        else:
            mark_feishu_sync_failed(job_id, value)
            failed += 1
    return {'success': success, 'failed': failed}


async def sync_due_jobs_once(limit: int = 20) -> dict[str, int]:
    jobs = get_due_feishu_sync_jobs(limit=limit)
    if not jobs:
        return {'success': 0, 'failed': 0, 'skipped': 0}
    if not feishu_enabled():
        return {'success': 0, 'failed': 0, 'skipped': len(jobs)}

    client = FeishuClient()
    result = await sync_jobs_batch(jobs, client)
    return {'success': result['success'], 'failed': result['failed'], 'skipped': 0}


async def feishu_retry_loop(interval_seconds: int = 60) -> None:
    while True:
        try:
            await sync_due_jobs_once(limit=20)
        except Exception:
            logger.exception('Feishu retry loop crashed')
        await asyncio.sleep(interval_seconds)
