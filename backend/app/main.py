"""
宿舍电费监控系统 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.scheduler import init_scheduler

app = FastAPI(
    title="宿舍电费监控系统",
    description="定时抓取电费数据并告警的MVP方案",
    version="1.0.0"
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

# 初始化定时任务调度器
init_scheduler()


@app.get("/")
async def root():
    return {"message": "宿舍电费监控系统 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
