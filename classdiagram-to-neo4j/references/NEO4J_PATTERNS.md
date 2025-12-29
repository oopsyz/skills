# Neo4j Query Patterns

These are common query patterns for the classdiagram-to-neo4j schema.

## Find an entity by FQN

```cypher
MATCH (e:Entity {fqn: $fqn}) RETURN e;
```

## Find all entities in a schema block

```cypher
MATCH (sb:SchemaBlock {id: $specId})-[:CONTAINS_ENTITY]->(e)
RETURN e;
```

## Expand relationships from an entity

```cypher
MATCH (e {fqn: $fqn})-[r:RELATES_TO]->(t)
RETURN e, r, t;
```

## Get fields for an entity

```cypher
MATCH (e {fqn: $fqn})-[:HAS_FIELD]->(f:Field)
RETURN f;
```

## Subgraph (2 hops)

```cypher
MATCH p=(e {fqn: $fqn})-[:RELATES_TO*1..2]->(x)
RETURN p;
```
