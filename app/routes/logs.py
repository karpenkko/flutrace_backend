from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, cast, String, desc
from datetime import datetime
from typing import Optional, List
from app.deps import get_db
from app.models import Log
from app.schemas import LogCreate, LogOut, LogDetail
from sqlalchemy.future import select

ENVIRONMENT_MAP = {
    "prod": "production",
    "production": "production",
    "stag": "staging",
    "staging": "staging",
    "dev": "development",
    "development": "development",
}

router = APIRouter(tags=["Logs"])

@router.post("/logs", response_model=LogOut)
async def create_log(log: LogCreate, db: AsyncSession = Depends(get_db)):
    new_log = Log(**log.model_dump())
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log

@router.get("/logs", response_model=list[LogDetail])
async def get_all_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Log))
    logs = result.scalars().all()
    return logs

@router.get("/logs/{project_token}", response_model=List[LogOut])
async def get_logs_for_project(
    project_token: str,
    level: Optional[str] = None,
    environment: Optional[str] = None,
    os: Optional[str] = None,
    search: Optional[str] = None,
    before: Optional[datetime] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    query = select(Log).where(Log.token == project_token)

    if level:
        query = query.where(Log.level == level)

    if environment:
        normalized_env = ENVIRONMENT_MAP.get(environment.lower())
        if normalized_env:
            query = query.where(Log.environment == normalized_env)

    if os:
        query = query.where(cast(Log.device["platform"], String).ilike(f"%{os}%"))

    if search:
        query = query.where(or_(
            Log.message.ilike(f"%{search}%"),
            cast(Log.error["name"], String).ilike(f"%{search}%")
        ))

    if before:
        query = query.where(Log.timestamp < before)

    query = query.order_by(desc(Log.timestamp)).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/logs/{project_token}/{log_id}", response_model=LogDetail)
async def get_log_detail(project_token: str, log_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Log).where(Log.id == log_id, Log.token == project_token))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
