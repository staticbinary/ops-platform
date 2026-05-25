from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True)
    owner = Column(String)
    status = Column(String)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)
    asset_id = Column(Integer, index=True, nullable=True)
    actor = Column(String, index=True)
    result = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))