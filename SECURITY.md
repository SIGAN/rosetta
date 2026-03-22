# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Rosetta, **please report it privately**. Do not open a public GitHub issue.

**Email:** [rosetta-support@griddynamics.com](mailto:rosetta-support@griddynamics.com)  
**Subject line:** `[SECURITY] <brief description>`

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof of concept
- Affected component(s) (e.g., `ims-mcp-server`, `rosetta-cli`, `rosetta-mcp-server`, instructions, RAGFlow deployment)
- Your suggested severity (Critical / High / Medium / Low)

### Response Commitment

| Milestone | Target |
|---|---|
| Acknowledgment of report | 3 business days |
| Initial triage and severity assessment | 7 business days |
| Patch or mitigation available | Best effort, dependent on severity |
| Public disclosure (coordinated) | After fix is released, or 90 days from report — whichever comes first |

We follow coordinated disclosure. We ask reporters to give us reasonable time to investigate and remediate before any public disclosure. We will credit reporters in the advisory unless they prefer to remain anonymous.

### Safe Harbor

We consider security research conducted in good faith to be authorized and will not pursue legal action against researchers who comply with this policy.

---

## Supported Versions

Security fixes are applied to the **current release and one prior release (N-1)** of each published package. Older releases do not receive backports.

| Component | Package | Supported |
|---|---|---|
| Rosetta MCP Server | [`ims-mcp`](https://pypi.org/project/ims-mcp/) | Current and N-1 |
| Rosetta CLI | [`rosetta-cli`](https://pypi.org/project/rosetta-cli/) | Current and N-1 |
| Instructions | Published via GitHub Releases | Current and N-1 |

---

## Security Architecture

### Design Principles

Rosetta is designed around a strict separation: it serves instructions and knowledge to AI coding agents but **never receives, processes, or stores client source code or project data**. The MCP server delivers context (rules, workflows, conventions) on demand. No repository content flows to Rosetta.

### Data Boundary

- Client source code and project files remain entirely within the IDE and the local agent runtime.
- The Rosetta MCP server transmits only curated instructions, scenario metadata, and workflow definitions.
- Write operations are disabled by default and require explicit enablement by the user.
- Inputs to the MCP server are structurally constrained to prevent unintended data propagation.

---

## Threat Model and Mitigations

### 1. Client Data Exposure

**Risk:** Unauthorized transmission or leakage of client data to the Rosetta server.

**Mitigations:**
- Rosetta's architecture prevents client data from reaching the MCP server by design.
- Write mode is disabled by default; enabling it requires an explicit action by the user.
- All MCP tool inputs are schema-validated to reject unexpected payloads.

**User Responsibility:**
- Do not enable write mode unless your use case requires it and you understand the data flow implications.

**Deployer Responsibility:**
- Validate all integrations with external systems for unintended data leakage.

### 2. Instruction Integrity (Prompt Injection / Poisoning)

**Risk:** Injection of malicious or unintended instructions that alter agent behavior.

**Mitigations:**
- All Rosetta instructions are governed, reviewed, and tested before publication.
- Instructions follow a versioned release lifecycle with change review gates.
- The instruction delivery pipeline does not accept dynamic or user-supplied instruction sources at runtime.

**Deployer Responsibility:**
- Ensure any custom instructions or extensions undergo the same review and approval process.
- Do not introduce unverified or dynamically generated instruction sources into the pipeline.
- Pin instruction versions in production environments.

### 3. MCP Transport Security

**Risk:** Interception, tampering, or replay of messages between the MCP client (IDE) and the Rosetta MCP server.

**Mitigations:**
- MCP connections use HTTP with TLS (HTTPS) for the streamable-HTTP and SSE transports.
- Authentication is enforced via OAuth where supported.
- STDIO transport is available for air-gapped or fully local deployments where network exposure must be eliminated.

**Deployer Responsibility:**
- Always use TLS-terminated endpoints in production. Do not expose MCP servers over plaintext HTTP.
- Rotate OAuth tokens and API keys on a regular cadence.
- For air-gapped environments, prefer the STDIO transport to eliminate network attack surface entirely.
- Do not embed API keys or OAuth secrets in version-controlled configuration files.

### 4. Authentication and Authorization

**Risk:** Unauthorized access to the Rosetta MCP server, RAGFlow, or administrative interfaces.

**Mitigations:**
- The Rosetta MCP server and RAGFlow require authentication for all operations.
- Internal services (including RAGFlow) are not publicly exposed by default and are intended for deployment within controlled network boundaries.

**Deployer Responsibility:**
- Deploy all components behind secure network boundaries (VPC, private subnets, or equivalent).
- Enforce least-privilege access to all services and administrative interfaces.
- Do not expose RAGFlow, internal APIs, or admin endpoints to the public internet.
- Use network-level controls (firewalls, security groups) to restrict access to authorized clients only.

### 5. Analytics and Logging

**Risk:** Leakage of sensitive data through analytics, telemetry, or logging pipelines.

**Mitigations:**
- Usage analytics is opt-in. No data is collected unless you deploy and configure a PostHog instance on your infrastructure and provide its API key via `POSTHOG_API_KEY`.
- When enabled, Rosetta records basic operational metadata: IP address, user email, coding agent name and version, MCP tool called, and tool parameters. This matches information already flowing through the MCP server — no additional data surface is introduced.
- A `before_send` hook strips technical parameters (pagination, model settings) before events leave the server.
- Disabled by default. Without a valid `POSTHOG_API_KEY`, no analytics events are emitted.

**Deployer Responsibility:**
- Review collected metadata for compliance with your organization's data handling and privacy policies.
- If you extend Rosetta with additional logging, ensure sensitive or regulated data is not captured unless explicitly secured and authorized.
- To disable analytics entirely, omit `POSTHOG_API_KEY` or set it to `DISABLED`.

### 6. AI-Generated Output and Coding Agents

**Risk:** Unsafe, incorrect, or vulnerable code generated by AI agents operating with Rosetta-provided context.

**Mitigations:**
- Rosetta implements guardrails including approval gates, risk assessment prompts, and structured workflows (Prepare → Research → Plan → Act) to reduce the likelihood of unsafe agent behavior.

**Limitations:**
- Rosetta provides context and guardrails, not guarantees. AI-generated code can still contain errors, security vulnerabilities, or logic flaws regardless of the instructions provided.

**User Responsibility:**
- **Review all generated code before execution or deployment.** Treat AI output with the same scrutiny as any untrusted contribution.
- Audit all tool calls made by coding agents, particularly those involving write operations or external integrations.
- Do not assume correctness or safety of any generated output.

### 7. LLM Gateway and Model Security

**Risk:** Prompt injection, data leakage, or adversarial exploitation of the underlying LLM.

**Mitigations:**
- Use of an LLM gateway is strongly recommended to centralize control, apply input/output filtering, and enforce security policies.

**Deployer Responsibility:**
- Configure an LLM gateway or proxy layer where possible to monitor and filter model interactions.
- Apply safeguards against prompt injection, jailbreaking, and data exfiltration at the gateway level.
- Monitor model inputs and outputs for anomalous patterns.

### 8. Supply Chain Security

**Risk:** Compromise of published packages (`ims-mcp`, `rosetta-cli`) or their dependencies.

**Mitigations:**
- Packages are published to PyPI via automated CI/CD pipelines with controlled access.
- The repository uses GitHub Actions with defined workflows for builds and releases.

**Deployer Responsibility:**
- Pin dependency versions in production deployments.
- Verify package integrity using checksums or signatures when available.
- Monitor dependencies for known vulnerabilities using tools such as `pip-audit`, Dependabot, or equivalent.
- Review the project's `requirements.txt` and transitive dependencies before deploying in sensitive environments.

---

## General Security Recommendations

- Follow defense-in-depth principles: do not rely on a single layer of protection.
- Apply least-privilege access controls across all components and integrations.
- Regularly audit configurations, access policies, and network exposure.
- Keep all dependencies, base images, and infrastructure components up to date.
- Perform a security review before any production deployment.
- Use separate environments (development, staging, production) with appropriate access controls for each.

---

## Scope and Limitations

This policy covers the Rosetta open-source project as published at [github.com/griddynamics/rosetta](https://github.com/griddynamics/rosetta), including the `ims-mcp` and `rosetta-cli` PyPI packages and the published instruction sets.

This policy does **not** cover:
- Hosted or managed Rosetta deployments operated by Grid Dynamics or third parties (these may have their own security policies).
- Third-party integrations, LLM providers, or IDE platforms used alongside Rosetta.
- The RAGFlow upstream project ([github.com/infiniflow/ragflow](https://github.com/infiniflow/ragflow)), which has its own security practices.

---

## Disclaimer

Rosetta is provided under the [Apache License 2.0](LICENSE) on an "AS IS" basis, without warranties or conditions of any kind. The threat model and mitigations described in this document represent best-effort guidance. Deployers are responsible for conducting their own security assessments appropriate to their environment, compliance requirements, and risk tolerance. Nothing in this document constitutes legal advice or a guarantee of security.
