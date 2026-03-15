"""Unit tests for the Authorizer service."""

import pytest

from ims_mcp.services.authorizer import Authorizer


class TestAiaDatasets:
    """aia-* datasets: always read, never write."""

    @pytest.mark.parametrize("policy", ["all", "team", "none"])
    def test_aia_read_always_allowed(self, policy):
        auth = Authorizer(read_policy=policy, write_policy=policy)
        assert auth.can_read("aia-r1", "user@example.com") is True

    @pytest.mark.parametrize("policy", ["all", "team", "none"])
    def test_aia_write_always_denied(self, policy):
        auth = Authorizer(read_policy=policy, write_policy=policy)
        assert auth.can_write("aia-r1", "user@example.com") is False

    def test_aia_r2(self):
        auth = Authorizer(read_policy="none", write_policy="all")
        assert auth.can_read("aia-r2", "user@example.com") is True
        assert auth.can_write("aia-r2", "user@example.com") is False


class TestProjectDatasetsAllPolicy:
    """project-* with policy=all."""

    def test_read_all(self):
        auth = Authorizer(read_policy="all", write_policy="none")
        assert auth.can_read("project-myapp", "anyone@example.com") is True

    def test_write_all(self):
        auth = Authorizer(read_policy="none", write_policy="all")
        assert auth.can_write("project-myapp", "anyone@example.com") is True

    def test_create_all(self):
        auth = Authorizer(read_policy="none", write_policy="all")
        assert auth.can_create("anyone@example.com") is True


class TestProjectDatasetsNonePolicy:
    """project-* with policy=none."""

    def test_read_none(self):
        auth = Authorizer(read_policy="none", write_policy="all")
        assert auth.can_read("project-myapp", "user@example.com") is False

    def test_write_none(self):
        auth = Authorizer(read_policy="all", write_policy="none")
        assert auth.can_write("project-myapp", "user@example.com") is False

    def test_create_none(self):
        auth = Authorizer(read_policy="all", write_policy="none")
        assert auth.can_create("user@example.com") is False


class TestProjectDatasetsTeamPolicy:
    """project-* with policy=team (stub: always True)."""

    def test_read_team(self):
        auth = Authorizer(read_policy="team", write_policy="none")
        assert auth.can_read("project-myapp", "member@example.com") is True

    def test_write_team(self):
        auth = Authorizer(read_policy="none", write_policy="team")
        assert auth.can_write("project-myapp", "member@example.com") is True

    def test_create_team(self):
        auth = Authorizer(read_policy="none", write_policy="team")
        assert auth.can_create("member@example.com") is True
