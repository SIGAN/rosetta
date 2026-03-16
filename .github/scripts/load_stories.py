#!/usr/bin/env python3
"""
Load Jira stories from epic CTORNDGAIN-1174 that require AI work.

Filtering logic:
  - Status "Planned"               AND no label AI-PLANNING or AI-PLANNED   → plan_matrix
  - Status "Ready for Development" AND no label AI-IMPLEMENTING or AI-IMPLEMENTED → impl_matrix

Writes to GITHUB_OUTPUT:
  plan_matrix, impl_matrix, has_plan, has_impl, plan_count, impl_count
"""

import os
import json
import base64
import urllib.request
import urllib.parse

JIRA_BASE = os.environ["JIRA_URL"].rstrip("/")
_creds = f"{os.environ['JIRA_USERNAME']}:{os.environ['JIRA_API_TOKEN']}"
AUTH = base64.b64encode(_creds.encode()).decode()


def jira_get(path: str) -> dict:
    req = urllib.request.Request(
        f"{JIRA_BASE}{path}",
        headers={
            "Authorization": f"Basic {AUTH}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


JQL = (
    'parent = CTORNDGAIN-1174 '
    'AND status in ("Planned", "Ready for Development") '
    'ORDER BY priority DESC'
)
url = f"/rest/api/3/search?jql={urllib.parse.quote(JQL)}&fields=summary,status,labels&maxResults=50"
data = jira_get(url)

plan_stories: list[dict] = []
impl_stories: list[dict] = []

for issue in data.get("issues", []):
    key: str = issue["key"]
    status: str = issue["fields"]["status"]["name"]
    labels: list[str] = issue["fields"].get("labels", [])
    # Truncate and sanitise summary for use in matrix JSON
    summary: str = issue["fields"]["summary"][:80].replace('"', "'").replace("\n", " ")

    if status == "Planned":
        if "AI-PLANNING" not in labels and "AI-PLANNED" not in labels:
            plan_stories.append({"story_key": key, "story_summary": summary})
    elif status == "Ready for Development":
        if "AI-IMPLEMENTING" not in labels and "AI-IMPLEMENTED" not in labels:
            impl_stories.append({"story_key": key, "story_summary": summary})

# GitHub Actions requires at least one matrix entry — use sentinel if empty
plan_matrix = (
    json.dumps({"include": plan_stories})
    if plan_stories
    else json.dumps({"include": [{"story_key": "__skip__", "story_summary": ""}]})
)
impl_matrix = (
    json.dumps({"include": impl_stories})
    if impl_stories
    else json.dumps({"include": [{"story_key": "__skip__", "story_summary": ""}]})
)

output_file = os.environ.get("GITHUB_OUTPUT", "/dev/stdout")
with open(output_file, "a") as f:
    f.write(f"plan_matrix={plan_matrix}\n")
    f.write(f"impl_matrix={impl_matrix}\n")
    f.write(f"plan_count={len(plan_stories)}\n")
    f.write(f"impl_count={len(impl_stories)}\n")
    f.write(f"has_plan={'true' if plan_stories else 'false'}\n")
    f.write(f"has_impl={'true' if impl_stories else 'false'}\n")

print(f"Stories to plan:      {len(plan_stories)}")
print(f"Stories to implement: {len(impl_stories)}")
for s in plan_stories:
    print(f"  [PLAN] {s['story_key']}: {s['story_summary']}")
for s in impl_stories:
    print(f"  [IMPL] {s['story_key']}: {s['story_summary']}")
