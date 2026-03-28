import asyncio
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class CLIResponse:
    status: int
    headers: dict[str, str]
    text: str
    json_data: dict[str, Any] | list[Any] | None
    elapsed_ms: float


class CLIClient:
    def __init__(
        self,
        timeout: float = 30.0,
        proxy: str | None = None,
    ) -> None:
        self.timeout = timeout
        self.proxy = proxy

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: str | None = None,
    ) -> CLIResponse:
        import time

        start = time.perf_counter()

        timeout = httpx.Timeout(self.timeout)

        async with httpx.AsyncClient(proxy=self.proxy) as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                content=data,
                timeout=timeout,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000

        json_data: dict[str, Any] | list[Any] | None = None
        if resp.headers.get("content-type", "").startswith("application/json"):
            json_data = resp.json()

        return CLIResponse(
            status=resp.status_code,
            headers=dict(resp.headers),
            text=resp.text,
            json_data=json_data,
            elapsed_ms=elapsed_ms,
        )


def run_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    json_data: dict[str, Any] | None = None,
    data: str | None = None,
    timeout: float = 30.0,
    proxy: str | None = None,
) -> CLIResponse:
    client = CLIClient(timeout=timeout, proxy=proxy)
    return asyncio.run(
        client.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            data=data,
        )
    )
