# 后端明显问题清单

审查时间：2026-06-02

范围：`main.py`、`app/routers/api.py`、`app/state.py`、`app/db.py`、`app/services/*.py`，以及当前运行中的本地服务 `http://127.0.0.1:6420`。

## P0：导出接口使用硬编码默认密码，当前可直接读取统计数据

涉及位置：

- `app/routers/api.py:25-26`
- `app/routers/api.py:232-258`

问题：

`EXPORT_KEY` 默认值是公开可猜的 `healing2024`。如果部署环境没有显式设置 `HEALING_EXPORT_KEY`，任何知道地址的人都可以访问导出相关接口。当前本地服务已验证：`/api/export/summary?key=healing2024` 返回了真实汇总数据。

影响：

- 研究数据统计可被未授权访问。
- `/api/export/csv` 和 `/api/export/json` 同样只靠这个默认 key 保护，风险更高。

建议：

- 移除默认值，未设置 `HEALING_EXPORT_KEY` 时直接禁用导出接口或启动失败。
- 导出接口增加登录态/管理员权限校验。
- 生产环境轮换当前 key。

## P0：媒体文件接口无权限校验，知道文件名即可读取上传图/结果图

涉及位置：

- `app/routers/api.py:64-73`
- `app/state.py:44-61`

问题：

`/api/image/{filename}` 只根据文件名在 `uploads/outputs` 中查找并返回文件，没有校验当前用户是否拥有对应 session。当前已验证：直接请求 uploads 中任意文件名可以返回图片内容。

影响：

- 上传的环境照片、生成图、画布快照可能被横向读取。
- 文件名虽然带随机片段，但一旦从日志、页面、导出或浏览器缓存泄漏，就没有二次保护。

建议：

- 通过 session 记录反查文件归属，并校验 `app.storage.user.id`。
- 媒体 URL 改为带 session 维度，例如 `/api/session/{sid}/image/{filename}`。
- 对导出数据中的本地路径和文件名做最小化处理。

## P0：多个写接口只信任 `session_id`，没有用户归属校验

涉及位置：

- `app/routers/api.py:37-56`
- `app/routers/api.py:76-84`
- `app/routers/api.py:122-130`
- `app/routers/api.py:162-176`
- `app/routers/api.py:205-219`

问题：

上传、生成、日志写入等接口都从请求体读取 `session_id` 后直接操作对应 session，没有校验该 session 是否属于当前登录用户。`/api/session` 还可以匿名创建 session。

影响：

- 用户 A 如果拿到用户 B 的 session id，可以覆盖 B 的上传图、触发生成、写入日志。
- 生成接口可能被未授权消耗外部图像 API 配额。
- 行为日志和研究数据可能被污染。

建议：

- 所有 session 读写统一走 `require_current_user_session(session_id)`。
- 匿名 `/api/session` 要么删除，要么只创建未绑定临时 session，并在后续绑定时校验。
- 对生成接口增加频率限制和 CSRF/来源校验。

## P1：生成接口对无效 JSON 没有兜底，直接返回 500

涉及位置：

- `app/routers/api.py:76-78`
- `app/routers/api.py:122-124`
- `app/routers/api.py:162-164`

问题：

`/api/generate/slider`、`/api/generate/chat`、`/api/generate/inpaint` 直接 `await request.json()`，不像 `/api/log/action` 那样捕获解析错误。当前已验证：向 `/api/generate/slider` 发送非 JSON body 会返回 500。

影响：

- 普通错误请求会污染服务端错误日志。
- 前端或第三方调用方拿不到稳定的 400 错误结构。

建议：

- 抽一个 `read_json_request()` helper，统一返回 400。
- 对 body 类型、字段类型和长度做显式校验。

## P1：上传接口只限制大小，不验证文件确实是图片

涉及位置：

- `app/routers/api.py:37-53`
- `app/state.py:137-143`

问题：

上传接口只检查文件大小，然后直接按原扩展名保存。没有 MIME、扩展名白名单、Pillow 解码验证，也没有对畸形图片做异常处理。

影响：

- 非图片文件可以进入 `uploads`，后续生成时在 `_image_to_base64()` 处失败。
- 如果 Pillow 遇到异常/超大像素图片，可能造成 500 或资源消耗。

建议：

- 保存前用 Pillow `Image.verify()` 或安全解码确认格式。
- 限制格式为 JPEG/PNG/WebP，限制像素总量。
- 上传失败返回 400，并清理已写入的临时文件。

## P1：滑杆/拖拽/灵感生成只支持 Markdown 图片 URL 响应，和对话生成解析能力不一致

涉及位置：

- `app/services/sd_service.py:294-325`
- `app/services/chat_service.py:87-112`

问题：

`sd_service._call_api()` 只从 `choices[0].message.content` 中解析 Markdown 图片 URL 或直接 URL；如果图像 API 返回 `data[0].url`、`data[0].b64_json` 或 `b64_json`，会报“未找到图片链接”。而 `chat_service` 已经支持这些格式。

影响：

- 同一个外部图像 API 响应格式下，对话模式可能成功，滑杆/拖拽/灵感模式失败。
- 更换模型或供应商后，部分模式会突然不可用。

建议：

- 把 `chat_service._extract_image_reference()` 抽成共享函数。
- `sd_service._call_api()` 同时支持 `data[].url`、`b64_json`、data URL 和 Markdown URL。

## P1：数据库迁移把 session 字段加到了 users 表，迁移脚本缺少列白名单和错误记录

涉及位置：

- `app/db.py:50-128`
- 当前数据库结构：`users` 表存在 `generation_count`、`chat_moods`、`chat_extra` 等非用户字段。

问题：

迁移逻辑里 `users` 表新增了 `generation_count`，当前数据库中还混入了 `chat_moods/chat_extra`。同时迁移失败被裸 `except Exception: pass` 吞掉，没有日志。

影响：

- 数据库结构逐渐偏离代码预期，后续导出/统计容易混淆。
- 真正的迁移失败无法被发现。
- 老库如果缺少 `sessions.generation_count`，当前迁移不会补，后续更新可能报 `no such column`。

建议：

- 建立显式 schema version 表。
- 按表维护严格迁移列表。
- 捕获重复列错误可以忽略，但其他异常要记录日志。
- 清理当前库中误加到 `users` 的无关列，或至少在文档中标记遗留字段。

## P2：密码使用无盐 SHA-256，安全性不足

涉及位置：

- `app/db.py:46-47`
- `app/db.py:181-188`

问题：

密码直接用 `hashlib.sha256(password.encode()).hexdigest()` 存储，没有盐、没有慢哈希。

影响：

- 数据库泄漏后，弱密码很容易被字典/彩虹表撞出。

建议：

- 改用 `argon2`、`bcrypt` 或 `passlib`。
- 旧密码登录成功后做渐进式 rehash。

## P2：`storage_secret` 硬编码在源码中

涉及位置：

- `main.py:113-122`

问题：

NiceGUI `storage_secret` 固定写在源码里。代码泄漏或多环境共用时，客户端存储签名安全性下降。

影响：

- 不利于生产部署和密钥轮换。

建议：

- 从环境变量读取，例如 `NICEGUI_STORAGE_SECRET`。
- 未设置时开发环境给提示，生产环境禁止启动。

## P2：上传预读中间件会把整个 multipart body 一次性读入内存

涉及位置：

- `main.py:28-55`

问题：

`UploadBodyPreReadMiddleware` 为 `/api/upload` 预读完整 body，再交给后续处理。虽然接口里有 20MB 限制，但限制发生在 body 已经全部进内存之后。

影响：

- 大请求可以在进入业务校验前占用内存。
- 并发上传时内存压力变大。

建议：

- 在中间件里按累计大小提前拒绝。
- 或改回框架支持的 streaming/form parser，并定位原 NiceGUI deadlock 的根因。

## P2：状态接口对模型可用性反馈不准确

涉及位置：

- `app/routers/api.py:223-230`
- `app/services/sd_service.py:778-779`

问题：

`is_model_loaded()` 永远返回 `True`，`/api/status` 会报告 `model_loaded: true`，即使 `HEALING_IMAGE_API_KEY` 未配置也一样。

影响：

- 前端/运维看到的健康状态和实际生成能力不一致。

建议：

- 至少检查 `HEALING_IMAGE_API_KEY` 是否存在。
- 更进一步可做一次轻量供应商连通性检查，并把结果拆成 `server_running`、`api_key_configured`、`provider_reachable`。

## 已做的轻量验证

- `uv run python -m py_compile main.py app/routers/api.py app/state.py app/db.py app/services/sd_service.py app/services/chat_service.py` 通过。
- `GET /api/export/summary?key=healing2024` 当前返回真实统计数据。
- `GET /api/image/{uploads中的文件名}` 当前返回 200 和图片内容。
- `GET /api/session` 当前可匿名创建 session。
- 向 `/api/generate/slider` 发送非 JSON body 当前返回 500。

