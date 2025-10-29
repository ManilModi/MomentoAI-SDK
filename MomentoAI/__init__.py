"""
ImageLens SDK
--------------

A lightweight Python SDK for interacting with the deployed ImageLens API
(hosted on Cloud Run). Supports both synchronous and asynchronous clients.

Usage Example:
---------------

>>> from imagelens import ImageLensClient
>>> client = ImageLensClient(
...     api_key="YOUR_API_KEY",
...     api_url="https://your-cloudrun-url.a.run.app"
... )
>>> resp = client.health()
>>> print(resp)

Or use the async version:

>>> import asyncio
>>> from imagelens import AsyncImageLensClient
>>> async def main():
...     client = AsyncImageLensClient(
...         api_key="YOUR_API_KEY",
...         api_url="https://your-cloudrun-url.a.run.app"
...     )
...     print(await client.health())
...     await client.close()
>>> asyncio.run(main())
"""

from .client import ImageLensClient
from .async_client import AsyncImageLensClient
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from . import endpoints

__all__ = [
    "ImageLensClient",
    "AsyncImageLensClient",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "endpoints",
]

__version__ = "0.1.0"
