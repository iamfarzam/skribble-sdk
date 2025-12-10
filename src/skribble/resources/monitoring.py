from __future__ import annotations

from typing import Any, Dict, List, Optional

from skribble.client import SkribbleClient


class MonitoringClient:
    """
    Client for monitoring-related endpoints:
    - Callbacks for SignatureRequests
    - System health
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def create_signature_request_with_callbacks(
        self,
        *,
        title: str,
        content: str,
        signatures: List[Dict[str, Any]],
        callbacks: List[Dict[str, Any]],
        **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Convenience wrapper for creating a SignatureRequest with all possible callbacks,
        similar to the "Create a signature request with all possible callbacks" example.

        This simply calls SignatureRequestsClient.create(...) under the hood.
        """
        return self._client.signature_requests.create(
            title=title,
            content=content,
            signatures=signatures,
            callbacks=callbacks,
            **extra_fields,
        )

    def system_health(self) -> Dict[str, Any]:
        """
        Check Skribble system health.

        Mirrors GET /management/health which returns e.g. {"status": "UP"}.
        """
        resp = self._client.request(
            "GET",
            "/health",
            management=True,
            auth=False,  # health endpoint typically doesn't require auth
        )
        return resp.json()
