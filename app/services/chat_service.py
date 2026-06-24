"""对话改造模式 - 图像生成服务

使用统一图像生成服务，通过情绪标签和自由描述生成改造图像。
"""
import logging

from app.services.sd_service import (
    _call_image_edit,
    _generated_bytes_from_reference,
    _match_original_size,
    _quality_safety_requirements,
    _sanitize_user_design_text,
)
from app.services.safety_policy import apply_safety_to_prompt

logger = logging.getLogger(__name__)

# 情绪标签 -> 英文描述映射（图像生成 prompt 效果更佳）
MOOD_PROMPT_MAP = {
    '平静放松': 'calm and relaxing atmosphere, gentle light, peaceful and serene',
    '充满活力': 'fresh and lively but not crowded, bright natural colors, gentle vitality',
    '治愈温暖': 'healing and warm, soft golden light, cozy and comforting',
    '清醒专注': 'crisp and clear, fresh air feeling, invigorating and focused',
    '浪漫诗意': 'romantic and poetic, dreamy soft light, gentle and enchanting',
    '神秘探索': 'safe gentle discovery, clear paths, soft layered light, calm non-threatening depth',
    '自然野趣': 'natural and wild, lush greenery, organic textures, earthy tones',
    '欢乐轻盈': 'joyful and light-hearted, cheerful colors, playful and bright',
}


def _build_chat_prompt(mood_tags: list[str], extra_text: str) -> str:
    if not isinstance(mood_tags, list):
        mood_tags = []
    mood_tags = [str(tag).strip()[:32] for tag in mood_tags if str(tag).strip()][:2]
    extra_text = _sanitize_user_design_text(str(extra_text or '').strip()[:220])
    mood_descs = [MOOD_PROMPT_MAP.get(tag, tag) for tag in mood_tags]
    mood_str = ', '.join(mood_descs)

    parts = [
        'Keep the original composition, viewpoint and structure unchanged.',
        'Create a clearly visible environmental transformation through greenery, safe facilities, materials, spatial layering and atmosphere, not only color grading.',
        _quality_safety_requirements('The before and after images must show an obvious but realistic improvement').replace('\n', ' '),
    ]

    if mood_str:
        parts.insert(0, f'Transform this outdoor environment photo to evoke the following emotional atmosphere: {mood_str}.')
    else:
        parts.insert(0, 'Transform this outdoor environment photo according to the user emotional intent.')

    if extra_text and extra_text.strip():
        parts.insert(1, f'Additional feeling: {extra_text.strip()}')

    prompt = ' '.join(parts)
    prompt_result = apply_safety_to_prompt(
        prompt,
        'chat',
        {'mood_tags': mood_tags, 'has_extra_text': bool(extra_text)},
    )
    return prompt_result['prompt']


def generate_from_chat(image_path: str, mood_tags: list[str], extra_text: str = '') -> tuple[bytes, str]:
    """根据情绪标签和自由描述生成改造图像，返回 (image_bytes, prompt)"""
    if not isinstance(mood_tags, list):
        mood_tags = []
    mood_tags = [str(tag).strip()[:32] for tag in mood_tags if str(tag).strip()][:2]
    extra_text = _sanitize_user_design_text(str(extra_text or '').strip()[:220])
    prompt = _build_chat_prompt(mood_tags, extra_text)
    logger.info(f'对话改造生成: moods={mood_tags}, prompt前80字符={prompt[:80]}')

    image_ref = _call_image_edit(image_path, prompt)
    logger.info(f'生成图片引用: {image_ref[:120]}')
    raw_bytes = _generated_bytes_from_reference(image_ref)
    return _match_original_size(raw_bytes, image_path), prompt
