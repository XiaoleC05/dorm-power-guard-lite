# DormPowerGuard-Lite

西华大学宿舍电费监控系统 - MVP快速验证方案

## 项目简介

这是一个针对**西华大学一卡通宿舍用电小程序**的轻量级电费监控系统，通过Python爬虫定时抓取电费数据，当余额低于设定阈值时自动发送邮件或QQ消息告警。

**管理员QQ：714085964**

> 本项目专门为西华大学学生设计，用于监控宿舍电费使用情况，避免因电费不足导致停电。

## 技术栈

### 后端
- **FastAPI** - 轻量级Web框架
- **APScheduler** - 定时任务调度
- **SQLAlchemy** - ORM框架
- **MySQL** - 数据库
- **BeautifulSoup4** - HTML解析（爬虫）

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI组件库
- **ECharts** - 数据可视化
- **Vite** - 构建工具

## 项目结构

```
dorm-power-guard-lite/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models.py       # 数据库模型
│   │   ├── schemas.py      # Pydantic模型
│   │   ├── services.py     # 业务逻辑
│   │   ├── crawler.py      # 爬虫模块
│   │   ├── alert.py        # 告警模块
│   │   ├── scheduler.py    # 定时任务
│   │   ├── database.py     # 数据库连接
│   │   ├── config.py       # 配置管理
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python依赖
│   ├── .env.example        # 环境变量示例
│   ├── init_db.sql         # 数据库初始化SQL
│   └── run.py              # 启动脚本
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # 状态管理
│   │   ├── router/        # 路由配置
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
└── README.md              # 项目说明
```

## 快速开始

> **详细使用指南请参考：`使用指南.md`**

### 1. 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 2. 后端部署

#### 2.1 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2.2 配置数据库

创建MySQL数据库：

```bash
mysql -u root -p < init_db.sql
```

或者手动创建数据库并运行SQLAlchemy自动创建表。

#### 2.3 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际配置：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dorm_power_guard

# 爬虫配置（西华大学一卡通系统）
CRAWLER_BASE_URL=https://ecard.xhu.edu.cn
CRAWLER_API_BASE_URL=https://ecard.xhu.edu.cn/api
CRAWLER_DORM_NUMBER=320  # 您的宿舍号
# 认证信息需要通过抓包获取（详见抓包教程）
CRAWLER_OPENID=your_openid
CRAWLER_JSESSIONID=your_jsessionid
CRAWLER_ROOM_ID=your_room_id

# 定时任务配置（每天执行时间点）
SCHEDULER_HOURS=8,12,18,22

# 邮件配置（可选）
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@qq.com
EMAIL_SMTP_PASSWORD=your_email_password
EMAIL_FROM=your_email@qq.com
EMAIL_TO=recipient@example.com

# QQ机器人配置（可选）
QQ_BOT_ENABLED=true
QQ_BOT_TYPE=go-cqhttp
QQ_BOT_API_URL=http://localhost:5700
QQ_BOT_GROUP_ID=123456789
```

#### 2.4 配置西华大学一卡通认证信息

**重要**：本项目针对**西华大学一卡通宿舍用电小程序**，需要通过抓包工具获取认证信息。

**详细步骤请参考：**
- `抓包教程-快速版.md` - 快速上手指南
- `抓包教程-详细版.md` - 详细教程

简要流程：
1. 使用Charles/Fiddler等工具抓包分析西华大学一卡通小程序API
2. 提取 `openid` 和 `JSESSIONID`（Cookie）
3. 配置到 `.env` 文件
4. 系统会自动使用这些认证信息抓取电费数据

**快速测试**：
```bash
cd backend
python -c "from app.crawler import get_crawler; crawler = get_crawler(); print(crawler.fetch_power_data())"
```

#### 2.5 启动后端

```bash
python run.py
```

后端将在 `http://localhost:8000` 启动。

### 3. 前端部署

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动。

#### 3.3 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 功能说明

### 核心功能

1. **定时爬虫** - 每天在指定时间点自动抓取电费数据
2. **数据存储** - 将电费记录存入MySQL数据库
3. **告警通知** - 余额低于阈值时发送邮件或QQ消息
4. **监控面板** - Web界面查看电费状态和趋势

### API接口

#### 电费记录
- `POST /api/power/records` - 创建记录
- `GET /api/power/records/{dorm_number}/latest` - 获取最新记录
- `GET /api/power/records/{dorm_number}` - 获取记录列表

#### 告警管理
- `POST /api/alert/rules` - 创建告警规则
- `GET /api/alert/rules` - 获取所有规则
- `PUT /api/alert/rules/{dorm_number}` - 更新规则
- `DELETE /api/alert/rules/{dorm_number}` - 删除规则
- `GET /api/alert/logs` - 获取告警日志

#### 系统管理
- `POST /api/system/crawl` - 手动触发爬虫

## 数据库设计

### power_records（电费记录表）
- `id` - 主键
- `dorm_number` - 宿舍号
- `balance` - 电费余额
- `power_consumption` - 用电量（可选）
- `record_time` - 记录时间
- `created_at` - 创建时间

### alert_rules（告警规则表）
- `id` - 主键
- `dorm_number` - 宿舍号（唯一）
- `threshold` - 告警阈值
- `enabled` - 是否启用
- `email_enabled` - 是否启用邮件告警
- `qq_enabled` - 是否启用QQ告警
- `last_alert_time` - 最后告警时间

### alert_logs（告警日志表）
- `id` - 主键
- `dorm_number` - 宿舍号
- `balance` - 触发告警时的余额
- `threshold` - 告警阈值
- `alert_type` - 告警类型（email/qq）
- `alert_status` - 告警状态（success/failed）
- `alert_message` - 告警消息
- `created_at` - 创建时间

## 注意事项

1. **爬虫实现**：需要根据实际电费查询网站实现爬虫逻辑，可能需要处理：
   - 登录验证码
   - Session管理
   - 反爬虫机制（User-Agent、请求频率等）

2. **告警频率控制**：系统已实现1小时内不重复告警的机制，避免频繁通知。

3. **安全性**：
   - 生产环境应修改CORS配置，限制前端访问来源
   - 数据库密码等敏感信息应使用环境变量
   - 考虑添加API认证机制

4. **部署建议**：
   - 使用 `supervisor` 或 `systemd` 管理后端进程
   - 使用 `nginx` 反向代理前端和后端
   - 配置MySQL定期备份

## 开发计划

- [x] 基础架构搭建
- [x] 数据库设计
- [x] 后端API实现
- [x] 前端界面开发
- [ ] 爬虫逻辑实现（需根据实际网站）
- [ ] 告警功能测试
- [ ] 部署文档完善

## 联系与支持

- **管理员QQ**：714085964
- **项目说明**：本项目专门为西华大学学生设计，用于监控宿舍电费使用情况
- **数据来源**：西华大学一卡通宿舍用电小程序（https://ecard.xhu.edu.cn）

如有问题或建议，欢迎通过QQ联系管理员。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

---

**注意**：本项目仅用于学习和个人使用，请遵守西华大学相关规定，不得用于商业用途。
