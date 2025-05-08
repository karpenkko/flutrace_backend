from sqlalchemy import Column, Integer, String, JSON, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

project_users = Table(
    "project_users",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    projects = relationship("Project", secondary=project_users, back_populates="users")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True) 
    name = Column(String, nullable=False)
    users = relationship("User", secondary=project_users, back_populates="projects")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    level = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    token = Column(String, nullable=False)
    environment = Column(String, nullable=True)

    device = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)
    custom = Column(JSON, nullable=True)
