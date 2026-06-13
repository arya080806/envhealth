"""Research archive exporter for production records.

The exporter keeps Feishu lightweight: Feishu stores searchable indexes and
counts, while full-resolution images and canvas JSON are archived on disk.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from xml.sax.saxutils import escape

from app.db import get_all_sessions, normalize_hci_participant_code
from app.state import media_filename, resolve_media_path

DEFAULT_EXPORT_ROOT = Path(
    os.getenv(
        'RESEARCH_EXPORT_ROOT',
        '/home/zm/envhealth/research_exports' if os.name != 'nt' else str(Path.cwd() / 'research_exports'),
    )
)

MODES = {
    'drag': '自由创作',
    'inspire': '灵感创想',
    'chat': '对话改造',
    'slider': '智能参数',
    'ai': '智能参数',
}

INDEX_COLUMNS = [
    ('exported_at', '导出时间'),
    ('session_created_at', '会话创建时间'),
    ('generation_created_at', '本次生成时间'),
    ('participant_code', '参与者编号'),
    ('participant_name', '姓名'),
    ('local_user_id', '本地用户ID'),
    ('session_id', '会话ID'),
    ('mode', '模式'),
    ('mode_label', '模式名称'),
    ('scene_type', '场景类型'),
    ('selected_recommend', '预设名称'),
    ('generation_index', '第几次生成'),
    ('generation_count_total', '生成总次数'),
    ('generation_status', '生成状态'),
    ('green_level', '绿化程度'),
    ('urban_level', '城市化程度'),
    ('vitality_level', '活力程度'),
    ('light_warmth', '光照温暖度'),
    ('chat_input', '对话改造输入/感受'),
    ('chat_moods', '情绪标签'),
    ('placed_element_count', '自由创作元素数'),
    ('sketch_stroke_count', '灵感创想笔画数'),
    ('prompt', 'AI提示词'),
    ('session_folder', '资料夹'),
    ('original_file', '原图'),
    ('generated_file', '修改后生成的图片'),
    ('operation_image_file', '修改的操作/笔画图片'),
    ('canvas_json_file', '操作JSON'),
    ('metadata_file', '元数据JSON'),
    ('source_original_path', '源原图路径'),
    ('source_generated_path', '源生成图路径'),
    ('source_operation_image_path', '源操作图路径'),
    ('notes', '备注'),
]


@dataclass
class ExportStats:
    sessions: int = 0
    rows: int = 0
    copied_files: int = 0
    missing_files: list[str] = field(default_factory=list)


def _safe_segment(value: Any, fallback: str = 'unknown') -> str:
    text = str(value or '').strip() or fallback
    text = text.replace('\\', '/').split('/')[-1]
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', '_', text)
    text = re.sub(r'\s+', '_', text).strip('._ ')
    return text[:80] or fallback


def _time_text(value: Any) -> str:
    if value in (None, ''):
        return ''
    try:
        ts = float(value)
    except (TypeError, ValueError):
        return str(value)
    if ts <= 0:
        return ''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))


def _json_text(value: Any) -> str:
    if value in (None, ''):
        return ''
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _stroke_count(sketch_data: Any) -> int:
    if not isinstance(sketch_data, dict):
        return 0
    strokes = sketch_data.get('strokes') or sketch_data.get('paths') or sketch_data.get('objects') or []
    return len(strokes) if isinstance(strokes, list) else 0


def _source_name(path_value: Any) -> str:
    name = media_filename(path_value)
    if name:
        return name
    raw = str(path_value or '').strip()
    for path_cls in (PurePosixPath, PureWindowsPath, Path):
        try:
            name = path_cls(raw).name
            if name:
                return name
        except Exception:
            pass
    return ''


def _copy_media(path_value: Any, dest_dir: Path, dest_stem: str, stats: ExportStats) -> str:
    source = resolve_media_path(path_value)
    if not source:
        if path_value:
            stats.missing_files.append(str(path_value))
        return ''
    suffix = source.suffix.lower() or Path(_source_name(path_value)).suffix.lower() or '.dat'
    dest = dest_dir / f'{dest_stem}{suffix}'
    if source.resolve() != dest.resolve():
        shutil.copy2(source, dest)
        stats.copied_files += 1
    return dest.name


def _generation_items(session: dict[str, Any]) -> list[dict[str, Any]]:
    history = session.get('generation_history') or []
    items: list[dict[str, Any]] = []
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and (item.get('path') or item.get('image_path')):
                items.append(dict(item))
    latest = session.get('generated_image_path')
    if latest and not any(str(item.get('path') or item.get('image_path') or '') == str(latest) for item in items):
        items.append({
            'path': latest,
            'created_at': session.get('generation_finished_at') or session.get('created_at'),
            'mode': session.get('mode_used', ''),
            'prompt': session.get('llm_prompt', ''),
            'canvas_path': session.get('canvas_snapshot_path', ''),
        })
    return sorted(items, key=lambda item: float(item.get('created_at') or 0))


def _latest_operation_image(session: dict[str, Any]) -> Any:
    canvas_history = session.get('canvas_history') or []
    if isinstance(canvas_history, list) and canvas_history:
        last = canvas_history[-1]
        if isinstance(last, dict):
            return last.get('path') or last.get('image_path') or last.get('canvas_path')
        if isinstance(last, str):
            return last
    return session.get('canvas_snapshot_path')


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open('w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=[label for _, label in INDEX_COLUMNS])
        writer.writeheader()
        for row in rows:
            writer.writerow({label: row.get(key, '') for key, label in INDEX_COLUMNS})


def _column_name(index: int) -> str:
    name = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _write_xlsx(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = [label for _, label in INDEX_COLUMNS]
    table = [headers] + [[row.get(key, '') for key, _ in INDEX_COLUMNS] for row in rows]
    sheet_rows = []
    for row_index, row in enumerate(table, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            ref = f'{_column_name(col_index)}{row_index}'
            text = escape(str(value or ''))
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        ))
        zf.writestr('_rels/.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        ))
        zf.writestr('xl/workbook.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="index" sheetId="1" r:id="rId1"/></sheets></workbook>'
        ))
        zf.writestr('xl/_rels/workbook.xml.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'
        ))
        zf.writestr('xl/worksheets/sheet1.xml', sheet_xml)


def generate_research_archive(output_root: str | Path = DEFAULT_EXPORT_ROOT) -> dict[str, Any]:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    participants_root = root / 'participants'
    participants_root.mkdir(parents=True, exist_ok=True)
    exported_at = _time_text(time.time())
    stats = ExportStats()
    index_rows: list[dict[str, Any]] = []

    sessions = get_all_sessions()
    for session in sessions:
        mode = str(session.get('mode_used') or '').strip()
        if mode not in MODES:
            continue
        stats.sessions += 1
        participant_code = normalize_hci_participant_code(session.get('participant_id') or '')
        participant_name = str(session.get('display_name') or '').strip()
        participant_segment = _safe_segment(participant_code or participant_name, 'unknown_participant')
        session_segment = _safe_segment(
            f"{session.get('id')}_{mode}_{session.get('scene_type') or session.get('selected_recommend')}",
            str(session.get('id') or 'session'),
        )
        session_dir = participants_root / participant_segment / session_segment
        session_dir.mkdir(parents=True, exist_ok=True)

        original_file = _copy_media(session.get('uploaded_image_path'), session_dir, 'original', stats)
        latest_operation = _latest_operation_image(session)
        operation_file = _copy_media(latest_operation, session_dir, 'operation_latest', stats)
        canvas_json_file = _copy_media(session.get('canvas_json_path'), session_dir, 'canvas', stats)

        metadata_file = session_dir / 'metadata.json'
        _write_json(metadata_file, session)

        generations = _generation_items(session)
        if not generations:
            generations = [{'path': '', 'created_at': '', 'prompt': session.get('llm_prompt', '')}]

        for generation_index, generation in enumerate(generations, start=1):
            generated_source = generation.get('path') or generation.get('image_path') or ''
            generated_file = _copy_media(generated_source, session_dir, f'generated_{generation_index:02d}', stats)
            operation_source = generation.get('canvas_path') or latest_operation
            generation_operation_file = _copy_media(
                operation_source,
                session_dir,
                f'operation_for_generated_{generation_index:02d}',
                stats,
            ) or operation_file
            row = {
                'exported_at': exported_at,
                'session_created_at': _time_text(session.get('created_at')),
                'generation_created_at': _time_text(generation.get('created_at')),
                'participant_code': participant_code,
                'participant_name': participant_name,
                'local_user_id': session.get('user_id') or '',
                'session_id': session.get('id') or '',
                'mode': mode,
                'mode_label': MODES.get(mode, mode),
                'scene_type': session.get('scene_type') or '',
                'selected_recommend': session.get('selected_recommend') or '',
                'generation_index': generation_index if generated_source else '',
                'generation_count_total': session.get('generation_count') or len(_generation_items(session)),
                'generation_status': session.get('generation_status') or '',
                'green_level': session.get('green_level') or '',
                'urban_level': session.get('urban_level') or '',
                'vitality_level': session.get('vitality_level') or '',
                'light_warmth': session.get('light_warmth') or '',
                'chat_input': session.get('chat_extra') or '',
                'chat_moods': _json_text(session.get('chat_moods')),
                'placed_element_count': len(session.get('placed_elements') or []),
                'sketch_stroke_count': _stroke_count(session.get('sketch_data')),
                'prompt': generation.get('prompt') or session.get('llm_prompt') or '',
                'session_folder': str(session_dir.relative_to(root)).replace('\\', '/'),
                'original_file': original_file,
                'generated_file': generated_file,
                'operation_image_file': generation_operation_file,
                'canvas_json_file': canvas_json_file,
                'metadata_file': metadata_file.name,
                'source_original_path': session.get('uploaded_image_path') or '',
                'source_generated_path': generated_source,
                'source_operation_image_path': operation_source or '',
                'notes': '',
            }
            index_rows.append(row)
            stats.rows += 1

    _write_csv(root / 'index.csv', index_rows)
    _write_xlsx(root / 'index.xlsx', index_rows)
    manifest = {
        'generated_at': exported_at,
        'output_root': str(root),
        'session_count': stats.sessions,
        'index_row_count': stats.rows,
        'copied_file_count': stats.copied_files,
        'missing_file_count': len(stats.missing_files),
        'missing_files': sorted(set(stats.missing_files))[:200],
    }
    _write_json(root / 'manifest.json', manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate envhealth research archive.')
    parser.add_argument('--output', default=str(DEFAULT_EXPORT_ROOT), help='Archive output directory')
    args = parser.parse_args()
    manifest = generate_research_archive(args.output)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
