#!/usr/bin/env python3
"""
Example usage of classdiagram-to-neo4j extraction and population.
"""

import os
from pathlib import Path

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from extract_diagram import extract_diagram
from populate_neo4j import populate_neo4j, load_data


def example_basic_extraction():
    """Example: Extract diagram to JSON."""
    print("Example 1: Basic Extraction")
    print("-" * 50)
    
    image_path = "../../tmf620_images/page_034_img_001.png"
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        print("Please update the path to a valid diagram image.")
        return
    
    # Extract diagram
    data = extract_diagram(
        image_path=image_path,
        provider="openai",  # or "anthropic"
        output_format="json",
        output_path="extracted_productoffering.json"
    )
    
    print(f"Extracted {len(data.get('entities', {}))} entities")
    print(f"Extracted {len(data.get('relationships', []))} relationships")
    print(f"Data saved to extracted_productoffering.json")


def example_extract_and_populate():
    """Example: Extract diagram and populate Neo4j."""
    print("\nExample 2: Extract and Populate Neo4j")
    print("-" * 50)
    
    image_path = "../../tmf620_images/page_034_img_001.png"
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    # Step 1: Extract
    print("Step 1: Extracting diagram...")
    data = extract_diagram(
        image_path=image_path,
        provider="openai",
        output_format="json",
        output_path="extracted_data.json"
    )
    
    # Step 2: Populate Neo4j
    print("Step 2: Populating Neo4j...")
    populate_neo4j(
        data=data,
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password"),
        neo4j_database=os.getenv("NEO4J_DATABASE", "neo4j")
    )
    
    print("Done!")


def example_from_existing_data():
    """Example: Populate Neo4j from existing extracted data."""
    print("\nExample 3: Populate from Existing Data")
    print("-" * 50)
    
    data_file = "extracted_data.json"
    
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        print("Run example_basic_extraction() first.")
        return
    
    # Load and populate
    data = load_data(data_file)
    
    populate_neo4j(
        data=data,
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    print("Done!")


def example_batch_processing():
    """Example: Process multiple diagrams."""
    print("\nExample 4: Batch Processing")
    print("-" * 50)
    
    diagrams = [
        "../../tmf620_images/page_034_img_001.png",
        "../../tmf620_images/page_030_img_001.png",
    ]
    
    all_data = {
        "entities": {},
        "relationships": [],
        "meta": {
            "sources": [],
            "extracted_at": None
        }
    }
    
    for diagram_path in diagrams:
        if not os.path.exists(diagram_path):
            print(f"Skipping {diagram_path} (not found)")
            continue
        
        print(f"Processing {diagram_path}...")
        data = extract_diagram(
            image_path=diagram_path,
            provider="openai"
        )
        
        # Merge entities
        if "entities" in data:
            all_data["entities"].update(data["entities"])
        
        # Merge relationships
        if "relationships" in data:
            all_data["relationships"].extend(data["relationships"])
        
        # Track sources
        if "meta" in data and "source" in data["meta"]:
            all_data["meta"]["sources"].append(data["meta"]["source"])
    
    # Save merged data
    import json
    with open("merged_extracted_data.json", "w") as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Merged {len(all_data['entities'])} entities")
    print(f"Merged {len(all_data['relationships'])} relationships")
    print("Merged data saved to merged_extracted_data.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagram to Neo4j examples")
    parser.add_argument("--example", choices=["1", "2", "3", "4"], default="1", help="Example to run")
    
    args = parser.parse_args()
    
    if args.example == "1":
        example_basic_extraction()
    elif args.example == "2":
        example_extract_and_populate()
    elif args.example == "3":
        example_from_existing_data()
    elif args.example == "4":
        example_batch_processing()

