# 运行指南

## Windows系统

### 1. 安装依赖

**方法A：使用安装脚本（推荐）**
```cmd
cd backend
install.bat
```

**方法B：手动安装**
```cmd
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. 配置环境变量

```cmd
copy .env.example .env
```

然后编辑 `.env` 文件，至少配置数据库连接：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=dorm_power_guard
```

### 3. 创建数据库

```cmd
mysql -u root -p
```

在MySQL中执行：
```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 检查导入（可选）

```cmd
python check_imports.py
```

### 5. 运行程序

```cmd
python run.py
```

如果一切正常，你会看到：
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问 `http://localhost:8000/docs` 查看API文档。

## Linux/Mac系统

### 1. 安装依赖

```bash
cd backend
chmod +x install.sh
./install.sh
```

或手动安装：
```bash
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env  # 或使用其他编辑器
```

### 3. 创建数据库

```bash
mysql -u root -p
```

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 运行程序

```bash
python3 run.py
```

## 常见错误及解决方案

### 错误1：ModuleNotFoundError

**错误信息：**
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
```cmd
pip install -r requirements.txt
```

### 错误2：数据库连接失败

**错误信息：**
```
OperationalError: (2003, "Can't connect to MySQL server")
```

**解决方案：**
1. 检查MySQL服务是否启动
2. 检查 `.env` 中的数据库配置是否正确
3. 确认数据库已创建

### 错误3：端口被占用

**错误信息：**
```
ERROR:    [Errno 48] Address already in use
```

**解决方案：**
1. 修改 `run.py` 中的端口号（如改为8001）
2. 或关闭占用8000端口的程序

### 错误4：导入错误

**错误信息：**
```
ImportError: cannot import name 'xxx' from 'app.xxx'
```

**解决方案：**
1. 运行 `python check_imports.py` 检查问题
2. 确保所有文件都在正确的位置
3. 检查Python路径是否正确

## 测试爬虫

```cmd
python test_crawler.py
```

## 查看日志

程序运行时的日志会直接输出到控制台。如果需要保存日志，可以修改 `run.py` 添加文件日志。

## 停止程序

按 `Ctrl+C` 停止程序。
