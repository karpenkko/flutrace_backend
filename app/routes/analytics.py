from sqlalchemy import select, func, cast, String, text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from app.models import Log  
from app.schemas import DashboardOut
from app.deps import get_db

router = APIRouter()

@router.get("/projects/{project_token}/dashboard", response_model=DashboardOut)
async def get_dashboard(project_token: str, db: AsyncSession = Depends(get_db)):
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

    # 📊 Динаміка логів за останні 7 днів
    log_counts_query = select(
        func.date_trunc("day", Log.timestamp).label("date"),
        func.count().label("count")
    ).where(
        Log.token == project_token,
        Log.timestamp >= week_ago_start
    ).group_by(
        text("date")
    ).order_by(text("date"))

    # 📈 Розподіл рівнів логів за сьогодні
    level_distribution_query = select(
        Log.level,
        func.count().label("count")
    ).where(
        Log.token == project_token,
        Log.timestamp >= today_start
    ).group_by(Log.level)

    # 🔢 Групування за версією
    app_version_expr = cast(Log.custom["appVersion"], String).label("version")

    top_versions_query = select(
        app_version_expr,
        func.count().label("errors")
    ).where(
        Log.token == project_token,
        Log.level.in_(["error", "critical"])
    ).group_by(
        app_version_expr
    ).order_by(
        func.count().desc()
    ).limit(5)

    # 🕒 Час останнього логу
    last_log_query = select(func.max(Log.timestamp)).where(
        Log.token == project_token
    )

    # 🔄 Виконання всіх запитів
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
