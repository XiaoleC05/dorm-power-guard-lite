# 部署说明（oxelia51.com）

## 服务器目录

```text
/opt/dorm-power-guard-lite/
├── backend/          # FastAPI + NoneBot
│   ├── .env          # 仅保留在服务器，不被 CI 覆盖
│   └── venv/
├── frontend/dist/    # GitHub Actions 构建产物
└── deploy/           # nginx / systemd 模板
```

## 首次初始化

```bash
ssh <your-server>
bash /opt/dorm-power-guard-lite/deploy/bootstrap-server.sh
```

在 `backend/.env` 中配置（勿提交到 Git）：

```env
APP_DEBUG=false
ADMIN_USERNAME=root
ADMIN_PASSWORD=<至少12位强随机密码>
ADMIN_JWT_SECRET=<至少32位随机字符串>
QQ_BOT_API_TOKEN=<至少32位随机字符串>
```

修改密码或 JWT 后执行：`systemctl restart dorm-backend dorm-nonebot`

## GitHub Secrets

| Name | Value |
|------|-------|
| SSH_HOST | 服务器 IP 或主机名 |
| SSH_USER | SSH 用户名 |
| SSH_PRIVATE_KEY | 部署专用私钥 |

## 登录

- 地址：https://oxelia51.com（备案通过后）或服务器 IP
- 用户名：`ADMIN_USERNAME`（默认 root）
- 密码：服务器 `backend/.env` 中的 `ADMIN_PASSWORD`（非代码默认值）

## 内存优化

- 前端在 GitHub Actions 构建，服务器不安装 Node
- systemd `MemoryMax` 限制 backend 256M / nonebot 128M
- NapCat Docker `mem_limit: 256m`
- MySQL `innodb_buffer_pool_size=64M`
