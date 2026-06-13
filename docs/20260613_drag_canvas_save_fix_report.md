# 2026-06-13 自由创作历史记录保存修复报告

## 问题

- 从草稿箱/历史记录进入自由创作后点击保存，会出现 `JavaScript did not respond within 8.0 s` 或 `消息太长`。
- 旧记录 `34dafa28e4e8` 的元素摆放图没有正确写入草稿箱记录和本地科研归档。
- 操作图在页面和归档中清晰度不足，部分保存结果只有展示图分辨率。

## 根因

- 保存画布时把整张 PNG 的 `data:image/...` 大文本通过 NiceGUI WebSocket 回传给 Python，高清图会超时或超过 WebSocket 消息大小限制。
- 自由创作画布初始化使用的是 `display=True` 展示优化图，导致后续导出的操作图最高只能达到展示图尺寸。
- 浏览器缓存了旧版 `canvas_editor.js`，部署后仍可能继续使用旧保存逻辑。

## 已执行修改

- `f7e1a1c Make drag draft save resilient`
  - 保存拆分为元素坐标、画布 JSON、元素布局图三个步骤。
  - 图片保存失败时保留结构化记录，并回退生成可追溯的元素布局图。
- `4cbccfb Upload drag canvas snapshots over HTTP`
  - 新增 `/api/canvas-snapshot` HTTP 接口。
  - 前端通过 `EnvCanvas.uploadCanvasSnapshot()` 直接 POST 图片到后端，避免 WebSocket 传大图。
- `6f8aed7 Bust cached drag canvas script`
  - 更新自由创作画布脚本版本号，强制浏览器加载新 JS。
- `1eaee6a Save drag snapshots at higher resolution`
  - 保存倍率恢复到高清上限。
- `ddc1511 Use original image for drag canvas export`
  - 自由创作画布改为加载原始上传图，导出操作图可达到原图分辨率。

## 验证结果

- 线上版本：`ddc1511`
- 线上健康接口：`https://envhealth.cn/api/status` 返回 `{"server":"running","model_loaded":true}`。
- 浏览器实际点击保存 `34dafa28e4e8`：
  - 页面显示：`已保存进度 / 已同步：元素坐标、画布JSON、元素布局图。`
  - 未再出现 `保存失败` 或 `消息太长`。
- 服务器最新操作图：
  - `/home/zm/envhealth/outputs/34dafa28e4e8_canvas_75c5b5.png`
  - 尺寸：`1672 x 941`
- 本地归档路径：
  - `D:\SSH\环境游戏程序\记录\participants\0127_20260612-1\20260612_145409_自由创作_第01次_34dafa28e4e8`
  - `operation_latest.png`：`1672 x 941`
  - `operation_for_generated_01.png`：`1672 x 941`
  - `operation_for_generated_02.png`：`1672 x 941`

## 仍需注意

- 已缺失原始上传文件的旧 Windows 路径记录仍无法补齐，本次归档仍报告 10 个旧文件缺失。
- 旧记录如果没有保存过 Fabric JSON，只能用已有元素坐标恢复布局；本次 `34dafa28e4e8` 已通过重新进入历史记录并点击保存补上真实画布 JSON 与高清操作图。
