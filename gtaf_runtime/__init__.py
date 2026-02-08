from .enforce import evaluate
from .types import EnforcementResult

# Public runtime API: enforce. Keep evaluate as backwards-compatible alias.
enforce = evaluate

__all__ = ["enforce", "evaluate", "EnforcementResult"]
