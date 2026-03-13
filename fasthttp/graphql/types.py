from typing import Annotated, Any

from annotated_doc import Doc


class GraphQLRequest:
    """
    GraphQL request object.

    Represents a GraphQL operation (query, mutation, or subscription)
    that can be sent to a GraphQL server.
    """

    def __init__(
        self,
        query: Annotated[
            str,
            Doc(
                """
                GraphQL query string.

                The query, mutation, or subscription operation
                to execute on the GraphQL server.
                """
            ),
        ],
        operation_name: Annotated[
            str | None,
            Doc(
                """
                Operation name for the GraphQL request.

                Required when the query contains multiple named
                operations to specify which one to execute.
                """
            ),
        ] = None,
        variables: Annotated[
            dict[str, Any] | None,
            Doc(
                """
                Variables for the GraphQL operation.

                A dictionary of variable values that will be
                substituted in the query.
                """
            ),
        ] = None,
    ) -> None:
        self.query = query
        self.operation_name = operation_name
        self.variables = variables

    def to_dict(self) -> dict[str, Any]:
        """Convert request to dictionary format for GraphQL API."""
        data: dict[str, Any] = {"query": self.query}

        if self.operation_name:
            data["operationName"] = self.operation_name

        if self.variables:
            data["variables"] = self.variables

        return data


class GraphQLResponse:
    """
    GraphQL response object.

    Represents the response from a GraphQL server,
    including data, errors, and extensions.
    """

    def __init__(
        self,
        data: Annotated[
            dict[str, Any] | None,
            Doc(
                """
                The result of the GraphQL operation.

                Contains the requested data if the operation
                was successful.
                """
            ),
        ] = None,
        errors: Annotated[
            list[dict[str, Any]] | None,
            Doc(
                """
                List of GraphQL errors.

                Contains error information if the operation
                failed or had validation errors.
                """
            ),
        ] = None,
        extensions: Annotated[
            dict[str, Any] | None,
            Doc(
                """
                Additional response extensions.

                Optional metadata from the GraphQL server.
                """
            ),
        ] = None,
    ) -> None:
        self.data = data
        self.errors = errors
        self.extensions = extensions

    @property
    def ok(self) -> bool:
        """Check if the GraphQL response has no errors."""
        return self.errors is None or len(self.errors) == 0

    @property
    def has_errors(self) -> bool:
        """Check if the GraphQL response has errors."""
        return not self.ok
