"""Structured safety policy for environment image generation prompts."""
from __future__ import annotations

import re
from typing import Any


SAFETY_POLICY_VERSION = 'safety_policy_v1'

SAFE_ALLOWED_ELEMENTS = {
    '树木', '树', '大树', '松树', '樱花树', '灌木', '草坪', '低矮花池', '花池',
    '花圃', '普通小路', '小路', '小径', '自然铺装', '长椅', '低矮座椅',
    '座椅', '柔和路灯', '普通树池', '树池', '低矮水面', '小型池塘', '池塘',
    '自然纹理', '温和日光', '阳光', '浅色天空', '开阔路径', '可停留空间',
    '灌木丛', '竹林', '花朵', '芦苇', '苔藓', '木栈道', '水面', '水草',
    '荷花', '石墙', '草地',
}

CAUTION_ELEMENTS = {
    '雕塑', '围栏', '桥', '拱桥', '亭子', '凉亭', '喷泉', '鸟', '飞鸟',
    '蝴蝶', '彩虹', '雾', '薄雾', '落叶', '花瓣', '较强装饰性设施', '较强象征性元素',
    '风车', '彩色装饰', '装饰',
}

BLOCKED_OR_REFRAMED_ELEMENTS = {
    '摄像头', '监控', '镜子', '强围栏', '铁丝网', '封闭笼状结构', '黑暗夜景',
    '黑夜', '夜景', '月光', '萤火虫', '强烈梦幻效果', '梦幻',
    '鬼怪', '鬼', '血腥', '血', '武器', '尖锐物', '破损设施', '危险高差',
    '悬崖', '高处边缘', '拥挤人群', '强烈运动人群', '商业噪声', '强霓虹',
    '霓虹', '强阴影', '超现实扭曲', '超现实', '人脸特写', '文字标语',
    '水印', '宗教符号', '政治符号', '攻击', '死亡', '恐怖',
}

RISK_TEXT_PATTERNS = {
    '被监控': '更开阔、柔和、没有监控感的安全休息空间',
    '监视': '视线开阔、路径清楚、没有监控感的安全公共空间',
    '跟踪': '视线开阔、路径清楚、让人安心的公共空间',
    '有人看我': '更开阔、柔和、没有被注视感的安全休息空间',
    '有人害我': '安全、安静、无威胁的自然环境',
    '声音': '安静、低噪声、让人容易放松的自然环境',
    '命令': '自主、舒缓、没有压迫感的可停留空间',
    '危险': '安全、稳定、动线清楚的环境',
    '攻击': '安全、安静、无威胁的自然环境',
    '血': '安全、干净、温和的自然环境',
    '死亡': '有生命力但低刺激的自然环境',
    '鬼': '真实、明亮、无威胁的日常自然环境',
    '恐怖': '安全、安静、无威胁的自然环境',
    '困住': '开阔、通透、路径清楚的可离开空间',
    '封闭': '开阔、通透、边界柔和的休息空间',
    '逃不出去': '路径清楚、出口感明确、让人安心的公共空间',
    '审判': '低压力、无评判感、温和包容的自然环境',
    '惩罚': '低压力、安全、温和包容的自然环境',
    '摄像头': '没有监控感、以柔和路灯和开阔视线替代的安全空间',
    '黑夜': '柔和自然光或傍晚但不昏暗的温暖光线',
    '坠落': '地面平稳、无高差风险、路径安全的环境',
    '自杀': '安全、稳定、可陪伴停留的自然环境',
    '自伤': '安全、稳定、可陪伴停留的自然环境',
}

_BLOCKED_REFRAME_MAP = {
    '摄像头': '柔和路灯',
    '监控': '柔和路灯',
    '镜子': '自然纹理墙面',
    '强围栏': '低矮花池边界',
    '围栏': '低矮花池边界',
    '铁丝网': '低矮花池边界',
    '封闭笼状结构': '开阔路径',
    '黑暗夜景': '柔和自然光',
    '黑夜': '柔和自然光',
    '夜景': '柔和自然光',
    '月光': '温和日光',
    '萤火虫': '柔和暖色光点',
    '强烈梦幻效果': '真实柔和光影',
    '梦幻': '真实柔和光影',
    '鬼怪': '温和自然景观',
    '鬼': '温和自然景观',
    '血腥': '自然纹理',
    '血': '自然纹理',
    '武器': '长椅',
    '尖锐物': '圆润自然铺装',
    '破损设施': '完整安全设施',
    '危险高差': '平缓步道',
    '悬崖': '平缓草坪',
    '高处边缘': '平缓步道',
    '拥挤人群': '开阔路径',
    '强烈运动人群': '开阔路径',
    '商业噪声': '安静可停留空间',
    '强霓虹': '柔和路灯',
    '霓虹': '柔和路灯',
    '强阴影': '柔和自然光',
    '超现实扭曲': '真实自然空间',
    '超现实': '真实自然空间',
    '人脸特写': '无具体身份的远处模糊行人轮廓',
    '文字标语': '自然纹理',
    '水印': '自然纹理',
    '宗教符号': '普通绿化',
    '政治符号': '普通绿化',
}

_CAUTION_REFRAME_MAP = {
    '雕塑': '普通、低矮、非象征化的景观小品',
    '围栏': '低矮、通透、边界柔和的花池边界',
    '桥': '低矮、平缓、安全的普通小桥',
    '拱桥': '低矮、平缓、安全的普通小桥',
    '亭子': '普通、开敞、日常的休息亭',
    '凉亭': '普通、开敞、日常的休息亭',
    '喷泉': '低矮、安静、小尺度的水景',
    '鸟': '真实、温和的鸟类，形象柔和，数量少，整体风格舒缓',
    '飞鸟': '真实、温和的飞鸟，形象柔和，数量少，整体风格舒缓',
    '蝴蝶': '真实、温和的蝴蝶，形象柔和，数量少，整体风格舒缓',
    '彩虹': '柔和、真实、低刺激的彩虹',
    '雾': '轻微空气透视，不做神秘化浓雾',
    '薄雾': '轻微空气透视，不做神秘化浓雾',
    '落叶': '少量日常自然落叶，不营造衰败或阴郁感',
    '花瓣': '少量真实花草点缀，不做梦幻化漂浮效果',
    '风车': '普通、低刺激、非游乐化的景观风车设施',
}


def _contains_any(text: str, terms: set[str] | dict[str, str]) -> list[str]:
    ordered_terms = sorted((term for term in terms if term), key=lambda term: (-len(term), term))
    return [term for term in ordered_terms if term in text]


def filter_element_name(name: str, category: str | None = None) -> dict[str, Any]:
    raw_name = str(name or '').strip()
    category = str(category or '').strip()
    normalized = raw_name
    haystack = f'{raw_name} {category}'

    blocked = _contains_any(haystack, BLOCKED_OR_REFRAMED_ELEMENTS)
    if blocked:
        term = blocked[0]
        safe_name = _BLOCKED_REFRAME_MAP.get(term, '安全、开阔、低刺激的自然环境元素')
        return {
            'safe_name': safe_name,
            'action': 'block_reframe',
            'reason': f'元素涉及风险或高刺激内容：{term}',
            'prompt_note': f'已将风险元素转译为{safe_name}，不得生成原始风险内容。',
        }

    caution = _contains_any(haystack, CAUTION_ELEMENTS)
    if caution:
        term = caution[0]
        safe_name = _CAUTION_REFRAME_MAP.get(term, f'普通、真实、低刺激、日常化的{normalized or "环境元素"}')
        return {
            'safe_name': safe_name,
            'action': 'caution_reframe',
            'reason': f'元素需要低刺激、非象征化处理：{term}',
            'prompt_note': f'请表现为{safe_name}，避免象征化、超现实或高刺激效果。',
        }

    if normalized in SAFE_ALLOWED_ELEMENTS or any(term in normalized for term in SAFE_ALLOWED_ELEMENTS):
        return {
            'safe_name': normalized,
            'action': 'allow',
            'reason': '元素在安全白名单中',
            'prompt_note': '保持真实、日常、低刺激的写实表达。',
        }

    safe_name = normalized or '可停留空间'
    return {
        'safe_name': safe_name,
        'action': 'allow',
        'reason': '未命中风险词，按普通环境元素处理',
        'prompt_note': '保持真实、日常、低刺激的写实表达。',
    }


def sanitize_user_text_for_safe_environment(text: str) -> dict[str, Any]:
    raw_text = str(text or '').strip()
    if not raw_text:
        return {
            'safe_text': '',
            'risk_detected': False,
            'risk_terms': [],
            'reframed': False,
            'reason': '',
        }

    terms = []
    reframes = []
    for term, safe_goal in RISK_TEXT_PATTERNS.items():
        if re.search(re.escape(term), raw_text, flags=re.IGNORECASE):
            terms.append(term)
            if safe_goal not in reframes:
                reframes.append(safe_goal)

    if not terms:
        return {
            'safe_text': raw_text,
            'risk_detected': False,
            'risk_terms': [],
            'reframed': False,
            'reason': '',
        }

    safe_text = '；'.join(reframes[:4]) or '安全、安静、无威胁的自然环境'
    return {
        'safe_text': safe_text,
        'risk_detected': True,
        'risk_terms': terms,
        'reframed': True,
        'reason': '用户文本包含风险词，已转译为安全环境目标',
    }


def build_global_safety_prompt() -> str:
    return (
        '\n[结构化安全白名单与风险过滤规则]\n'
        '生成结果必须真实、稳定、温和、低刺激，适合稳定期精神分裂症患者在研究员陪伴下观看。\n'
        '禁止生成监控摄像头、镜面反射、强围栏、笼状结构、黑暗夜景、强阴影、威胁性物体、'
        '破损失控设施、高处坠落风险、拥挤人群、强烈运动、强商业噪声、鬼怪、血腥、暴力、'
        '超现实扭曲、人脸特写、文字标语和水印。\n'
        '如用户输入涉及风险内容，不要复现风险内容，而要转译为更开阔、更柔和、更安全、更可停留的环境。\n'
        '人群默认不生成；如必须表现活力，只允许远处少量模糊行人或无具体身份的人物轮廓。\n'
        '动物、昆虫仅在用户明确选择鸟、飞鸟、蝴蝶等低刺激自然元素时少量、温和、舒缓地出现；其他动物、昆虫、夜景、强梦幻效果默认不生成。\n'
        '遵守现实世界物理规则；路灯、构筑物、树木、亭子、风车等实体必须落地、附着或有合理支撑，不得悬空漂浮；天空区域只适合云、柔和彩虹、远处飞鸟/蝴蝶、柔和光点等轻量自然现象。\n'
        '保持原图视角、构图、主体建筑、地平线、尺度关系和真实材质；修改应清楚可见但不夸张。'
    )


def apply_safety_to_prompt(
    prompt: str,
    mode: str,
    safety_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(safety_context or {})
    context.setdefault('mode', mode)
    prompt = str(prompt or '').strip()
    safety_prompt = build_global_safety_prompt()
    if '[结构化安全白名单与风险过滤规则]' not in prompt:
        prompt = f'{prompt}\n{safety_prompt}'.strip()
    return {
        'prompt': prompt,
        'safety_policy_version': SAFETY_POLICY_VERSION,
        'safety_context': context,
    }


def safety_log_from_actions(
    actions: list[dict[str, Any]] | None = None,
    *,
    risk_text: dict[str, Any] | None = None,
    mode: str = '',
) -> dict[str, Any]:
    actions = [a for a in (actions or []) if isinstance(a, dict)]
    blocked = [a for a in actions if a.get('action') in ('caution_reframe', 'block_reframe')]
    risk_text = dict(risk_text or {})
    return {
        'safety_policy_version': SAFETY_POLICY_VERSION,
        'safety_actions': actions,
        'blocked_or_reframed_items': blocked,
        'risk_text_detected': bool(risk_text.get('risk_detected')),
        'risk_text_reframed': risk_text.get('safe_text', '') if risk_text.get('risk_detected') else '',
        'image_input_mode': 'original_image_edit',
        'mask_used': False,
        'guide_image_used': False,
        'mode': mode,
    }
