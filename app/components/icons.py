"""自然插画风格 SVG 图标库
风格：渐变、立体感、自然主题、无背景，仅图标本身
"""
import uuid


def _uid() -> str:
    return uuid.uuid4().hex[:6]


def _wrap(svg_body: str, size: int = 48, vb: str = '0 0 64 64') -> str:
    # 给每个 SVG 实例的内部 ID 加唯一前缀，防止同页面多实例冲突
    prefix = _uid()
    body = svg_body.replace('id="', f'id="{prefix}_').replace('url(#', f'url(#{prefix}_')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="{vb}" fill="none">{body}</svg>'
    )


# ============================================================
# 绿化类
# ============================================================

def icon_tree(size: int = 48) -> str:
    """大树 - 茂密圆形树冠"""
    return _wrap('''
    <defs>
      <linearGradient id="tr1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#4CAF50"/>
        <stop offset="100%" stop-color="#1B5E20"/>
      </linearGradient>
      <linearGradient id="tr2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#5D4037"/>
        <stop offset="100%" stop-color="#3E2723"/>
      </linearGradient>
    </defs>
    <rect x="28" y="38" width="8" height="18" rx="2" fill="url(#tr2)"/>
    <ellipse cx="32" cy="28" rx="20" ry="18" fill="url(#tr1)"/>
    <ellipse cx="24" cy="24" rx="12" ry="11" fill="#66BB6A" opacity="0.7"/>
    <ellipse cx="38" cy="22" rx="10" ry="9" fill="#81C784" opacity="0.5"/>
    <ellipse cx="32" cy="18" rx="8" ry="6" fill="#A5D6A7" opacity="0.4"/>
    ''', size)


def icon_pine(size: int = 48) -> str:
    """松树 - 三角形层叠"""
    return _wrap('''
    <defs>
      <linearGradient id="pn1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#2E7D32"/>
        <stop offset="100%" stop-color="#1B5E20"/>
      </linearGradient>
    </defs>
    <rect x="29" y="44" width="6" height="14" rx="1.5" fill="#5D4037"/>
    <polygon points="32,4 10,34 54,34" fill="url(#pn1)"/>
    <polygon points="32,14 14,38 50,38" fill="#388E3C"/>
    <polygon points="32,24 16,44 48,44" fill="#43A047"/>
    <polygon points="32,8 18,30 46,30" fill="#66BB6A" opacity="0.4"/>
    ''', size)


def icon_bush(size: int = 48) -> str:
    """灌木 - 矮丛"""
    return _wrap('''
    <defs>
      <linearGradient id="bs1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <ellipse cx="32" cy="38" rx="26" ry="16" fill="url(#bs1)"/>
    <ellipse cx="22" cy="34" rx="14" ry="12" fill="#4CAF50"/>
    <ellipse cx="42" cy="34" rx="14" ry="12" fill="#43A047"/>
    <ellipse cx="32" cy="30" rx="12" ry="10" fill="#81C784" opacity="0.6"/>
    <rect x="30" y="48" width="4" height="8" rx="1" fill="#5D4037"/>
    ''', size)


def icon_flower(size: int = 48) -> str:
    """花坛 - 多彩花朵"""
    return _wrap('''
    <defs>
      <linearGradient id="fl1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#F48FB1"/>
        <stop offset="100%" stop-color="#EC407A"/>
      </linearGradient>
    </defs>
    <rect x="30" y="36" width="4" height="18" rx="1" fill="#4CAF50"/>
    <ellipse cx="22" cy="50" rx="6" ry="3" fill="#388E3C"/>
    <ellipse cx="42" cy="50" rx="6" ry="3" fill="#388E3C"/>
    <circle cx="32" cy="26" r="6" fill="#FFF176"/>
    <ellipse cx="32" cy="16" rx="6" ry="7" fill="url(#fl1)"/>
    <ellipse cx="22" cy="22" rx="6" ry="7" fill="#F48FB1" transform="rotate(-50 22 22)"/>
    <ellipse cx="42" cy="22" rx="6" ry="7" fill="#F48FB1" transform="rotate(50 42 22)"/>
    <ellipse cx="26" cy="32" rx="6" ry="7" fill="#EC407A" transform="rotate(-120 26 32)"/>
    <ellipse cx="38" cy="32" rx="6" ry="7" fill="#EC407A" transform="rotate(120 38 32)"/>
    <circle cx="32" cy="26" r="4" fill="#FFEE58"/>
    ''', size)


def icon_lawn(size: int = 48) -> str:
    """草坪 - 嫩芽"""
    return _wrap('''
    <defs>
      <linearGradient id="lw1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81C784"/>
        <stop offset="100%" stop-color="#388E3C"/>
      </linearGradient>
    </defs>
    <path d="M32 56 C32 56 32 30 32 20 C32 8 46 4 50 16 C42 12 36 18 32 30" fill="url(#lw1)"/>
    <path d="M32 56 C32 56 32 32 30 24 C26 10 14 8 12 20 C18 14 26 20 30 32" fill="#4CAF50"/>
    <rect x="30" y="48" width="4" height="10" rx="1" fill="#5D4037"/>
    <ellipse cx="32" cy="56" rx="10" ry="4" fill="#8D6E63" opacity="0.3"/>
    ''', size)


def icon_vine(size: int = 48) -> str:
    """藤蔓 - 攀爬"""
    return _wrap('''
    <defs>
      <linearGradient id="vn1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <path d="M20 58 C20 48 16 40 24 32 C32 24 28 16 36 8" stroke="#4CAF50" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M44 58 C44 48 48 40 40 32 C32 24 36 16 28 8" stroke="#388E3C" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="24" cy="32" rx="6" ry="4" fill="url(#vn1)" transform="rotate(-30 24 32)"/>
    <ellipse cx="36" cy="20" rx="5" ry="3.5" fill="#81C784" transform="rotate(20 36 20)"/>
    <ellipse cx="20" cy="46" rx="5" ry="3.5" fill="#4CAF50" transform="rotate(-20 20 46)"/>
    <ellipse cx="40" cy="12" rx="4" ry="3" fill="#A5D6A7" transform="rotate(30 40 12)"/>
    <ellipse cx="44" cy="42" rx="5" ry="3.5" fill="#66BB6A" transform="rotate(15 44 42)"/>
    ''', size)


def icon_bamboo(size: int = 48) -> str:
    """竹林 - 竹节挺拔"""
    return _wrap('''
    <defs>
      <linearGradient id="bm1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
      <linearGradient id="bm2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81C784"/>
        <stop offset="100%" stop-color="#388E3C"/>
      </linearGradient>
    </defs>
    <rect x="12" y="10" width="7" height="52" rx="3" fill="url(#bm1)"/>
    <rect x="12" y="22" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="12" y="36" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="12" y="50" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="28" y="4" width="7" height="52" rx="3" fill="url(#bm2)"/>
    <rect x="28" y="16" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="28" y="30" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="28" y="44" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="44" y="8" width="7" height="52" rx="3" fill="url(#bm1)"/>
    <rect x="44" y="20" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="44" y="34" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <rect x="44" y="48" width="7" height="2" rx="1" fill="#1B5E20" opacity="0.5"/>
    <path d="M15 22 C8 18 4 12 8 8" stroke="#4CAF50" stroke-width="2" fill="none" stroke-linecap="round"/>
    <ellipse cx="6" cy="7" rx="5" ry="3" fill="#66BB6A" transform="rotate(-20 6 7)"/>
    <path d="M33 16 C42 10 50 6 54 10" stroke="#81C784" stroke-width="2" fill="none" stroke-linecap="round"/>
    <ellipse cx="56" cy="9" rx="5" ry="3" fill="#A5D6A7" transform="rotate(20 56 9)"/>
    <path d="M47 20 C40 14 34 12 32 6" stroke="#4CAF50" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    ''', size)


# ============================================================
# 设施类
# ============================================================


def icon_bench(size: int = 48) -> str:
    """长椅"""
    return _wrap('''
    <defs>
      <linearGradient id="bn1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#8D6E63"/>
        <stop offset="100%" stop-color="#5D4037"/>
      </linearGradient>
    </defs>
    <rect x="10" y="26" width="44" height="5" rx="2" fill="url(#bn1)"/>
    <rect x="10" y="33" width="44" height="5" rx="2" fill="#6D4C41"/>
    <rect x="10" y="40" width="44" height="5" rx="2" fill="#5D4037"/>
    <rect x="8" y="18" width="4" height="8" rx="1" fill="#4E342E"/>
    <rect x="52" y="18" width="4" height="8" rx="1" fill="#4E342E"/>
    <rect x="12" y="44" width="4" height="14" rx="1" fill="#3E2723" transform="rotate(-4 14 44)"/>
    <rect x="48" y="44" width="4" height="14" rx="1" fill="#3E2723" transform="rotate(4 50 44)"/>
    ''', size)


def icon_lamp(size: int = 48) -> str:
    """路灯"""
    return _wrap('''
    <defs>
      <linearGradient id="lm1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFD54F"/>
        <stop offset="100%" stop-color="#FFB300"/>
      </linearGradient>
      <radialGradient id="lm2" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#FFF9C4" stop-opacity="0.8"/>
        <stop offset="100%" stop-color="#FFD54F" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <rect x="30" y="24" width="4" height="34" rx="1.5" fill="#546E7A"/>
    <ellipse cx="32" cy="58" rx="8" ry="3" fill="#455A64"/>
    <circle cx="32" cy="16" r="14" fill="url(#lm2)"/>
    <path d="M22 20 L32 10 L42 20 Z" fill="url(#lm1)"/>
    <path d="M22 20 L42 20 L40 24 L24 24 Z" fill="#F9A825"/>
    <rect x="24" y="24" width="16" height="3" rx="1" fill="#546E7A"/>
    ''', size)


def icon_fountain(size: int = 48) -> str:
    """喷泉"""
    return _wrap('''
    <defs>
      <linearGradient id="ft1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#90CAF9"/>
        <stop offset="100%" stop-color="#42A5F5"/>
      </linearGradient>
      <linearGradient id="ft2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#BDBDBD"/>
        <stop offset="100%" stop-color="#757575"/>
      </linearGradient>
    </defs>
    <ellipse cx="32" cy="52" rx="24" ry="8" fill="url(#ft2)"/>
    <ellipse cx="32" cy="48" rx="24" ry="6" fill="#E0E0E0"/>
    <rect x="28" y="32" width="8" height="18" rx="2" fill="#9E9E9E"/>
    <ellipse cx="32" cy="38" rx="14" ry="5" fill="#BDBDBD"/>
    <path d="M32 6 C32 6 28 16 24 22 C20 28 32 30 32 30 C32 30 44 28 40 22 C36 16 32 6 32 6Z" fill="url(#ft1)" opacity="0.8"/>
    <path d="M26 18 C24 24 20 26 18 24" stroke="#64B5F6" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M38 18 C40 24 44 26 46 24" stroke="#64B5F6" stroke-width="2" fill="none" stroke-linecap="round"/>
    ''', size)


def icon_sculpture(size: int = 48) -> str:
    """雕塑"""
    return _wrap('''
    <defs>
      <linearGradient id="sc1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#BDBDBD"/>
        <stop offset="100%" stop-color="#757575"/>
      </linearGradient>
    </defs>
    <rect x="20" y="50" width="24" height="8" rx="2" fill="#616161"/>
    <rect x="24" y="46" width="16" height="6" rx="1" fill="#757575"/>
    <path d="M32 8 C24 8 20 16 20 24 C20 32 24 36 28 38 L28 46 L36 46 L36 38 C40 36 44 32 44 24 C44 16 40 8 32 8Z" fill="url(#sc1)"/>
    <ellipse cx="28" cy="20" rx="2.5" ry="3" fill="#616161"/>
    <ellipse cx="36" cy="20" rx="2.5" ry="3" fill="#616161"/>
    <path d="M28 28 C30 31 34 31 36 28" stroke="#616161" stroke-width="1.5" fill="none"/>
    ''', size)


def icon_path(size: int = 48) -> str:
    """步道"""
    return _wrap('''
    <defs>
      <linearGradient id="pt1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#D7CCC8"/>
        <stop offset="100%" stop-color="#A1887F"/>
      </linearGradient>
    </defs>
    <path d="M18 8 C22 20 26 32 24 44 C22 52 20 58 18 62" stroke="url(#pt1)" stroke-width="14" fill="none" stroke-linecap="round"/>
    <path d="M46 8 C42 20 38 32 40 44 C42 52 44 58 46 62" stroke="url(#pt1)" stroke-width="14" fill="none" stroke-linecap="round"/>
    <path d="M20 8 C24 20 28 32 26 44 C24 52 22 58 20 62" stroke="#BCAAA4" stroke-width="10" fill="none" stroke-linecap="round"/>
    <path d="M44 8 C40 20 36 32 38 44 C40 52 42 58 44 62" stroke="#BCAAA4" stroke-width="10" fill="none" stroke-linecap="round"/>
    <rect x="26" y="12" width="12" height="4" rx="1" fill="#8D6E63" transform="rotate(-5 32 14)"/>
    <rect x="27" y="26" width="10" height="4" rx="1" fill="#8D6E63" transform="rotate(3 32 28)"/>
    <rect x="26" y="40" width="12" height="4" rx="1" fill="#8D6E63" transform="rotate(-2 32 42)"/>
    <rect x="25" y="54" width="14" height="4" rx="1" fill="#8D6E63"/>
    ''', size)


def icon_fence(size: int = 48) -> str:
    """围栏"""
    return _wrap('''
    <defs>
      <linearGradient id="fc1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A1887F"/>
        <stop offset="100%" stop-color="#6D4C41"/>
      </linearGradient>
    </defs>
    <rect x="8" y="18" width="6" height="38" rx="1.5" fill="url(#fc1)"/>
    <rect x="22" y="14" width="6" height="42" rx="1.5" fill="url(#fc1)"/>
    <rect x="36" y="14" width="6" height="42" rx="1.5" fill="url(#fc1)"/>
    <rect x="50" y="18" width="6" height="38" rx="1.5" fill="url(#fc1)"/>
    <polygon points="8,18 11,10 14,18" fill="#8D6E63"/>
    <polygon points="22,14 25,6 28,14" fill="#8D6E63"/>
    <polygon points="36,14 39,6 42,14" fill="#8D6E63"/>
    <polygon points="50,18 53,10 56,18" fill="#8D6E63"/>
    <rect x="6" y="28" width="52" height="4" rx="1" fill="#795548"/>
    <rect x="6" y="40" width="52" height="4" rx="1" fill="#795548"/>
    ''', size)


# ============================================================
# 水体类
# ============================================================

def icon_stream(size: int = 48) -> str:
    """小溪"""
    return _wrap('''
    <defs>
      <linearGradient id="st1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4FC3F7"/>
        <stop offset="100%" stop-color="#0288D1"/>
      </linearGradient>
    </defs>
    <path d="M12 14 C20 18 28 14 36 22 C44 30 52 26 56 30" stroke="url(#st1)" stroke-width="8" fill="none" stroke-linecap="round"/>
    <path d="M8 32 C16 36 24 30 32 38 C40 46 48 42 56 46" stroke="#29B6F6" stroke-width="8" fill="none" stroke-linecap="round"/>
    <path d="M12 50 C20 54 28 48 36 54 C44 60 50 56 56 58" stroke="#4FC3F7" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="M16 16 C20 18 24 16 28 20" stroke="#B3E5FC" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M20 34 C24 36 28 33 32 36" stroke="#B3E5FC" stroke-width="2" fill="none" stroke-linecap="round"/>
    ''', size)


def icon_pond(size: int = 48) -> str:
    """池塘"""
    return _wrap('''
    <defs>
      <radialGradient id="pd1" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#4FC3F7"/>
        <stop offset="80%" stop-color="#0288D1"/>
        <stop offset="100%" stop-color="#01579B"/>
      </radialGradient>
    </defs>
    <ellipse cx="32" cy="38" rx="28" ry="18" fill="url(#pd1)"/>
    <ellipse cx="32" cy="36" rx="26" ry="15" fill="#29B6F6" opacity="0.4"/>
    <ellipse cx="26" cy="34" rx="10" ry="4" fill="#B3E5FC" opacity="0.3"/>
    <path d="M16 24 C16 18 20 14 24 14 C24 10 30 8 34 12 C36 8 44 8 44 16 C48 16 50 22 46 26" stroke="#81D4FA" stroke-width="1.5" fill="none" opacity="0.5"/>
    <ellipse cx="20" cy="44" rx="4" ry="2" fill="#4CAF50"/>
    <ellipse cx="18" cy="42" rx="3" ry="4" fill="#66BB6A" transform="rotate(-20 18 42)"/>
    ''', size)


def icon_waterscape(size: int = 48) -> str:
    """水景"""
    return _wrap('''
    <defs>
      <linearGradient id="ws1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#4FC3F7"/>
        <stop offset="100%" stop-color="#0277BD"/>
      </linearGradient>
    </defs>
    <ellipse cx="32" cy="52" rx="26" ry="8" fill="#0288D1"/>
    <ellipse cx="32" cy="50" rx="26" ry="6" fill="#29B6F6"/>
    <rect x="28" y="30" width="8" height="22" rx="2" fill="#78909C"/>
    <path d="M32 4 C32 4 26 16 22 24 C18 32 32 34 32 34 C32 34 46 32 42 24 C38 16 32 4 32 4Z" fill="url(#ws1)" opacity="0.7"/>
    <path d="M28 14 C24 22 20 24 16 22" stroke="#B3E5FC" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M36 14 C40 22 44 24 48 22" stroke="#B3E5FC" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="22" cy="50" rx="6" ry="2" fill="#B3E5FC" opacity="0.4"/>
    ''', size)


# ============================================================
# 氛围类
# ============================================================

def icon_sun(size: int = 48) -> str:
    """阳光"""
    return _wrap('''
    <defs>
      <radialGradient id="sn1" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#FFF9C4"/>
        <stop offset="60%" stop-color="#FFD54F"/>
        <stop offset="100%" stop-color="#FF8F00"/>
      </radialGradient>
    </defs>
    <circle cx="32" cy="32" r="12" fill="url(#sn1)"/>
    <g stroke="#FFB300" stroke-width="3" stroke-linecap="round">
      <line x1="32" y1="4" x2="32" y2="14"/>
      <line x1="32" y1="50" x2="32" y2="60"/>
      <line x1="4" y1="32" x2="14" y2="32"/>
      <line x1="50" y1="32" x2="60" y2="32"/>
      <line x1="12" y1="12" x2="19" y2="19"/>
      <line x1="45" y1="45" x2="52" y2="52"/>
      <line x1="52" y1="12" x2="45" y2="19"/>
      <line x1="19" y1="45" x2="12" y2="52"/>
    </g>
    ''', size)


def icon_fog(size: int = 48) -> str:
    """雾气"""
    return _wrap('''
    <g opacity="0.7">
      <rect x="6" y="16" width="40" height="5" rx="2.5" fill="#B0BEC5"/>
      <rect x="12" y="26" width="44" height="5" rx="2.5" fill="#90A4AE"/>
      <rect x="4" y="36" width="48" height="5" rx="2.5" fill="#78909C"/>
      <rect x="10" y="46" width="36" height="5" rx="2.5" fill="#B0BEC5"/>
    </g>
    ''', size)


def icon_leaves(size: int = 48) -> str:
    """落叶"""
    return _wrap('''
    <defs>
      <linearGradient id="lf1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FF8A65"/>
        <stop offset="100%" stop-color="#BF360C"/>
      </linearGradient>
      <linearGradient id="lf2" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFB74D"/>
        <stop offset="100%" stop-color="#E65100"/>
      </linearGradient>
    </defs>
    <path d="M18 14 C18 14 6 28 18 40 C30 28 18 14 18 14Z" fill="url(#lf1)" transform="rotate(-15 18 27)"/>
    <line x1="18" y1="16" x2="18" y2="38" stroke="#D84315" stroke-width="1" transform="rotate(-15 18 27)"/>
    <path d="M44 8 C44 8 30 24 44 38 C58 24 44 8 44 8Z" fill="url(#lf2)" transform="rotate(20 44 23)"/>
    <line x1="44" y1="10" x2="44" y2="36" stroke="#BF360C" stroke-width="1" transform="rotate(20 44 23)"/>
    <path d="M30 36 C30 36 20 48 30 56 C40 48 30 36 30 36Z" fill="#FF7043" transform="rotate(-8 30 46)"/>
    <line x1="30" y1="38" x2="30" y2="54" stroke="#D84315" stroke-width="1" transform="rotate(-8 30 46)"/>
    ''', size)


def icon_petals(size: int = 48) -> str:
    """花瓣"""
    return _wrap('''
    <defs>
      <linearGradient id="pe1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#F8BBD0"/>
        <stop offset="100%" stop-color="#EC407A"/>
      </linearGradient>
    </defs>
    <ellipse cx="20" cy="18" rx="8" ry="12" fill="url(#pe1)" transform="rotate(-30 20 18)" opacity="0.9"/>
    <ellipse cx="44" cy="22" rx="7" ry="10" fill="#F48FB1" transform="rotate(25 44 22)" opacity="0.8"/>
    <ellipse cx="16" cy="42" rx="6" ry="10" fill="#F06292" transform="rotate(-15 16 42)" opacity="0.7"/>
    <ellipse cx="42" cy="46" rx="8" ry="11" fill="url(#pe1)" transform="rotate(35 42 46)" opacity="0.85"/>
    <ellipse cx="32" cy="32" rx="6" ry="9" fill="#FCE4EC" transform="rotate(-5 32 32)" opacity="0.6"/>
    ''', size)


def icon_bird(size: int = 48) -> str:
    """鸟类"""
    return _wrap('''
    <defs>
      <linearGradient id="bd1" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ECEFF1"/>
        <stop offset="100%" stop-color="#90A4AE"/>
      </linearGradient>
    </defs>
    <ellipse cx="28" cy="32" rx="14" ry="10" fill="url(#bd1)"/>
    <circle cx="18" cy="28" r="8" fill="#CFD8DC"/>
    <circle cx="16" cy="26" r="2" fill="#263238"/>
    <polygon points="8,28 2,26 8,30" fill="#FF8F00"/>
    <path d="M38 24 C44 14 56 12 58 18 C54 14 46 18 40 26" fill="#B0BEC5"/>
    <path d="M36 38 C42 46 52 48 56 44 C50 48 42 44 38 36" fill="#90A4AE"/>
    <line x1="24" y1="42" x2="22" y2="52" stroke="#FF8F00" stroke-width="2" stroke-linecap="round"/>
    <line x1="30" y1="42" x2="28" y2="52" stroke="#FF8F00" stroke-width="2" stroke-linecap="round"/>
    ''', size)


# ============================================================
# 页面专用图标
# ============================================================

def icon_camera_lens(size: int = 48) -> str:
    """相机"""
    return _wrap('''
    <g stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.92">
      <path d="M18 23.5H26L29.5 18H38L41.8 23.5H46C50.4 23.5 53 26.1 53 30.2V43.2C53 47.3 50.4 50 46 50H18C13.6 50 11 47.3 11 43.2V30.2C11 26.1 13.6 23.5 18 23.5Z"/>
      <circle cx="32" cy="36" r="9"/>
      <path d="M46 29H46.1"/>
    </g>
    ''', size)


def icon_palette(size: int = 48) -> str:
    """调色板 - 改造"""
    return _wrap('''
    <defs>
      <linearGradient id="pa1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFF3E0"/>
        <stop offset="100%" stop-color="#FFE0B2"/>
      </linearGradient>
    </defs>
    <path d="M32 6 C14 6 4 20 4 34 C4 50 16 58 28 58 C34 58 36 52 32 50 C28 48 28 44 34 44 C58 44 60 18 32 6Z" fill="url(#pa1)" stroke="#BCAAA4" stroke-width="1"/>
    <circle cx="18" cy="22" r="5" fill="#F44336"/>
    <circle cx="14" cy="36" r="5" fill="#2196F3"/>
    <circle cx="24" cy="48" r="4" fill="#4CAF50"/>
    <circle cx="30" cy="16" r="4" fill="#FF9800"/>
    <circle cx="42" cy="20" r="4" fill="#9C27B0"/>
    ''', size)


def icon_heart_heal(size: int = 48) -> str:
    """疗愈心形"""
    return _wrap('''
    <defs>
      <linearGradient id="hh1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <path d="M32 56 C32 56 4 38 4 22 C4 12 12 6 22 6 C28 6 32 12 32 12 C32 12 36 6 42 6 C52 6 60 12 60 22 C60 38 32 56 32 56Z" fill="url(#hh1)"/>
    <path d="M32 50 C32 50 12 36 12 24 C12 16 18 12 24 12 C28 12 32 18 32 18" fill="#81C784" opacity="0.5"/>
    <path d="M28 28 L32 36 L40 20" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    ''', size)


def icon_park_scene(size: int = 48) -> str:
    """公园场景"""
    return _wrap('''
    <defs>
      <linearGradient id="pk1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81C784"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <path d="M0 42 C8 38 16 40 24 36 C32 32 40 34 48 36 C56 38 60 40 64 42 L64 64 L0 64Z" fill="url(#pk1)"/>
    <rect x="18" y="28" width="4" height="16" rx="1" fill="#5D4037"/>
    <ellipse cx="20" cy="22" rx="12" ry="10" fill="#4CAF50"/>
    <ellipse cx="16" cy="20" rx="6" ry="6" fill="#66BB6A"/>
    <rect x="44" y="32" width="3" height="12" rx="1" fill="#5D4037"/>
    <polygon points="46,14 36,32 56,32" fill="#388E3C"/>
    <circle cx="50" cy="10" r="6" fill="#FFD54F"/>
    ''', size)


def icon_city_scene(size: int = 48) -> str:
    """城市场景"""
    return _wrap('''
    <defs>
      <linearGradient id="ct1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#B0BEC5"/>
        <stop offset="100%" stop-color="#607D8B"/>
      </linearGradient>
    </defs>
    <rect x="4" y="28" width="14" height="32" rx="2" fill="url(#ct1)"/>
    <rect x="22" y="16" width="14" height="44" rx="2" fill="#78909C"/>
    <rect x="40" y="22" width="14" height="38" rx="2" fill="#90A4AE"/>
    <rect x="56" y="34" width="6" height="26" rx="1" fill="#B0BEC5"/>
    <rect x="7" y="32" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="7" y="40" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="25" y="20" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="30" y="20" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="25" y="28" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="30" y="28" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="43" y="26" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="48" y="26" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="43" y="34" width="3" height="4" rx="0.5" fill="#FFF9C4"/>
    <rect x="0" y="58" width="64" height="6" rx="1" fill="#455A64"/>
    ''', size)


def icon_sliders(size: int = 48) -> str:
    """参数调节"""
    return _wrap('''
    <rect x="10" y="16" width="44" height="4" rx="2" fill="#C8E6C9"/>
    <rect x="10" y="30" width="44" height="4" rx="2" fill="#C8E6C9"/>
    <rect x="10" y="44" width="44" height="4" rx="2" fill="#C8E6C9"/>
    <circle cx="22" cy="18" r="6" fill="#2E7D32" stroke="white" stroke-width="2"/>
    <circle cx="40" cy="32" r="6" fill="#4CAF50" stroke="white" stroke-width="2"/>
    <circle cx="30" cy="46" r="6" fill="#66BB6A" stroke="white" stroke-width="2"/>
    ''', size)


def icon_pencil(size: int = 48) -> str:
    """画笔 - 自由创作"""
    return _wrap('''
    <defs>
      <linearGradient id="pc1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4CAF50"/>
        <stop offset="100%" stop-color="#1B5E20"/>
      </linearGradient>
    </defs>
    <path d="M44 6 L54 16 L22 48 L8 54 L14 40 Z" fill="url(#pc1)"/>
    <path d="M44 6 L54 16 L50 20 L40 10 Z" fill="#1B5E20"/>
    <path d="M8 54 L14 40 L22 48 Z" fill="#FFD54F"/>
    <line x1="16" y1="42" x2="20" y2="46" stroke="#BF360C" stroke-width="1"/>
    ''', size)


def icon_sparkle(size: int = 48) -> str:
    """星光 - 智能推荐"""
    return _wrap('''
    <defs>
      <linearGradient id="sp1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFD54F"/>
        <stop offset="100%" stop-color="#FF8F00"/>
      </linearGradient>
    </defs>
    <path d="M32 2 L36 24 L58 28 L36 32 L32 54 L28 32 L6 28 L28 24Z" fill="url(#sp1)"/>
    <path d="M14 8 L16 16 L24 18 L16 20 L14 28 L12 20 L4 18 L12 16Z" fill="#FFE082" opacity="0.7"/>
    <path d="M50 40 L52 46 L58 48 L52 50 L50 56 L48 50 L42 48 L48 46Z" fill="#FFE082" opacity="0.7"/>
    ''', size)


# ============================================================
# 通用/UI 图标
# ============================================================

def icon_bulb(size: int = 48) -> str:
    """灯泡 - 理论/建议"""
    return _wrap('''
    <defs>
      <linearGradient id="bl1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFF9C4"/>
        <stop offset="100%" stop-color="#FFD54F"/>
      </linearGradient>
      <radialGradient id="bl2" cx="0.5" cy="0.3" r="0.6">
        <stop offset="0%" stop-color="#FFFDE7" stop-opacity="0.7"/>
        <stop offset="100%" stop-color="#FFD54F" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="32" cy="24" r="18" fill="url(#bl2)"/>
    <path d="M32 6 C20 6 12 15 12 26 C12 34 18 38 22 42 L22 48 L42 48 L42 42 C46 38 52 34 52 26 C52 15 44 6 32 6Z" fill="url(#bl1)" stroke="#F9A825" stroke-width="1.5"/>
    <rect x="24" y="48" width="16" height="4" rx="1" fill="#FFB300"/>
    <rect x="26" y="52" width="12" height="3" rx="1" fill="#FFA000"/>
    <rect x="28" y="55" width="8" height="3" rx="1.5" fill="#FF8F00"/>
    <line x1="32" y1="16" x2="32" y2="34" stroke="#FF8F00" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
    <line x1="24" y1="26" x2="40" y2="26" stroke="#FF8F00" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
    ''', size)


def icon_microscope(size: int = 48) -> str:
    """显微镜 - 研究"""
    return _wrap('''
    <defs>
      <linearGradient id="ms1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#78909C"/>
        <stop offset="100%" stop-color="#37474F"/>
      </linearGradient>
    </defs>
    <rect x="16" y="54" width="32" height="5" rx="2" fill="#455A64"/>
    <rect x="28" y="18" width="6" height="36" rx="2" fill="url(#ms1)"/>
    <rect x="22" y="44" width="18" height="4" rx="1" fill="#546E7A"/>
    <circle cx="31" cy="14" r="10" fill="none" stroke="#546E7A" stroke-width="3"/>
    <circle cx="31" cy="14" r="6" fill="#81D4FA" opacity="0.5"/>
    <path d="M38 8 L46 4" stroke="#78909C" stroke-width="3" stroke-linecap="round"/>
    <path d="M20 30 L14 30 L14 40 L20 40" stroke="#607D8B" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    ''', size)


def icon_clipboard(size: int = 48) -> str:
    """剪贴板 - 记录"""
    return _wrap('''
    <defs>
      <linearGradient id="cb1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#4CAF50"/>
      </linearGradient>
    </defs>
    <rect x="12" y="10" width="40" height="48" rx="5" fill="url(#cb1)"/>
    <rect x="14" y="12" width="36" height="44" rx="4" fill="white" opacity="0.9"/>
    <rect x="24" y="4" width="16" height="12" rx="3" fill="#388E3C"/>
    <circle cx="32" cy="10" r="3" fill="#C8E6C9"/>
    <rect x="20" y="22" width="24" height="3" rx="1" fill="#81C784"/>
    <rect x="20" y="30" width="20" height="3" rx="1" fill="#A5D6A7"/>
    <rect x="20" y="38" width="22" height="3" rx="1" fill="#81C784"/>
    <rect x="20" y="46" width="16" height="3" rx="1" fill="#A5D6A7"/>
    ''', size)


def icon_brain(size: int = 48) -> str:
    """大脑 - 心理"""
    return _wrap('''
    <defs>
      <linearGradient id="br1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#CE93D8"/>
        <stop offset="100%" stop-color="#7B1FA2"/>
      </linearGradient>
    </defs>
    <path d="M32 8 C24 8 16 14 14 22 C12 28 14 34 18 38 C16 42 18 48 24 50 C26 54 30 56 32 56 C34 56 38 54 40 50 C46 48 48 42 46 38 C50 34 52 28 50 22 C48 14 40 8 32 8Z" fill="url(#br1)"/>
    <path d="M32 12 C32 12 32 56 32 56" stroke="#E1BEE7" stroke-width="1.5" opacity="0.6"/>
    <path d="M20 20 C24 22 28 18 32 22 C36 18 40 22 44 20" stroke="#E1BEE7" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M18 30 C22 32 26 28 32 32 C38 28 42 32 46 30" stroke="#E1BEE7" stroke-width="1.5" fill="none" opacity="0.5"/>
    <path d="M20 40 C24 42 28 38 32 42 C36 38 40 42 44 40" stroke="#E1BEE7" stroke-width="1.5" fill="none" opacity="0.5"/>
    <circle cx="24" cy="26" r="2" fill="#F3E5F5" opacity="0.6"/>
    <circle cx="40" cy="34" r="2" fill="#F3E5F5" opacity="0.6"/>
    ''', size)


def icon_book(size: int = 48) -> str:
    """书本 - 介绍"""
    return _wrap('''
    <defs>
      <linearGradient id="bk1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <path d="M10 10 L10 52 C10 52 20 48 32 52 L32 14 C20 10 10 10 10 10Z" fill="url(#bk1)"/>
    <path d="M54 10 L54 52 C54 52 44 48 32 52 L32 14 C44 10 54 10 54 10Z" fill="#43A047"/>
    <path d="M32 14 C20 10 10 10 10 10 L10 12 C10 12 20 12 32 16Z" fill="#1B5E20" opacity="0.3"/>
    <line x1="16" y1="22" x2="28" y2="26" stroke="white" stroke-width="1.5" opacity="0.5" stroke-linecap="round"/>
    <line x1="16" y1="30" x2="28" y2="34" stroke="white" stroke-width="1.5" opacity="0.5" stroke-linecap="round"/>
    <line x1="16" y1="38" x2="26" y2="42" stroke="white" stroke-width="1.5" opacity="0.5" stroke-linecap="round"/>
    ''', size)


def icon_flask(size: int = 48) -> str:
    """烧瓶 - 实验"""
    return _wrap('''
    <defs>
      <linearGradient id="fk1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81D4FA"/>
        <stop offset="100%" stop-color="#0288D1"/>
      </linearGradient>
    </defs>
    <rect x="24" y="4" width="16" height="20" rx="2" fill="#B0BEC5"/>
    <path d="M24 24 L12 48 C10 52 12 58 18 58 L46 58 C52 58 54 52 52 48 L40 24Z" fill="#ECEFF1" stroke="#90A4AE" stroke-width="1.5"/>
    <path d="M16 44 L48 44 L52 48 C54 52 52 58 46 58 L18 58 C12 58 10 52 12 48Z" fill="url(#fk1)" opacity="0.7"/>
    <circle cx="28" cy="50" r="3" fill="#4FC3F7" opacity="0.6"/>
    <circle cx="38" cy="52" r="2" fill="#B3E5FC" opacity="0.5"/>
    <rect x="22" y="2" width="20" height="4" rx="1" fill="#78909C"/>
    ''', size)


def icon_meditation(size: int = 48) -> str:
    """冥想 - 禅意"""
    return _wrap('''
    <defs>
      <linearGradient id="md1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
      <radialGradient id="md2" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#C8E6C9" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="#66BB6A" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="32" cy="32" r="26" fill="url(#md2)"/>
    <circle cx="32" cy="16" r="7" fill="url(#md1)"/>
    <path d="M22 28 C22 28 20 40 18 46 C16 50 24 52 32 52 C40 52 48 50 46 46 C44 40 42 28 42 28" fill="url(#md1)"/>
    <path d="M18 38 C14 36 10 38 12 42" stroke="#4CAF50" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M46 38 C50 36 54 38 52 42" stroke="#4CAF50" stroke-width="2" fill="none" stroke-linecap="round"/>
    <circle cx="28" cy="15" r="1" fill="#1B5E20"/>
    <circle cx="36" cy="15" r="1" fill="#1B5E20"/>
    <path d="M30 19 C31 20 33 20 34 19" stroke="#1B5E20" stroke-width="1" fill="none"/>
    ''', size)


def icon_books(size: int = 48) -> str:
    """书堆 - 科学文献"""
    return _wrap('''
    <defs>
      <linearGradient id="bs2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <rect x="8" y="38" width="48" height="10" rx="2" fill="url(#bs2)" transform="rotate(-3 32 43)"/>
    <rect x="10" y="26" width="44" height="10" rx="2" fill="#43A047" transform="rotate(2 32 31)"/>
    <rect x="12" y="14" width="40" height="10" rx="2" fill="#81C784" transform="rotate(-1 32 19)"/>
    <rect x="10" y="38" width="4" height="10" rx="1" fill="#1B5E20" transform="rotate(-3 12 43)"/>
    <rect x="12" y="26" width="4" height="10" rx="1" fill="#2E7D32" transform="rotate(2 14 31)"/>
    <rect x="14" y="14" width="4" height="10" rx="1" fill="#4CAF50" transform="rotate(-1 16 19)"/>
    <line x1="24" y1="42" x2="44" y2="41" stroke="white" stroke-width="1" opacity="0.4" stroke-linecap="round"/>
    <line x1="22" y1="30" x2="42" y2="31" stroke="white" stroke-width="1" opacity="0.4" stroke-linecap="round"/>
    <line x1="24" y1="18" x2="40" y2="18" stroke="white" stroke-width="1" opacity="0.4" stroke-linecap="round"/>
    ''', size)


def icon_save(size: int = 48) -> str:
    """保存/下载"""
    return _wrap('''
    <defs>
      <linearGradient id="sv1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <rect x="8" y="8" width="48" height="48" rx="6" fill="url(#sv1)"/>
    <rect x="16" y="8" width="28" height="20" rx="2" fill="#1B5E20" opacity="0.4"/>
    <rect x="32" y="10" width="8" height="14" rx="1" fill="#A5D6A7"/>
    <rect x="16" y="34" width="32" height="18" rx="3" fill="white" opacity="0.9"/>
    <rect x="22" y="40" width="20" height="3" rx="1" fill="#81C784"/>
    <rect x="22" y="46" width="14" height="2" rx="1" fill="#A5D6A7"/>
    ''', size)


def icon_construction(size: int = 48) -> str:
    """建筑/人造元素"""
    return _wrap('''
    <defs>
      <linearGradient id="cn1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFB74D"/>
        <stop offset="100%" stop-color="#E65100"/>
      </linearGradient>
    </defs>
    <rect x="6" y="30" width="52" height="26" rx="3" fill="#78909C"/>
    <rect x="10" y="34" width="12" height="10" rx="1" fill="#B0BEC5"/>
    <rect x="26" y="34" width="12" height="10" rx="1" fill="#B0BEC5"/>
    <rect x="42" y="34" width="12" height="10" rx="1" fill="#B0BEC5"/>
    <rect x="10" y="48" width="12" height="6" rx="1" fill="#90A4AE"/>
    <rect x="26" y="48" width="12" height="6" rx="1" fill="#90A4AE"/>
    <polygon points="32,4 6,30 58,30" fill="url(#cn1)"/>
    <polygon points="32,10 14,28 50,28" fill="#FF9800" opacity="0.5"/>
    ''', size)


def icon_people(size: int = 48) -> str:
    """人群 - 环境活力"""
    return _wrap('''
    <defs>
      <linearGradient id="pp1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#90A4AE"/>
        <stop offset="100%" stop-color="#546E7A"/>
      </linearGradient>
    </defs>
    <circle cx="20" cy="16" r="7" fill="url(#pp1)"/>
    <path d="M8 38 C8 28 14 24 20 24 C26 24 32 28 32 38Z" fill="#78909C"/>
    <circle cx="44" cy="16" r="7" fill="#607D8B"/>
    <path d="M32 38 C32 28 38 24 44 24 C50 24 56 28 56 38Z" fill="#546E7A"/>
    <circle cx="32" cy="22" r="8" fill="#B0BEC5"/>
    <path d="M18 44 C18 32 24 28 32 28 C40 28 46 32 46 44Z" fill="#90A4AE"/>
    ''', size)


def icon_chat(size: int = 48) -> str:
    """对话气泡 - 反馈"""
    return _wrap('''
    <defs>
      <linearGradient id="ch1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#4CAF50"/>
      </linearGradient>
    </defs>
    <path d="M8 10 L56 10 C58 10 60 12 60 14 L60 38 C60 40 58 42 56 42 L20 42 L12 54 L12 42 L8 42 C6 42 4 40 4 38 L4 14 C4 12 6 10 8 10Z" fill="url(#ch1)"/>
    <rect x="14" y="20" width="28" height="3" rx="1.5" fill="white" opacity="0.6"/>
    <rect x="14" y="28" width="20" height="3" rx="1.5" fill="white" opacity="0.6"/>
    <rect x="14" y="36" width="24" height="2" rx="1" fill="white" opacity="0.4"/>
    ''', size)


def icon_star(size: int = 48) -> str:
    """星星 - 满意度"""
    return _wrap('''
    <defs>
      <linearGradient id="st2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FFD54F"/>
        <stop offset="100%" stop-color="#FF8F00"/>
      </linearGradient>
    </defs>
    <path d="M32 4 L38 24 L58 24 L42 36 L48 56 L32 44 L16 56 L22 36 L6 24 L26 24Z" fill="url(#st2)"/>
    <path d="M32 10 L36 24 L50 24 L38 33 L43 48 L32 40 L21 48 L26 33 L14 24 L28 24Z" fill="#FFE082" opacity="0.5"/>
    ''', size)


def icon_leaf_hero(size: int = 48) -> str:
    """大叶子 - 首页hero用"""
    return _wrap('''
    <defs>
      <linearGradient id="lh1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#81C784"/>
        <stop offset="100%" stop-color="#1B5E20"/>
      </linearGradient>
      <linearGradient id="lh2" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <path d="M32 4 C32 4 4 16 4 40 C4 56 20 60 32 60 C44 60 60 56 60 40 C60 16 32 4 32 4Z" fill="url(#lh1)"/>
    <path d="M32 4 C32 4 12 20 8 40 C16 36 24 28 32 16 C40 28 48 36 56 40 C52 20 32 4 32 4Z" fill="url(#lh2)" opacity="0.5"/>
    <path d="M32 12 C32 12 32 52 32 56" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
    <path d="M32 24 C28 20 20 22 16 28" stroke="#1B5E20" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.3"/>
    <path d="M32 32 C36 28 44 30 48 36" stroke="#1B5E20" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.3"/>
    <path d="M32 40 C28 36 22 38 18 44" stroke="#1B5E20" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.3"/>
    ''', size)


# ============================================================
# 扩充元素图标
# ============================================================

def icon_palm(size: int = 48) -> str:
    """棕榈树"""
    return _wrap('''
    <defs>
      <linearGradient id="pm1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#66BB6A"/>
        <stop offset="100%" stop-color="#1B5E20"/>
      </linearGradient>
      <linearGradient id="pm2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#8D6E63"/>
        <stop offset="100%" stop-color="#4E342E"/>
      </linearGradient>
    </defs>
    <path d="M30 58 C30 58 28 38 30 22 C32 10 34 22 34 58" fill="url(#pm2)" stroke="#6D4C41" stroke-width="1"/>
    <path d="M32 22 C32 22 10 20 6 10 C14 8 24 16 32 22Z" fill="url(#pm1)"/>
    <path d="M32 22 C32 22 54 18 58 8 C50 6 40 14 32 22Z" fill="#4CAF50"/>
    <path d="M32 20 C32 20 16 28 8 22 C12 14 24 16 32 20Z" fill="#81C784"/>
    <path d="M32 20 C32 20 48 28 56 22 C52 14 40 16 32 20Z" fill="#66BB6A"/>
    <path d="M32 24 C32 24 20 36 14 32 C16 24 26 22 32 24Z" fill="#A5D6A7" opacity="0.7"/>
    <ellipse cx="31" cy="59" rx="6" ry="3" fill="#5D4037" opacity="0.3"/>
    ''', size)


def icon_sakura(size: int = 48) -> str:
    """樱花树"""
    return _wrap('''
    <defs>
      <linearGradient id="sk1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#F8BBD0"/>
        <stop offset="100%" stop-color="#F06292"/>
      </linearGradient>
      <linearGradient id="sk2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#8D6E63"/>
        <stop offset="100%" stop-color="#4E342E"/>
      </linearGradient>
    </defs>
    <rect x="29" y="36" width="6" height="22" rx="2" fill="url(#sk2)"/>
    <ellipse cx="32" cy="28" rx="22" ry="18" fill="url(#sk1)"/>
    <ellipse cx="22" cy="24" rx="13" ry="11" fill="#F48FB1" opacity="0.7"/>
    <ellipse cx="40" cy="22" rx="11" ry="10" fill="#FCE4EC" opacity="0.6"/>
    <ellipse cx="32" cy="16" rx="10" ry="8" fill="#F8BBD0" opacity="0.5"/>
    <circle cx="20" cy="20" r="3" fill="#FFECB3" opacity="0.8"/>
    <circle cx="36" cy="16" r="2" fill="#FFECB3" opacity="0.8"/>
    <circle cx="28" cy="30" r="2.5" fill="#FFCDD2" opacity="0.7"/>
    ''', size)


def icon_reed(size: int = 48) -> str:
    """芦苇"""
    return _wrap('''
    <defs>
      <linearGradient id="rd1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#388E3C"/>
      </linearGradient>
      <linearGradient id="rd2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#D7CCC8"/>
        <stop offset="100%" stop-color="#8D6E63"/>
      </linearGradient>
    </defs>
    <rect x="14" y="8" width="3" height="50" rx="1.5" fill="url(#rd1)"/>
    <ellipse cx="15" cy="10" rx="4" ry="10" fill="url(#rd2)" opacity="0.85"/>
    <rect x="28" y="14" width="3" height="46" rx="1.5" fill="#81C784"/>
    <ellipse cx="29" cy="16" rx="3.5" ry="9" fill="#A1887F" opacity="0.85"/>
    <rect x="42" y="6" width="3" height="52" rx="1.5" fill="url(#rd1)"/>
    <ellipse cx="43" cy="8" rx="4" ry="10" fill="url(#rd2)" opacity="0.85"/>
    <path d="M14 30 C20 28 26 32 29 30" stroke="#66BB6A" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <path d="M29 24 C34 22 38 26 43 24" stroke="#81C784" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    ''', size)


def icon_cactus(size: int = 48) -> str:
    """仙人掌"""
    return _wrap('''
    <defs>
      <linearGradient id="ca1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81C784"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <rect x="26" y="14" width="12" height="44" rx="6" fill="url(#ca1)"/>
    <path d="M16 32 C16 32 16 22 22 22 L26 22 L26 32" fill="#4CAF50"/>
    <path d="M16 32 C12 30 10 24 14 20" stroke="#388E3C" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M48 36 C48 36 48 26 42 26 L38 26 L38 36" fill="#66BB6A"/>
    <path d="M48 36 C52 34 54 28 50 24" stroke="#388E3C" stroke-width="3" fill="none" stroke-linecap="round"/>
    <ellipse cx="32" cy="14" rx="5" ry="4" fill="#F48FB1"/>
    <circle cx="30" cy="12" r="2" fill="#F06292"/>
    <circle cx="34" cy="12" r="2" fill="#F06292"/>
    <rect x="26" y="56" width="12" height="4" rx="2" fill="#5D4037"/>
    ''', size)


def icon_moss(size: int = 48) -> str:
    """苔藓"""
    return _wrap('''
    <defs>
      <radialGradient id="mo1" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </radialGradient>
    </defs>
    <ellipse cx="32" cy="46" rx="28" ry="12" fill="#388E3C" opacity="0.4"/>
    <ellipse cx="24" cy="44" rx="18" ry="10" fill="url(#mo1)"/>
    <ellipse cx="40" cy="44" rx="16" ry="9" fill="#66BB6A"/>
    <ellipse cx="32" cy="40" rx="20" ry="11" fill="url(#mo1)"/>
    <circle cx="20" cy="38" r="5" fill="#81C784"/>
    <circle cx="32" cy="34" r="6" fill="#A5D6A7"/>
    <circle cx="44" cy="38" r="5" fill="#81C784"/>
    <circle cx="28" cy="30" r="4" fill="#C8E6C9"/>
    <circle cx="38" cy="32" r="3.5" fill="#A5D6A7"/>
    ''', size)


def icon_swing(size: int = 48) -> str:
    """秋千"""
    return _wrap('''
    <defs>
      <linearGradient id="sw1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A1887F"/>
        <stop offset="100%" stop-color="#5D4037"/>
      </linearGradient>
    </defs>
    <rect x="8" y="6" width="5" height="46" rx="2" fill="url(#sw1)" transform="rotate(-8 10 29)"/>
    <rect x="51" y="6" width="5" height="46" rx="2" fill="url(#sw1)" transform="rotate(8 54 29)"/>
    <rect x="6" y="6" width="52" height="5" rx="2" fill="#6D4C41"/>
    <line x1="20" y1="10" x2="18" y2="36" stroke="#8D6E63" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="44" y1="10" x2="46" y2="36" stroke="#8D6E63" stroke-width="2.5" stroke-linecap="round"/>
    <rect x="14" y="34" width="36" height="6" rx="3" fill="#A1887F"/>
    <rect x="16" y="36" width="32" height="3" rx="1.5" fill="#BCAAA4"/>
    ''', size)


def icon_pavilion(size: int = 48) -> str:
    """凉亭"""
    return _wrap('''
    <defs>
      <linearGradient id="pv1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FF8A65"/>
        <stop offset="100%" stop-color="#BF360C"/>
      </linearGradient>
      <linearGradient id="pv2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A1887F"/>
        <stop offset="100%" stop-color="#5D4037"/>
      </linearGradient>
    </defs>
    <polygon points="32,4 4,26 60,26" fill="url(#pv1)"/>
    <polygon points="32,10 8,28 56,28" fill="#FF7043" opacity="0.4"/>
    <rect x="6" y="24" width="52" height="4" rx="1" fill="#E64A19"/>
    <rect x="10" y="28" width="6" height="28" rx="1.5" fill="url(#pv2)"/>
    <rect x="48" y="28" width="6" height="28" rx="1.5" fill="url(#pv2)"/>
    <rect x="24" y="28" width="6" height="28" rx="1.5" fill="#8D6E63" opacity="0.6"/>
    <rect x="34" y="28" width="6" height="28" rx="1.5" fill="#8D6E63" opacity="0.6"/>
    <rect x="8" y="54" width="48" height="4" rx="1" fill="#6D4C41"/>
    ''', size)


def icon_boardwalk(size: int = 48) -> str:
    """木栈道"""
    return _wrap('''
    <defs>
      <linearGradient id="bw1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#BCAAA4"/>
        <stop offset="100%" stop-color="#795548"/>
      </linearGradient>
    </defs>
    <rect x="4" y="24" width="56" height="8" rx="2" fill="url(#bw1)"/>
    <rect x="4" y="34" width="56" height="8" rx="2" fill="#A1887F"/>
    <rect x="4" y="44" width="56" height="6" rx="2" fill="#8D6E63"/>
    <rect x="10" y="22" width="4" height="32" rx="1" fill="#6D4C41"/>
    <rect x="24" y="22" width="4" height="32" rx="1" fill="#6D4C41"/>
    <rect x="38" y="22" width="4" height="32" rx="1" fill="#6D4C41"/>
    <rect x="52" y="22" width="4" height="32" rx="1" fill="#6D4C41"/>
    <path d="M4 24 C16 14 32 10 60 24" stroke="#A1887F" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>
    ''', size)


def icon_windmill(size: int = 48) -> str:
    """风车"""
    return _wrap('''
    <defs>
      <linearGradient id="wm1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#90CAF9"/>
        <stop offset="100%" stop-color="#1565C0"/>
      </linearGradient>
    </defs>
    <rect x="30" y="32" width="4" height="28" rx="1.5" fill="#78909C"/>
    <ellipse cx="32" cy="62" rx="8" ry="3" fill="#546E7A"/>
    <circle cx="32" cy="30" r="4" fill="#546E7A"/>
    <path d="M32 26 C32 26 28 14 20 8 C24 18 30 24 32 26Z" fill="url(#wm1)" opacity="0.9"/>
    <path d="M36 30 C36 30 48 28 56 22 C46 24 38 28 36 30Z" fill="#64B5F6" opacity="0.9"/>
    <path d="M32 34 C32 34 36 46 44 52 C40 42 34 36 32 34Z" fill="#42A5F5" opacity="0.9"/>
    <path d="M28 30 C28 30 16 32 8 38 C18 36 26 32 28 30Z" fill="#90CAF9" opacity="0.9"/>
    <circle cx="32" cy="30" r="3" fill="white"/>
    ''', size)


def icon_trashcan(size: int = 48) -> str:
    """垃圾桶"""
    return _wrap('''
    <defs>
      <linearGradient id="tc1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#80CBC4"/>
        <stop offset="100%" stop-color="#00695C"/>
      </linearGradient>
    </defs>
    <rect x="16" y="18" width="32" height="38" rx="3" fill="url(#tc1)"/>
    <rect x="14" y="14" width="36" height="6" rx="2" fill="#00897B"/>
    <rect x="22" y="8" width="20" height="8" rx="2" fill="#4DB6AC"/>
    <rect x="26" y="10" width="12" height="4" rx="1" fill="#80CBC4"/>
    <rect x="24" y="22" width="3" height="26" rx="1.5" fill="#004D40" opacity="0.3"/>
    <rect x="30" y="22" width="3" height="26" rx="1.5" fill="#004D40" opacity="0.3"/>
    <rect x="36" y="22" width="3" height="26" rx="1.5" fill="#004D40" opacity="0.3"/>
    ''', size)


def icon_waterfall(size: int = 48) -> str:
    """瀑布"""
    return _wrap('''
    <defs>
      <linearGradient id="wf1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#B3E5FC"/>
        <stop offset="100%" stop-color="#0288D1"/>
      </linearGradient>
      <linearGradient id="wf2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#78909C"/>
        <stop offset="100%" stop-color="#37474F"/>
      </linearGradient>
    </defs>
    <path d="M4 14 L28 14 L28 6 L36 6 L36 14 L60 14 L60 22 L4 22Z" fill="url(#wf2)"/>
    <path d="M14 22 C14 22 12 38 10 50 C14 50 16 40 18 28 C20 40 22 50 24 50 C26 40 26 28 28 22Z" fill="url(#wf1)"/>
    <path d="M28 22 C28 22 28 34 30 46 C32 46 32 34 34 22Z" fill="#81D4FA"/>
    <path d="M34 22 C34 22 36 36 38 50 C40 50 42 38 42 22Z" fill="url(#wf1)" opacity="0.9"/>
    <ellipse cx="28" cy="52" rx="24" ry="8" fill="#4FC3F7" opacity="0.5"/>
    <ellipse cx="28" cy="50" rx="20" ry="5" fill="#B3E5FC" opacity="0.4"/>
    ''', size)


def icon_lotus(size: int = 48) -> str:
    """荷花"""
    return _wrap('''
    <defs>
      <linearGradient id="lt1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#F8BBD0"/>
        <stop offset="100%" stop-color="#E91E63"/>
      </linearGradient>
      <linearGradient id="lt2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#2E7D32"/>
      </linearGradient>
    </defs>
    <ellipse cx="20" cy="52" rx="16" ry="8" fill="url(#lt2)"/>
    <ellipse cx="44" cy="54" rx="12" ry="6" fill="#4CAF50"/>
    <ellipse cx="32" cy="38" rx="7" ry="6" fill="#FFF9C4"/>
    <path d="M32 38 C32 38 22 44 20 36 C22 28 30 34 32 38Z" fill="url(#lt1)"/>
    <path d="M32 38 C32 38 42 44 44 36 C42 28 34 34 32 38Z" fill="#F48FB1"/>
    <path d="M32 38 C32 38 24 32 26 22 C30 18 32 30 32 38Z" fill="url(#lt1)"/>
    <path d="M32 38 C32 38 40 32 38 22 C34 18 32 30 32 38Z" fill="#F48FB1"/>
    <path d="M32 38 C32 38 28 28 32 20 C36 28 32 38 32 38Z" fill="#FCE4EC"/>
    <circle cx="32" cy="37" r="4" fill="#FFF176"/>
    ''', size)


def icon_seagrass(size: int = 48) -> str:
    """水草"""
    return _wrap('''
    <defs>
      <linearGradient id="sg1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#80CBC4"/>
        <stop offset="100%" stop-color="#00695C"/>
      </linearGradient>
    </defs>
    <path d="M16 58 C16 58 14 44 18 34 C20 26 14 18 18 10 C22 18 20 28 18 36 C20 46 20 58 16 58Z" fill="url(#sg1)"/>
    <path d="M32 58 C32 58 28 44 34 32 C38 24 32 14 36 6 C40 16 36 26 34 34 C32 44 34 58 32 58Z" fill="#4DB6AC"/>
    <path d="M48 58 C48 58 46 46 50 36 C52 28 48 18 50 8 C54 16 52 26 50 38 C50 48 50 58 48 58Z" fill="url(#sg1)" opacity="0.9"/>
    <ellipse cx="18" cy="10" rx="5" ry="3" fill="#80CBC4" transform="rotate(-20 18 10)"/>
    <ellipse cx="36" cy="6" rx="4" ry="3" fill="#4DB6AC" transform="rotate(15 36 6)"/>
    <ellipse cx="50" cy="8" rx="4" ry="3" fill="#80CBC4" transform="rotate(-10 50 8)"/>
    ''', size)


def icon_rock(size: int = 48) -> str:
    """礁石"""
    return _wrap('''
    <defs>
      <linearGradient id="rk1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#90A4AE"/>
        <stop offset="100%" stop-color="#37474F"/>
      </linearGradient>
    </defs>
    <ellipse cx="32" cy="52" rx="28" ry="10" fill="#455A64" opacity="0.5"/>
    <path d="M8 52 C8 38 14 22 26 18 C32 16 36 20 40 18 C50 16 56 32 56 48Z" fill="url(#rk1)"/>
    <path d="M12 48 C10 36 16 24 28 20" stroke="#607D8B" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.4"/>
    <path d="M36 18 C44 20 52 32 54 44" stroke="#546E7A" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.4"/>
    <path d="M8 52 C14 44 22 42 30 46 C38 50 48 50 56 48" stroke="#78909C" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>
    <ellipse cx="22" cy="30" rx="6" ry="4" fill="#546E7A" opacity="0.3" transform="rotate(-20 22 30)"/>
    ''', size)


def icon_rainbow(size: int = 48) -> str:
    """彩虹"""
    return _wrap('''
    <path d="M4 44 C4 22 16 10 32 10 C48 10 60 22 60 44" stroke="#F44336" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M8 44 C8 24 18 14 32 14 C46 14 56 24 56 44" stroke="#FF9800" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M12 44 C12 26 20 18 32 18 C44 18 52 26 52 44" stroke="#FFEB3B" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M16 44 C16 28 22 22 32 22 C42 22 48 28 48 44" stroke="#4CAF50" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M20 44 C20 30 24 26 32 26 C40 26 44 30 44 44" stroke="#2196F3" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M24 44 C24 32 26 30 32 30 C38 30 40 32 40 44" stroke="#9C27B0" stroke-width="3" fill="none" stroke-linecap="round"/>
    <ellipse cx="8" cy="46" rx="10" ry="6" fill="white" opacity="0.7"/>
    <ellipse cx="56" cy="46" rx="10" ry="6" fill="white" opacity="0.7"/>
    ''', size)


def icon_firefly(size: int = 48) -> str:
    """萤火虫"""
    return _wrap('''
    <defs>
      <radialGradient id="ff1" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#F9FBE7" stop-opacity="1"/>
        <stop offset="60%" stop-color="#CCFF90" stop-opacity="0.7"/>
        <stop offset="100%" stop-color="#76FF03" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="ff2" cx="0.5" cy="0.5" r="0.5">
        <stop offset="0%" stop-color="#FFFDE7" stop-opacity="1"/>
        <stop offset="50%" stop-color="#FFD740" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="#FFD740" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="18" cy="18" r="14" fill="url(#ff1)"/>
    <circle cx="18" cy="18" r="4" fill="#76FF03" opacity="0.9"/>
    <ellipse cx="18" cy="20" rx="3" ry="5" fill="#33691E"/>
    <line x1="14" y1="18" x2="8" y2="14" stroke="#558B2F" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="22" y1="18" x2="28" y2="14" stroke="#558B2F" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="44" cy="38" r="10" fill="url(#ff2)"/>
    <circle cx="44" cy="38" r="3" fill="#FFD740" opacity="0.9"/>
    <ellipse cx="44" cy="40" rx="2.5" ry="4" fill="#F57F17"/>
    <line x1="41" y1="38" x2="36" y2="34" stroke="#F9A825" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="47" y1="38" x2="52" y2="34" stroke="#F9A825" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="32" cy="52" r="5" fill="url(#ff1)" opacity="0.5"/>
    ''', size)


def icon_butterfly(size: int = 48) -> str:
    """蝴蝶"""
    return _wrap('''
    <defs>
      <linearGradient id="bt1" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FF8A65"/>
        <stop offset="100%" stop-color="#FF3D00"/>
      </linearGradient>
      <linearGradient id="bt2" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#FFD54F"/>
        <stop offset="100%" stop-color="#FF6F00"/>
      </linearGradient>
    </defs>
    <path d="M32 28 C26 20 8 10 8 24 C8 34 22 32 32 28Z" fill="url(#bt1)"/>
    <path d="M32 28 C38 20 56 10 56 24 C56 34 42 32 32 28Z" fill="url(#bt1)"/>
    <path d="M32 32 C24 36 10 46 14 54 C20 56 28 44 32 32Z" fill="url(#bt2)" opacity="0.9"/>
    <path d="M32 32 C40 36 54 46 50 54 C44 56 36 44 32 32Z" fill="url(#bt2)" opacity="0.9"/>
    <circle cx="26" cy="20" r="4" fill="black" opacity="0.15"/>
    <circle cx="38" cy="20" r="4" fill="black" opacity="0.15"/>
    <path d="M32 16 C32 16 32 50 32 50" stroke="#3E2723" stroke-width="2" stroke-linecap="round"/>
    <path d="M30 14 C28 8 24 6 22 8" stroke="#4E342E" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <path d="M34 14 C36 8 40 6 42 8" stroke="#4E342E" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    ''', size)


def icon_moonlight(size: int = 48) -> str:
    """月光"""
    return _wrap('''
    <defs>
      <radialGradient id="ml1" cx="0.4" cy="0.4" r="0.6">
        <stop offset="0%" stop-color="#FFFDE7"/>
        <stop offset="100%" stop-color="#F9A825"/>
      </radialGradient>
    </defs>
    <path d="M44 32 C44 46 34 56 22 56 C16 56 10 54 6 50 C12 52 18 52 24 50 C36 46 42 36 38 24 C36 18 32 14 28 12 C36 12 44 20 44 32Z" fill="url(#ml1)"/>
    <circle cx="20" cy="14" r="2" fill="#FFF9C4" opacity="0.9"/>
    <circle cx="52" cy="20" r="2.5" fill="#FFF9C4" opacity="0.7"/>
    <circle cx="10" cy="32" r="1.5" fill="#FFF9C4" opacity="0.8"/>
    <circle cx="56" cy="42" r="2" fill="#FFF9C4" opacity="0.6"/>
    <circle cx="36" cy="8" r="1.5" fill="#FFF9C4" opacity="0.7"/>
    <circle cx="8" cy="52" r="1" fill="#FFF9C4" opacity="0.5"/>
    <path d="M6 44 C14 40 22 42 28 48" stroke="#FFF9C4" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.4"/>
    ''', size)


def icon_cabin(size: int = 48) -> str:
    """木屋"""
    return _wrap('''
    <defs>
      <linearGradient id="cb1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#BF360C"/>
        <stop offset="100%" stop-color="#7F2700"/>
      </linearGradient>
      <linearGradient id="cb2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#BCAAA4"/>
        <stop offset="100%" stop-color="#6D4C41"/>
      </linearGradient>
    </defs>
    <polygon points="32,6 6,28 58,28" fill="url(#cb1)"/>
    <rect x="10" y="26" width="44" height="32" rx="2" fill="url(#cb2)"/>
    <rect x="14" y="30" width="10" height="10" rx="1" fill="#90CAF9" opacity="0.8"/>
    <rect x="40" y="30" width="10" height="10" rx="1" fill="#90CAF9" opacity="0.8"/>
    <rect x="25" y="36" width="14" height="22" rx="1" fill="#5D4037"/>
    <rect x="28" y="38" width="4" height="10" rx="0.5" fill="#BCAAA4" opacity="0.6"/>
    <rect x="33" y="38" width="4" height="10" rx="0.5" fill="#BCAAA4" opacity="0.6"/>
    <circle cx="26" cy="47" r="1.5" fill="#FFB300"/>
    <path d="M18 6 C18 6 20 0 22 4" stroke="#546E7A" stroke-width="2" stroke-linecap="round" fill="none"/>
    <path d="M20 4 C22 2 24 4 22 6" stroke="#607D8B" stroke-width="1.5" fill="none"/>
    ''', size)


def icon_stone_wall(size: int = 48) -> str:
    """石墙"""
    return _wrap('''
    <defs>
      <linearGradient id="sw2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#90A4AE"/>
        <stop offset="100%" stop-color="#455A64"/>
      </linearGradient>
    </defs>
    <rect x="4" y="14" width="56" height="36" rx="3" fill="#546E7A"/>
    <rect x="6" y="16" width="24" height="10" rx="2" fill="url(#sw2)"/>
    <rect x="32" y="16" width="26" height="10" rx="2" fill="#607D8B"/>
    <rect x="4" y="28" width="16" height="10" rx="2" fill="#607D8B"/>
    <rect x="22" y="28" width="24" height="10" rx="2" fill="url(#sw2)"/>
    <rect x="48" y="28" width="14" height="10" rx="2" fill="#607D8B"/>
    <rect x="6" y="40" width="20" height="8" rx="2" fill="url(#sw2)"/>
    <rect x="28" y="40" width="20" height="8" rx="2" fill="#78909C"/>
    <rect x="50" y="40" width="10" height="8" rx="2" fill="url(#sw2)"/>
    <path d="M4 10 C20 8 44 10 60 8" stroke="#37474F" stroke-width="4" stroke-linecap="round"/>
    ''', size)


def icon_arch_bridge(size: int = 48) -> str:
    """拱桥"""
    return _wrap('''
    <defs>
      <linearGradient id="ab1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#BCAAA4"/>
        <stop offset="100%" stop-color="#5D4037"/>
      </linearGradient>
      <linearGradient id="ab2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#81D4FA"/>
        <stop offset="100%" stop-color="#0288D1"/>
      </linearGradient>
    </defs>
    <ellipse cx="32" cy="54" rx="28" ry="8" fill="url(#ab2)" opacity="0.6"/>
    <path d="M4 38 C4 38 4 22 32 22 C60 22 60 38 60 38Z" fill="url(#ab1)"/>
    <rect x="4" y="36" width="56" height="6" rx="2" fill="#8D6E63"/>
    <rect x="4" y="36" width="56" height="3" rx="1" fill="#A1887F"/>
    <rect x="6" y="20" width="6" height="18" rx="1" fill="#795548"/>
    <rect x="52" y="20" width="6" height="18" rx="1" fill="#795548"/>
    <path d="M8 38 C8 38 8 28 32 28 C56 28 56 38 56 38" fill="none" stroke="#6D4C41" stroke-width="2"/>
    <rect x="4" y="18" width="56" height="4" rx="1" fill="#6D4C41"/>
    ''', size)


def icon_flower_bed(size: int = 48) -> str:
    """花圃"""
    return _wrap('''
    <defs>
      <linearGradient id="fb1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#A5D6A7"/>
        <stop offset="100%" stop-color="#388E3C"/>
      </linearGradient>
    </defs>
    <rect x="6" y="36" width="52" height="18" rx="4" fill="#5D4037"/>
    <rect x="8" y="34" width="48" height="6" rx="2" fill="#795548"/>
    <rect x="6" y="38" width="52" height="12" rx="2" fill="url(#fb1)" opacity="0.3"/>
    <rect x="8" y="34" width="4" height="14" rx="1" fill="#6D4C41"/>
    <rect x="52" y="34" width="4" height="14" rx="1" fill="#6D4C41"/>
    <rect x="16" y="18" width="3" height="18" rx="1" fill="#4CAF50"/>
    <circle cx="17" cy="14" r="6" fill="#F44336"/>
    <circle cx="15" cy="12" r="2.5" fill="#FFCDD2" opacity="0.7"/>
    <rect x="28" y="14" width="3" height="22" rx="1" fill="#388E3C"/>
    <circle cx="29" cy="10" r="7" fill="#FF9800"/>
    <circle cx="27" cy="8" r="3" fill="#FFE0B2" opacity="0.7"/>
    <rect x="40" y="20" width="3" height="16" rx="1" fill="#4CAF50"/>
    <circle cx="41" cy="16" r="6" fill="#E91E63"/>
    <circle cx="39" cy="14" r="2.5" fill="#FCE4EC" opacity="0.7"/>
    ''', size)


# ============================================================
# 查找表：emoji -> SVG 函数映射
# ============================================================

ICON_MAP = {
    # 绿化
    '🌳': icon_tree,
    '🌲': icon_pine,
    '🌿': icon_bush,
    '🎋': icon_bamboo,
    '🪷': icon_flower,
    '🌺': icon_flower,
    '🌱': icon_lawn,
    '🍀': icon_vine,
    # 设施
    '🪑': icon_bench,
    '🏮': icon_lamp,
    '🔦': icon_lamp,
    '⛲': icon_fountain,
    '🗿': icon_sculpture,
    '🛤️': icon_path,
    '🚧': icon_fence,
    '🏗️': icon_fence,        # 围栏 → icon_fence（移除后面重复的 icon_construction 覆盖）
    # 水体
    '💧': icon_stream,
    '🌊': icon_pond,
    '🏞️': icon_waterscape,   # 池塘/水景 → icon_waterscape（移除后面重复的 icon_park_scene 覆盖）
    # 氛围
    '☀️': icon_sun,
    '🌫️': icon_fog,
    '🍂': icon_leaves,
    '🌸': icon_petals,
    '🕊️': icon_bird,
    '🦅': icon_bird,
    # 页面图标（用不同 key，不与元素 emoji 冲突）
    '📷': icon_camera_lens,
    '🎨': icon_palette,
    '💚': icon_heart_heal,
    '🏙️': icon_city_scene,
    '🎚️': icon_sliders,
    '✏️': icon_pencil,
    '✨': icon_sparkle,
    # 通用/UI
    '💡': icon_bulb,
    '🔬': icon_microscope,
    '📋': icon_clipboard,
    '🧠': icon_brain,
    '📖': icon_book,
    '🧪': icon_flask,
    '🧘': icon_meditation,
    '📚': icon_books,
    '💾': icon_save,
    '🏚️': icon_construction,  # 使用不同 emoji key，避免覆盖 🏗️→fence
    '👥': icon_people,
    '💬': icon_chat,
    '⭐': icon_star,
    '🌿hero': icon_leaf_hero,
    # 公园场景 - 用专属 key（不与水景 🏞️ 冲突）
    '🏞️park': icon_park_scene,
    # 扩充植被
    '🌴': icon_palm,
    '🌸tree': icon_sakura,
    '🌾': icon_reed,
    '🌵': icon_cactus,
    '🪨moss': icon_moss,
    # 扩充设施
    '🪁': icon_swing,
    '⛩️': icon_pavilion,
    '🪵': icon_boardwalk,
    '🎡': icon_windmill,
    '🗑️': icon_trashcan,
    # 扩充水景
    '💦': icon_waterfall,
    '🪷lotus': icon_lotus,
    '🌿water': icon_seagrass,
    '🪨': icon_rock,
    # 扩充氛围
    '🌈': icon_rainbow,
    '✨bug': icon_firefly,
    '🦋': icon_butterfly,
    '🌙': icon_moonlight,
    # 建筑分类
    '🏠': icon_cabin,
    '🧱': icon_stone_wall,
    '🌉': icon_arch_bridge,
    '🌻': icon_flower_bed,
}


def get_svg(emoji: str, size: int = 48) -> str:
    """根据 emoji 获取对应的 SVG 字符串，找不到则回退空"""
    fn = ICON_MAP.get(emoji)
    if fn:
        return fn(size)
    return ''


def get_canvas_element(emoji: str, x: float, y: float, size: int = 48) -> str:
    """生成画布叠加 SVG 元素，定位在 (x, y) 图像坐标处。
    返回可直接拼接到 interactive_image.content 的 SVG 片段。
    """
    import re
    fn = ICON_MAP.get(emoji)
    if not fn:
        return (
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" '
            f'dominant-baseline="central" style="filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3))">'
            f'{emoji}</text>'
        )
    full_svg = fn(size)
    match = re.search(r'<svg[^>]*>(.*)</svg>', full_svg, re.DOTALL)
    if not match:
        return (
            f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{emoji}</text>'
        )
    inner = match.group(1)
    half = size / 2
    return (
        f'<svg x="{x - half}" y="{y - half}" width="{size}" height="{size}" '
        f'viewBox="0 0 64 64" style="overflow:visible; '
        f'filter:drop-shadow(0 3px 6px rgba(0,0,0,0.35))">'
        f'{inner}</svg>'
    )
