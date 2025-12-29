# Vision Extraction Prompts

This document contains optimized prompts for extracting data from UML class diagrams using vision models.

## Standard Extraction Prompt

```
Analyze this UML class diagram and extract:
1. All entities (classes/boxes) with their names
2. All properties (attributes) within each entity with their types
3. All relationships (lines/arrows) between entities with:
   - Source and target entities
   - Relationship type/name
   - Cardinality (multiplicity) if shown
   - Direction
   - Any role names

Return the data in JSON format with this structure:
{
  "entities": {
    "EntityName": {
      "label": "EntityName",
      "properties": [
        {"name": "propertyName", "type": "string", "required": true/false}
      ]
    }
  },
  "relationships": [
    {
      "from": "SourceEntity",
      "to": "TargetEntity",
      "type": "relationship_type",
      "cardinality": "0..1" or "0..*" or "1" or "1..*",
      "direction": "out" or "in" or "bidirectional",
      "role": "roleName" or null
    }
  ],
  "metadata": {
    "diagram_type": "uml_class",
    "color_coding": {},
    "notes": []
  }
}

Be thorough and extract all visible information. If cardinality is not shown, use "0..*" as default.
```

## TMF-Specific Prompt

```
Analyze this TMF (TM Forum) API specification diagram and extract:
1. All entities (resource types) with their names
2. All properties (attributes) within each entity with their types and required flags
3. All relationships between entities with:
   - Source and target entities
   - Relationship type (e.g., "has_specification", "belongs_to_category")
   - Cardinality (0..1, 0..*, 1, 1..*)
   - Direction
   - Role names if present

Pay special attention to:
- Reference entities (ending in "Ref")
- Color coding (light yellow = resource, white = sub-resource)
- Dashed lines (may indicate separate diagrams)
- Mandatory properties (marked with (1))

Return JSON in the specified format. For TMF diagrams, normalize relationship types to snake_case.
```

## High-Detail Prompt

```
Analyze this UML class diagram in extreme detail:

1. Extract ALL entities:
   - Full entity name
   - All visible properties with types
   - Required/optional indicators
   - Default values if shown
   - Constraints if visible

2. Extract ALL relationships:
   - Exact relationship names/labels
   - Source and target entities
   - Cardinality on both ends
   - Relationship direction
   - Role names
   - Aggregation/composition indicators
   - Inheritance relationships

3. Extract visual metadata:
   - Color coding meanings
   - Border styles (solid, dashed)
   - Special markers or icons
   - Notes or annotations

4. Extract structural information:
   - Package/namespace groupings
   - Stereotypes
   - Constraints or invariants

Return comprehensive JSON with all extracted information.
```

## Error Recovery Prompt

```
The previous extraction may have missed some information. Please review this diagram again and:

1. Check for any entities that were missed
2. Verify all properties were extracted
3. Ensure all relationships were captured
4. Verify cardinalities are correct
5. Check for any special notations or markers

Return a JSON with:
- "missing_entities": [] - Any entities not in previous extraction
- "missing_relationships": [] - Any relationships not in previous extraction
- "corrections": [] - Any corrections to previous data
- "additional_metadata": {} - Any additional information found
```

