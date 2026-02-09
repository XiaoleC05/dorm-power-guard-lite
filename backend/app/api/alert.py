"""
告警管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import AlertRuleResponse, AlertRuleCreate, AlertRuleUpdate, AlertLogResponse
from app.services import AlertRuleService, AlertLogService

router = APIRouter()


@router.post("/rules", response_model=AlertRuleResponse, summary="创建告警规则")
async def create_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """创建告警规则"""
    # 检查是否已存在
    existing = AlertRuleService.get_rule(db, rule.dorm_number)
    if existing:
        raise HTTPException(status_code=400, detail="该宿舍的告警规则已存在")
    return AlertRuleService.create_rule(db, rule)


@router.get("/rules", response_model=List[AlertRuleResponse], summary="获取所有告警规则")
async def get_all_rules(db: Session = Depends(get_db)):
    """获取所有告警规则"""
    return AlertRuleService.get_all_rules(db)


@router.get("/rules/{dorm_number}", response_model=AlertRuleResponse, summary="获取告警规则")
async def get_rule(dorm_number: str, db: Session = Depends(get_db)):
    """获取指定宿舍的告警规则"""
    rule = AlertRuleService.get_rule(db, dorm_number)
    if not rule:
        raise HTTPException(status_code=404, detail="未找到告警规则")
    return rule


@router.put("/rules/{dorm_number}", response_model=AlertRuleResponse, summary="更新告警规则")
async def update_rule(
    dorm_number: str,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """更新告警规则"""
    rule = AlertRuleService.update_rule(db, dorm_number, rule_update)
    if not rule:
        raise HTTPException(status_code=404, detail="未找到告警规则")
    return rule


@router.delete("/rules/{dorm_number}", summary="删除告警规则")
async def delete_rule(dorm_number: str, db: Session = Depends(get_db)):
    """删除告警规则"""
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
