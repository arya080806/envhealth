"""AI 图像编辑服务 - 使用远程 API

通过 OpenAI-compatible images.edit 接口发送原图 + 改造描述，
API 返回改造后的图片数据或链接。
"""
import io
import re
import base64
import binascii
import logging
import os
import random
import ipaddress
import socket
import urllib.parse
import urllib.error
import urllib.request
import json
import ssl
import uuid
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from app.services.safety_policy import (
    apply_safety_to_prompt,
    filter_element_name,
    sanitize_user_text_for_safe_environment,
)

logger = logging.getLogger(__name__)

API_URL = os.getenv('HEALING_IMAGE_API_URL', 'https://aihubmix.com/v1')
API_KEY = os.getenv('HEALING_IMAGE_API_KEY', '')
MODEL = os.getenv('HEALING_IMAGE_MODEL', 'gpt-image-2')
IMAGE_SIZE = os.getenv('HEALING_IMAGE_SIZE', 'auto')
IMAGE_QUALITY = os.getenv('HEALING_IMAGE_QUALITY', 'auto')
IMAGE_OPERATION = os.getenv('HEALING_IMAGE_OPERATION', 'edit')
IMAGE_EDIT_MAX_SIZE = int(os.getenv('HEALING_IMAGE_EDIT_MAX_SIZE', '1536'))
IMAGE_API_TIMEOUT = int(os.getenv('HEALING_IMAGE_TIMEOUT', '360'))
MAX_REMOTE_IMAGE_BYTES = 25 * 1024 * 1024
MAX_INLINE_IMAGE_CHARS = 36 * 1024 * 1024


def mask_edit_available() -> bool:
    """Whether the active image endpoint can receive an edit mask."""
    try:
        return _generation_endpoint()[1] == 'edit'
    except Exception:
        return False


def _quality_safety_requirements(visible_focus: str) -> str:
    return (
        f'[安全与质量] {visible_focus}；整体必须安全、稳定、温和，适合精神分裂症患者使用。'
        '不要加入任何可能被患者感到威胁的高风险物件、惊吓感、暴力感、压迫感、'
        '破损失控的设施、高处风险、拥挤混乱人群或超现实扭曲画面。'
        '遵守现实世界物理规则；路灯、构筑物、树木、亭子、风车等实体必须落地、附着或有合理支撑，不得悬空漂浮。'
        '天空区域只适合云、柔和彩虹、远处飞鸟/蝴蝶、柔和光点等轻量自然现象。'
        '保持照片写实质量，光影方向、透视、材质颗粒、遮挡关系和景深都要与原图自然融合，无文字水印。'
    )


def _request_timeout(default: int) -> int:
    try:
        value = int(os.getenv('HEALING_IMAGE_TIMEOUT', str(default or IMAGE_API_TIMEOUT)))
    except (TypeError, ValueError):
        value = default or IMAGE_API_TIMEOUT
    return max(60, min(900, value))


def _raise_timeout(exc: Exception) -> None:
    raise TimeoutError('图像生成服务响应超时，请稍后重试') from exc


def _build_prompt(green: float, urban: float, vitality: float, light: float) -> str:
    """根据滑杆参数构建中文改造描述 prompt"""
    parts = ['请基于这张照片，生成一张改造后的场景图。保持原始构图和视角不变，但改造结果必须与原图有肉眼可见差异，按以下要求修改环境：']

    if green > 70:
        parts.append('- 植物较多：增加更多树木、灌木、草坪和低矮花池，让植物层次更丰富，但保持开阔视线和真实日常尺度')
    elif green > 40:
        parts.append('- 植物中等：适度增加树木、灌木和草坪，保持自然覆盖度适中、空间清楚易读')
    else:
        parts.append('- 植物较少：仅保留少量整洁植物，避免杂乱密集，维持清晰路径和可停留空间')

    if urban > 70:
        parts.append('- 设施较多：增加座椅、普通小路、自然铺装、柔和路灯和低矮花池边界等日常设施，设施完整但不过度装饰')
    elif urban > 40:
        parts.append('- 设施中等：适度添加座椅、小路、路灯或铺装，让空间更方便停留和通行，整体保持简洁')
    else:
        parts.append('- 设施较少：减少座椅、小路、路灯等人造设施，只保留必要、低刺激、真实可用的基础设施')

    if vitality > 70:
        parts.append('- 高安全活力：通过明亮开阔的空间、完整设施、清晰路径和鲜活植物表现生机，不生成拥挤人群、强运动、商业噪声或复杂互动')
    elif vitality > 40:
        parts.append('- 适度安全活力：增加少量可停留设施和清晰路径，保持平和有序，不出现明显人群')
    else:
        parts.append('- 安静宁静：场景中无人或极少人，营造宁静冥想的氛围')

    if light > 70:
        parts.append('- 光线更温暖：使用柔和、温暖但不过度金黄的自然光，画面明亮稳定，不生成黑暗夜景或强烈阴影')
    elif light > 40:
        parts.append('- 光线自然：保持明亮、柔和、冷暖平衡的自然日光，空气通透且不过度梦幻化')
    else:
        parts.append('- 光线更清冷：使用柔和清冷的自然日光或阴天漫射光，色调略冷但不昏暗、不压抑')

    parts.append(_quality_safety_requirements('不要只调整亮度或色温，至少让绿化、设施、材质或空间层次产生清楚可比较的变化'))
    return '\n'.join(parts)


def coords_to_spatial_language(x_pct: float, y_pct: float) -> str:
    """将百分比坐标转为自然空间语言描述（9宫格精细版）"""
    if y_pct < 25:
        vertical = '天空高处'
    elif y_pct < 45:
        vertical = '画面上部'
    elif y_pct < 60:
        vertical = '画面中景'
    elif y_pct < 78:
        vertical = '画面中下方'
    else:
        vertical = '地面前景'

    if x_pct < 25:
        horizontal = '偏左'
    elif x_pct < 42:
        horizontal = '左侧'
    elif x_pct < 58:
        horizontal = '中央'
    elif x_pct < 75:
        horizontal = '右侧'
    else:
        horizontal = '偏右'

    return f'{vertical}{horizontal}'


# 多变描述池：每个元素名对应多条措辞，随机选一条让 prompt 更生动
_ELEMENT_PROMPTS_POOL: dict[str, list[str]] = {
    '大树': [
        '一棵枝叶茂盛的大树，树冠如伞般舒展',
        '一棵粗壮的参天大树，树叶随风轻摆',
        '一棵枝繁叶茂的大树，投下斑驳树荫',
    ],
    '树冠': [
        '一棵树冠饱满圆润的树木',
        '一棵冠幅宽广的绿色乔木',
    ],
    '树干': [
        '一棵笔直挺拔的树',
        '一棵主干笔直的高大乔木',
    ],
    '树梢': [
        '远处参天大树伸向天际的树梢',
        '天际线上方露出的树梢剪影',
    ],
    '树桩': ['一棵自然生长的树'],
    '树丛': [
        '一片郁郁葱葱的树丛',
        '几棵树木聚集成的密实树丛',
        '一片交错生长的绿色树丛',
    ],
    '松树': ['一棵高大挺拔的松树'],
    '灌木': ['一丛修剪整齐的绿色灌木'],
    '灌木球': [
        '修剪成球形的绿色灌木',
        '一个圆润可爱的灌木球',
    ],
    '灌木带': [
        '一排整齐连续的灌木',
        '沿线延展的灌木绿篱',
    ],
    '灌木围合': [
        '围合成弧形的灌木丛',
        '半环形围合的灌木，形成天然边界',
    ],
    '花圃': [
        '一个精心设计的花圃',
        '色彩缤纷的花圃种植区',
    ],
    '草坪': [
        '一片修剪平整的翠绿草坪',
        '一块绿意盎然的天然草地',
        '柔软如毯的绿色草坪',
    ],
    '植被': [
        '茂密的绿色植被覆盖',
        '自然生长的丰富植被群落',
    ],
    '绿化带': [
        '连续的绿化种植带',
        '道路两旁的绿化植物带',
    ],
    '花点': [
        '点点鲜艳的花卉点缀',
        '散落的彩色小花簇',
    ],
    '叶片': ['随风飘舞的翠绿叶片'],
    '花朵': [
        '盛开的鲜花',
        '色彩绚丽的花朵竞相绽放',
        '一朵朵娇艳的花儿迎风绽放',
    ],
    '花坛': [
        '一个色彩鲜艳的圆形花坛',
        '精心布置的几何花坛',
        '繁花似锦的环形花坛',
    ],
    '花瓣': ['随风飘落的花瓣'],
    '螺旋花坛': ['旋转排列的螺旋形花坛'],
    '小溪': [
        '一条自然弯曲的清澈小溪',
        '蜿蜒流淌的一泓清溪',
        '潺潺作响的林间小溪',
    ],
    '溪流': [
        '一段清澈见底的小溪流',
        '从石间流过的浅浅溪流',
    ],
    '水面': [
        '平静如镜的水面，倒映着天光',
        '粼粼波光的开阔水面',
    ],
    '池塘': [
        '一个倒映天空的宁静小池塘',
        '被睡莲点缀的静谧池塘',
        '碧绿清幽的天然小池塘',
    ],
    '喷泉': [
        '一座精致的喷泉水景',
        '水珠飞溅的小型喷泉',
    ],
    '喷泉池': [
        '一个圆形的喷泉水池',
        '设计典雅的喷泉水池',
    ],
    '水景': ['一处流水潺潺的水景'],
    '太阳': [
        '温暖明亮的阳光洒落',
        '金色阳光普照，洒下暖意',
    ],
    '太阳光芒': ['放射状的金色阳光'],
    '月亮': ['柔和皎洁的月光'],
    '阳光': ['温暖的阳光穿过树叶洒落'],
    '云朵': [
        '洁白蓬松的云朵点缀天空',
        '几朵悠闲的白云缓缓飘过',
    ],
    '云带': ['天边如丝绸般的白色云带'],
    '飘带云': ['飘逸如带的薄云'],
    '彩云': [
        '彩霞般绚烂的晚霞云彩',
        '被夕阳染成金紫色的绚丽云霞',
    ],
    '漩涡云': ['旋转状的奇幻云彩'],
    '光环': ['光芒四射的光环'],
    '圆形云': ['如棉絮般的圆形积云'],
    '天际线': ['开阔而层次分明的天际线'],
    '远山': [
        '远处连绵起伏的山脉',
        '薄雾中隐约可见的远山轮廓',
        '层叠渐远的青山剪影',
    ],
    '山脉轮廓': [
        '锯齿状起伏的山脉轮廓',
        '远处群山连绵的天际线',
    ],
    '晚霞': ['金橙色渐变的壮美晚霞'],
    '闪电': ['划破天际的闪电'],
    '飞鸟': [
        '自由翱翔的鸟群',
        '三两只飞鸟掠过天空',
        '远方天际自在飞翔的鸟',
    ],
    '蝴蝶': [
        '翩翩起舞的彩色蝴蝶',
        '几只蝴蝶在花间飞舞',
    ],
    '萤火虫': ['闪烁微光的萤火虫'],
    '星点': ['若隐若现的点点星光'],
    '石子': ['散落在地的天然鹅卵石'],
    '石头': [
        '几块天然形态的景观石',
        '苔藓覆盖的自然石块',
    ],
    '落叶': [
        '秋色斑斓的飘零落叶',
        '地面上金黄色的落叶铺满',
    ],
    '蘑菇': ['林间冒出的小蘑菇'],
    '路灯': [
        '一盏复古风格的铸铁路灯',
        '一盏暖光柔和的景观路灯',
    ],
    '小径': [
        '一条蜿蜒的石板小径',
        '一条曲折通幽的鹅卵石小径',
    ],
    '碎石路': ['铺满碎石的自然小路'],
    '铺装路面': ['整齐铺设的地面'],
    '台阶': ['渐次升高的石阶'],
    '栅栏': [
        '一段木质田园栅栏',
        '低矮的装饰性围栏',
    ],
    '栅栏柱': ['简洁的栅栏立柱'],
    '屋顶': ['建筑的坡屋顶轮廓'],
    '矮墙': ['一道矮矮的砌石围墙'],
    '草坪小径': ['一条穿越草地的步道'],
    '地面小径': ['一条铺设整齐的步道'],
    '立柱': ['一根装饰性景观立柱'],
    '塔尖': ['建筑或景观塔的尖顶'],
    '竹子': [
        '一丛翠绿摇曳的竹林',
        '几竿翠竹随风摆动',
    ],
    '藤蔓': [
        '攀附蔓延的绿色藤蔓',
        '自然垂落的藤蔓植物',
    ],
    '装饰雕塑': ['一座精美的景观雕塑'],
    '热气球': ['天空中漂浮的彩色热气球'],
    '云团': ['天空中一团团蓬松的白云'],
    '天空氛围': [
        '通透明亮的天空',
        '层次丰富、清澈高远的天空',
    ],
    '地面氛围': [
        '自然质朴的地面',
        '覆盖着自然纹理的地面',
    ],
    '野草': ['自由生长的野草野花'],
}


_SAFE_ELEMENT_PROMPTS: dict[str, list[str]] = {
    '仙人掌': ['无刺多肉植物组合，边缘圆润柔和'],
    '瀑布': ['低矮缓流的浅水景观，边缘平缓安全'],
    '礁石': ['圆润的自然景观石，表面平稳不尖锐'],
    '闪电': ['柔和明亮的天光层次'],
    '漩涡云': ['柔和层叠的云带'],
    '光环': ['柔和漫射的自然光晕'],
    '塔尖': ['柔和的屋顶或景观轮廓'],
    '台阶': ['低矮防滑台阶，边缘圆润清晰'],
    '碎石路': ['平整防滑的自然步道'],
}

_UNSAFE_LABEL_PATTERNS = (
    '刀', '枪', '武器', '血', '火灾', '明火', '爆炸', '闪电', '悬崖', '坠落',
    '尖刺', '尖锐', '破损', '危险', '恐怖', '鬼', '怪物', '混乱',
)


def _safe_element_name(name: str) -> str:
    clean = str(name or '').strip()
    if not clean:
        return clean
    filtered = filter_element_name(clean)
    clean = str(filtered.get('safe_name') or clean).strip()
    if clean in _SAFE_ELEMENT_PROMPTS:
        return clean
    if any(pattern in clean for pattern in _UNSAFE_LABEL_PATTERNS):
        return '安全自然景观元素'
    return clean


def _sanitize_user_design_text(text: str) -> str:
    clean = str(text or '').strip()
    if not clean:
        return ''
    sanitized = sanitize_user_text_for_safe_environment(clean)
    if sanitized.get('risk_detected'):
        return str(sanitized.get('safe_text') or '安全、安静、无威胁的自然环境')
    if any(pattern in clean for pattern in _UNSAFE_LABEL_PATTERNS):
        return '希望保持安全、稳定、温和的疗愈环境，并用自然景观元素表达用户意图。'
    return clean


def _get_element_desc(name: str) -> str:
    """从多变描述池中随机选取一条元素描述"""
    safe_name = _safe_element_name(name)
    pool = _SAFE_ELEMENT_PROMPTS.get(safe_name) or _ELEMENT_PROMPTS_POOL.get(safe_name)
    if pool:
        return random.choice(pool)
    return safe_name


def _decode_image_data(value: str) -> bytes | None:
    if not value or not isinstance(value, str):
        return None
    candidate = value.strip()
    if candidate.startswith('data:') and ',' in candidate:
        candidate = candidate.split(',', 1)[1]
    candidate = re.sub(r'\s+', '', candidate)
    if len(candidate) > MAX_INLINE_IMAGE_CHARS:
        return None
    try:
        return base64.b64decode(candidate, validate=True)
    except (binascii.Error, ValueError):
        return None


def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get('text'), str):
                chunks.append(item['text'])
            image_url = item.get('image_url')
            if isinstance(image_url, dict) and isinstance(image_url.get('url'), str):
                chunks.append(image_url['url'])
            elif isinstance(image_url, str):
                chunks.append(image_url)
        return '\n'.join(chunks)
    return ''


def _get_api_key() -> str:
    return os.getenv('HEALING_IMAGE_API_KEY', API_KEY).strip()


def _generation_endpoint() -> tuple[str, str]:
    raw_url = os.getenv('HEALING_IMAGE_API_URL', API_URL).strip().rstrip('/')
    if not raw_url:
        raw_url = 'https://aihubmix.com/v1'
    if raw_url.endswith('/chat/completions'):
        return raw_url, 'chat'
    if raw_url.endswith('/images/generations'):
        return raw_url, 'images'
    if raw_url.endswith('/images/edits'):
        return raw_url, 'edit'

    operation = os.getenv('HEALING_IMAGE_OPERATION', IMAGE_OPERATION).strip().lower()
    if operation in ('generate', 'generation', 'generations', 'images'):
        return f'{raw_url}/images/generations', 'images'
    return f'{raw_url}/images/edits', 'edit'


def _text_prompt_from_messages(messages: list) -> str:
    chunks: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = message.get('content')
        if isinstance(content, str):
            chunks.append(content)
            continue
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and isinstance(item.get('text'), str):
                    chunks.append(item['text'])
    return '\n\n'.join(chunk.strip() for chunk in chunks if chunk and chunk.strip())


def _extract_image_reference(result: dict) -> str | None:
    if not isinstance(result, dict):
        return None

    data = result.get('data')
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            return first.get('url') or first.get('b64_json')

    if isinstance(result.get('url'), str):
        return result['url']
    if isinstance(result.get('b64_json'), str):
        return result['b64_json']

    choices = result.get('choices')
    if isinstance(choices, list) and choices:
        first_choice = choices[0] if isinstance(choices[0], dict) else {}
        message = first_choice.get('message', {}) if isinstance(first_choice, dict) else {}
        content = _content_to_text(message.get('content'))
        if content:
            markdown_match = re.search(r'!\[.*?\]\((https?://[^\s)]+)\)', content)
            if markdown_match:
                return markdown_match.group(1)
            url_match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp)(?:\?\S*)?)', content)
            if url_match:
                return url_match.group(1)
            data_match = re.search(
                r'(data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=\s]+)',
                content,
            )
            if data_match:
                return data_match.group(1)
    return None


def _call_api(messages: list, timeout: int = 120) -> str:
    """调用 API 并返回图片引用：可为远程 URL、data URL 或 b64_json。"""
    timeout = _request_timeout(timeout)
    api_key = _get_api_key()
    if not api_key:
        raise ValueError('缺少 HEALING_IMAGE_API_KEY 环境变量，无法调用图像生成服务')

    endpoint, mode = _generation_endpoint()
    if mode == 'edit':
        endpoint = endpoint.replace('/images/edits', '/images/generations')
        mode = 'images'

    if mode == 'images':
        prompt = _text_prompt_from_messages(messages)
        if not prompt:
            raise ValueError('缺少图像生成 prompt')
        payload = {
            'model': os.getenv('HEALING_IMAGE_MODEL', MODEL),
            'prompt': prompt,
            'n': 1,
            'size': os.getenv('HEALING_IMAGE_SIZE', IMAGE_SIZE),
            'quality': os.getenv('HEALING_IMAGE_QUALITY', IMAGE_QUALITY),
        }
    else:
        payload = {
            'model': os.getenv('HEALING_IMAGE_MODEL', MODEL),
            'messages': messages,
        }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        raise ValueError(f'图像生成 API 请求失败 ({exc.code}): {body[:300]}') from exc
    except (TimeoutError, socket.timeout) as exc:
        _raise_timeout(exc)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, 'reason', None), socket.timeout):
            _raise_timeout(exc)
        raise

    image_ref = _extract_image_reference(result)
    if image_ref:
        return image_ref
    raise ValueError(f'API 响应中未找到图片: {str(result)[:300]}')


def _image_bytes_for_edit(image_path: str) -> tuple[bytes, str, str]:
    """将任意本地图片转为接口稳定接受的 PNG 文件载荷。"""
    img = Image.open(image_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')
    max_size = int(os.getenv('HEALING_IMAGE_EDIT_MAX_SIZE', str(IMAGE_EDIT_MAX_SIZE)))
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue(), 'image.png', 'image/png'


def _encode_multipart(
    fields: dict[str, str | int | float],
    files: dict[str, tuple[str, bytes, str]],
) -> tuple[bytes, str]:
    boundary = f'----HealingImageEdit{uuid.uuid4().hex}'
    body = bytearray()

    def add_line(value: str | bytes = b'') -> None:
        if isinstance(value, str):
            value = value.encode('utf-8')
        body.extend(value)
        body.extend(b'\r\n')

    for name, value in fields.items():
        add_line(f'--{boundary}')
        add_line(f'Content-Disposition: form-data; name="{name}"')
        add_line()
        add_line(str(value))

    for name, (filename, content, content_type) in files.items():
        safe_filename = filename.replace('"', '')
        add_line(f'--{boundary}')
        add_line(
            f'Content-Disposition: form-data; name="{name}"; filename="{safe_filename}"'
        )
        add_line(f'Content-Type: {content_type}')
        add_line()
        body.extend(content)
        body.extend(b'\r\n')

    add_line(f'--{boundary}--')
    return bytes(body), f'multipart/form-data; boundary={boundary}'


def _call_image_edit(image_path: str, prompt: str, mask_path: str | None = None, timeout: int = 180) -> str:
    """调用 images.edit，用原图作为编辑参考并返回图片引用。"""
    timeout = _request_timeout(timeout)
    api_key = _get_api_key()
    if not api_key:
        raise ValueError('缺少 HEALING_IMAGE_API_KEY 环境变量，无法调用图像生成服务')

    endpoint, mode = _generation_endpoint()
    if mode == 'chat':
        b64 = _image_to_base64(image_path)
        return _call_api([
            {
                'role': 'user',
                'content': [
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
                    {'type': 'text', 'text': prompt},
                ],
            }
        ], timeout=timeout)

    if mode == 'images':
        return _call_api([{'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}], timeout=timeout)

    image_bytes, image_name, image_type = _image_bytes_for_edit(image_path)
    fields = {
        'model': os.getenv('HEALING_IMAGE_MODEL', MODEL),
        'prompt': prompt,
        'n': '1',
        'size': os.getenv('HEALING_IMAGE_SIZE', IMAGE_SIZE),
        'quality': os.getenv('HEALING_IMAGE_QUALITY', IMAGE_QUALITY),
    }
    files = {'image': (image_name, image_bytes, image_type)}
    if mask_path:
        mask_bytes, mask_name, mask_type = _image_bytes_for_edit(mask_path)
        files['mask'] = (mask_name, mask_bytes, mask_type)

    body, content_type = _encode_multipart(fields, files)
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': content_type,
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode('utf-8', errors='replace')
        raise ValueError(f'图像编辑 API 请求失败 ({exc.code}): {body_text[:300]}') from exc
    except (TimeoutError, socket.timeout) as exc:
        _raise_timeout(exc)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, 'reason', None), socket.timeout):
            _raise_timeout(exc)
        raise

    image_ref = _extract_image_reference(result)
    if image_ref:
        return image_ref
    raise ValueError(f'API 响应中未找到图片: {str(result)[:300]}')


def _generated_bytes_from_reference(image_ref: str) -> bytes:
    decoded = _decode_image_data(image_ref)
    if decoded:
        return decoded
    if not image_ref.startswith(('http://', 'https://')):
        raise ValueError('API 响应中的图片数据格式无法识别')
    return _download_image(image_ref)


def _mask_number(value, default: float, min_value: float, max_value: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(min_value, min(max_value, number))


def _mask_box_from_region(region: dict, width: int, height: int) -> tuple[int, int, int, int] | None:
    x_pct = _mask_number(region.get('x'), 50.0, 0.0, 100.0)
    y_pct = _mask_number(region.get('y'), 50.0, 0.0, 100.0)
    bbox_w = _mask_number(
        region.get('bboxW') or region.get('widthPct'),
        _mask_number(region.get('defaultW'), 16.0, 6.0, 60.0),
        2.0,
        100.0,
    )
    bbox_h = _mask_number(
        region.get('bboxH') or region.get('heightPct'),
        _mask_number(region.get('defaultH'), 14.0, 6.0, 60.0),
        2.0,
        100.0,
    )
    pad = _mask_number(region.get('padPct'), 4.0, 0.0, 18.0)
    bbox_w = max(_mask_number(region.get('minW'), 8.0, 1.0, 80.0), bbox_w) + pad * 2
    bbox_h = max(_mask_number(region.get('minH'), 8.0, 1.0, 80.0), bbox_h) + pad * 2

    left = int(round((x_pct - bbox_w / 2) / 100 * width))
    top = int(round((y_pct - bbox_h / 2) / 100 * height))
    right = int(round((x_pct + bbox_w / 2) / 100 * width))
    bottom = int(round((y_pct + bbox_h / 2) / 100 * height))
    left = max(0, min(width - 1, left))
    top = max(0, min(height - 1, top))
    right = max(left + 1, min(width, right))
    bottom = max(top + 1, min(height, bottom))
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def _draw_mask_region(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], region: dict) -> None:
    shape = str(region.get('shapeType') or '').strip().lower()
    if shape in {'round', 'dot', 'spiral', 'enclosure'}:
        draw.ellipse(box, fill=0)
        return
    radius = max(2, min(box[2] - box[0], box[3] - box[1]) // 6)
    try:
        draw.rounded_rectangle(box, radius=radius, fill=0)
    except AttributeError:
        draw.rectangle(box, fill=0)


def _create_soft_edit_mask(image_path: str, regions: list[dict]) -> str | None:
    if not regions:
        return None
    try:
        with Image.open(image_path) as original:
            width, height = original.size
        if width <= 0 or height <= 0:
            return None

        alpha = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(alpha)
        drawn = 0
        for region in regions[:80]:
            if not isinstance(region, dict):
                continue
            box = _mask_box_from_region(region, width, height)
            if not box:
                continue
            _draw_mask_region(draw, box, region)
            drawn += 1
        if not drawn:
            return None

        blur_radius = max(2, int(round(min(width, height) * 0.012)))
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
        mask = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        mask.putalpha(alpha)
        mask_path = Path(tempfile.gettempdir()) / f'healing_edit_mask_{uuid.uuid4().hex}.png'
        mask.save(mask_path, format='PNG')
        return str(mask_path)
    except Exception:
        logger.warning('Failed to create edit mask; falling back to prompt-only edit', exc_info=True)
        return None


def _cleanup_temp_mask(mask_path: str | None) -> None:
    if not mask_path:
        return
    try:
        Path(mask_path).unlink(missing_ok=True)
    except Exception:
        logger.debug('Failed to remove temporary edit mask: %s', mask_path, exc_info=True)


def _call_image_edit_with_optional_mask(image_path: str, prompt: str, mask_path: str | None) -> str:
    if not mask_path:
        return _call_image_edit(image_path, prompt)
    try:
        return _call_image_edit(image_path, prompt, mask_path=mask_path)
    except ValueError as exc:
        message = str(exc).lower()
        likely_mask_issue = any(term in message for term in ('mask', 'unsupported', 'invalid', '400'))
        if not likely_mask_issue:
            raise
        logger.warning(
            'Masked image edit failed; retrying without mask. Error: %s',
            str(exc)[:240],
        )
        return _call_image_edit(image_path, prompt)


def _regions_from_inpaint_elements(elements: list[dict]) -> list[dict]:
    regions: list[dict] = []
    for item in elements[:20]:
        if not isinstance(item, dict):
            continue
        scale = _mask_number(item.get('scale'), 1.0, 0.05, 8.0)
        default_w = max(8.0, min(42.0, 13.0 * scale))
        default_h = max(8.0, min(46.0, 15.0 * scale))
        regions.append({
            'x': item.get('x', 50),
            'y': item.get('y', 50),
            'bboxW': item.get('bboxW') or item.get('widthPct'),
            'bboxH': item.get('bboxH') or item.get('heightPct'),
            'defaultW': default_w,
            'defaultH': default_h,
            'minW': 8,
            'minH': 8,
            'padPct': 4.5,
            'shapeType': item.get('shapeType') or 'round',
        })
    return regions


def _nearest_stroke_geometry(annotation: dict, stroke_log: list[dict]) -> dict:
    if not stroke_log:
        return {}
    stroke_ids = set(str(item) for item in annotation.get('strokeIds', []) if item)
    if stroke_ids:
        for stroke in stroke_log:
            if isinstance(stroke, dict) and str(stroke.get('strokeId') or stroke.get('id') or '') in stroke_ids:
                return stroke

    ax = _mask_number(annotation.get('x'), 50.0, 0.0, 100.0)
    ay = _mask_number(annotation.get('y'), 50.0, 0.0, 100.0)
    best: dict = {}
    best_dist = 9999.0
    for stroke in stroke_log[:80]:
        if not isinstance(stroke, dict):
            continue
        sx = _mask_number(stroke.get('x'), 50.0, 0.0, 100.0)
        sy = _mask_number(stroke.get('y'), 50.0, 0.0, 100.0)
        dist = ((sx - ax) ** 2 + (sy - ay) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best = stroke
    return best if best_dist <= 26 else {}


def _annotation_region(annotation: dict, stroke_log: list[dict]) -> dict:
    stroke = _nearest_stroke_geometry(annotation, stroke_log)
    bbox_w = annotation.get('bboxW') or stroke.get('bboxW')
    bbox_h = annotation.get('bboxH') or stroke.get('bboxH')
    shape_type = annotation.get('shapeType') or stroke.get('shapeType') or 'free'
    return {
        'x': annotation.get('x', stroke.get('x', 50)),
        'y': annotation.get('y', stroke.get('y', 50)),
        'bboxW': bbox_w,
        'bboxH': bbox_h,
        'defaultW': 16,
        'defaultH': 14,
        'minW': 8,
        'minH': 8,
        'padPct': 5,
        'shapeType': shape_type,
    }


def _regions_from_sketch_data(sketch_data: dict, elements: list[dict]) -> list[dict]:
    stroke_log = sketch_data.get('strokeLog') if isinstance(sketch_data.get('strokeLog'), list) else []
    annotations = sketch_data.get('userAnnotations') if isinstance(sketch_data.get('userAnnotations'), list) else []
    regions: list[dict] = []

    # User annotations are the semantic source of truth; nearby strokes fill in size/shape when labels are abstract.
    if annotations:
        for annotation in annotations[:80]:
            if isinstance(annotation, dict):
                regions.append(_annotation_region(annotation, stroke_log))
        return regions

    if stroke_log:
        for stroke in stroke_log[:80]:
            if not isinstance(stroke, dict):
                continue
            regions.append({
                'x': stroke.get('x', 50),
                'y': stroke.get('y', 50),
                'bboxW': stroke.get('bboxW'),
                'bboxH': stroke.get('bboxH'),
                'defaultW': 15,
                'defaultH': 13,
                'minW': 7,
                'minH': 7,
                'padPct': 5,
                'shapeType': stroke.get('shapeType') or 'free',
            })
        return regions

    for item in elements[:40]:
        if not isinstance(item, dict):
            continue
        regions.append({
            'x': item.get('x', 50),
            'y': item.get('y', 50),
            'bboxW': item.get('bboxW'),
            'bboxH': item.get('bboxH'),
            'defaultW': 14,
            'defaultH': 12,
            'minW': 7,
            'minH': 7,
            'padPct': 5,
            'shapeType': item.get('shapeType') or 'free',
        })
    return regions


def _is_public_http_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return False
    try:
        infos = socket.getaddrinfo(parsed.hostname, None, type=socket.SOCK_STREAM)
    except OSError:
        return False
    for info in infos:
        address = info[4][0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
    return True


def _download_image(url: str) -> bytes:
    """下载图片"""
    if not _is_public_http_url(url):
        raise ValueError('unsafe image URL')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, timeout=60, context=ctx)
    data = resp.read(MAX_REMOTE_IMAGE_BYTES + 1)
    if len(data) > MAX_REMOTE_IMAGE_BYTES:
        raise ValueError('remote image is too large')
    return data


def _image_to_base64(image_path: str, max_size: int = 1024) -> str:
    """将图片转为 base64（缩放以控制大小）"""
    with Image.open(image_path) as original:
        img = original.convert('RGB')
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def _match_original_size(generated_bytes: bytes, original_path: str) -> bytes:
    """将生成的图片调整为与原图完全相同的尺寸，保持比例一致"""
    with Image.open(original_path) as original:
        orig_w, orig_h = original.size

    with Image.open(io.BytesIO(generated_bytes)) as generated_original:
        generated = generated_original.convert('RGB')
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
                          vitality: float, light: float, **_) -> tuple[bytes, str]:
    """滑杆模式：基于参数生成改造场景，返回 (image_bytes, prompt)"""
    logger.info(f'滑杆生成: green={green}, urban={urban}, vitality={vitality}, light={light}')

    green = max(0.0, min(100.0, _safe_float(green, 50)))
    urban = max(0.0, min(100.0, _safe_float(urban, 50)))
    vitality = max(0.0, min(100.0, _safe_float(vitality, 50)))
    light = max(0.0, min(100.0, _safe_float(light, 50)))
    prompt = _build_prompt(green, urban, vitality, light)
    prompt_result = apply_safety_to_prompt(
        prompt,
        'slider',
        {
            'green_level': green,
            'urban_level': urban,
            'vitality_level': vitality,
            'light_warmth': light,
        },
    )
    prompt = prompt_result['prompt']
    logger.info(f'Prompt:\n{prompt}')

    image_ref = _call_image_edit(image_path, prompt)
    logger.info(f'生成图片引用: {image_ref[:120]}')
    raw_bytes = _generated_bytes_from_reference(image_ref)
    return _match_original_size(raw_bytes, image_path), prompt


def generate_inpainting(image_path: str, elements: list[dict]) -> tuple[bytes, str]:
    """拖拽模式：根据放置的元素描述进行改造，返回 (image_bytes, prompt)"""
    if not isinstance(elements, list):
        raise ValueError('elements must be a list')
    elements = [el for el in elements[:20] if isinstance(el, dict)]
    logger.info(f'Inpainting: {len(elements)} elements')

    element_descriptions = []
    for el in elements:
        safety = filter_element_name(el.get('name', ''), el.get('category', ''))
        name = _safe_element_name(safety.get('safe_name', ''))
        x_pct = max(0.0, min(100.0, _safe_float(el.get('x'), 50)))
        y_pct = max(0.0, min(100.0, _safe_float(el.get('y'), 50)))
        scale = max(0.05, min(8.0, _safe_float(el.get('scale'), 1)))
        spatial = coords_to_spatial_language(x_pct, y_pct)
        desc = _get_element_desc(name)
        annotation = _sanitize_user_design_text(
            el.get('safe_annotation') or el.get('annotation') or el.get('elemAnnotation') or ''
        )[:100]
        if annotation:
            desc = f'优先按照用户标注“{annotation}”理解该元素；基础元素为{name}，参考描述为{desc}'
        if scale >= 1.6:
            size_hint = '作为清晰可见的较大主体'
        elif scale <= 0.7:
            size_hint = '作为精致但能看清的局部点缀'
        else:
            size_hint = '作为明确可见的环境元素'
        prompt_note = safety.get('prompt_note') or '保持真实、日常、低刺激的写实表达。'
        element_descriptions.append(
            f'在{spatial}位置按用户放置意图生成{desc}，{size_hint}，不要缩成难以察觉的小变化；{prompt_note}'
        )

    prompt = (
        '请基于这张照片，生成一张改造后的场景图。保持原始构图和视角不变，但用户放置的元素必须形成肉眼可见的实际改造，按以下要求添加元素：\n'
        + '\n'.join(f'- {d}' for d in element_descriptions)
        + '\n' + _quality_safety_requirements('不要只做轻微调色，所有用户放置的元素都要在对应位置生成清楚、写实、可比较的环境变化')
    )
    if mask_edit_available() and elements:
        prompt += (
            '\n[局部编辑] 已随原图提供柔边透明 mask；请优先只在 mask 透明区域生成用户放置的元素，'
            '保留 mask 外的原图结构、透视、材质和光影连续性。'
        )
    prompt_result = apply_safety_to_prompt(prompt, 'drag', {'element_count': len(elements)})
    prompt = prompt_result['prompt']
    logger.info(f'Prompt:\n{prompt}')

    mask_path = _create_soft_edit_mask(image_path, _regions_from_inpaint_elements(elements)) if mask_edit_available() else None
    try:
        image_ref = _call_image_edit_with_optional_mask(image_path, prompt, mask_path)
    finally:
        _cleanup_temp_mask(mask_path)
    logger.info(f'生成图片引用: {image_ref[:120]}')
    raw_bytes = _generated_bytes_from_reference(image_ref)
    return _match_original_size(raw_bytes, image_path), prompt


def _build_light_description(light: float) -> str:
    """5 档光线描述"""
    if light > 80:
        return '金色夕照暖阳，色调浓暖如黄金时刻，光影绵长'
    if light > 65:
        return '暖调柔和阳光，色温偏暖黄，光线有质感'
    if light > 50:
        return '明亮自然日光，色调均衡通透'
    if light > 35:
        return '柔和漫射光，色调略偏冷灰，宁静清爽'
    return '阴天清冷漫射光，色调偏蓝灰，氛围清冽幽远'


def _build_vitality_description(vitality: float) -> str:
    """4 档活力/植被描述"""
    if vitality > 75:
        return '植被极度繁茂，花叶鲜亮饱满，满目生机'
    if vitality > 55:
        return '植被生长旺盛，绿意盎然，色彩丰富'
    if vitality > 35:
        return '植被适中有致，绿色清淡柔和'
    return '植被稀疏空旷，留白辽远，禅意悠长'


def _build_season_hint(vitality: float, light: float) -> str:
    """根据 vitality + light 组合推断季节氛围词"""
    if vitality > 75 and light > 65:
        return '盛夏午后'
    if vitality > 65 and light > 55:
        return '春末暖日'
    if vitality < 40 and light < 40:
        return '深秋薄暮'
    if vitality < 35 and light > 60:
        return '初冬晴朗'
    if vitality > 55 and light < 45:
        return '雨后清晨'
    return ''


def _build_coherence_lines(elements: list[dict]) -> list[str]:
    """根据元素间空间关系生成连贯性指令"""
    if len(elements) < 2:
        return []
    lines = []
    names = [el.get('elemName') or el.get('name', '') for el in elements if isinstance(el, dict)]
    name_set = set(names)

    relation_rules = [
        ({'大树', '小溪'}, '大树与小溪之间保持自然过渡，树根延伸至溪边'),
        ({'花坛', '池塘'}, '花坛围绕池塘边缘分布，花与水相映成趣'),
        ({'草坪', '小径'}, '小径自然穿越草坪，石板与绿草交错'),
        ({'路灯', '小径'}, '路灯沿小径一侧排列，营造漫步氛围'),
        ({'大树', '草坪'}, '大树树荫洒落在草坪上，光斑与绿地交织'),
        ({'飞鸟', '大树'}, '鸟群在大树上空盘旋飞翔'),
        ({'花朵', '灌木带'}, '花朵点缀于灌木丛间，增加色彩层次'),
        ({'远山', '云带'}, '远山与云带相接，层次渐远渐淡'),
        ({'池塘', '树丛'}, '树丛掩映池塘，水面倒映枝叶'),
        ({'竹子', '小溪'}, '翠竹沿溪生长，竹影映水'),
        ({'栅栏', '花朵'}, '花朵攀附或紧贴栅栏生长'),
        ({'喷泉', '花坛'}, '花坛环绕喷泉，形成中心景观'),
    ]
    for required_names, desc in relation_rules:
        if required_names.issubset(name_set):
            lines.append(f'- {desc}')

    return lines[:3]


def _shape_to_language(annotation: dict) -> str:
    """将笔画几何特征转为空间形态约束语言"""
    bbox_w = _safe_float(annotation.get('bboxW'), 0)
    bbox_h = _safe_float(annotation.get('bboxH'), 0)
    aspect_ratio = _safe_float(annotation.get('aspectRatio'), 1)

    if bbox_w < 6 and bbox_h < 6:
        size_label = '小尺度点状区域'
    elif bbox_w > 24 or bbox_h > 24:
        size_label = '较大面积区域'
    else:
        size_label = '中等尺度区域'

    if aspect_ratio >= 2.2:
        shape_label = '横向延展形态'
    elif aspect_ratio <= 0.55:
        shape_label = '竖向生长形态'
    elif 0.8 <= aspect_ratio <= 1.25:
        shape_label = '接近团簇或圆润形态'
    else:
        shape_label = '自由曲线形态'

    return f'{size_label}，整体呈现{shape_label}'


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _merge_user_annotations(elements: list[dict], annotations: list[dict]) -> list[dict]:
    """用户标注优先覆盖自动识别结果，支持 groupId 合并多笔为一条 prompt"""
    merged = []
    for el in (elements or []):
        if not isinstance(el, dict):
            continue
        confidence = _safe_float(el.get('confidence'), 1)
        elem_name = (
            '柔和自然层次或可停留空间'
            if confidence < 0.5
            else _safe_element_name(el.get('elemName') or el.get('name', ''))
        )
        merged.append(dict(
            el,
            elemName=elem_name,
            source=el.get('source', 'auto'),
            lowConfidenceSafetyReframed=confidence < 0.5,
        ))
    if not annotations:
        return merged

    used_indices: set[int] = set()
    for ann in annotations:
        if not isinstance(ann, dict):
            continue
        ann_x = _safe_float(ann.get('x'), 50)
        ann_y = _safe_float(ann.get('y'), 50)
        best_idx = None
        best_dist = 9999.0
        for idx, el in enumerate(merged):
            if idx in used_indices:
                continue
            dx = _safe_float(el.get('x'), 50) - ann_x
            dy = _safe_float(el.get('y'), 50) - ann_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        is_group = ann.get('isGroup', False)
        stroke_ids = ann.get('strokeIds', [])

        text_safety = sanitize_user_text_for_safe_environment(ann.get('userLabel', ''))
        safe_label = (
            text_safety.get('safe_text')
            if text_safety.get('risk_detected')
            else _safe_element_name(text_safety.get('safe_text', ''))
        )
        merged_ann = {
            'elemName': safe_label,
            'icon': '✎',
            'confidence': 1.0,
            'x': ann_x,
            'y': ann_y,
            'color': ann.get('color'),
            'tint': '',
            'source': 'user',
            'shapeHint': _shape_to_language(ann),
            'bboxW': ann.get('bboxW', 0),
            'bboxH': ann.get('bboxH', 0),
            'aspectRatio': ann.get('aspectRatio', 1),
            'groupId': ann.get('groupId'),
            'isGroup': is_group,
            'strokeCount': len(stroke_ids),
            'safetyReframedText': bool(text_safety.get('risk_detected')),
        }

        if best_idx is not None and best_dist <= 18:
            existing = merged[best_idx]
            merged[best_idx] = {
                **existing,
                **merged_ann,
                'zone': existing.get('zone', ann.get('zone')),
                'tint': existing.get('tint', ''),
            }
            used_indices.add(best_idx)
        else:
            merged.append(merged_ann)

    return merged


def _shape_type_to_language(shape_type: str) -> str:
    shape_map = {
        'round': '圆润团簇',
        'tall': '竖向生长',
        'wide': '横向延展',
        'dot': '点状聚焦',
        'wave': '波浪延展',
        'enclosure': '围合边界',
        'zigzag': '折线动势',
        'spiral': '旋转中心',
        'free': '自由曲线',
    }
    return shape_map.get(str(shape_type or '').strip(), '自由曲线')


def _expanded_element_phrase(name: str, desc: str) -> str:
    if name in {'花朵', '花点', '花坛', '花圃', '螺旋花坛'}:
        return '连续花境、花带和成片花丛'
    if name in {'灌木', '灌木带', '灌木围合', '树丛', '植被', '绿化带'}:
        return '连续的灌木与植被群落'
    if name in {'小溪', '溪流', '水景', '水面', '池塘', '喷泉', '喷泉池'}:
        return '顺着笔触展开的水景系统'
    if name in {'藤蔓', '竹子', '叶片'}:
        return '顺着笔触攀附和蔓延的植物层'
    return desc or name


def _find_stroke_context(el: dict, stroke_log: list[dict], used_indices: set[int]) -> dict | None:
    if not stroke_log:
        return None

    name = el.get('elemName') or el.get('name') or ''
    x_pct = _safe_float(el.get('x'), 50)
    y_pct = _safe_float(el.get('y'), 50)
    best_idx = None
    best_score = 9999.0

    for idx, stroke in enumerate(stroke_log[:80]):
        if idx in used_indices or not isinstance(stroke, dict):
            continue
        sx = _safe_float(stroke.get('x'), 50)
        sy = _safe_float(stroke.get('y'), 50)
        dist = ((sx - x_pct) ** 2 + (sy - y_pct) ** 2) ** 0.5
        label = stroke.get('userLabel') or stroke.get('autoLabel') or ''
        label_bonus = -12 if name and label == name else 0
        area_bonus = -min(18, (_safe_float(stroke.get('bboxW'), 0) * _safe_float(stroke.get('bboxH'), 0)) / 80)
        score = dist + label_bonus + area_bonus
        if score < best_score:
            best_score = score
            best_idx = idx

    if best_idx is None:
        return None
    if best_score > 38:
        return None
    used_indices.add(best_idx)
    return stroke_log[best_idx]


def _stroke_guided_line(name: str, desc: str, spatial: str, tint: str, stroke: dict) -> str:
    bbox_w = _safe_float(stroke.get('bboxW'), 0)
    bbox_h = _safe_float(stroke.get('bboxH'), 0)
    area = bbox_w * bbox_h
    max_dim = max(bbox_w, bbox_h)
    shape = _shape_type_to_language(stroke.get('shapeType'))
    element_phrase = _expanded_element_phrase(name, desc)
    tint_text = f'，色调呼应{tint}' if tint else ''

    if max_dim >= 24 or area >= 260:
        return (
            f'- 在{spatial}沿用户这条{shape}大笔触生成{element_phrase}{tint_text}；'
            f'覆盖或贯穿宽约画面{bbox_w:.1f}%、高约画面{bbox_h:.1f}%的区域，'
            '必须成为一眼可见的主景改造，不能只做小点缀或轻微调色'
        )
    if max_dim >= 14 or area >= 100:
        return (
            f'- 在{spatial}顺着用户{shape}笔触布置{element_phrase}{tint_text}；'
            f'影响范围约宽{bbox_w:.1f}%、高{bbox_h:.1f}%，需要有清楚的前后差异'
        )
    return f'- 在{spatial}按用户笔触位置添加{desc}{tint_text}，新元素需要清晰可见'


def _build_sketch_prompt(
    elements: list[dict],
    scene_intent: dict,
    mood_params: dict,
    complexity: str = 'medium',
    stroke_log: list[dict] | None = None,
) -> str:
    """三段式 Prompt 构建器（增强版）：保留段 / 添加段 / 氛围段"""
    lines = []
    stroke_log = [s for s in (stroke_log or []) if isinstance(s, dict)]

    lines.append('请基于这张照片，生成一张改造后的场景图。')
    lines.append('[保留] 保持原始视角、地平线位置、主体建筑轮廓和整体空间尺度；未被笔触覆盖的区域尽量稳定。')

    if stroke_log:
        large_strokes = [
            s for s in stroke_log
            if max(_safe_float(s.get('bboxW'), 0), _safe_float(s.get('bboxH'), 0)) >= 24
            or _safe_float(s.get('bboxW'), 0) * _safe_float(s.get('bboxH'), 0) >= 260
        ]
        lines.append('[笔触执行] 用户手绘笔触是明确的空间改造指令，不只是氛围参考。')
        if large_strokes:
            largest = max(
                large_strokes,
                key=lambda s: _safe_float(s.get('bboxW'), 0) * _safe_float(s.get('bboxH'), 0),
            )
            lines.append(
                '- 检测到大范围笔触：'
                f'约覆盖宽{_safe_float(largest.get("bboxW"), 0):.1f}%、高{_safe_float(largest.get("bboxH"), 0):.1f}%，'
                f'形态为{_shape_type_to_language(largest.get("shapeType"))}；'
                '改造后该区域必须出现肉眼可辨的新增景观层次。'
            )
        lines.append('- 不要只调整亮度、色温或轻微增加细节；用户画过的区域必须产生可比较的结构或元素变化。')

    add_lines = []
    used_stroke_indices: set[int] = set()

    for el in elements:
        raw_name = el.get('elemName') or el.get('name', '')
        name = str(raw_name).strip() if el.get('safetyReframedText') else _safe_element_name(raw_name)
        x_pct = el.get('x', 50)
        y_pct = el.get('y', 50)
        tint = el.get('tint', '')
        spatial = coords_to_spatial_language(x_pct, y_pct)
        source = el.get('source', 'auto')

        if source == 'user':
            shape_hint = el.get('shapeHint', '')
            bbox_w = el.get('bboxW', 0)
            bbox_h = el.get('bboxH', 0)
            is_group = el.get('isGroup', False)
            stroke_count = el.get('strokeCount', 1)
            base_line = f'- 在{spatial}按照用户指定内容生成{name}'
            if is_group and stroke_count > 1:
                base_line += f'（由{stroke_count}笔组合描绘的整体区域）'
            if shape_hint:
                base_line += f'，并尽量贴合该笔画的空间轮廓：{shape_hint}'
            if bbox_w and bbox_h:
                base_line += f'，参考区域宽约画面{bbox_w}% 、高约画面{bbox_h}%'
            add_lines.append(base_line)
            continue

        desc = _get_element_desc(name)
        stroke_context = _find_stroke_context(el, stroke_log, used_stroke_indices)
        if stroke_context:
            add_lines.append(_stroke_guided_line(name, desc, spatial, tint, stroke_context))
        elif tint:
            add_lines.append(f'- 在{spatial}自然融入{desc}，色调呈现{tint}的视觉效果')
        else:
            add_lines.append(f'- 在{spatial}自然融入{desc}')

    if scene_intent:
        for pattern in scene_intent.get('spatialPatterns', []):
            zone = pattern.get('zone', 'ground')
            elem = pattern.get('element', '')
            ptype = pattern.get('type', '')
            if not elem:
                continue
            zone_label = {
                'sky': '天空区域', 'midground': '画面中景区域', 'ground': '地面前景区域',
            }.get(zone, '画面中')
            if ptype == 'linear':
                direction = pattern.get('direction', '')
                dir_hint = '横向延伸' if direction == 'horizontal' else '纵向生长'
                add_lines.append(f'- 在{zone_label}以{dir_hint}方式添加{elem}')
            elif ptype == 'enclosure':
                add_lines.append(f'- 在{zone_label}形成围合感，添加{elem}')
            elif ptype == 'scatter':
                add_lines.append(f'- 在{zone_label}散落点缀{elem}')
            elif ptype == 'vertical':
                add_lines.append(f'- 在{zone_label}添加{elem}，营造竖向层次感')
            elif ptype == 'wash':
                add_lines.append(f'- 在{zone_label}整体覆盖{elem}，营造沉浸式自然感')
            else:
                add_lines.append(f'- 在{zone_label}融入{elem}')

    if add_lines:
        lines.append('[添加] 在场景中自然融入以下改造内容：')
        lines.extend(add_lines)

    if complexity in ('medium', 'rich') and elements:
        coherence = _build_coherence_lines(elements)
        if coherence:
            lines.append('[空间关系] 元素之间保持自然衔接：')
            lines.extend(coherence)

    tints = list({el.get('tint', '') for el in elements if el.get('tint', '')})
    if len(tints) >= 2:
        lines.append(f'[色彩] 整体色彩氛围融合{" 与 ".join(tints[:3])}的搭配，营造丰富的视觉层次。')
    elif len(tints) == 1:
        lines.append(f'[色彩] 整体色彩倾向：{tints[0]}。')

    dominant_mood = ''
    if scene_intent:
        dominant_mood = scene_intent.get('dominantMood', '')
    if not dominant_mood and mood_params:
        label_obj = mood_params.get('moodLabel')
        if label_obj:
            dominant_mood = label_obj.get('label', '')

    if dominant_mood:
        dominant_mood = _sanitize_user_design_text(dominant_mood)
        lines.append(f'[氛围] 整体光影风格参考「{dominant_mood}」的意境：')
        if mood_params:
            light = _safe_float(mood_params.get('light'), 50)
            vitality = _safe_float(mood_params.get('vitality'), 50)
            lines.append(f'- 光线：{_build_light_description(light)}')
            lines.append(f'- 植被：{_build_vitality_description(vitality)}')
            season = _build_season_hint(vitality, light)
            if season:
                lines.append(f'- 时令氛围：如同「{season}」的感觉')
        else:
            lines.append(f'- 整体营造"{dominant_mood}"的视觉感受')

    if scene_intent:
        lens_label = scene_intent.get('creativeLensLabel') or ''
        lens_prompt = scene_intent.get('creativeLensPrompt') or ''
        ai_agency = _safe_float(scene_intent.get('aiAgency'), 70)
        if lens_label or lens_prompt:
            lines.append(f'[创意方向] {lens_label}：{lens_prompt}')
        if ai_agency <= 40:
            lines.append('[用户能动性] AI 只做低强度辅助，尽量保留用户笔迹位置和原图结构，避免过度发挥。')
        elif ai_agency >= 85:
            lines.append('[用户能动性] 可进行更大胆的环境想象，用户画过的区域应被转化为清晰可见的主景或次主景。')
        else:
            lines.append('[用户能动性] 在用户笔迹和标注基础上积极扩展，保持可解释、可追溯，同时保证前后图有明显差异。')

    if complexity == 'simple':
        lines.append(_quality_safety_requirements('笔触区域必须清楚可见地改变，不能只是轻微调色'))
    elif complexity == 'rich':
        lines.append(
            _quality_safety_requirements(
                '笔触覆盖区需要成为主要视觉变化来源，前景清晰、远景略有空气透视感'
            )
        )
    else:
        lines.append(_quality_safety_requirements('笔触覆盖区要有明确变化，前后图需要能直接比较出改造内容'))

    return '\n'.join(lines)


def generate_from_sketch(image_path: str, sketch_data: dict) -> tuple[bytes, str]:
    """灵感创想模式：三层感知引擎 → 复杂度自适应 Prompt 生成，返回 (image_bytes, prompt)"""
    if not isinstance(sketch_data, dict):
        raise ValueError('sketch_data must be a dict')
    sketch_type = sketch_data.get('type', 'mood')
    scene_intent = sketch_data.get('sceneIntent') if isinstance(sketch_data.get('sceneIntent'), dict) else {}
    mood_params = sketch_data.get('moodParams') if isinstance(sketch_data.get('moodParams'), dict) else {}
    elements = sketch_data.get('results') if isinstance(sketch_data.get('results'), list) else []
    annotations = sketch_data.get('userAnnotations') if isinstance(sketch_data.get('userAnnotations'), list) else []
    elements = _merge_user_annotations(elements, annotations)
    complexity = scene_intent.get('complexityLevel', 'medium') if scene_intent else 'medium'
    interaction_round = sketch_data.get('interactionRound', 1)
    stroke_log = sketch_data.get('strokeLog') if isinstance(sketch_data.get('strokeLog'), list) else []

    user_count = sum(1 for a in annotations if isinstance(a, dict) and a.get('userLabel'))
    group_count = sum(1 for a in annotations if isinstance(a, dict) and a.get('isGroup'))

    logger.info(
        f'灵感创想生成: type={sketch_type}, '
        f'elements={len(elements)}, '
        f'annotations={len(annotations)} (groups={group_count}), '
        f'patterns={len(scene_intent.get("spatialPatterns", []))}, '
        f'complexity={complexity}, '
        f'round={interaction_round}, '
        f'strokeLog={len(stroke_log)} strokes'
    )

    prompt = _build_sketch_prompt(elements, scene_intent, mood_params, complexity, stroke_log)
    if mask_edit_available() and (annotations or stroke_log or elements):
        prompt += (
            '\n[笔画与 mask] 已随原图提供来自用户笔画/标注的柔边透明 mask。'
            '如果患者画得抽象，请以用户标注语义为准，同时参考笔画所在位置、覆盖范围、方向和形态，'
            '只在对应区域内自然转化为空间元素，保留区域外原图稳定。'
        )
    prompt_result = apply_safety_to_prompt(
        prompt,
        'inspire',
        {
            'sketch_type': sketch_type,
            'annotation_count': len(annotations),
            'stroke_count': len(stroke_log),
            'complexity': complexity,
        },
    )
    prompt = prompt_result['prompt']
    logger.info(f'Prompt:\n{prompt}')

    mask_path = _create_soft_edit_mask(image_path, _regions_from_sketch_data(sketch_data, elements)) if mask_edit_available() else None
    try:
        image_ref = _call_image_edit_with_optional_mask(image_path, prompt, mask_path)
    finally:
        _cleanup_temp_mask(mask_path)
    logger.info(f'生成图片引用: {image_ref[:120]}')
    raw_bytes = _generated_bytes_from_reference(image_ref)
    return _match_original_size(raw_bytes, image_path), prompt


def is_model_loaded() -> bool:
    return True
