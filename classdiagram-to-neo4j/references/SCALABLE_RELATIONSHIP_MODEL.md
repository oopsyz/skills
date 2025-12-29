# Scalable Relationship Model

This document explains the scalable relationship model used for Neo4j population.

See `../../../schema_examples/neo4j/SCALABLE_RELATIONSHIP_MODEL.md` for the full documentation.

## Quick Reference

### Relationship Pattern

```cypher
(:Entity)-[:RELATES_TO {
    type: 'relationship_type',
    cardinality: '0..*',
    direction: 'out',
    role: null,
    order: 0
}]->(:TargetEntity)
```

### Benefits

- **Scalable**: Add new relationship types without schema changes
- **Queryable**: Filter by `type` property
- **Maintainable**: Single relationship type to manage
- **Performant**: Index on `type` for fast filtering

### Common Relationship Types

- `has_specification` - Entity has a specification
- `belongs_to_category` - Entity belongs to a category
- `has_price` - Entity has pricing
- `sold_through_channel` - Entity sold through channel
- `relates_to_offering` - Entity relates to another offering

