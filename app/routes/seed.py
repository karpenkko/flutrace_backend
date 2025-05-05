from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models import Log
from app.deps import get_db

router = APIRouter(tags=["Dev"], prefix="/dev")


@router.post("/logs/seed", status_code=201)
async def seed_logs(db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta
    from app.schemas import LogCreate  # або звідки у тебе ця модель
    from app.models import Log

    now = datetime.utcnow()
    today = now.replace(hour=12, minute=0)
    yesterday = today - timedelta(days=1)

    raw_logs = [
        {
            "message": "User signed in",
            "level": "info",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "android", "model": "Pixel 5", "version": 30, "manufacturer": "Google"},
            "error": {"name": None, "code": None},
            "custom": {"appVersion": "1.0.0", "userId": "xyz-123", "country": "UA"}
        },
        {
            "message": "Invalid login",
            "level": "error",
            "timestamp": yesterday,
            "token": "1234-abc",
            "environment": "production",
            "device": {"platform": "ios", "model": "iPhone 14", "version": 16, "manufacturer": "Apple"},
            "error": {"name": "LoginException", "code": "401"},
            "custom": {"appVersion": "1.0.1", "username": "test_user"}
        },
        {
            "message": "Missing auth token",
            "level": "error",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "production",
            "device": {"platform": "web", "model": "Chrome", "version": 120, "manufacturer": "Google"},
            "error": {"name": "AuthError", "code": "401"},
            "custom": {"appVersion": "1.0.2", "page": "login"}
        },
        {
            "message": "Crash on profile screen",
            "level": "critical",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "android", "model": "Pixel 7", "version": 34, "manufacturer": "Google"},
            "error": {"name": "NullPointerException", "code": "E500"},
            "custom": {"appVersion": "1.0.3", "userAction": "openProfile"}
        },
        {
            "message": "Permission denied",
            "level": "warning",
            "timestamp": yesterday,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "android", "model": "Pixel 6", "version": 33, "manufacturer": "Google"},
            "error": {"name": "SecurityException", "code": "E403"},
            "custom": {"appVersion": "1.0.1", "feature": "Camera Access"}
        },
        {
            "message": "Payment processed",
            "level": "info",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "production",
            "device": {"platform": "ios", "model": "iPhone 13", "version": 16, "manufacturer": "Apple"},
            "error": {"name": None, "code": None},
            "custom": {"appVersion": "1.0.4", "paymentId": "pay-abc123"}
        },
        {
            "message": "Server timeout",
            "level": "error",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "production",
            "device": {"platform": "android", "model": "Samsung S21", "version": 31, "manufacturer": "Samsung"},
            "error": {"name": "TimeoutException", "code": "504"},
            "custom": {"appVersion": "1.0.4", "request": "/api/data"}
        },
        {
            "message": "Unexpected null value",
            "level": "critical",
            "timestamp": yesterday,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "ios", "model": "iPhone 12", "version": 15, "manufacturer": "Apple"},
            "error": {"name": "NullValueError", "code": "E000"},
            "custom": {"appVersion": "1.0.2", "field": "username"}
        },
        {
            "message": "User logged out",
            "level": "info",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "web", "model": "Firefox", "version": 112, "manufacturer": "Mozilla"},
            "error": {"name": None, "code": None},
            "custom": {"appVersion": "1.0.0", "userId": "xyz-789"}
        },
        {
            "message": "File upload failed",
            "level": "error",
            "timestamp": today,
            "token": "1234-abc",
            "environment": "staging",
            "device": {"platform": "android", "model": "OnePlus 9", "version": 33, "manufacturer": "OnePlus"},
            "error": {"name": "UploadError", "code": "E413"},
            "custom": {"appVersion": "1.0.5", "fileSize": "8MB"}
        },
    ]

    logs_to_create = [Log(**LogCreate(**log).model_dump()) for log in raw_logs]
    db.add_all(logs_to_create)
    await db.commit()

    return {"message": f"Seeded {len(logs_to_create)} logs successfully."}
