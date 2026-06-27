import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.database import SessionLocal
from app.models import Host, MonitorSetting, PingStatus, PingResult, PortMonitor, SslMonitor
from app.services.monitor import ping_target
from app.services.port_checker import check_port
from app.services.ssl_checker import check_ssl
from app.services.slack_notifier import notify_down, notify_port_down, notify_ssl_expiry

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler(timezone="UTC")
_JOB_ID = "ping_all_hosts"
_SSL_JOB_ID = "check_all_ssl"
_SSL_NOTIFY_THRESHOLD_DAYS = 30


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
        now = datetime.now(timezone.utc)
        for host in hosts:
            status, response_time_ms = ping_target(host.ip_address)
            result = PingResult(
                host_id=host.id,
                status=status,
                response_time_ms=response_time_ms,
            )
            db.add(result)
            if status == PingStatus.DOWN:
                notify_down(
                    host_id=host.id,
                    host_name=host.name,
                    ip_address=host.ip_address,
                    detected_at=result.pinged_at,
                )

            ports = (
                db.query(PortMonitor)
                .filter(PortMonitor.host_id == host.id, PortMonitor.is_active.is_(True))
                .all()
            )
            for pm in ports:
                is_open = check_port(host.ip_address, pm.port)
                pm.last_status = is_open
                pm.last_checked_at = now
                if not is_open:
                    notify_port_down(
                        host_id=host.id,
                        host_name=host.name,
                        ip_address=host.ip_address,
                        port=pm.port,
                        detected_at=now,
                    )
        db.commit()
        cleanup_old_results(db)
    except Exception:  # noqa: BLE001
        logger.exception("Periodic ping job failed")
        db.rollback()
    finally:
        db.close()


def check_all_ssl() -> None:
    db = SessionLocal()
    try:
        hosts = db.query(Host).filter(Host.is_active.is_(True)).all()
        now = datetime.now(timezone.utc)
        for host in hosts:
            result = check_ssl(host.ip_address)

            record = db.query(SslMonitor).filter(SslMonitor.host_id == host.id).first()
            if record is None:
                record = SslMonitor(host_id=host.id)
                db.add(record)

            record.last_checked_at = now
            if result is None:
                record.days_until_expiry = None
                record.expires_at = None
            else:
                days_remaining, expires_at = result
                record.days_until_expiry = days_remaining
                record.expires_at = expires_at
                if days_remaining <= _SSL_NOTIFY_THRESHOLD_DAYS:
                    notify_ssl_expiry(
                        host_id=host.id,
                        host_name=host.name,
                        days_remaining=days_remaining,
                        expires_at=expires_at,
                    )
        db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("SSL check job failed")
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

    if not scheduler.get_job(_SSL_JOB_ID):
        scheduler.add_job(
            check_all_ssl,
            "cron",
            hour=9,
            minute=0,
            id=_SSL_JOB_ID,
            timezone="UTC",
        )


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
