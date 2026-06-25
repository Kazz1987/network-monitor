import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.database import SessionLocal
from app.models import Host, MonitorSetting, PingResult
from app.services.monitor import ping_target

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler(timezone="UTC")
_JOB_ID = "ping_all_hosts"


def get_or_create_settings(db) -> MonitorSetting:
    setting = db.query(MonitorSetting).first()
    if setting is None:
        setting = MonitorSetting(interval_seconds=settings.DEFAULT_PING_INTERVAL_SECONDS)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


def ping_all_hosts() -> None:
    db = SessionLocal()
    try:
        hosts = db.query(Host).filter(Host.is_active.is_(True)).all()
        for host in hosts:
            status, response_time_ms = ping_target(host.ip_address)
            db.add(
                PingResult(
                    host_id=host.id,
                    status=status,
                    response_time_ms=response_time_ms,
                )
            )
        db.commit()
        cleanup_old_results(db)
    except Exception:  # noqa: BLE001
        logger.exception("Periodic ping job failed")
        db.rollback()
    finally:
        db.close()


def cleanup_old_results(db) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.HISTORY_RETENTION_HOURS)
    db.query(PingResult).filter(PingResult.pinged_at < cutoff).delete(synchronize_session=False)
    db.commit()


def reschedule(interval_seconds: int) -> None:
    if scheduler.get_job(_JOB_ID):
        scheduler.remove_job(_JOB_ID)
    scheduler.add_job(
        ping_all_hosts,
        "interval",
        seconds=interval_seconds,
        id=_JOB_ID,
        next_run_time=datetime.now(timezone.utc),
    )


def start_scheduler() -> None:
    db = SessionLocal()
    try:
        setting = get_or_create_settings(db)
        interval = setting.interval_seconds
    finally:
        db.close()

    if not scheduler.running:
        scheduler.start()
    reschedule(interval)


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
