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

from PIL import Image

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


def _get_element_desc(name: str) -> str:
    """从多变描述池中随机选取一条元素描述"""
    pool = _ELEMENT_PROMPTS_POOL.get(name)
    if pool:
        return random.choice(pool)
    return name


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
                          vitality: float, light: float, **_) -> tuple[bytes, str]:
    """滑杆模式：基于参数生成改造场景，返回 (image_bytes, prompt)"""
    logger.info(f'滑杆生成: green={green}, urban={urban}, vitality={vitality}, light={light}')

    green = max(0.0, min(100.0, _safe_float(green, 50)))
    urban = max(0.0, min(100.0, _safe_float(urban, 50)))
    vitality = max(0.0, min(100.0, _safe_float(vitality, 50)))
    light = max(0.0, min(100.0, _safe_float(light, 50)))
    prompt = _build_prompt(green, urban, vitality, light)
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
        name = el.get('name', '')
        x_pct = max(0.0, min(100.0, _safe_float(el.get('x'), 50)))
        y_pct = max(0.0, min(100.0, _safe_float(el.get('y'), 50)))
        spatial = coords_to_spatial_language(x_pct, y_pct)
        desc = _get_element_desc(name)
        element_descriptions.append(f'在{spatial}位置自然融入{desc}')

    prompt = (
        '请基于这张照片，生成一张改造后的场景图。保持原始构图和视角不变，按以下要求添加元素：\n'
        + '\n'.join(f'- {d}' for d in element_descriptions)
        + '\n要求：新添加的元素要与原有环境自然融合，光影一致，真实感强，无文字水印。'
    )
    logger.info(f'Prompt:\n{prompt}')

    image_ref = _call_image_edit(image_path, prompt)
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
    merged = [dict(el, source=el.get('source', 'auto')) for el in (elements or []) if isinstance(el, dict)]
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

        merged_ann = {
            'elemName': ann.get('userLabel', ''),
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
        name = el.get('elemName') or el.get('name', '')
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
        lines.append('[要求] 照片写实风格，新元素与原环境自然融合；但笔触区域必须清楚可见地改变，无文字水印。')
    elif complexity == 'rich':
        lines.append(
            '[要求] 与原图光影方向保持一致，照片写实风格，新元素与原环境无缝融合，'
            '注意远近透视关系，前景清晰、远景略有空气透视感；笔触覆盖区需要成为主要视觉变化来源，无文字水印。'
        )
    else:
        lines.append('[要求] 与原图光影方向保持一致，照片写实风格，新元素与原环境无缝融合；笔触覆盖区要有明确变化，无文字水印。')

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
    logger.info(f'Prompt:\n{prompt}')

    image_ref = _call_image_edit(image_path, prompt)
    logger.info(f'生成图片引用: {image_ref[:120]}')
    raw_bytes = _generated_bytes_from_reference(image_ref)
    return _match_original_size(raw_bytes, image_path), prompt


def is_model_loaded() -> bool:
    return True
