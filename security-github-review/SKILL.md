---
name: security-github-review
description: Security review workflow for GitHub repositories using the Security MCP (OWASP ASVS + NIST 800-53) as the primary reference and mapping layer. Use when asked to security review a repo, produce an OWASP/NIST-aligned checklist, map findings to ASVS/NIST controls, generate a prioritized vulnerability report, or create security requirements/acceptance criteria from repo code/config.
---

# Security GitHub Review

## Description

Perform a practical, code-aware security review of a GitHub repository and translate findings into:
- Actionable issues with evidence (file paths, symbols, config keys)
- Recommended remediations
- Mappings to OWASP ASVS requirements and (optionally) NIST 800-53 controls via Security MCP

The Security MCP is used to (1) retrieve relevant ASVS requirements for the repo's features and risk surface, and (2) map ASVS requirements to NIST controls for compliance framing.

## Inputs

- `repo` (required): GitHub URL (preferred) or Local path. If not provided, ask for it before starting analysis, do not assume it is local path.
- `target` (optional): Subdirectory/module to focus on.
- `threat_model` (optional): 3-10 bullet summary of actors, assets, and entry points.
- `constraints` (optional): Language/framework, deployment model, authn/authz approach, data sensitivity.
- `output` (optional): `report` (default), `checklist`, or `requirements`.
- `report_path` (optional): Output Markdown path for deliverables. If omitted, create a non-overwriting, versioned Markdown filename (see versioning rules below).
- `compliance` (optional): `none` (default), `nist-800-53`, or `privacy`.
- `depth` (optional): `quick` (default), `standard`, `deep`.
- `mcp_server` (optional): MCP server name for security standards lookup. Defaults to "security" which provides comprehensive ASVS (345 requirements) and NIST 800-53 (1189 controls) datasets with bidirectional mapping support. If unavailable, ask user for the correct server name.

## Actions

1. Acquire repo context
   - If `repo` is a URL, clone to a temp folder; if local, use as-is.
   - Identify tech stack, entry points, and deployment (Docker/K8s/CI).
2. Inventory attack surface
   - Auth/session handling, authorization, input validation, file upload, SSRF/RCE primitives.
   - Secrets, crypto, dependency and supply-chain posture.
3. Review code and config
   - Trace data flows from ingress -> business logic -> storage -> egress.
   - Check framework defaults and security headers/CSRF/CORS.
4. Use Security MCP to anchor to standards
   - Query ASVS requirements relevant to observed features/risks.
   - Map ASVS -> NIST controls when `compliance=nist-800-53`.
5. Write deliverables
   - Findings: severity, likelihood, impact, evidence, remediation, mapping (ASVS + optional NIST).
   - Gaps checklist: missing controls inferred from ASVS searches.
   - Requirements: acceptance criteria derived from ASVS.

## Orchestration Logic

### Step 0: Confirm scope (fast)

- Verify security MCP server availability:
  - Use MCP health check to verify dataset status (345 ASVS requirements, 1189 NIST 800-53 controls)
  - If MCP server is unavailable, continue review without mappings and label as such
- If `repo` is missing, ask for either:
  - a GitHub URL (HTTPS is fine), or
  - a local path to the repo checkout.
  Do not proceed with review steps until `repo` is provided.
- Load appropriate prompt template from `references/prompts-for-depth-levels.md`:
  - If `depth` is not provided, default to `quick` (fast review focusing on critical/high severity issues).
  - Load prompt template based on `depth` and `compliance` parameters:
    - `depth=quick`: Use quick review prompts (L1 ASVS focus, top_k=3, 3-5 min budget)
    - `depth=standard` or unspecified: Use standard review prompts (L2 ASVS focus, top_k=5-10, 15-30 min budget)
    - `depth=deep`: Use deep review prompts (L2 ASVS comprehensive, top_k=10-20, 60-120 min budget)
    - `compliance=nist-800-53`: Use NIST compliance-focused prompts (family-based NIST searches, bidirectional mapping)
    - `compliance=privacy`: Use privacy-focused prompts (PII, GDPR, CCPA assessment)
  - Proceed with review using loaded prompt template.
- After completing the review, ask the user:
  - "Would you like a more advanced analysis? This can include code-level vulnerability analysis, threat modeling, deeper ASVS/NIST compliance checks, and comprehensive remediation strategies."
  - If user responds "yes" or "advanced", offer to re-run the review with:
    - `depth=standard` for deeper analysis
    - Code-level vulnerability examination
    - Detailed threat modeling with attack scenarios
    - Expanded ASVS/NIST compliance mapping
    - Comprehensive remediation guidelines with code examples
  - If user declines or requests to proceed, finalize the current quick review output.
- If `output` or `depth` is still ambiguous after initial preference check, proceed with `output=report`, `depth=quick`, and ask clarifying questions.

### Step 1: Repository inventory

Collect:
- Languages/frameworks (e.g., `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, `.csproj`)
- Runtime and deployment (`Dockerfile`, `docker-compose.yml`, `helm/`, `.github/workflows/`)
- Security-relevant config (`.env*`, `config*.json/yaml`, `nginx.conf`, `CORS`, `JWT`, `OAuth`)
If `target` is provided, prioritize that subdirectory but still scan root-level config and CI/CD.

### Step 2: Quick risk-based triage

Prioritize review by likelihood x impact:
- Authentication/session and credential handling
- Authorization checks near data access and admin endpoints
- Deserialization, template rendering, command execution, SSRF primitives
- File upload and path traversal
- Injection surfaces (SQL/NoSQL/LDAP, template, shell, ORM misuse)
- Dependency posture (lockfiles, private registries, integrity pins)

### Step 3: Evidence-first findings

For each candidate issue:
- Capture the exact sink/source and why it's exploitable.
- Capture a minimal reproduction path (request -> handler -> sink).
- If you cannot prove exploitability, downgrade to risk/gap and state uncertainty.

### Step 4: Use Security MCP (ASVS then optional NIST)

Primary MCP Tool: Security MCP Server

The MCP server provides comprehensive security standards lookup capabilities:
- **Dataset Size**: 345 OWASP ASVS requirements, 1189 NIST 800-53 controls
- **ASVS Levels**: Support for L1, L2, L3 filtering
- **NIST Families**: Support for family-based filtering (AC, IA, SC, AU, SA, SI, etc.)
- **Bidirectional Mapping**: ASVS ↔ NIST control mapping with relationship analysis
- **Search Methodology**: Natural language queries with similarity scoring

Use the confirmed MCP server from Step 0.

#### Typical Flow:

1. **Search ASVS** by natural-language description of what you found or what the repo does
   - Tool: `search_security_requirements(query, levels, top_k)`
   - Parameters:
     - `query`: Natural language description (e.g., "authentication and session management", "SQL injection prevention")
     - `levels`: Optional comma-separated ASVS levels (e.g., "L1,L2,L3", defaults to all levels)
     - `top_k`: Maximum number of results to return (default 10)
   - Returns: ASVS shortcode, section, group, description, L1/L2/L3 flags, similarity score

2. **Search NIST 800-53** by natural-language description
   - Tool: `search_nist_80053_controls(query, family, top_k)`
   - Parameters:
     - `query`: Natural language description (e.g., "access control and authentication")
     - `family`: Optional NIST family code (e.g., "AC", "IA", "SC")
     - `top_k`: Maximum number of results to return (default 10)
   - Returns: NIST identifier, name, family, related controls, discussion

3. **Map ASVS → NIST** (when compliance=nist-800-53)
   - Tool: `asvs_to_nist_mapping(asvs_shortcode, top_k)`
   - Parameters:
     - `asvs_shortcode`: ASVS requirement identifier (e.g., "V7.2.4")
     - `top_k`: Maximum number of NIST candidates to return (default 5)
   - Returns: ASVS details + list of candidate NIST controls

4. **Map NIST → ASVS** (when compliance=nist-800-53)
   - Tool: `nist_to_asvs_mapping(identifier, top_k)`
   - Parameters:
     - `identifier`: NIST control identifier (e.g., "AC-2")
     - `top_k`: Maximum number of ASVS candidates to return (default 5)
   - Returns: NIST control details + list of candidate ASVS requirements

5. **Execute Cypher queries** (advanced relationship analysis)
   - Tool: `execute_cypher_query(query, graph_name)`
   - Parameters:
     - `query`: Cypher query string
     - `graph_name`: Optional graph name (defaults to configured graph)
   - Use for: Complex graph traversals, control relationship analysis

6. **Attach identifiers** to findings and/or to missing-control gaps
   - ASVS IDs (e.g., `V6.2.4`) for application-level security requirements
   - NIST control identifiers (e.g., `AC-2`) for compliance framing

#### Query Strategy by Depth:

- **Quick (depth=quick)**: Use `levels="L1"`, `top_k=3`, minimal searches
- **Standard (depth=standard)**: Use `levels="L2"`, `top_k=5-10`, focused searches
- **Deep (depth=deep)**: Use `levels="L2"`, `top_k=10-20`, comprehensive domain coverage
- **Compliance (compliance=nist-800-53)**: Add NIST family-based searches and bidirectional mapping

#### Search Examples:

```python
# Authentication security
search_security_requirements(
    query="authentication and session management security",
    levels="L2",
    top_k=5
)

# Input validation
search_security_requirements(
    query="input validation SQL injection prevention",
    levels="L2",
    top_k=5
)

# NIST access control
search_nist_80053_controls(
    query="access control authorization",
    family="AC",
    top_k=5
)

# ASVS to NIST mapping
asvs_to_nist_mapping(
    asvs_shortcode="V7.2.4",
    top_k=5
)
```

If MCP tools are unavailable, fallback to `references/security-mcp-query-snippets.md` for manual lookup patterns.

### Step 5: Output formats

- `output=report`: write a Markdown report file (see template below)
- `output=checklist`: ASVS-driven checklist tailored to the repo's stack/features
- `output=requirements`: user-story-friendly acceptance criteria derived from ASVS

### Report file requirement (Markdown)

Always write the final deliverable to a Markdown file at `report_path`. In chat, summarize and link to the written file path.

### Report versioning (non-overwriting)

Do not overwrite prior reports.

- If the user provides `report_path`, and the file already exists, create a new file by appending a version suffix.
- If the user does not provide `report_path`, default to a versioned filename.

Recommended default naming:
- `SECURITY_REVIEW_YYYYMMDD_HHMM.md` (24h local time)

If a collision still occurs (same minute), append an increment:
- `SECURITY_REVIEW_YYYYMMDD_HHMM_v2.md`, `..._v3.md`, etc.

Use this minimal structure:

```md
# Security Review Report

> Version: YYYYMMDD_HHMM (or vN)

## Scope
- Repo:
- Target:
- Depth:
- Compliance:

## Executive Summary
- Top risks:
- Overall posture:

## Findings (Prioritized)
### [ID] Title (Severity)
- Evidence: (file:line, function, config key)
- Impact:
- Exploit scenario:
- Recommendation:
- Mapping:
  - ASVS:
  - NIST (optional):

## Gaps / Missing Controls
- ...

## Recommended Next Steps (30/60/90)
- ...

## Appendix
- Inventory notes
- Tooling/commands run (if any)
```

## Error Handling

- If cloning fails or the repo is private, ask for a local path or a zip export.
- If Security MCP is unavailable, proceed with a best-effort review and label the report as unmapped to ASVS/NIST due to missing access.
- If the repo is too large, switch to `depth=quick`, focus on entry points and high-risk modules, and document what was not reviewed.
- If language/framework is unfamiliar, focus on architecture/config, trust boundaries, and common security primitives, and state limitations.

## Notes & Assumptions

- This skill produces a review suitable for engineering triage; it is not a formal pentest.
- Severity should be justified (impact + exploitability) and include remediation priority.
- Avoid inventing tool names: if the exact Security MCP tool surface differs, adapt while keeping the same conceptual flow (ASVS search -> optional NIST mapping).
