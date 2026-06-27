from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Host, SslMonitor
from app.schemas import SslMonitorResponse
router = APIRouter(prefix="/api/hosts", tags=["ssl"])


@router.get("/{host_id}/ssl", response_model=SslMonitorResponse)
def get_ssl(host_id: int, db: Session = Depends(get_db)) -> SslMonitorResponse:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")

    record = db.query(SslMonitor).filter(SslMonitor.host_id == host_id).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SSL情報がまだ取得されていません")

    return record
