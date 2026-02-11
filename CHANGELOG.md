# 开发日志

## [未发布] - 2026-02-11

### 数据库优化

#### 数据库模式细化
- ✅ 细化数据库模型字段注释，确保所有字段都有清晰的说明
- ✅ 更新数据库初始化SQL脚本，确保字段注释与模型一致
- ✅ 更新Pydantic schemas，确保字段注释准确
- ✅ 删除数据库中多余的表（admins, users, dorm_submissions, login_attempts, multi_dorm_requests, submission_limits）
- ✅ 数据库现在只包含3个必需的表：power_records, alert_rules, alert_logs

#### 数据库管理脚本
- ✅ 添加 `list_tables.sql` 和 `list_tables.bat` - 查看数据库所有表
- ✅ 添加 `drop_unused_tables.py` - 自动检测并删除多余表的Python脚本（推荐）
- ✅ 添加 `drop_unused_tables.sql` 和 `drop_unused_tables.bat` - SQL方式删除多余表

### 脚本优化

#### 统一启动脚本
- ✅ 创建 `start-all-complete.bat` - 一键启动所有服务的批处理脚本
- ✅ 创建 `start-all-complete.ps1` - 一键启动所有服务的PowerShell脚本（功能更强大）
- ✅ 创建 `stop-all.bat` - 一键停止所有服务的脚本
- ✅ 自动检测并停止已运行的服务
- ✅ 按顺序启动：后端 → NoneBot → NapCatQQ → 前端
- ✅ 显示服务状态和用户操作提示（如NapCatQQ登录）
- ✅ 自动检查依赖并安装
- ✅ 自动复制NapCat配置文件

#### 删除多余脚本
- ✅ 删除 `start-all.bat` - 旧的启动脚本，已被统一脚本替代
- ✅ 删除 `backend/nonebot_bot/start.bat` - 单独启动NoneBot脚本，已被统一脚本替代
- ✅ 删除 `backend/nonebot_bot/start-napcat.bat` - 单独启动NapCat脚本，已被统一脚本替代
- ✅ 删除 `backend/nonebot_bot/start-napcat-shell.bat` - NapCat Shell版本启动脚本
- ✅ 更新文档，移除对已删除脚本的引用

### 文档整理

#### 文档合并和优化
- ✅ 删除多余的文档文件，只保留核心文档（README.md, 技术栈文档.md, CHANGELOG.md）
- ✅ 将前端组件开发规范合并到技术栈文档中
- ✅ 更新所有文档，确保与最新代码一致
- ✅ 明确文档维护原则：不再生成多余的文档和测试内容，只更新现有文档

### 功能优化

- ✅ 单一宿舍监控：项目重构为仅监控配置文件中设置的宿舍号
- ✅ 告警规则优化：接收方必须从告警规则中配置，移除全局配置作为接收方的逻辑
- ✅ 监控面板优化：整合告警规则配置到监控面板，页面简洁
- ✅ 定时任务优化：从每天指定时间点改为每小时执行一次

---

## [1.0.0] - 2026-02-11

### 核心功能

- ✅ 定时爬取电费数据（每小时执行一次）
- ✅ 邮件和QQ告警功能
- ✅ 防频繁告警机制（1小时窗口）
- ✅ Web监控面板和数据可视化
- ✅ 单一宿舍监控支持

---

---

**维护者**: 管理员QQ：714085964
