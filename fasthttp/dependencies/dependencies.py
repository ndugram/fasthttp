from __future__ import annotations

from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Annotated, Any, Generic, Literal, TypeVar

from annotated_doc import Doc
from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class Dependency(BaseModel, Generic[T]):
    """
    Encapsulates a dependency function injected into the request lifecycle.

    Created via :func:`Depends`. Called before each request to modify
    the request config (headers, params, auth tokens, etc.).

    Example:
    ```python
    async def add_auth(route, config: dict) -> dict:
        config.setdefault("headers", {})["Authorization"] = "Bearer token"
        return config

    dep = Depends(add_auth)
    ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    func: Any
    """Dependency function — receives (route, config) and returns modified config."""

    use_cache: bool = True
    """Cache the result for the request duration. Useful for expensive calls."""

    scope: Literal["function", "request"] | None = "function"
    """Execution scope — currently only "function" is supported."""

    _is_async: bool = PrivateAttr()

    def __init__(
        self,
        func: Any, # noqa: ANN401
        *,
        use_cache: bool = True,
        scope: Literal["function", "request"] | None = "function",
    ) -> None:
        super().__init__(func=func, use_cache=use_cache, scope=scope)

    def model_post_init(self, __context: object, /) -> None:
        self._is_async = iscoroutinefunction(self.func)

    @property
    def __name__(self) -> str: # pyright: ignore[reportIncompatibleVariableOverride]
        return self.func.__name__  # type: ignore[no-any-return]

    async def __call__(self, route: Any, config: dict) -> dict:  # noqa: ANN401
        if self._is_async:
            return await self.func(route, config)
        return self.func(route, config)


def Depends(  # noqa: N802
    func: Annotated[
        Callable[..., T],
        Doc("Dependency function that receives (route, config) and returns modified config."),
    ],
    *,
    use_cache: Annotated[
        bool,
        Doc(
            """
            Cache the dependency result for the request duration.
            Useful for expensive computations. Default: True
            """
        ),
    ] = True,
    scope: Annotated[
        Literal["function", "request"] | None,
        Doc(
            """
            When to execute the dependency:
            - "function": execute before the request (default)
            - "request": execute around request/response cycle

            Currently only "function" is supported.
            """
        ),
    ] = "function",
) -> Dependency[T]:
    """Declare a dependency for a route handler."""
    return Dependency(func, use_cache=use_cache, scope=scope)
