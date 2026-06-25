from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.models import Host, PingResult
from app.schemas import PingResultResponse

router = APIRouter(prefix="/api/hosts", tags=["metrics"])
settings = get_settings()


@router.get("/{host_id}/metrics", response_model=list[PingResultResponse])
def get_host_metrics(host_id: int, db: Session = Depends(get_db)) -> list[PingResultResponse]:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.HISTORY_RETENTION_HOURS)
    results = (
        db.query(PingResult)
        .filter(PingResult.host_id == host_id, PingResult.pinged_at >= cutoff)
        .order_by(PingResult.pinged_at.asc())
        .all()
    )
    return results
