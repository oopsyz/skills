# Class Diagram to Neo4j Extraction Skill

This skill extracts structured data from UML class diagrams and populates Neo4j graph databases.

## Why This Matters

### For Telco

- Telco domains (TMF APIs, product catalog, pricing, ordering) are highly relational; a graph makes dependency tracing, impact analysis, and lineage queries straightforward.
- A lot of telco domain knowledge lives in diagrams (specs, architecture decks); extracting it into a graph makes it searchable and reusable across teams and tools.

### Why a Graph Database

- Telco models are many-to-many by default; Neo4j represents relationships as first-class edges instead of complex join patterns.
- You can persist semantics on relationships (role, cardinality, direction, provenance, version), which matches what class diagrams encode and what architects need to reason about change.
- Multi-hop questions ("what relates to what?") map directly to graph traversals and are efficient to query in Cypher.

### Why It's Critical for AI

- AI agents reason more reliably over explicit structure; a graph turns implicit diagram knowledge into a queryable model instead of free-form text.
- It improves grounding for generation (APIs, mappings, docs) by letting agents fetch the exact entities/fields/relationships they need, reducing inconsistencies.
- It enables relationship-aware retrieval (paths, neighbors, subgraphs), which matches telco questions better than keyword/document retrieval alone.

## Quick Start

### Installation

```bash
pip install openai anthropic neo4j pyyaml
# or
pip install -r requirements.txt
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"

export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
```

### Basic Usage

```bash
# Extract diagram to JSON
python scripts/extract_diagram.py diagram.png --output extracted.json

# Populate Neo4j from extracted data
python scripts/populate_neo4j.py extracted.json --password your-password
```

### Python Usage

```python
from scripts.extract_diagram import extract_diagram
from scripts.populate_neo4j import populate_neo4j

# Extract
data = extract_diagram("diagram.png", provider="openai")

# Populate
populate_neo4j(
    data=data,
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
```

## Features

- Vision model extraction (OpenAI GPT-4 Vision, Anthropic Claude)
- Structured data extraction (entities, properties, relationships)
- Scalable Neo4j relationship model
- Batch processing support
- Provenance tracking
- YAML and JSON output formats

## Documentation

- [SKILL.md](SKILL.md) - Complete skill documentation
- [examples/](examples/) - Usage examples
- [references/](references/) - Reference documentation

## Requirements

- Python 3.8+
- OpenAI API key OR Anthropic API key
- Neo4j database (local or remote)
  - **Neo4j server 4.3+** required for relationship property indexes
  - See `NEO4J_REQUIREMENTS.md` for version compatibility details

## License

See main project license.

## Using in OpenAI Codex

### Install the skill (once)

In your target project directory:

```bash
codex
$skill-installer install https://github.com/oopsyz/skills/tree/main/classdiagram-to-neo4j
```

Replace the URL with your fork/path if needed.

### Example Codex prompt

Put your diagram image somewhere in the project (for example `diagrams/product_offering.png`), then in Codex:

```text
$classdiagram-to-neo4j

Extract `diagrams/product_offering.png` into `out/product_offering.json`, then populate Neo4j at `bolt://localhost:7687`.
Use the OpenAI provider and keep the extraction deterministic (low temperature).
After loading, run a Cypher query to list the first 10 `:Entity` nodes with their `name`.
```

Codex typically executes the same underlying steps as the CLI examples: `scripts/extract_diagram.py` (image -> structured JSON/YAML) followed by `scripts/populate_neo4j.py` (structured data -> Neo4j).

## Attribution

Brought to you by [TinCan Lab](https://tincanwireless.com).

