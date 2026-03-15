"""Resource read with bundling by resource_path metadata."""

from __future__ import annotations

from ims_mcp.clients.doc_cache import InstructionDocCache
from ims_mcp.clients.document import DocumentClient
from ims_mcp.context import CallContext
from ims_mcp.services.bundler import Bundler
from ims_mcp.tools.validation import normalize_relative_path


def normalize_resource_path(path: str) -> str:
    """Normalize VFS resource path to publisher metadata format."""
    normalized = (path or "").strip().replace("\\", "/")
    return normalized.lstrip("/")


async def read_instruction_resource(
    path: str,
    call_ctx: CallContext,
    document_client: DocumentClient,
    bundler: Bundler,
    doc_cache: InstructionDocCache | None = None,
) -> str:
    """Query docs by resource_path metadata and bundle with existing Bundler.

    When doc_cache is provided, filters from the cached full doc list
    instead of issuing a separate RAGFlow query.
    """
    normalized_path, err = normalize_relative_path(normalize_resource_path(path), field="path")
    if err:
        return err
    assert normalized_path is not None

    dataset_name = call_ctx.config.instruction_dataset
    if not call_ctx.authorizer.can_read(dataset_name, call_ctx.user_email):
        return "Error: reading instructions is not permitted"
    try:
        dataset = call_ctx.ragflow.get_dataset(name=dataset_name)
    except Exception as exc:
        return f"Error: failed to open instruction dataset '{dataset_name}': {exc}"

    if not dataset:
        return f"Error: instruction dataset not found: {dataset_name}"

    # Try cache-based lookup first
    if doc_cache is not None:
        try:
            all_docs = doc_cache.get_all_docs(dataset, dataset_name)
            docs = [
                doc for doc in all_docs
                if (Bundler._resource_path(doc) == normalized_path)
            ]
            if docs:
                return bundler.bundle(docs, dataset_name)
            # Fall through to direct query if cache miss
        except Exception:
            pass

    # Direct query fallback (also used when no cache provided)
    import json
    metadata_condition = json.dumps({
        "logic": "and",
        "conditions": [
            {
                "name": "resource_path",
                "comparison_operator": "=",
                "value": normalized_path,
            }
        ],
    })

    try:
        docs = document_client.list_docs(
            dataset=dataset,
            page_size=1000,
            metadata_condition=metadata_condition,
        )
    except Exception as exc:
        return f"Error: failed to query documents for resource_path '{normalized_path}': {exc}"

    if not docs:
        return f"No documents found for resource path: {normalized_path}"

    return bundler.bundle(docs, dataset_name)
