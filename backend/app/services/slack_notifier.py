import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# host_id -> last notification sent at (UTC)
_last_notified: dict[int, datetime] = {}
# (host_id, port) -> last notification sent at (UTC)
_last_port_notified: dict[tuple[int, int], datetime] = {}
# host_id -> last SSL notification sent at (UTC)
_last_ssl_notified: dict[int, datetime] = {}
_COOLDOWN = timedelta(hours=1)
_SSL_COOLDOWN = timedelta(hours=24)


def _should_notify(host_id: int) -> bool:
    last = _last_notified.get(host_id)
    if last is None:
        return True
    return datetime.now(timezone.utc) - last >= _COOLDOWN


def _should_notify_port(host_id: int, port: int) -> bool:
    last = _last_port_notified.get((host_id, port))
    if last is None:
        return True
    return datetime.now(timezone.utc) - last >= _COOLDOWN


def notify_down(
    host_id: int,
    host_name: str,
    ip_address: str,
    detected_at: datetime,
) -> None:
    """Send a Slack notification when a host goes DOWN, with 1-hour cooldown per host."""
    webhook_url = settings.SLACK_WEBHOOK_URL
    if not webhook_url:
        return

    if not _should_notify(host_id):
        logger.debug("Slack notification suppressed for host %s (cooldown active)", host_name)
        return

    timestamp = detected_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = {
        "text": (
            f":red_circle: *ホストダウン検知*\n"
            f"• ホスト名: `{host_name}`\n"
            f"• IPアドレス: `{ip_address}`\n"
            f"• 検知時刻: `{timestamp}`"
        )
    }

    try:
        response = httpx.post(webhook_url, json=payload, timeout=30.0)
        logger.info(
            "Slack API response for host %s: status=%s body=%r",
            host_name,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        _last_notified[host_id] = datetime.now(timezone.utc)
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Slack notification failed for host %s: status=%s body=%r",
            host_name,
            exc.response.status_code,
            exc.response.text,
        )
    except httpx.HTTPError as exc:
        logger.warning("Slack notification failed for host %s: %s", host_name, exc)
    except Exception as exc:
        logger.exception("Slack notification unexpected error for host %s", host_name)


def notify_port_down(host_id: int, host_name: str, ip_address: str, port: int, detected_at: datetime) -> None:
    """Send a Slack notification when a monitored port goes DOWN, with 1-hour cooldown per (host, port)."""
    webhook_url = settings.SLACK_WEBHOOK_URL
    if not webhook_url:
        return

    if not _should_notify_port(host_id, port):
        logger.debug("Slack port notification suppressed for host %s port %d (cooldown active)", host_name, port)
        return

    timestamp = detected_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = {
        "text": (
            f":large_orange_circle: *ポートダウン検知*\n"
            f"• ホスト名: `{host_name}`\n"
            f"• IPアドレス: `{ip_address}`\n"
            f"• ポート: `{port}`\n"
            f"• 検知時刻: `{timestamp}`"
        )
    }

    try:
        response = httpx.post(webhook_url, json=payload, timeout=30.0)
        logger.info(
            "Slack port notification response for host %s port %d: status=%s body=%r",
            host_name,
            port,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        _last_port_notified[(host_id, port)] = datetime.now(timezone.utc)
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Slack port notification failed for host %s port %d: status=%s body=%r",
            host_name,
            port,
            exc.response.status_code,
            exc.response.text,
        )
    except httpx.HTTPError as exc:
        logger.warning("Slack port notification failed for host %s port %d: %s", host_name, port, exc)
    except Exception as exc:
        logger.exception("Slack port notification unexpected error for host %s port %d", host_name, port)


def notify_ssl_expiry(host_id: int, host_name: str, days_remaining: int, expires_at: datetime) -> None:
    """Send a Slack notification when SSL certificate expiry is within 30 days, with 24-hour cooldown per host."""
    webhook_url = settings.SLACK_WEBHOOK_URL
    if not webhook_url:
        return

    last = _last_ssl_notified.get(host_id)
    if last is not None and datetime.now(timezone.utc) - last < _SSL_COOLDOWN:
        logger.debug("Slack SSL notification suppressed for host %s (cooldown active)", host_name)
        return

    icon = ":red_circle:" if days_remaining <= 7 else ":warning:"
    urgency = "緊急" if days_remaining <= 7 else "警告"
    expiry_str = expires_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = {
        "text": (
            f"{icon} *SSL証明書期限{urgency}*\n"
            f"• ホスト名: `{host_name}`\n"
            f"• 残り日数: `{days_remaining}日`\n"
            f"• 有効期限: `{expiry_str}`"
        )
    }

    try:
        response = httpx.post(webhook_url, json=payload, timeout=30.0)
        logger.info(
            "Slack SSL notification response for host %s: status=%s body=%r",
            host_name,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        _last_ssl_notified[host_id] = datetime.now(timezone.utc)
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Slack SSL notification failed for host %s: status=%s body=%r",
            host_name,
            exc.response.status_code,
            exc.response.text,
        )
    except httpx.HTTPError as exc:
        logger.warning("Slack SSL notification failed for host %s: %s", host_name, exc)
    except Exception as exc:
        logger.exception("Slack SSL notification unexpected error for host %s", host_name)
