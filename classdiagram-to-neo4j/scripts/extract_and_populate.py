#!/usr/bin/env python3
"""
Convenience script that combines extraction and Neo4j population in one step.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_diagram import extract_diagram
from populate_neo4j import populate_neo4j, validate_extracted_data


def extract_and_populate(
    image_path: str,
    neo4j_uri: str = None,
    neo4j_user: str = None,
    neo4j_password: str = None,
    neo4j_database: str = "neo4j",
    provider: str = "openai",
    model: str = None,
    save_intermediate: bool = True,
    intermediate_path: str = None,
    validate: bool = True
):
    """
    Extract diagram and populate Neo4j in one step.
    
    Args:
        image_path: Path to diagram image
        neo4j_uri: Neo4j URI (defaults to env var or localhost)
        neo4j_user: Neo4j username (defaults to env var or "neo4j")
        neo4j_password: Neo4j password (required)
        neo4j_database: Neo4j database name
        provider: Vision provider ("openai" or "anthropic")
        model: Model name (uses default if not provided)
        save_intermediate: Whether to save extracted data
        intermediate_path: Path to save intermediate data
    """
    # Get Neo4j settings from args or env
    neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_password:
        raise ValueError("Neo4j password required. Provide as argument or set NEO4J_PASSWORD env var.")
    
    # Step 1: Extract diagram
    print(f"Extracting diagram: {image_path}")
    intermediate_path = intermediate_path or f"{Path(image_path).stem}_extracted.json"
    
    data = extract_diagram(
        image_path=image_path,
        provider=provider,
        output_format="json",
        output_path=intermediate_path if save_intermediate else None,
        model=model
    )
    
    print(f"Extracted {len(data.get('entities', {}))} entities")
    print(f"Extracted {len(data.get('relationships', []))} relationships")
    
    if save_intermediate:
        print(f"Intermediate data saved to: {intermediate_path}")
    
    # Validate if requested
    if validate:
        from populate_neo4j import validate_extracted_data
        errors = validate_extracted_data(data)
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
            raise ValueError("Data validation failed. Fix errors or use --no-validate to skip.")
        print("Data validation passed")
    
    # Step 2: Populate Neo4j
    print(f"Populating Neo4j: {neo4j_uri}")
    populate_neo4j(
        data=data,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        neo4j_database=neo4j_database,
        validate=validate
    )
    
    print("Done!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract diagram and populate Neo4j")
    parser.add_argument("image_path", help="Path to diagram image")
    parser.add_argument("--uri", help="Neo4j URI (defaults to NEO4J_URI env var)")
    parser.add_argument("--user", help="Neo4j username (defaults to NEO4J_USER env var)")
    parser.add_argument("--password", help="Neo4j password (defaults to NEO4J_PASSWORD env var)")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai", help="Vision provider")
    parser.add_argument("--model", help="Model name (uses default if not provided)")
    parser.add_argument("--no-save", action="store_true", help="Don't save intermediate extracted data")
    parser.add_argument("--intermediate", help="Path to save intermediate extracted data")
    parser.add_argument("--no-validate", action="store_true", help="Skip data validation")
    
    args = parser.parse_args()
    
    extract_and_populate(
        image_path=args.image_path,
        neo4j_uri=args.uri,
        neo4j_user=args.user,
        neo4j_password=args.password,
        neo4j_database=args.database,
        provider=args.provider,
        model=args.model,
        save_intermediate=not args.no_save,
        intermediate_path=args.intermediate,
        validate=not args.no_validate
    )

