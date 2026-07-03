"""
DormGuard - 宿舍电费监控主应用入口
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import router
from app.scheduler import init_scheduler, shutdown_scheduler
from app.database import SessionLocal
from app.services import CrawlerService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def _deferred_initial_crawl():
    """延迟后台抓取，避免阻塞服务启动。"""
    await asyncio.sleep(3)
    db = SessionLocal()
    try:
        success = CrawlerService.crawl_and_save(db)
        if success:
            logger.info("后台初始数据抓取成功")
        else:
            logger.warning("后台初始数据抓取失败，将在定时任务中重试")
    except Exception as e:
        logger.error(f"后台初始数据抓取异常：{e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_scheduler()
    asyncio.create_task(_deferred_initial_crawl())
    logger.info("应用已启动，定时任务就绪")

    yield

    shutdown_scheduler()
    logger.info("应用关闭")


app = FastAPI(
    title="DormGuard",
    description="宿舍电费监控与告警系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oxelia51.com",
        "https://www.oxelia51.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，捕获所有未处理的异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    logger.error(f"请求路径: {request.url.path}")
    logger.error(f"请求方法: {request.method}")
    if settings.APP_DEBUG:
        content = {
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": request.url.path,
        }
    else:
        content = {"detail": "服务器内部错误，请稍后重试"}
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证失败: {exc}")
    body = exc.body
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8")
        except UnicodeDecodeError:
            body = None
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body},
    )


@app.get("/")
async def root():
    return {"status": "ok", "service": "oxelia-toolbox"}


@app.get("/health")
async def health():
    return {"status": "ok"}
