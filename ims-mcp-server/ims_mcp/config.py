"""Environment-backed configuration for Rosetta MCP."""

from __future__ import annotations

import os
from dataclasses import dataclass

from ims_mcp.constants import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_OAUTH_CALLBACK_PATH,
    DEFAULT_PLAN_TTL_DAYS,
    DEFAULT_POSTHOG_HOST,
    DEFAULT_READ_POLICY,
    DEFAULT_SERVER_URL,
    DEFAULT_USER_EMAIL,
    DEFAULT_VERSION,
    DEFAULT_WRITE_POLICY,
    ENV_ALLOWED_ORIGINS,
    ENV_FERNET_KEY,
    ENV_HTTP_HOST,
    ENV_HTTP_PORT,
    ENV_IMS_DEBUG,
    ENV_INSTRUCTION_ROOT_FILTER,
    ENV_INVITE_EMAILS,
    ENV_OAUTH_AUTHORIZATION_ENDPOINT,
    ENV_OAUTH_BASE_URL,
    ENV_OAUTH_CALLBACK_PATH,
    ENV_OAUTH_CLIENT_ID,
    ENV_OAUTH_CLIENT_SECRET,
    ENV_OAUTH_INTROSPECTION_ENDPOINT,
    ENV_OAUTH_JWT_SIGNING_KEY,
    ENV_OAUTH_REVOCATION_ENDPOINT,
    ENV_OAUTH_EXTRA_SCOPES,
    ENV_OAUTH_MODE,
    ENV_OAUTH_OIDC_CONFIG_URL,
    ENV_OAUTH_REQUIRED_SCOPES,
    ENV_OAUTH_SCOPE,
    ENV_OAUTH_TOKEN_ENDPOINT,
    OAUTH_MODE_OAUTH,
    OAUTH_MODE_OIDC,
    ENV_PLAN_TTL_DAYS,
    ENV_POSTHOG_API_KEY,
    ENV_POSTHOG_HOST,
    ENV_READ_POLICY,
    ENV_REDIS_URL,
    ENV_ROSETTA_API_KEY,
    ENV_ROSETTA_SERVER_URL,
    ENV_TRANSPORT,
    ENV_USER_EMAIL,
    ENV_VERSION,
    ENV_WRITE_POLICY,
    INSTRUCTION_DATASET_TEMPLATE,
    TRANSPORT_HTTP,
    TRANSPORT_STDIO,
    VALID_POLICIES,
)


def _parse_int(value: str, default: int) -> int:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return default


def _parse_port(value: str, default: int) -> int:
    parsed = _parse_int(value, default)
    if 1 <= parsed <= 65535:
        return parsed
    return default


def _normalize_transport(value: str) -> str:
    normalized = value.lower().strip()
    if normalized in {TRANSPORT_STDIO, TRANSPORT_HTTP}:
        return normalized
    return TRANSPORT_STDIO


def _normalize_callback_path(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return DEFAULT_OAUTH_CALLBACK_PATH
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized


@dataclass(frozen=True)
class RosettaConfig:
    server_url: str
    version: str
    api_key: str
    posthog_api_key: str
    posthog_host: str
    debug: bool
    root_filter: list[str]
    transport: str
    http_host: str
    http_port: int
    redis_url: str | None
    fernet_key: str | None
    allowed_origins: list[str]
    # OAuth (HTTP transports only)
    oauth_authorization_endpoint: str
    oauth_token_endpoint: str
    oauth_introspection_endpoint: str
    oauth_client_id: str
    oauth_client_secret: str
    oauth_base_url: str
    oauth_callback_path: str
    oauth_valid_scopes: str
    oauth_extra_scopes: str
    oauth_revocation_endpoint: str
    oauth_jwt_signing_key: str | None
    oauth_mode: str
    oauth_oidc_config_url: str
    oauth_required_scopes: list[str] | None
    # Authorization policies
    read_policy: str
    write_policy: str
    user_email: str
    invite_emails: list[str]
    # Plan manager
    plan_ttl_days: int

    @classmethod
    def from_env(cls) -> "RosettaConfig":
        raw_debug = os.getenv(ENV_IMS_DEBUG, "")
        raw_filter = os.getenv(ENV_INSTRUCTION_ROOT_FILTER, "")
        root_filter = [item.strip().lower() for item in raw_filter.split(",") if item.strip()]

        http_port = _parse_port(os.getenv(ENV_HTTP_PORT, ""), DEFAULT_HTTP_PORT)

        raw_origins = os.getenv(ENV_ALLOWED_ORIGINS, "")
        allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

        raw_invite = os.getenv(ENV_INVITE_EMAILS, "")
        invite_emails = [e.strip() for e in raw_invite.split(",") if e.strip()]

        read_policy = os.getenv(ENV_READ_POLICY, DEFAULT_READ_POLICY).lower().strip() or DEFAULT_READ_POLICY
        write_policy = os.getenv(ENV_WRITE_POLICY, DEFAULT_WRITE_POLICY).lower().strip() or DEFAULT_WRITE_POLICY
        if read_policy not in VALID_POLICIES:
            read_policy = DEFAULT_READ_POLICY
        if write_policy not in VALID_POLICIES:
            write_policy = DEFAULT_WRITE_POLICY

        return cls(
            server_url=os.getenv(ENV_ROSETTA_SERVER_URL, DEFAULT_SERVER_URL).rstrip("/"),
            version=os.getenv(ENV_VERSION, DEFAULT_VERSION).strip() or DEFAULT_VERSION,
            api_key=os.getenv(ENV_ROSETTA_API_KEY, "").strip(),
            posthog_api_key=os.getenv(ENV_POSTHOG_API_KEY, ""),
            posthog_host=os.getenv(ENV_POSTHOG_HOST, DEFAULT_POSTHOG_HOST).strip() or DEFAULT_POSTHOG_HOST,
            debug=raw_debug.lower() in {"1", "true", "yes", "on"},
            root_filter=root_filter,
            transport=_normalize_transport(os.getenv(ENV_TRANSPORT, TRANSPORT_STDIO)),
            http_host=os.getenv(ENV_HTTP_HOST, DEFAULT_HTTP_HOST).strip() or DEFAULT_HTTP_HOST,
            http_port=http_port,
            redis_url=os.getenv(ENV_REDIS_URL, "").strip() or None,
            fernet_key=os.getenv(ENV_FERNET_KEY, "").strip() or None,
            allowed_origins=allowed_origins,
            oauth_authorization_endpoint=os.getenv(ENV_OAUTH_AUTHORIZATION_ENDPOINT, "").strip(),
            oauth_token_endpoint=os.getenv(ENV_OAUTH_TOKEN_ENDPOINT, "").strip(),
            oauth_introspection_endpoint=os.getenv(ENV_OAUTH_INTROSPECTION_ENDPOINT, "").strip(),
            oauth_client_id=os.getenv(ENV_OAUTH_CLIENT_ID, "").strip(),
            oauth_client_secret=os.getenv(ENV_OAUTH_CLIENT_SECRET, "").strip(),
            oauth_base_url=os.getenv(ENV_OAUTH_BASE_URL, "").strip(),
            oauth_callback_path=_normalize_callback_path(
                os.getenv(ENV_OAUTH_CALLBACK_PATH, DEFAULT_OAUTH_CALLBACK_PATH)
            ),
            oauth_valid_scopes=os.getenv(ENV_OAUTH_SCOPE, "").strip(),
            oauth_extra_scopes=os.getenv(ENV_OAUTH_EXTRA_SCOPES, "").strip(),
            oauth_mode=os.getenv(ENV_OAUTH_MODE, OAUTH_MODE_OAUTH).lower().strip(),
            oauth_oidc_config_url=os.getenv(ENV_OAUTH_OIDC_CONFIG_URL, "").strip(),
            oauth_required_scopes=[
                s.strip() for s in os.getenv(ENV_OAUTH_REQUIRED_SCOPES, "").split()
                if s.strip()
            ] or None,
            oauth_revocation_endpoint=os.getenv(ENV_OAUTH_REVOCATION_ENDPOINT, "").strip(),
            oauth_jwt_signing_key=os.getenv(ENV_OAUTH_JWT_SIGNING_KEY, "").strip() or None,
            read_policy=read_policy,
            write_policy=write_policy,
            user_email=os.getenv(ENV_USER_EMAIL, DEFAULT_USER_EMAIL).strip() or DEFAULT_USER_EMAIL,
            invite_emails=invite_emails,
            plan_ttl_days=_parse_int(os.getenv(ENV_PLAN_TTL_DAYS, ""), DEFAULT_PLAN_TTL_DAYS),
        )

    @property
    def instruction_dataset(self) -> str:
        return INSTRUCTION_DATASET_TEMPLATE.format(version=self.version)

    @property
    def oauth_configured(self) -> bool:
        """True when all required OAuth fields are set."""
        if self.oauth_mode == OAUTH_MODE_OIDC:
            return bool(
                self.oauth_oidc_config_url
                and self.oauth_client_id
                and self.oauth_client_secret
            )
        return bool(
            self.oauth_authorization_endpoint
            and self.oauth_token_endpoint
            and self.oauth_introspection_endpoint
            and self.oauth_client_id
            and self.oauth_client_secret
        )

    def resolve_oauth_base_url(self) -> str:
        """Return the public base URL for OAuth callbacks."""
        if self.oauth_base_url:
            return self.oauth_base_url.rstrip("/")
        return f"http://{self.http_host}:{self.http_port}"
