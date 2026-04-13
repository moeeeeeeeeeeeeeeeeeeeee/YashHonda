from app.engine import calculate_quote
from app.masters import VEHICLE_PRICING
from app.schemas import PurchaseMode, QuoteCalculationRequest


def test_calculate_quote_with_optional_lines() -> None:
    preview = calculate_quote(
        QuoteCalculationRequest(
            model_code="ACTIVA_110_STD",
            color="Blue",
            purchase_mode=PurchaseMode.CASH,
            include_extended_warranty=True,
            include_optional_accessories=True,
            include_helmet=True,
        ),
        VEHICLE_PRICING["ACTIVA_110_STD"],
    )

    assert preview.display_name == "Activa 110 Std"
    assert preview.totals.grand_total == 103053
    assert preview.option_set == "Extended warranty, Optional accessories, Helmet"


def test_calculate_quote_rejects_unknown_color() -> None:
    try:
        calculate_quote(
            QuoteCalculationRequest(
                model_code="ACTIVA_110_STD",
                color="Green",
                purchase_mode=PurchaseMode.CASH,
            ),
            VEHICLE_PRICING["ACTIVA_110_STD"],
        )
    except ValueError as exc:
        assert "Color" in str(exc)
    else:
        raise AssertionError("Expected a ValueError for an unavailable color")
