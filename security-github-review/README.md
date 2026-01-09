# Security GitHub Review Skill

A comprehensive security review workflow for GitHub repositories that integrates with the Security MCP to provide OWASP ASVS and NIST 800-53 aligned security assessments.

## Overview

This skill performs practical, code-aware security reviews of GitHub repositories and translates findings into actionable security reports, checklists, and requirements. It leverages the Security MCP (Model Context Protocol) to map findings to industry-standard security frameworks.

## Features

- **Code-Aware Analysis**: Reviews actual code, configuration files, and deployment artifacts
- **Standards Alignment**: Maps findings to OWASP ASVS requirements and optionally NIST 800-53 controls
- **Multiple Output Formats**: Generates reports, checklists, or requirements documents
- **Evidence-Based**: Provides specific file paths, line numbers, and exploit scenarios
- **Risk Prioritization**: Focuses on high-impact vulnerabilities first

## Usage

### Basic Usage

```bash
# Review a GitHub repository
security-github-review --repo https://github.com/user/repo

# Review a local repository
security-github-review --repo /path/to/local/repo

# Generate a checklist instead of a report
security-github-review --repo https://github.com/user/repo --output checklist

# Include NIST 800-53 compliance mapping
security-github-review --repo https://github.com/user/repo --compliance nist-800-53
```

### Input Parameters

- **`repo`** (required): GitHub URL or local path to the repository
- **`target`** (optional): Subdirectory or module to focus the review on
- **`threat_model`** (optional): Brief description of threat actors, assets, and entry points
- **`constraints`** (optional): Technical constraints (language, framework, deployment model, etc.)
- **`output`** (optional): Output format - `report` (default), `checklist`, or `requirements`
- **`report_path`** (optional): Custom path for the output file
- **`compliance`** (optional): `none` (default) or `nist-800-53`
- **`depth`** (optional): Review depth - `quick` (default), `standard`, or `deep`

## Workflow

The skill follows a structured workflow:

1. **Repository Inventory**: Identifies tech stack, dependencies, and deployment configuration
2. **Attack Surface Analysis**: Maps authentication, authorization, input validation, and other security-critical areas
3. **Code Review**: Traces data flows and identifies vulnerabilities with evidence
4. **Standards Mapping**: Uses Security MCP to map findings to ASVS/NIST controls
5. **Report Generation**: Creates prioritized findings with remediation recommendations

## Output Formats

### Report (Default)

A comprehensive security review report including:
- Executive summary with top risks
- Prioritized findings with evidence
- Exploit scenarios and remediation steps
- ASVS/NIST control mappings
- Missing controls and gaps
- Recommended next steps (30/60/90 day plan)

### Checklist

An ASVS-driven checklist tailored to the repository's technology stack and features, suitable for security audits and compliance reviews.

### Requirements

User-story-friendly acceptance criteria derived from ASVS requirements, suitable for development teams to implement security controls.

## Security MCP Integration

This skill requires access to the Security MCP server, which provides:
- OWASP ASVS requirement search and retrieval
- NIST 800-53 control mapping
- Cross-framework mapping (ASVS ↔ NIST)

If the Security MCP is unavailable, the skill will proceed with a best-effort review but will note that findings are unmapped to standards.

## Report Versioning

Reports are automatically versioned to prevent overwriting:
- Default naming: `SECURITY_REVIEW_YYYYMMDD_HHMM.md`
- If a file already exists, a version suffix is appended (`_v2`, `_v3`, etc.)

## Limitations

- This skill produces engineering triage reviews, not formal penetration tests
- Review depth may be limited for very large repositories
- Framework-specific knowledge may be limited for uncommon technologies
- Requires Security MCP access for standards mapping

## Error Handling

The skill handles common scenarios:
- Private repositories: Prompts for local path or zip export
- Large repositories: Switches to quick mode and documents scope limitations
- Unfamiliar technologies: Focuses on architecture and common security primitives
- Missing Security MCP: Proceeds with unmapped findings

## Examples

### Quick Review

```bash
security-github-review --repo https://github.com/user/repo --depth quick
```

### Deep Review with NIST Mapping

```bash
security-github-review \
  --repo https://github.com/user/repo \
  --depth deep \
  --compliance nist-800-53 \
  --output report
```

### Focused Module Review

```bash
security-github-review \
  --repo https://github.com/user/repo \
  --target src/api \
  --threat_model "Public API endpoints, user input, database access"
```

## Related Skills

- **Security MCP**: Provides the underlying ASVS and NIST 800-53 data
- **BPMN2Skill**: Can be used to model security review workflows

## References

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST SP 800-53](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- Security MCP query snippets: `references/security-mcp-query-snippets.md`
