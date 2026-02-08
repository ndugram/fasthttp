from typing import TYPE_CHECKING, Annotated

from annotated_doc import Doc

if TYPE_CHECKING:
    from .response import Response
    from .routing import Route
    from .types import RequestsOptinal


class BaseMiddleware:
    """
    Base class for middleware in FastHTTP.

    Middleware allows you to hook into the request/response lifecycle
    to add custom behavior such as logging, authentication, rate limiting,
    request modification, response transformation, etc.

    Override the methods you need in your middleware class:

    - `before_request()`: Called before sending the HTTP request
    - `after_response()`: Called after receiving a successful response
    - `on_error()`: Called when an error occurs during the request

    Example:
    ```python
        from fasthttp.middleware import BaseMiddleware

        class LoggingMiddleware(BaseMiddleware):
            async def before_request(self, route, config):
                print(f"Requesting: {route.method} {route.url}")

            async def after_response(self, response, route, config):
                print(f"Response: {response.status}")

        app = FastHTTP(middleware=[LoggingMiddleware()])
    ```
    """

    async def before_request(
        self,
        route: Annotated[
            "Route",
            Doc(
                """
                The route being executed.

                Contains information about the HTTP method,
                URL, handler function, and optional request data
                such as query parameters, JSON body, or raw data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Request configuration dictionary.

                Contains optional settings for the HTTP request
                including headers, timeout, and redirect behavior.
                Modifications to this config will be applied to
                the request before it is sent.
                """
            ),
        ],
    ) -> Annotated[
        "RequestsOptinal",
        Doc(
            """
            Modified or original request configuration.

            Return the config dict (possibly modified) to apply
            changes to the request. Any changes to headers, timeout,
            or redirect settings will be used when sending the request.
            """
        ),
    ]:
        """
        Called before sending the HTTP request.

        Use this hook to:
        - Modify request headers
        - Add authentication tokens
        - Log outgoing requests
        - Validate request parameters
        - Apply rate limiting

        The config dict is mutable and changes will affect the request.
        """
        return config

    async def after_response(
        self,
        response: Annotated[
            "Response",
            Doc(
                """
                The HTTP response object.

                Contains the response status code, text content,
                headers, and methods for parsing JSON data.
                """
            ),
        ],
        route: Annotated[
            "Route",
            Doc(
                """
                The route that was executed.

                Information about the request that generated this response,
                including method, URL, handler, and request data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Request configuration that was used.

                The config dict that was applied to the request
                before it was sent. Useful for logging or debugging.
                """
            ),
        ],
    ) -> Annotated[
        "Response",
        Doc(
            """
            Modified or original response object.

            Return the response object (possibly modified) to apply
            changes. You can modify the response text, add metadata,
            or transform the response data in any way.
            """
        ),
    ]:
        """
        Called after receiving a successful response.

        Use this hook to:
        - Transform response data
        - Log response metrics
        - Cache responses
        - Validate response schema
        - Extract custom headers

        The response object is mutable and changes will affect
        how the response is processed by the handler.
        """
        return response

    async def on_error(
        self,
        error: Annotated[
            Exception,
            Doc(
                """
                The exception that occurred.

                Can be any exception raised during request execution,
                such as connection errors, timeout errors, or
                HTTP status errors.
                """
            ),
        ],
        route: Annotated[
            "Route",
            Doc(
                """
                The route that failed.

                Information about the request that encountered an error,
                including method, URL, handler, and request data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Request configuration that was used.

                The config dict that was applied to the request
                before the error occurred. Useful for error logging
                and debugging.
                """
            ),
        ],
    ) -> Annotated[
        None,
        Doc(
            """
            No return value.

            This method is called for side effects only, such as
            logging, sending notifications, or tracking metrics.
            """
        ),
    ]:
        """
        Called when an error occurs during the request.

        Use this hook to:
        - Log errors with custom formatting
        - Send error notifications
        - Implement retry logic
        - Track error metrics

        Note: This method cannot prevent the error from being logged
        by the client. It is purely for additional error handling.
        """


class MiddlewareManager:
    """
    Manages execution of middleware chain.

    This class is used internally by FastHTTP to execute middleware
    in the order they were registered.
    """

    def __init__(
        self,
        middlewares: Annotated[
            list["BaseMiddleware"] | None,
            Doc(
                """
                List of middleware instances to execute.

                Middleware will be executed in the order they
                appear in this list. Each middleware hook
                (before_request, after_response, on_error)
                will be called for all middleware in sequence.
                """
            ),
        ] = None,
    ) -> Annotated[
        None,
        Doc(
            """
            No return value.

            Initializes the middleware manager with the provided
            middleware list or an empty list if None.
            """
        ),
    ]:
        self.middlewares = middlewares or []

    async def process_before_request(
        self,
        route: Annotated[
            "Route",
            Doc(
                """
                The route being executed.

                Contains information about the HTTP request that
                is about to be sent, including method, URL,
                handler, and request data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Initial request configuration.

                The config dict that will be passed through all
                middleware before_request hooks. Each middleware
                can modify this config.
                """
            ),
        ],
    ) -> Annotated[
        "RequestsOptinal",
        Doc(
            """
            Final request configuration after middleware processing.

            Returns the config dict after all middleware
            before_request hooks have been executed.
            Modifications from middleware are applied.
            """
        ),
    ]:
        """
        Execute all before_request middleware hooks.

        This method iterates through all registered middleware
        and calls their before_request method in order.
        Each middleware can modify the config dict.
        """
        current_config = config
        for middleware in self.middlewares:
            current_config = await middleware.before_request(route, current_config)
        return current_config

    async def process_after_response(
        self,
        response: Annotated[
            "Response",
            Doc(
                """
                The HTTP response object.

                Contains the response that was received from
                the server, including status, text, and headers.
                """
            ),
        ],
        route: Annotated[
            "Route",
            Doc(
                """
                The route that was executed.

                Information about the request that generated
                this response, including method, URL,
                handler, and request data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Request configuration that was used.

                The config dict that was applied to the request
                before it was sent.
                """
            ),
        ],
    ) -> Annotated[
        "Response",
        Doc(
            """
            Final response object after middleware processing.

            Returns the response after all middleware
            after_response hooks have been executed.
            Modifications from middleware are applied.
            """
        ),
    ]:
        """
        Execute all after_response middleware hooks.

        This method iterates through all registered middleware
        and calls their after_response method in order.
        Each middleware can modify the response object.
        """
        current_response = response
        for middleware in self.middlewares:
            current_response = await middleware.after_response(
                current_response, route, config
            )
        return current_response

    async def process_on_error(
        self,
        error: Annotated[
            Exception,
            Doc(
                """
                The exception that occurred.

                The error that was raised during request execution.
                """
            ),
        ],
        route: Annotated[
            "Route",
            Doc(
                """
                The route that failed.

                Information about the request that encountered
                an error, including method, URL, handler,
                and request data.
                """
            ),
        ],
        config: Annotated[
            "RequestsOptinal",
            Doc(
                """
                Request configuration that was used.

                The config dict that was applied to the request
                before the error occurred.
                """
            ),
        ],
    ) -> Annotated[
        None,
        Doc(
            """
            No return value.

            This method is called for side effects only,
            such as error logging or notifications.
            """
        ),
    ]:
        """
        Execute all on_error middleware hooks.

        This method iterates through all registered middleware
        and calls their on_error method in order.
        Each middleware can handle the error as needed.
        """
        for middleware in self.middlewares:
            await middleware.on_error(error, route, config)
