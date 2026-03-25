from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_script_module():
    spec = spec_from_file_location(
        "load_stories",
        Path(__file__).with_name("load_stories.py"),
    )
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fetch_story_issues_uses_enhanced_search_endpoint():
    module = load_script_module()
    calls = []

    def fake_request(jira_base, auth_header, path, *, method="GET", payload=None):
        calls.append(
            {
                "jira_base": jira_base,
                "auth_header": auth_header,
                "path": path,
                "method": method,
                "payload": payload,
            }
        )
        return {"issues": [], "total": 0}

    result = module.fetch_story_issues(
        "https://example.atlassian.net",
        "encoded-auth",
        request_fn=fake_request,
    )

    assert result == {"issues": []}
    assert calls == [
        {
            "jira_base": "https://example.atlassian.net",
            "auth_header": "encoded-auth",
            "path": "/rest/api/3/search/jql?maxResults=50&startAt=0",
            "method": "POST",
            "payload": {"jql": module.JQL, "fields": module.FIELDS},
        }
    ]


def test_fetch_story_issues_paginates_all_results():
    module = load_script_module()

    issue_a = {"key": "CTORNDGAIN-10", "fields": {"summary": "A", "status": {"name": "Planned"}, "labels": []}}
    issue_b = {"key": "CTORNDGAIN-11", "fields": {"summary": "B", "status": {"name": "Planned"}, "labels": []}}
    issue_c = {"key": "CTORNDGAIN-12", "fields": {"summary": "C", "status": {"name": "Planned"}, "labels": []}}

    pages = [
        {"issues": [issue_a, issue_b], "total": 3},
        {"issues": [issue_c], "total": 3},
    ]
    call_count = {"n": 0}

    def fake_request(jira_base, auth_header, path, *, method="GET", payload=None):
        idx = call_count["n"]
        call_count["n"] += 1
        return pages[idx]

    result = module.fetch_story_issues(
        "https://example.atlassian.net",
        "encoded-auth",
        request_fn=fake_request,
    )

    assert result == {"issues": [issue_a, issue_b, issue_c]}
    assert call_count["n"] == 2


def test_collect_story_matrices_filters_labels_and_statuses():
    module = load_script_module()

    plan_stories, impl_stories = module.collect_story_matrices(
        {
            "issues": [
                {
                    "key": "CTORNDGAIN-1",
                    "fields": {
                        "summary": 'Plan "story"\nneeds cleanup',
                        "status": {"name": "Planned"},
                        "labels": [],
                    },
                },
                {
                    "key": "CTORNDGAIN-2",
                    "fields": {
                        "summary": "Already planning",
                        "status": {"name": "Planned"},
                        "labels": ["AI-PLANNING"],
                    },
                },
                {
                    "key": "CTORNDGAIN-3",
                    "fields": {
                        "summary": "Ready to implement",
                        "status": {"name": "Selected for Development"},
                        "labels": [],
                    },
                },
                {
                    "key": "CTORNDGAIN-4",
                    "fields": {
                        "summary": "Already implemented",
                        "status": {"name": "Selected for Development"},
                        "labels": ["AI-IMPLEMENTED"],
                    },
                },
            ]
        }
    )

    assert plan_stories == [
        {"story_key": "CTORNDGAIN-1", "story_summary": "Plan 'story' needs cleanup"}
    ]
    assert impl_stories == [
        {"story_key": "CTORNDGAIN-3", "story_summary": "Ready to implement"}
    ]
