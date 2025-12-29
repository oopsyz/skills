#!/usr/bin/env python3
"""
Extract entities, properties, and relationships from UML class diagram images.
Uses vision models to analyze diagrams and extract structured data.
"""

from __future__ import annotations

import json
import os
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None

try:
    import yaml
except ImportError:
    yaml = None


def encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_with_openai(image_path: str, api_key: Optional[str] = None, model: str = "gpt-4-vision-preview") -> Dict[str, Any]:
    """Extract diagram data using OpenAI Vision API."""
    if OpenAI is None:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
    
    client = OpenAI(api_key=api_key)
    
    base64_image = encode_image(image_path)
    
    prompt = """Analyze this UML class diagram and extract:
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

Be thorough and extract all visible information. If cardinality is not shown, use "0..*" as default."""
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=4000,
        temperature=0.1
    )
    
    content = response.choices[0].message.content
    
    # Try to extract JSON from response
    try:
        # Look for JSON code block
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        else:
            json_str = content.strip()
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, return raw content for manual review
        return {
            "error": "Failed to parse JSON from response",
            "raw_content": content,
            "entities": {},
            "relationships": []
        }


def extract_with_anthropic(image_path: str, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229") -> Dict[str, Any]:
    """Extract diagram data using Anthropic Claude Vision API."""
    if Anthropic is None:
        raise ImportError("anthropic package is required. Install with: pip install anthropic")
    
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
    
    client = Anthropic(api_key=api_key)
    
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    prompt = """Analyze this UML class diagram and extract:
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

Be thorough and extract all visible information. If cardinality is not shown, use "0..*" as default."""
    
    message = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.b64encode(image_data).decode("utf-8")
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    content = message.content[0].text
    
    # Try to extract JSON from response
    try:
        # Look for JSON code block
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        else:
            json_str = content.strip()
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse JSON from response",
            "raw_content": content,
            "entities": {},
            "relationships": []
        }


def normalize_relationship_type(from_entity: str, to_entity: str, relationship_name: Optional[str] = None) -> str:
    """Normalize relationship type name to snake_case."""
    if relationship_name:
        # Convert to snake_case
        normalized = relationship_name.lower().replace(" ", "_").replace("-", "_")
        return normalized
    
    # Generate default name from entity names
    to_lower = to_entity.lower()
    if to_lower.endswith("ref"):
        return f"has_{to_lower}"
    elif to_lower.startswith(from_entity.lower()):
        return f"has_{to_lower.replace(from_entity.lower(), '').strip('_')}"
    else:
        return f"relates_to_{to_lower}"


def add_provenance(data: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Add provenance metadata to extracted data."""
    from datetime import datetime
    
    if "meta" not in data:
        data["meta"] = {}
    
    data["meta"]["source"] = source
    data["meta"]["extracted_at"] = datetime.utcnow().isoformat() + "Z"
    data["meta"]["extraction_tool"] = "classdiagram-to-neo4j"
    
    return data


def extract_diagram(
    image_path: str,
    provider: str = "openai",
    output_format: str = "json",
    output_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract diagram data from image.
    
    Args:
        image_path: Path to diagram image
        provider: Vision provider ("openai" or "anthropic")
        output_format: Output format ("json" or "yaml")
        output_path: Optional path to save output
        api_key: Optional API key (uses env var if not provided)
        model: Optional model name (uses default if not provided)
    
    Returns:
        Extracted diagram data as dictionary
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Select provider and model
    if provider == "openai":
        model = model or "gpt-4-vision-preview"
        data = extract_with_openai(image_path, api_key, model)
    elif provider == "anthropic":
        model = model or "claude-3-opus-20240229"
        data = extract_with_anthropic(image_path, api_key, model)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'anthropic'")
    
    # Normalize relationship types
    if "relationships" in data:
        for rel in data["relationships"]:
            if "type" not in rel or not rel["type"]:
                rel["type"] = normalize_relationship_type(
                    rel.get("from", ""),
                    rel.get("to", ""),
                    rel.get("name")
                )
    
    # Add provenance
    data = add_provenance(data, image_path)
    
    # Save output if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_format == "yaml":
            if yaml is None:
                raise ImportError("pyyaml package required for YAML output. Install with: pip install pyyaml")
            with open(output_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
    
    return data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract data from UML class diagram images")
    parser.add_argument("image_path", help="Path to diagram image")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai", help="Vision provider")
    parser.add_argument("--model", help="Model name (uses default if not provided)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    parser.add_argument("--api-key", help="API key (uses env var if not provided)")
    
    args = parser.parse_args()
    
    data = extract_diagram(
        image_path=args.image_path,
        provider=args.provider,
        output_format=args.format,
        output_path=args.output,
        api_key=args.api_key,
        model=args.model
    )
    
    if args.output:
        print(f"Extracted data saved to {args.output}")
    else:
        print(json.dumps(data, indent=2))

