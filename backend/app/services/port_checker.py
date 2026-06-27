import logging
import socket

logger = logging.getLogger(__name__)


def check_port(host: str, port: int, timeout: float = 3.0) -> bool:
    """Try to establish a TCP connection to host:port. Returns True if open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False
