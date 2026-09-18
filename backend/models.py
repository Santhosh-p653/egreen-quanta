"""
models.py — SQLAlchemy ORM Models for Authentication and Optimization Audit Logging.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="dispatcher", nullable=False)  # "admin" or "dispatcher"
    created_at = Column(DateTime, default=utc_now)

    logs = relationship("OptimizationLog", back_populates="user")


class OptimizationLog(Base):
    __tablename__ = "optimization_logs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(100), nullable=False)
    algorithm = Column(String(50), nullable=False)
    traffic_mode = Column(String(20), default="real")
    n_stops = Column(Integer, nullable=False)
    total_distance_km = Column(Float, nullable=False)
    total_time_min = Column(Float, nullable=False)
    time_saved_min = Column(Float, default=0.0)
    crossover_iteration = Column(Integer, nullable=True)
    runtime_ms = Column(Float, default=0.0)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="logs")
