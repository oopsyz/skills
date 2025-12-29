# TMF MCP Builder Skill

Build TM Forum (TMF) MCP servers from TMF OpenAPI specs (TMF6xx/7xx YAML). Use this skill to generate a working MCP tool surface for TMF APIs, optionally backed by a local mock server for development.

## Why This Matters

### For Telco

- TMF APIs encode telco domain models (product, customer, service, resource) and the operational workflows around them; turning a spec into tools makes integration and automation much faster.
- Tooling around TMF specs is repetitive (CRUD endpoints, paging, error handling, /hub subscriptions); a standard build workflow reduces drift across teams and vendors.

### Why MCP

- MCP turns your API surface into typed, discoverable tools that agents can call reliably (instead of scraping docs or generating ad-hoc HTTP requests).
- Consistent tool naming and ergonomic inputs (especially for create/patch) make LLM tool-use more accurate and reduce retries.

### Why It's Critical for AI

- Agents need stable tool contracts; MCP + strong schemas reduce hallucinations and make multi-step telco tasks (create -> query -> update -> subscribe) automatable.
- Spec-driven generation enables faster iteration and safer refactors: when the OpenAPI changes, you can regenerate/update tools and re-run evaluation prompts.

## Quick Start

### Prerequisites

- A TMF OpenAPI YAML file (TMF6xx/7xx), e.g. `TMF620-Product_Offering_Management-*.oas.yaml`
- Python 3.8+

### Use the bundled helpers

```bash
# Summarize a TMF OpenAPI spec into a compact JSON inventory
python scripts/tmf_openapi_inventory.py --spec path/to/TMF6xx.oas.yaml --out tmf_inventory.json

# Copy shared mock utilities into your project (optional, for mock server builds)
python scripts/copy_tmf_commons.py --dest path/to/your/project
```

## Features

- TMF-specific naming conventions for files and tools (`tmf{number}_{action}_{resource}`)
- Guidance for create/patch input ergonomics (avoid blob-only inputs)
- $ref resolution and `allOf` merge expectations (TMF-heavy patterns)
- Optional `/hub` event-subscription support guidance for mocks
- Bundled `tmf_commons` utilities for consistent mock server scaffolding

## Documentation

- [SKILL.md](SKILL.md) - Complete workflow and conventions
- `references/resource-creation-guidelines.md` - Create/patch input rules (important)
- `references/TMF_MCP_SERVER_CREATION_PROMPT_all-in-one.md` - Full generation prompt
- `references/TMF_MCP_SERVER_CREATION_PROMPT_libraries.md` - Libraries-based prompt

## Requirements

Runtime dependencies depend on the generated server shape, but typical builds include:

- `mcp` (Python SDK) + `FastMCP`
- `httpx`
- `fastapi` + `uvicorn` (if generating a mock server)
- `pyyaml`

## Using in OpenAI Codex

### Install the skill (once)

In your target project directory:

```bash
codex
$skill-installer install https://github.com/oopsyz/skills/tree/main/tmf-mcp-builder
```

Replace the URL with your fork/path if needed.

### Example Codex prompt

Place your TMF OpenAPI spec in the project (for example `specs/TMF620.oas.yaml`), then in Codex:

```text
$tmf-mcp-builder

Given `specs/TMF620.oas.yaml`, generate a dev sandbox:
- FastAPI mock server with in-memory storage for the main resources
- An `httpx.AsyncClient` TMF client
- An MCP server using the official `mcp` Python SDK / `FastMCP` that exposes CRUD tools

Constraints:
- Resolve `$ref` and merge `allOf` schemas (TMF style)
- Use tool names like `tmf620_list_product_offering`, `tmf620_get_product_offering`, `tmf620_create_product_offering`, `tmf620_patch_product_offering`
- For `create_*` and `patch_*`, expose field-level inputs (not a single blob dict)
- Implement `/hub` subscription tools only if present in the spec

Also create `README-TMF0620.md` describing how to run the mock server and MCP server, env vars, and the tool list.
```

## Attribution

Brought to you by [TinCan Lab](https://tincanwireless.com).
