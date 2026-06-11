"""智能推荐入口已合并到参数调节页面。"""
from nicegui import ui


def create_ai_mode_page():
    @ui.page('/ai-mode')
    async def ai_mode_page(sid: str = '', back: str = ''):
        target = f'/slider-mode?sid={sid}'
        if back:
            target += f'&back={back}'
        ui.navigate.to(target)
