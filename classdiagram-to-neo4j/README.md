# Class Diagram to Neo4j Extraction Skill

This skill extracts structured data from UML class diagrams and populates Neo4j graph databases.

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

- ✅ Vision model extraction (OpenAI GPT-4 Vision, Anthropic Claude)
- ✅ Structured data extraction (entities, properties, relationships)
- ✅ Scalable Neo4j relationship model
- ✅ Batch processing support
- ✅ Provenance tracking
- ✅ YAML and JSON output formats

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

