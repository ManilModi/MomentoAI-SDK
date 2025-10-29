import os
import httpx
from typing import Optional, Dict, Any
from .exceptions import AuthenticationError, APIError
from .utils import handle_response
from . import endpoints as ep


class AsyncImageLensClient:
    """Asynchronous client for the ImageLens API."""

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, timeout: int = 60):
        """
        Initialize the asynchronous ImageLens client.

        Args:
            api_key (str, optional): API key for authentication.
            api_url (str, optional): Base URL for the deployed API (e.g. Cloud Run endpoint).
            timeout (int, optional): Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("IMAGELENS_API_KEY")
        self.api_url = (api_url or os.getenv("IMAGELENS_API_URL") or "").rstrip("/")

        if not self.api_key:
            raise AuthenticationError("Missing API key. Set IMAGELENS_API_KEY or pass api_key.")
        if not self.api_url:
            raise ValueError("Missing API URL. Set IMAGELENS_API_URL or pass api_url.")

        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"x-api-key": self.api_key},
            timeout=timeout,
        )

    # -------------------------
    # Health Endpoint
    # -------------------------
    async def health(self) -> Dict[str, Any]:
        """Check API health status."""
        response = await self._client.get(ep.HEALTH)
        return handle_response(response)

    # -------------------------
    # Core Endpoints
    # -------------------------
    async def vectorize_image(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        """
        Upload and vectorize an image.

        Args:
            file_path (str): Path to the image file.
            event_id (str): Event ID.
            business_id (str): Business ID.

        Returns:
            Dict[str, Any]: API response with embedding/vector data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        files = {"file": open(file_path, "rb")}
        data = {"event_id": event_id, "business_id": business_id}

        try:
            response = await self._client.post(ep.VECTORIZER, files=files, data=data)
        finally:
            files["file"].close()

        return handle_response(response)

    async def find_face(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        """
        Detect and extract facial embeddings from an image.

        Args:
            file_path (str): Path to image.
            event_id (str): Event ID.
            business_id (str): Business ID.

        Returns:
            Dict[str, Any]: Face detection and embedding results.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        files = {"file": open(file_path, "rb")}
        data = {"event_id": event_id, "business_id": business_id}

        try:
            response = await self._client.post(ep.FIND_FACE, files=files, data=data)
        finally:
            files["file"].close()

        return handle_response(response)

    async def search_face(self, file_path: str, event_id: str, business_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search for similar faces within an event and business context.

        Args:
            file_path (str): Path to image.
            event_id (str): Event ID.
            business_id (str): Business ID.
            top_k (int, optional): Number of top matches to return.

        Returns:
            Dict[str, Any]: Search results with matching confidence scores.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        files = {"file": open(file_path, "rb")}
        data = {"event_id": event_id, "business_id": business_id, "top_k": str(top_k)}

        try:
            response = await self._client.post(ep.SEARCH_FACE, files=files, data=data)
        finally:
            files["file"].close()

        return handle_response(response)

    async def list_embeddings(self, event_id: str, business_id: str) -> Dict[str, Any]:
        """
        List all stored embeddings for a given event and business.

        Args:
            event_id (str): Event ID.
            business_id (str): Business ID.

        Returns:
            Dict[str, Any]: List of stored image embeddings.
        """
        params = {"event_id": event_id, "business_id": business_id}
        response = await self._client.get(ep.LIST_EMBEDDINGS, params=params)
        return handle_response(response)

    async def delete_embedding(self, embedding_id: str) -> Dict[str, Any]:
        """
        Delete an embedding by ID.

        Args:
            embedding_id (str): Unique embedding identifier.

        Returns:
            Dict[str, Any]: Confirmation of deletion.
        """
        response = await self._client.delete(f"{ep.DELETE_EMBEDDING}/{embedding_id}")
        return handle_response(response)

    # -------------------------
    # Lifecycle
    # -------------------------
    async def close(self):
        """Close the underlying HTTP session."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
