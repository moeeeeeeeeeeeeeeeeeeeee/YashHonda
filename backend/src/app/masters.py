from __future__ import annotations

from app.schemas import CompanyProfile, FinanceTerms, VehicleVariantPricing


COMPANY_PROFILE = CompanyProfile(
    code="YH",
    name="Yash Honda",
    address="Opp Kirloskar Bridge, Ramtekdi, Hadapsar, Pune 411040",
    bank_name="Yash Honda Main Collection",
    account_number="0000000000000000",
    upi_id="payments@yashhonda",
    qr_code_ref="qr://yash-honda-main",
    gst_number="27ABCDE1234F1Z5",
)


VEHICLE_PRICING: dict[str, VehicleVariantPricing] = {
    "ACTIVA_110_STD": VehicleVariantPricing(
        variant_code="ACTIVA_110_STD",
        display_name="Activa 110 Std",
        vehicle_group="mc",
        ex_showroom=77525,
        rto=9298,
        insurance=6982,
        standard_charges=2380,
        pdi=0,
        extended_warranty=737,
        optional_accessories=3883,
        helmet=2248,
        tcs=0,
        finance_terms=FinanceTerms(
            down_payment=35000,
            emi_24=2999,
            emi_36=2344,
            emi_48=1899,
        ),
        available_colors=["Blue", "Grey", "Black", "White", "Red"],
        features=["Scooter", "109cc", "Daily commuter"],
    ),
    "SHINE_125_DISK": VehicleVariantPricing(
        variant_code="SHINE_125_DISK",
        display_name="Shine 125 Disk",
        vehicle_group="mc",
        ex_showroom=86869,
        rto=10347,
        insurance=7579,
        standard_charges=2150,
        pdi=0,
        extended_warranty=894,
        optional_accessories=1141,
        helmet=2248,
        tcs=0,
        finance_terms=FinanceTerms(
            down_payment=42000,
            emi_24=3450,
            emi_36=2680,
            emi_48=2240,
        ),
        available_colors=["Black", "Red", "Blue", "Grey"],
        features=["Motorcycle", "125cc", "Disk brake"],
    ),
    "UNICORN": VehicleVariantPricing(
        variant_code="UNICORN",
        display_name="Honda Unicorn",
        vehicle_group="mc",
        ex_showroom=113327,
        rto=13315,
        insurance=12475,
        standard_charges=2150,
        pdi=0,
        extended_warranty=894,
        optional_accessories=1141,
        helmet=2248,
        tcs=0,
        finance_terms=FinanceTerms(
            down_payment=50000,
            emi_24=4550,
            emi_36=3520,
            emi_48=2920,
        ),
        available_colors=["Black", "Red", "Blue"],
        features=["Motorcycle", "160cc class", "Premium commuter"],
    ),
    "CB350_DLX_PRO": VehicleVariantPricing(
        variant_code="CB350_DLX_PRO",
        display_name="CB350 DLX PRO",
        vehicle_group="big_wing",
        ex_showroom=200200,
        rto=25104,
        insurance=14365,
        standard_charges=2130,
        pdi=0,
        extended_warranty=1000,
        rsa=1999,
        optional_accessories=11317,
        ceramic=3500,
        tcs=0,
        finance_terms=FinanceTerms(
            down_payment=80000,
            emi_24=7890,
            emi_36=6175,
            emi_48=5210,
        ),
        available_colors=["Red", "Blue", "Black", "Silver"],
        features=["BigWing", "350cc", "Touring ready"],
    ),
}


FINANCE_PROVIDERS = ["Shri Ram", "Tata", "HDFC", "Cash"]
AREAS = ["Kothrud", "Hadapsar", "Wakad", "Camp", "Nashik"]
PURCHASE_MODES = ["cash", "finance"]
SALES_EXECUTIVES = ["Vinayak", "Sheel Gupta", "SDG", "Tanuja"]
