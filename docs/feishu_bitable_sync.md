# 飞书多维表格同步说明

本项目采用“本地 SQLite 为主数据源，飞书多维表格为运营/查看/导出副本”的方式。前端或 NiceGUI 页面提交后，后端先写入本地数据库，再把同步任务写入 `feishu_sync_jobs` 队列，由后台任务异步同步到飞书。飞书失败不会影响用户提交。

字段级联动审计与最新测试记录见：[`feishu_field_linkage_audit.md`](feishu_field_linkage_audit.md)。

## 1. 当前绑定的 Base

Base 地址：`https://icnqsp04t4w8.feishu.cn/base/JwEfb3HgTaopgysRBxycIKPSn7d`

| 环境变量 | 当前值 |
| --- | --- |
| `FEISHU_BITABLE_APP_TOKEN` | `JwEfb3HgTaopgysRBxycIKPSn7d` |
| `FEISHU_BITABLE_PARTICIPANTS_TABLE_ID` | `tblOpqLdd7QB9GCS` |
| `FEISHU_BITABLE_SESSIONS_TABLE_ID` | `tblDQueP2IcUENC8` |
| `FEISHU_BITABLE_DRAG_ELEMENTS_TABLE_ID` | `tbl5rKD7pngR3JPT` |
| `FEISHU_BITABLE_INSPIRE_ELEMENTS_TABLE_ID` | `tblRHCZlil3gxHJP` |
| `FEISHU_BITABLE_CHAT_SUMMARY_TABLE_ID` | `tblZkSIqni3IjZ9J` |
| `FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID` | `tbl0b7OU7sommUqK` |
| `FEISHU_BITABLE_MODE_USAGE_TABLE_ID` | `tblswhN4OsyWRZwj` |
| `FEISHU_BITABLE_WORK_COUNTS_TABLE_ID` | `tblsa0bsFu7I1tHs` |

真实 `FEISHU_APP_SECRET` 只允许放在本地 `.env` 或部署环境变量中，不要写入源码、文档或 Git。

## 2. 中文显示规则

飞书多维表格是给研究人员运营查看、核对和导出数据用的副本，因此可见的数据看板尽量使用中文显示：

- 飞书左侧数据表名使用中文，例如 `参与者基本信息`、`会话摘要`、`作品数量汇总`。
- 飞书字段名使用中文，例如 `参与者编号`、`草稿箱作品总数`、`自由创作修改/生成次数`。
- 飞书视图名使用中文，例如 `默认视图`。
- 飞书系统默认主列统一命名为 `系统主列_忽略`，仅用于满足多维表格结构要求，科研导出时可以忽略。
- 后端同步类型、数据库字段、环境变量仍可使用英文技术名，例如 `session_summary`、`participant_code`、`FEISHU_BITABLE_SESSIONS_TABLE_ID`，但文档中必须同时给出中文解释。
- 后续新增表或字段时，优先新增中文显示名；如果必须保留英文，应在本文件或字段审计文档中添加中文注释。

## 3. 飞书表与唯一键

| 飞书表显示名 | 后端同步类型 | 唯一键 | 用途 |
| --- | --- | --- | --- |
| `参与者基本信息` | `hci_participant` | `参与者编号` | 参与者基本信息 |
| `会话摘要` | `session_summary` | `会话ID` | 会话摘要 |
| `自由创作元素摘要` | `drag_element_summary` | `会话ID` | 自由创作元素数量摘要 |
| `灵感创想元素摘要` | `inspire_element_summary` | `会话ID` | 灵感创想识别与自定义类别摘要 |
| `对话改造摘要` | `chat_mode_summary` | `会话ID` | 对话改造模式的低隐私摘要 |
| `智能参数摘要` | `slider_mode_summary` | `会话ID` | 智能参数/旧 `ai` 模式的参数摘要 |
| `模式使用次数` | `mode_usage_count` | `汇总键` | 每名用户一行，汇总四种模式累计使用次数 |
| `作品数量汇总` | `work_count_summary` | `汇总键` | 草稿箱作品总数，以及四个模式分别的作品数和修改/生成次数 |

飞书默认主列已统一改名为 `系统主列_忽略`，只是为了满足多维表格结构要求，科研导出时可以忽略。

## 4. 字段映射

`会话摘要` 是历史上的通用会话表，曾在创建空会话时立即排队同步，因此会出现大量 `使用模式` 为空、四个环境参数均为 50 的默认行。新版 HCI/CHI 研究不再把这张表作为核心分析表；对话改造、智能参数、自由创作、灵感创想均优先使用各自的模式子表，`会话摘要` 只保留作历史排查或迁移参考。

### 4.1 `参与者基本信息`

| 本地字段 | 飞书字段 |
| --- | --- |
| `participant_code` | 参与者编号 |
| `registered_name` | 登记姓名 |
| `site_id` | 中心编号 |
| `study_phase` | 研究阶段 |
| `diagnosis_group` | 诊断大类 |
| `birth_date` | 出生日期 |
| `gender` | 性别 |
| `education_band` | 教育层级 |
| `user_id` | 本地用户ID |
| `local_id` | 本地参与者ID |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

### 4.2 `自由创作元素摘要`

| 本地字段 | 飞书字段 |
| --- | --- |
| `session_id` | 会话ID |
| `user_id` | 本地用户ID |
| `participant_code` | 参与者编号 |
| `display_name` | 登记姓名 |
| `scene_type` | 场景类型 |
| `plant_element_count` | 植物类摆放数 |
| `other_element_count` | 其他元素摆放数 |
| `total_custom_element_count` | 自定义元素总数 |
| `generated_image_path` | 生成图片路径 |
| `updated_at` | 更新时间 |

### 4.3 `灵感创想元素摘要`

| 本地字段 | 飞书字段 |
| --- | --- |
| `session_id` | 会话ID |
| `user_id` | 本地用户ID |
| `participant_code` | 参与者编号 |
| `display_name` | 登记姓名 |
| `scene_type` | 场景类型 |
| `stroke_count` | 总笔画数 |
| `auto_plant_count` | 自动识别植物类数 |
| `auto_other_count` | 自动识别其他类数 |
| `auto_total_count` | 自动识别总数 |
| `user_custom_label_count` | 用户自定义类别数 |
| `user_custom_plant_count` | 用户自定义植物类数 |
| `user_custom_other_count` | 用户自定义其他类数 |
| `user_custom_labels` | 用户自定义类别明细 |
| `generated_image_path` | 生成图片路径 |
| `updated_at` | 更新时间 |

### 4.4 `对话改造摘要`

这张表同步每次对话改造的结构化摘要，并同时记录用户写下的提示词和系统实际给 AI 图像生成服务的完整提示词。当前后端不会从自由文本强行推断环境参数；只有会话中已有明确的最终参数值时，才写入四个最终参数字段。

| 本地字段 | 飞书字段 | 中文解释 |
| --- | --- | --- |
| `session_id` | 会话ID | 对话改造会话 ID |
| `user_id` | 本地用户ID | 本地排查用 |
| `participant_code` | 参与者编号 | 匿名研究编号 |
| `display_name` | 登记姓名 | 现场核对用 |
| `scene_type` | 场景类型 | 当前环境/模板类型 |
| `mood_tag_count` | 情绪标签数 | 用户选择的情绪/意向标签数量 |
| `mood_tags` | 情绪标签明细 | 以分号拼接的标签摘要 |
| `user_prompt` | 用户提示词 | 用户在对话改造中输入的补充描述原文 |
| `extra_text_length` | 补充描述字数 | 用户提示词的字数，便于统计输入量 |
| `has_extra_text` | 是否填写补充描述 | 用于判断是否有额外语言输入 |
| `chat_green_level` | 最终绿化程度 | 有明确来源时同步 |
| `chat_urban_level` | 最终城市化程度 | 有明确来源时同步 |
| `chat_vitality_level` | 最终活力程度 | 有明确来源时同步 |
| `chat_light_warmth` | 最终光照温暖度 | 有明确来源时同步 |
| `generation_count` | 生成次数 | 当前会话生成次数 |
| `generation_status` | 生成状态 | `pending` / `done` / `failed` 等 |
| `generation_error` | AI错误摘要 | 失败时的简短错误文本 |
| `llm_prompt` | AI提示词 | 实际发送给 AI 图像生成服务的完整提示词；历史缺失时仅在可重建时补齐 |
| `generated_image_path` | 生成图片路径 | 本地生成文件路径 |
| `updated_at` | 更新时间 | 摘要更新时间 |

### 4.5 `智能参数摘要`

这张表记录参数调节模式的明确滑杆值和生成状态。历史旧模式名 `ai` 会按智能参数模式同步到同一张表，便于旧数据归并。

| 本地字段 | 飞书字段 | 中文解释 |
| --- | --- | --- |
| `session_id` | 会话ID | 智能参数会话 ID |
| `user_id` | 本地用户ID | 本地排查用 |
| `participant_code` | 参与者编号 | 匿名研究编号 |
| `display_name` | 登记姓名 | 现场核对用 |
| `scene_type` | 场景类型 | 当前环境/模板类型 |
| `selected_recommend` | 预设名称 | 用户选择的推荐预设 |
| `green_level` | 绿化程度 | 用户滑杆值或后端实际参数 |
| `urban_level` | 城市化程度 | 用户滑杆值或后端实际参数 |
| `vitality_level` | 活力程度 | 用户滑杆值或后端实际参数 |
| `light_warmth` | 光照温暖度 | 用户滑杆值或后端实际参数 |
| `generation_count` | 生成次数 | 当前会话生成次数 |
| `generation_status` | 生成状态 | `pending` / `done` / `failed` 等 |
| `generation_error` | AI错误摘要 | 失败时的简短错误文本 |
| `generated_image_path` | 生成图片路径 | 本地生成文件路径 |
| `updated_at` | 更新时间 | 摘要更新时间 |

### 4.6 `模式使用次数`

| 本地字段 | 飞书字段 |
| --- | --- |
| `summary_key` | 汇总键 |
| `participant_code` | 参与者编号 |
| `display_name` | 登记姓名 |
| `total_usage_count` | 总使用次数 |
| `drag_usage_count` | 自由创作使用次数 |
| `inspire_usage_count` | 灵感创想使用次数 |
| `chat_usage_count` | 对话改造使用次数 |
| `slider_usage_count` | 智能参数使用次数 |
| `last_mode_used` | 最近使用模式 |
| `last_session_id` | 最近会话ID |
| `updated_at` | 更新时间 |

### 4.7 `作品数量汇总`

这张表用于替代之前较分散的“保存作品次数”等不稳定指标。它不记录细碎行为，只记录草稿箱作品数量和作品层面的有效修改/生成次数。新版 Word 已将“主动继续次数”列为后台候选指标，但当前飞书同步尚未实现，需先确认稳定定义后再新增。

| 本地字段 | 飞书字段 | 中文解释 |
| --- | --- | --- |
| `summary_key` | 汇总键 | 飞书 upsert 唯一键，当前等于本地用户 ID |
| `participant_code` | 参与者编号 | 匿名研究编号 |
| `display_name` | 登记姓名 | 研究人员登记的姓名或代称 |
| `total_draft_work_count` | 草稿箱作品总数 | 该参与者草稿箱中全部作品/项目数量 |
| `drag_work_count` | 自由创作作品数 | 草稿箱中来自自由创作模式的作品数量 |
| `drag_revision_generation_count` | 自由创作修改/生成次数 | 自由创作模式下保存草稿或发起 AI 生成的累计次数 |
| `inspire_work_count` | 灵感创想作品数 | 草稿箱中来自灵感创想模式的作品数量 |
| `inspire_revision_generation_count` | 灵感创想修改/生成次数 | 灵感创想模式下保存草图草稿或发起 AI 生成的累计次数 |
| `chat_work_count` | 对话改造作品数 | 草稿箱中来自对话改造模式的作品数量 |
| `chat_revision_generation_count` | 对话改造修改/生成次数 | 对话改造模式下保存结果或发起 AI 生成的累计次数 |
| `slider_work_count` | 智能参数作品数 | 草稿箱中来自智能参数模式的作品数量 |
| `slider_revision_generation_count` | 智能参数修改/生成次数 | 智能参数模式下保存结果或发起 AI 生成的累计次数 |
| `updated_at` | 更新时间 | 统计刷新时间 |

## 5. 同步机制

后端服务：`app/services/feishu_sync.py`

核心机制：

- 获取 `tenant_access_token`：`POST /open-apis/auth/v3/tenant_access_token/internal`。
- token 在内存中缓存，过期前自动刷新。
- 封装 `GET`、`POST`、`PUT`、`PATCH` 请求。
- 同步前自动检查飞书字段，缺失字段会自动创建。
- 按唯一键查找远程记录，存在则 `PUT` 更新，不存在则 `POST` 新增。
- 同步失败写入本地 `feishu_sync_jobs`，后台按退避策略重试。

程序只会新增缺失字段和更新映射字段，不会自动删除飞书旧字段。旧字段如果不再需要，需要在飞书里人工确认后删除；这样可以避免误删历史数据或影响已经导出的数据文件。

当前口径下不新增和不同步：

- 作品与环境输出汇总表。
- 研究员观察日志。
- 安全事件日志。
- 程序内量表系统。
- 主动继续次数旧口径；新版候选指标当前尚未实现，需定义后再新增。
- 研究员帮助等级。
- `session_summary` 文本摘要。
- 轨迹级行为数据。

## 6. 环境变量

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=replace_with_your_app_secret
FEISHU_BITABLE_APP_TOKEN=appxxxxxxxxxxxxxxxx
FEISHU_BITABLE_PARTICIPANTS_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_SESSIONS_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_DRAG_ELEMENTS_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_INSPIRE_ELEMENTS_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_CHAT_SUMMARY_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_SLIDER_SUMMARY_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_MODE_USAGE_TABLE_ID=tblxxxxxxxxxxxxxxxx
FEISHU_BITABLE_WORK_COUNTS_TABLE_ID=tblxxxxxxxxxxxxxxxx
HEALING_EXPORT_KEY=replace_with_research_admin_key
```

## 7. 最小验证方法

页面验证：

1. 打开 `/login`。
2. 输入姓名/研究登记名与性别。
3. 点击“作为新参与者登记”，确认生成顺序编号。
4. 在 `/participant-info` 补充中心编号、研究阶段、诊断大类、出生日期、教育层级。
5. 完成一次自由创作或灵感创想，等待后台同步。
6. 在飞书对应子表查看是否出现参与者编号、会话 ID 和统计字段。

接口状态验证：

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:6420/api/feishu/sync/status?key=你的HEALING_EXPORT_KEY"

Invoke-RestMethod `
  -Uri "http://127.0.0.1:6420/api/feishu/sync/retry?key=你的HEALING_EXPORT_KEY" `
  -Method Post
```

历史端到端测试：`FeishuSyncTest0604` 已生成纯数字参与者编号 `0001`，参与者表、自由创作子表、灵感创想子表、模式使用次数表、会话摘要表均同步成功。2026-06-10 已新增飞书表 `作品数量汇总`，现有 9 名本地用户的作品数量汇总已同步成功。2026-06-11 已新增 `对话改造摘要` 与 `智能参数摘要`，用于替代会话摘要中的混合参数列。最新字段级测试见上方审计文档。

## 8. 飞书后台配置要点

如果以后更换 Base，需要确认：

1. 自建应用已经开通多维表格相关权限。
2. 应用权限变更已经发布生效。
3. 目标多维表格中已添加“环境游戏改造”作为文档应用。
4. `.env` 中的 `FEISHU_BITABLE_APP_TOKEN` 和各 `TABLE_ID` 已更新。

关键路径：打开目标多维表格，右上角 `...` -> `更多` -> `添加文档应用`，搜索并添加“环境游戏改造”。缺少这一步时，后端常见错误是 `91403 Forbidden`。

## 9. 官方 API 参考

- [自建应用获取 tenant_access_token](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)
- [多维表格新增数据表](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/create)
- [多维表格新增字段](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/create)
- [多维表格列出字段](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/list)
- [多维表格新增记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create)
- [多维表格更新记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update)
- [多维表格列出记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/list)
