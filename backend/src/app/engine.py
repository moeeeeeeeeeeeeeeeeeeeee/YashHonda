from __future__ import annotations

from collections import Counter, defaultdict

from app.pricing_types import ResolvedAccessory
from app.schemas import (
    ChargeCode,
    ChargeLine,
    FinanceTerms,
    QuoteCalculationRequest,
    QuotePreview,
    QuoteTotals,
    VehicleVariantPricing,
)


def _bundled_accessories(
    request: QuoteCalculationRequest, variant: VehicleVariantPricing
) -> list[ResolvedAccessory]:
    bundled: list[ResolvedAccessory] = []
    if request.include_extended_warranty and variant.extended_warranty:
        bundled.append(
            ResolvedAccessory(
                code=f"__bundle_ew::{variant.variant_code}",
                name="Extended warranty",
                amount=variant.extended_warranty,
                charge_type="optional",
                exclusion_group="bundle_ew",
                max_per_group=1,
            )
        )
    if request.include_optional_accessories and variant.optional_accessories:
        bundled.append(
            ResolvedAccessory(
                code=f"__bundle_opt_acc::{variant.variant_code}",
                name="Optional accessories",
                amount=variant.optional_accessories,
                charge_type="optional",
                exclusion_group="bundle_opt_acc",
                max_per_group=1,
            )
        )
    if request.include_helmet and variant.helmet:
        bundled.append(
            ResolvedAccessory(
                code=f"__bundle_helmet::{variant.variant_code}",
                name="Helmet",
                amount=variant.helmet,
                charge_type="optional",
                exclusion_group="bundle_helmet",
                max_per_group=1,
            )
        )
    if request.include_ceramic and variant.ceramic:
        bundled.append(
            ResolvedAccessory(
                code=f"__bundle_ceramic::{variant.variant_code}",
                name="Ceramic",
                amount=variant.ceramic,
                charge_type="optional",
                exclusion_group="bundle_ceramic",
                max_per_group=1,
            )
        )
    return bundled


def _validate_accessory_selection(accessories: list[ResolvedAccessory]) -> None:
    counts = Counter(acc.code for acc in accessories)
    duplicates = [code for code, total in counts.items() if total > 1]
    if duplicates:
        raise ValueError(f"Duplicate accessory selections: {', '.join(duplicates)}")

    group_usage: dict[str, int] = defaultdict(int)
    for acc in accessories:
        if not acc.exclusion_group:
            continue
        group_usage[acc.exclusion_group] += 1
        if group_usage[acc.exclusion_group] > acc.max_per_group:
            raise ValueError(
                f"Too many accessories in group '{acc.exclusion_group}' "
                f"(max {acc.max_per_group})"
            )


def calculate_quote(
    request: QuoteCalculationRequest,
    variant: VehicleVariantPricing,
    accessories: list[ResolvedAccessory] | None = None,
) -> QuotePreview:
    if request.color not in variant.available_colors:
        raise ValueError(
            f"Color '{request.color}' is not available for model '{request.model_code}'"
        )

    selected = list(accessories or [])
    selected.extend(_bundled_accessories(request, variant))
    _validate_accessory_selection(selected)

    lines = [
        ChargeLine(
            code=ChargeCode.EX_SHOWROOM,
            description="Ex-showroom",
            amount=variant.ex_showroom,
        ),
        ChargeLine(code=ChargeCode.RTO, description="RTO / road tax", amount=variant.rto),
        ChargeLine(
            code=ChargeCode.INSURANCE,
            description="Insurance",
            amount=variant.insurance,
        ),
        ChargeLine(
            code=ChargeCode.STANDARD,
            description="Standard charges",
            amount=variant.standard_charges,
        ),
    ]

    if variant.pdi:
        lines.append(
            ChargeLine(code=ChargeCode.PDI, description="PDI", amount=variant.pdi)
        )

    if variant.rsa:
        lines.append(
            ChargeLine(
                code=ChargeCode.RSA,
                description="RSA",
                amount=variant.rsa,
            )
        )

    if variant.tcs:
        lines.append(
            ChargeLine(
                code=ChargeCode.TCS,
                description="TCS (where applicable)",
                amount=variant.tcs,
            )
        )

    for acc in selected:
        description = (
            f"{acc.name} ({acc.code})"
            if not acc.code.startswith("__bundle_")
            else acc.name
        )
        lines.append(
            ChargeLine(
                code=ChargeCode.ACCESSORY,
                description=description,
                amount=acc.amount,
                charge_type=acc.charge_type,
            )
        )

    subtotal = sum(line.amount for line in lines if line.charge_type != "finance_view")
    preview = QuotePreview(
        model_code=request.model_code,
        display_name=variant.display_name,
        color=request.color,
        purchase_mode=request.purchase_mode,
        lines=lines,
        finance_terms=FinanceTerms(
            down_payment=variant.finance_terms.down_payment,
            emi_24=variant.finance_terms.emi_24,
            emi_36=variant.finance_terms.emi_36,
            emi_48=variant.finance_terms.emi_48,
        ),
        totals=QuoteTotals(subtotal=subtotal, grand_total=subtotal),
    )
    return preview
