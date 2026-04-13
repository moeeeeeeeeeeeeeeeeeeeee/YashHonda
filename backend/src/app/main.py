from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db_session, init_db
from app.masters import (
    AREAS,
    COMPANY_PROFILE,
    FINANCE_PROVIDERS,
    PURCHASE_MODES,
    SALES_EXECUTIVES,
    VEHICLE_PRICING,
)
from app.models import (
    AccessoryCompatibilityModel,
    AccessoryMasterModel,
    VehicleVariantModel,
)
from app.repository import DatabaseRepository
from app.schemas import (
    Inquiry,
    InquiryCreate,
    InquiryListResponse,
    Quote,
    QuoteDocumentLink,
    QuoteCalculationRequest,
    QuoteCreate,
    QuotePreview,
)


def get_repository(session: Session = Depends(get_db_session)) -> DatabaseRepository:
    return DatabaseRepository(session)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yash Honda Quote API",
        version="0.1.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        lifespan=lifespan,
    )

    @app.get("/api/v1/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/masters/models")
    def list_models(session: Session = Depends(get_db_session)) -> list[dict[str, object]]:
        rows = session.scalars(select(VehicleVariantModel)).all()
        if rows:
            return [
                {
                    "model_code": row.variant_code,
                    "display_name": row.display_name,
                    "vehicle_group": row.vehicle_group,
                    "available_colors": list(row.available_colors or []),
                    "features": list(row.features or []),
                }
                for row in rows
            ]
        return [
            {
                "model_code": pricing.variant_code,
                "display_name": pricing.display_name,
                "vehicle_group": pricing.vehicle_group,
                "available_colors": pricing.available_colors,
                "features": pricing.features,
            }
            for pricing in VEHICLE_PRICING.values()
        ]

    @app.get("/api/v1/masters/accessories")
    def list_accessories(
        variant_code: str, session: Session = Depends(get_db_session)
    ) -> list[dict[str, object]]:
        accessories = session.scalars(
            select(AccessoryMasterModel)
            .join(
                AccessoryCompatibilityModel,
                AccessoryCompatibilityModel.accessory_id == AccessoryMasterModel.id,
            )
            .where(AccessoryCompatibilityModel.variant_code == variant_code)
            .order_by(AccessoryMasterModel.code)
        ).all()
        return [
            {
                "code": accessory.code,
                "name": accessory.name,
                "amount": accessory.amount,
                "category": accessory.category,
                "exclusion_group": accessory.exclusion_group,
                "max_per_group": accessory.max_per_group,
            }
            for accessory in accessories
        ]

    @app.get("/api/v1/masters/supporting")
    def supporting_masters() -> dict[str, object]:
        return {
            "finance_providers": FINANCE_PROVIDERS,
            "areas": AREAS,
            "purchase_modes": PURCHASE_MODES,
            "sales_executives": SALES_EXECUTIVES,
            "company_profile": COMPANY_PROFILE.model_dump(),
        }

    @app.post("/api/v1/inquiries", response_model=Inquiry)
    def create_inquiry(
        payload: InquiryCreate,
        repository: DatabaseRepository = Depends(get_repository),
    ) -> Inquiry:
        return repository.create_inquiry(payload, actor="sales")

    @app.get("/api/v1/inquiries/open", response_model=InquiryListResponse)
    def list_open_inquiries(
        repository: DatabaseRepository = Depends(get_repository),
    ) -> InquiryListResponse:
        return InquiryListResponse(items=list(repository.list_open_inquiries()))

    @app.post("/api/v1/quotes/calculate", response_model=QuotePreview)
    def preview_quote(
        payload: QuoteCalculationRequest,
        repository: DatabaseRepository = Depends(get_repository),
    ) -> QuotePreview:
        try:
            return repository.preview_quote(payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/v1/quotes", response_model=Quote)
    def create_quote(
        payload: QuoteCreate,
        repository: DatabaseRepository = Depends(get_repository),
    ) -> Quote:
        try:
            return repository.create_quote(payload, actor="sales")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/quotes/{quote_id}", response_model=Quote)
    def get_quote(
        quote_id: UUID,
        repository: DatabaseRepository = Depends(get_repository),
    ) -> Quote:
        quote = repository.get_quote(quote_id)
        if quote is None:
            raise HTTPException(status_code=404, detail="Quote not found")
        return quote

    @app.get("/api/v1/quotes/{quote_id}/pdf", response_model=QuoteDocumentLink)
    def get_quote_pdf(
        quote_id: UUID,
        repository: DatabaseRepository = Depends(get_repository),
    ) -> QuoteDocumentLink:
        quote = repository.get_quote(quote_id)
        if quote is None or quote.pdf is None:
            raise HTTPException(status_code=404, detail="Quote PDF not found")
        return quote.pdf

    return app


app = create_app()
