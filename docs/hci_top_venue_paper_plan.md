# CHI 顶会方向 HCI 论文深化规划：生成式 AI 恢复性环境共创

版本：v0.2  
日期：2026-06-04  
目标会议：CHI 主会优先；备选 CSCW / DIS / IMWUT / TOCHI  
项目：`healing-environment`

## 1. 一句话定位

这篇 HCI 论文不应写成临床疗效 RCT，而应写成：

> 面向稳定期精神障碍社区康复人群，研究生成式 AI 环境共创系统如何通过不同的用户控制方式支持恢复需求表达、情绪调节、控制感和安全参与，并提出可迁移的人机协作设计原则。

RCT 论文回答“有没有疗效”。CHI 论文回答“这种交互为什么值得设计、如何设计、不同交互模式有什么取舍、在真实社区康复中如何被患者和治疗师共同使用”。

## 2. 推荐 CHI 论文题目

英文题目可选：

1. Designing Generative-AI Restorative Environment Co-Creation for People with Serious Mental Illness.
2. Agency, Safety, and Expression in Generative-AI Environmental Co-Creation for Community Mental Health.
3. From Prompting to Co-Creating: Comparing Interaction Modes for Restorative Environment Generation in Psychiatric Rehabilitation.

中文核心题目：

生成式 AI 恢复性环境共创在精神障碍社区康复中的交互模式、控制感与安全设计研究。

## 3. CHI 论文的核心贡献

### Contribution 1：系统贡献

一个面向精神障碍社区康复场景的生成式 AI 恢复性环境共创系统。

系统包含四种交互模式：

- 自由创作：拖拽环境元素。
- 灵感创想：草图/标注输入。
- 对话改造：情绪标签 + 简短文本。
- 智能参数：绿化、人造元素、活力、光线温度四参数。

系统贡献要写清楚：

- 为什么恢复性环境适合精神康复。
- 为什么不能只做开放 prompt。
- 为什么需要多种 AI agency 模式。
- 为什么治疗师应作为协作者，而不是被系统替代。

### Contribution 2：实证贡献

通过 Study 2 的受试者内实验，比较四种模式在以下方面的差异：

- 认知负担。
- 控制感。
- 表达匹配度。
- 即时恢复感。
- 安全感。
- 偏好和可继续使用意愿。

### Contribution 3：部署贡献

通过 Study 3 的 4 周社区部署，说明系统在真实康复流程中的使用方式：

- 患者如何选择模式。
- 哪些场景需要治疗师帮助。
- 哪些设计降低负担。
- 哪些安全边界是必要的。
- 系统如何成为患者和治疗师讨论环境、情绪和恢复需求的中介物。

### Contribution 4：设计原则

输出面向精神健康 GenAI 共创系统的设计原则：

- AI agency 应可调节，而不是越自动越好。
- 对临床/脆弱人群，参数化入口比开放 prompt 更稳定。
- 创作控制感本身可能是恢复体验的一部分。
- 不适检测必须嵌入每次会话。
- 治疗师角色应被设计进系统流程。
- 日志记录要足够分析，但避免监控感。

## 4. 理论框架

建议用三个理论框架支撑 CHI 叙事。

### 4.1 AI Agency Spectrum

把四种模式解释为用户控制权和 AI 主动性的变化：

| 模式 | 用户控制 | AI 主动性 | 核心问题 |
|---|---:|---:|---|
| 自由创作 | 高 | 中 | 控制感强，但操作负担是否过高 |
| 灵感创想 | 中高 | 中高 | 非文字表达是否有助于低语言负担参与 |
| 对话改造 | 中 | 高 | 自然语言是否更能表达情绪，但带来解释偏差 |
| 智能参数 | 中 | 中 | 参数化是否在低负担和控制感之间取得平衡 |

### 4.2 Restorative Environment Design

将环境心理学变量转译为界面控制：

- 绿化程度：自然性和软吸引。
- 人造元素：设施、秩序、可达性。
- 环境活力：静谧到活跃的刺激水平。
- 光线温度：安全、温暖、清醒或放松。
- 情绪目标：用户希望环境带来的状态。

### 4.3 Safety-by-Design in Mental Health HCI

围绕精神健康场景强调：

- 最小化开放式风险输入。
- 明确系统不是治疗替代。
- 支持治疗师在场。
- 每次会话后做不适检测。
- 不保存不必要的敏感文本。
- 不用拟人化语言制造依赖。

## 5. 研究总结构

推荐写成三阶段混合方法研究：

| 阶段 | 目的 | 样本 | 方法 | 论文作用 |
|---|---|---:|---|---|
| Study 1 | 形成设计需求 | 患者 12-18，治疗师/医生 8-12 | 访谈、原型走查、图片卡片排序 | 解释系统为什么这样设计 |
| Study 2 | 比较四种模式 | 患者 32-40 | 受试者内实验、量表、访谈 | 主实证贡献 |
| Study 3 | 真实场景部署 | 患者 30-50，治疗师 6-10 | 4 周部署、日志、周反馈、访谈 | 生态有效性和设计原则 |

如果时间有限，CHI 主投稿最低配置应保留：

- Study 2 四模式对比。
- Study 3 短期部署。
- Study 1 可以压缩为专家访谈 + 患者走查，但不能完全没有形成性研究。

## 6. Study 2 深化：四模式受试者内对比实验

### 6.1 研究问题

RQ2.1：四种环境共创模式在认知负担、控制感、表达匹配度和即时恢复感上有何差异？

RQ2.2：精神障碍社区康复人群更偏好哪种 AI agency 关系，为什么？

RQ2.3：哪些模式更容易需要治疗师帮助，哪些模式更容易产生不适、困惑或失控感？

### 6.2 预期假设

H1：智能参数模式的认知负担最低。

H2：自由创作模式的控制感最高，但任务时长和帮助需求也更高。

H3：对话改造模式的表达匹配度较高，但安全担忧和理解偏差风险更高。

H4：灵感创想模式适合非文字表达者，但对识别准确性更敏感。

### 6.3 设计

设计类型：

- 受试者内设计。
- 每名参与者体验四种模式。
- 使用 4x4 Latin square 平衡顺序。
- 每种模式使用同一个任务目标和同类起始环境。

建议样本：

- 目标样本 32-40 名稳定期精神障碍患者。
- 最低可行样本 24 名。
- 若临床招募困难，可加入 8-12 名治疗师作为专家评价补充，但主分析应以患者为主。

实验任务：

> 请把这个环境改造成一个让你更安全、更放松、或更愿意停留的地方。

起始环境：

- 使用统一的中性社区/庭院/室外空间图片。
- 不建议让每人上传完全不同图片，否则四模式比较会混入图片差异。
- 可以准备 2-3 张起始图，按参与者随机分配，但四个模式内保持同一张。

每种模式时长：

- 教学 2 分钟。
- 操作 8 分钟。
- 生成和查看结果 2-3 分钟。
- post-mode 量表 3-5 分钟。
- 中间休息 2-3 分钟。

总时长：

- 约 90-110 分钟。
- 精神障碍人群不建议超过 2 小时。

### 6.4 Study 2 实验流程

1. 研究说明和知情同意，10 分钟。
2. 基线信息和安全确认，10 分钟。
3. 四种模式总教程，5 分钟。
4. 按 Latin square 进入模式 1。
5. 模式前即时情绪评分，30 秒。
6. 模式任务，8-10 分钟。
7. 模式后量表，3-5 分钟。
8. 休息 2-3 分钟。
9. 重复步骤 4-8，直到完成四个模式。
10. 总体 SUS、UES-SF 和四模式排序，8-10 分钟。
11. 半结构访谈，15-20 分钟。

### 6.5 Study 2 量表和填写时间点

#### 基线，只填一次

| 内容 | 推荐工具 | 目的 |
|---|---|---|
| 人口学 | 自编表 | 样本描述 |
| 数字素养 | 简短数字素养条目 | 控制协变量 |
| 既往 AI 使用 | 自编 3 项 | 解释偏好差异 |
| 当前心理状态 | PHQ-9、GAD-7 可选 | 样本描述，不作为 HCI 主结局 |
| 安全筛查 | 研究医生/治疗师确认 | 确认适合参与 |

#### 每个模式前，各填一次

建议 2 个 0-10 分视觉模拟评分：

- 当前心情愉悦度。
- 当前紧张/焦虑程度。

用途：控制不同模式开始前的状态差异。

#### 每个模式后，各填一次

每种模式后填一组短表。每人会填 4 次。

| 指标 | 推荐量表/条目 | 说明 |
|---|---|---|
| 认知负担 | NASA-TLX raw 6 项 | 不做加权，直接用 6 项原始均分 |
| 即时恢复感 | PRS-5 或 PRS short | 评估这张环境是否恢复性 |
| 控制感 | 自编 1-2 项 | “我能控制这个环境如何变化” |
| 表达匹配度 | 自编 1-2 项 | “结果表达了我想要的感觉” |
| 安全/不适 | 自编 1 项 | 无、轻微、中等、明显 |
| 再次使用意愿 | 自编 1 项 | 0-10 分 |

不建议每个模式都填完整 SUS。SUS 是总体系统可用性量表，四遍填写会很累，也不一定适合短任务对比。

#### 四个模式全部结束后，只填一次

| 内容 | 工具 | 目的 |
|---|---|---|
| 总体可用性 | SUS | 整个系统是否可用 |
| 总体参与度 | UES-SF | 参与感、吸引力、耐用性 |
| 模式偏好 | 排序题 | 最喜欢到最不喜欢 |
| 模式适用情景 | 半结构访谈 | 解释为什么 |
| 治疗师帮助体验 | 自编题/访谈 | 评估人机协作 |

### 6.6 Study 2 程序记录

每个模式必须记录：

- `participant_code`
- `mode_used`
- `order_index`
- `task_id`
- `mode_started_at`
- `mode_ended_at`
- `duration_seconds`
- `task_completed`
- `selected_mood_goal`
- `generation_count`
- `generated_success`
- `saved_result`
- `discomfort_flag`
- `assistance_level`

模式特异记录：

- 自由创作：最终元素数。
- 灵感创想：笔画数、标注数。
- 对话改造：文本长度、情绪标签数量，不默认导出完整文本。
- 智能参数：四个参数最终值。

### 6.7 Study 2 分析计划

量化：

- 线性混合效应模型：`score ~ mode + order + (1 | participant)`。
- 非正态时用 Friedman test + 事后比较。
- 控制协变量：数字素养、既往 AI 使用、基线症状、模式顺序。

定性：

- 半结构访谈做 reflexive thematic analysis。
- 重点编码：控制感、表达、负担、安全、治疗师帮助、模式偏好。

核心图表：

- 四模式雷达图：负担、控制、表达、恢复感、安全。
- 模式偏好 Sankey 或排序热图。
- AI agency spectrum 图。
- 典型参与者路径图。

## 7. Study 3 深化：4 周社区部署研究

### 7.1 研究问题

RQ3.1：系统在真实社区康复流程中能否被稳定持续使用？

RQ3.2：患者在自然部署中如何选择四种模式，不同模式承担什么角色？

RQ3.3：治疗师如何帮助患者完成 AI 环境共创，何时需要介入？

RQ3.4：哪些设计因素影响安全感、可继续使用意愿和现实迁移？

### 7.2 设计

设计类型：

- 4 周真实场景部署。
- 混合方法。
- 不作为临床疗效试验。
- 关注可用性、接受度、参与轨迹和安全。

样本：

- 30-50 名稳定期精神障碍患者。
- 6-10 名治疗师/社工。
- 2-4 个社区康复点。

使用频率：

- 每周 2-3 次。
- 每次 15-20 分钟。
- 总目标 8-12 次。

模式开放策略：

- 第 1 周：四种模式都由治疗师带领体验一次。
- 第 2-4 周：允许参与者自由选择模式。

这样既能观察真实偏好，也不会让初次使用者只固定在某个入口。

如果你想把 Study 3 与后续 RCT 更紧密衔接，也可以设置：

- A 方案：Study 3 开放四模式，观察自然选择。
- B 方案：Study 3 后半段固定推荐“智能参数模式”，检验它是否适合 RCT。

### 7.3 Study 3 会话流程

每次 15-20 分钟：

1. 治疗师确认当天状态适合参与。
2. 患者填写 2 个会话前即时评分。
3. 选择情绪目标。
4. 选择模式或进入指定模式。
5. 完成环境改造和生成。
6. 保存或放弃结果。
7. 填写 5 个会话后短评分。
8. 治疗师记录帮助程度和安全事件。

### 7.4 Study 3 量表和填写时间点

#### 部署前 T0，只填一次

| 内容 | 工具 | 用途 |
|---|---|---|
| 人口学和数字素养 | 自编简表 | 样本描述 |
| 既往 AI/游戏经验 | 自编简表 | 解释使用偏好 |
| 心理状态 | PHQ-9、GAD-7 或 WHO-5 | 描述样本，不主打疗效 |
| 系统期待 | 自编 3 项 | 比较期待和实际体验 |
| 安全确认 | 治疗师/医生记录 | 确认适合参与 |

#### 每次使用前，填 2 项

- 当前心情愉悦度，0-10。
- 当前紧张/焦虑程度，0-10。

#### 每次使用后，填 5 项

- 我的心情比刚才更好。
- 我的紧张/焦虑比刚才更低。
- 这个环境让我有恢复感。
- 我感觉自己能控制创作过程。
- 本次使用让我不适或更焦虑。

每次实验只需要这 5 项，约 1 分钟。不要每次都填 SUS、UES-SF 或完整 PHQ/GAD。

#### 每周一次

| 内容 | 工具 | 用途 |
|---|---|---|
| 本周继续使用意愿 | 自编 1 项 | 接受度趋势 |
| 本周最喜欢模式 | 排序/单选 | 模式自然偏好 |
| 本周最大困难 | 自编开放题 | 发现部署问题 |
| 本周安全/不适 | 自编 1-2 项 | 安全追踪 |
| 治疗师观察 | 简短记录 | 人机协作分析 |

#### 4 周结束 T1，只填一次

| 内容 | 工具 | 用途 |
|---|---|---|
| 总体可用性 | SUS | 系统可用性 |
| 总体参与度 | UES-SF | 参与质量 |
| 满意度 | CSQ-8 或自编满意度 | 接受度 |
| 幸福感/心理状态 | WHO-5，PHQ-9/GAD-7 可选 | 探索性变化 |
| 模式偏好 | 排序题 | 自然部署后的偏好 |
| 半结构访谈 | 访谈提纲 | 设计原则 |

#### 1 个月随访，可选

只问：

- 是否还记得/想再次使用某个环境。
- 是否把生成图像用于自我调节。
- 是否愿意在社区康复中继续使用。

### 7.5 Study 3 程序记录

每次会话必须记录：

- `participant_code`
- `visit_number`
- `scheduled_week`
- `mode_used`
- `started_at`
- `ended_at`
- `duration_seconds`
- `completed`
- `selected_mood_goal`
- `generation_count`
- `generated_success`
- `saved_result`
- `assistance_level`
- `discomfort_flag`
- `adverse_event_flag`

分析足够了。不需要记录每一次撤回、每一次坐标移动。

### 7.6 Study 3 分析计划

量化：

- 完成率。
- 平均每周使用次数。
- 每次平均时长。
- 模式选择分布。
- 不适事件比例。
- 治疗师帮助程度分布。
- 即时情绪变化：post - pre。
- 使用轨迹聚类：探索型、参数型、对话型、低参与型。

定性：

- 患者访谈：表达、控制、安全、恢复感、现实迁移。
- 治疗师访谈：何时介入、如何解释、工作负担、安全担忧。
- 现场观察：流程是否打断社区康复节奏。

核心输出：

- 真实世界使用轨迹。
- 治疗师参与的设计模型。
- 面向精神健康 GenAI 共创系统的部署原则。

## 8. 量表选择总表

| 量表/指标 | Study 2 时间点 | Study 3 时间点 | 作用 |
|---|---|---|---|
| PHQ-9 | 基线，可选 | T0/T1，可选 | 样本描述，探索性心理状态 |
| GAD-7 | 基线，可选 | T0/T1，可选 | 样本描述，探索性焦虑 |
| WHO-5 | 基线可选 | T0/T1 推荐 | 幸福感/恢复状态 |
| NASA-TLX raw | 每个模式后 | 不建议每次填 | 比较模式认知负担 |
| PRS-5/PRS short | 每个模式后 | 每次后可用 1-2 项短版 | 即时恢复感 |
| Perceived Control | 每个模式后 | 每次后 | 控制感 |
| Expression Fit | 每个模式后 | 可选 | 结果是否表达想要的感觉 |
| SUS | 四模式全部结束后一次 | T1 结束一次 | 总体可用性 |
| UES-SF | 四模式全部结束后一次 | T1 结束一次，可每周用超短版 | 总体参与度 |
| CSQ-8 | 不必须 | T1 结束一次 | 满意度/可接受性 |
| 不适/安全项 | 每个模式后 | 每次后 + 每周 | 安全监测 |
| 模式偏好排序 | 四模式结束后 | T1 结束一次 | 偏好与个体化设计 |

量表来源参考：

- NASA-TLX 官方说明见 [NASA TLX](https://human-factors.arc.nasa.gov/groups/TLX/) 和 [NASA Software Catalog](https://software.nasa.gov/software/ARC-15150-1A)。
- SUS 原始条目来源 Brooke 的 [SUS - A quick and dirty usability scale](https://www.websm.org/db/12/16455/Web)。
- UES-SF 可参考 O'Brien、Cairns、Hall 的 [User Engagement Scale short form](https://oro.open.ac.uk/68806/)。
- PRS 短版可参考 [Perceived Restorativeness Scale shorter version](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.01735/full)。

## 9. 后端高价值日志

完整工程计划见：

[hci_backend_core_logging_plan.md](D:/SSH/环境游戏程序/healing-environment/docs/hci_backend_core_logging_plan.md)

HCI 论文需要的最小核心日志：

- `participant_code`
- `study_phase`
- `site_id`
- `mode_used`
- `order_index`
- `task_id`
- `started_at`
- `ended_at`
- `duration_seconds`
- `task_completed`
- `selected_mood_goal`
- `generated_success`
- `generation_count`
- `saved_result`
- `green_level`
- `urban_level`
- `vitality_level`
- `light_warmth`
- `element_count`
- `text_length`
- `sketch_stroke_count`
- `pre_mood`
- `post_mood`
- `restorativeness`
- `perceived_control`
- `discomfort_flag`
- `assistance_level`

## 10. CHI 论文大纲

### Abstract

写清楚：

- 问题：精神障碍人群需要低负担、可控、安全的数字康复表达工具。
- 方法：形成性研究 + 四模式受试者内对比 + 4 周社区部署。
- 发现：四种 AI agency 模式在负担、控制、表达和安全上形成不同取舍。
- 贡献：系统、实证发现、部署经验、设计原则。

### 1. Introduction

逻辑：

1. 精神障碍社区康复需要支持情绪表达和恢复体验的低门槛工具。
2. 恢复性环境共创把情绪调节、环境偏好和自我控制结合起来。
3. 生成式 AI 提供新机会，但开放 prompt 对临床人群有认知和安全风险。
4. HCI 尚缺少对不同 AI agency 模式在精神健康场景中的系统比较。
5. 本文通过三阶段研究提出设计原则。

### 2. Related Work

建议三块：

- Digital mental health and HCI。
- Generative AI for mental health support。
- Human-AI co-creation, agency, and visual expression。

### 3. System Design

写：

- 设计目标。
- 四模式。
- 恢复性环境变量。
- 治疗师辅助流程。
- 内容安全和数据最小化。
- 后端核心日志。

### 4. Study 1: Formative Design

写：

- 参与者。
- 访谈和原型走查。
- 设计需求。
- 安全边界。
- 四模式如何由需求推导出来。

### 5. Study 2: Controlled Mode Comparison

写：

- 受试者内设计。
- Latin square。
- 任务材料。
- 量表时间点。
- 日志字段。
- 统计分析。
- 结果图表。

### 6. Study 3: Field Deployment

写：

- 部署场景。
- 使用频率。
- 治疗师角色。
- 每次短量表。
- 日志与访谈。
- 使用轨迹和安全结果。

### 7. Findings

建议组织成 4 个发现：

1. 参数化交互降低负担，但牺牲部分表达深度。
2. 直接操控增强控制感，但需要更多治疗师帮助。
3. 文本和草图支持个体化表达，但需要更明确的安全边界。
4. 治疗师把系统从“AI 工具”转化为“康复对话媒介”。

### 8. Discussion

讨论：

- Adjustable agency for vulnerable users。
- Co-creation as emotional articulation。
- Safety as situated human-AI collaboration。
- Minimal logging as ethical infrastructure。
- 与 RCT 的关系：HCI 解释交互机制，RCT 验证疗效。

### 9. Design Implications

输出 6-8 条原则：

- 先情绪目标，后环境控制。
- 为低负担入口提供参数化控制。
- 为深表达保留文本/草图，但增加安全边界。
- 将治疗师作为设计对象。
- 每次会话都做不适检测。
- 让用户保存、命名、回看环境结果。
- 记录会话级核心数据，不做微行为监控。
- 让 AI 生成有失败恢复和再尝试机制。

### 10. Limitations

写：

- 样本来自稳定期人群，不代表急性期。
- 四周部署不能证明临床疗效。
- 生成模型版本变化影响可重复性。
- 研究场景可能受治疗师支持影响。
- 文化和地区限制。

### 11. Conclusion

强调：

生成式 AI 的价值不是自动治疗，而是在安全边界内支持患者表达恢复需求、体验控制感，并与治疗师共同形成可讨论的恢复性环境。

## 11. 近年 CHI 参考文献与可借鉴点

### 11.1 数字心理健康与 LLM 心理支持

1. [Facilitating Self-Guided Mental Health Interventions Through Human-Language Model Interaction: A Case Study of Cognitive Restructuring](https://doi.org/10.1145/3613904.3642761), CHI 2024.

   内容：研究语言模型如何支持自助式心理健康干预中的认知重构。相关摘要指出，自助心理干预有潜力扩大可及性，但可能认知负担高、情绪触发强。  
   借鉴：你的 Study 2 应把“认知负担”和“情绪触发/不适”作为核心指标，而不是只测满意度。

2. [Evaluating the Experience of LGBTQ+ People Using Large Language Model Based Chatbots for Mental Health Support](https://doi.org/10.1145/3613904.3642482), CHI 2024.

   内容：研究 LGBTQ+ 人群使用 LLM 聊天机器人进行心理支持的体验。  
   借鉴：对脆弱或边缘化人群使用 GenAI，论文必须写清身份、安全、信任和适配问题。

3. [Understanding the Benefits and Challenges of Deploying Conversational AI Leveraging Large Language Models for Public Health Intervention](https://doi.org/10.1145/3544548.3581503), CHI 2023.

   内容：研究 CareCall 这类 LLM 驱动公共卫生对话系统的部署，包含用户、远程操作者和开发者等 34 名利益相关者。  
   借鉴：你的 Study 3 不能只访谈患者，也要访谈治疗师/社工，因为部署中的人机协作和责任分配是 CHI 很看重的点。

4. [Exploring Effects of Chatbot-based Social Contact on Reducing Mental Illness Stigma](https://doi.org/10.1145/3544548.3581384), CHI 2023.

   内容：设计第一人称和第三人称叙事聊天机器人，用混合方法研究其对精神疾病污名的影响。  
   借鉴：可以参考其“叙事 + 混合方法 + 心理健康态度变量”的写法；你的对话/环境生成也可以被解释为一种低威胁表达和反思媒介。

5. [Meeting Users Where They Are: User-centered Design of an Automated Text Messaging Tool to Support the Mental Health of Young Adults](https://doi.org/10.1145/3491102.3502046), CHI 2022.

   内容：通过在线讨论和设计工作坊，与有抑郁/焦虑症状的年轻人共创自动短信心理支持工具；参与者希望工具易用、可按心情调整参与深度，同时警惕过度拟人化语气。  
   借鉴：你的系统也应支持“可变参与深度”，并避免把 AI 说成像治疗师或朋友一样。

6. [Approaches to Tailoring Between-Session Mental Health Therapy Activities](https://doi.org/10.1145/3613904.3642856), CHI 2024.

   内容：访谈 13 名治疗师和 14 名来访者，研究治疗间活动如何根据技能、困难、不适和生活障碍进行个性化。  
   借鉴：你的 Study 3 可以把“治疗师如何调整任务难度、何时介入、如何处理不适”作为部署发现。

7. [“Can you be with that feeling?”: Extending Design Strategies for Interoceptive Awareness for the Context of Mental Health](https://doi.org/10.1145/3613904.3643054), CHI 2024.

   内容：结合心理治疗实践和 HCI 设计探针，探索如何支持心理健康中的内感受觉觉察；包含视觉隐喻、身体地图等表达方式。  
   借鉴：你的环境图像可以被写成“视觉隐喻和情绪表达媒介”，而不是单纯的 AI 画图。

8. [“This app said I had severe depression, and now I don’t know what to do”: the unintentional harms of mental health applications](https://doi.org/10.1145/3613904.3642178), CHI 2024.

   内容：分析 36 个抑郁自我管理应用的 6253 条用户评论，归纳心理健康应用的非预期伤害。  
   借鉴：你的论文必须主动讨论风险、退出机制、内容边界和“不替代治疗”的沟通方式。

9. [Challenges and Opportunities for the Design of Inclusive Digital Mental Health Tools: Understanding Culturally Diverse Young People's Experiences](https://doi.org/10.1145/3613904.3642641), CHI 2024.

   内容：研究文化和语言多样背景青年使用数字心理健康工具的障碍和需求，包含专业人员和 41 名青年参与者。  
   借鉴：你可以强调稳定期精神障碍人群的数字素养差异，并把低语言负担、低认知负担作为设计贡献。

10. [Societal-Scale Human-AI Interaction Design? How Hospitals and Companies are Integrating Pervasive Sensing into Mental Healthcare](https://doi.org/10.1145/3613904.3642793), CHI 2024.

    内容：讨论医院和企业如何把 AI 与感知技术整合到心理健康中，以及由此产生的制度、伦理和人机交互问题。  
    借鉴：你的后端日志要写成“最小必要数据”，避免被审稿人质疑对精神健康人群过度采集。

### 11.2 生成式 AI 与人机共创

11. [ContextCam: Bridging Context Awareness with Creative Human-AI Image Co-Creation](https://doi.org/10.1145/3613904.3642129), CHI 2024.

    内容：面向图像共创，结合环境信息和个人状态，支持用户与 AI 共同生成图像。  
    借鉴：你的系统同样是环境图像共创，但更聚焦精神健康场景；可以借鉴其“上下文 + 个人状态 + 图像生成”的系统叙事。

12. [Fashioning Creative Expertise with Generative AI: Graphical Interfaces for Design Space Exploration Better Support Ideation Than Text Prompts](https://doi.org/10.1145/3613904.3642908), CHI 2024.

    内容：比较图形化设计空间探索和纯文本 prompt，在生成式 AI 创意任务中图形界面更支持构思。  
    借鉴：这篇非常适合支撑你为什么不要只做对话 prompt，而要比较拖拽、草图和参数化界面。

13. [Understanding Nonlinear Collaboration between Human and AI Agents: A Co-design Framework for Creative Design](https://doi.org/10.1145/3613904.3642812), CHI 2024.

    内容：指出创意设计是非线性的，而很多 AI 设计工具过于线性；通过专家形成性研究和原型评估提出人机共设计框架。  
    借鉴：你的四模式可以写成不同的非线性共创路径，而不是四个孤立功能。

14. [Generative AI in the Wild: Prospects, Challenges, and Strategies](https://doi.org/10.1145/3613904.3642160), CHI 2024.

    内容：访谈 18 名创意行业 GenAI 用户，提出 Learning、Using、Assessing 框架，分析真实世界中 GenAI 共创的机会、挑战和策略。  
    借鉴：Study 3 可以模仿其真实使用场景取向，关注用户如何学习、使用和评估 AI 生成结果。

15. [A user-centered framework for human-AI co-creativity](https://doi.org/10.1145/3613905.3650929), CHI EA 2024.

    内容：提出人机共创中自动化和用户 agency/control 的用户中心框架。  
    借鉴：可作为你四模式 AI agency spectrum 的理论支持，但它是 CHI Extended Abstract，不是主会长文，引用时注意层级。

## 12. 投稿策略

### CHI 主会最强叙事

不要写：

> 我们做了一个 AI 疗愈环境程序，用户很喜欢。

要写：

> 我们研究了精神障碍社区康复场景中生成式 AI 共创的 agency、安全和表达问题。通过四模式受试者内对比和 4 周社区部署，我们发现低负担参数化、直接操控、文本表达和草图表达在控制感、认知负担、恢复感与安全性上形成可解释的取舍，并提出面向脆弱人群 GenAI 共创系统的设计原则。

### 最推荐数据组合

CHI 主投稿最好有：

- Study 2：32-40 名患者四模式对比。
- Study 3：30-50 名患者 4 周部署。
- 治疗师访谈：6-10 名。
- 高质量系统图和模式截图。
- 明确量表时间点。
- 安全事件完整报告。
- 强讨论，不把 AI 神化。

### 风险与补救

| 风险 | 补救 |
|---|---|
| 像应用展示 | 强化研究问题、理论框架、混合方法 |
| 临床疗效不显著 | 明确 HCI 论文不主打疗效 |
| 样本小 | 做受试者内设计 + 高质量访谈 |
| 四模式太散 | 用 AI agency spectrum 统一 |
| 安全风险被质疑 | 每次不适检测 + 治疗师在场 + 最小日志 |
| 量表负担过重 | 每次只填短评分，完整量表只在关键时间点 |

## 13. 近期执行清单

1. 完成 HCI 后端核心日志改造。
2. 固定 Study 2 的四模式任务材料和起始图片。
3. 编写 Study 2 Latin square 随机顺序脚本。
4. 做 3-5 名内部人员流程测试。
5. 邀请 3 名治疗师评估量表负担。
6. 先做 8-10 名患者试运行，检查是否超过 2 小时。
7. 修订量表和流程。
8. 正式开展 Study 2。
9. 根据 Study 2 结果决定 Study 3 是否开放四模式或主推某一模式。
10. 4 周社区部署并同步做治疗师访谈。

最关键判断：

> CHI 论文不是证明你的程序“治病”，而是证明你发现并系统研究了一个重要 HCI 问题：在精神健康高风险场景中，生成式 AI 共创应该如何分配控制权、降低负担、支持表达并保持安全。
