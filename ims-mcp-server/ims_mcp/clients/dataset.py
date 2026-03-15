"""Dataset lookup and caching."""

from __future__ import annotations

import time

from ragflow_sdk import RAGFlow


class DatasetLookup:
    """Bidirectional name<->id dataset cache with TTL and negative caching."""

    def __init__(self, ragflow: RAGFlow, ttl_seconds: int = 300):
        self._ragflow = ragflow
        self._ttl = ttl_seconds
        self._name_to_id: dict[str, tuple[float, str | None]] = {}
        self._id_to_name: dict[str, tuple[float, str | None]] = {}

    def invalidate(self) -> None:
        self._name_to_id.clear()
        self._id_to_name.clear()
        self._last_refresh = 0.0

    def _is_alive(self, ts: float) -> bool:
        return (time.time() - ts) < self._ttl

    def _refresh(self) -> None:
        """Fetch all datasets and rebuild both caches."""
        datasets = self._ragflow.list_datasets(page=1, page_size=1000)
        now = time.time()
        self._name_to_id.clear()
        self._id_to_name.clear()
        for ds in datasets:
            self._name_to_id[ds.name] = (now, ds.id)
            self._id_to_name[ds.id] = (now, ds.name)
        self._last_refresh = now

    def _ensure_fresh(self) -> None:
        if not hasattr(self, "_last_refresh") or not self._is_alive(self._last_refresh):
            self._refresh()

    def get_id(self, name: str) -> str | None:
        self._ensure_fresh()
        cached = self._name_to_id.get(name)
        return cached[1] if cached else None

    def get_name(self, dataset_id: str) -> str | None:
        self._ensure_fresh()
        cached = self._id_to_name.get(dataset_id)
        return cached[1] if cached else None
