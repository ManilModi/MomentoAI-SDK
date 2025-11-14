import os
import httpx
from typing import Optional, Dict, Any
from .exceptions import AuthenticationError
from .utils import handle_response
from . import endpoints as ep


class AsyncMomentoAIClient:
    """Asynchronous client for the Momento AI API with per-user Supabase integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_service_key: Optional[str] = None,
        supabase_bucket: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = api_key or os.getenv("MOMENTOAI_API_KEY", "public-access")
        self.api_url = (api_url or os.getenv("MOMENTOAI_API_URL") or "").rstrip("/")

        # ✅ Store per-user Supabase credentials
        self.supabase_url = supabase_url
        self.supabase_service_key = supabase_service_key
        self.supabase_bucket = supabase_bucket

        if not self.api_url:
            raise ValueError("Missing API URL. Set MOMENTOAI_API_URL or pass api_url.")

        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"x-api-key": self.api_key},
            timeout=timeout,
        )

    # --- Validation Helper ---
    def _validate_supabase(self):
        if not all([self.supabase_url, self.supabase_service_key, self.supabase_bucket]):
            raise AuthenticationError(
                "Missing Supabase credentials. "
                "Please provide supabase_url, supabase_service_key, and supabase_bucket."
            )

    # --- Health ---
    async def health(self) -> Dict[str, Any]:
        response = await self._client.get(ep.HEALTH)
        return handle_response(response)

    # --- Core ---
    async def _post_file(self, endpoint: str, file_path: str, data: Dict[str, str]) -> Dict[str, Any]:
        self._validate_supabase()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        data.update({
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        })

        files = {"file": open(file_path, "rb")}
        try:
            response = await self._client.post(endpoint, files=files, data=data)
        finally:
            files["file"].close()

        return handle_response(response)

    async def vectorize_image(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        return await self._post_file(ep.VECTORIZER, file_path, {
            "event_id": event_id,
            "business_id": business_id
        })

    async def find_face(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        return await self._post_file(ep.FIND_FACE, file_path, {
            "event_id": event_id,
            "business_id": business_id
        })

    async def search_face(self, prompt: str, event_id: str, business_id: str, top_k: int = 5) -> Dict[str, Any]:
        """Asynchronously searches for similar images using a text prompt and user's Supabase credentials."""
        
        params = {
            "prompt": prompt,
            "event_ids": [event_id],
            "business_id": business_id,
            "top_k": top_k,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }

        response = await self._client.get(ep.SEARCH_FACE, params=params)
        return handle_response(response)


    async def list_embeddings(self, event_id: str, business_id: str) -> Dict[str, Any]:
        self._validate_supabase()
        params = {
            "event_id": event_id,
            "business_id": business_id,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }
        response = await self._client.get(ep.LIST_EMBEDDINGS, params=params)
        return handle_response(response)

    async def delete_embedding(self, embedding_id: str) -> Dict[str, Any]:
        self._validate_supabase()
        params = {
            "embedding_id": embedding_id,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }
        response = await self._client.delete(ep.DELETE_EMBEDDING, params=params)
        return handle_response(response)

    # --- Lifecycle ---
    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
