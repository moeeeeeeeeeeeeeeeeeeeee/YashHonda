from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db import get_engine, reset_engine_cache
from app.masters import VEHICLE_PRICING
from app.models import (
    AccessoryCompatibilityModel,
    AccessoryMasterModel,
    Base,
    VehicleVariantModel,
)
from app.schemas import VehicleVariantPricing


def upsert_variants(session: Session) -> None:
    session.execute(delete(VehicleVariantModel))
    for pricing in VEHICLE_PRICING.values():
        session.add(
            VehicleVariantModel(
                variant_code=pricing.variant_code,
                display_name=pricing.display_name,
                vehicle_group=pricing.vehicle_group,
                ex_showroom=pricing.ex_showroom,
                rto=pricing.rto,
                insurance=pricing.insurance,
                standard_charges=pricing.standard_charges,
                pdi=pricing.pdi,
                extended_warranty=pricing.extended_warranty,
                rsa=pricing.rsa,
                optional_accessories=pricing.optional_accessories,
                helmet=pricing.helmet,
                ceramic=pricing.ceramic,
                tcs=pricing.tcs,
                down_payment=pricing.finance_terms.down_payment,
                emi_24=pricing.finance_terms.emi_24,
                emi_36=pricing.finance_terms.emi_36,
                emi_48=pricing.finance_terms.emi_48,
                available_colors=list(pricing.available_colors),
                features=list(pricing.features),
            )
        )


def seed_accessories(session: Session, pricing: VehicleVariantPricing) -> None:
    accessories = [
        AccessoryMasterModel(
            code=f"MOD_VISOR::{pricing.variant_code}",
            name="Premium visor",
            amount=1200,
            category="modification",
            exclusion_group="mods",
            max_per_group=3,
        ),
        AccessoryMasterModel(
            code=f"MOD_SEAT::{pricing.variant_code}",
            name="Comfort seat upgrade",
            amount=3500,
            category="modification",
            exclusion_group="mods",
            max_per_group=3,
        ),
        AccessoryMasterModel(
            code=f"MOD_CRASH_GUARD::{pricing.variant_code}",
            name="Crash guard kit",
            amount=4800,
            category="modification",
            exclusion_group="mods",
            max_per_group=3,
        ),
        AccessoryMasterModel(
            code=f"STYLE_GRAPHICS_A::{pricing.variant_code}",
            name="Graphics package A",
            amount=2500,
            category="styling",
            exclusion_group="graphics",
            max_per_group=1,
        ),
        AccessoryMasterModel(
            code=f"STYLE_GRAPHICS_B::{pricing.variant_code}",
            name="Graphics package B",
            amount=2500,
            category="styling",
            exclusion_group="graphics",
            max_per_group=1,
        ),
    ]

    for accessory in accessories:
        session.add(accessory)
        session.flush()
        session.add(
            AccessoryCompatibilityModel(
                accessory_id=accessory.id,
                variant_code=pricing.variant_code,
            )
        )


def run_seed() -> None:
    reset_engine_cache()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        session.execute(delete(AccessoryCompatibilityModel))
        session.execute(delete(AccessoryMasterModel))
        upsert_variants(session)
        for pricing in VEHICLE_PRICING.values():
            seed_accessories(session, pricing)
        session.commit()
