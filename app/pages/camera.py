"""拍照/上传页面 - 高级 UI"""
import base64
from nicegui import ui, app, events
from app.theme import COLORS, COMMON_STYLE, META_VIEWPORT, GLASS_CARD_STYLE, TOP_BAR_STYLE, PRIMARY_BTN_STYLE
from app.state import save_upload, create_session, get_session
from app.components.icons import get_svg


def create_camera_page():
    @ui.page('/camera')
    def camera_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)

        # 检查登录
        user = app.storage.user.get('user', None)
        if not user:
            ui.navigate.to('/login')
            return

        user_id = user.get('id')
        state = {'session_id': create_session(user_id=user_id), 'uploaded': False, 'scene_type': ''}

        with ui.column().classes('mobile-page'):
            # 顶部栏 - 毛玻璃
            with ui.row().style(TOP_BAR_STYLE):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props(
                    'flat round dense'
                ).style(f'color:{COLORS["primary_dark"]}')
                ui.label('拍摄环境').style(
                    f'font-size:17px; font-weight:600; margin-left:4px; color:{COLORS["text"]}'
                )

            with ui.column().style('padding:20px 20px; gap:16px; width:100%'):
                # 说明文字
                ui.label('拍摄或上传一张环境照片，可以是城市街区、公园、社区等任何户外场所。').classes(
                    'animate-in'
                ).style(
                    f'font-size:14px; color:{COLORS["text_secondary"]}; line-height:1.7; font-weight:300'
                )

                # 预览图片
                preview_img = ui.image().style(
                    'width:100%; border-radius:20px; object-fit:contain; display:none;'
                    'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                )
                # 上传成功提示
                success_label = ui.label('').style('display:none;')
                with success_label:
                    pass
                success_label = ui.element('div').style(
                    f'display:none; padding:10px 16px; border-radius:14px; width:100%;'
                    f'background:linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary_light"]}10);'
                    f'border:1px solid {COLORS["primary"]}25;'
                )
                with success_label:
                    ui.label(f'✓ 图片已上传').style(
                        f'font-size:13px; color:{COLORS["primary_dark"]}; font-weight:500;'
                    )

                async def handle_upload(e: events.UploadEventArguments):
                    content = await e.file.read()
                    save_upload(state['session_id'], content, e.file.name)
                    b64 = base64.b64encode(content).decode()
                    mime = e.file.content_type or 'image/jpeg'
                    preview_img.set_source(f'data:{mime};base64,{b64}')
                    preview_img.style(
                        'display:block; width:100%; border-radius:20px; object-fit:contain;'
                        'box-shadow:0 8px 32px rgba(27,67,50,0.12);'
                    )
                    success_label.style(
                        f'display:block; padding:10px 16px; border-radius:14px; width:100%;'
                        f'background:linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary_light"]}10);'
                        f'border:1px solid {COLORS["primary"]}25;'
                    )
                    upload_area.style('display:none')
                    scene_section.set_visibility(True)
                    next_btn.set_visibility(True)
                    re_btn.set_visibility(True)
                    state['uploaded'] = True

                # 上传区域
                upload_area = ui.upload(
                    label='点击拍照或选择照片',
                    on_upload=handle_upload,
                    auto_upload=True,
                    max_file_size=20_000_000,
                ).props('accept="image/*" flat bordered').style(
                    'width:100%; min-height:200px; border-radius:20px;'
                    f'border:2px dashed {COLORS["primary"]}30;'
                ).classes('w-full')

                # 重新选择按钮
                re_btn = ui.button('重新选择', on_click=lambda: reset_upload()).props(
                    'flat outline no-caps'
                ).style(
                    f'width:100%; border-radius:28px; color:{COLORS["primary"]};'
                    f'border:2px solid {COLORS["primary"]}40; font-weight:500;'
                    'transition:all 0.3s;'
                )
                re_btn.set_visibility(False)

                def reset_upload():
                    preview_img.style('display:none')
                    success_label.style('display:none')
                    upload_area.style('display:block; width:100%; min-height:200px; border-radius:20px;')
                    scene_section.set_visibility(False)
                    next_btn.set_visibility(False)
                    re_btn.set_visibility(False)
                    state['uploaded'] = False

                # 场景类型选择
                scene_section = ui.column().style('width:100%; gap:10px; margin-top:8px')
                scene_section.set_visibility(False)

                with scene_section:
                    ui.label('场景类型').style(
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
                                    ui.html(get_svg('🏞️', 28)).style('width:28px; height:28px;')
                                ui.label('公园/自然').style(f'font-size:14px; font-weight:600; color:{COLORS["text"]}')
                                ui.label('绿地、公园、景区').style(
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
                                    ui.html(get_svg('🏙️', 28)).style('width:28px; height:28px;')
                                ui.label('城市街区').style(f'font-size:14px; font-weight:600; color:{COLORS["text"]}')
                                ui.label('街道、社区').style(
                                    f'font-size:12px; color:{COLORS["text_secondary"]}'
                                )

                # 下一步按钮
                next_btn = ui.button('下一步：选择改造模式 →', on_click=lambda: go_next()).props(
                    'no-caps unelevated'
                ).style(PRIMARY_BTN_STYLE + 'margin-top:8px;')
                next_btn.set_visibility(False)

                async def go_next():
                    if not state['uploaded']:
                        ui.notify('请先上传图片', type='warning')
                        return
                    ui.navigate.to(f'/mode-select?sid={state["session_id"]}')
