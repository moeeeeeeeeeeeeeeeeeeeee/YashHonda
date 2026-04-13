from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Literal, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.documents import document_service
from app.engine import calculate_quote
from app.masters import VEHICLE_PRICING
from app.models import (
    AccessoryCompatibilityModel,
    AccessoryMasterModel,
    AuditLogModel,
    CustomerModel,
    InquiryModel,
    QuoteModel,
    VehicleVariantModel,
)
from app.pricing_types import ResolvedAccessory
from app.schemas import (
    Customer,
    FinanceTerms,
    Inquiry,
    InquiryCreate,
    InquiryStatus,
    PurchaseMode,
    Quote,
    QuoteCalculationRequest,
    QuoteCreate,
    QuoteDocumentLink,
    QuotePreview,
    VehicleVariantPricing,
)


def _to_customer(model: CustomerModel) -> Customer:
    return Customer(
        id=UUID(model.id),
        name=model.name,
        mobile=model.mobile,
        email=model.email,
        created_at=model.created_at,
    )


def _to_inquiry(model: InquiryModel) -> Inquiry:
    return Inquiry(
        id=UUID(model.id),
        customer=_to_customer(model.customer),
        source=model.source,
        area=model.area,
        vehicle_type=model.vehicle_type,
        model_code=model.model_code,
        color=model.color,
        purchase_mode=PurchaseMode(model.purchase_mode),
        financer=model.financer,
        exchange=model.exchange,
        old_vehicle=model.old_vehicle,
        kms=model.kms,
        owner_count=model.owner_count,
        sales_executive=model.sales_executive,
        buying_when=model.buying_when,
        remarks=model.remarks,
        status=model.status,
        created_at=model.created_at,
    )


def _to_quote(model: QuoteModel) -> Quote:
    pdf = (
        QuoteDocumentLink.model_validate(model.pdf_data)
        if model.pdf_data is not None
        else None
    )
    return Quote(
        id=UUID(model.id),
        inquiry_id=UUID(model.inquiry_id),
        quote_number=model.quote_number,
        status=model.status,
        preview=QuotePreview.model_validate(model.preview_data),
        pdf=pdf,
        created_at=model.created_at,
    )


def _variant_from_db(row: VehicleVariantModel) -> VehicleVariantPricing:
    return VehicleVariantPricing(
        variant_code=row.variant_code,
        display_name=row.display_name,
        vehicle_group=row.vehicle_group,
        ex_showroom=row.ex_showroom,
        rto=row.rto,
        insurance=row.insurance,
        standard_charges=row.standard_charges,
        pdi=row.pdi,
        extended_warranty=row.extended_warranty,
        rsa=row.rsa,
        optional_accessories=row.optional_accessories,
        helmet=row.helmet,
        ceramic=row.ceramic,
        tcs=row.tcs,
        finance_terms=FinanceTerms(
            down_payment=row.down_payment,
            emi_24=row.emi_24,
            emi_36=row.emi_36,
            emi_48=row.emi_48,
        ),
        available_colors=list(row.available_colors or []),
        features=list(row.features or []),
    )


def _load_variant(session: Session, model_code: str) -> VehicleVariantPricing:
    row = session.scalar(
        select(VehicleVariantModel).where(VehicleVariantModel.variant_code == model_code)
    )
    if row is not None:
        return _variant_from_db(row)
    if model_code not in VEHICLE_PRICING:
        raise ValueError(f"Unknown model code '{model_code}'")
    return VEHICLE_PRICING[model_code]


def _resolve_accessories(
    session: Session, variant_code: str, codes: list[str]
) -> list[ResolvedAccessory]:
    if not codes:
        return []

    accessories: list[ResolvedAccessory] = []
    for code in codes:
        accessory = session.scalar(
            select(AccessoryMasterModel).where(AccessoryMasterModel.code == code)
        )
        if accessory is None:
            raise ValueError(f"Unknown accessory code '{code}'")

        compatible = session.scalar(
            select(AccessoryCompatibilityModel).where(
                AccessoryCompatibilityModel.accessory_id == accessory.id,
                AccessoryCompatibilityModel.variant_code == variant_code,
            )
        )
        if compatible is None:
            raise ValueError(
                f"Accessory '{code}' is not compatible with variant '{variant_code}'"
            )

        if accessory.charge_type not in {"base", "optional", "finance_view"}:
            raise ValueError(f"Invalid charge_type for accessory '{code}'")

        accessories.append(
            ResolvedAccessory(
                code=accessory.code,
                name=accessory.name,
                amount=accessory.amount,
                charge_type=cast(
                    Literal["base", "optional", "finance_view"], accessory.charge_type
                ),
                exclusion_group=accessory.exclusion_group,
                max_per_group=accessory.max_per_group,
            )
        )

    return accessories


class DatabaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def preview_quote(self, payload: QuoteCalculationRequest) -> QuotePreview:
        variant = _load_variant(self.session, payload.model_code)
        accessories = _resolve_accessories(
            self.session, payload.model_code, payload.selected_accessory_codes
        )
        return calculate_quote(payload, variant, accessories)

    def create_inquiry(self, payload: InquiryCreate, actor: str = "system") -> Inquiry:
        customer = CustomerModel(
            name=payload.customer.name,
            mobile=payload.customer.mobile,
            email=payload.customer.email,
        )
        inquiry = InquiryModel(
            customer=customer,
            source=payload.source,
            area=payload.area,
            vehicle_type=payload.vehicle_type,
            model_code=payload.model_code,
            color=payload.color,
            purchase_mode=payload.purchase_mode.value,
            financer=payload.financer,
            exchange=payload.exchange,
            old_vehicle=payload.old_vehicle,
            kms=payload.kms,
            owner_count=payload.owner_count,
            sales_executive=payload.sales_executive,
            buying_when=payload.buying_when,
            remarks=payload.remarks,
            status=InquiryStatus.OPEN.value,
        )
        self.session.add_all([customer, inquiry])
        self.session.flush()
        self.session.add(
            AuditLogModel(
                entity_type="inquiry",
                entity_id=inquiry.id,
                action="created",
                actor=actor,
            )
        )
        self.session.commit()
        self.session.refresh(inquiry)
        return _to_inquiry(inquiry)

    def list_open_inquiries(self) -> Iterable[Inquiry]:
        result = self.session.scalars(
            select(InquiryModel)
            .options(joinedload(InquiryModel.customer))
            .where(InquiryModel.status == InquiryStatus.OPEN.value)
            .order_by(InquiryModel.created_at.desc())
        )
        return [_to_inquiry(model) for model in result.unique().all()]

    def create_quote(self, payload: QuoteCreate, actor: str = "system") -> Quote:
        inquiry = self.session.scalar(
            select(InquiryModel)
            .options(joinedload(InquiryModel.customer))
            .where(InquiryModel.id == str(payload.inquiry_id))
        )
        if inquiry is None:
            raise KeyError("Inquiry not found")

        preview = self.preview_quote(payload)
        sequence = self.session.scalar(select(func.count()).select_from(QuoteModel)) or 0
        quote_number = f"YH-{datetime.utcnow().year}-{sequence + 1:06d}"
        quote = QuoteModel(
            inquiry_id=inquiry.id,
            quote_number=quote_number,
            status="issued",
            preview_data=preview.model_dump(mode="json"),
        )
        self.session.add(quote)
        self.session.flush()

        pdf = document_service.build_quote_document(UUID(quote.id), quote.quote_number)
        quote.pdf_data = pdf.model_dump(mode="json")
        inquiry.status = InquiryStatus.BOOKED.value
        self.session.add(
            AuditLogModel(
                entity_type="quote",
                entity_id=quote.id,
                action="issued",
                actor=actor,
            )
        )
        self.session.commit()
        self.session.refresh(quote)
        return _to_quote(quote)

    def get_quote(self, quote_id: UUID) -> Quote | None:
        quote = self.session.scalar(
            select(QuoteModel).where(QuoteModel.id == str(quote_id))
        )
        return _to_quote(quote) if quote is not None else None
