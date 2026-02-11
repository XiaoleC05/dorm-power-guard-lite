# 脚本目录说明

本目录包含项目相关的数据库脚本文件。

## 目录结构

```
scripts/
└── db/                    # 数据库相关脚本
    ├── init_db.sql       # 数据库初始化SQL（必需）
    ├── drop_unused_tables.py    # 删除多余表的Python脚本（推荐）
    └── drop_unused_tables_safe.bat  # 安全删除多余表的批处理脚本（Windows，推荐）
```

## 使用方法

### 数据库初始化

**Windows:**
```bash
mysql -u root -p < backend\scripts\db\init_db.sql
```

**Linux/Mac:**
```bash
mysql -u root -p < backend/scripts/db/init_db.sql
```

### 删除多余的表

**推荐方式（使用Python脚本，更安全）：**

**Windows:**
```bash
# 使用批处理脚本（推荐，自动确认）
backend\scripts\db\drop_unused_tables_safe.bat

# 或直接运行Python脚本（需要手动确认）
python backend\scripts\db\drop_unused_tables.py
```

**Linux/Mac:**
```bash
python backend/scripts/db/drop_unused_tables.py
```

**注意：**
- 当前代码中定义的表：`power_records`、`alert_rules`、`alert_logs`
- 其他表将被视为多余表并可能被删除
- 删除操作不可逆，请先备份数据库！

## 数据库迁移

数据库迁移脚本位于 `backend/migrations/` 目录：

- `add_room_id.py` - 添加 room_id 字段到 alert_rules 表
- `add_qq_receiver_id.py` - 添加 qq_receiver_id 字段到 alert_rules 表

**使用方法：**
```bash
cd backend
python migrations/add_room_id.py
python migrations/add_qq_receiver_id.py
```

## 项目启动

项目启动脚本位于项目根目录：

- `start-all-complete.bat` - Windows完整启动脚本（推荐）
- `start-all-complete.ps1` - PowerShell完整启动脚本
- `stop-all.bat` - 停止所有服务脚本

**使用方法：**
```bash
# 启动所有服务（后端、前端、NoneBot、NapCat）
start-all-complete.bat

# 停止所有服务
stop-all.bat
```

## 注意事项

1. **路径问题**: 数据库脚本需要从项目根目录或backend目录运行
2. **环境变量**: 确保已配置`.env`文件，参考`.env.example`
3. **Python版本**: 需要Python 3.8或更高版本
4. **数据库备份**: 执行删除操作前请先备份数据库
