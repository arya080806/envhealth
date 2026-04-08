"""AI 图像生成服务 - 使用远程 API

通过 chat/completions 接口发送原图 + 改造描述，
API 返回改造后的图片链接。
"""
import io
import re
import base64
import logging
import urllib.request
import json
import ssl

from PIL import Image

logger = logging.getLogger(__name__)

API_URL = 'https://ai.t8star.cn/v1/chat/completions'
API_KEY = 'sk-EDa4bbMKMnnfjuZTQw9KkS4Y3PG7NNBwjt6UkhxmYLQV455m'
MODEL = 'gpt-image-1'


def _build_prompt(green: float, urban: float, vitality: float, light: float) -> str:
    """根据滑杆参数构建中文改造描述 prompt"""
    parts = ['请基于这张照片，生成一张改造后的场景图。保持原始构图和视角不变，按以下要求修改环境：']

    if green > 70:
        parts.append('- 大幅增加绿化：添加大量树木、灌木、藤蔓和草坪，让绿色植被覆盖大部分可用区域')
    elif green > 40:
        parts.append('- 适度绿化：添加一些树木和灌木丛，保持中等程度的植被覆盖')
    else:
        parts.append('- 保持低绿化：仅保留少量植被，以硬质铺装和建筑为主')

    if urban > 70:
        parts.append('- 丰富人造设施：添加多个公园长椅、路灯、雕塑、步道和装饰性围栏')
    elif urban > 40:
        parts.append('- 适度人造元素：添加几把长椅和路灯，保持简洁')
    else:
        parts.append('- 减少人工痕迹：尽量减少人造设施，保持自然原生状态')

    if vitality > 70:
        parts.append('- 高活力氛围：场景中有多个行人在散步、交谈，整体热闹有活力')
    elif vitality > 40:
        parts.append('- 适度活力：场景中有少量行人，氛围平和')
    else:
        parts.append('- 安静宁静：场景中无人或极少人，营造宁静冥想的氛围')

    if light > 70:
        parts.append('- 暖色光线：金色暖阳照射，色调偏暖黄，如傍晚黄金时刻')
    elif light > 40:
        parts.append('- 自然光线：明亮的日光，色调自然平衡')
    else:
        parts.append('- 冷色光线：阴天柔和光线，色调偏蓝灰，氛围清冷')

    parts.append('要求：真实感强，风格统一，无文字水印，像真实照片一样自然。')
    return '\n'.join(parts)


ELEMENT_PROMPTS_CN = {
    '大树': '一棵枝叶茂盛的大树',
    '松树': '一棵高大的松树',
    '灌木': '一丛绿色灌木',
    '花坛': '一个色彩鲜艳的花坛',
    '草坪': '一片翠绿的草坪',
    '藤蔓': '墙壁上攀爬的绿色藤蔓',
    '长椅': '一把木质公园长椅',
    '路灯': '一盏复古风格路灯',
    '喷泉': '一座装饰性喷泉',
    '雕塑': '一座公园石雕',
    '步道': '一条铺设整齐的步道',
    '围栏': '一段低矮的装饰围栏',
    '小溪': '一条清澈的小溪',
    '池塘': '一个平静的小池塘',
    '水景': '一处流水景观',
    '阳光': '温暖的阳光光线',
    '雾气': '清晨的薄雾',
    '落叶': '地面的秋色落叶',
    '花瓣': '飘落的粉色花瓣',
    '鸟类': '几只栖息的鸟',
}


def _call_api(messages: list, timeout: int = 120) -> str:
    """调用 API 并返回图片 URL"""
    payload = {
        'model': MODEL,
        'messages': messages,
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        },
    )
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
    result = json.loads(resp.read())

    content = result['choices'][0]['message']['content']
    # 从 markdown 中提取图片 URL: ![image](URL)
    match = re.search(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)
    if match:
        return match.group(1)
    # 也可能直接返回URL
    match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp))', content)
    if match:
        return match.group(1)
    raise ValueError(f'API 响应中未找到图片链接: {content[:200]}')


def _download_image(url: str) -> bytes:
    """下载图片"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, timeout=60, context=ctx)
    return resp.read()


def _image_to_base64(image_path: str, max_size: int = 1024) -> str:
    """将图片转为 base64（缩放以控制大小）"""
    img = Image.open(image_path).convert('RGB')
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def _match_original_size(generated_bytes: bytes, original_path: str) -> bytes:
    """将生成的图片调整为与原图完全相同的尺寸，保持比例一致"""
    original = Image.open(original_path)
    orig_w, orig_h = original.size

    generated = Image.open(io.BytesIO(generated_bytes)).convert('RGB')
    gen_w, gen_h = generated.size

    if (gen_w, gen_h) == (orig_w, orig_h):
        return generated_bytes

    logger.info(f'尺寸调整: 生成图 {gen_w}x{gen_h} -> 原图 {orig_w}x{orig_h}')

    # 先按原图比例裁剪生成图（避免拉伸变形），再缩放到精确尺寸
    orig_ratio = orig_w / orig_h
    gen_ratio = gen_w / gen_h

    if abs(gen_ratio - orig_ratio) > 0.01:
        # 比例不同，需要居中裁剪
        if gen_ratio > orig_ratio:
            # 生成图更宽，裁两侧
            new_w = int(gen_h * orig_ratio)
            left = (gen_w - new_w) // 2
            generated = generated.crop((left, 0, left + new_w, gen_h))
        else:
            # 生成图更高，裁上下
            new_h = int(gen_w / orig_ratio)
            top = (gen_h - new_h) // 2
            generated = generated.crop((0, top, gen_w, top + new_h))

    # 缩放到原图精确尺寸
    generated = generated.resize((orig_w, orig_h), Image.LANCZOS)

    buf = io.BytesIO()
    generated.save(buf, format='PNG', quality=95)
    return buf.getvalue()


def generate_from_sliders(image_path: str, green: float, urban: float,
                          vitality: float, light: float, **_) -> bytes:
    """滑杆模式：基于参数生成改造场景"""
    logger.info(f'滑杆生成: green={green}, urban={urban}, vitality={vitality}, light={light}')

    b64 = _image_to_base64(image_path)
    prompt = _build_prompt(green, urban, vitality, light)
    logger.info(f'Prompt:\n{prompt}')

    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
                {'type': 'text', 'text': prompt},
            ],
        }
    ]

    img_url = _call_api(messages)
    logger.info(f'生成图片 URL: {img_url}')
    raw_bytes = _download_image(img_url)
    return _match_original_size(raw_bytes, image_path)


def generate_inpainting(image_path: str, elements: list[dict]) -> bytes:
    """拖拽模式：根据放置的元素描述进行改造"""
    logger.info(f'Inpainting: {len(elements)} elements')

    b64 = _image_to_base64(image_path)

    element_descriptions = []
    for el in elements:
        name = el.get('name', '')
        x_pct = el.get('x', 50)
        y_pct = el.get('y', 50)

        # 位置描述
        h_pos = '左侧' if x_pct < 33 else ('中间' if x_pct < 66 else '右侧')
        v_pos = '上方' if y_pct < 33 else ('中间' if y_pct < 66 else '下方')
        desc = ELEMENT_PROMPTS_CN.get(name, name)
        element_descriptions.append(f'在画面{v_pos}{h_pos}位置添加{desc}')

    prompt = (
        '请基于这张照片，生成一张改造后的场景图。保持原始构图和视角不变，按以下要求添加元素：\n'
        + '\n'.join(f'- {d}' for d in element_descriptions)
        + '\n要求：新添加的元素要与原有环境自然融合，光影一致，真实感强，无文字水印。'
    )
    logger.info(f'Prompt:\n{prompt}')

    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
                {'type': 'text', 'text': prompt},
            ],
        }
    ]

    img_url = _call_api(messages)
    logger.info(f'生成图片 URL: {img_url}')
    raw_bytes = _download_image(img_url)
    return _match_original_size(raw_bytes, image_path)


def is_model_loaded() -> bool:
    return True
