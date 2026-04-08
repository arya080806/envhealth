"""结果对比页面 - 高级 UI"""
from pathlib import Path
from nicegui import ui
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import get_session
from app.components.icons import get_svg


def create_result_page():
    @ui.page('/result')
    def result_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        session = get_session(sid) if sid else None

        # 前后对比滑动组件 CSS
        ui.add_head_html('''<style>
.compare-wrap {
  position: relative; width: 100%; overflow: hidden;
  border-radius: 20px; box-shadow: 0 8px 32px rgba(27,67,50,0.14);
  background: #e8f0ea; user-select: none; -webkit-user-select: none;
  cursor: col-resize;
}
.compare-wrap img {
  display: block; width: 100%; height: auto;
  object-fit: cover; pointer-events: none;
}
.compare-before-clip {
  position: absolute; top: 0; left: 0; height: 100%;
  width: 50%; overflow: hidden;
}
.compare-before-clip img {
  width: auto; min-width: 100%; max-width: none;
  position: absolute; top: 0; left: 0;
}
.compare-divider {
  position: absolute; top: 0; left: 50%; height: 100%; width: 2px;
  background: white; box-shadow: 0 0 8px rgba(0,0,0,0.3);
  transform: translateX(-50%); pointer-events: none; z-index: 10;
}
.compare-handle {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 40px; height: 40px; border-radius: 50%;
  background: white; box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  display: flex; align-items: center; justify-content: center;
}
.compare-label {
  position: absolute; top: 12px; padding: 4px 12px;
  border-radius: 20px; font-size: 12px; font-weight: 600;
  color: white; backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px); pointer-events: none;
  z-index: 11;
}
.compare-label-before {
  left: 12px; background: rgba(27,67,50,0.65);
}
.compare-label-after {
  right: 12px;
  background: linear-gradient(135deg, rgba(45,106,79,0.8), rgba(82,183,136,0.8));
}
.compare-range {
  position: absolute; inset: 0; width: 100%; height: 100%;
  opacity: 0; cursor: col-resize; z-index: 20; margin: 0;
  -webkit-appearance: none;
}
.compare-hint {
  text-align: center; font-size: 11px; color: #6B7280;
  margin-top: 6px; font-weight: 300;
}
</style>''')

        # v-html 会剥离内联事件（oninput 等），因此必须用 addEventListener 绑定
        ui.add_head_html('''<script>
function cmpUpdate(v) {
  var pct = v + '%';
  var clip = document.getElementById('cmp-before-clip');
  var div  = document.getElementById('cmp-divider');
  var img  = document.getElementById('cmp-before-img');
  var wrap = document.getElementById('cmp-wrap');
  if (clip) clip.style.width = pct;
  if (div)  div.style.left  = pct;
  if (img && wrap) img.style.width = wrap.offsetWidth + 'px';
}
function cmpBind() {
  var slider = document.querySelector('.compare-range');
  if (!slider) return;
  if (slider._cmpBound) return;
  slider._cmpBound = true;
  slider.addEventListener('input', function() { cmpUpdate(this.value); });
  slider.addEventListener('touchmove', function() { cmpUpdate(this.value); });
  cmpUpdate(slider.value);
}
window.addEventListener('load', cmpBind);
new MutationObserver(function() { cmpBind(); })
  .observe(document.body, {childList: true, subtree: true});
</script>''')

        with ui.column().classes('mobile-page'):
            # 顶部栏
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/mode-select?sid={sid}')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('改造结果').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px; gap:16px; width:100%'):

                # 对比标题
                with ui.row().classes('animate-in').style('align-items:center; gap:8px'):
                    ui.label('改造前 vs 改造后').style(
                        f'font-size:16px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                    )

                ui.element('div').classes('section-divider')

                # ── 滑动对比组件 ──
                orig_url = ''
                gen_url = ''
                if session and session.uploaded_image_path:
                    orig_url = f'/api/image/{Path(session.uploaded_image_path).name}'
                if session and session.generated_image_path:
                    gen_url = f'/api/image/{Path(session.generated_image_path).name}'

                if gen_url:
                    # 有生成图：展示滑动对比
                    compare_html = f'''
<div class="compare-wrap animate-in" id="cmp-wrap">
  <img src="{gen_url}" alt="改造后" id="cmp-after">
  <div class="compare-before-clip" id="cmp-before-clip">
    <img src="{orig_url}" alt="改造前" id="cmp-before-img" style="width:100%;position:static;">
  </div>
  <div class="compare-divider" id="cmp-divider">
    <div class="compare-handle">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M7 4L3 10L7 16" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M13 4L17 10L13 16" stroke="#2D6A4F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  </div>
  <div class="compare-label compare-label-before">改造前</div>
  <div class="compare-label compare-label-after">改造后</div>
  <input type="range" min="0" max="100" value="50" class="compare-range">
</div>
<p class="compare-hint">← 拖动滑块查看前后对比 →</p>
'''
                    ui.html(compare_html).classes('animate-in animate-in-delay-1').style('width:100%')
                else:
                    # 无生成图：仅显示原图
                    with ui.element('div').classes('animate-in animate-in-delay-1').style(
                        'width:100%; position:relative; border-radius:20px; overflow:hidden;'
                        'box-shadow:0 4px 20px rgba(27,67,50,0.08);'
                    ):
                        if orig_url:
                            ui.image(orig_url).style('width:100%; border-radius:20px; object-fit:cover;')
                        with ui.column().classes('glass-card').style(
                            'width:100%; padding:32px; text-align:center; align-items:center; margin-top:8px;'
                        ):
                            ui.label('暂未生成改造图').style(
                                f'color:{COLORS["text_secondary"]}; font-size:14px; font-weight:300'
                            )

                # 参数摘要
                ui.label('环境参数').classes('animate-in animate-in-delay-3').style(
                    f'font-size:15px; font-weight:600; color:{COLORS["text"]}; margin-top:4px;'
                    'letter-spacing:0.5px;'
                )

                green = session.green_level if session else 50
                urban = session.urban_level if session else 50
                vitality = session.vitality_level if session else 50
                light = session.light_warmth if session else 50

                with ui.row().classes('animate-in animate-in-delay-3').style(
                    'width:100%; gap:10px; flex-wrap:wrap'
                ):
                    param_configs = [
                        ('🌿', '绿化', green, COLORS['primary']),
                        ('🏗️', '人造', urban, COLORS['secondary']),
                        ('👥', '活力', vitality, COLORS['accent']),
                        ('☀️', '光线', light, COLORS['accent_light']),
                    ]
                    for icon_key, label, val, color in param_configs:
                        with ui.card().classes('glass-card').style(
                            'flex:1; min-width:calc(50% - 8px); padding:14px 12px; text-align:center;'
                            'border:none !important;'
                        ):
                            with ui.row().style('justify-content:center; align-items:center; gap:4px'):
                                svg = get_svg(icon_key, 14)
                                if svg:
                                    ui.html(svg).style('width:14px; height:14px;')
                                ui.label(label).style(
                                    f'font-size:11px; color:{COLORS["text_secondary"]}; font-weight:400'
                                )
                            ui.label(f'{int(val)}%').style(
                                f'font-size:22px; font-weight:700; color:{color}; margin:4px 0'
                            )
                            # 进度条
                            with ui.element('div').classes('progress-bar'):
                                ui.element('div').classes('progress-bar-fill').style(
                                    f'width:{int(val)}%; background:linear-gradient(90deg, {color}, {color}88);'
                                )

                # 操作按钮
                with ui.row().classes('animate-in animate-in-delay-4').style(
                    'width:100%; gap:12px; margin-top:8px'
                ):
                    ui.button('重新调整', on_click=lambda: ui.navigate.to(f'/mode-select?sid={sid}')).props(
                        'outline no-caps'
                    ).style(
                        f'flex:1; border-radius:28px; color:{COLORS["primary"]};'
                        f'border:2px solid {COLORS["primary"]}40; padding:14px; font-weight:500;'
                        'transition:all 0.3s;'
                    )
                    ui.button('进入评估 →', on_click=lambda: ui.navigate.to(f'/survey?sid={sid}')).props(
                        'no-caps unelevated'
                    ).style(
                        f'flex:1; background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                        'color:white; border-radius:28px; padding:14px; font-weight:600;'
                        f'box-shadow:0 6px 20px rgba(45,106,79,0.25);'
                    )

                # 下载按钮
                if session and session.generated_image_path:
                    gen_fname2 = Path(session.generated_image_path).name
                    ui.link('下载结果图片', f'/api/image/{gen_fname2}', new_tab=True).style(
                        f'display:block; text-align:center; padding:14px;'
                        f'border:2px solid {COLORS["border"]}; border-radius:28px;'
                        f'color:{COLORS["text"]}; text-decoration:none; font-size:14px;'
                        'font-weight:500; transition:all 0.3s;'
                    )
