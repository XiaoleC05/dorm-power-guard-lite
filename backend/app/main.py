"""
西华大学宿舍电费监控系统 - 主应用入口

本项目针对西华大学一卡通宿舍用电小程序，用于监控宿舍电费使用情况。
管理员QQ：714085964
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.scheduler import init_scheduler, shutdown_scheduler
from app.database import SessionLocal
from app.services import CrawlerService
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动，开始执行初始数据抓取...")
    db = SessionLocal()
    try:
        success = CrawlerService.crawl_and_save(db)
        if success:
            logger.info("启动时数据抓取成功")
        else:
            logger.warning("启动时数据抓取失败，将在定时任务中重试")
    except Exception as e:
        logger.error(f"启动时数据抓取异常：{e}")
    finally:
        db.close()
    
    # 初始化定时任务调度器
    init_scheduler()
    
    yield
    
    # 关闭时执行
    shutdown_scheduler()
    logger.info("应用关闭")


app = FastAPI(
    title="西华大学宿舍电费监控系统",
    description="针对西华大学一卡通宿舍用电小程序的电费监控和告警系统。管理员QQ：714085964",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置为具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "西华大学宿舍电费监控系统 API",
        "version": "1.0.0",
        "description": "针对西华大学一卡通宿舍用电小程序的电费监控系统",
        "admin_qq": "714085964"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
