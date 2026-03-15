"""Auto-invite service for newly created project datasets.

Stub implementation — RAGFlow SDK does not expose a team-invite API.
Methods are defined as no-ops (no exceptions) so call sites are ready
for future implementation.
"""

from __future__ import annotations

from typing import Any


async def auto_invite(
    ragflow: Any,
    dataset: Any,
    user_email: str,
    invite_emails: list[str],
) -> None:
    """Invite *invite_emails* (and optionally *user_email*) to *dataset*.

    Stub: does nothing.  When RAGFlow adds an invite API, implement here.
    """
