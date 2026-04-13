from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class PurchaseMode(str, Enum):
    CASH = "cash"
    FINANCE = "finance"


class InquiryStatus(str, Enum):
    OPEN = "open"
    BOOKED = "booked"
    CLOSED = "closed"


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"


class ChargeCode(str, Enum):
    EX_SHOWROOM = "ex_showroom"
    RTO = "rto"
    INSURANCE = "insurance"
    STANDARD = "standard"
    PDI = "pdi"
    EXTENDED_WARRANTY = "extended_warranty"
    RSA = "rsa"
    OPTIONAL_ACCESSORIES = "optional_accessories"
    HELMET = "helmet"
    CERAMIC = "ceramic"
    TCS = "tcs"
    ACCESSORY = "accessory"


class ChargeLine(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    code: ChargeCode
    description: str
    amount: float = Field(ge=0)
    charge_type: Literal["base", "optional", "finance_view"] = "base"


class FinanceTerms(BaseModel):
    down_payment: float = Field(ge=0)
    emi_24: float = Field(ge=0)
    emi_36: float = Field(ge=0)
    emi_48: float = Field(ge=0)


class CompanyProfile(BaseModel):
    code: str
    name: str
    address: str
    bank_name: str
    account_number: str
    upi_id: str
    qr_code_ref: str
    gst_number: str


class VehicleVariantPricing(BaseModel):
    variant_code: str
    display_name: str
    vehicle_group: str
    ex_showroom: float
    rto: float
    insurance: float
    standard_charges: float
    pdi: float = 0
    extended_warranty: float = 0
    rsa: float = 0
    optional_accessories: float = 0
    helmet: float = 0
    ceramic: float = 0
    tcs: float = 0
    finance_terms: FinanceTerms
    available_colors: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)


class CustomerCreate(BaseModel):
    name: str
    mobile: str
    email: str | None = None


class Customer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    mobile: str
    email: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InquiryCreate(BaseModel):
    customer: CustomerCreate
    source: str
    area: str
    vehicle_type: str
    model_code: str
    color: str
    purchase_mode: PurchaseMode
    financer: str | None = None
    exchange: bool = False
    old_vehicle: str | None = None
    kms: int | None = None
    owner_count: str | None = None
    sales_executive: str
    buying_when: str
    remarks: str | None = None


class Inquiry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer: Customer
    source: str
    area: str
    vehicle_type: str
    model_code: str
    color: str
    purchase_mode: PurchaseMode
    financer: str | None = None
    exchange: bool = False
    old_vehicle: str | None = None
    kms: int | None = None
    owner_count: str | None = None
    sales_executive: str
    buying_when: str
    remarks: str | None = None
    status: InquiryStatus = InquiryStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuoteCalculationRequest(BaseModel):
    inquiry_id: UUID | None = None
    model_code: str
    color: str
    purchase_mode: PurchaseMode
    financer: str | None = None
    selected_accessory_codes: list[str] = Field(default_factory=list)
    include_extended_warranty: bool = False
    include_optional_accessories: bool = False
    include_helmet: bool = False
    include_ceramic: bool = False


class QuoteTotals(BaseModel):
    subtotal: float
    grand_total: float
    currency: str = "INR"


class QuoteDocumentLink(BaseModel):
    storage_key: str
    bucket: str
    url: str
    expires_at: datetime


class QuotePreview(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    model_code: str
    display_name: str
    color: str
    purchase_mode: PurchaseMode
    lines: list[ChargeLine]
    finance_terms: FinanceTerms
    totals: QuoteTotals

    @computed_field
    @property
    def option_set(self) -> str:
        option_labels = [
            line.description
            for line in self.lines
            if line.charge_type == "optional" and line.amount > 0
        ]
        return ", ".join(option_labels) if option_labels else "base"


class QuoteCreate(QuoteCalculationRequest):
    inquiry_id: UUID


class Quote(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    inquiry_id: UUID
    quote_number: str
    status: QuoteStatus = QuoteStatus.ISSUED
    preview: QuotePreview
    pdf: QuoteDocumentLink | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InquiryListResponse(BaseModel):
    items: list[Inquiry]


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entity_type: str
    entity_id: UUID
    action: str
    actor: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
