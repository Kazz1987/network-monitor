import logging
import socket
import ssl
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def check_ssl(hostname: str, timeout: float = 10.0) -> tuple[int, datetime] | None:
    """Check SSL certificate expiry for hostname.

    Returns (days_remaining, expires_at) or None on connection/cert failure.
    IP addresses without IP SANs in the cert will return None.
    """
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=timeout) as raw_sock:
            with ctx.wrap_socket(raw_sock, server_hostname=hostname) as ssl_sock:
                cert = ssl_sock.getpeercert()
    except (OSError, ssl.SSLError, socket.timeout) as exc:
        logger.debug("SSL check failed for %s: %s", hostname, exc)
        return None

    not_after = cert.get("notAfter")
    if not_after is None:
        return None

    expires_at = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days_remaining = (expires_at - datetime.now(timezone.utc)).days
    return days_remaining, expires_at
