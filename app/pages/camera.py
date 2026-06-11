"""Camera/upload page with generated preset environments."""
from pathlib import Path

from nicegui import app, ui

from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate
from app.db import get_hci_participant_by_user_id
from app.state import create_session, get_session, save_upload
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, PRIMARY_BTN_STYLE, TOP_BAR_STYLE


PRESET_SCENES = [
    {
        'title': '雨后口袋花园',
        'subtitle': '城市边角里的清新绿意',
        'image': 'pocket-garden.png',
        'scene_type': 'park',
    },
    {
        'title': '庭院水厅',
        'subtitle': '木色、树影与静水庭院',
        'image': 'courtyard-water-lounge.png',
        'scene_type': 'courtyard',
    },
    {
        'title': '静谧竹庭',
        'subtitle': '碎石、苔藓与晨间竹影',
        'image': 'bamboo-courtyard.png',
        'scene_type': 'courtyard',
    },
    {
        'title': '社区花径',
        'subtitle': '温暖、明亮、适合散步',
        'image': 'community-flower-lane.png',
        'scene_type': 'urban',
    },
    {
        'title': '山谷晨湖',
        'subtitle': '晨光、溪流与开阔山景',
        'image': 'mountain-lake-morning.png',
        'scene_type': 'water',
    },
    {
        'title': '日光疗愈室',
        'subtitle': '木色、绿意与安静休憩',
        'image': 'sunlit-healing-room.png',
        'scene_type': 'courtyard',
    },
]


PRESET_DIR = Path(__file__).resolve().parent.parent / 'static' / 'images' / 'presets'


def _preset_url(filename: str) -> str:
    return f'/static/images/presets/{filename}'


def _camera_page_css() -> str:
    return f'''
    <style>
    .camera-copy {{
        font-size: 14px;
        color: {COLORS['text_secondary']};
        line-height: 1.75;
        font-weight: 300;
    }}

    .camera-upload-box {{
        width: 100%;
        min-height: 220px;
        border-radius: 24px;
        border: 2px dashed rgba(183,242,126,0.30);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: border-color 0.22s ease, background 0.22s ease, transform 0.22s ease;
        background: rgba(183,242,126,0.045);
    }}

    .camera-upload-box:hover {{
        border-color: rgba(183,242,126,0.54);
        background: rgba(183,242,126,0.07);
    }}

    .camera-upload-box:active {{
        transform: scale(0.99);
    }}

    .camera-upload-icon {{
        width: 58px;
        height: 58px;
        margin: 0 auto 14px;
        color: {COLORS['text']};
        opacity: 0.92;
    }}

    .camera-upload-icon svg {{
        width: 58px;
        height: 58px;
        display: block;
    }}

    .preset-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
    }}

    .preset-card {{
        position: relative;
        min-height: 142px;
        overflow: hidden;
        border-radius: 8px;
        border: 1px solid rgba(244,240,230,0.13);
        background: rgba(16,29,22,0.78);
        cursor: pointer;
        box-shadow: 0 12px 28px rgba(0,0,0,0.20);
        transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    }}

    .preset-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(183,242,126,0.34);
        box-shadow: 0 16px 34px rgba(0,0,0,0.26);
    }}

    .preset-card:active {{
        transform: scale(0.985);
    }}

    .preset-card img {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    .preset-card::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(7,18,13,0.02) 22%, rgba(7,18,13,0.80) 100%);
    }}

    .preset-meta {{
        position: absolute;
        left: 10px;
        right: 10px;
        bottom: 9px;
        z-index: 1;
        color: {COLORS['text']};
    }}

    .preset-title {{
        font-size: 13px;
        font-weight: 750;
        line-height: 1.2;
    }}

    .preset-subtitle {{
        margin-top: 4px;
        font-size: 10.5px;
        color: rgba(244,240,230,0.74);
        line-height: 1.35;
    }}

    @media (min-width: 900px) and (orientation: landscape) {{
        .camera-shell {{
            padding: 24px 34px 124px !important;
            display: grid !important;
            grid-template-columns: minmax(360px, .78fr) minmax(560px, 1.22fr);
            gap: 18px 24px !important;
            align-items: center !important;
            align-content: center !important;
            min-height: calc(100dvh - 72px);
        }}

        .camera-copy,
        .camera-upload-box {{
            grid-column: 1;
        }}

        .camera-copy {{
            align-self: end;
            max-width: 36ch;
            margin-bottom: 6px;
            translate: 0 48px;
        }}

        .camera-upload-box {{
            min-height: 260px;
            align-self: start;
            translate: 0 48px;
        }}

        .camera-preset-section {{
            grid-column: 2;
            grid-row: 1 / span 6;
            align-self: center;
            margin-top: 0 !important;
        }}

        .preset-grid {{
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }}

        .preset-card {{
            min-height: 184px;
        }}
    }}

    @media (max-width: 360px) {{
        .preset-grid {{
            grid-template-columns: 1fr;
        }}

        .preset-card {{
            min-height: 156px;
        }}
    }}
    </style>
    '''


def create_camera_page():
    @ui.page('/camera')
    def camera_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(_camera_page_css())

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        user_id = user.get('id')
        if not get_hci_participant_by_user_id(user_id):
            smooth_navigate('/participant-info?next_path=/camera')
            return

        existing_upload = None

        if sid:
            session = get_session(sid)
            if session and session.uploaded_image_path:
                existing_upload = session.uploaded_image_path
                state = {'session_id': sid, 'uploaded': True}
            elif session:
                state = {'session_id': sid, 'uploaded': False}
            else:
                state = {'session_id': create_session(user_id=user_id), 'uploaded': False}
        else:
            state = {'session_id': create_session(user_id=user_id), 'uploaded': False}

        def reset_upload():
            preview_img.style('display:none')
            success_label.style('display:none')
            upload_area.set_visibility(True)
            next_btn.set_visibility(False)
            re_btn.set_visibility(False)
            state['uploaded'] = False

        async def go_next():
            if not state['uploaded']:
                ui.notify('请先上传图片，或选择一个下方场景', type='warning')
                return
            smooth_navigate(f'/mode-select?sid={state["session_id"]}')

        async def use_preset(scene: dict):
            preset_path = PRESET_DIR / scene['image']
            if not preset_path.exists():
                ui.notify('预设场景图片不存在', type='negative')
                return

            saved_path = save_upload(
                state['session_id'],
                preset_path.read_bytes(),
                scene['image'],
            )
            session = get_session(state['session_id'])
            if session:
                session.scene_type = scene['scene_type']

            state['uploaded'] = True
            preview_img.set_source(f'/api/image/{Path(saved_path).name}')
            smooth_navigate(f'/mode-select?sid={state["session_id"]}')

        with ui.column().classes('mobile-page'):
            bottom_nav()
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary"]}')
                ui.label('拍摄环境').style(
                    f'font-size:17px; font-weight:700; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().classes('camera-shell').style('padding:20px 20px 106px; gap:16px; width:100%'):
                ui.label(
                    '拍摄或上传一张环境照片，可以是城市街区、公园、社区、住所等任何场所。'
                ).classes('animate-in camera-copy')

                preview_img = ui.image().style(
                    'width:100%; border-radius:20px; object-fit:contain; display:none;'
                    'box-shadow:0 8px 32px rgba(0,0,0,0.24);'
                )

                success_label = ui.element('div').style(
                    'display:none; padding:10px 16px; border-radius:14px; width:100%;'
                    'background:rgba(183,242,126,0.10); border:1px solid rgba(183,242,126,0.22);'
                )
                with success_label:
                    ui.label('图片已准备好').style(
                        f'font-size:13px; color:{COLORS["primary"]}; font-weight:650;'
                    )

                trigger = ui.element('div').style('display:none')
                trigger_id = trigger.id

                async def on_upload_done(e):
                    data = e.args
                    if not isinstance(data, dict):
                        return
                    if 'error' in data:
                        ui.notify(data['error'], type='negative')
                        return
                    if 'image_url' in data:
                        preview_img.set_source(data['image_url'])
                        preview_img.style(
                            'display:block; width:100%; border-radius:20px; object-fit:contain;'
                            'box-shadow:0 8px 32px rgba(0,0,0,0.24);'
                        )
                        success_label.style(
                            'display:block; padding:10px 16px; border-radius:14px; width:100%;'
                            'background:rgba(183,242,126,0.10); border:1px solid rgba(183,242,126,0.22);'
                        )
                        upload_area.set_visibility(False)
                        next_btn.set_visibility(True)
                        re_btn.set_visibility(True)
                        state['uploaded'] = True

                trigger.on('upload_done', on_upload_done)

                upload_area = ui.element('div').classes('camera-upload-box')
                with upload_area:
                    ui.html(f'''
                    <div style="text-align:center; padding:20px; pointer-events:none;">
                        <div id="upIcon{trigger_id}" class="camera-upload-icon">{get_svg('📷', 58)}</div>
                        <div id="upLabel{trigger_id}" style="font-size:14px; color:{COLORS['text_secondary']};">
                            点击拍照或选择照片
                        </div>
                        <div id="upProgress{trigger_id}" style="display:none; color:{COLORS['primary']};">
                            <div style="font-size:14px; font-weight:650;">上传中</div>
                            <div id="upPct{trigger_id}" style="font-size:12px; margin-top:4px;">0%</div>
                        </div>
                        <div style="font-size:12px; color:{COLORS['text_muted']}; margin-top:8px;">
                            支持 jpg/png，最大 20MB
                        </div>
                    </div>
                    <input type="file" id="fileIn{trigger_id}" accept="image/*" style="display:none">
                    ''')
                upload_area.on(
                    'click',
                    js_handler=f'() => document.getElementById("fileIn{trigger_id}").click()',
                )

                ui.add_head_html(f'''<script>
                document.addEventListener("DOMContentLoaded", function() {{
                    var _t = setInterval(function() {{
                        var fi = document.getElementById("fileIn{trigger_id}");
                        if (!fi) return;
                        clearInterval(_t);
                        fi.addEventListener("change", async function() {{
                            var file = this.files[0];
                            if (!file) return;
                            if (file.size > 20*1024*1024) {{
                                try {{ getElement({trigger_id}).$emit("upload_done",
                                    {{error:"文件过大，请选择小于 20MB 的图片"}}); }} catch(e) {{
                                    alert("文件过大，请选择小于 20MB 的图片"); }}
                                this.value = ""; return;
                            }}
                            var lbl = document.getElementById("upLabel{trigger_id}");
                            var prg = document.getElementById("upProgress{trigger_id}");
                            var pct = document.getElementById("upPct{trigger_id}");
                            if (lbl) lbl.style.display = "none";
                            if (prg) prg.style.display = "block";

                            var xhr = new XMLHttpRequest();
                            xhr.open("POST", "/api/upload", true);
                            xhr.upload.onprogress = function(ev) {{
                                if (ev.lengthComputable && pct)
                                    pct.textContent = Math.round(ev.loaded/ev.total*100) + "%";
                            }};
                            xhr.onload = function() {{
                                try {{
                                    var data = JSON.parse(xhr.responseText);
                                    if (xhr.status === 200) {{
                                        try {{ getElement({trigger_id}).$emit("upload_done", data); }}
                                        catch(e) {{ window.location.href="/camera?sid="+data.session_id; }}
                                    }} else {{
                                        try {{ getElement({trigger_id}).$emit("upload_done",
                                            {{error: data.error||"上传失败"}}); }} catch(e) {{
                                            alert(data.error||"上传失败"); }}
                                    }}
                                }} catch(e) {{
                                    try {{ getElement({trigger_id}).$emit("upload_done",
                                        {{error:"服务器响应异常"}}); }} catch(e2) {{
                                        alert("服务器响应异常"); }}
                                }}
                                if (lbl) lbl.style.display = "block";
                                if (prg) prg.style.display = "none";
                            }};
                            xhr.onerror = function() {{
                                try {{ getElement({trigger_id}).$emit("upload_done",
                                    {{error:"网络错误，请重试"}}); }} catch(e) {{
                                    alert("网络错误，请重试"); }}
                                if (lbl) lbl.style.display = "block";
                                if (prg) prg.style.display = "none";
                            }};
                            var fd = new FormData();
                            fd.append("file", file);
                            fd.append("session_id", "{state['session_id']}");
                            xhr.send(fd);
                            this.value = "";
                        }});
                    }}, 200);
                }});
                </script>''')

                if existing_upload:
                    img_name = Path(existing_upload).name
                    preview_img.set_source(f'/api/image/{img_name}')
                    preview_img.style(
                        'display:block; width:100%; border-radius:20px; object-fit:contain;'
                        'box-shadow:0 8px 32px rgba(0,0,0,0.24);'
                    )
                    success_label.style(
                        'display:block; padding:10px 16px; border-radius:14px; width:100%;'
                        'background:rgba(183,242,126,0.10); border:1px solid rgba(183,242,126,0.22);'
                    )
                    upload_area.set_visibility(False)

                re_btn = ui.button('重新选择', on_click=reset_upload).props(
                    'flat outline no-caps'
                ).style(
                    f'width:100%; border-radius:28px; color:{COLORS["primary"]};'
                    'border:2px solid rgba(183,242,126,0.25); font-weight:650;'
                )
                re_btn.set_visibility(bool(existing_upload))

                next_btn = ui.button('下一步：选择改造模式', on_click=go_next).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:2px;')
                next_btn.set_visibility(bool(existing_upload))

                with ui.column().classes('camera-preset-section').style('width:100%; gap:10px; margin-top:6px;'):
                    ui.label('也可选择预设场景').style(
                        f'font-size:14px; font-weight:700; color:{COLORS["text"]};'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.element('div').classes('preset-grid'):
                        for scene in PRESET_SCENES:
                            card = ui.element('button').classes('preset-card').props('aria-label="' + scene['title'] + '"')
                            card.style('appearance:none; -webkit-appearance:none; padding:0; text-align:left;')
                            card.on('click', lambda s=scene: use_preset(s))
                            with card:
                                ui.html(
                                    f'<img src="{_preset_url(scene["image"])}" alt="{scene["title"]}">'
                                    '<div class="preset-meta">'
                                    f'<div class="preset-title">{scene["title"]}</div>'
                                    f'<div class="preset-subtitle">{scene["subtitle"]}</div>'
                                    '</div>'
                                )
