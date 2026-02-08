from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


Outcome = Literal["EXECUTE", "DENY"]


@dataclass(frozen=True)
class EnforcementResult:
    outcome: Outcome
    drc_id: str | None
    revision: int | None
    valid_until: str | None
    reason_code: str
    refs: list[str]
    details: dict[str, Any]
