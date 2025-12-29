---
name: classdiagram-to-neo4j
description: Extract entities, properties, and relationships from UML class diagrams (images) and populate Neo4j graph database. Supports TMF-style diagrams, schema diagrams, and other UML class diagrams. Uses vision models for extraction and generates Cypher queries for Neo4j population.
---

# Class Diagram to Neo4j Extraction Skill

## Overview

This skill extracts structured data from UML class diagrams (images) and populates Neo4j graph databases. It's designed for:
- TMF (TM Forum) API specification diagrams
- UML class diagrams
- Entity-relationship diagrams
- Schema diagrams

## Workflow

### 1. **Image Analysis**
   - Use vision models (GPT-4 Vision, Claude Vision, etc.) to analyze diagram images
   - Extract text, boxes, lines, and relationships
   - Identify entities, properties, and relationships

### 2. **Structured Extraction**
   - Parse entities (classes) with their properties
   - Extract relationships (associations, inheritance, etc.)
   - Capture cardinality and relationship metadata
   - Handle color coding and visual indicators

### 3. **Data Normalization**
   - Convert to structured format (YAML/JSON)
   - Normalize entity names and types
   - Standardize relationship types
   - Handle references and aliases

### 4. **Neo4j Population**
   - Generate Cypher queries
   - Create nodes with properties
   - Create relationships with metadata
   - Handle constraints and indexes

## Usage Patterns

### Pattern 1: Direct Image → Neo4j

```python
from classdiagram_to_neo4j import extract_and_populate

# Extract from image and populate Neo4j
extract_and_populate(
    image_path="diagrams/product_offering.png",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
```

### Pattern 2: Extract → YAML → Neo4j

```python
from classdiagram_to_neo4j import extract_to_yaml, populate_from_yaml

# Step 1: Extract to YAML
yaml_data = extract_to_yaml("diagrams/product_offering.png")

# Step 2: Review/edit YAML if needed
# ... manual review ...

# Step 3: Populate Neo4j
populate_from_yaml(yaml_data, neo4j_uri="bolt://localhost:7687")
```

### Pattern 3: Batch Processing

```python
from classdiagram_to_neo4j import batch_extract_and_populate

# Process multiple diagrams
diagrams = [
    "diagrams/product_offering.png",
    "diagrams/category.png",
    "diagrams/pricing.png"
]

batch_extract_and_populate(
    diagrams=diagrams,
    neo4j_uri="bolt://localhost:7687",
    merge_strategy="update"  # or "skip" or "replace"
)
```

## Diagram Types Supported

### TMF-Style Diagrams
- ProductOffering hub diagrams
- Category relationships
- Specification diagrams
- Reference entity diagrams

### UML Class Diagrams
- Classes with attributes
- Associations with multiplicities
- Inheritance hierarchies
- Aggregations and compositions

### Schema Diagrams
- Database schemas
- API schemas
- Domain models

## Extraction Process

### Step 1: Vision Analysis

The vision model analyzes the image and extracts:
- **Entities**: Boxes/classes with names
- **Properties**: Attributes within entities
- **Relationships**: Lines/arrows between entities
- **Metadata**: Cardinality, roles, types
- **Visual Indicators**: Colors, borders, dashed lines

### Step 2: Structured Output

Extracted data is normalized into:

```yaml
meta:
  source: "diagrams/product_offering.png"
  extracted_at: "2024-01-01T00:00:00Z"
  diagram_type: "uml_class"

entities:
  ProductOffering:
    label: "ProductOffering"
    properties:
      - name: "id"
        type: "string"
        required: true
      - name: "name"
        type: "string"
        required: true
      - name: "isBundle"
        type: "boolean"
        required: false

relationships:
  - from: "ProductOffering"
    to: "ProductSpecification"
    type: "has_specification"
    cardinality: "0..1"
    direction: "out"
    properties:
      role: null
```

### Step 3: Neo4j Population

Generates Cypher queries:

```cypher
// Create entities
MERGE (po:ProductOffering {id: 'ProductOffering'})
SET po.name = 'ProductOffering',
    po.label = 'ProductOffering';

// Create relationships
MATCH (po:ProductOffering {id: 'ProductOffering'})
MATCH (ps:ProductSpecification {id: 'ProductSpecification'})
MERGE (po)-[r:RELATES_TO {
    type: 'has_specification',
    cardinality: '0..1',
    direction: 'out'
}]->(ps);
```

## Key Features

### 1. **Scalable Relationship Model**
   - Uses generic `RELATES_TO` relationship type
   - Stores relationship type in `type` property
   - Avoids relationship type explosion
   - See `references/SCALABLE_RELATIONSHIP_MODEL.md`

### 2. **Provenance Tracking**
   - Tracks source diagram for each entity
   - Maintains extraction metadata
   - Supports versioning

### 3. **Conflict Resolution**
   - Handles duplicate entities
   - Merges properties intelligently
   - Resolves relationship conflicts

### 4. **Validation**
   - Validates extracted data
   - Checks for missing required properties
   - Verifies relationship consistency

## Configuration

### Vision Model Settings

```yaml
vision:
  provider: "openai"  # or "anthropic", "google"
  model: "gpt-4-vision-preview"
  max_tokens: 4000
  temperature: 0.1
```

### Neo4j Settings

```yaml
neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "password"
  database: "neo4j"
  create_constraints: true
  create_indexes: true
```

### Extraction Settings

```yaml
extraction:
  include_properties: true
  include_methods: false
  normalize_names: true
  handle_references: true
  extract_cardinality: true
```

## Output Formats

### YAML Format

See `schema_examples/tmf620/productoffering_hub.core.example.yaml` for example.

### JSON Format

```json
{
  "meta": {
    "source": "diagrams/product_offering.png",
    "extracted_at": "2024-01-01T00:00:00Z"
  },
  "entities": {
    "ProductOffering": {
      "label": "ProductOffering",
      "properties": [...]
    }
  },
  "relationships": [...]
}
```

### Cypher Format

See `schema_examples/neo4j/tmf620_productoffering_scalable_model.cypher` for example.

## Integration with Existing Tools

### With TMF MCP Builder

```python
# Extract diagram → Populate Neo4j → Query for context
from classdiagram_to_neo4j import extract_and_populate
from neo4j_query import get_subgraph

# Extract and populate
extract_and_populate("diagrams/tmf620_productoffering.png")

# Query for relevant subgraph
subgraph = get_subgraph(
    entity_name="ProductOffering",
    hops=2,
    relationship_types=["has_specification", "has_price"]
)

# Use subgraph in LLM context
```

### With Schema Blocks

```python
# Extract → YAML Schema Block → Neo4j
from classdiagram_to_neo4j import extract_to_yaml
from schema_blocks import create_schema_block
from neo4j_import import import_schema_block

yaml_data = extract_to_yaml("diagrams/product_offering.png")
schema_block = create_schema_block(yaml_data)
import_schema_block(schema_block)
```

## Best Practices

1. **Pre-process Images**
   - Ensure high resolution
   - Remove noise and artifacts
   - Standardize format (PNG preferred)

2. **Validate Extraction**
   - Review extracted YAML/JSON
   - Verify entity names
   - Check relationship cardinalities

3. **Incremental Updates**
   - Use merge strategies
   - Track changes
   - Maintain provenance

4. **Query Optimization**
   - Create indexes on common properties
   - Use relationship type filters
   - Limit hop depth

5. **Error Handling**
   - Handle missing entities
   - Validate relationships
   - Log extraction issues

## Examples

See `examples/` directory for:
- Simple UML class diagram extraction
- TMF ProductOffering diagram extraction
- Batch processing example
- Custom extraction rules

## References

- `references/SCALABLE_RELATIONSHIP_MODEL.md` - Relationship modeling approach
- `references/VISION_EXTRACTION_PROMPTS.md` - Vision model prompts
- `references/NEO4J_PATTERNS.md` - Neo4j query patterns
- `schema_examples/neo4j/` - Example Cypher scripts

## Troubleshooting

### Common Issues

1. **Low Extraction Quality**
   - Increase image resolution
   - Use better vision model
   - Provide more context in prompts

2. **Missing Relationships**
   - Check diagram clarity
   - Verify relationship detection logic
   - Review extraction output

3. **Neo4j Population Errors**
   - Check constraints
   - Verify relationship types
   - Review Cypher syntax

4. **Performance Issues**
   - Batch operations
   - Use transactions
   - Create indexes

## Future Enhancements

- Support for sequence diagrams
- Support for activity diagrams
- Multi-page diagram handling
- Automatic relationship inference
- Diagram versioning and diff

