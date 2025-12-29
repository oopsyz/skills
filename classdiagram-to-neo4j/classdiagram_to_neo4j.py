"""Convenience imports and helpers for classdiagram-to-neo4j."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Union

from scripts.extract_diagram import extract_diagram
from scripts.populate_neo4j import populate_neo4j, load_data
from scripts.extract_and_populate import extract_and_populate

__all__ = [
    "extract_diagram",
    "extract_to_yaml",
    "populate_from_yaml",
    "batch_extract_and_populate",
    "extract_and_populate",
]


def extract_to_yaml(
    image_path: str,
    output_path: Optional[str] = None,
    **kwargs,
):
    """Extract diagram to YAML (wrapper around extract_diagram)."""
    return extract_diagram(
        image_path=image_path,
        output_format="yaml",
        output_path=output_path,
        **kwargs,
    )


def populate_from_yaml(
    yaml_data: Union[str, Path, dict],
    **kwargs,
):
    """Populate Neo4j from YAML data or a YAML/JSON file path."""
    if isinstance(yaml_data, (str, Path)):
        data = load_data(str(yaml_data))
    elif isinstance(yaml_data, dict):
        data = yaml_data
    else:
        raise TypeError("yaml_data must be a file path or a dict")

    return populate_neo4j(data=data, **kwargs)


def batch_extract_and_populate(
    diagrams: Iterable[str],
    merge_strategy: str = "update",
    **kwargs,
):
    """Process multiple diagrams in sequence."""
    if merge_strategy not in (None, "update"):
        raise ValueError("merge_strategy supports only 'update' in this version")

    results = []
    for diagram_path in diagrams:
        results.append(extract_and_populate(image_path=diagram_path, **kwargs))

    return results
