from sqlalchemy import select, func, cast, String, text, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import literal_column
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from app.models import Log, User 
from app.schemas import DashboardOut, TimePoint, FullAnalyticsOut, OSStat, DeviceStat, MessageStat, CountryStat
from app.deps import get_db
from typing import List
from app.auth.jwt import get_current_user

router = APIRouter( tags=["Report"])

@router.get("/projects/{project_token}/dashboard", response_model=DashboardOut)
async def get_dashboard(project_token: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_ago_start = today_start - timedelta(days=7)

    # Загальна кількість логів за сьогодні
    total_today_query = select(func.count()).where(
        Log.token == project_token,
        Log.timestamp >= today_start
    )

    # Кількість error та critical
    error_critical_query = select(
        func.count().filter(Log.level == 'error').label("error"),
        func.count().filter(Log.level == 'critical').label("critical")
    ).where(
        Log.token == project_token,
        Log.timestamp >= today_start
    )

    # Загальна кількість вчора і тиждень тому
    total_yesterday_query = select(func.count()).where(
        Log.token == project_token,
        Log.timestamp >= yesterday_start,
        Log.timestamp < today_start
    )

    total_week_ago_query = select(func.count()).where(
        Log.token == project_token,
        Log.timestamp >= week_ago_start,
        Log.timestamp < today_start
    )

    # Динаміка логів за останні 7 днів
    log_counts_query = select(
        func.date_trunc("day", Log.timestamp).label("date"),
        func.count().label("count")
    ).where(
        Log.token == project_token,
        Log.level.in_(["warning", "error", "critical"]),
        Log.timestamp >= week_ago_start
    ).group_by(
        text("date")
    ).order_by(text("date"))

    # Розподіл рівнів логів за сьогодні
    level_distribution_query = select(
        Log.level,
        func.count().label("count")
    ).where(
        Log.token == project_token,
        Log.timestamp >= today_start
    ).group_by(Log.level)

    # Групування за версією
    app_version_expr = cast(Log.custom["appVersion"], String).label("version")

    top_versions_query = select(
        app_version_expr,
        func.count().label("errors")
    ).where(
        Log.token == project_token,
        Log.level.in_(["warning", "error", "critical"]),
        Log.custom["appVersion"].isnot(None),
        text("logs.custom ->> 'appVersion' ~ '^[0-9]+(\\.[0-9]+)*$'")
    ).group_by(
        app_version_expr
)


    # Час останнього логу
    last_log_query = select(func.max(Log.timestamp)).where(
        Log.token == project_token
    )

    total_today = (await db.execute(total_today_query)).scalar()
    error_critical = (await db.execute(error_critical_query)).first()
    total_yesterday = (await db.execute(total_yesterday_query)).scalar()
    total_week_ago = (await db.execute(total_week_ago_query)).scalar()
    log_counts_result = (await db.execute(log_counts_query)).all()
    level_distribution_result = (await db.execute(level_distribution_query)).all()
    top_versions_result = (await db.execute(top_versions_query)).all()
    last_log = (await db.execute(last_log_query)).scalar()

    def get_percentage_change(current, past):
        if past == 0:
            return None
        return round(((current - past) / past) * 100, 2)

    return {
        "total_logs_today": total_today,
        "error_logs_today": error_critical.error,
        "critical_logs_today": error_critical.critical,
        "comparison": {
            "yesterday": get_percentage_change(total_today, total_yesterday),
            "last_week": get_percentage_change(total_today, total_week_ago),
        },
        "log_counts": [
            {"date": row.date.date().isoformat(), "count": row.count}
            for row in log_counts_result
        ],
        "level_distribution_today": [
            {"level": row.level, "count": row.count}
            for row in level_distribution_result
        ],
        "top_versions": [
            {"version": row.version, "errors": row.errors}
            for row in top_versions_result
        ],
        "last_log_timestamp": last_log,
    }

@router.get("/projects/{project_token}/analytics/logs_count", response_model=List[TimePoint])
async def get_logs_count(
    project_token: str,
    interval: str = Query("day", enum=["hour", "day", "month"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.utcnow()

    if interval == "hour":
        group_expr = func.date_trunc("hour", Log.timestamp)
        label_format = "HH24:MI"
        start_time = now - timedelta(hours=24)

    elif interval == "day":
        group_expr = func.date_trunc("day", Log.timestamp)
        label_format = "DD.MM"
        start_time = now - timedelta(days=7)

    elif interval == "month":
        group_expr = func.date_trunc("day", Log.timestamp)
        label_format = "DD.MM"
        start_time = now - timedelta(days=30)

    else:
        raise ValueError("Invalid interval")

    query = (
        select(
            func.to_char(group_expr, label_format).label("label"),
            func.count().label("count"),
            group_expr.label("timestamp")
        )
        .where(
            Log.token == project_token,
            Log.level.in_(["warning", "error", "critical"]),
            Log.timestamp >= start_time
        )
        .group_by(group_expr)
        .order_by(group_expr)
    )

    result = await db.execute(query)
    rows = result.all()

    return [TimePoint(label=row.label, count=row.count, timestamp=row.timestamp) for row in rows]


@router.get("/projects/{project_token}/analytics/summary", response_model=FullAnalyticsOut)
async def get_full_analytics(project_token: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # ос
    os_expr = cast(Log.device["platform"], String)
    os_query = (
        select(os_expr.label("os"), func.count().label("count"))
        .where(
            Log.token == project_token,
            Log.level.in_(["warning", "error", "critical"]),
            os_expr.isnot(None),
            os_expr != ""
        )
        .group_by("os")
    )

    # Пристрої
    model_expr = cast(Log.device["model"], String)
    model_query = (
        select(model_expr.label("model"), func.count().label("count"))
        .where(
            Log.token == project_token,
            Log.level.in_(["warning", "error", "critical"]),
            model_expr.isnot(None),
            model_expr != ""
        )
        .group_by("model")
        .order_by(func.count().desc())
        .limit(7)
    )

    # Повідомлення
    message_query = (
        select(Log.message.label("message"), func.count().label("count"))
        .where(
            Log.token == project_token,
            Log.level.in_(["warning", "error", "critical"]),
            Log.message.isnot(None),
            Log.message != ""
        )
        .group_by(Log.message)
        .order_by(func.count().desc())
        .limit(10)
    )

    # Помилки по країнах
    country_expr = cast(Log.custom["country"], String)
    country_query = (
        select(country_expr.label("country"), func.count().label("count"))
        .where(
            Log.token == project_token,
            Log.level.in_(["warning", "error", "critical"]),
            country_expr.isnot(None),
            country_expr != ""
        )
        .group_by("country")
        .order_by(func.count().desc())
        .limit(5)
    )

    os_rows = (await db.execute(os_query)).all()
    model_rows = (await db.execute(model_query)).all()
    message_rows = (await db.execute(message_query)).all()
    country_rows = (await db.execute(country_query)).all()

    return FullAnalyticsOut(
        os_distribution=[
            OSStat(os=row.os, count=row.count) for row in os_rows
        ],
        top_devices=[
            DeviceStat(model=row.model, count=row.count) for row in model_rows
        ],
        top_messages=[
            MessageStat(message=row.message, count=row.count) for row in message_rows
        ],
        errors_by_country=[
            CountryStat(country=row.country, count=row.count) for row in country_rows
        ]
    )

