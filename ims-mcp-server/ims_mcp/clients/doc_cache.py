"""TTL-cached full document list for instruction datasets.

Shared by list_instructions and VFS resource reads to avoid repeated
RAGFlow queries for the same dataset.
"""

from __future__ import annotations

import time

from ims_mcp.clients.document import DocumentClient
from ims_mcp.constants import DOC_CACHE_TTL_SECONDS
from ims_mcp.typing_utils import DatasetLike, DocumentLike


class InstructionDocCache:
    """Cache all documents from an instruction dataset with TTL."""

    def __init__(self, document_client: DocumentClient, ttl: int = DOC_CACHE_TTL_SECONDS):
        self._document_client = document_client
        self._ttl = ttl
        self._docs: list[DocumentLike] = []
        self._dataset_name: str = ""
        self._last_refresh: float = 0.0

    def _is_stale(self, dataset_name: str) -> bool:
        if dataset_name != self._dataset_name:
            return True
        return (time.time() - self._last_refresh) > self._ttl

    def get_all_docs(self, dataset: DatasetLike, dataset_name: str) -> list[DocumentLike]:
        """Return cached full doc list, refreshing if stale."""
        if not self._is_stale(dataset_name):
            return self._docs
        self._docs = self._document_client.list_docs(
            dataset=dataset, page_size=10000,
        )
        self._dataset_name = dataset_name
        self._last_refresh = time.time()
        return self._docs

    def invalidate(self) -> None:
        self._docs = []
        self._dataset_name = ""
        self._last_refresh = 0.0
