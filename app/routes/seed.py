from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models import Log
from app.deps import get_db

router = APIRouter(tags=["Dev"], prefix="/dev")


@router.post("/logs/seed", status_code=201)
async def seed_logs(db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta
    from app.schemas import LogCreate 
    from app.models import Log

    # now = datetime.utcnow()
    # today = now.replace(hour=12, minute=0)
    # yesterday = today - timedelta(days=1)

    # base_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    # token = "15a5af3d4f274a65ba3475a518adbb76"
    # error_info = {"name": "DatabaseTimeout", "code": "DB504"}
    # device_info = {
    #     "platform": "android",
    #     "model": "Pixel 7 Pro",
    #     "version": 34,
    #     "manufacturer": "Google",
    #     "systemVersion": "13",
    #     "name": "pixel"
    # }
    # custom_info = {
    #     "appVersion": "2.1.0",
    #     "country": "Ukraine"
    # }

    # logs = []
    # for i in range(10):
    #     log_data = LogCreate(
    #         message="Database timeout while fetching user profile",
    #         level="error",
    #         timestamp=base_time - timedelta(days=i),
    #         token=token,
    #         environment="production",
    #         device=device_info,
    #         error=error_info,
    #         custom=custom_info,
    #     )
    #     logs.append(Log(**log_data.model_dump()))

    # base_time = datetime.utcnow().replace(hour=14, minute=0, second=0, microsecond=0)
    # token = "15a5af3d4f274a65ba3475a518adbb76"
    # error_info = {"name": "AuthFailure", "code": "AUTH401"}
    # device_info = {
    #     "platform": "ios",
    #     "model": "iPhone 14 Pro",
    #     "version": 16,
    #     "manufacturer": "Apple",
    #     "systemVersion": "16.4",
    #     "name": "iPhone"
    # }
    # custom_info = {
    #     "appVersion": "2.2.0",
    #     "country": "Germany"
    # }

    # logs = []
    # for i in range(7):
    #     log_data = LogCreate(
    #         message="Authorization failed for user session",
    #         level="warning",
    #         timestamp=base_time - timedelta(days=i),
    #         token=token,
    #         environment="staging",
    #         device=device_info,
    #         error=error_info,
    #         custom=custom_info,
    #     )
    #     logs.append(Log(**log_data.model_dump()))

    base_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    token = "15a5af3d4f274a65ba3475a518adbb76"
    error_info = {"name": "DataCorruption", "code": "DC999"}
    device_info = {
        "platform": "android",
        "model": "Galaxy S23",
        "version": 33,
        "manufacturer": "Samsung"
    }
    custom_info = {
        "appVersion": "3.0.0",
        "country": "France"
    }

    logs = []
    for i in range(5):
        log_data = LogCreate(
            message="Critical: Data corruption detected during sync",
            level="critical",
            timestamp=base_time - timedelta(days=i),
            token=token,
            environment="production",
            device=device_info,
            error=error_info,
            custom=custom_info,
        )
        logs.append(Log(**log_data.model_dump()))

    db.add_all(logs)

    # raw_logs = [
    #     {
    #         "message": "User signed in",
    #         "level": "info",
    #         "timestamp": today,
    #         "token": "15a5af3d4f274a65ba3475a518adbb76",
    #         "environment": "staging",
    #         "device": {
    #             "platform": "android",
    #             "model": "Pixel 5",
    #             "version": 30,
    #             "manufacturer": "Google",
    #             "systemVersion": "11",
    #             "name": "Pixel"
    #         },
    #         "error": {"name": None, "code": None},
    #         "custom": {
    #             "appVersion": "1.0.0",
    #             "userId": "xyz-123",
    #             "country": "Ukraine"
    #         }
    #     },
    #     {
    #         "message": "Invalid login",
    #         "level": "error",
    #         "timestamp": yesterday.replace(hour=9),
    #         "token": "15a5af3d4f274a65ba3475a518adbb76",
    #         "environment": "production",
    #         "device": {
    #             "platform": "ios",
    #             "model": "iPhone 14",
    #             "version": 16,
    #             "manufacturer": "Apple",
    #             "systemVersion": "16.2",
    #             "name": "iPhone"
    #         },
    #         "error": {"name": "LoginException", "code": "401"},
    #         "custom": {
    #             "appVersion": "1.0.1",
    #             "username": "test_user",
    #             "country": "Germany"
    #         }
    #     },
    #     {
    #         "message": "Crash on profile screen",
    #         "level": "critical",
    #         "timestamp": today.replace(hour=10),
    #         "token": "15a5af3d4f274a65ba3475a518adbb76",
    #         "environment": "staging",
    #         "device": {
    #             "platform": "android",
    #             "model": "Samsung S21",
    #             "version": 31,
    #             "manufacturer": "Samsung",
    #             "systemVersion": "12",
    #             "name": "Samsung"
    #         },
    #         "error": {"name": "NullPointerException", "code": "E500"},
    #         "custom": {
    #             "appVersion": "1.0.3",
    #             "userAction": "openProfile",
    #             "country": "Poland"
    #         }
    #     },
    #     {
    #         "message": "Permission denied",
    #         "level": "warning",
    #         "timestamp": yesterday.replace(hour=14),
    #         "token": "15a5af3d4f274a65ba3475a518adbb76",
    #         "environment": "staging",
    #         "device": {
    #             "platform": "ios",
    #             "model": "iPhone 13",
    #             "version": 15,
    #             "manufacturer": "Apple",
    #             "systemVersion": "15.5",
    #             "name": "iPhone"
    #         },
    #         "error": {"name": "SecurityException", "code": "E403"},
    #         "custom": {
    #             "appVersion": "1.0.1",
    #             "feature": "Camera Access",
    #             "country": "France"
    #         }
    #     },
    #     {
    #         "message": "Server timeout",
    #         "level": "error",
    #         "timestamp": today.replace(hour=15),
    #         "token": "15a5af3d4f274a65ba3475a518adbb76",
    #         "environment": "production",
    #         "device": {
    #             "platform": "android",
    #             "model": "OnePlus 9",
    #             "version": 33,
    #             "manufacturer": "OnePlus",
    #             "systemVersion": "13",
    #             "name": "OnePlus"
    #         },
    #         "error": {"name": "TimeoutException", "code": "504"},
    #         "custom": {
    #             "appVersion": "1.0.4",
    #             "request": "/api/data",
    #             "country": "Spain"
    #         }
    #     }
    # ]

    # logs_to_create = [Log(**LogCreate(**log).model_dump()) for log in raw_logs]
    # db.add_all(logs_to_create)


    await db.commit()

    return {"message": f"Seeded {len(logs)} logs successfully."}
