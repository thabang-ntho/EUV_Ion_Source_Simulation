from __future__ import annotations

import math
import re
from typing import Any, Dict, Optional, Tuple
import time

_UNIT_RE = re.compile(r"^\s*([+-]?[0-9]*\.?[0-9]+(?:[eE][+-]?\d+)?)\s*(?:\[([^\]]+)\])?\s*$")


def parse_value_unit(s: str) -> Tuple[Optional[float], Optional[str]]:
    """Parse a COMSOL-style value like '1.23[um]' or '300[K]'.

    Returns (value_float, unit_str). If parsing fails, returns (None, None).
    """
    m = _UNIT_RE.match(s.strip())
    if not m:
        return None, None
    val = float(m.group(1))
    unit = m.group(2)
    return val, unit


def unit_is_si(unit: Optional[str], expected: str) -> bool:
    """Best-effort check that unit string matches expected SI unit label.

    This does not convert units; it only checks for exact label match when provided.
    """
    if unit is None:
        return True  # allow unit-less for COMSOL parameterized expressions
    return unit.strip() == expected


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe_eval_expr(expr: str, variables: Dict[str, Any]) -> Any:
    """Evaluate a simple math expression safely with a limited namespace.

    Allowed: basic Python operators, math functions, and provided variables.
    """
    allowed = {k: getattr(math, k) for k in (
        'pi','e','sin','cos','tan','asin','acos','atan','atan2','sqrt','log','log10','exp','fabs','pow','floor','ceil'
    )}
    allowed.update(variables)
    return eval(expr, {"__builtins__": {}}, allowed)


def retry(func, attempts: int = 3, delay: float = 1.0):
    """Retry a callable for transient failures.

    Returns the function result or raises the last exception.
    """
    last = None
    for i in range(1, attempts + 1):
        try:
            return func()
        except Exception as e:  # noqa: BLE001 (broad by design for transient wrappers)
            last = e
            if i < attempts:
                time.sleep(delay)
    raise last
