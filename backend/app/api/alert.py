"""
告警管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.config import settings
from app.schemas import AlertRuleResponse, AlertRuleCreate, AlertRuleUpdate, AlertLogResponse
from app.services import AlertRuleService, AlertLogService

router = APIRouter()


@router.post("/rules", response_model=AlertRuleResponse, summary="创建告警规则")
async def create_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """创建告警规则（单一宿舍，最多一个）"""
    # 检查是否已存在规则
    existing_rules = AlertRuleService.get_all_rules(db)
    if existing_rules:
        raise HTTPException(status_code=400, detail="告警规则已存在，本项目仅支持单一宿舍监控")
    
    # 检查宿舍号是否与配置文件一致
    config_dorm = settings.CRAWLER_DORM_NUMBER
    if config_dorm and rule.dorm_number != config_dorm:
        raise HTTPException(status_code=400, detail=f"宿舍号必须与配置文件一致：{config_dorm}")
    
    try:
        return AlertRuleService.create_rule(db, rule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rules", response_model=Optional[AlertRuleResponse], summary="获取当前告警规则")
async def get_current_rule(db: Session = Depends(get_db)):
    """获取当前告警规则（单一宿舍，从配置文件读取宿舍号）"""
    config_dorm = settings.CRAWLER_DORM_NUMBER
    if not config_dorm:
        raise HTTPException(status_code=400, detail="配置文件中未设置CRAWLER_DORM_NUMBER")
    
    rule = AlertRuleService.get_rule(db, config_dorm)
    # 如果找不到规则，返回None（FastAPI会自动处理为204 No Content）
    return rule


@router.get("/rules/{dorm_number}", response_model=AlertRuleResponse, summary="获取告警规则（兼容接口）")
async def get_rule(dorm_number: str, db: Session = Depends(get_db)):
    """获取指定宿舍的告警规则（兼容接口）"""
    rule = AlertRuleService.get_rule(db, dorm_number)
    if not rule:
        raise HTTPException(status_code=404, detail="未找到告警规则")
    return rule


@router.put("/rules", response_model=AlertRuleResponse, summary="更新当前告警规则")
async def update_current_rule(
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """更新当前告警规则（单一宿舍，从配置文件读取宿舍号）"""
    config_dorm = settings.CRAWLER_DORM_NUMBER
    if not config_dorm:
        raise HTTPException(status_code=400, detail="配置文件中未设置CRAWLER_DORM_NUMBER")
    
    try:
        rule = AlertRuleService.update_rule(db, config_dorm, rule_update)
        if not rule:
            raise HTTPException(status_code=404, detail="未找到告警规则，请先创建")
        return rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rules/{dorm_number}", response_model=AlertRuleResponse, summary="更新告警规则（兼容接口）")
async def update_rule(
    dorm_number: str,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """更新告警规则（兼容接口）"""
    try:
        rule = AlertRuleService.update_rule(db, dorm_number, rule_update)
        if not rule:
            raise HTTPException(status_code=404, detail="未找到告警规则")
        return rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rules", summary="删除当前告警规则")
async def delete_current_rule(db: Session = Depends(get_db)):
    """删除当前告警规则（单一宿舍，从配置文件读取宿舍号）"""
    config_dorm = settings.CRAWLER_DORM_NUMBER
    if not config_dorm:
        raise HTTPException(status_code=400, detail="配置文件中未设置CRAWLER_DORM_NUMBER")
    
    success = AlertRuleService.delete_rule(db, config_dorm)
    if not success:
        raise HTTPException(status_code=404, detail="未找到告警规则")
    return {"message": "删除成功"}


@router.delete("/rules/{dorm_number}", summary="删除告警规则（兼容接口）")
async def delete_rule(dorm_number: str, db: Session = Depends(get_db)):
    """删除告警规则（兼容接口）"""
    success = AlertRuleService.delete_rule(db, dorm_number)
    if not success:
        raise HTTPException(status_code=404, detail="未找到告警规则")
    return {"message": "删除成功"}


@router.get("/logs", response_model=List[AlertLogResponse], summary="获取告警日志")
async def get_logs(
    dorm_number: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取告警日志"""
    return AlertLogService.get_logs(db, dorm_number, limit)
