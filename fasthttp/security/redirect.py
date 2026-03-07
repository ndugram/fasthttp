import ipaddress
import socket
from urllib.parse import urlparse
from dataclasses import dataclass

PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
]


@dataclass
class RedirectConfig:
    max_hops: int = 10
    block_file_protocol: bool = True
    block_internal_ips: bool = True
    block_javascript: bool = True
    allow_http_downgrade: bool = False


class RedirectProtection:
    def __init__(
        self,
        config: RedirectConfig | None = None
    ) -> None:
        self._config = config or RedirectConfig()
        self._redirect_count = 0

    def reset(self) -> None:
        self._redirect_count = 0

    def check_redirect(
        self,
        original_url: str,
        redirect_url: str,
        original_method: str = "GET"
    ) -> tuple[bool, str | None]:
        self._redirect_count += 1

        if self._redirect_count > self._config.max_hops:
            return False, f"Too many redirects (max: {self._config.max_hops})"

        parsed = urlparse(redirect_url)
        scheme = parsed.scheme.lower()

        if self._config.block_file_protocol and scheme == "file":
            return False, "Redirect to file:// protocol is blocked"

        if self._config.block_javascript and scheme in ("javascript", "data"):
            return False, f"Redirect to {scheme}:// protocol is blocked"

        if scheme == "http" and self._config.allow_http_downgrade:
            original_parsed = urlparse(original_url)
            if original_parsed.scheme.lower() == "https":
                return False, "HTTP downgrade not allowed (HTTPS -> HTTP)"

        if self._config.block_internal_ips:
            ip_check = self._check_internal_destination(redirect_url)
            if not ip_check[0]:
                return ip_check

        return True, None

    def _check_internal_destination(
        self, url: str
    ) -> tuple[bool, str | None]:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return True, None

        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)

            if ip.is_loopback:
                return False, f"Redirect to loopback IP: {ip}"

            if ip.is_link_local:
                return False, f"Redirect to link-local IP: {ip}"

            for network in PRIVATE_RANGES:
                if ip in network:
                    return False, f"Redirect to private IP: {ip} ({network})"

        except socket.gaierror:
            pass
        except Exception as e:
            pass

        return True, None

    def should_follow_redirect(
        self, original_scheme: str, redirect_scheme: str
    ) -> tuple[bool, str | None]:
        if original_scheme == "https" and redirect_scheme == "http":
            if not self._config.allow_http_downgrade:
                return False, "HTTPS -> HTTP downgrade blocked"
        return True, None
