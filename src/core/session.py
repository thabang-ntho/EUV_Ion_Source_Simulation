from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional
import os
import time

from .errors import ComsolConnectError, LicenseError
from .utils import retry


def _start_mph(host: Optional[str] = None, port: Optional[int] = None):
    import mph  # lazy import to avoid hard dependency during tests

    if host is not None and port is not None:
        return mph.start(host=host, port=int(port))
    return mph.start()


@contextmanager
def Session(retries: int = 3, delay: float = 1.0, timeout_s: Optional[float] = None):
    """Context manager for an MPh/COMSOL session with retries and diagnostics.

    Attempts to start a client using environment variables `COMSOL_HOST` and
    `COMSOL_PORT` if set. Retries transient failures up to `retries` times.
    On failure, raises `ComsolConnectError` with a suggested fix.
    """
    host = os.environ.get("COMSOL_HOST")
    port = os.environ.get("COMSOL_PORT")
    t0 = time.time()
    try:
        client = retry(lambda: _start_mph(host, int(port) if port else None), attempts=retries, delay=delay)
    except Exception as e:  # noqa: BLE001
        tip = (
            "Check COMSOL license/server availability. Ensure JAVA_HOME and COMSOL_HOME are set. "
            "If using a remote server, set COMSOL_HOST/COMSOL_PORT."
        )
        msg = f"Failed to start COMSOL session: {e}"
        # License-related hints
        low = str(e).lower()
        if "license" in low or "lm_" in low:
            raise LicenseError(msg, suggested_fix=tip) from e
        raise ComsolConnectError(msg, suggested_fix=tip) from e
    else:
        try:
            yield client
        finally:
            # Best-effort close
            try:
                if hasattr(client, "close"):
                    client.close()
            except Exception:
                pass
    finally:
        if timeout_s is not None and (time.time() - t0) > timeout_s:
            # Timing exceeded; not an error, but useful for logs
            pass

