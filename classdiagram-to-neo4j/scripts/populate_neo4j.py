#!/usr/bin/env python3
"""
Populate Neo4j database from extracted diagram data.
Uses scalable data model with stable labels and FQN-based identity.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

try:
    import yaml
except ImportError:
    yaml = None


def load_data(file_path: str) -> Dict[str, Any]:
    """Load extracted data from JSON or YAML file."""
    path = Path(file_path)
    
    if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
        if yaml is None:
            raise ImportError("pyyaml package required. Install with: pip install pyyaml")
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    else:
        with open(file_path, "r") as f:
            return json.load(f)


# Valid cardinality patterns
VALID_CARDINALITY_PATTERNS = {
    "0..1", "0..*", "1", "1..*", "1..1", "*", 
    "0..0", "1..0", "0..n", "1..n", "n", "m..n"
}

# Valid direction values
VALID_DIRECTIONS = {"out", "in", "bidirectional"}

# Valid relationship types (common patterns)
VALID_RELATIONSHIP_TYPES = {
    "has", "belongs_to", "contains", "references", "relates_to",
    "inherits_from", "implements", "depends_on", "uses"
}


def validate_cardinality(card: Optional[str], field_name: str) -> Optional[str]:
    """Validate cardinality format."""
    if card is None:
        return None  # None is valid (unknown)
    
    if not isinstance(card, str):
        return f"{field_name} must be a string or null"
    
    # Check exact match first
    if card in VALID_CARDINALITY_PATTERNS:
        return None
    
    # Check pattern matches (e.g., "0..5", "1..10")
    if re.match(r'^\d+\.\.\d+$', card):
        return None
    
    if re.match(r'^\d+\.\.\*$', card):
        return None
    
    return f"{field_name} has invalid cardinality format '{card}'"


def validate_extracted_data(data: Dict[str, Any]) -> List[str]:
    """Validate extracted data structure and return list of errors."""
    errors = []
    entity_names = set()
    
    if "entities" not in data:
        errors.append("Missing 'entities' key")
    elif not isinstance(data["entities"], dict):
        errors.append("'entities' must be a dictionary")
    else:
        entity_names = set(data["entities"].keys())
    
    if "relationships" not in data:
        errors.append("Missing 'relationships' key")
    elif not isinstance(data["relationships"], list):
        errors.append("'relationships' must be a list")
    
    # Validate entities
    if "entities" in data and isinstance(data["entities"], dict):
        for entity_name, entity_data in data["entities"].items():
            if not isinstance(entity_data, dict):
                errors.append(f"Entity '{entity_name}' data must be a dictionary")
                continue
            
            # Validate kind if present
            if "kind" in entity_data:
                kind = entity_data["kind"]
                if kind not in ALLOWED_KINDS:
                    errors.append(f"Entity '{entity_name}' has invalid kind '{kind}' (must be one of {ALLOWED_KINDS})")
            
            if "properties" in entity_data:
                if not isinstance(entity_data["properties"], list):
                    errors.append(f"Entity '{entity_name}' properties must be a list")
                else:
                    for prop_idx, prop in enumerate(entity_data["properties"]):
                        if not isinstance(prop, dict):
                            errors.append(f"Entity '{entity_name}' property[{prop_idx}] must be a dictionary")
                            continue
                        
                        if "name" not in prop:
                            errors.append(f"Entity '{entity_name}' property[{prop_idx}] missing 'name'")
                        
                        if "type" in prop and not isinstance(prop["type"], str):
                            errors.append(f"Entity '{entity_name}' property[{prop_idx}] 'type' must be a string")
    
    # Validate relationships
    if "relationships" in data and isinstance(data["relationships"], list):
        for i, rel in enumerate(data["relationships"]):
            if not isinstance(rel, dict):
                errors.append(f"Relationship[{i}] must be a dictionary")
                continue
            
            # Validate required fields
            if "from" not in rel:
                errors.append(f"Relationship[{i}] missing 'from'")
            elif rel["from"] not in entity_names:
                errors.append(f"Relationship[{i}] 'from' entity '{rel['from']}' not found in entities")
            
            if "to" not in rel:
                errors.append(f"Relationship[{i}] missing 'to'")
            elif rel["to"] not in entity_names:
                errors.append(f"Relationship[{i}] 'to' entity '{rel['to']}' not found in entities")
            
            # Validate cardinalities
            if "fromCardinality" in rel:
                card_error = validate_cardinality(rel["fromCardinality"], f"Relationship[{i}].fromCardinality")
                if card_error:
                    errors.append(card_error)
            
            if "toCardinality" in rel:
                card_error = validate_cardinality(rel["toCardinality"], f"Relationship[{i}].toCardinality")
                if card_error:
                    errors.append(card_error)
            
            # Legacy cardinality field
            if "cardinality" in rel:
                card_error = validate_cardinality(rel["cardinality"], f"Relationship[{i}].cardinality")
                if card_error:
                    errors.append(card_error)
            
            # Validate direction
            if "direction" in rel:
                direction = rel["direction"]
                if direction not in VALID_DIRECTIONS:
                    errors.append(f"Relationship[{i}] has invalid direction '{direction}' (must be one of {VALID_DIRECTIONS})")
            
            # Validate type (if present)
            if "type" in rel and rel["type"]:
                rel_type = rel["type"]
                if not isinstance(rel_type, str):
                    errors.append(f"Relationship[{i}] 'type' must be a string")
                # Note: We don't enforce exact match, but warn about unusual patterns
                if not any(rel_type.startswith(prefix) for prefix in VALID_RELATIONSHIP_TYPES):
                    # Just a warning, not an error
                    pass
    
    return errors


def generate_fqn(spec_id: str, entity_name: str) -> str:
    """Generate fully qualified name for entity."""
    return f"{spec_id}#{entity_name}"


# Allowed entity kinds (prevent label injection)
ALLOWED_KINDS = {"Entity", "RefType", "SchemaBlock"}


def determine_entity_kind(entity_name: str, entity_data: Dict[str, Any]) -> str:
    """Determine entity kind (Entity, RefType) with allowlist validation."""
    # Check if it's a reference type
    if entity_name.endswith("Ref") or entity_name.endswith("Reference"):
        return "RefType"
    
    # Check metadata for kind, but validate against allowlist
    if "kind" in entity_data:
        kind = entity_data["kind"]
        if kind in ALLOWED_KINDS:
            return kind
        # If kind is not in allowlist, log warning and default to Entity
        print(f"Warning: Unknown kind '{kind}' for entity '{entity_name}', defaulting to 'Entity'")
    
    # Default to Entity
    return "Entity"


def create_stable_constraints(driver, database: str = "neo4j") -> None:
    """Create constraints for stable labels."""
    with driver.session(database=database) as session:
        constraints = [
            "CREATE CONSTRAINT entity_fqn IF NOT EXISTS FOR (e:Entity) REQUIRE e.fqn IS UNIQUE;",
            "CREATE CONSTRAINT reftype_fqn IF NOT EXISTS FOR (r:RefType) REQUIRE r.fqn IS UNIQUE;",
            "CREATE CONSTRAINT schema_block_id IF NOT EXISTS FOR (s:SchemaBlock) REQUIRE s.id IS UNIQUE;",
            "CREATE CONSTRAINT field_fqn IF NOT EXISTS FOR (f:Field) REQUIRE f.fqn IS UNIQUE;",
        ]
        
        for constraint_query in constraints:
            try:
                session.run(constraint_query)
            except Exception as e:
                print(f"Note: Could not create constraint: {e}")


def create_stable_indexes(driver, database: str = "neo4j", check_server_version: bool = True) -> None:
    """Create indexes for stable labels (correct Neo4j syntax)."""
    with driver.session(database=database) as session:
        # Node property indexes (work on all Neo4j versions)
        node_indexes = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);",
            "CREATE INDEX entity_spec_id IF NOT EXISTS FOR (e:Entity) ON (e.specId);",
            "CREATE INDEX reftype_name IF NOT EXISTS FOR (r:RefType) ON (r.name);",
            "CREATE INDEX field_name IF NOT EXISTS FOR (f:Field) ON (f.name);",
        ]
        
        for index_query in node_indexes:
            try:
                session.run(index_query)
            except Exception as e:
                print(f"Note: Could not create index: {e}")
        
        # Relationship property indexes (require Neo4j 4.3+)
        rel_indexes = [
            "CREATE INDEX relationship_type IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.type);",
            "CREATE INDEX relationship_cardinality IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.cardinality);",
        ]
        
        if check_server_version:
            # Try to check server version
            try:
                result = session.run("CALL dbms.components() YIELD name, versions RETURN versions[0] as version")
                version_str = result.single()["version"]
                version_parts = version_str.split(".")
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                
                if major < 4 or (major == 4 and minor < 3):
                    print(f"Warning: Neo4j server version {version_str} does not support relationship property indexes (requires 4.3+). Skipping relationship indexes.")
                    print("See NEO4J_REQUIREMENTS.md for details.")
                    return
            except Exception:
                # If version check fails, try creating indexes anyway
                pass
        
        for index_query in rel_indexes:
            try:
                session.run(index_query)
            except Exception as e:
                print(f"Note: Could not create relationship property index (may require Neo4j 4.3+): {e}")
                print("See NEO4J_REQUIREMENTS.md for version compatibility details.")


def derive_spec_id(source_path: str, meta: Dict[str, Any]) -> Tuple[str, str]:
    """
    Derive specId and diagramId from source path and metadata.
    
    Returns:
        tuple: (spec_id, diagram_id)
    
    Examples:
        - "tmf620/page_034.png" -> ("tmf620", "page_034")
        - "tmf620/productoffering.png" -> ("tmf620", "productoffering")
        - "diagrams/tmf620_productoffering.png" -> ("tmf620", "productoffering")
    """
    # Check metadata first
    if "specId" in meta:
        spec_id = meta["specId"]
        diagram_id = meta.get("diagramId") or Path(source_path).stem
        return (spec_id, diagram_id)
    
    # Try to extract from path structure
    path = Path(source_path)
    parts = path.parts
    
    # Look for patterns like "tmf620/page_034.png" or "tmf620/productoffering.png"
    if len(parts) >= 2:
        # Check if parent directory looks like a spec ID (e.g., "tmf620")
        parent = parts[-2]
        if parent.startswith("tmf") or parent.startswith("spec"):
            spec_id = parent
            diagram_id = path.stem
            return (spec_id, diagram_id)
    
    # Check filename for spec prefix (e.g., "tmf620_productoffering.png")
    stem = path.stem
    if "_" in stem:
        parts = stem.split("_", 1)
        if parts[0].startswith("tmf") or parts[0].startswith("spec"):
            spec_id = parts[0]
            diagram_id = parts[1] if len(parts) > 1 else stem
            return (spec_id, diagram_id)
    
    # Default: use parent directory or filename stem as spec_id
    if len(parts) >= 2:
        spec_id = parts[-2]
    else:
        spec_id = "default"
    
    diagram_id = path.stem
    return (spec_id, diagram_id)


def create_schema_block(driver, data: Dict[str, Any], database: str = "neo4j") -> Tuple[str, str]:
    """Create SchemaBlock node and return (spec_id, diagram_id)."""
    meta = data.get("meta", {})
    source = meta.get("source", "unknown")
    
    spec_id, diagram_id = derive_spec_id(source, meta)
    
    with driver.session(database=database) as session:
        # Use diagram_id as the unique SchemaBlock ID (one per diagram)
        query = """
        MERGE (sb:SchemaBlock {id: $diagram_id})
        SET sb.specId = $spec_id,
            sb.diagramId = $diagram_id,
            sb.title = $title,
            sb.version = $version,
            sb.artifact = $artifact,
            sb.extractedAt = $extractedAt
        RETURN sb.specId as spec_id, sb.diagramId as diagram_id
        """
        
        result = session.run(
            query,
            spec_id=spec_id,
            diagram_id=diagram_id,
            title=meta.get("title", f"Schema Block: {spec_id}/{diagram_id}"),
            version=meta.get("version", "1.0"),
            artifact=meta.get("source", source),
            extractedAt=meta.get("extracted_at", datetime.utcnow().isoformat() + "Z")
        )
        
        row = result.single()
        return (row["spec_id"], row["diagram_id"])


# Note: create_entity, create_field, and create_relationship are now replaced
# by bulk UNWIND operations in populate_neo4j() for better performance.
# These functions are kept for backward compatibility but not used in the main flow.


def populate_neo4j(
    data: Dict[str, Any],
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_database: str = "neo4j",
    create_constraints_flag: bool = True,
    create_indexes_flag: bool = True,
    validate: bool = True
) -> None:
    """
    Populate Neo4j database from extracted diagram data.
    
    Args:
        data: Extracted diagram data dictionary
        neo4j_uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        neo4j_database: Neo4j database name (now actually used!)
        create_constraints_flag: Whether to create constraints
        create_indexes_flag: Whether to create indexes
        validate: Whether to validate data before populating
    """
    if GraphDatabase is None:
        raise ImportError("neo4j package required. Install with: pip install neo4j")
    
    # Validate data if requested
    if validate:
        errors = validate_extracted_data(data)
        if errors:
            raise ValueError(f"Data validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    try:
        # Create constraints and indexes
        if create_constraints_flag:
            create_stable_constraints(driver, neo4j_database)
        
        if create_indexes_flag:
            create_stable_indexes(driver, neo4j_database, check_server_version=True)
        
        # Create schema block
        spec_id, diagram_id = create_schema_block(driver, data, neo4j_database)
        print(f"Created schema block: {spec_id}/{diagram_id}")
        
        # Track FQNs for relationship creation
        entity_fqns = {}
        
        # Bulk create entities using UNWIND (performance optimization)
        if "entities" in data:
            # Separate entities by kind for correct label assignment
            entity_items = []
            reftype_items = []
            
            for name, entity_data in data["entities"].items():
                item = {
                    "entity_name": name,
                    "entity_data": entity_data,
                    "spec_id": spec_id
                }
                
                # Determine kind with allowlist validation
                kind = determine_entity_kind(name, entity_data)
                if kind == "RefType":
                    reftype_items.append(item)
                else:
                    entity_items.append(item)
            
            with driver.session(database=neo4j_database) as session:
                # Bulk create Entity nodes
                if entity_items:
                    query_entity = """
                    UNWIND $entities AS ent
                    WITH ent.entity_name AS name, ent.entity_data AS data, ent.spec_id AS spec_id,
                         spec_id + '#' + name AS fqn
                    MERGE (e:Entity {fqn: fqn})
                    SET e.name = name,
                        e.label = COALESCE(data.label, name),
                        e.specId = spec_id,
                        e.kind = 'Entity'
                    RETURN e.fqn AS fqn, name AS entity_name
                    """
                    result = session.run(query_entity, entities=entity_items)
                    for record in result:
                        entity_fqns[record["entity_name"]] = record["fqn"]
                        print(f"Created entity: {record['entity_name']} ({record['fqn']})")
                
                # Bulk create RefType nodes
                if reftype_items:
                    query_reftype = """
                    UNWIND $entities AS ent
                    WITH ent.entity_name AS name, ent.entity_data AS data, ent.spec_id AS spec_id,
                         spec_id + '#' + name AS fqn
                    MERGE (e:RefType {fqn: fqn})
                    SET e.name = name,
                        e.label = COALESCE(data.label, name),
                        e.specId = spec_id,
                        e.kind = 'RefType'
                    RETURN e.fqn AS fqn, name AS entity_name
                    """
                    result = session.run(query_reftype, entities=reftype_items)
                    for record in result:
                        entity_fqns[record["entity_name"]] = record["fqn"]
                        print(f"Created reftype: {record['entity_name']} ({record['fqn']})")
        
        # Bulk create fields using UNWIND
        if "entities" in data:
            fields_list = []
            for entity_name, entity_data in data["entities"].items():
                entity_fqn = entity_fqns.get(entity_name)
                if entity_fqn and "properties" in entity_data:
                    for field_data in entity_data["properties"]:
                        fields_list.append({
                            "entity_fqn": entity_fqn,
                            "field_name": field_data.get("name", ""),
                            "field_type": field_data.get("type", "string"),
                            "field_required": field_data.get("required", False),
                            "field_description": field_data.get("description"),
                            "field_default": field_data.get("default")
                        })
            
            if fields_list:
                with driver.session(database=neo4j_database) as session:
                    query = """
                    UNWIND $fields AS f
                    WITH f.entity_fqn AS entity_fqn, f.field_name AS name, f.field_type AS type,
                         f.field_required AS required, f.field_description AS desc, f.field_default AS default_val,
                         entity_fqn + '.' + name AS field_fqn
                    MERGE (field:Field {fqn: field_fqn})
                    SET field.name = name,
                        field.type = type,
                        field.required = required,
                        field.entityFqn = entity_fqn,
                        field.description = desc,
                        field.defaultValue = default_val
                    WITH field, entity_fqn
                    MATCH (e) WHERE e.fqn = entity_fqn
                    MERGE (e)-[:HAS_FIELD]->(field)
                    """
                    session.run(query, fields=fields_list)
                    print(f"Created {len(fields_list)} fields")
        
        # Bulk create relationships using UNWIND
        if "relationships" in data:
            relationships_list = []
            for rel in data["relationships"]:
                from_entity = rel.get("from")
                to_entity = rel.get("to")
                
                if from_entity and to_entity:
                    from_fqn = entity_fqns.get(from_entity)
                    to_fqn = entity_fqns.get(to_entity)
                    
                    if from_fqn and to_fqn:
                        relationships_list.append({
                            "from_fqn": from_fqn,
                            "to_fqn": to_fqn,
                            "rel_type": rel.get("type", "relates_to"),
                            "from_cardinality": rel.get("fromCardinality") or rel.get("cardinality"),
                            "to_cardinality": rel.get("toCardinality") or rel.get("cardinality"),
                            "direction": rel.get("direction", "out"),
                            "role": rel.get("role"),
                            "name": rel.get("name"),
                            "relationship_type": rel.get("relationshipType"),
                            "order": rel.get("order"),
                            "is_containment": rel.get("isContainment", False),
                            "is_inheritance": rel.get("isInheritance", False),
                            "is_dashed": rel.get("isDashed", False)
                        })
            
            if relationships_list:
                with driver.session(database=neo4j_database) as session:
                    query = """
                    UNWIND $relationships AS rel
                    MATCH (from) WHERE from.fqn = rel.from_fqn
                    MATCH (to) WHERE to.fqn = rel.to_fqn
                    WITH from, to, rel,
                         CASE rel.direction
                           WHEN 'in' THEN false
                           WHEN 'bidirectional' THEN true
                           ELSE true
                         END AS create_out,
                         CASE rel.direction
                           WHEN 'out' THEN false
                           WHEN 'bidirectional' THEN true
                           ELSE false
                         END AS create_in
                    FOREACH (x IN CASE WHEN create_out THEN [1] ELSE [] END |
                      MERGE (from)-[r:RELATES_TO]->(to)
                      SET r.type = rel.rel_type,
                          r.direction = 'out',
                          r.fromCardinality = rel.from_cardinality,
                          r.toCardinality = rel.to_cardinality,
                          r.role = rel.role,
                          r.name = rel.name,
                          r.relationshipType = rel.relationship_type,
                          r.order = rel.order,
                          r.isContainment = rel.is_containment,
                          r.isInheritance = rel.is_inheritance,
                          r.isDashed = rel.is_dashed
                    )
                    FOREACH (x IN CASE WHEN create_in THEN [1] ELSE [] END |
                      MERGE (to)-[r:RELATES_TO]->(from)
                      SET r.type = rel.rel_type,
                          r.direction = 'in',
                          r.fromCardinality = rel.to_cardinality,
                          r.toCardinality = rel.from_cardinality,
                          r.role = rel.role,
                          r.name = rel.name,
                          r.relationshipType = rel.relationship_type,
                          r.order = rel.order,
                          r.isContainment = rel.is_containment,
                          r.isInheritance = rel.is_inheritance,
                          r.isDashed = rel.is_dashed
                    )
                    """
                    session.run(query, relationships=relationships_list)
                    print(f"Created {len(relationships_list)} relationships")
        
        # Link schema block to entities
        with driver.session(database=neo4j_database) as session:
            session.run("""
                MATCH (sb:SchemaBlock {diagramId: $diagram_id})
                MATCH (e) WHERE e.specId = $spec_id
                MERGE (sb)-[:CONTAINS_ENTITY]->(e)
            """, spec_id=spec_id, diagram_id=diagram_id)
        
        print("Neo4j population completed successfully!")
    
    finally:
        driver.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate Neo4j from extracted diagram data")
    parser.add_argument("data_file", help="Path to extracted data file (JSON or YAML)")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name")
    parser.add_argument("--no-constraints", action="store_true", help="Skip creating constraints")
    parser.add_argument("--no-indexes", action="store_true", help="Skip creating indexes")
    parser.add_argument("--no-validate", action="store_true", help="Skip data validation")
    
    args = parser.parse_args()
    
    data = load_data(args.data_file)
    
    populate_neo4j(
        data=data,
        neo4j_uri=args.uri,
        neo4j_user=args.user,
        neo4j_password=args.password,
        neo4j_database=args.database,
        create_constraints_flag=not args.no_constraints,
        create_indexes_flag=not args.no_indexes,
        validate=not args.no_validate
    )
