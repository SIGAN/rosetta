import os

from ims_mcp.config import RosettaConfig


def test_from_env_defaults(monkeypatch):
    monkeypatch.delenv("ROSETTA_SERVER_URL", raising=False)
    monkeypatch.delenv("VERSION", raising=False)
    monkeypatch.delenv("ROSETTA_API_KEY", raising=False)
    monkeypatch.delenv("ROSETTA_OAUTH_CALLBACK_PATH", raising=False)
    cfg = RosettaConfig.from_env()
    assert cfg.server_url == "https://ims.evergreen.gcp.griddynamics.net"
    assert cfg.instruction_dataset == "aia-r2"
    assert cfg.oauth_callback_path == "/auth/callback"


def test_root_filter_parsing(monkeypatch):
    monkeypatch.setenv("INSTRUCTION_ROOT_FILTER", "OrgA, orgB ,")
    cfg = RosettaConfig.from_env()
    assert cfg.root_filter == ["orga", "orgb"]


def test_oauth_callback_path_override(monkeypatch):
    monkeypatch.setenv("ROSETTA_OAUTH_CALLBACK_PATH", "/oauth/custom")
    cfg = RosettaConfig.from_env()
    assert cfg.oauth_callback_path == "/oauth/custom"


def test_oauth_callback_path_gets_leading_slash(monkeypatch):
    monkeypatch.setenv("ROSETTA_OAUTH_CALLBACK_PATH", "oauth/custom")
    cfg = RosettaConfig.from_env()
    assert cfg.oauth_callback_path == "/oauth/custom"


def test_invalid_transport_falls_back_to_stdio(monkeypatch):
    monkeypatch.setenv("ROSETTA_TRANSPORT", "grpc")
    cfg = RosettaConfig.from_env()
    assert cfg.transport == "stdio"


def test_http_port_must_be_in_valid_range(monkeypatch):
    monkeypatch.setenv("ROSETTA_HTTP_PORT", "70000")
    cfg = RosettaConfig.from_env()
    assert cfg.http_port == 8000

    monkeypatch.setenv("ROSETTA_HTTP_PORT", "0")
    cfg = RosettaConfig.from_env()
    assert cfg.http_port == 8000


def test_allowed_scopes_parsing(monkeypatch):
    monkeypatch.setenv("ROSETTA_ALLOWED_SCOPES", "allow_client_data, project_read beta allow_client_data")
    cfg = RosettaConfig.from_env()
    assert cfg.allowed_scopes == ("allow_client_data", "project_read", "beta")
