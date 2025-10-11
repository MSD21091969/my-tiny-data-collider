#!/usr/bin/env python3
"""
Generate comprehensive Pydantic model documentation.
Reads models_inventory_v1.yaml and creates markdown documentation.
"""

import yaml
from pathlib import Path


def generate_model_docs():
    """Generate model documentation from inventory."""

    # Read inventory
    inventory_path = Path("config/models_inventory_v1.yaml")
    with open(inventory_path) as f:
        inventory = yaml.safe_load(f)

    print(f"# Pydantic Models Documentation")
    print(f"Generated from: {inventory['version']}")
    print(f"Last updated: {inventory['generated_at']}\n")

    # Process each layer
    for layer_name, layer_data in inventory["layers"].items():
        print(f"## {layer_name.replace('_', ' ').title()}")
        print(f"{layer_data['description']}\n")

        # List models in this layer
        for model in layer_data.get("models", []):
            print(f"### {model['name']}")
            print(f"- **File:** `{model['file']}`")
            print(f"- **Description:** {model['description']}")
            print()


if __name__ == "__main__":
    generate_model_docs()
