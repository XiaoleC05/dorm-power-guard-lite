# 快速开始指南

## 5分钟快速体验

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd dorm-power-guard-lite
```

### 2. 后端快速启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（Windows使用 python -m venv venv）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制示例文件）
cp .env.example .env

# 编辑 .env 文件，至少配置数据库连接
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=dorm_power_guard

# 创建数据库（需要先启动MySQL）
mysql -u root -p -e "CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 初始化数据库表
python -c "from app.database import init_db; init_db()"

# 启动后端（开发模式）
python run.py
```

后端将在 `http://localhost:8000` 启动，访问 `http://localhost:8000/docs` 查看API文档。

### 3. 前端快速启动

```bash
# 新开一个终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动。

### 4. 测试API（可选）

使用curl测试：

```bash
# 创建告警规则
curl -X POST "http://localhost:8000/api/alert/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "dorm_number": "101",
    "threshold": 20.0,
    "enabled": true,
    "email_enabled": false,
    "qq_enabled": false
  }'

# 手动触发爬虫（需要先实现爬虫逻辑）
curl -X POST "http://localhost:8000/api/system/crawl"

# 获取最新记录
curl "http://localhost:8000/api/power/records/101/latest"
```

## 重要提示

### ⚠️ 必须完成的任务

1. **实现爬虫逻辑**：
   - 编辑 `backend/app/crawler.py`
   - 实现 `login()` 方法：根据实际网站实现登录逻辑
   - 实现 `fetch_power_data()` 方法：抓取电费数据并返回字典格式

2. **配置爬虫参数**：
   - 在 `.env` 中配置 `CRAWLER_BASE_URL`、`CRAWLER_USERNAME`、`CRAWLER_PASSWORD`、`CRAWLER_DORM_NUMBER`

3. **配置告警（可选）**：
   - 邮件告警：配置SMTP相关参数
   - QQ告警：配置QQ机器人API地址

### 📝 爬虫实现示例

```python
# backend/app/crawler.py 中的 fetch_power_data 方法示例

def fetch_power_data(self) -> Optional[Dict]:
    """抓取电费数据"""
    if not self.login():
        return None
    
    try:
        # 访问电费查询页面
        response = self.session.get(f"{self.base_url}/power/query")
        response.raise_for_status()
        
        # 解析HTML（示例）
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 提取数据（需要根据实际HTML结构调整）
        balance_element = soup.find('span', class_='balance')
        balance = float(balance_element.text.replace('元', '').strip())
        
        power_element = soup.find('span', class_='power')
        power_consumption = float(power_element.text.replace('度', '').strip()) if power_element else None
        
        return {
            'dorm_number': self.dorm_number,
            'balance': balance,
            'power_consumption': power_consumption
        }
    except Exception as e:
        logger.error(f"抓取失败：{e}")
        return None
```

### 🔧 常见问题

**Q: 数据库连接失败？**
A: 检查MySQL服务是否启动，用户名密码是否正确，数据库是否已创建。

**Q: 前端无法连接后端？**
A: 检查后端是否在8000端口运行，前端vite.config.js中的proxy配置是否正确。

**Q: 定时任务不执行？**
A: 检查 `.env` 中的 `SCHEDULER_HOURS` 配置，查看后端日志确认调度器是否启动。

**Q: 爬虫返回None？**
A: 检查爬虫配置是否正确，登录是否成功，网站结构是否变化。

## 下一步

1. 根据实际电费查询网站实现爬虫逻辑
2. 配置告警通知（邮件或QQ）
3. 测试完整流程
4. 部署到服务器（参考 DEPLOYMENT.md）

## 获取帮助

- 查看完整文档：README.md
- 部署指南：DEPLOYMENT.md
- API文档：启动后端后访问 http://localhost:8000/docs
