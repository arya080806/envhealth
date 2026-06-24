"""灵感创想模式页面。

该页面承载手绘输入、自动识别、用户标注修正、研究数据采集与图像生成。
"""
from __future__ import annotations

import asyncio
import json

from nicegui import ui

from app.components.nav import bottom_nav, smooth_navigate
from app.state import get_session, media_url, resolve_media_path, save_canvas_json, save_canvas_snapshot, save_output
from app.theme import COMMON_STYLE, LIGHT_PRIMARY_BTN_STYLE, LIGHT_TOP_BAR_STYLE, META_VIEWPORT


INSPIRE_CSS = """
<style>
.inspire-shell {
    padding: 20px 18px 112px;
    gap: 14px;
}
.inspire-card {
    width: 100%;
    border-radius: 22px;
    border: 1px solid rgba(47,123,88,.14);
    background: rgba(255,255,248,.76);
    box-shadow: 0 16px 34px rgba(38,70,52,.08);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}
.inspire-top-action,
.light-page .q-btn.inspire-top-action {
    min-width: 58px;
    height: 36px;
    border-radius: 12px !important;
    padding: 0 14px;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 0;
    box-shadow: none;
}
.inspire-top-action.clear,
.light-page .q-btn.inspire-top-action.clear {
    background: rgba(47,123,88,.10) !important;
    color: #2F7B58 !important;
    border: 1px solid rgba(47,123,88,.18) !important;
}
.inspire-top-action.save,
.light-page .q-btn.inspire-top-action.save {
    background: #2F7B58 !important;
    color: #FFFDF4 !important;
    border: 1px solid rgba(47,123,88,.24) !important;
}
.inspire-brief {
    padding: 14px 16px;
    color: #173126;
}
.inspire-brief-title {
    font-size: 15px;
    font-weight: 900;
    color: #173126;
    margin-bottom: 4px;
}
.inspire-brief-sub {
    font-size: 12px;
    color: rgba(23,49,38,.56);
    line-height: 1.5;
}
.inspire-canvas-wrap {
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
    min-height: 250px;
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(47,123,88,.12);
    background:
        linear-gradient(180deg, rgba(255,255,248,.28), rgba(240,248,239,.46)),
        repeating-linear-gradient(90deg, rgba(47,123,88,.055) 0 1px, transparent 1px 32px),
        repeating-linear-gradient(0deg, rgba(47,123,88,.045) 0 1px, transparent 1px 32px),
        #f3f8ef;
    position: relative;
    touch-action: none;
}
.inspire-canvas-wrap.canvas-drawing {
    box-shadow: inset 0 0 0 2px rgba(47,123,88,.18);
}
#inspire-canvas {
    display: block;
    width: 100%;
}
.inspire-toolbar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}
.inspire-tool-btn {
    border: 1px solid rgba(47,123,88,.18);
    background: rgba(255,255,248,.78);
    color: #2F7B58;
    border-radius: 12px;
    padding: 8px 11px;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
}
.inspire-tool-btn.active {
    background: #2F7B58;
    color: #F8FAF2;
    border-color: #2F7B58;
}
.inspire-tool-btn:disabled {
    opacity: .45;
    cursor: not-allowed;
}
.inspire-tool-btn.danger {
    color: #E76F51;
}
.color-dot {
    width: 27px;
    height: 27px;
    border-radius: 999px;
    border: 2px solid rgba(255,255,248,.88);
    box-shadow: 0 0 0 1px rgba(47,123,88,.12), 0 8px 16px rgba(38,70,52,.10);
    cursor: pointer;
}
.color-dot.selected {
    box-shadow: 0 0 0 3px rgba(47,123,88,.24), 0 8px 16px rgba(38,70,52,.10);
}
.brush-range {
    accent-color: #2F7B58;
    width: 118px;
}
.inspire-meta-row {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
    color: rgba(23,49,38,.54);
}
.inspire-panel {
    width: 100%;
    padding: 13px 14px;
}
.inspire-panel-title {
    font-size: 13px;
    color: #173126;
    font-weight: 900;
    margin-bottom: 8px;
}
.lens-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
}
.lens-card {
    border: 1px solid rgba(47,123,88,.14);
    border-radius: 16px;
    padding: 10px 8px;
    min-height: 74px;
    background: rgba(255,255,248,.64);
    cursor: pointer;
}
.lens-card.active {
    background: rgba(47,123,88,.12);
    border-color: rgba(47,123,88,.42);
}
.lens-card strong {
    display: block;
    color: #173126;
    font-size: 12px;
    margin-bottom: 4px;
}
.lens-card span {
    display: block;
    color: rgba(23,49,38,.58);
    font-size: 10px;
    line-height: 1.35;
}
.agency-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.agency-row input {
    flex: 1;
    accent-color: #2F7B58;
}
.agency-value {
    min-width: 54px;
    text-align: right;
    font-size: 11px;
    color: rgba(23,49,38,.62);
    font-weight: 700;
}
#inspire-result-area {
    min-height: 88px;
    border-radius: 18px;
    border: 1px dashed rgba(47,123,88,.22);
    padding: 13px 14px;
    background: rgba(255,255,248,.50);
    color: rgba(23,49,38,.70);
}
.result-title {
    font-size: 13px;
    font-weight: 900;
    color: #173126;
    margin-bottom: 7px;
}
.elem-tags, .explain-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.elem-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    border-radius: 999px;
    background: rgba(47,123,88,.10);
    color: #2F7B58;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 800;
}
.explain-chip {
    border-radius: 12px;
    background: rgba(139,92,246,.08);
    color: #5b43a4;
    padding: 7px 9px;
    font-size: 10px;
    line-height: 1.35;
}
#layer-panel {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    padding: 10px;
    border-radius: 20px;
    border: 1px solid rgba(47,123,88,.14);
    background:
        linear-gradient(180deg, rgba(255,255,248,.80), rgba(241,248,238,.64)),
        repeating-linear-gradient(90deg, rgba(47,123,88,.04) 0 1px, transparent 1px 30px);
    box-shadow: 0 12px 28px rgba(38,70,52,.08);
    margin-top: -6px;
}
.layer-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 2px 2px 4px;
}
.layer-panel-title {
    font-size: 12px;
    font-weight: 900;
    color: #173126;
}
.layer-panel-count {
    font-size: 10px;
    font-weight: 800;
    color: rgba(23,49,38,.48);
}
.layer-list {
    display: flex;
    flex-direction: column;
    gap: 7px;
}
.layer-item {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr) auto;
    align-items: center;
    gap: 9px;
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(47,123,88,.10);
    background: rgba(255,255,248,.70);
    color: #173126;
    font-size: 11px;
    cursor: pointer;
}
.layer-item.active {
    background: rgba(47,123,88,.12);
    border-color: rgba(47,123,88,.38);
    box-shadow: inset 3px 0 0 #2F7B58;
}
.layer-thumb {
    width: 44px;
    height: 32px;
    border-radius: 10px;
    background: rgba(47,123,88,.06);
    border: 1px solid rgba(47,123,88,.10);
    overflow: hidden;
}
.layer-thumb svg {
    display: block;
    width: 100%;
    height: 100%;
}
.layer-main {
    min-width: 0;
}
.layer-name {
    font-size: 12px;
    font-weight: 900;
    color: #173126;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.layer-sub {
    margin-top: 2px;
    font-size: 10px;
    color: rgba(23,49,38,.50);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.layer-zone {
    font-size: 10px;
    font-weight: 800;
    color: rgba(47,123,88,.78);
    white-space: nowrap;
}
.annotation-box {
    display: none;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
}
.annotation-box.visible {
    display: flex;
    margin-top: -6px;
}
.annotation-box input {
    flex: 1;
    min-width: 138px;
    border: 1px solid rgba(47,123,88,.18);
    border-radius: 14px;
    background: rgba(255,255,248,.82);
    padding: 9px 10px;
    color: #173126;
    outline: none;
    font-size: 12px;
}
.annotation-box button {
    border: none;
    border-radius: 12px;
    padding: 9px 10px;
    background: #2F7B58;
    color: #F8FAF2;
    font-size: 12px;
    font-weight: 800;
}
.annotation-box button.secondary {
    border: 1px solid rgba(47,123,88,.18);
    background: rgba(255,255,248,.78);
    color: #2F7B58;
}
.annotation-box button.danger {
    background: rgba(231,111,81,.12);
    color: #C8523C;
}
.inspire-error {
    display: none;
    width: 100%;
    padding: 11px 13px;
    border-radius: 16px;
    border: 1px solid rgba(231,111,81,.20);
    background: rgba(231,111,81,.08);
    color: #C8523C;
    font-size: 12px;
}
.inspire-loading {
    display: none;
    width: 100%;
    padding: 12px 14px;
    border-radius: 18px;
    background: rgba(255,255,248,.82);
    border: 1px solid rgba(47,123,88,.14);
    box-shadow: 0 14px 28px rgba(38,70,52,.10);
}
.inspire-loading-head {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: #173126;
    font-size: 12px;
    font-weight: 900;
}
.inspire-loading-note {
    margin-top: 5px;
    color: rgba(23,49,38,.58);
    font-size: 11px;
    line-height: 1.45;
    font-weight: 700;
}
.inspire-loading-track {
    overflow: hidden;
    height: 8px;
    margin-top: 10px;
    border-radius: 999px;
    background: rgba(47,123,88,.13);
}
.inspire-loading-fill {
    width: 72%;
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #2F7B58, #B7F27E);
    animation: inspireAiProgress 2.6s ease-in-out infinite;
}
@keyframes inspireAiProgress {
    0% { width: 12%; transform: translateX(-18%); }
    45% { width: 72%; transform: translateX(0); }
    100% { width: 92%; transform: translateX(6%); }
}
.inspire-fallback {
    display: none;
    padding: 12px;
    border-radius: 16px;
    background: rgba(231,111,81,.08);
    color: #C8523C;
    font-size: 12px;
}
.inspire-inline-label {
    position: absolute;
    z-index: 5;
    max-width: 132px;
    padding: 5px 8px;
    border-radius: 10px;
    background: rgba(255,255,248,.92);
    color: #173126;
    font-size: 12px;
    font-weight: 800;
    line-height: 1.2;
    box-shadow: 0 6px 18px rgba(10,31,24,.12);
    pointer-events: none;
    transform: translate3d(0,0,0);
}
.inspire-shell {
    padding-top: 16px;
    gap: 12px;
}
.inspire-brief {
    padding: 15px 16px 13px;
}
.inspire-brief-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    cursor: pointer;
}
.inspire-brief-head .inspire-brief-title {
    margin-bottom: 0;
}
.inspire-brief-actions {
    display: flex;
    align-items: center;
    gap: 6px;
}
.brief-toggle-btn {
    border: 1px solid rgba(47,123,88,.14);
    background: rgba(255,255,248,.72);
    color: rgba(23,49,38,.62);
    border-radius: 999px;
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 900;
    white-space: nowrap;
    cursor: pointer;
}
.inspire-brief-body {
    display: block;
}
.inspire-brief.collapsed {
    padding-bottom: 15px;
}
.inspire-brief.collapsed .inspire-brief-body {
    display: none;
}
.stroke-guide-btn {
    border: 1px solid rgba(47,123,88,.18);
    background: rgba(47,123,88,.10);
    color: #2F7B58;
    border-radius: 999px;
    padding: 6px 9px;
    font-size: 11px;
    font-weight: 900;
    white-space: nowrap;
    cursor: pointer;
}
.hint-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 10px;
}
.hint-chip {
    display: grid;
    grid-template-columns: 46px minmax(0, 1fr);
    column-gap: 8px;
    align-items: center;
    border: 1px solid rgba(47,123,88,.12);
    border-radius: 15px;
    padding: 8px;
    background: rgba(47,123,88,.055);
    color: #173126;
}
.stroke-example {
    grid-row: 1 / 3;
    height: 22px;
    margin-bottom: 0;
    border-radius: 8px;
    background: rgba(255,255,248,.54);
    overflow: hidden;
}
.stroke-example svg {
    display: block;
    width: 100%;
    height: 100%;
}
.stroke-example path,
.stroke-example circle {
    stroke: #2F7B58;
    stroke-width: 4;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
}
.stroke-example circle {
    fill: #2F7B58;
    stroke: none;
}
.stroke-example.mid path,
.stroke-example.mid circle {
    stroke: #52B788;
    fill: none;
}
.stroke-example.mid circle {
    fill: #52B788;
}
.stroke-example.ground path {
    stroke: #3A86FF;
}
.stroke-example.note path {
    stroke: #8B5CF6;
}
.hint-chip strong {
    display: block;
    font-size: 12px;
    font-weight: 900;
    margin-bottom: 1px;
}
.hint-chip span {
    display: block;
    font-size: 10px;
    color: rgba(23,49,38,.58);
    line-height: 1.35;
}
.canvas-stage {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 9px;
}
.canvas-stage > * {
    width: 100%;
}
.compact-controls {
    width: 100%;
    padding: 10px;
}
.control-row {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}
.control-row + .control-row {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(47,123,88,.08);
}
.mode-group,
.selection-group,
.action-group,
.color-group,
.brush-group {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}
.mode-group {
    flex: 1;
}
.selection-group {
    flex: 1 1 100%;
}
.mode-group .inspire-tool-btn {
    flex: 1;
    text-align: center;
    white-space: nowrap;
}
.selection-group .inspire-tool-btn {
    flex: 1;
    text-align: center;
    white-space: nowrap;
}
.action-group .inspire-tool-btn {
    white-space: nowrap;
}
.color-group {
    flex: 1;
    justify-content: flex-start;
}
.brush-group {
    flex: 0 0 132px;
    justify-content: flex-end;
}
.brush-label {
    font-size: 11px;
    color: rgba(23,49,38,.56);
    white-space: nowrap;
}
.color-dot {
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
}
.custom-color-dot {
    position: relative;
    display: inline-grid;
    place-items: center;
    background: conic-gradient(#E76F51, #E9C46A, #52B788, #3A86FF, #8B5CF6, #E76F51);
}
.custom-color-dot input {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}
.custom-color-dot span {
    width: 16px;
    height: 16px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: rgba(255,255,248,.92);
    color: #173126;
    font-size: 14px;
    line-height: 1;
    font-weight: 900;
}
.brush-range {
    width: 92px;
}
.settings-strip {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 8px 2px 0;
}
.settings-summary {
    font-size: 11px;
    color: rgba(23,49,38,.58);
    line-height: 1.35;
    min-width: 0;
}
.setting-pill {
    border: 1px solid rgba(47,123,88,.18);
    background: rgba(47,123,88,.10);
    color: #2F7B58;
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 900;
    white-space: nowrap;
    cursor: pointer;
}
.settings-modal {
    position: fixed;
    inset: 0;
    z-index: 1200;
    display: none;
    align-items: flex-end;
    justify-content: center;
    background: rgba(7,18,13,.38);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.settings-modal.visible {
    display: flex;
}
.settings-sheet {
    width: min(100%, 430px);
    max-height: calc(78vh - 72px);
    overflow: auto;
    border-radius: 28px 28px 0 0;
    border: 1px solid rgba(47,123,88,.14);
    background:
        linear-gradient(180deg, rgba(255,255,248,.96), rgba(246,250,241,.96)),
        #FFFDF4;
    padding: 18px;
    margin-bottom: 78px;
    box-shadow: 0 -22px 50px rgba(38,70,52,.22);
}
.settings-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}
.settings-head strong {
    font-size: 16px;
    color: #173126;
}
.settings-head button,
.settings-done {
    border: none;
    background: #2F7B58;
    color: #F8FAF2;
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 900;
    cursor: pointer;
}
.settings-note {
    font-size: 11px;
    color: rgba(23,49,38,.58);
    line-height: 1.5;
    margin-bottom: 14px;
}
.settings-section {
    margin-top: 14px;
}
.settings-section-title {
    font-size: 13px;
    color: #173126;
    font-weight: 900;
    margin-bottom: 8px;
}
.settings-done {
    width: 100%;
    margin-top: 16px;
    padding: 12px;
}
.settings-sheet .lens-grid {
    grid-template-columns: 1fr;
}
.settings-sheet .lens-card {
    min-height: 0;
    display: block;
}
.settings-sheet .agency-row {
    padding: 12px;
    border-radius: 18px;
    background: rgba(47,123,88,.06);
}
.clear-confirm-modal {
    position: fixed;
    inset: 0;
    z-index: 1210;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: rgba(7,18,13,.42);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.clear-confirm-modal.visible {
    display: flex;
}
.clear-confirm-sheet {
    width: min(100%, 360px);
    border-radius: 8px;
    background: #FFFDF4;
    border: 1px solid rgba(47,123,88,.16);
    box-shadow: 0 22px 56px rgba(12,34,24,.24);
    padding: 18px;
    color: #173126;
}
.clear-confirm-title {
    font-size: 16px;
    line-height: 1.35;
    font-weight: 950;
    margin-bottom: 8px;
}
.clear-confirm-text {
    color: rgba(23,49,38,.68);
    font-size: 13px;
    line-height: 1.55;
}
.clear-confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 18px;
}
.clear-confirm-actions button {
    border: 0;
    border-radius: 999px;
    min-width: 72px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 900;
    cursor: pointer;
}
.clear-confirm-actions .secondary {
    background: rgba(47,123,88,.10);
    color: #2F7B58;
}
.clear-confirm-actions .danger {
    background: #E76F51;
    color: #FFFDF4;
}
.stroke-guide-modal {
    position: fixed;
    inset: 0;
    z-index: 1190;
    display: none;
    align-items: flex-end;
    justify-content: center;
    background: rgba(8,28,20,.28);
}
.stroke-guide-modal.visible {
    display: flex;
}
.stroke-guide-sheet {
    width: min(100%, 470px);
    max-height: 78vh;
    overflow-y: auto;
    padding: 16px;
    border-radius: 24px 24px 0 0;
    border: 1px solid rgba(47,123,88,.16);
    background: rgba(255,255,248,.96);
    box-shadow: 0 -18px 40px rgba(12,34,24,.18);
}
.stroke-guide-head {
    position: sticky;
    top: -16px;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: -2px -2px 12px;
    padding: 2px 2px 10px;
    background: rgba(255,255,248,.96);
}
.stroke-guide-head strong {
    color: #173126;
    font-size: 15px;
    font-weight: 900;
}
.stroke-guide-close {
    border: 1px solid rgba(47,123,88,.14);
    background: rgba(47,123,88,.08);
    color: #2F7B58;
    border-radius: 999px;
    padding: 7px 11px;
    font-size: 12px;
    font-weight: 900;
    cursor: pointer;
}
.stroke-guide-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.stroke-guide-card {
    border: 1px solid rgba(47,123,88,.12);
    border-radius: 16px;
    padding: 10px;
    background: rgba(47,123,88,.05);
}
.stroke-guide-card .stroke-example {
    display: block;
    grid-row: auto;
    height: 46px;
    margin-bottom: 8px;
    border-radius: 12px;
}
.stroke-guide-card strong {
    display: block;
    color: #173126;
    font-size: 12px;
    font-weight: 900;
    margin-bottom: 3px;
}
.stroke-guide-card span {
    display: block;
    color: rgba(23,49,38,.58);
    font-size: 10px;
    line-height: 1.4;
}
.inspire-save-card {
    width: min(340px, calc(100vw - 48px));
    border-radius: 8px;
    padding: 20px 18px 16px;
    color: #173126;
    background: #FFFDF4;
    border: 1px solid rgba(47,123,88,.16);
    box-shadow: 0 22px 56px rgba(12,34,24,.24);
}
.q-card.inspire-save-card,
.q-dialog__inner > .q-card.inspire-save-card {
    color: #173126 !important;
    background: #FFFDF4 !important;
    border: 1px solid rgba(47,123,88,.18) !important;
}
.q-card.inspire-save-card *,
.q-dialog__inner > .q-card.inspire-save-card * {
    color: inherit;
}
.q-card.inspire-save-card .inspire-save-copy,
.q-dialog__inner > .q-card.inspire-save-card .inspire-save-copy {
    color: rgba(23,49,38,.76) !important;
}
.inspire-save-title {
    font-size: 17px;
    line-height: 1.35;
    font-weight: 950;
    text-align: center;
}
.inspire-save-copy {
    margin-top: 8px;
    color: rgba(23,49,38,.68);
    font-size: 13px;
    line-height: 1.55;
    text-align: center;
}
.inspire-save-action {
    margin-top: 16px;
}
.q-card.inspire-save-card .q-btn.inspire-save-action,
.q-dialog__inner > .q-card.inspire-save-card .q-btn.inspire-save-action {
    background: #2F7B58 !important;
    color: #F8FAF2 !important;
    border-radius: 999px !important;
}
@media (min-width: 900px) and (orientation: landscape) {
    .inspire-shell {
        display: grid !important;
        width: min(100%, 1520px);
        margin: 0 auto;
        grid-template-columns: minmax(720px, 1fr) 340px;
        gap: 16px 28px;
        align-items: start !important;
        padding: 20px clamp(16px, 1.8vw, 28px) 122px;
    }

    .inspire-brief {
        grid-column: 2;
        grid-row: 1;
    }

    .canvas-stage {
        grid-column: 1;
        grid-row: 1 / span 8;
        position: sticky;
        top: 92px;
    }

    .inspire-canvas-wrap {
        min-height: 0;
        border-radius: 24px;
    }

    .compact-controls {
        border-radius: 20px;
    }

    .control-row {
        flex-wrap: wrap;
    }

    .mode-group {
        flex: 1 1 100%;
    }

    .color-group {
        flex: 1 1 160px;
    }

    .brush-group {
        flex: 0 0 148px;
    }

    .inspire-shell > div:has(.inspire-meta-row),
    .inspire-shell > div:has(#annotation-box),
    .inspire-error,
    .inspire-loading,
    .inspire-shell > .q-btn {
        grid-column: 2;
    }

    #layer-panel {
        max-height: calc(100vh - 470px);
        overflow: auto;
    }

    .settings-sheet {
        width: min(720px, calc(100vw - 72px));
        border-radius: 24px;
        margin-bottom: 96px;
    }

    .stroke-guide-sheet {
        width: min(760px, calc(100vw - 72px));
        border-radius: 24px;
        margin-bottom: 96px;
    }

    .stroke-guide-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}
#inspire-result-area {
    order: 3;
}
</style>
"""


def _image_url(session) -> str:
    return media_url(getattr(session, 'uploaded_image_path', '') if session else '', display=True)


def _canvas_json_url(session) -> str:
    return media_url(getattr(session, 'canvas_json_path', '') if session else '')


def _clamp_number(value, default: float, min_value: float, max_value: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(min_value, min(max_value, number))


def _clean_text(value, max_len: int = 120) -> str:
    return str(value or '').strip()[:max_len]


def _normalize_sketch_payload(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError('invalid sketch payload')

    results = []
    for item in (data.get('results') if isinstance(data.get('results'), list) else [])[:40]:
        if not isinstance(item, dict):
            continue
        name = _clean_text(item.get('elemName') or item.get('name'), 80)
        icon = _clean_text(item.get('icon'), 24)
        if not name and not icon:
            continue
        results.append({
            'elemName': name,
            'icon': icon,
            'confidence': round(_clamp_number(item.get('confidence'), 0.5, 0.0, 1.0), 3),
            'shapeType': _clean_text(item.get('shapeType'), 40),
            'tint': _clean_text(item.get('tint'), 40),
            'zone': _clean_text(item.get('zone'), 40),
            'x': round(_clamp_number(item.get('x'), 50.0, 0.0, 100.0), 1),
            'y': round(_clamp_number(item.get('y'), 50.0, 0.0, 100.0), 1),
            'color': _clean_text(item.get('color'), 32),
            'source': _clean_text(item.get('source') or 'auto', 24),
        })

    annotations = []
    for item in (data.get('userAnnotations') if isinstance(data.get('userAnnotations'), list) else [])[:40]:
        if not isinstance(item, dict):
            continue
        label = _clean_text(item.get('userLabel'), 80)
        if not label:
            continue
        annotations.append({
            'userLabel': label,
            'strokeId': _clean_text(item.get('strokeId'), 80),
            'strokeIds': [_clean_text(v, 80) for v in (item.get('strokeIds') or [])[:20]],
            'groupId': _clean_text(item.get('groupId'), 80),
            'isGroup': bool(item.get('isGroup')),
            'x': round(_clamp_number(item.get('x'), 50.0, 0.0, 100.0), 1),
            'y': round(_clamp_number(item.get('y'), 50.0, 0.0, 100.0), 1),
            'bboxW': round(_clamp_number(item.get('bboxW'), 0.0, 0.0, 100.0), 1),
            'bboxH': round(_clamp_number(item.get('bboxH'), 0.0, 0.0, 100.0), 1),
            'aspectRatio': round(_clamp_number(item.get('aspectRatio'), 1.0, 0.05, 20.0), 2),
            'color': _clean_text(item.get('color'), 32),
            'shapeType': _clean_text(item.get('shapeType'), 40),
            'zone': _clean_text(item.get('zone'), 40),
        })

    mood = data.get('moodParams') if isinstance(data.get('moodParams'), dict) else None
    mood_params = None
    if mood:
        mood_params = {
            'green': round(_clamp_number(mood.get('green'), 50.0, 0.0, 100.0), 1),
            'urban': round(_clamp_number(mood.get('urban'), 50.0, 0.0, 100.0), 1),
            'vitality': round(_clamp_number(mood.get('vitality'), 50.0, 0.0, 100.0), 1),
            'light': round(_clamp_number(mood.get('light'), 50.0, 0.0, 100.0), 1),
            'moodLabel': mood.get('moodLabel') if isinstance(mood.get('moodLabel'), dict) else None,
        }

    scene_intent = data.get('sceneIntent') if isinstance(data.get('sceneIntent'), dict) else {}
    normalized_intent = {
        'dominantMood': _clean_text(scene_intent.get('dominantMood'), 80),
        'complexityLevel': _clean_text(scene_intent.get('complexityLevel') or 'medium', 24),
        'creativeLens': _clean_text(scene_intent.get('creativeLens'), 40),
        'creativeLensLabel': _clean_text(scene_intent.get('creativeLensLabel'), 80),
        'creativeLensPrompt': _clean_text(scene_intent.get('creativeLensPrompt'), 240),
        'aiAgency': round(_clamp_number(scene_intent.get('aiAgency'), 70.0, 20.0, 100.0), 1),
        'spatialPatterns': scene_intent.get('spatialPatterns')[:20] if isinstance(scene_intent.get('spatialPatterns'), list) else [],
        'proximityRelations': scene_intent.get('proximityRelations')[:20] if isinstance(scene_intent.get('proximityRelations'), list) else [],
    }

    stroke_log = []
    for item in (data.get('strokeLog') if isinstance(data.get('strokeLog'), list) else [])[:80]:
        if not isinstance(item, dict):
            continue
        stroke_log.append({
            'strokeId': _clean_text(item.get('strokeId'), 80),
            'autoLabel': _clean_text(item.get('autoLabel'), 80),
            'userLabel': _clean_text(item.get('userLabel'), 80),
            'source': _clean_text(item.get('source'), 24),
            'shapeType': _clean_text(item.get('shapeType'), 40),
            'zone': _clean_text(item.get('zone'), 40),
            'x': round(_clamp_number(item.get('x'), 50.0, 0.0, 100.0), 1),
            'y': round(_clamp_number(item.get('y'), 50.0, 0.0, 100.0), 1),
            'bboxW': round(_clamp_number(item.get('bboxW'), 0.0, 0.0, 100.0), 1),
            'bboxH': round(_clamp_number(item.get('bboxH'), 0.0, 0.0, 100.0), 1),
            'aspectRatio': round(_clamp_number(item.get('aspectRatio'), 1.0, 0.05, 20.0), 2),
            'color': _clean_text(item.get('color'), 32),
            'explanation': _clean_text(item.get('explanation'), 260),
        })

    return {
        'type': 'element' if data.get('type') == 'element' else 'mood',
        'results': results,
        'moodParams': mood_params,
        'strokeCount': int(_clamp_number(data.get('strokeCount'), len(stroke_log), 0, 80)),
        'sceneIntent': normalized_intent,
        'interactionRound': int(_clamp_number(data.get('interactionRound'), 1, 1, 200)),
        'strokeLog': stroke_log,
        'userAnnotations': annotations,
        'hciMetrics': data.get('hciMetrics') if isinstance(data.get('hciMetrics'), dict) else {},
    }


def _build_inspire_bootstrap(init_payload: str) -> str:
    return f'''<script>
(function() {{
    var initPayload = {init_payload};

    function showFallback(message) {{
        var fallback = document.getElementById('inspire-fallback');
        if (!fallback) return;
        fallback.textContent = message || '画布引擎未加载成功，请刷新页面。';
        fallback.style.display = 'block';
    }}

    function loadScriptOnce(src, globalName, marker) {{
        if (globalName && window[globalName]) return Promise.resolve();
        return new Promise(function(resolve, reject) {{
            var existing = document.querySelector('script[data-inspire-loader="' + marker + '"]');
            if (existing) {{
                if (globalName && window[globalName]) {{
                    resolve();
                    return;
                }}
                existing.remove();
            }}
            var script = document.createElement('script');
            script.src = src;
            script.dataset.inspireLoader = marker;
            script.onload = function() {{ resolve(); }};
            script.onerror = function() {{ reject(new Error(src)); }};
            document.head.appendChild(script);
        }});
    }}

    function initWhenReady(attempt) {{
        if (window.InspireCanvas && document.getElementById('inspire-canvas')) {{
            window.InspireCanvas.init(initPayload);
            return;
        }}
        if (attempt < 80) {{
            setTimeout(function() {{ initWhenReady(attempt + 1); }}, 100);
            return;
        }}
        showFallback('画布引擎未加载成功，请刷新页面。');
    }}

    loadScriptOnce('/static/vendor/fabric.min.js', 'fabric', 'fabric')
        .then(function() {{ return loadScriptOnce('/static/sketch_analyzer.js', 'SketchAnalyzer', 'sketch-analyzer'); }})
        .then(function() {{ return loadScriptOnce('/static/sketch_composer.js', 'SketchComposer', 'sketch-composer'); }})
        .then(function() {{
            return loadScriptOnce(
                '/static/inspire_canvas.js?v=inspire-prompt-force-20260612',
                'InspireCanvas',
                'inspire-canvas'
            );
        }})
        .then(function() {{ initWhenReady(0); }})
        .catch(function() {{ showFallback('画布引擎未加载成功，请刷新页面。'); }});
}})();
</script>'''


def create_inspire_page():
    @ui.page('/inspire-mode')
    async def inspire_mode(sid: str = '', back: str = ''):
        ui.add_head_html(META_VIEWPORT)
        ui.add_head_html(COMMON_STYLE)
        ui.add_head_html(INSPIRE_CSS)

        session = get_session(sid) if sid else None

        img_url = _image_url(session)
        canvas_json_url = _canvas_json_url(session)
        back_url = f'/result?sid={sid}&back=records' if back == 'result' else (
            '/records' if back == 'records' else f'/mode-select?sid={sid}'
        )

        with ui.column().classes('mobile-page light-page').style('gap:0'):
            with ui.row().style(LIGHT_TOP_BAR_STYLE + 'padding-right:68px;gap:8px;'):
                ui.button(icon='arrow_back', on_click=lambda: smooth_navigate(back_url)).props('flat round dense')
                ui.label('灵感创想').style('font-size:18px;font-weight:900;margin-left:8px;')
                ui.element('div').style('flex:1')
                ui.button('清除', on_click=lambda: ui.run_javascript('InspireCanvas.clear();'), color=None).props(
                    'unelevated no-caps'
                ).classes('inspire-top-action clear')

                save_btn = ui.button('保存', color=None).props('unelevated no-caps').classes('inspire-top-action save')

            bottom_nav(light=True)

            with ui.column().classes('inspire-shell'):
                with ui.element('div').classes('inspire-card inspire-brief'):
                    ui.html(
                        '<div class="inspire-brief-head">'
                        '<div class="inspire-brief-title">在画布上进行灵感表达</div>'
                        '<div class="inspire-brief-actions">'
                        '<button type="button" class="stroke-guide-btn" onclick="event.stopPropagation();InspireCanvas.openStrokeGuide()">点击查看笔画提示</button>'
                        '</div>'
                        '</div>',
                        sanitize=False,
                    )

                with ui.element('div').classes('canvas-stage'):
                    ui.html(
                        '<div id="inspire-fallback" class="inspire-fallback">'
                        '画布引擎未加载成功，请检查网络或刷新页面。'
                        '</div>'
                        '<div id="inspire-canvas-wrapper" class="inspire-canvas-wrap">'
                        '<canvas id="inspire-canvas"></canvas>'
                        '<div id="inspire-inline-label" class="inspire-inline-label" style="display:none"></div>'
                        '</div>',
                        sanitize=False,
                    ).style('width:100%;')

                    ui.html(
                        '<div class="inspire-card compact-controls">'
                        '<div class="control-row">'
                        '<div class="mode-group">'
                        '<button id="mode-draw-btn" class="inspire-tool-btn active" onclick="InspireCanvas.setMode(\'draw\')">画笔</button>'
                        '<button id="mode-select-btn" class="inspire-tool-btn" onclick="InspireCanvas.setMode(\'select\')">选择标注</button>'
                        '<button id="layer-toggle-btn" class="inspire-tool-btn active" onclick="InspireCanvas.toggleLayers()">图层</button>'
                        '</div>'
                        '<div class="selection-group">'
                        '<button id="multi-select-btn" class="inspire-tool-btn" onclick="InspireCanvas.toggleMultiSelect()">多选</button>'
                        '<button id="group-selected-btn" class="inspire-tool-btn" onclick="InspireCanvas.groupSelected()" disabled>组合</button>'
                        '<button id="ungroup-selected-btn" class="inspire-tool-btn" onclick="InspireCanvas.ungroupSelected()" disabled>解组</button>'
                        '</div>'
                        '<div class="action-group">'
                        '<button class="inspire-tool-btn" onclick="InspireCanvas.undo()">↩ 撤销</button>'
                        '</div>'
                        '</div>'
                        '<div class="control-row">'
                        '<div class="color-group" aria-label="画笔颜色">'
                        '<div class="color-dot selected" data-color="#2D6A4F" style="background:#2D6A4F" onclick="InspireCanvas.setColor(\'#2D6A4F\')"></div>'
                        '<div class="color-dot" data-color="#52B788" style="background:#52B788" onclick="InspireCanvas.setColor(\'#52B788\')"></div>'
                        '<div class="color-dot" data-color="#E76F51" style="background:#E76F51" onclick="InspireCanvas.setColor(\'#E76F51\')"></div>'
                        '<div class="color-dot" data-color="#3A86FF" style="background:#3A86FF" onclick="InspireCanvas.setColor(\'#3A86FF\')"></div>'
                        '<div class="color-dot" data-color="#8B5CF6" style="background:#8B5CF6" onclick="InspireCanvas.setColor(\'#8B5CF6\')"></div>'
                        '<label id="custom-color-dot" class="color-dot custom-color-dot" title="自定义颜色" aria-label="自定义颜色">'
                        '<input id="custom-color-input" type="color" value="#2D6A4F" onchange="InspireCanvas.setColor(this.value, true)">'
                        '<span>+</span>'
                        '</label>'
                        '</div>'
                        '<div class="brush-group"><span class="brush-label">笔粗</span>'
                        '<input type="range" class="brush-range" min="1" max="20" value="4" oninput="InspireCanvas.setBrushSize(parseInt(this.value,10))">'
                        '</div>'
                        '</div>'
                        '</div>',
                        sanitize=False,
                    ).style('width:100%;')

                ui.html(
                    '<div class="inspire-meta-row">'
                    '<span id="inspire-stroke-count">已绘制 0 笔</span>'
                    '<span id="inspire-analyze-state">画完后系统自动分析</span>'
                    '</div>'
                    '<div class="settings-strip">'
                    '<div id="settings-summary" class="settings-summary">创意方向：疗愈自然 · AI 采纳 70%</div>'
                    '<button class="setting-pill" onclick="InspireCanvas.openSettings()">创作设置</button>'
                    '</div>',
                    sanitize=False,
                ).style('width:100%;')

                ui.html(
                    '<div id="settings-modal" class="settings-modal" onclick="InspireCanvas.closeSettings(event)">'
                    '<div class="settings-sheet" onclick="event.stopPropagation()">'
                    '<div class="settings-head"><strong>创作设置</strong>'
                    '<button type="button" onclick="event.preventDefault();event.stopPropagation();InspireCanvas.closeSettings();return false;">完成</button></div>'
                    '<div class="settings-note">创意方向和 AI 采纳强度会写入生成提示词，影响最终生成效果。</div>'
                    '<div class="settings-section">'
                    '<div class="settings-section-title">创意方向</div>'
                    '<div class="lens-grid">'
                    '<div class="lens-card active" data-lens="restorative" onclick="InspireCanvas.setLens(\'restorative\')">'
                    '<strong>疗愈自然</strong><span>提高恢复感、绿色覆盖与柔和光影</span></div>'
                    '<div class="lens-card" data-lens="playful" onclick="InspireCanvas.setLens(\'playful\')">'
                    '<strong>自由灵感</strong><span>保留手绘偶然性，鼓励更发散的生成</span></div>'
                    '<div class="lens-card" data-lens="minimal" onclick="InspireCanvas.setLens(\'minimal\')">'
                    '<strong>克制写实</strong><span>保留原图结构，只做可落地的环境微更新</span></div>'
                    '</div></div>'
                    '<div class="settings-section">'
                    '<div class="settings-section-title">AI 采纳强度</div>'
                    '<div class="agency-row">'
                    '<span style="font-size:11px;color:rgba(23,49,38,.58)">接近原图</span>'
                    '<input id="agency-slider" type="range" min="20" max="100" value="70" '
                    'oninput="InspireCanvas.setAgency(parseInt(this.value,10))">'
                    '<span style="font-size:11px;color:rgba(23,49,38,.58)">更多创意</span>'
                    '<span id="agency-value" class="agency-value">70%</span>'
                    '</div></div>'
                    '<button type="button" class="settings-done" onclick="event.preventDefault();event.stopPropagation();InspireCanvas.closeSettings();return false;">完成设置</button>'
                    '</div></div>',
                    sanitize=False,
                )

                ui.html(
                    '<div id="clear-confirm-modal" class="clear-confirm-modal" onclick="InspireCanvas.cancelClear(event)">'
                    '<div class="clear-confirm-sheet" onclick="event.stopPropagation()">'
                    '<div class="clear-confirm-title">确认清除所有笔画？</div>'
                    '<div class="clear-confirm-text">当前画布上的笔画和标注会被全部清除，此操作不能撤销。</div>'
                    '<div class="clear-confirm-actions">'
                    '<button type="button" class="secondary" onclick="event.preventDefault();event.stopPropagation();InspireCanvas.cancelClear();return false;">否</button>'
                    '<button type="button" class="danger" onclick="event.preventDefault();event.stopPropagation();InspireCanvas.confirmClear();return false;">是</button>'
                    '</div></div></div>'
                    '<div id="stroke-guide-modal" class="stroke-guide-modal" onclick="InspireCanvas.closeStrokeGuide(event)">'
                    '<div class="stroke-guide-sheet" onclick="event.stopPropagation()">'
                    '<div class="stroke-guide-head"><strong>笔画示意</strong>'
                    '<button type="button" class="stroke-guide-close" onclick="event.preventDefault();event.stopPropagation();InspireCanvas.closeStrokeGuide();return false;">完成</button></div>'
                    '<div class="stroke-guide-grid">'
                    '<div class="stroke-guide-card"><div class="stroke-example sky">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M14 30 C35 10, 63 12, 82 30"/></svg>'
                    '</div><strong>单笔弧线 / 天空边界</strong><span>一笔曲线；常识别为云、远山、柔和边界</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example sky">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><circle cx="70" cy="23" r="5"/></svg>'
                    '</div><strong>单笔点按 / 小型元素</strong><span>一次点按或短点；常识别为飞鸟、星点、花点</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example mid">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M70 38 L70 8"/></svg>'
                    '</div><strong>单笔竖线 / 竹木树干</strong><span>一笔竖向线；常识别为竹、树干、立柱</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example mid">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M35 31 C28 19, 43 12, 52 20 C57 8, 77 11, 75 24 C92 18, 96 35, 78 35 C66 41, 45 39, 35 31"/></svg>'
                    '</div><strong>单笔团簇 / 树冠灌木</strong><span>一笔连续绕画；常识别为树冠、灌木、花丛</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example ground">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M14 24 C28 10, 42 36, 56 23 S85 11, 101 24 S122 35, 132 17"/></svg>'
                    '</div><strong>单笔波线 / 水线小溪</strong><span>一笔连续波线；常识别为水线、路径、柔和边界</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example ground">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M28 31 C38 12, 76 9, 96 23 C88 42, 45 43, 28 31"/></svg>'
                    '</div><strong>单笔围合 / 花坛水池</strong><span>首尾接近的一笔；常识别为花坛、水池、围合区域</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example ground">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M60 33 L78 15"/></svg>'
                    '</div><strong>单笔短线 / 草地纹理</strong><span>一笔短划；常识别为草、地被、细碎肌理</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example note">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M16 31 L35 20 L53 27 L75 13 L99 25 L124 16"/></svg>'
                    '</div><strong>单笔折线 / 山脊远山</strong><span>一笔折线；常识别为山脊、天际线、碎石边界</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example sky">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M48 32 C30 10, 80 8, 70 31 C66 44, 34 41, 48 22"/></svg>'
                    '</div><strong>单笔旋绕 / 花丛装饰</strong><span>一笔旋转形；常识别为花丛、藤蔓、装饰节点</span></div>'
                    '<div class="stroke-guide-card"><div class="stroke-example note">'
                    '<svg viewBox="0 0 140 46" aria-hidden="true"><path d="M22 30 C36 14, 53 14, 66 28"/><path d="M76 34 C86 16, 106 17, 116 30"/></svg>'
                    '</div><strong>多笔对象 / 先多选组合</strong><span>每一笔会先独立识别；同一对象由多笔组成时，先多选再组合</span></div>'
                    '</div></div></div>',
                    sanitize=False,
                )

                ui.html(
                    '<div id="annotation-box" class="annotation-box">'
                    '<input id="annotation-input" placeholder="修正 AI 理解，例如：竹林、小溪、圆形花坛">'
                    '<button class="secondary" onclick="InspireCanvas.duplicateSelected()">复制</button>'
                    '<button class="danger" onclick="InspireCanvas.deleteSelected()">删除</button>'
                    '<button onclick="InspireCanvas.confirmAnnotation()">确认标注</button>'
                    '</div>'
                    '<div id="layer-panel" style="display:none"></div>'
                    '',
                    sanitize=False,
                ).style('width:100%;')

                error_label = ui.label('').classes('inspire-error')
                loading_row = ui.element('div').classes('inspire-loading')
                with loading_row:
                    ui.html(
                        '<div class="inspire-loading-head">'
                        '<span>AI 正在生成</span><span>请稍候</span>'
                        '</div>'
                        '<div class="inspire-loading-note">'
                        'AI 会在后台生成，可前往其他页面；生成完成后会在草稿箱通知你。'
                        '</div>'
                        '<div class="inspire-loading-track"><div class="inspire-loading-fill"></div></div>',
                        sanitize=False,
                    )

                gen_btn = ui.button('✦ AI 生成效果图', on_click=lambda: generate_sketch()).props('no-caps unelevated').style(
                    LIGHT_PRIMARY_BTN_STYLE
                )

        with ui.dialog() as save_dialog, ui.card().classes('inspire-save-card'):
            save_dialog_title = ui.label('已保存进度').classes('inspire-save-title')
            save_dialog_copy = ui.label('当前画布和画笔位置已同步到草稿箱。').classes('inspire-save-copy')
            ui.button('知道了', on_click=save_dialog.close).props('unelevated no-caps').classes('inspire-save-action').style(
                'width:100%;background:#2F7B58;color:#F8FAF2;font-weight:900;'
            )

        def _show_save_dialog(title: str, copy: str) -> None:
            save_dialog_title.set_text(title)
            save_dialog_copy.set_text(copy)
            save_dialog.open()

        async def save_draft():
            if not session:
                _show_save_dialog('无法保存', '当前会话无效，请返回重新进入。')
                return

            save_btn.disable()
            try:
                session.mode_used = 'inspire'
                submit_json = await ui.run_javascript('InspireCanvas.getSubmitData()', timeout=6.0)
                paths_json = await ui.run_javascript('InspireCanvas.getPathsJSON()', timeout=8.0)
                canvas_data_url = await ui.run_javascript('InspireCanvas.getCanvasDataURL()', timeout=8.0)

                if submit_json and submit_json != 'null':
                    data = _normalize_sketch_payload(json.loads(submit_json))
                    session.sketch_data = data
                    if data.get('type') == 'element':
                        session.placed_elements = data.get('results', [])
                    if data.get('moodParams'):
                        mp = data['moodParams']
                        session.green_level = mp.get('green', 50)
                        session.urban_level = mp.get('urban', 50)
                        session.vitality_level = mp.get('vitality', 50)
                        session.light_warmth = mp.get('light', 50)

                if paths_json is not None:
                    try:
                        save_canvas_json(sid, paths_json or '[]')
                    except Exception:
                        pass
                if canvas_data_url and canvas_data_url.startswith('data:image'):
                    try:
                        save_canvas_snapshot(sid, canvas_data_url)
                    except Exception:
                        pass

                _show_save_dialog('已保存进度', '当前画布和画笔位置已同步到草稿箱。')
            except Exception as exc:
                _show_save_dialog('保存失败', str(exc)[:160])
            finally:
                save_btn.enable()

        async def generate_sketch():
            upload_path = resolve_media_path(session.uploaded_image_path if session else '')
            if not session or not upload_path:
                ui.notify('请先上传原始图片，再进入灵感创想', type='warning')
                return

            submit_json = await ui.run_javascript('InspireCanvas.getSubmitData()', timeout=6.0)
            if not submit_json or submit_json == 'null':
                ui.notify('请先在画布上画几笔，或保存一个明确的创意方向', type='warning')
                return

            try:
                data = _normalize_sketch_payload(json.loads(submit_json))
            except Exception:
                ui.notify('画布数据解析失败，请重试', type='negative')
                return

            if not data or int(data.get('strokeCount') or 0) <= 0:
                ui.notify('请先在画布上画几笔', type='warning')
                return

            gen_btn.disable()
            loading_row.style('display:block')
            error_label.style('display:none')

            try:
                session.mode_used = 'inspire'
                canvas_data_url = await ui.run_javascript('InspireCanvas.getCanvasDataURL()', timeout=8.0)
                paths_json = await ui.run_javascript('InspireCanvas.getPathsJSON()', timeout=8.0)

                session.sketch_data = data
                if data.get('type') == 'element':
                    session.placed_elements = data.get('results', [])
                if data.get('moodParams'):
                    mp = data['moodParams']
                    session.green_level = mp.get('green', 50)
                    session.urban_level = mp.get('urban', 50)
                    session.vitality_level = mp.get('vitality', 50)
                    session.light_warmth = mp.get('light', 50)
                if canvas_data_url and canvas_data_url.startswith('data:image'):
                    try:
                        save_canvas_snapshot(sid, canvas_data_url)
                    except Exception:
                        pass
                if paths_json is not None:
                    try:
                        save_canvas_json(sid, paths_json or '[]')
                    except Exception:
                        pass

                from app.routers.api import start_sketch_generation_job
                started = start_sketch_generation_job(
                    sid,
                    str(upload_path),
                    data,
                )
                if not started:
                    raise RuntimeError('AI 已在后台生成中，请稍候。')
                await ui.run_javascript('InspireCanvas.advanceRound();', timeout=1.0)
                _show_save_dialog('AI 会在后台生成', '可以前往其他页面，生成完成后会在草稿箱通知你。')
                gen_btn.set_text('后台生成中')
            except Exception as exc:
                error_label.set_text(f'生成失败：{exc}')
                error_label.style('display:block')
                gen_btn.enable()
                loading_row.style('display:none')

        save_btn.on('click', save_draft)

        init_payload = json.dumps({'imageUrl': img_url, 'sessionId': sid, 'restoreUrl': canvas_json_url})
        ui.add_body_html(_build_inspire_bootstrap(init_payload))
