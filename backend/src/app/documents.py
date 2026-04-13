from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.schemas import QuoteDocumentLink
from app.settings import get_settings


class DocumentService:
    def build_quote_document(self, quote_id: UUID, quote_number: str) -> QuoteDocumentLink:
        settings = get_settings()
        expires_at = datetime.now(UTC) + timedelta(minutes=15)
        storage_key = f"quotes/{quote_id}/{quote_number}.pdf"
        url = (
            f"{settings.public_api_base_url}/api/v1/quote-documents/"
            f"{quote_id}?expires_at={expires_at.isoformat()}"
        )
        return QuoteDocumentLink(
            storage_key=storage_key,
            bucket=settings.quote_document_bucket,
            url=url,
            expires_at=expires_at,
        )


document_service = DocumentService()
