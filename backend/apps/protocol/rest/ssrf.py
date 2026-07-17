"""SSRF-protection helpers for the REST / API protocol.

Private / reserved IP ranges are blocked at request time.
Domain-level allow-lists can be added later without changing the protocol code.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from common.core.config import settings

_PRIVATE_NETS = [
    ipaddress.ip_network("0.0.0.0/8"),          # "this host" (RFC 1122)
    ipaddress.ip_network("10.0.0.0/8"),          # RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),       # CGNAT (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),         # Loopback
    ipaddress.ip_network("169.254.0.0/16"),      # Link-local
    ipaddress.ip_network("172.16.0.0/12"),       # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),        # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),        # TEST-NET-1 (documentation)
    ipaddress.ip_network("192.168.0.0/16"),      # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),       # Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),     # TEST-NET-2 (documentation)
    ipaddress.ip_network("203.0.113.0/24"),      # TEST-NET-3 (documentation)
    ipaddress.ip_network("224.0.0.0/4"),         # Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # Reserved (future use)
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    ipaddress.ip_network("::1/128"),             # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),            # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),           # IPv6 link-local
]


def _is_private_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return any(addr in net for net in _PRIVATE_NETS)
    except ValueError:
        return True  # unparseable → block


def check_ssrf(url: str) -> None:
    """Raise `ValueError` if *url* resolves to a private / reserved IP.

    Skipped entirely when ``settings.API_SSRF_PROTECTION`` is False.
    When ``settings.API_SSRF_ALLOW_PRIVATE`` is True, private IPs are allowed
    (useful for internal / on-premise deployments).
    """
    if not settings.API_SSRF_PROTECTION:
        return
    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError("URL has no hostname")
    if settings.API_SSRF_ALLOW_PRIVATE:
        return
    try:
        infos = socket.getaddrinfo(parsed.hostname, None, family=socket.AF_UNSPEC)
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {parsed.hostname}")
    for family, *_rest, sockaddr in infos:
        ip_str = sockaddr[0]
        if _is_private_ip(ip_str):
            raise ValueError(
                f"SSRF blocked: {parsed.hostname} resolves to private IP {ip_str}"
            )
