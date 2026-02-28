"""
FastHTTP CLI - Command-line interface for FastHTTP client.

This module provides a Typer-based CLI for interacting with FastHTTP
from the command line, including sending HTTP requests, running
applications, and interactive mode.

Example:
    fasthttp get https://google.com status
    fasthttp post https://api.example.com data -j '{"key": "value"}'
    fasthttp put https://api.example.com/1 json -H "Authorization:Bearer token"
"""

from fasthttp.cli.main import app

__all__ = ("app",)
