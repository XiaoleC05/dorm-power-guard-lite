# 小程序爬虫实现指南

## 针对 ecard.xhu.edu.cn 微信小程序的数据抓取方案

### 核心思路

微信小程序的数据通常通过HTTPS API获取，我们需要：
1. **抓包分析**：使用抓包工具分析小程序API接口
2. **获取Token**：提取认证Token
3. **调用API**：直接调用API获取电费数据

---

## 步骤1：抓包分析小程序API

### 1.1 安装抓包工具

推荐使用以下工具之一：

**Windows/Mac:**
- **Charles** (推荐) - https://www.charlesproxy.com/
- **Fiddler** - https://www.telerik.com/fiddler
- **mitmproxy** - 命令行工具

**Android:**
- **HttpCanary** - Android抓包工具
- **Packet Capture** - 无需root

### 1.2 配置抓包工具

#### Charles配置步骤：

1. **启动Charles**
2. **配置代理**：
   - Proxy → Proxy Settings → Port: 8888
   - 勾选 "Enable transparent HTTP proxying"
3. **安装证书**：
   - Help → SSL Proxying → Install Charles Root Certificate
   - 在手机上配置代理：设置 → WiFi → 高级 → 代理 → 手动
   - 代理主机：电脑IP地址
   - 代理端口：8888
   - 在手机浏览器访问 `chls.pro/ssl` 安装证书
4. **启用SSL抓包**：
   - Proxy → SSL Proxying Settings
   - 添加 `ecard.xhu.edu.cn`，端口 `443`

#### mitmproxy配置（Linux/Mac）：

```bash
# 安装
pip install mitmproxy

# 启动
mitmproxy -p 8080

# 配置手机代理指向电脑IP:8080
# 访问 http://mitm.it 安装证书
```

### 1.3 抓取小程序请求

1. **打开微信小程序**（电费查询小程序）
2. **在抓包工具中查看请求**
3. **找到电费查询相关的API请求**

关键信息需要记录：
- **API地址**：如 `https://ecard.xhu.edu.cn/api/power/query`
- **请求方法**：GET 或 POST
- **请求头**：特别是 `Authorization`、`token`、`Cookie` 等
- **请求参数**：宿舍号、用户ID等
- **响应格式**：JSON结构

---

## 步骤2：提取Token

### 2.1 从请求头提取

在抓包工具中找到包含Token的请求头：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

或者：

```
token: abc123def456...
```

### 2.2 Token有效期

- **短期Token**：可能几小时或1天过期，需要定期刷新
- **长期Token**：可能几个月有效

### 2.3 配置Token

将提取的Token配置到 `.env` 文件：

```env
CRAWLER_TOKEN=your_token_here
CRAWLER_API_BASE_URL=https://ecard.xhu.edu.cn/api
```

---

## 步骤3：分析API接口

### 3.1 常见API结构

小程序API通常遵循RESTful风格：

```
GET /api/power/query?dorm=101
POST /api/power/query
  Body: {"dorm_number": "101"}
```

### 3.2 响应格式示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "dorm_number": "101",
    "balance": 50.5,
    "power_consumption": 120.3,
    "update_time": "2024-01-01 12:00:00"
  }
}
```

### 3.3 更新爬虫代码

根据实际API调整 `backend/app/crawler.py`：

```python
# 修改 fetch_power_data 方法中的API地址和参数
api_url = f"{self.api_base_url}/power/query"  # 根据实际API调整

# 调整参数名（可能是 dorm, room, roomNumber 等）
params = {'dorm': self.dorm_number}

# 调整数据提取逻辑（根据实际响应结构）
balance = data.get('balance')  # 或 data.get('data', {}).get('balance')
```

---

## 步骤4：处理Token刷新

### 4.1 如果Token会过期

需要实现Token刷新机制：

1. **找到刷新Token的API**（通常在登录或认证相关接口）
2. **配置刷新URL**：
   ```env
   CRAWLER_TOKEN_REFRESH_URL=https://ecard.xhu.edu.cn/api/auth/refresh
   ```
3. **实现刷新逻辑**（代码已包含在 `_refresh_token` 方法中）

### 4.2 手动刷新Token

如果自动刷新失败，可以：
1. 重新抓包获取新Token
2. 更新 `.env` 文件中的 `CRAWLER_TOKEN`

---

## 步骤5：测试爬虫

### 5.1 手动测试

```bash
cd backend
source venv/bin/activate
python -c "
from app.crawler import get_crawler
crawler = get_crawler()
data = crawler.fetch_power_data()
print(data)
"
```

### 5.2 通过API测试

```bash
curl -X POST http://localhost:8000/api/system/crawl
```

### 5.3 查看日志

```bash
# 查看后端日志
tail -f /var/log/dorm-power-guard.log
# 或
sudo supervisorctl tail dorm-power-guard
```

---

## 常见问题

### Q1: 抓不到HTTPS请求？

**A:** 
- 确保已安装并信任抓包工具的证书
- 检查手机代理设置是否正确
- 某些小程序可能使用了证书绑定，需要特殊处理

### Q2: Token很快过期？

**A:**
- 实现Token自动刷新机制
- 或者使用更长期的认证方式（如Session Cookie）

### Q3: API返回401未授权？

**A:**
- Token可能已过期，需要刷新
- 检查请求头格式是否正确（Bearer token 或其他格式）
- 可能需要其他认证信息（如Cookie、签名等）

### Q4: 找不到电费查询API？

**A:**
- 尝试在小程序中执行查询操作，观察抓包工具中的请求
- 查看小程序网络请求的URL模式
- 可能API路径不是 `/api/power/query`，需要根据实际情况调整

### Q5: 如何获取长期有效的Token？

**A:**
- 分析登录流程，看是否有刷新Token的接口
- 或者使用账号密码登录获取Token（如果支持）
- 某些系统可能支持API Key方式认证

---

## 替代方案

如果无法通过API获取数据，可以考虑：

### 方案A：模拟登录网页版

如果 `ecard.xhu.edu.cn` 有网页版：
1. 分析网页登录流程
2. 使用Selenium或Playwright模拟浏览器
3. 抓取网页数据

### 方案B：OCR识别

1. 使用Selenium截图小程序页面
2. 使用OCR识别电费余额
3. 准确度较低，不推荐

### 方案C：手动输入（临时方案）

1. 提供手动输入接口
2. 定期手动更新数据
3. 仅用于测试其他功能

---

## 安全提示

1. **不要泄露Token**：Token相当于密码，不要提交到公开仓库
2. **使用环境变量**：敏感信息存储在 `.env` 文件中
3. **定期更新Token**：如果Token泄露，及时更换
4. **遵守使用条款**：确保抓取行为符合网站使用条款

---

## 下一步

1. ✅ 完成抓包分析
2. ✅ 提取Token和API信息
3. ✅ 更新爬虫代码
4. ✅ 测试数据抓取
5. ✅ 配置定时任务
6. ✅ 测试告警功能

如有问题，请查看日志或联系开发者。
