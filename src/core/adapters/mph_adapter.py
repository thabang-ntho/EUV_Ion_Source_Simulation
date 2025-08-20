from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional


class SessionAdapter:
    """Adapter interface for acquiring a modeling session (scaffold)."""

    @contextmanager
    def open(self) -> Iterator[Any]:  # returns a client-like object
        raise NotImplementedError


class MphSessionAdapter(SessionAdapter):
    """Default adapter backed by MPh (COMSOL Java API)."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, retries: int = 3, delay: float = 1.0):
        self.host = host
        self.port = port
        self.retries = retries
        self.delay = delay

    @contextmanager
    def open(self) -> Iterator[Any]:
        from ..session import Session

        with Session(retries=self.retries, delay=self.delay) as client:
            yield client


class ModelAdapter:
    """Adapter around a modeling client to create and operate on models (scaffold)."""

    def __init__(self, client: Any):
        self.client = client

    def create_model(self, name: str) -> Any:
        return self.client.create(name)

