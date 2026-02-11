# 脚本目录说明

本目录包含项目相关的各种脚本文件，按功能分类组织。

## 目录结构

```
scripts/
├── db/                    # 数据库相关脚本
│   ├── init_db.sql       # 数据库初始化SQL
│   └── create_user.sql   # 创建数据库用户SQL
├── migrations/            # 数据库迁移脚本
│   ├── run_migration.bat              # 运行qq_receiver_id迁移（Windows）
│   └── run_migration_room_id.bat     # 运行room_id迁移（Windows）
├── start/                 # 启动脚本
│   ├── start.bat         # Windows启动脚本
│   ├── start.sh          # Linux/Mac启动脚本
│   └── start.ps1         # PowerShell启动脚本
├── install/               # 安装脚本
│   ├── install.bat       # Windows依赖安装脚本
│   ├── install.sh        # Linux/Mac依赖安装脚本
│   └── install_windows_service.ps1  # Windows服务安装脚本
├── deploy.sh              # 快速部署脚本（Linux）
├── update.sh              # 代码更新脚本（Linux）
└── README.md              # 本说明文件
```

## 使用方法

### 数据库初始化

**Windows:**
```bash
mysql -u root -p < scripts/db/init_db.sql
mysql -u root -p < scripts/db/create_user.sql
```

**Linux/Mac:**
```bash
mysql -u root -p < scripts/db/init_db.sql
mysql -u root -p < scripts/db/create_user.sql
```

### 数据库迁移

**Windows:**
```bash
# 添加qq_receiver_id字段
scripts\migrations\run_migration.bat

# 添加room_id字段
scripts\migrations\run_migration_room_id.bat
```

**Linux/Mac:**
```bash
# 直接运行Python迁移脚本
python migrations/add_qq_receiver_id.py
python migrations/add_room_id.py
```

### 启动服务

**Windows:**
```bash
# 使用批处理脚本
scripts\start\start.bat

# 或使用PowerShell脚本
scripts\start\start.ps1
```

**Linux/Mac:**
```bash
scripts/start/start.sh
```

### 安装依赖

**Windows:**
```bash
scripts\install\install.bat
```

**Linux/Mac:**
```bash
scripts/install/install.sh
```

### 安装Windows服务

```powershell
# 需要以管理员身份运行
scripts\install\install_windows_service.ps1
```

### 快速部署（Linux）

```bash
# 需要root权限
sudo scripts/deploy.sh
```

### 更新代码（Linux）

```bash
scripts/update.sh
```

## 注意事项

1. **路径问题**: 所有脚本都设计为从`backend`目录运行，脚本内部会自动切换到正确的目录
2. **权限问题**: 某些脚本需要管理员/root权限，请根据提示操作
3. **环境变量**: 确保已配置`.env`文件，参考`.env.example`
4. **Python版本**: 需要Python 3.8或更高版本
