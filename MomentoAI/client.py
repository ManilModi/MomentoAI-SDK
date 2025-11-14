import os
import httpx
from typing import Optional, Dict, Any
from .exceptions import AuthenticationError
from .utils import handle_response
from . import endpoints as ep


class MomentoAIClient:
    """Synchronous client for the Momento AI API with per-user Supabase integration."""

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

        self._client = httpx.Client(
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
    def health(self) -> Dict[str, Any]:
        response = self._client.get(ep.HEALTH)
        return handle_response(response)

    # --- Core ---
    def _post_file(self, endpoint: str, file_path: str, data: Dict[str, str]) -> Dict[str, Any]:
        """Upload a file and include Supabase credentials for the request."""
        self._validate_supabase()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        data.update({
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        })

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = self._client.post(endpoint, files=files, data=data)
        return handle_response(response)

    def vectorize_image(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        """Uploads an image to user's Supabase and vectorizes it."""
        return self._post_file(ep.VECTORIZER, file_path, {"event_id": event_id, "business_id": business_id})

    def find_face(self, file_path: str, event_id: str, business_id: str) -> Dict[str, Any]:
        """Finds faces within the image using user's Supabase."""
        return self._post_file(ep.FIND_FACE, file_path, {"event_id": event_id, "business_id": business_id})

    def search_face(self, prompt: str, event_id: str, business_id: str, top_k: int = 5) -> Dict[str, Any]:
        """Searches for similar images using a text prompt and user's Supabase embeddings."""
        
        params = {
            "prompt": prompt,
            "event_ids": [event_id],
            "business_id": business_id,
            "top_k": top_k,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }

        response = self._client.get(ep.SEARCH_FACE, params=params)
        return handle_response(response)


    def list_embeddings(self, event_id: str, business_id: str) -> Dict[str, Any]:
        """Lists all embeddings for a specific event/business."""
        self._validate_supabase()
        params = {
            "event_id": event_id,
            "business_id": business_id,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }
        response = self._client.get(ep.LIST_EMBEDDINGS, params=params)
        return handle_response(response)

    def delete_embedding(self, embedding_id: str) -> Dict[str, Any]:
        """Deletes a specific embedding record."""
        self._validate_supabase()
        params = {
            "embedding_id": embedding_id,
            "supabase_url": self.supabase_url,
            "supabase_service_key": self.supabase_service_key,
            "supabase_bucket": self.supabase_bucket,
        }
        response = self._client.delete(ep.DELETE_EMBEDDING, params=params)
        return handle_response(response)

    # --- Lifecycle ---
    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
