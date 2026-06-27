from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Host, PortMonitor
from app.schemas import PortMonitorCreate, PortMonitorResponse

router = APIRouter(prefix="/api/hosts", tags=["ports"])


@router.get("/{host_id}/ports", response_model=list[PortMonitorResponse])
def list_ports(host_id: int, db: Session = Depends(get_db)) -> list[PortMonitorResponse]:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")
    return db.query(PortMonitor).filter(PortMonitor.host_id == host_id).order_by(PortMonitor.port.asc()).all()


@router.post("/{host_id}/ports", response_model=PortMonitorResponse, status_code=status.HTTP_201_CREATED)
def create_port(host_id: int, payload: PortMonitorCreate, db: Session = Depends(get_db)) -> PortMonitorResponse:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ホストが見つかりません")

    existing = db.query(PortMonitor).filter(
        PortMonitor.host_id == host_id,
        PortMonitor.port == payload.port,
    ).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このポートは既に登録されています")

    port_monitor = PortMonitor(host_id=host_id, port=payload.port, description=payload.description)
    db.add(port_monitor)
    db.commit()
    db.refresh(port_monitor)
    return port_monitor


@router.delete("/{host_id}/ports/{port_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_port(host_id: int, port_id: int, db: Session = Depends(get_db)) -> None:
    port_monitor = db.query(PortMonitor).filter(
        PortMonitor.id == port_id,
        PortMonitor.host_id == host_id,
    ).first()
    if port_monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ポートが見つかりません")
    db.delete(port_monitor)
    db.commit()
