import ipaddress
import re
import socket
from typing import Union

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


class PrivateAddressError(ValueError):
    pass


class InvalidTargetError(ValueError):
    pass


def is_private_or_reserved(ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validate_target(value: str) -> str:
    """Validate a host/IP string, rejecting private/reserved/invalid addresses.

    Returns the sanitized value (stripped). Raises PrivateAddressError or
    InvalidTargetError on failure.
    """
    candidate = value.strip()
    if not candidate:
        raise InvalidTargetError("ターゲットを入力してください")

    # Disallow characters that have no business in a hostname/IP, blocking
    # shell-metacharacter style injection attempts before they reach subprocess.
    if not re.fullmatch(r"[A-Za-z0-9.:\-]+", candidate):
        raise InvalidTargetError("使用できない文字が含まれています")

    try:
        ip = ipaddress.ip_address(candidate)
    except ValueError:
        ip = None

    if ip is not None:
        if is_private_or_reserved(ip):
            raise PrivateAddressError("プライベート/予約済みIPアドレスは許可されていません")
        return candidate

    if not _HOSTNAME_RE.match(candidate):
        raise InvalidTargetError("IPアドレスまたはホスト名の形式が不正です")

    # Resolve hostname and ensure none of the resolved addresses are private.
    try:
        infos = socket.getaddrinfo(candidate, None)
    except socket.gaierror:
        raise InvalidTargetError("ホスト名を解決できません")

    resolved_ips = {info[4][0] for info in infos}
    for resolved in resolved_ips:
        addr = ipaddress.ip_address(resolved.split("%")[0])
        if is_private_or_reserved(addr):
            raise PrivateAddressError("プライベート/予約済みIPアドレスに解決されるホスト名は許可されていません")

    return candidate
