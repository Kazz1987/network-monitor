import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PingStatus(str, enum.Enum):
    UP = "UP"
    DOWN = "DOWN"


class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    ping_results: Mapped[list["PingResult"]] = relationship(
        "PingResult", back_populates="host", cascade="all, delete-orphan"
    )
    port_monitors: Mapped[list["PortMonitor"]] = relationship(
        "PortMonitor", back_populates="host", cascade="all, delete-orphan"
    )
    ssl_monitor: Mapped[Optional["SslMonitor"]] = relationship(
        "SslMonitor", back_populates="host", cascade="all, delete-orphan", uselist=False
    )


class PingResult(Base):
    __tablename__ = "ping_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[PingStatus] = mapped_column(Enum(PingStatus), nullable=False)
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pinged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    host: Mapped["Host"] = relationship("Host", back_populates="ping_results")


class PortMonitor(Base):
    __tablename__ = "port_monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    host: Mapped["Host"] = relationship("Host", back_populates="port_monitors")


class SslMonitor(Base):
    __tablename__ = "ssl_monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    days_until_expiry: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    host: Mapped["Host"] = relationship("Host", back_populates="ssl_monitor")


class MonitorSetting(Base):
    __tablename__ = "monitor_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
