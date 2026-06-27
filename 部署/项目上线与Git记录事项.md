# 环境疗愈项目上线与 Git 记录事项

更新时间：2026-06-11

## 一、线上访问地址

- 主站：https://envhealth.cn
- www：https://www.envhealth.cn
- 健康检查：https://envhealth.cn/api/status

当前健康检查正常时应返回：

```json
{"server":"running","model_loaded":true}
```

## 二、GitHub 仓库

- 仓库 SSH 地址：`git@github.com:arya080806/envhealth.git`
- 当前本地 remote 使用 HTTPS：`https://github.com/arya080806/envhealth.git`
- 线上部署分支：`main`
- 本地工作分支当前为：`master`
- 推送方式：`git push origin HEAD:main`

说明：

- 本机之前 SSH 推送 GitHub 失败，原因是 GitHub SSH key 未配置成功。
- 当前使用 GitHub CLI 登录后的 HTTPS remote，可以正常推送。
- 服务器 `/home/zm/envhealth` 从 GitHub `main` 分支拉取代码。

## 三、服务器信息

- 服务器 IP：`43.167.184.248`
- SSH 用户：`zm`
- 常用 SSH 命令示例：

```bash
ssh -i ~/.ssh/id_rsa zm@43.167.184.248
```

Windows 本机常用命令：

```powershell
& 'C:\Program Files\Git\usr\bin\ssh.exe' -i "$env:USERPROFILE\.ssh\id_rsa" zm@43.167.184.248
```

## 四、服务器项目路径

- 线上项目目录：`/home/zm/envhealth`
- 线上 Nginx 配置：`/etc/nginx/conf.d/envhealth.cn.conf`
- 线上 systemd 服务：`/etc/systemd/system/envhealth.service`
- 项目内备份配置：
  - `部署/envhealth-nginx.conf`
  - `部署/envhealth.service`

## 五、线上运行方式

项目通过 systemd 常驻运行。

服务名：

```bash
envhealth.service
```

查看状态：

```bash
sudo systemctl status envhealth.service
```

重启服务：

```bash
sudo systemctl restart envhealth.service
```

查看最近日志：

```bash
sudo journalctl -u envhealth.service --no-pager -n 120
```

当前服务端口：

```text
6425
```

Nginx 将 `envhealth.cn` 和 `www.envhealth.cn` 反向代理到：

```text
http://127.0.0.1:6425
```

## 六、Nginx 与 HTTPS

Nginx 域名配置已启用：

```text
envhealth.cn
www.envhealth.cn
```

HTTPS 证书由 Certbot / Let’s Encrypt 管理。

证书位置：

```text
/etc/letsencrypt/live/envhealth.cn/fullchain.pem
/etc/letsencrypt/live/envhealth.cn/privkey.pem
```

检查 Nginx 配置：

```bash
sudo nginx -t
```

重载 Nginx：

```bash
sudo systemctl reload nginx
```

注意：

- 修改 Nginx 配置后必须先执行 `sudo nginx -t`。
- 通过后再 reload。
- NiceGUI 需要 WebSocket，Nginx 配置里必须保留：

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_read_timeout 3600;
proxy_send_timeout 3600;
```

## 七、标准修改与部署流程

以后本地修改项目后，推荐流程如下。

### 1. 本地修改代码

在本地项目目录修改：

```text
D:\SSH\环境游戏程序\healing-environment
```

### 2. 本地测试

至少执行：

```bash
uv run python -m compileall -q main.py app
```

如涉及页面交互，应打开本地或线上页面实际点一遍。

### 3. Git 保存

查看状态：

```bash
git status --short --branch
```

提交：

```bash
git add <修改的文件>
git commit -m "简短中文说明"
```

推送到 GitHub main：

```bash
git push origin HEAD:main
```

### 4. 服务器拉取与部署

登录服务器后执行：

```bash
cd /home/zm/envhealth
git pull --ff-only origin main
/home/zm/.local/bin/uv run python -m compileall -q main.py app
sudo systemctl restart envhealth.service
sudo systemctl is-active envhealth.service
curl --noproxy '*' -sS --max-time 20 https://envhealth.cn/api/status
```

预期：

```text
active
{"server":"running","model_loaded":true}
```

## 八、Git 规则与注意事项

- 不要直接在服务器手动改业务代码；应优先本地修改、提交、推 GitHub，再服务器拉取。
- 服务器如果临时修了代码，必须同步回本地和 GitHub，避免下次部署被覆盖。
- 每次部署前先看 `git status`，确认没有未提交的重要改动。
- 使用 `git pull --ff-only origin main`，避免服务器产生不清楚的 merge commit。
- 本地分支虽然叫 `master`，但线上分支是 GitHub 的 `main`。
- 当前推送命令建议固定使用：`git push origin HEAD:main`。
- 不要提交 `.env`、数据库、上传文件、日志等运行时数据。
- `.pyc` 通常不提交，但本项目曾有恢复页面依赖 `recovery_backup_20260529/pages_pyc/*.pyc` 的历史情况；如未来删除或调整该依赖，需要先确认页面加载不受影响。

## 九、运行时数据注意事项

线上运行数据主要在：

```text
/home/zm/envhealth/data
/home/zm/envhealth/uploads
/home/zm/envhealth/outputs
```

这些目录属于运行数据，不应随意删除。

数据库：

```text
/home/zm/envhealth/data/healing.db
```

修改数据库前必须先备份。

备份示例：

```bash
cp /home/zm/envhealth/data/healing.db /home/zm/envhealth/data/healing.db.bak.$(date +%Y%m%d_%H%M%S)
```

## 十、已修复的重要线上问题记录

### 1. Nginx 域名 404

原因：Nginx 未配置 `envhealth.cn` server_name。

处理：

- 添加 `/etc/nginx/conf.d/envhealth.cn.conf`
- 配置反向代理到 `127.0.0.1:6425`
- 使用 certbot 启用 HTTPS

### 2. 登录/注册点击像是无效

原因：

- 线上旧数据中 `users.participant_id` 已占用某些编号。
- 原编号生成只检查 `hci_participants.participant_code`，没有检查 `users.participant_id`。
- 注册时触发 `UNIQUE constraint failed: users.participant_id`。
- 异常后连接没有正确 rollback，进一步导致 `database is locked`。

处理：

- 编号生成同时检查 `users` 和 `hci_participants`。
- SQLite 设置 `timeout=30` 和 `PRAGMA busy_timeout=30000`。
- 登录/注册写库使用 `BEGIN IMMEDIATE`。
- 异常时 rollback 并关闭连接。

### 3. 登录按钮误创建新编号

原因：

- 旧逻辑中，“登录”找不到同名同性参与者时，会继续创建新编号。

现逻辑：

- 点“登录”：只登录已有参与者；找不到则提示“未找到已有参与者，请点击‘注册’创建新编号”。
- 点“注册”：才创建新编号。

## 十一、常用排查命令

查看服务：

```bash
sudo systemctl status envhealth.service
```

查看错误日志：

```bash
sudo journalctl -u envhealth.service --since "10 minutes ago" --no-pager | grep -E "ERROR|Traceback|UNIQUE|locked"
```

测试本机服务：

```bash
curl --noproxy '*' -sS --max-time 20 http://127.0.0.1:6425/api/status
```

测试 HTTPS：

```bash
curl --noproxy '*' -sS --max-time 20 https://envhealth.cn/api/status
```

查看 Nginx 是否加载域名配置：

```bash
sudo nginx -T | grep -E "envhealth.cn|listen|server_name" -n
```

## 十二、给未来对话的提示

如果以后在别的对话中继续处理本项目，请先查看本文件。

优先确认：

1. 本地目录是否为 `D:\SSH\环境游戏程序\healing-environment`。
2. GitHub 仓库是否为 `https://github.com/arya080806/envhealth.git` / `git@github.com:arya080806/envhealth.git`。
3. 线上目录是否为 `/home/zm/envhealth`。
4. 服务是否为 `envhealth.service`。
5. 域名是否为 `https://envhealth.cn` 和 `https://www.envhealth.cn`。
6. 部署后必须验证 `/api/status`。

---

## 十三、2026-06-27 本地最新版本 Git 保存记录

记录时间：2026-06-27 22:58:28 +08:00  
项目目录：`D:\SSH\环境游戏程序\healing-environment`  
GitHub 仓库：`git@github.com:arya080806/envhealth.git`  
当前分支：`master`（推送到远端 `main`）

| 项目 | 内容 |
| --- | --- |
| 保存提交短号 | `4bd46d4` |
| 保存提交完整哈希 | `4bd46d43095955a739f289bf654ca0104d72503b` |
| 提交时间 | `2026-06-27T22:58:19+08:00` |
| 提交人 | `Codex <codex@local>` |
| 提交说明 | `保存拖拽标注与安全策略快照` |

本次保存内容：

- 拖拽创作画布新增元素标注面板，支持对单个放置元素补充用户意图，并随画布 JSON/布局提交给后端。
- 拖拽生成 API 会保留并安全转译元素标注，生成 prompt 优先参考用户标注，再结合基础元素描述。
- 安全策略允许鸟、飞鸟、蝴蝶、彩虹等在用户明确选择时以真实、温和、低刺激方式出现。
- 安全 prompt 增加现实物理约束，要求路灯、构筑物、树木、亭子、风车等实体落地或有合理支撑，避免悬空漂浮。
- 调整拖拽元素库，移除萤火虫、月光等更易引发误生成的氛围项。
- 新增和更新安全策略测试，覆盖元素标注优先、低刺激自然元素转译、物理约束提示和生成 prompt 内容。

提交统计：

- 变更文件：6 个
- 新增行：496 行
- 删除行：35 行

校验记录：

- `py -3 -m compileall app tests`
- `uv run python -m compileall app tests`
- `uv run python -m unittest tests.test_safety_policy`
