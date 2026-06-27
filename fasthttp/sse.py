from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SSEEvent:
    event: str = "message"
    data: str = ""
    id: str | None = None
    retry: int | None = None
    _raw: list[str] = field(default_factory=list, repr=False)
