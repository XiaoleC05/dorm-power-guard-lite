# 快速配置指南 - ecard.xhu.edu.cn

## 针对西华大学电费小程序（ecard.xhu.edu.cn）的配置步骤

### 第一步：抓包获取Token（必须）

由于是微信小程序，需要通过抓包工具获取API Token。

#### 推荐工具：Charles（最简单）

1. **下载安装Charles**
   - 官网：https://www.charlesproxy.com/
   - 有14天免费试用

2. **配置Charles抓包**
   ```
   1. 启动Charles
   2. Proxy → Proxy Settings → Port: 8888
   3. Proxy → SSL Proxying Settings → 添加 ecard.xhu.edu.cn:443
   ```

3. **手机配置代理**
   ```
   设置 → WiFi → 点击当前WiFi → 代理 → 手动
   服务器：你的电脑IP地址（Charles会显示）
   端口：8888
   ```

4. **安装证书**
   - 手机浏览器访问：`chls.pro/ssl`
   - 下载并安装证书
   - iOS需要在"设置→通用→关于本机→证书信任设置"中信任证书

5. **抓取小程序请求**
   - 打开微信小程序（电费查询）
   - 在Charles中查看请求
   - 找到包含Token的请求头（通常是 `Authorization` 或 `token`）
   - 记录API地址和请求格式

### 第二步：配置环境变量

编辑 `backend/.env` 文件：

```env
# 基础配置
CRAWLER_BASE_URL=https://ecard.xhu.edu.cn
CRAWLER_API_BASE_URL=https://ecard.xhu.edu.cn/api

# Token（从抓包工具中获取）
CRAWLER_TOKEN=your_token_here

# 宿舍号
CRAWLER_DORM_NUMBER=101

# 如果Token会过期，配置刷新接口（可选）
CRAWLER_TOKEN_REFRESH_URL=https://ecard.xhu.edu.cn/api/auth/refresh
```

### 第三步：调整API接口（根据实际抓包结果）

编辑 `backend/app/crawler.py` 中的 `fetch_power_data` 方法：

```python
# 根据实际API调整以下内容：

# 1. API地址（可能是 /api/power/query 或其他）
api_url = f"{self.api_base_url}/power/query"

# 2. 请求参数名（可能是 dorm, room, roomNumber 等）
params = {'dorm': self.dorm_number}

# 3. 响应数据提取（根据实际JSON结构调整）
balance = data.get('balance')  # 或 data.get('data', {}).get('balance')
```

### 第四步：测试爬虫

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python test_crawler.py
```

如果测试成功，会显示：
```
✅ 数据抓取成功！
宿舍号: 101
余额: 50.5 元
用电量: 120.3 度
```

### 第五步：配置go-cqhttp（QQ机器人）

1. **下载go-cqhttp**
   - 地址：https://github.com/Mrs4s/go-cqhttp/releases
   - 选择对应系统版本

2. **配置go-cqhttp**
   ```yaml
   # config.yml
   account:
     uin: YOUR_QQ_NUMBER
     password: YOUR_QQ_PASSWORD
   
   servers:
     - http:
         host: 0.0.0.0
         port: 5700
   ```

3. **启动go-cqhttp**
   ```bash
   ./go-cqhttp
   ```

4. **配置后端**
   在 `backend/.env` 中添加：
   ```env
   QQ_BOT_ENABLED=true
   QQ_BOT_TYPE=go-cqhttp
   QQ_BOT_API_URL=http://localhost:5700
   QQ_BOT_GROUP_ID=123456789  # 你的QQ群号
   ```

### 常见问题

**Q: 抓不到HTTPS请求？**
- 确保已安装并信任Charles证书
- 检查手机代理设置
- 某些小程序可能使用证书绑定，需要特殊处理

**Q: Token格式是什么？**
- 可能是 `Bearer xxxxx` 格式
- 或直接是 `xxxxx` 字符串
- 查看抓包工具中的请求头确定

**Q: API地址找不到？**
- 在小程序中执行查询操作
- 观察Charles中的网络请求
- 查找包含"power"、"electric"、"fee"等关键词的请求

**Q: Token过期怎么办？**
- 重新抓包获取新Token
- 或配置Token刷新接口（如果API支持）

### 需要帮助？

1. 查看详细指南：`backend/CRAWLER_GUIDE.md`
2. 查看测试日志：运行 `python test_crawler.py` 查看详细错误信息
3. 检查后端日志：查看应用运行日志
