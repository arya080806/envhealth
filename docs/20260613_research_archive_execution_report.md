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

## 实际部署与执行结果

### 1. Git 与线上部署

已推送到 GitHub `main` 并同步到服务器：

```text
当前线上版本：552bfaa
```

健康检查结果：

```json
{"server":"running","model_loaded":true}
```

### 2. 线上归档生成与本地拉取

已在线上生成：

```text
/home/zm/envhealth/research_exports
```

并已拉取到本地：

```text
D:\SSH\环境游戏程序\记录
```

本地文件包含：

```text
index.xlsx
index.csv
manifest.json
research_exports_latest.tar.gz
participants/
```

实际导出结果：

- 线上导出 session：98 个
- 索引行：99 行
- 本地 participants 文件：231 个
- 压缩包大小：约 358 MB

注意：本次线上导出中有 10 个缺失源文件，均为早期记录中保存的 Windows 本地路径，例如 `D:\python\环境游戏程序\...`。这些文件不在服务器磁盘上，因此无法从线上补齐。后续通过 envhealth.cn 正常生成的新记录会直接保存在服务器 `uploads/outputs` 下，可以正常归档。

### 3. 飞书汇总表去重与实时更新

已重新排队并同步【模式使用次数】和【作品数量汇总】。

已清理旧口径记录：

- 【模式使用次数】：删除旧 `user_id` 汇总键记录 11 条
- 【作品数量汇总】：删除旧 `user_id` 汇总键记录 11 条

复核结果：

- 【模式使用次数】：9 行，参与者编号无重复
- 【作品数量汇总】：9 行，参与者编号无重复
- 当前两张表的 `汇总键` 已与 `参与者编号` 一致

## 后续使用方法

以后需要拉取最新科研记录时，运行：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\SSH\环境游戏程序\记录\pull_envhealth_research_exports.ps1"
```

脚本会自动：

1. 在线上重新生成 `/home/zm/envhealth/research_exports`
2. 打包为 `/tmp/envhealth_research_exports.tar.gz`
3. 下载到本机临时目录
4. 解压到 `D:\SSH\环境游戏程序\记录`
5. 更新 `index.xlsx`、`index.csv` 和 `participants/`
