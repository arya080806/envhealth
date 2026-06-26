import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.services import chat_service, sd_service
from app.services.safety_policy import (
    build_global_safety_prompt,
    filter_element_name,
    sanitize_user_text_for_safe_environment,
)
from app.routers import api as api_routes


def _temp_image_path() -> str:
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    img = Image.new('RGB', (24, 16), '#88aa88')
    img.save(tmp.name)
    return tmp.name


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new('RGB', (24, 16), '#99bb99').save(buf, format='PNG')
    return buf.getvalue()


class SafetyPolicyTests(unittest.TestCase):
    def test_global_prompt_contains_core_constraints(self):
        prompt = build_global_safety_prompt()
        self.assertIn('结构化安全白名单与风险过滤规则', prompt)
        self.assertIn('稳定期精神分裂症患者', prompt)
        self.assertIn('禁止生成监控摄像头', prompt)
        self.assertIn('动物、昆虫、夜景、强梦幻效果默认不生成', prompt)

    def test_drag_reframes_blocked_elements_before_prompt(self):
        image_path = _temp_image_path()
        captured = {}

        def fake_call(_image_path, prompt, *args, **kwargs):
            captured['prompt'] = prompt
            return 'fake-ref'

        elements = [
            {'name': '摄像头', 'category': '设施', 'x': 20, 'y': 40, 'scale': 1},
            {'name': '黑夜', 'category': '氛围', 'x': 50, 'y': 30, 'scale': 1},
            {'name': '萤火虫', 'category': '氛围', 'x': 70, 'y': 30, 'scale': 1},
            {'name': '彩虹', 'category': '氛围', 'x': 60, 'y': 20, 'scale': 1},
            {'name': '强围栏', 'category': '设施', 'x': 50, 'y': 80, 'scale': 1},
        ]

        with patch.object(sd_service, '_call_image_edit', fake_call), \
                patch.object(sd_service, '_generated_bytes_from_reference', lambda _ref: _png_bytes()):
            sd_service.generate_inpainting(image_path, elements)

        prompt = captured['prompt']
        self.assertIn('结构化安全白名单与风险过滤规则', prompt)
        self.assertIn('柔和路灯', prompt)
        self.assertIn('柔和自然光', prompt)
        self.assertIn('低矮花池边界', prompt)
        self.assertNotIn('生成摄像头', prompt)
        self.assertNotIn('生成黑夜', prompt)
        self.assertNotIn('生成萤火虫', prompt)
        self.assertNotIn('生成彩虹', prompt)
        self.assertNotIn('生成强围栏', prompt)

    def test_inspire_reframes_risk_user_annotations(self):
        image_path = _temp_image_path()
        captured = {}

        def fake_call(_image_path, prompt, *args, **kwargs):
            captured['prompt'] = prompt
            return 'fake-ref'

        sketch_data = {
            'type': 'element',
            'results': [
                {'elemName': '摄像头', 'confidence': 0.9, 'x': 40, 'y': 40},
                {'elemName': '不确定符号', 'confidence': 0.3, 'x': 55, 'y': 60},
            ],
            'userAnnotations': [
                {'userLabel': '被监控', 'x': 30, 'y': 50, 'bboxW': 20, 'bboxH': 10},
                {'userLabel': '黑夜恐怖', 'x': 70, 'y': 50, 'bboxW': 18, 'bboxH': 12},
            ],
            'strokeLog': [
                {'strokeId': 's1', 'autoLabel': '摄像头', 'userLabel': '恐怖', 'x': 30, 'y': 50, 'bboxW': 20, 'bboxH': 10},
            ],
            'sceneIntent': {'dominantMood': '自由创想', 'complexityLevel': 'medium', 'spatialPatterns': []},
            'moodParams': {'green': 50, 'urban': 50, 'vitality': 50, 'light': 50},
        }

        with patch.object(sd_service, '_call_image_edit', fake_call), \
                patch.object(sd_service, '_generated_bytes_from_reference', lambda _ref: _png_bytes()):
            sd_service.generate_from_sketch(image_path, sketch_data)

        prompt = captured['prompt']
        self.assertIn('结构化安全白名单与风险过滤规则', prompt)
        self.assertIn('没有监控感', prompt)
        self.assertIn('柔和自然层次或可停留空间', prompt)
        self.assertIn('安全、安静、无威胁的自然环境', prompt)
        self.assertNotIn('被监控', prompt)
        self.assertNotIn('黑夜恐怖', prompt)

    def test_chat_risk_text_reframes_and_records_terms(self):
        safety = sanitize_user_text_for_safe_environment('我觉得被监控，有人跟踪，黑夜很恐怖')
        self.assertTrue(safety['risk_detected'])
        self.assertIn('被监控', safety['risk_terms'])
        self.assertIn('黑夜', safety['risk_terms'])
        self.assertIn('没有监控感', safety['safe_text'])

        image_path = _temp_image_path()
        captured = {}

        def fake_call(_image_path, prompt, *args, **kwargs):
            captured['prompt'] = prompt
            return 'fake-ref'

        with patch.object(chat_service, '_call_image_edit', fake_call), \
                patch.object(chat_service, '_generated_bytes_from_reference', lambda _ref: _png_bytes()):
            chat_service.generate_from_chat(image_path, ['平静放松'], safety['safe_text'])

        prompt = captured['prompt']
        self.assertIn('结构化安全白名单与风险过滤规则', prompt)
        self.assertIn('没有监控感', prompt)
        self.assertNotIn('被监控', prompt)
        self.assertNotIn('有人跟踪', prompt)

    def test_slider_high_vitality_uses_safe_activity_language(self):
        prompt = sd_service._build_prompt(80, 80, 95, 60)
        self.assertIn('高安全活力', prompt)
        self.assertIn('不生成拥挤人群、强运动、商业噪声或复杂互动', prompt)
        self.assertNotIn('少量行人', prompt)

    def test_masked_edits_send_soft_alpha_masks(self):
        image_path = _temp_image_path()
        captures = []

        def fake_call(_image_path, prompt, *args, **kwargs):
            mask_path = kwargs.get('mask_path')
            capture = {'prompt': prompt, 'mask_path': mask_path}
            self.assertTrue(mask_path and Path(mask_path).exists())
            with Image.open(mask_path) as mask:
                capture['mode'] = mask.mode
                capture['size'] = mask.size
                capture['alpha_extrema'] = mask.getchannel('A').getextrema()
            captures.append(capture)
            return 'fake-ref'

        with patch.object(sd_service, '_call_image_edit', fake_call), \
                patch.object(sd_service, '_generated_bytes_from_reference', lambda _ref: _png_bytes()), \
                patch.object(sd_service, 'mask_edit_available', lambda: True):
            sd_service.generate_inpainting(image_path, [
                {'name': 'tree', 'category': 'plant', 'x': 50, 'y': 50, 'scale': 1, 'widthPct': 20, 'heightPct': 20},
            ])
            sd_service.generate_from_sketch(image_path, {
                'type': 'element',
                'results': [{'elemName': 'tree', 'confidence': 0.9, 'x': 70, 'y': 50, 'bboxW': 8, 'bboxH': 8}],
                'userAnnotations': [{'userLabel': 'shrub', 'x': 70, 'y': 50, 'bboxW': 12, 'bboxH': 10}],
                'strokeLog': [{'strokeId': 's1', 'autoLabel': 'tree', 'x': 70, 'y': 50, 'bboxW': 18, 'bboxH': 12, 'shapeType': 'wide'}],
                'strokeCount': 1,
                'sceneIntent': {'complexityLevel': 'medium', 'spatialPatterns': []},
                'moodParams': {'green': 50, 'urban': 50, 'vitality': 50, 'light': 50},
            })

        self.assertEqual(len(captures), 2)
        for capture in captures:
            self.assertEqual(capture['mode'], 'RGBA')
            self.assertEqual(capture['size'], (24, 16))
            self.assertLess(capture['alpha_extrema'][0], 255)
            self.assertEqual(capture['alpha_extrema'][1], 255)
            self.assertFalse(Path(capture['mask_path']).exists())
        self.assertIn('局部编辑', captures[0]['prompt'])
        self.assertIn('笔画与 mask', captures[1]['prompt'])

    def test_masked_edit_retries_without_mask_when_gateway_rejects_mask(self):
        image_path = _temp_image_path()
        calls = []

        def fake_call(_image_path, _prompt, *args, **kwargs):
            mask_path = kwargs.get('mask_path')
            calls.append(bool(mask_path))
            if mask_path:
                raise ValueError('image edit API request failed (400): unsupported mask')
            return 'fake-ref'

        with patch.object(sd_service, '_call_image_edit', fake_call), \
                patch.object(sd_service, '_generated_bytes_from_reference', lambda _ref: _png_bytes()), \
                patch.object(sd_service, 'mask_edit_available', lambda: True):
            sd_service.generate_inpainting(image_path, [
                {'name': 'tree', 'category': 'plant', 'x': 50, 'y': 50, 'scale': 1, 'widthPct': 20, 'heightPct': 20},
            ])

        self.assertEqual(calls, [True, False])

    def test_filter_element_name_records_actions(self):
        result = filter_element_name('强围栏', '设施')
        self.assertEqual(result['action'], 'block_reframe')
        self.assertEqual(result['safe_name'], '低矮花池边界')

    def test_api_safety_helpers_preserve_generation_shapes(self):
        elements, drag_log = api_routes._safe_inpaint_elements([
            {'name': '摄像头', 'category': '设施', 'x': 10, 'y': 20, 'scale': 1},
        ])
        self.assertEqual(elements[0]['name'], '柔和路灯')
        self.assertEqual(elements[0]['original_name'], '摄像头')
        self.assertEqual(drag_log['safety_policy_version'], 'safety_policy_v1')
        self.assertTrue(drag_log['blocked_or_reframed_items'])

        safe_text, chat_log = api_routes._safe_chat_text('被监控 黑夜')
        self.assertIn('没有监控感', safe_text)
        self.assertTrue(chat_log['risk_text_detected'])
        self.assertIn('被监控', chat_log['safety_actions'][0]['risk_terms'])

        sketch, inspire_log = api_routes._safe_sketch_payload({
            'type': 'element',
            'results': [{'elemName': '摄像头', 'confidence': 0.4, 'x': 50, 'y': 50}],
            'userAnnotations': [{'userLabel': '恐怖', 'x': 50, 'y': 50}],
            'strokeLog': [{'autoLabel': '黑夜', 'x': 50, 'y': 50}],
            'strokeCount': 1,
        })
        self.assertEqual(sketch['results'][0]['elemName'], '柔和自然层次或可停留空间')
        self.assertIn('安全、安静、无威胁', sketch['userAnnotations'][0]['userLabel'])
        self.assertTrue(inspire_log['blocked_or_reframed_items'])

        normalized = api_routes._normalize_inpaint_elements([
            {'name': 'tree', 'x': 30, 'y': 40, 'widthPct': 19.4, 'heightPct': 12.6, 'scaleToBg': 0.25},
        ])
        self.assertEqual(normalized[0]['widthPct'], 19.4)
        self.assertEqual(normalized[0]['heightPct'], 12.6)
        self.assertEqual(normalized[0]['scaleToBg'], 0.25)

        self.assertLessEqual(api_routes._slider_vitality_value({'green_level': 100}, 100, 100), 60)


if __name__ == '__main__':
    unittest.main()
