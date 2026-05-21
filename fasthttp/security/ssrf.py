import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

try:
    from fasthttp._core import (
        is_private_ip as _rs_is_private_ip,
        is_local_hostname as _rs_is_local_hostname,
    )
    _RUST = True
except ImportError:
    _RUST = False

PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
]

LOCAL_DOMAINS = [
    "localhost",
    "localhost.localdomain",
    "local",
    "intranet",
    "internal",
    "private",
]

LOCALHOST_NAMES = [
    "localho.st",
    "lvh.me",
    "0x7f000001",
    "127.1",
    "::1",
    "0:0:0:0:0:0:0:1",
]


class SSRFProtection:
    def __init__(self):
        self._dns_cache = {}

    async def check_url(self, url: str) -> bool:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False

        hostname_lower = hostname.lower()

        if _RUST:
            if _rs_is_local_hostname(hostname_lower):
                return False
        else:
            if hostname_lower in LOCALHOST_NAMES:
                return False
            if any(hostname_lower.endswith(domain) for domain in LOCAL_DOMAINS):
                return False
            if hostname_lower in ("127.0.0.1", "0.0.0.0", "::1", "0"):
                return False

        try:
            ip_str = await asyncio.to_thread(socket.gethostbyname, hostname)

            if _RUST:
                if _rs_is_private_ip(ip_str):
                    return False
            else:
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback or ip.is_link_local or ip.is_multicast:
                    return False
                for network in PRIVATE_RANGES:
                    if ip in network:
                        return False

        except socket.gaierror:
            return True
        except Exception:
            return False

        return True

    async def validate_request(self, url: str) -> None:
        if not await self.check_url(url):
            raise SSRFBlockedError(f"SSRF protection blocked request to: {url}")


class SSRFBlockedError(Exception):
    pass
