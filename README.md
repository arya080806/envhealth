# 项目启动说明

以后每次打开项目或重启项目，都统一按服务器地址访问：

- 浏览器打开地址：`http://43.167.184.248:6420`

## 启动方式

### 1. 在 Linux 服务器中启动项目
在项目根目录执行：

```bash
nohup uv run python main.py >> server_stdout.log 2>> server_stderr.log < /dev/null &
```

### 2. 重启项目
在项目根目录执行：

```bash
./restart.sh
```

## 打开方式
启动或重启完成后，在 Cursor 浏览器中打开：

```text
http://43.167.184.248:6420
```

## 补充说明
- 不再默认使用本地 `http://localhost:6420`
- 以后凡是"打开项目"或"重启项目"，默认都按服务器地址 `http://43.167.184.248:6420` 处理
- Windows 下也可以通过 `start_bg.bat` 间接启动，但打开地址仍然使用服务器地址：`http://43.167.184.248:6420`

## 开发说明
- 当前 `main.py` 中 `reload=False`，代码修改后需要执行 `./restart.sh` 重启才能生效
- 如果仅修改前端（Python 页面文件、静态 JS/CSS），也需要重启服务后刷新浏览器
- 面向研究人员查看的数据看板、飞书多维表格、导出说明和用户可见字段，默认使用中文显示名。
- 后端代码、数据库字段、环境变量和同步类型可以保留英文技术名，但相关 Markdown 文档必须提供中文解释或中文映射，避免只出现英文缩写。
- 飞书默认主列、系统自动字段等无法删除的字段，应改成中文提示名，例如 `系统主列_忽略`；科研导出时可忽略。

## 环境变量

图像生成服务不再在源码中硬编码密钥。部署或本地实验前请设置：

```bash
export HEALING_IMAGE_API_KEY="你的图像生成服务密钥"
export HEALING_IMAGE_API_URL="https://aihubmix.com/v1"
export HEALING_IMAGE_MODEL="gpt-image-2"
export HEALING_IMAGE_SIZE="auto"
export HEALING_IMAGE_QUALITY="auto"
export HEALING_IMAGE_OPERATION="edit"
export HEALING_IMAGE_EDIT_MAX_SIZE="1536"
export HEALING_EXPORT_KEY="研究者导出密码"
```

Windows PowerShell 示例：

```powershell
$env:HEALING_IMAGE_API_KEY="你的图像生成服务密钥"
$env:HEALING_IMAGE_API_URL="https://aihubmix.com/v1"
$env:HEALING_IMAGE_MODEL="gpt-image-2"
$env:HEALING_IMAGE_SIZE="auto"
$env:HEALING_IMAGE_QUALITY="auto"
$env:HEALING_IMAGE_OPERATION="edit"
$env:HEALING_IMAGE_EDIT_MAX_SIZE="1536"
$env:HEALING_EXPORT_KEY="研究者导出密码"
```
