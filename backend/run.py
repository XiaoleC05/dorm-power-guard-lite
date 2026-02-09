"""
应用启动入口
"""
import uvicorn
import logging
from app.main import app
from app.database import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # 初始化数据库表
    init_db()
    
    # 启动应用
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
