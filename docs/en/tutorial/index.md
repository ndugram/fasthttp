# Tutorial - User Guide

This tutorial will guide you through all the features of FastHTTP, from basic to advanced.

## Structure

The tutorial is divided into several sections:

### Getting Started
- [First Steps](first-steps.md) - Installation and basic concepts
- [HTTP Methods](http-methods.md) - GET, POST, PUT, PATCH, DELETE
- [Request Parameters](request-parameters.md) - Query, JSON, headers
- [Response Handling](response-handling.md) - Working with responses

### Core Features
- [Parallel Execution](parallel-execution.md) - Concurrent requests
- [Routers](routers.md) - Group routes with prefixes and nesting
- [Tags](tags.md) - Grouping and filtering
- [Dependencies](dependencies.md) - Request modification
- [Lifespan](lifespan.md) - Startup and shutdown

### Data Validation
- [Pydantic Validation](validation/pydantic-validation.md) - Response validation
- [Request Validation](validation/request-validation.md) - Validate before sending
- [Error Validation](validation/error-validation.md) - Handle API errors

### Configuration
- [Settings](configuration/settings.md) - Application configuration
- [Headers](configuration/headers.md) - HTTP headers
- [Timeouts](configuration/timeouts.md) - Request timeouts
- [Logging](configuration/logging.md) - Debug mode
- [Environment Variables](configuration/environment.md) - Configuration via env
- [HTTP/2](configuration/http2.md) - HTTP/2 support
- [Proxy](configuration/proxy.md) - Proxy configuration

### Advanced
- [Middleware](middleware/index.md) - Global request logic
- [Security](security/index.md) - Built-in protection
- [GraphQL](graphql/index.md) - GraphQL support
- [OpenAPI](openapi/index.md) - Swagger UI

## How to Use

Each section builds upon the previous one. We recommend reading in order if you are new to FastHTTP.

## Examples

All sections include practical code examples that you can copy and run.
