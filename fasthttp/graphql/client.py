from typing import Annotated

import httpx
from annotated_doc import Doc

from .types import GraphQLRequest, GraphQLResponse


class _GraphQLClient:
    """
    Internal GraphQL client for executing queries and mutations.
    """

    def __init__(
        self,
        url: Annotated[
            str,
            Doc(
                """
                GraphQL endpoint URL.
                """
            ),
        ],
        headers: Annotated[
            dict[str, str] | None,
            Doc(
                """
                Additional headers for GraphQL requests.
                """
            ),
        ] = None,
        timeout: Annotated[
            float | None,
            Doc(
                """
                Request timeout in seconds.
                """
            ),
        ] = 30.0,
    ) -> None:
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    def _prepare_headers(
        self,
        additional_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        headers = dict(self.headers)
        headers.setdefault("Content-Type", "application/json")

        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def query(
        self,
        query: Annotated[
            str,
            Doc(
                """
                GraphQL query string.
                """
            ),
        ],
        variables: Annotated[
            dict | None,
            Doc(
                """
                Query variables.
                """
            ),
        ] = None,
        operation_name: Annotated[
            str | None,
            Doc(
                """
                Operation name.
                """
            ),
        ] = None,
        headers: Annotated[
            dict[str, str] | None,
            Doc(
                """
                Additional headers for this request.
                """
            ),
        ] = None,
    ) -> GraphQLResponse:
        """
        Execute a GraphQL query.
        """
        request = GraphQLRequest(
            query=query,
            variables=variables,
            operation_name=operation_name,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.url,
                json=request.to_dict(),
                headers=self._prepare_headers(headers),
                timeout=self.timeout,
            )

        # Parse response
        try:
            data = response.json()
        except Exception:
            data = {}

        return GraphQLResponse(
            data=data.get("data"),
            errors=data.get("errors"),
            extensions=data.get("extensions"),
        )

    async def mutation(
        self,
        mutation: Annotated[
            str,
            Doc(
                """
                GraphQL mutation string.
                """
            ),
        ],
        variables: Annotated[
            dict | None,
            Doc(
                """
                Mutation variables.
                """
            ),
        ] = None,
        operation_name: Annotated[
            str | None,
            Doc(
                """
                Operation name.
                """
            ),
        ] = None,
        headers: Annotated[
            dict[str, str] | None,
            Doc(
                """
                Additional headers for this request.
                """
            ),
        ] = None,
    ) -> GraphQLResponse:
        """
        Execute a GraphQL mutation.
        """
        return await self.query(
            query=mutation,
            variables=variables,
            operation_name=operation_name,
            headers=headers,
        )


def create_graphql_client(
    url: Annotated[
        str,
        Doc(
            """
            GraphQL endpoint URL.
            """
        ),
    ],
    headers: Annotated[
        dict[str, str] | None,
        Doc(
            """
            Additional headers for GraphQL requests.
            """
        ),
    ] = None,
    timeout: Annotated[
        float | None,
        Doc(
            """
            Request timeout in seconds.
            """
        ),
    ] = 30.0,
) -> _GraphQLClient:
    """
    Create a GraphQL client instance.
    """
    return _GraphQLClient(url=url, headers=headers, timeout=timeout)
