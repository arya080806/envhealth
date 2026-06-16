# 重要更正：本报告已被替代

用户已在 2026-06-12 明确说明，今天预实验使用的入口是 `https://yuhealth.cn`，不是本报告最初排查的 `https://envhealth.cn`。因此本报告中的线上入口、接口、飞书同步和 iPad 结论不适用于今天这次患者预实验。

请以后优先查看同目录下的 `20260612_yuhealth_entry_correction_report.md`。本文件仅保留为历史排查记录，避免误把 `envhealth.cn` 的结论套用到 `yuhealth.cn`。

# 2026-06-12 预实验故障排查报告与稳定性改造计划

检查时间：2026-06-12  
检查范围：线上正式域名、旧 IP 入口、本地代码、SQLite/飞书同步链路、页面资源与 iPad 尺寸渲染。

## 一、结论摘要

今天的主要问题不是单点 bug，而是三类底层不稳定叠加：

1. **入口地址分裂**：旧地址 `http://43.167.184.248:6420` 当前返回 `502 Bad Gateway`；正式入口 `https://envhealth.cn` 正常。患者若使用旧 IP，会出现 iPad 打不开、操作不进入当前线上服务、飞书不同步等现象。
2. **飞书同步配置和容错不足**：正式线上飞书同步启用，但同步队列存在失败。一次手动重试后 4 条成功、5 条仍失败，失败集中在缺少 `FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID`、`session_summary` 表 ID 无效、远端 record_id 已失效。
3. **前端/后端耦合导致卡顿**：预设图原图 2.38-3.30MB，预设点击会同步读原图、写上传文件、生成显示图、写数据库、入同步队列后再跳转；同时底部导航每 4 秒全局轮询一次生成通知，后端每次全表扫描所有 session。数据量上来后页面切换和 AI 生成前后的卡顿会持续恶化。

## 二、关键验证结果

### 1. 线上入口

- `https://envhealth.cn/api/status` 返回正常：`{"server":"running","model_loaded":true}`。
- `http://43.167.184.248:6420/api/status` 返回 `502 Bad Gateway`。
- 部署文档指向正式域名和 systemd 端口 `6425`，但 README 和 `restart.sh` 仍提到旧 IP/`6420`，存在现场使用混乱风险。

### 2. 两个患者账号的数据

正式域名导出中能找到今天两个患者记录，说明数据已进入线上数据库，不是完全没有落库：

| 账号显示名 | 参与者编号 | session 数 | 有场景 session | 有模式 session | 生成次数 | 模式分布 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `20260612-1` | `0127` | 19 | 13 | 3 | 4 | slider:1, inspire:1, drag:1 |
| `20260612-2` | `0128` | 2 | 2 | 2 | 2 | slider:1, drag:1 |

异常点：`20260612-1` 产生了 19 个 session，但只有 3 个真正进入模式。这会污染导出、加重通知查询和同步排队压力。

### 3. 飞书同步状态

正式域名重试前：

- `enabled=true`
- `success=13`
- `pending=7`
- `failed=2`

触发一次已有队列重试后：

- `success=17`
- `failed=5`
- `pending=0`

剩余失败：

- `slider_mode_summary / 3ac341d0b345`：`Missing table id env: FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID`
- `slider_mode_summary / c5918f359480`：`Missing table id env: FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID`
- `session_summary / 3c8a18bb9b2b`：`Feishu API error 1254041: TableIdNotFound`
- `work_count_summary / 7`：`Feishu API error 1254043: record not found,id = recvm6XbziJPWw`
- `work_count_summary / 10`：`Feishu API error 1254043: record not found,id = recvm6XbziJPWw`

判断：

- 线上 `.env` 很可能缺少 `FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID`，本地 `.env` 有该项。
- `session_summary` 的表 ID 在飞书端已不存在或线上配置仍是旧表。
- `work_count_summary` 保存了已不存在的飞书 `remote_record_id`，同步器没有在 `record not found` 时自动清空 record_id 并按唯一键重新 upsert。

### 4. 图片与页面加载

预设原图大小和线上耗时：

- 原图：2.38-3.30MB，单张下载约 1.6-3.0 秒。
- `display` 图：169-309KB，单张约 0.38-0.65 秒。
- `thumb` 图：3.6-5.9KB，单张约 0.31-0.33 秒。

页面代码大部分使用 `display=True`，方向是对的。但首次请求 `display/thumb` 时由后端同步生成；预设点击还会把原图复制到 `uploads`，再生成 display 图，因此患者点击后仍会感觉慢。

### 5. iPad 显示

浏览器 iPad 尺寸下，`https://envhealth.cn/` 和 `/login` 可正常渲染，无控制台错误、无空白页。  
旧 IP 入口不可用，因此 iPad 现场打不开的首要嫌疑是使用了旧地址、HTTP/IP 入口、缓存或真实 Safari WebKit 兼容问题。还需要用真实 iPad Safari 复测正式域名。

## 三、代码层风险点

1. `app/pages/camera.py`
   - 进入 `/camera` 时立即创建 session，用户只是返回/刷新也会产生空 session。
   - `use_preset()` 同步读取大图、保存上传、更新 session、生成 display 图，然后跳转。

2. `app/components/nav.py`
   - 每个页面底部导航每 4 秒请求 `/api/generation/notifications`。

3. `app/routers/api.py`
   - `/api/generation/notifications` 调用 `get_all_sessions()`，每次扫描并 JSON 解析全部 session。
   - `serve_image()` 和 `serve_preset_image()` 首次请求 `display/thumb` 时同步处理图片。

4. `app/db.py`
   - `SessionProxy.__setattr__` 每设置一个字段就写库。
   - `update_session()` 每次写库后都会 `queue_hci_core_summaries(session_id)`，一次 AI 点击可能触发多次汇总和多条同步队列更新。

5. `app/services/feishu_sync.py`
   - `record not found` 没有自动恢复路径。
   - 缺少“启动时校验所有必需飞书表 ID”的硬性健康检查。

## 四、立即修复计划

1. 统一入口
   - 现场和文档只保留 `https://envhealth.cn`。
   - 更新 README、二维码、操作手册，删除或标记旧 `43.167.184.248:6420`。
   - 服务器上对旧入口做 301 到正式域名，或彻底关闭并明确告知不用。

2. 修复线上飞书配置
   - 登录服务器检查 `/home/zm/envhealth/.env`。
   - 补上 `FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID=tbl0b7OU7sommUqK`。
   - 校正 `FEISHU_BITABLE_SESSIONS_TABLE_ID`，确认飞书中该表真实存在；若会话摘要已废弃，应停止同步该类型或迁移到新表。
   - 对 `work_count_summary` 中失败记录清空失效 `remote_record_id` 后重新按唯一键同步。
   - 重启 `envhealth.service`，执行 `/api/feishu/sync/retry`，确认 `failed=0`。

3. 补同步今天患者数据
   - 验证 `20260612-1 / 0127` 和 `20260612-2 / 0128` 在对应飞书子表中出现。
   - 重点核对 `智能参数摘要`、`自由创作元素摘要`、`灵感创想元素摘要`、`模式使用次数`、`作品数量汇总`。

4. 临时降低卡顿
   - 把通知轮询从 4 秒改成 15-30 秒，或只在草稿箱页面启用。
   - 预先生成所有 preset 的 display/thumb 图，不在患者点击时生成。

## 五、底层稳定性改造计划

### 阶段 A：数据与同步层重构

目标：飞书失败不影响实验记录，但失败必须可见、可恢复、可追踪。

- 增加 `/api/health/deep`：检查数据库可写、图片 API 配置、飞书 app token、所有表 ID、队列失败数。
- 启动时校验所有 `SYNC_TARGETS` 的表 ID；缺失配置直接在健康检查中红灯，不允许静默跳过。
- 为 `FeishuSyncError` 增加错误分类：missing_config、table_missing、record_missing、permission_denied、rate_limit、network。
- `record_missing` 自动恢复：清空 `remote_record_id`，按唯一键查找；查不到则新建。
- `table_missing` 和 `missing_config` 标记为配置错误，不做指数退避空转，避免后台一直重试。
- 给队列加告警：failed > 0 或 pending 超过阈值时后台管理页明显提示。
- 增加飞书同步单元测试，覆盖缺 env、表不存在、record_id 失效、批量 upsert、字段类型转换。

### 阶段 B：Session 生命周期重构

目标：只记录真实实验行为，不让空 session 污染数据和拖慢查询。

- `/camera` 不再进入页面就创建 session；改为上传/选择预设时才创建。
- session 增加状态：`created / media_ready / mode_started / generation_started / completed / abandoned`。
- 对无上传、无模式、无交互的 session 定期归档或排除出导出。
- 通知接口改成 SQL 精确查询，不调用 `get_all_sessions()`。
- 增加索引：`sessions(user_id, created_at)`、`sessions(generation_status, generation_finished_at, generation_seen_at)`。

### 阶段 C：写库与入队去抖

目标：一次用户操作只产生一次稳定的数据更新和一次同步入队。

- `SessionProxy` 增加批量更新方法，减少多字段逐个写库。
- `update_session()` 支持 `queue=False`，复杂操作完成后统一 `queue_hci_core_summaries()`。
- AI 生成开始、完成、失败使用事务封装，保证状态、次数、图片路径和队列一致。
- 汇总表按模式增量更新，避免每次字段变更都重算所有子表。

### 阶段 D：图片与前端性能

目标：患者点击后立即反馈，重活交给后台。

- 预设图构建期生成 `display/thumb`，页面直接引用静态小图。
- 选择预设时不再复制 3MB 原图到 uploads；session 记录 preset 引用，只有需要 AI 输入时读取源图。
- 用户上传后异步生成 display/thumb，并在 UI 上先显示本地预览。
- 给图片加 `loading="lazy"`、明确宽高、`srcset`。
- 大图处理放到线程池或任务队列，不在请求/点击路径同步阻塞。
- 对 drag/inspire 的 canvas 序列化做节流，生成时只提交必要字段，快照保存可后台化。

### 阶段 E：iPad/Safari 兼容与回归测试

目标：每次部署前知道 iPad 是否可用。

- 固定一台真实 iPad Safari 作为验收设备。
- 加 Playwright/浏览器回归：桌面、iPad 尺寸下访问首页、登录、相机页、四个模式页，要求无空白、无控制台错误。
- 增加现场 smoke checklist：正式域名、登录、预设选择、四模式打开、后台生成、草稿箱通知、飞书状态。
- 保留旧 Safari runtime，但减少 `backdrop-filter`、大背景图和高成本视觉效果在低性能设备上的使用。

## 六、建议验收标准

1. `https://envhealth.cn/api/status` 正常，旧 IP 不再作为患者入口。
2. `/api/feishu/sync/status`：`failed=0`，`pending` 在 1-2 分钟内自动归零。
3. 新建一名测试参与者，完成预设进入四个模式，飞书对应子表均有记录。
4. iPad Safari 打开正式域名，首页、登录、相机页、模式选择和四个模式页均可显示。
5. 预设点击到模式选择页小于 1 秒；模式页首图显示小于 1 秒。
6. AI 生成点击后 300ms 内 UI 有反馈，页面可切换，不阻塞导航。
7. 空 session 明显减少，导出不再混入大量无上传、无模式记录。
