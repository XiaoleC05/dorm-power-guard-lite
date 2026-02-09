from fastapi import APIRouter
from app.api import power, alert, system

router = APIRouter()

router.include_router(power.router, prefix="/power", tags=["电费记录"])
router.include_router(alert.router, prefix="/alert", tags=["告警管理"])
router.include_router(system.router, prefix="/system", tags=["系统管理"])
