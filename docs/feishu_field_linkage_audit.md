# 飞书字段联动审计与测试记录

更新时间：2026-06-10

本文档用于明确“程序字段 -> 本地表/队列 -> 飞书多维表格字段”的联动范围，并记录本次针对基本信息与核心统计同步链路的检查结果。主数据源仍是本地 SQLite；飞书是运营查看与导出副本。字段定义以 `app/services/feishu_sync.py` 中的 `SYNC_TARGETS` 为准。

## 0. 命名与显示规则

飞书多维表格和研究数据看板面向研究人员使用，优先使用中文显示名：

- 飞书数据表、视图、字段尽量使用中文名称。
- 后端同步类型、数据库字段和环境变量可以保留英文技术名，但本审计文档必须提供对应中文解释。
- 如果后续新增英文技术字段，应同时补充“飞书字段/中文解释”。
- 飞书自动生成且不参与科研分析的默认主列统一显示为 `系统主列_忽略`。
- 不为了中文显示而修改后端字段名、数据库列名或同步类型，避免影响现有代码和同步逻辑。

## 1. 同步总览

| 同步类型 | 本地来源 | 飞书表用途 | 唯一键 | 主要触发点 |
| --- | --- | --- | --- | --- |
| `hci_participant` | `hci_participants` | 参与者基本信息 | `参与者编号` | 登录/登记创建参与者；保存“参与者信息”；账号页基本信息修改后保存 |
| `session_summary` | `sessions` + `users` | 会话摘要 | `会话ID` | 创建会话；任意会话字段更新 |
| `drag_element_summary` | `sessions.placed_elements` | 自由创作元素数量摘要 | `会话ID` | 自由创作会话更新后，且 `mode_used = drag` |
| `inspire_element_summary` | `sessions.sketch_data` | 灵感创想识别与自定义类别摘要 | `会话ID` | 灵感创想会话更新后，且 `mode_used = inspire` |
| `mode_usage_count` | `sessions` 聚合 | 每名用户每种模式累计使用次数 | `用户模式键` | 会话更新后，且存在 `user_id` 与 `mode_used` |
| `work_count_summary` | 草稿箱/会话记录聚合 | 作品数量与修改/生成次数汇总 | `汇总键` | 保存草稿、发起 AI 生成、生成完成、草稿箱记录变化、删除草稿后 |

## 2. 基本信息联动字段

页面：`/account` 展示基本信息；“修改基本信息”进入 `/participant-info?next_path=/account`。

本地表：`hci_participants`

飞书同步类型：`hci_participant`

| 页面字段 | 本地字段 | 飞书字段 | 当前处理 |
| --- | --- | --- | --- |
| 研究编号 | `participant_code` | 参与者编号 | 统一为纯数字，如 `0002`；旧 `HCI-0002` 会规范化为 `0002` |
| 姓名 / 登记名 | `registered_name` | 登记姓名 | 由登记页写入，资料页只读展示 |
| 中心/社区编号 | `site_id` | 中心编号 | 可为空；空值同步为空 |
| 研究阶段 | `study_phase` | 研究阶段 | 可选 `未填写`、`pilot`、`study2`、`study3`；不再默认强写 `pilot` |
| 诊断大类 | `diagnosis_group` | 诊断大类 | 可选诊断大类或 `其他/未填写` |
| 出生日期 | `birth_date` | 出生日期 | 可为空；空日期会同步为远端空值，避免飞书残留旧日期 |
| 性别 | `gender` | 性别 | 来自登记页或资料页选择 |
| 教育层级 | `education_band` | 教育层级 | 可选教育层级或 `未填写` |
| 注册时间 | `created_at` | 创建时间 | 本地时间戳转 `YYYY-MM-DD HH:MM:SS` 后同步 |
| 更新时间 | `updated_at` | 更新时间 | 每次保存参与者资料后更新 |
| 本地用户ID | `user_id` | 本地用户ID | 用于排查本地用户关联 |
| 本地参与者ID | `id` | 本地参与者ID | 用于排查本地参与者行 |

## 3. 会话摘要联动字段

同步类型：`session_summary`

| 本地字段 / 计算字段 | 飞书字段 | 说明 |
| --- | --- | --- |
| `session_id` | 会话ID | 本地会话主键 |
| `user_id` | 本地用户ID | 本地用户行 ID |
| `participant_id` | 登录用户编号 | 会统一规范化；旧 `HCI-0002` 会变成 `0002`，非研究编号如 `U93667270` 保持原样 |
| `display_name` | 显示名 | 用户显示名 |
| `scene_type` | 场景类型 | 当前环境/模板类型 |
| `mode_used` | 使用模式 | `drag`、`inspire`、`chat`、`slider` 等 |
| `green_level` | 绿化强度 | 智能参数模式字段 |
| `urban_level` | 城市化强度 | 智能参数模式字段 |
| `vitality_level` | 活力强度 | 智能参数模式字段 |
| `light_warmth` | 光照温暖度 | 智能参数模式字段 |
| `generation_count` | 生成次数 | 当前会话生成次数 |
| `element_count_final` | 最终元素数 | `placed_elements` 数组长度 |
| `survey_completed` | 是否完成问卷 | 同步为“是/否” |
| `overall_satisfaction` | 总体满意度 | 问卷字段 |
| `feedback_text` | 反馈文本 | 问卷反馈 |
| `sketch_stroke_count` | 草图笔画数 | `sketch_data.strokeCount` |
| `uploaded_image_path` | 上传图片路径 | 本地上传文件路径 |
| `generated_image_path` | 生成图片路径 | 本地生成文件路径 |
| `created_at` | 创建时间 | 会话创建时间 |
| `survey_completed_at` | 问卷完成时间 | 可为空；空日期同步为空 |

## 4. 自由创作摘要联动字段

同步类型：`drag_element_summary`

| 本地字段 / 计算字段 | 飞书字段 | 说明 |
| --- | --- | --- |
| `session_id` | 会话ID | 自由创作会话 ID |
| `user_id` | 本地用户ID | 本地用户行 ID |
| `participant_code` | 参与者编号 | 统一规范化为纯数字研究编号；非研究编号保持原样 |
| `display_name` | 登记姓名 | 用户显示名 |
| `scene_type` | 场景类型 | 当前环境/模板类型 |
| `plant_element_count` | 植物类摆放数 | 根据元素名称/类别识别植物类 |
| `other_element_count` | 其他元素摆放数 | 非植物类元素数量 |
| `total_custom_element_count` | 自定义元素总数 | 植物类 + 其他类 |
| `generated_image_path` | 生成图片路径 | 本地生成文件路径 |
| `updated_at` | 更新时间 | 摘要更新时间 |

## 5. 灵感创想摘要联动字段

同步类型：`inspire_element_summary`

| 本地字段 / 计算字段 | 飞书字段 | 说明 |
| --- | --- | --- |
| `session_id` | 会话ID | 灵感创想会话 ID |
| `user_id` | 本地用户ID | 本地用户行 ID |
| `participant_code` | 参与者编号 | 统一规范化为纯数字研究编号；非研究编号保持原样 |
| `display_name` | 登记姓名 | 用户显示名 |
| `scene_type` | 场景类型 | 当前环境/模板类型 |
| `stroke_count` | 总笔画数 | `sketch_data.strokeCount` 或笔画日志长度 |
| `auto_plant_count` | 自动识别植物类数 | 自动标签中植物类数量 |
| `auto_other_count` | 自动识别其他类数 | 自动标签中非植物类数量 |
| `auto_total_count` | 自动识别总数 | 自动植物类 + 自动其他类 |
| `user_custom_label_count` | 用户自定义类别数 | 用户自定义标注数量 |
| `user_custom_plant_count` | 用户自定义植物类数 | 自定义标签中植物类数量 |
| `user_custom_other_count` | 用户自定义其他类数 | 自定义标签中非植物类数量 |
| `user_custom_labels` | 用户自定义类别明细 | 格式如 `花坛:植物; 长椅:其他` |
| `generated_image_path` | 生成图片路径 | 本地生成文件路径 |
| `updated_at` | 更新时间 | 摘要更新时间 |

## 6. 模式使用次数联动字段

同步类型：`mode_usage_count`

| 本地字段 / 计算字段 | 飞书字段 | 说明 |
| --- | --- | --- |
| `usage_key` | 用户模式键 | 格式：`{user_id}:{mode_used}` |
| `user_id` | 本地用户ID | 本地用户行 ID |
| `participant_code` | 参与者编号 | 统一规范化为纯数字研究编号；非研究编号保持原样 |
| `display_name` | 登记姓名 | 用户显示名 |
| `mode_used` | 使用模式 | 当前模式 |
| `usage_count` | 使用次数 | 该用户该模式历史会话数量 |
| `last_session_id` | 最近会话ID | 最近一次该模式会话 |
| `updated_at` | 更新时间 | 统计更新时间 |

## 7. 作品数量与修改/生成次数联动字段

本节是 2026-06-10 已实现的新口径。它覆盖之前“主动继续次数”“保存作品次数”“研究员帮助等级”等冗余或不稳定字段。

本地表：`hci_work_count_summaries`  
飞书表显示名：`作品数量汇总`  
飞书表 ID：`tblsa0bsFu7I1tHs`  
同步类型：`work_count_summary`  
唯一键：`汇总键`，当前等于本地用户 ID；`参与者编号` 作为科研合并字段保留。

| 本地字段 / 计算字段 | 飞书字段 | 中文解释 |
| --- | --- | --- |
| `summary_key` | 汇总键 | 飞书 upsert 唯一键，当前等于本地用户 ID |
| `participant_code` | 参与者编号 | 匿名研究编号，用于和外部量表合并 |
| `user_id` | 本地用户ID | 本地排查用，不作为论文核心变量 |
| `display_name` | 登记姓名 | 研究人员登记的姓名或代称 |
| `total_draft_work_count` | 草稿箱作品总数 | 该参与者草稿箱中全部作品/项目数量 |
| `drag_work_count` | 自由创作作品数 | 草稿箱中来自自由创作模式的作品数量 |
| `drag_revision_generation_count` | 自由创作修改/生成次数 | 自由创作模式下保存草稿或发起 AI 生成的累计次数；不记录每次拖动 |
| `inspire_work_count` | 灵感创想作品数 | 草稿箱中来自灵感创想模式的作品数量 |
| `inspire_revision_generation_count` | 灵感创想修改/生成次数 | 灵感创想模式下保存草图草稿或发起 AI 生成的累计次数 |
| `chat_work_count` | 对话改造作品数 | 草稿箱中来自对话改造模式的作品数量 |
| `chat_revision_generation_count` | 对话改造修改/生成次数 | 对话改造模式下保存结果或发起 AI 生成的累计次数 |
| `slider_work_count` | 智能参数作品数 | 草稿箱中来自智能参数模式的作品数量 |
| `slider_revision_generation_count` | 智能参数修改/生成次数 | 智能参数模式下保存结果或发起 AI 生成的累计次数 |
| `updated_at` | 更新时间 | 统计刷新时间 |

统计口径：

- “作品数”只统计草稿箱里实际存在的作品/项目。
- “修改/生成次数”是作品层面的有效迭代次数，保存草稿计 1 次，发起 AI 生成计 1 次。
- 不记录鼠标轨迹、hover、撤回、连续拖拽坐标、每次滑杆微调。
- 四个模式分别统计作品数和修改/生成次数；四个模式作品数相加应等于草稿箱作品总数。

## 8. 四个环境参数记录口径

四个环境参数指：绿化程度、城市化程度、活力程度、光照温暖度。它们是程序控制 AI 环境改造方向的设计参数，不是临床症状量表。

| 参数 | 中文解释 | 在 AI 提示词中的作用 |
| --- | --- | --- |
| 绿化程度 | 图像中树木、草地、灌木、花卉等自然植被的多少 | 高值会生成“大幅增加树木、灌木、藤蔓和草坪”等提示 |
| 城市化程度 | 图像中硬质铺装、建筑、长椅、路灯、围栏、道路等人工设施的多少 | 高值会生成“丰富人造设施，添加长椅、路灯、雕塑、步道”等提示 |
| 活力程度 | 环境是安静少人，还是有活动、人群、社交与动态感 | 高值会生成“有行人散步、交谈，整体热闹有活力”等提示 |
| 光照温暖度 | 画面光照偏冷、自然，还是偏暖、柔和、治愈 | 高值会生成“金色暖阳、暖黄光线、傍晚黄金时刻”等提示 |

| 模式 | 记录方式 |
| --- | --- |
| 自由创作模式 | 不记录四个环境参数，只记录植物类数量、其他元素数量、总元素数量、作品数量、修改/生成次数 |
| 灵感创想模式 | 优先记录系统识别和用户自定义类别；只有存在明确系统参数时才记录四个环境参数，不强行推断 |
| 对话改造模式 | 保存 AI 最终用于生成图像的四个环境参数；如果没有稳定参数转换，则暂不记录 |
| 智能参数模式 | 直接记录用户滑杆值或后端实际生成参数 |

## 9. 明确不记录的内容

以下内容不进入程序后端与飞书同步：

- 作品与环境输出汇总表。
- 研究员观察日志。
- 安全事件日志。
- 程序内量表系统。
- 主动继续次数。
- 研究员帮助等级。
- `session_summary` 文本摘要。
- 轨迹级行为数据。

## 10. 本次发现并修复的问题

| 问题 | 影响 | 修复 |
| --- | --- | --- |
| 资料页出生日期强制必填 | 无法保存“出生日期未填写”的真实状态，也无法更新其它基本信息 | 允许出生日期为空，空值保存为 `''` |
| 研究阶段空值会在表单中默认变成 `pilot` | 用户未选择时可能被静默写成 `pilot` 并同步到飞书 | 增加 `未填写` 选项，空值默认显示和保存为 `未填写` |
| 飞书 Date 字段为空时被跳过 | 远端可能保留旧出生日期或旧问卷完成时间 | Date 字段在 payload 中存在但为空时，向飞书发送 `None` 清空远端 |
| 会话/元素摘要兜底使用旧 `participant_id` 时可能带 `HCI-` | 不同表中的参与者编号格式可能不一致 | 会话摘要、自由创作摘要、灵感创想摘要、模式使用统计均统一走编号规范化 |

## 11. 测试记录

### 11.1 本地模拟测试

命令：临时 SQLite 数据库 + 假 FeishuClient，不写入真实飞书。

覆盖内容：

- `upsert_hci_participant(participant_code='HCI-0042', birth_date='')` 保存为 `0042`。
- `feishu_sync_jobs.target_key` 写入 `0042`。
- `hci_participant` 生成的飞书字段包含 `参与者编号 = 0042`、`登记姓名 = TestUser`、`出生日期 = None`。
- `session_summary` 里的 `participant_id` 从 `HCI-0042` 规范化为 `0042`。
- `drag_element_summary` 里的 `participant_code` 从兜底编号规范化为 `0042`。
- `_sync_job_blocking` 会以 `参与者编号 = 0042` 作为唯一键，并保留旧值 `HCI-0042` 作为远端兼容查找值。

结果：通过。

### 11.2 真实飞书参与者资料同步

对象：当前参与者 `0002 / Arya`

步骤：

1. 重新把本地 `hci_participants` 行入队为 `hci_participant`。
2. 执行单条 `sync_job`。
3. 用飞书 API 读回远端记录。

结果：

| 字段 | 远端读回 |
| --- | --- |
| `participant_code` / 参与者编号 | `0002` |
| `registered_name` / 登记姓名 | `Arya` |
| `gender` / 性别 | `女` |
| `site_id` / 中心编号 | 空 |
| `study_phase` / 研究阶段 | `未填写` |
| `diagnosis_group` / 诊断大类 | `其他/未填写` |
| `birth_date` / 出生日期 | 空 |
| `education_band` / 教育层级 | `未填写` |
| `user_id` / 本地用户ID | `8` |
| `local_id` / 本地参与者ID | `5` |

同步状态：`success`，远端记录 ID：`recvlACkqO3dYX`。

### 11.3 真实飞书队列全量回归

对象：当前数据库中已入队的所有同步类型。

步骤：

1. 执行 `sync_due_jobs_once(limit=50)`，随后对飞书响应较慢的剩余任务逐条执行 `sync_job`。
2. 复查 `feishu_sync_jobs` 的 `sync_type` / `status` 聚合结果。

最终结果：

| 同步类型 | 成功数量 | 非成功数量 |
| --- | ---: | ---: |
| `hci_participant` | 2 | 0 |
| `session_summary` | 16 | 0 |
| `drag_element_summary` | 2 | 0 |
| `inspire_element_summary` | 2 | 0 |
| `mode_usage_count` | 4 | 0 |
| `work_count_summary` | 9 | 0 |

结论：核心作品汇总同步已验证成功。当前队列中仍可能存在旧会话摘要等历史待同步任务，应用启动后的后台重试会继续处理；这不影响本次新增的 `work_count_summary` 链路。

## 12. 后续注意事项

- 程序会自动新增缺失字段，但不会删除飞书旧字段，也不会强制修改已有字段类型。
- 如果某个飞书字段历史上被建成文本字段，即使程序按数字发送，飞书读回也可能表现为字符串；这不影响当前唯一键与展示，但如需严格字段类型，需要人工确认后在飞书侧重建或迁移字段。
- `session_summary` 当前会在创建空会话时也排队，因此快速打开页面可能产生一些空会话摘要任务；这属于现有产品行为，不会影响基本信息联动。
- 飞书默认主列已统一改名为 `系统主列_忽略`，科研导出时可以忽略。
- `work_count_summary` 已实现并完成真实飞书同步测试；后续如果调整“草稿箱作品”的定义，需要同步更新本地统计口径和文档。
