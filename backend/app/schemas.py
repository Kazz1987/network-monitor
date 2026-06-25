import html
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import get_settings
from app.core.security import InvalidTargetError, PrivateAddressError, validate_target
from app.models import PingStatus

settings = get_settings()

_NAME_RE = re.compile(r"^[\w\s.\-]{1,100}$", re.UNICODE)


def _sanitize_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("名前を入力してください")
    if not _NAME_RE.match(value):
        raise ValueError("名前に使用できない文字が含まれています")
    return html.escape(value)


class HostCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _sanitize_name(value)

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        try:
            return validate_target(value)
        except (PrivateAddressError, InvalidTargetError) as exc:
            raise ValueError(str(exc)) from exc


class HostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ip_address: str
    is_active: bool
    is_default: bool
    created_at: datetime
    latest_status: PingStatus | None = None
    latest_response_time_ms: float | None = None
    uptime_percentage: float | None = None


class PingResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    host_id: int
    status: PingStatus
    response_time_ms: float | None
    pinged_at: datetime


class ManualPingResponse(BaseModel):
    host_id: int
    status: PingStatus
    response_time_ms: float | None
    pinged_at: datetime


class MonitorSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interval_seconds: int
    updated_at: datetime


class MonitorSettingUpdate(BaseModel):
    interval_seconds: int = Field(
        ...,
        ge=settings.MIN_PING_INTERVAL_SECONDS,
        le=settings.MAX_PING_INTERVAL_SECONDS,
    )
