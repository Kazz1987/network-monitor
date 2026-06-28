import logging
import re
import subprocess
import sys
from typing import Optional, Tuple

from app.core.config import get_settings
from app.core.security import InvalidTargetError, PrivateAddressError, validate_target
from app.models import PingStatus

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    from ping3 import ping as _ping3_ping
except ImportError:  # pragma: no cover - environment without ping3
    _ping3_ping = None

_VALID_TARGET_RE = re.compile(r"^[A-Za-z0-9.:\-]+$")


def _ping_with_ping3(target: str, timeout: float) -> Optional[float]:
    try:
        result = _ping3_ping(target, timeout=timeout, unit="ms")
    except Exception as exc:  # ping3 raises various OS-level errors
        logger.warning("ping3 failed for %s: %s", target, exc)
        return None
    if result is None or result is False:
        return None
    return float(result)


def _ping_with_subprocess(target: str, timeout: float) -> Optional[float]:
    # target is re-validated against a strict allow-list to prevent command injection.
    if not _VALID_TARGET_RE.fullmatch(target):
        return None

    count_flag, timeout_flag = ("-n", "-w") if sys.platform.startswith("win") else ("-c", "-W")
    timeout_value = str(int(timeout * 1000)) if sys.platform.startswith("win") else str(max(1, int(timeout)))

    try:
        proc = subprocess.run(
            ["ping", count_flag, "1", timeout_flag, timeout_value, target],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
            shell=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.warning("subprocess ping failed for %s: %s", target, exc)
        return None

    if proc.returncode != 0:
        return None

    match = re.search(r"time[=<]([\d.]+)\s*ms", proc.stdout, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0


def ping_target(target: str) -> Tuple[PingStatus, Optional[float]]:
    """Ping a validated target, returning (status, response_time_ms)."""
    try:
        validate_target(target)
    except (PrivateAddressError, InvalidTargetError) as exc:
        logger.error("Refusing to ping invalid/private target %s: %s", target, exc)
        return PingStatus.DOWN, None

    timeout = settings.PING_TIMEOUT_SECONDS
    response_time = None

    if _ping3_ping is not None:
        response_time = _ping_with_ping3(target, timeout)

    if response_time is None:
        response_time = _ping_with_subprocess(target, timeout)

    if response_time is None:
        return PingStatus.DOWN, None
    return PingStatus.UP, round(response_time, 2)
