from __future__ import annotations

from types import SimpleNamespace

import pytest

from ims_mcp.config import RosettaConfig
from ims_mcp.context import CallContext
from ims_mcp.services.authorizer import Authorizer
from ims_mcp.tools.feedback import submit_feedback
from ims_mcp.tools.instructions import list_instructions, query_instructions
from ims_mcp.tools.projects import discover_projects, query_project_context, store_project_context
from ims_mcp.tools.resources import read_instruction_resource
from ims_mcp.tools.validation import normalize_project_name, normalize_relative_path


class _InstructionDoc:
    def __init__(self, doc_id: str, name: str, content: str, meta_fields: dict):
        self.id = doc_id
        self.name = name
        self._content = content
        self.meta_fields = meta_fields

    def download(self):
        return self._content.encode("utf-8")


class _InstructionDocClient:
    def download_content(self, doc):
        return doc._content


class _InstructionDocCache:
    def __init__(self, docs):
        self.docs = docs
        self.calls = []

    def get_all_docs(self, dataset, dataset_name: str):
        self.calls.append((dataset, dataset_name))
        return self.docs


class _DatasetLookup:
    def __init__(self, mapping: dict[str, str] | None = None):
        self.mapping = mapping or {}

    def get_id(self, name: str) -> str | None:
        return self.mapping.get(name)

    def invalidate(self) -> None:
        return None


class _Ragflow:
    def __init__(self, datasets=None):
        self._datasets = datasets or []

    def list_datasets(self, page=1, page_size=1000):
        return list(self._datasets)

    def get_dataset(self, name: str):
        return object()


class _FeedbackService:
    def __init__(self):
        self.calls = []

    def submit(self, request_mode: str, feedback: dict, call_ctx: CallContext) -> str:
        self.calls.append((request_mode, feedback, call_ctx))
        return "ok"


class _SelectiveAuthorizer:
    def __init__(self, readable: set[str]):
        self.readable = readable

    def can_read(self, dataset_name: str, user_email: str) -> bool:
        return dataset_name in self.readable

    def can_write(self, dataset_name: str, user_email: str) -> bool:
        return dataset_name in self.readable

    def can_create(self, user_email: str) -> bool:
        return True


def make_call_ctx(*, authorizer=None, ragflow=None, dataset_lookup=None) -> CallContext:
    return CallContext(
        config=RosettaConfig.from_env(),
        ragflow=ragflow or _Ragflow(),
        dataset_lookup=dataset_lookup or _DatasetLookup(),
        ctx=None,
        username="tester",
        repository="RulesOfPower",
        tool_name="test",
        params={},
        user_email="tester@example.com",
        authorizer=authorizer or Authorizer("all", "all"),
    )


@pytest.mark.asyncio
async def test_query_project_context_requires_query_or_tags():
    call_ctx = make_call_ctx(dataset_lookup=_DatasetLookup({"project-demo": "d1"}))
    result = await query_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        bundler=object(),
        query_builder=object(),
        repository_name="demo",
    )
    assert result == "Error: at least one of query or tags is required"


@pytest.mark.asyncio
async def test_query_project_context_rejects_invalid_repository_name():
    call_ctx = make_call_ctx(dataset_lookup=_DatasetLookup({"project-demo": "d1"}))
    result = await query_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        bundler=object(),
        query_builder=object(),
        repository_name="../bad",
        tags=["architecture"],
    )
    assert result == "Error: repository_name must not contain '/' or '\\' characters"


@pytest.mark.asyncio
async def test_store_project_context_rejects_empty_fields():
    call_ctx = make_call_ctx()
    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="   ",
        document="ARCHITECTURE.md",
        tags=["architecture"],
        content="# x",
    )
    assert result == "Error: repository_name must not be empty"

    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="demo",
        document="ARCHITECTURE.md",
        tags=[],
        content="# x",
    )
    assert result == "Error: tags must contain at least one tag"

    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="demo",
        document="ARCHITECTURE.md",
        tags=["architecture"],
        content="   ",
    )
    assert result == "Error: content must not be empty"


@pytest.mark.asyncio
async def test_store_project_context_rejects_invalid_document_path():
    call_ctx = make_call_ctx()
    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="demo",
        document="../ARCHITECTURE.md",
        tags=["architecture"],
        content="# x",
    )
    assert result == "Error: document must not contain empty, '.' or '..' path segments"


@pytest.mark.asyncio
async def test_store_project_context_rejects_invalid_repository_name():
    call_ctx = make_call_ctx()
    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="../bad",
        document="ARCHITECTURE.md",
        tags=["architecture"],
        content="# x",
        force=True,
    )
    assert result == "Error: repository_name must not contain '/' or '\\' characters"

    result = await store_project_context(
        call_ctx=call_ctx,
        document_client=object(),
        repository_name="demo",
        document="nested//ARCHITECTURE.md",
        tags=["architecture"],
        content="# x",
    )
    assert result == "Error: document must not contain empty, '.' or '..' path segments"


@pytest.mark.asyncio
async def test_discover_projects_filters_unreadable_and_sorts():
    ragflow = _Ragflow(
        datasets=[
            SimpleNamespace(id="1", name="project-zeta"),
            SimpleNamespace(id="99", name="project-alpha"),
            SimpleNamespace(id="9", name="aia-r2"),
            SimpleNamespace(id="2", name="project-bravo"),
            SimpleNamespace(id="7", name="project-../bad"),
        ]
    )
    call_ctx = make_call_ctx(
        ragflow=ragflow,
        authorizer=_SelectiveAuthorizer({"project-alpha", "project-zeta", "project-../bad"}),
    )
    result = await discover_projects(call_ctx=call_ctx)
    assert 'name="alpha"' in result
    assert 'name="zeta"' in result
    assert 'name="bravo"' not in result
    assert '../bad' not in result
    assert result.index('name="alpha"') < result.index('name="zeta"')


@pytest.mark.asyncio
async def test_submit_feedback_rejects_empty_request_mode_and_fields():
    service = _FeedbackService()
    call_ctx = make_call_ctx()

    result = await submit_feedback(
        call_ctx=call_ctx,
        feedback_service=service,
        request_mode="   ",
        feedback={
            "summary": "s",
            "root_cause": "r",
            "prompt_suggestions": "p",
            "context": "c",
        },
    )
    assert result == "Error: request_mode must not be empty"

    result = await submit_feedback(
        call_ctx=call_ctx,
        feedback_service=service,
        request_mode="coding.md",
        feedback={
            "summary": "   ",
            "root_cause": "r",
            "prompt_suggestions": [],
            "context": "c",
        },
    )
    assert result == "Error: feedback.summary must not be empty"


@pytest.mark.asyncio
async def test_submit_feedback_normalizes_list_prompt_suggestions():
    service = _FeedbackService()
    call_ctx = make_call_ctx()

    result = await submit_feedback(
        call_ctx=call_ctx,
        feedback_service=service,
        request_mode=" coding.md ",
        feedback={
            "summary": " summary ",
            "root_cause": " root cause ",
            "prompt_suggestions": [" first ", "second"],
            "context": " ctx ",
        },
    )
    assert result == "ok"
    request_mode, payload, _ = service.calls[0]
    assert request_mode == "coding.md"
    assert payload["summary"] == "summary"
    assert payload["prompt_suggestions"] == ["first", "second"]


@pytest.mark.asyncio
async def test_query_instructions_rejects_invalid_tags():
    call_ctx = make_call_ctx()
    result = await query_instructions(
        call_ctx=call_ctx,
        document_client=object(),
        bundler=object(),
        query_builder=object(),
        tags=[" "],
    )
    assert result == "Error: tags[0] must not be empty"


def test_normalize_relative_path_rejects_double_slash_segments():
    normalized, err = normalize_relative_path("rules//bootstrap.md", field="path")
    assert normalized is None
    assert err == "Error: path must not contain empty, '.' or '..' path segments"


def test_normalize_relative_path_strips_leading_slash():
    # Leading slashes should be silently stripped to handle AI agent confusion
    normalized, err = normalize_relative_path("/skills", field="path_prefix")
    assert err is None
    assert normalized == "skills"
    
    normalized, err = normalize_relative_path("/rules/bootstrap-core-policy.md", field="path")
    assert err is None
    assert normalized == "rules/bootstrap-core-policy.md"
    
    # Multiple leading slashes should also be handled
    normalized, err = normalize_relative_path("///skills", field="path_prefix")
    assert err is None
    assert normalized == "skills"
    
    # Trailing slashes should also be stripped
    normalized, err = normalize_relative_path("skills/", field="path_prefix")
    assert err is None
    assert normalized == "skills"
    
    normalized, err = normalize_relative_path("/skills/", field="path_prefix")
    assert err is None
    assert normalized == "skills"
    
    normalized, err = normalize_relative_path("rules/bootstrap/", field="path")
    assert err is None
    assert normalized == "rules/bootstrap"


def test_normalize_project_name_rejects_path_like_values():
    normalized, err = normalize_project_name("../bad")
    assert normalized is None
    assert err == "Error: repository_name must not contain '/' or '\\' characters"


@pytest.mark.asyncio
async def test_list_instructions_rejects_traversal_prefix():
    call_ctx = make_call_ctx()
    result = await list_instructions(
        call_ctx=call_ctx,
        doc_cache=object(),
        bundler=object(),
        full_path_from_root="../rules",
    )
    assert result == "Error: full_path_from_root must not contain empty, '.' or '..' path segments"


@pytest.mark.asyncio
async def test_list_instructions_accepts_leading_slash_and_normalizes():
    from ims_mcp.services.bundler import Bundler

    docs = [
        _InstructionDoc(
            "1",
            "skill1.md",
            "CONTENT1",
            {"sort_order": 1, "tags": ["t1"], "resource_path": "skills/coding.md"},
        ),
        _InstructionDoc(
            "2",
            "rule1.md",
            "CONTENT2",
            {"sort_order": 2, "tags": ["t2"], "resource_path": "rules/bootstrap.md"},
        ),
    ]
    doc_cache = _InstructionDocCache(docs)
    call_ctx = make_call_ctx()

    # Test that "/skills" works the same as "skills"
    result_with_slash = await list_instructions(
        call_ctx=call_ctx,
        doc_cache=doc_cache,
        bundler=Bundler(_InstructionDocClient()),
        full_path_from_root="/skills",
    )
    
    result_without_slash = await list_instructions(
        call_ctx=call_ctx,
        doc_cache=doc_cache,
        bundler=Bundler(_InstructionDocClient()),
        full_path_from_root="skills",
    )
    
    # Both should succeed and return the same result
    assert "No children found" not in result_with_slash
    assert result_with_slash == result_without_slash


@pytest.mark.asyncio
async def test_list_instructions_all_returns_listing_with_duplicate_path_note():
    from ims_mcp.services.bundler import Bundler

    docs = [
        _InstructionDoc(
            "1",
            "alpha-a.md",
            "FIRST",
            {"sort_order": 1, "tags": ["t1"], "resource_path": "rules/alpha.md"},
        ),
        _InstructionDoc(
            "2",
            "alpha-b.md",
            "SECOND",
            {"sort_order": 2, "tags": ["t2"], "resource_path": "rules/alpha.md"},
        ),
        _InstructionDoc(
            "3",
            "beta.md",
            "THIRD",
            {"sort_order": 3, "tags": ["t3"], "resource_path": "rules/beta.md"},
        ),
        _InstructionDoc(
            "4",
            "ignored.md",
            "IGNORED",
            {"sort_order": 4, "tags": ["t4"]},
        ),
    ]
    doc_cache = _InstructionDocCache(docs)
    call_ctx = make_call_ctx()

    result = await list_instructions(
        call_ctx=call_ctx,
        doc_cache=doc_cache,
        bundler=Bundler(_InstructionDocClient()),
        full_path_from_root="all",
    )

    assert result.startswith("List of all instruction files, without content.")
    assert "When acquired, files with duplicate path values are bundled/combined together" in result
    assert "Use guaranteed unique 3-part/2-part tags to read specific content" in result
    assert result.count('path="rules/alpha.md"') == 2
    assert "FIRST" not in result and "SECOND" not in result and "THIRD" not in result
    assert "IGNORED" not in result
    assert doc_cache.calls


@pytest.mark.asyncio
async def test_read_instruction_resource_rejects_invalid_path_and_unauthorized_access():
    unauthorized_ctx = make_call_ctx(authorizer=_SelectiveAuthorizer(set()))
    result = await read_instruction_resource(
        path="rules/bootstrap-core-policy.md",
        call_ctx=unauthorized_ctx,
        document_client=object(),
        bundler=object(),
    )
    assert result == "Error: reading instructions is not permitted"

    authorized_ctx = make_call_ctx()
    result = await read_instruction_resource(
        path="../rules/bootstrap-core-policy.md",
        call_ctx=authorized_ctx,
        document_client=object(),
        bundler=object(),
    )
    assert result == "Error: path must not contain empty, '.' or '..' path segments"


def test_server_normalize_tags_preserves_blank_string_for_validation():
    from ims_mcp.server import _normalize_tags

    assert _normalize_tags("") == (None, "Error: tags must not be empty")
    assert _normalize_tags(" tag ") == (["tag"], None)
