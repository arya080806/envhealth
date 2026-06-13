# 2026-06-13 科研记录归档与汇总表改造执行报告

## 本次改造目标

1. 按“线上生成归档，本地一键拉取”方案落地科研记录归档。
2. 本地生成 `index.xlsx` / `index.csv`，记录精确时间、参与者编号、姓名、会话、模式、生成次数、图片和 JSON 路径。
3. 让【模式使用次数】和【作品数量汇总】在飞书中按参与者编号实时更新，避免同一参与者多行。

## 已完成修改

### 1. 新增线上科研归档器

新增模块：`app/services/research_archive.py`

执行方式：

```bash
cd /home/zm/envhealth
python -m app.services.research_archive --output /home/zm/envhealth/research_exports
```

输出结构：

```text
/home/zm/envhealth/research_exports/
  index.xlsx
  index.csv
  manifest.json
  participants/
    参与者编号/
      会话ID_模式_场景/
        original.*
        generated_01.*
        generated_02.*
        operation_latest.*
        operation_for_generated_01.*
        canvas.json
        metadata.json
```

索引文件字段包含：

- 导出时间、会话创建时间、本次生成时间
- 参与者编号、姓名、本地用户 ID、会话 ID
- 模式、模式名称、场景类型、预设名称
- 第几次生成、生成总次数、生成状态
- 智能参数四项：绿化程度、城市化程度、活力程度、光照温暖度
- 对话改造输入/感受、情绪标签
- 自由创作元素数、灵感创想笔画数、AI 提示词
- 原图、修改后生成图片、修改操作/笔画图片、操作 JSON、元数据 JSON 路径

### 2. 新增本地一键拉取脚本

仓库脚本：

```text
tools/pull_research_exports.ps1
```

本地便捷脚本：

```text
D:\SSH\环境游戏程序\记录\pull_envhealth_research_exports.ps1
```

执行后会先让服务器重新生成 `/home/zm/envhealth/research_exports`，再拉取到：

```text
D:\SSH\环境游戏程序\记录
```

### 3. 汇总表按参与者编号更新

修改文件：`app/db.py`

已将【模式使用次数】和【作品数量汇总】的飞书唯一键从本地 `user_id` 改为：

```text
参与者编号优先；没有参与者编号时才退回 user_id
```

同时统计时会聚合同一参与者编号下的多个本地 user_id，减少重复登录、重新注册或测试登录造成的多行问题。

## 验证结果

本地烟测命令：

```bash
uv run python -m app.services.research_archive --output <临时目录>
```

结果：

- 导出 session：128 个
- 索引行：129 行
- 复制图片/JSON：166 个
- `index.csv` 与 `index.xlsx` 均成功生成
- 缺失文件仅为本地测试占位路径 `test://drag.png`、`test://inspire.png`，不属于真实患者素材

## 部署后还需要执行

1. 部署新版代码到线上。
2. 线上重新排队并同步【模式使用次数】、【作品数量汇总】。
3. 清理飞书中旧的以本地 user_id 作为“汇总键”的重复汇总行。
4. 运行本地拉取脚本，生成并下载最新科研归档。

