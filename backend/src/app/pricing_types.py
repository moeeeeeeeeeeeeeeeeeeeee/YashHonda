from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ResolvedAccessory:
    code: str
    name: str
    amount: float
    charge_type: Literal["base", "optional", "finance_view"]
    exclusion_group: str | None
    max_per_group: int
