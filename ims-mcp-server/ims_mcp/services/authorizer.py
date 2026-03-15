"""Policy-based authorization for dataset access."""

from __future__ import annotations

from ims_mcp.constants import POLICY_ALL, POLICY_NONE, POLICY_TEAM, PROJECT_DATASET_PREFIX


class Authorizer:
    """Enforces read/write/create policies on datasets.

    Rules:
        - ``aia-*`` datasets: read always allowed, write always denied.
        - ``project-*`` datasets: governed by *read_policy* / *write_policy*.
        - Policy ``all``  → everybody.
        - Policy ``team`` → team members only (stub: always True for now).
        - Policy ``none`` → nobody.
    """

    def __init__(self, read_policy: str, write_policy: str) -> None:
        self._read_policy = read_policy
        self._write_policy = write_policy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def can_read(self, dataset_name: str, user_email: str) -> bool:
        if _is_aia(dataset_name):
            return True
        return self._evaluate(self._read_policy, dataset_name, user_email)

    def can_write(self, dataset_name: str, user_email: str) -> bool:
        if _is_aia(dataset_name):
            return False
        return self._evaluate(self._write_policy, dataset_name, user_email)

    def can_create(self, user_email: str) -> bool:
        """Dataset creation follows write policy."""
        if self._write_policy == POLICY_ALL:
            return True
        if self._write_policy == POLICY_TEAM:
            return True  # everybody can create; current user auto-invited
        return False  # POLICY_NONE

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate(policy: str, dataset_name: str, user_email: str) -> bool:
        if policy == POLICY_ALL:
            return True
        if policy == POLICY_NONE:
            return False
        if policy == POLICY_TEAM:
            return _check_team_membership(dataset_name, user_email)
        return False


def _is_aia(dataset_name: str) -> bool:
    return dataset_name.startswith("aia-")


def _check_team_membership(dataset_name: str, user_email: str) -> bool:
    """Check whether *user_email* is a member of the dataset team.

    Stub: always returns ``True``.  RAGFlow SDK does not expose a
    team-membership API.  When it does, implement the actual check here.
    """
    return True
