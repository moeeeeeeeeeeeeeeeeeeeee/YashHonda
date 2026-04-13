from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    mobile: Mapped[str] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    inquiries: Mapped[list["InquiryModel"]] = relationship(back_populates="customer")


class InquiryModel(Base):
    __tablename__ = "inquiries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    source: Mapped[str] = mapped_column(String(80))
    area: Mapped[str] = mapped_column(String(120))
    vehicle_type: Mapped[str] = mapped_column(String(60))
    model_code: Mapped[str] = mapped_column(String(60))
    color: Mapped[str] = mapped_column(String(80))
    purchase_mode: Mapped[str] = mapped_column(String(30))
    financer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    exchange: Mapped[bool] = mapped_column(Boolean, default=False)
    old_vehicle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    kms: Mapped[int | None] = mapped_column(nullable=True)
    owner_count: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sales_executive: Mapped[str] = mapped_column(String(120))
    buying_when: Mapped[str] = mapped_column(String(120))
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    customer: Mapped[CustomerModel] = relationship(back_populates="inquiries")
    quotes: Mapped[list["QuoteModel"]] = relationship(back_populates="inquiry")


class QuoteModel(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    inquiry_id: Mapped[str] = mapped_column(ForeignKey("inquiries.id"), index=True)
    quote_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="issued")
    preview_data: Mapped[dict] = mapped_column(JSON)
    pdf_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    inquiry: Mapped[InquiryModel] = relationship(back_populates="quotes")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(60))
    actor: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VehicleVariantModel(Base):
    __tablename__ = "vehicle_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    variant_code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    vehicle_group: Mapped[str] = mapped_column(String(30))
    ex_showroom: Mapped[float] = mapped_column(Float)
    rto: Mapped[float] = mapped_column(Float)
    insurance: Mapped[float] = mapped_column(Float)
    standard_charges: Mapped[float] = mapped_column(Float)
    pdi: Mapped[float] = mapped_column(Float, default=0)
    extended_warranty: Mapped[float] = mapped_column(Float, default=0)
    rsa: Mapped[float] = mapped_column(Float, default=0)
    optional_accessories: Mapped[float] = mapped_column(Float, default=0)
    helmet: Mapped[float] = mapped_column(Float, default=0)
    ceramic: Mapped[float] = mapped_column(Float, default=0)
    tcs: Mapped[float] = mapped_column(Float, default=0)
    down_payment: Mapped[float] = mapped_column(Float)
    emi_24: Mapped[float] = mapped_column(Float)
    emi_36: Mapped[float] = mapped_column(Float)
    emi_48: Mapped[float] = mapped_column(Float)
    available_colors: Mapped[list] = mapped_column(JSON, default=list)
    features: Mapped[list] = mapped_column(JSON, default=list)


class AccessoryMasterModel(Base):
    __tablename__ = "accessory_masters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    amount: Mapped[float] = mapped_column(Float)
    charge_type: Mapped[str] = mapped_column(String(20), default="optional")
    category: Mapped[str] = mapped_column(String(60), default="accessory")
    exclusion_group: Mapped[str | None] = mapped_column(String(80), nullable=True)
    max_per_group: Mapped[int] = mapped_column(Integer, default=1)


class AccessoryCompatibilityModel(Base):
    __tablename__ = "accessory_compatibility"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    accessory_id: Mapped[str] = mapped_column(ForeignKey("accessory_masters.id"), index=True)
    variant_code: Mapped[str] = mapped_column(String(60), index=True)
