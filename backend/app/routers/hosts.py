from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import rate_limiter
from app.database import get_db
from app.models import Host, PingResult, PingStatus
from app.schemas import HostCreate, HostResponse, ManualPingResponse
from app.services.monitor import ping_target

router = APIRouter(prefix="/api/hosts", tags=["hosts"])
settings = get_settings()

_create_host_limiter = rate_limiter(max_requests=10, window_seconds=60)
_manual_ping_limiter = rate_limiter(max_requests=6, window_seconds=60)


def _build_host_response(db: Session, host: Host) -> HostResponse:
    latest = (
        db.query(PingResult)
        .filter(PingResult.host_id == host.id)
        .order_by(PingResult.pinged_at.desc())
        .first()
    )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.HISTORY_RETENTION_HOURS)
    total = (
        db.query(func.count(PingResult.id))
        .filter(PingResult.host_id == host.id, PingResult.pinged_at >= cutoff)
        .scalar()
        or 0
    )
    up_count = (
        db.query(func.count(PingResult.id))
        .filter(
            PingResult.host_id == host.id,
            PingResult.pinged_at >= cutoff,
            PingResult.status == PingStatus.UP,
        )
        .scalar()
        or 0
    )
    uptime_percentage = round((up_count / total) * 100, 2) if total > 0 else None

    return HostResponse(
        id=host.id,
        name=host.name,
        ip_address=host.ip_address,
        is_active=host.is_active,
        is_default=host.is_default,
        created_at=host.created_at,
        latest_status=latest.status if latest else None,
        latest_response_time_ms=latest.response_time_ms if latest else None,
        uptime_percentage=uptime_percentage,
    )


@router.get("", response_model=list[HostResponse])
def list_hosts(db: Session = Depends(get_db)) -> list[HostResponse]:
    hosts = db.query(Host).order_by(Host.created_at.asc()).all()
    return [_build_host_response(db, host) for host in hosts]


@router.post(
    "",
    response_model=HostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_create_host_limiter)],
)
def create_host(payload: HostCreate, db: Session = Depends(get_db)) -> HostResponse:
    host = Host(name=payload.name, ip_address=payload.ip_address)
    db.add(host)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このIPアドレスは既に登録されています")
    db.refresh(host)
    return _build_host_response(db, host)


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_host(host_id: int, db: Session = Depends(get_db)) -> None:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")
    if host.is_default:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="デフォルトホストは削除できません")
    db.delete(host)
    db.commit()


@router.post(
    "/{host_id}/ping",
    response_model=ManualPingResponse,
    dependencies=[Depends(_manual_ping_limiter)],
)
def manual_ping(host_id: int, db: Session = Depends(get_db)) -> ManualPingResponse:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")

    status_result, response_time_ms = ping_target(host.ip_address)
    result = PingResult(host_id=host.id, status=status_result, response_time_ms=response_time_ms)
    db.add(result)
    db.commit()
    db.refresh(result)

    return ManualPingResponse(
        host_id=host.id,
        status=result.status,
        response_time_ms=result.response_time_ms,
        pinged_at=result.pinged_at,
    )
