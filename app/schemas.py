from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int

class UserOut(BaseModel):
    id: int
    email: EmailStr

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str

class ProjectUpdate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: str
    name: str
    users: List[str]

    class Config:
        orm_mode = True

class LogCreate(BaseModel):
    message: str
    level: str
    timestamp: datetime
    token: str
    environment: Optional[str] = None
    device: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None

class LogOut(BaseModel):
    id: int
    message: str
    level: str
    timestamp: datetime
    token: str
    environment: Optional[str] = None
    device: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class LogDetail(LogOut):
    device: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class ComparisonStats(BaseModel):
    yesterday: Optional[float]
    last_week: Optional[float]

class VersionErrorStat(BaseModel):
    version: str
    errors: int

class LogCountPoint(BaseModel):
    date: str  
    count: int

class LevelCount(BaseModel):
    level: str  
    count: int

class DashboardOut(BaseModel):
    total_logs_today: int
    error_logs_today: int
    critical_logs_today: int
    comparison: ComparisonStats
    log_counts: List[LogCountPoint]
    level_distribution_today: List[LevelCount]
    top_versions: List[VersionErrorStat]
    last_log_timestamp: Optional[datetime]


class TimePoint(BaseModel):
    label: str
    count: int
    timestamp: datetime


class OSStat(BaseModel):
    os: str
    count: int

class DeviceStat(BaseModel):
    model: str
    count: int

class MessageStat(BaseModel):
    message: str
    count: int

class CountryStat(BaseModel):
    country: str
    count: int

class FullAnalyticsOut(BaseModel):
    os_distribution: List[OSStat]
    top_devices: List[DeviceStat]
    top_messages: List[MessageStat]
    errors_by_country: List[CountryStat]
