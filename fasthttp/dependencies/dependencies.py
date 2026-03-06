from collections.abc import Callable
from typing import Annotated, Any, Literal

from annotated_doc import Doc


class Dependency:
    def __init__(
        self,
        func: Annotated[
            Callable,
            Doc("Async function that modifies request config"),
        ],
        use_cache: Annotated[
            bool,
            Doc(
                """
                If True, cache dependency result for the request duration.
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
    ) -> None:
        self.func = func
        self.use_cache = use_cache
        self.scope = scope
        self.__name__ = func.__name__

    async def __call__(self, route: Any, config: dict) -> dict:
        return await self.func(route, config)


def Depends(  # noqa: N802
    func: Annotated[
        Callable,
        Doc("Dependency async function that modifies request config"),
    ],
    use_cache: Annotated[
        bool,
        Doc(
            """
            If True, the dependency result is cached for the duration
            of the request. Useful for expensive computations.
            Default: True
            """
        ),
    ] = True,
    scope: Annotated[
        Literal["function", "request"] | None,
        Doc(
            """
            When to execute the dependency:
            - "function": execute before the request (default)
            - "request": execute around the entire request/response cycle

            Currently only "function" is supported.
            """
        ),
    ] = "function",
) -> Dependency:
    return Dependency(func, use_cache=use_cache, scope=scope)
