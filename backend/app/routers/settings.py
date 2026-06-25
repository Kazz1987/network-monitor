from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MonitorSettingResponse, MonitorSettingUpdate
from app.services.scheduler import get_or_create_settings, reschedule

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=MonitorSettingResponse)
def get_settings_endpoint(db: Session = Depends(get_db)) -> MonitorSettingResponse:
    setting = get_or_create_settings(db)
    return setting


@router.put("", response_model=MonitorSettingResponse)
def update_settings_endpoint(
    payload: MonitorSettingUpdate, db: Session = Depends(get_db)
) -> MonitorSettingResponse:
    setting = get_or_create_settings(db)
    setting.interval_seconds = payload.interval_seconds
    db.commit()
    db.refresh(setting)
    reschedule(setting.interval_seconds)
    return setting
