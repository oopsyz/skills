# Neo4j Server Requirements

## Version Compatibility

### Relationship Property Indexes

**Important**: Relationship property indexes (`FOR ()-[r:RELATES_TO]-() ON (r.type)`) require Neo4j server version **4.3+**.

- **Neo4j 4.3+**: Full support for relationship property indexes
- **Neo4j 4.0-4.2**: Relationship property indexes not supported (indexes will fail silently)
- **Neo4j 3.x**: Not supported

### Driver vs Server Version

The `requirements.txt` specifies the **Python driver version**, not the server version:

```txt
neo4j>=5.0.0  # Python driver version
```

**You must ensure your Neo4j server is version 4.3 or higher** for relationship property indexes to work.

### Checking Your Neo4j Version

```cypher
CALL dbms.components() YIELD name, versions, edition
RETURN name, versions[0] as version, edition;
```

Or via command line:
```bash
neo4j version
```

### Workaround for Older Neo4j Versions

If you're using Neo4j < 4.3, you can disable relationship property indexes:

```python
populate_neo4j(
    data=data,
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    create_indexes_flag=False  # Skip indexes
)
```

Then create only node property indexes manually:

```cypher
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_spec_id IF NOT EXISTS FOR (e:Entity) ON (e.specId);
```

### Performance Impact

Without relationship property indexes:
- Queries filtering by `r.type` will be slower
- Consider using node labels or other strategies for filtering
- For large datasets, upgrade to Neo4j 4.3+

## Recommended Neo4j Configuration

For optimal performance with hundreds of diagrams:

```properties
# neo4j.conf
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=4g
dbms.memory.pagecache.size=2g

# Enable relationship property indexes (4.3+)
dbms.index.default_schema_provider=native-btree-1.0
```

## Bulk Import Alternative

For initial loads of hundreds of diagrams, consider using `neo4j-admin import`:

1. Export extracted data to CSV format
2. Use `neo4j-admin import` for faster bulk loading
3. Then use this tool for incremental updates

See Neo4j documentation for CSV import format.

