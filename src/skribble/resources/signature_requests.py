from __future__ import annotations

from typing import Any, Dict, List, Optional

from skribble.exceptions import SkribbleError
from skribble.client import SkribbleClient


class SignatureRequestsClient:
    """
    Client for /v2/signature-requests endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    # ---------- Create ----------

    def create(
        self,
        *,
        title: str,
        signatures: List[Dict[str, Any]],
        content: Optional[str] = None,
        file_url: Optional[str] = None,
        document_id: Optional[str] = None,
        visual_signatures: Optional[List[Dict[str, Any]]] = None,
        observers: Optional[List[Dict[str, Any]]] = None,
        callbacks: Optional[List[Dict[str, Any]]] = None,
        auto_attachments: Optional[List[Dict[str, Any]]] = None,
        signature_level: Optional[str] = None,
        legislation: Optional[str] = None,
        owner_account_email: Optional[str] = None,
        signing_sequence: Optional[List[str]] = None,
        disable_tan: Optional[bool] = None,
        disable_notifications: Optional[bool] = None,
        **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Create a SignatureRequest.

        This method unifies the multiple "Create SignatureRequest" variants from the Postman
        examples:

        - PDF via `content` (Base64 PDF)
        - PDF via `file_url`
        - Existing Document via `document_id`
        - Extended options: `observers`, `callbacks`, `auto_attachments`, signing sequence,
          notification controls, etc.

        Exactly one of `content`, `file_url` or `document_id` must be provided.
        """
        source_fields = [name for name, val in
                         [("content", content), ("file_url", file_url), ("document_id", document_id)]
                         if val is not None]
        if len(source_fields) != 1:
            raise SkribbleError(
                "Exactly one of `content`, `file_url` or `document_id` must be set"
            )

        body: Dict[str, Any] = {
            "title": title,
            "signatures": signatures,
        }
        if content is not None:
            body["content"] = content
        if file_url is not None:
            body["file_url"] = file_url
        if document_id is not None:
            body["document_id"] = document_id

        if visual_signatures is not None:
            body["visual_signatures"] = visual_signatures
        if observers is not None:
            body["observers"] = observers
        if callbacks is not None:
            body["callbacks"] = callbacks
        if auto_attachments is not None:
            body["auto_attachments"] = auto_attachments
        if signature_level is not None:
            body["signature_level"] = signature_level
        if legislation is not None:
            body["legislation"] = legislation
        if owner_account_email is not None:
            body["owner_account_email"] = owner_account_email
        if signing_sequence is not None:
            body["signing_sequence"] = signing_sequence
        if disable_tan is not None:
            body["disable_tan"] = disable_tan
        if disable_notifications is not None:
            body["disable_notifications"] = disable_notifications

        # Any additional fields introduced by the API can be passed via extra_fields
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            "/signature-requests",
            json=body,
        )
        return resp.json()

    # ---------- Find / list ----------

    def list(
        self,
        *,
        account_email: Optional[str] = None,
        search: Optional[str] = None,
        signature_status: Optional[str] = None,
        status_overall: Optional[str] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        List and filter SignatureRequests.

        Mirrors "List and find SignatureRequests" in the Postman collection.
        """
        params: Dict[str, Any] = {}
        if account_email is not None:
            params["account_email"] = account_email
        if search is not None:
            params["search"] = search
        if signature_status is not None:
            params["signature_status"] = signature_status
        if status_overall is not None:
            params["status_overall"] = status_overall
        if page_number is not None:
            params["page_number"] = page_number
        if page_size is not None:
            params["page_size"] = page_size
        params.update(extra_params)

        resp = self._client.request(
            "GET",
            "/signature-requests",
            params=params,
        )
        return resp.json()

    def get(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Get a single SignatureRequest by ID.
        """
        resp = self._client.request(
            "GET",
            f"/signature-requests/{signature_request_id}",
        )
        return resp.json()

    def get_bulk(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        List SignatureRequests by bulk.

        Mirrors POST /v2/signature-requests/bulk which accepts an array of IDs.
        """
        resp = self._client.request(
            "POST",
            "/signature-requests/bulk",
            json=ids,
        )
        return resp.json()

    # ---------- Signers ----------

    def add_signer(
        self,
        signature_request_id: str,
        *,
        account_email: Optional[str] = None,
        signer_identity_data: Optional[Dict[str, Any]] = None,
        **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Add an individual signer to an existing SignatureRequest.

        Mirrors POST /v2/signature-requests/{SR_ID}/signatures
        using the same parameters as when creating a SignatureRequest.
        """
        if not account_email and not signer_identity_data:
            raise SkribbleError("At least one of account_email or signer_identity_data must be provided.")

        body: Dict[str, Any] = {}
        if account_email is not None:
            body["account_email"] = account_email
        if signer_identity_data is not None:
            body["signer_identity_data"] = signer_identity_data
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/signatures",
            json=body,
        )
        return resp.json()

    def remove_signer(self, signature_request_id: str, signer_id: str) -> None:
        """
        Remove an individual signer by signature ID from a SignatureRequest.

        Mirrors DELETE /v2/signature-requests/{SR_ID}/signatures/{SID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}/signatures/{signer_id}",
            expected_status=204,
        )

    # ---------- Attachments ----------

    def add_attachment(
        self,
        signature_request_id: str,
        *,
        filename: str,
        content_type: str,
        content: str,
        **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Add an attachment to a SignatureRequest.

        Mirrors POST /v2/signature-requests/{SR_ID}/attachments with body containing
        filename, content_type, content (Base64).
        """
        body: Dict[str, Any] = {
            "filename": filename,
            "content_type": content_type,
            "content": content,
        }
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/attachments",
            json=body,
        )
        return resp.json()

    def remove_attachment(self, signature_request_id: str, attachment_id: str) -> None:
        """
        Remove an attachment from a SignatureRequest.

        Mirrors DELETE /v2/signature-requests/{SR_ID}/attachments/{ATTACHMENT_ID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}/attachments/{attachment_id}",
            expected_status=204,
        )

    # ---------- Delete / withdraw / remind ----------

    def delete(self, signature_request_id: str) -> None:
        """
        Delete a SignatureRequest and its associated document.

        Mirrors DELETE /v2/signature-requests/{SR_ID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}",
            expected_status=204,
        )

    def withdraw(self, signature_request_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Withdraw a SignatureRequest, optionally providing a message.

        Mirrors POST /v2/signature-requests/{SR_ID}/withdraw
        """
        body = {"message": message} if message is not None else {}
        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/withdraw",
            json=body if body else None,
        )
        return resp.json()

    def remind(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Send reminder notifications to open signers.

        Mirrors POST /v2/signature-requests/{SR_ID}/remind
        """
        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/remind",
        )
        return resp.json()

    # ---------- Callbacks (Monitoring/Callbacks) ----------

    def list_callbacks(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Get the list of callbacks configured for a SignatureRequest.

        Mirrors GET /v2/signature-requests/{SR_ID}/callbacks
        """
        resp = self._client.request(
            "GET",
            f"/signature-requests/{signature_request_id}/callbacks",
        )
        return resp.json()
