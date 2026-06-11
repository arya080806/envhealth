"""Compatibility route for the removed about page."""
from nicegui import ui

from app.components.nav import smooth_navigate
from app.theme import COMMON_STYLE, META_VIEWPORT


def create_about_page():
    @ui.page('/about')
    def about_page():
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.timer(0.01, lambda: smooth_navigate('/account'), once=True)
