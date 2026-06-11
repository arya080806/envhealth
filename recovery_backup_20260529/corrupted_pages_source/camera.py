"""鎷嶇収/涓婁紶椤甸潰 - 楂樼骇 UI"""
from pathlib import Path as _Path

from nicegui import ui, app
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import save_upload, create_session, get_session
from app.components.icons import get_svg
from app.components.nav import bottom_nav, smooth_navigate


def create_camera_page():
    @ui.page('/camera')
    def camera_page(sid: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        user = app.storage.user.get('user', None)
        if not user:
            smooth_navigate('/login')
            return

        user_id = user.get('id')

        existing_upload = None
        if sid:
            session = get_session(sid)
            if session and session.uploaded_image_path:
                existing_upload = session.uploaded_image_path
                state = {'session_id': sid, 'uploaded': True, 'scene_type': getattr(session, 'scene_type', '') or ''}
            elif session:
                state = {'session_id': sid, 'uploaded': False, 'scene_type': ''}
            else:
                state = {'session_id': create_session(user_id=user_id), 'uploaded': False, 'scene_type': ''}
        else:
            state = {'session_id': create_session(user_id=user_id), 'uploaded': False, 'scene_type': ''}

        with ui.column().classes('mobile-page'):
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('鎷嶆憚鐜').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px 20px 100px; gap:16px; width:100%'):
                ui.label('鎷嶆憚鎴栦笂浼犱竴寮犵幆澧冪収鐗囷紝鍙互鏄煄甯傝鍖恒€佸叕鍥€佺ぞ鍖虹瓑浠讳綍鎴峰鍦烘墍銆?).classes(
                    'animate-in'
                ).style(
                    f'font-size:14px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                preview_img = ui.image().style(
                    'width:100%; border-radius:20px; object-fit:contain; display:none;'
                    'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                )

                success_label = ui.element('div').style(
                    f'display:none; padding:10px 16px; border-radius:14px; width:100%;'
                    f'background:linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary_light"]}10);'
                    f'border:1px solid {COLORS["primary"]}25;'
                )
                with success_label:
                    ui.label('鉁?鍥剧墖宸蹭笂浼?).style(
                        f'font-size:13px; color:{COLORS["primary_dark"]}; font-weight:500;'
                    )

                # JS鈫扨ython 鍥炶皟妗ユ帴鍏冪礌
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
                            'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                        )
                        success_label.style(
                            f'display:block; padding:10px 16px; border-radius:14px; width:100%;'
                            f'background:linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary_light"]}10);'
                            f'border:1px solid {COLORS["primary"]}25;'
                        )
                        upload_area.set_visibility(False)
                        scene_section.set_visibility(True)
                        next_btn.set_visibility(True)
                        re_btn.set_visibility(True)
                        state['uploaded'] = True

                trigger.on('upload_done', on_upload_done)

                upload_area = ui.element('div').style(
                    'width:100%; min-height:200px; border-radius:20px;'
                    f'border:2px dashed {COLORS["primary"]}30;'
                    'display:flex; align-items:center; justify-content:center;'
                    'cursor:pointer; transition:all 0.3s;'
                    f'background:rgba(45,106,79,0.03);'
                )
                with upload_area:
                    ui.html(f'''
                    <div style="text-align:center; padding:20px; pointer-events:none;">
                        <div id="upIcon{trigger_id}" style="font-size:48px; margin-bottom:12px;">馃摲</div>
                        <div id="upLabel{trigger_id}" style="font-size:14px; color:{COLORS['text_secondary']};">
                            鐐瑰嚮鎷嶇収鎴栭€夋嫨鐓х墖</div>
                        <div id="upProgress{trigger_id}" style="display:none; color:{COLORS['primary']};">
                            <div style="font-size:14px; font-weight:500;">涓婁紶涓€?/div>
                            <div id="upPct{trigger_id}" style="font-size:12px; margin-top:4px;">0%</div>
                        </div>
                        <div style="font-size:12px; color:#aaa; margin-top:8px;">鏀寔 jpg/png锛屾渶澶?20MB</div>
                    </div>
                    <input type="file" id="fileIn{trigger_id}" accept="image/*"
                           style="display:none">
                    ''')
                upload_area.on('click', js_handler=f'() => document.getElementById("fileIn{trigger_id}").click()')

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
                                    {{error:"鏂囦欢杩囧ぇ锛岃閫夋嫨灏忎簬20MB鐨勫浘鐗?}}); }} catch(e) {{
                                    alert("鏂囦欢杩囧ぇ锛岃閫夋嫨灏忎簬20MB鐨勫浘鐗?); }}
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
                                            {{error: data.error||"涓婁紶澶辫触"}}); }} catch(e) {{
                                            alert(data.error||"涓婁紶澶辫触"); }}
                                    }}
                                }} catch(e) {{
                                    try {{ getElement({trigger_id}).$emit("upload_done",
                                        {{error:"鏈嶅姟鍣ㄥ搷搴斿紓甯?}}); }} catch(e2) {{
                                        alert("鏈嶅姟鍣ㄥ搷搴斿紓甯?); }}
                                }}
                                if (lbl) lbl.style.display = "block";
                                if (prg) prg.style.display = "none";
                            }};
                            xhr.onerror = function() {{
                                try {{ getElement({trigger_id}).$emit("upload_done",
                                    {{error:"缃戠粶閿欒锛岃閲嶈瘯"}}); }} catch(e) {{
                                    alert("缃戠粶閿欒锛岃閲嶈瘯"); }}
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
                    img_name = _Path(existing_upload).name
                    preview_img.set_source(f'/api/image/{img_name}')
                    preview_img.style(
                        'display:block; width:100%; border-radius:20px; object-fit:contain;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    )
                    success_label.style(
                        f'display:block; padding:10px 16px; border-radius:14px; width:100%;'
                        f'background:linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary_light"]}10);'
                        f'border:1px solid {COLORS["primary"]}25;'
                    )
                    upload_area.set_visibility(False)

                re_btn = ui.button('閲嶆柊閫夋嫨', on_click=lambda: reset_upload()).props(
                    'flat outline no-caps'
                ).style(
                    f'width:100%; border-radius:28px; color:{COLORS["primary"]};'
                    f'border:2px solid {COLORS["primary"]}40; font-weight:500;'
                    'transition:all 0.3s;'
                )
                re_btn.set_visibility(bool(existing_upload))

                def reset_upload():
                    preview_img.style('display:none')
                    success_label.style('display:none')
                    upload_area.set_visibility(True)
                    scene_section.set_visibility(False)
                    next_btn.set_visibility(False)
                    re_btn.set_visibility(False)
                    state['uploaded'] = False

                # 鍦烘櫙绫诲瀷閫夋嫨
                scene_section = ui.column().style('width:100%; gap:10px; margin-top:8px')
                scene_section.set_visibility(bool(existing_upload))

                with scene_section:
                    ui.label('鍦烘櫙绫诲瀷').style(
                        f'font-size:14px; font-weight:600; color:{COLORS["text"]}; letter-spacing:0.5px'
                    )
                    ui.element('div').classes('section-divider')

                    with ui.row().style('width:100%; gap:12px'):
                        park_card = ui.card().classes('glass-card hover-lift card-press').style(
                            'flex:1; padding:16px; cursor:pointer; border:2px solid transparent !important;'
                            'transition:all 0.3s;'
                        )
                        urban_card = ui.card().classes('glass-card hover-lift card-press').style(
                            'flex:1; padding:16px; cursor:pointer; border:2px solid transparent !important;'
                            'transition:all 0.3s;'
                        )

                        def select_scene(scene_type):
                            state['scene_type'] = scene_type
                            session = get_session(state['session_id'])
                            session.scene_type = scene_type
                            if scene_type == 'park':
                                park_card.style(
                                    f'flex:1; padding:16px; cursor:pointer;'
                                    f'border:2px solid {COLORS["primary"]} !important;'
                                    f'background:rgba(45,106,79,0.06) !important;'
                                    f'box-shadow:0 0 0 4px {COLORS["primary"]}15 !important;'
                                )
                                urban_card.classes('glass-card hover-lift card-press')
                                urban_card.style(
                                    'flex:1; padding:16px; cursor:pointer; border:2px solid transparent !important;'
                                )
                            else:
                                urban_card.style(
                                    f'flex:1; padding:16px; cursor:pointer;'
                                    f'border:2px solid {COLORS["primary"]} !important;'
                                    f'background:rgba(45,106,79,0.06) !important;'
                                    f'box-shadow:0 0 0 4px {COLORS["primary"]}15 !important;'
                                )
                                park_card.style(
                                    'flex:1; padding:16px; cursor:pointer; border:2px solid transparent !important;'
                                )

                        with park_card.on('click', lambda: select_scene('park')):
                            with ui.column().style('align-items:center; gap:8px'):
                                with ui.element('div').style(
                                    f'width:48px; height:48px; border-radius:14px;'
                                    f'background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});'
                                    'display:flex; align-items:center; justify-content:center;'
                                    'box-shadow:0 4px 12px rgba(45,106,79,0.2);'
                                ):
                                    ui.html(get_svg('馃彏锔?, 28)).style('width:28px; height:28px;')
                                ui.label('鍏洯/鑷劧').style(f'font-size:14px; font-weight:600; color:{COLORS["text"]}')
                                ui.label('缁垮湴銆佸叕鍥€佹櫙鍖?).style(
                                    f'font-size:12px; color:{COLORS["text_secondary"]}'
                                )

                        with urban_card.on('click', lambda: select_scene('urban')):
                            with ui.column().style('align-items:center; gap:8px'):
                                with ui.element('div').style(
                                    f'width:48px; height:48px; border-radius:14px;'
                                    f'background:linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]});'
                                    'display:flex; align-items:center; justify-content:center;'
                                    'box-shadow:0 4px 12px rgba(212,163,115,0.3);'
                                ):
                                    ui.html(get_svg('馃彊锔?, 28)).style('width:28px; height:28px;')
                                ui.label('鍩庡競琛楀尯').style(f'font-size:14px; font-weight:600; color:{COLORS["text"]}')
                                ui.label('琛楅亾銆佺ぞ鍖?).style(
                                    f'font-size:12px; color:{COLORS["text_secondary"]}'
                                )

                # 涓嬩竴姝ユ寜閽?                next_btn = ui.button('涓嬩竴姝ワ細閫夋嫨鏀归€犳ā寮?鈫?, on_click=lambda: go_next()).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:8px;')
                next_btn.set_visibility(bool(existing_upload))

                async def go_next():
                    if not state['uploaded']:
                        ui.notify('璇峰厛涓婁紶鍥剧墖', type='warning')
                        return
                    smooth_navigate(f'/mode-select?sid={state["session_id"]}')

            bottom_nav()
