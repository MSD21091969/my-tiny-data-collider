#!/usr/bin/env python3
"""
Generate field mapping documentation for data transformations.
Analyzes mapper files and documents field transformations.
"""

from pathlib import Path


def analyze_mappers():
    """Document field mappings from mapper files."""

    print("# Field Mapping Documentation\n")

    mapper_dir = Path("src/pydantic_models/mappers")

    if not mapper_dir.exists():
        print("No mapper directory found")
        return

    # List all mapper files
    mapper_files = sorted(mapper_dir.glob("*_mapper.py"))

    print(f"Found {len(mapper_files)} mapper files:\n")

    for mapper_file in mapper_files:
        mapper_name = mapper_file.stem.replace("_mapper", "")
        print(f"## {mapper_name.replace('_', ' ').title()}")
        print(f"**File:** `{mapper_file.relative_to(Path.cwd())}`\n")

        # Read file and extract function signatures
        with open(mapper_file) as f:
            content = f.read()

            # Find function definitions
            for line in content.split("\n"):
                if line.strip().startswith("def "):
                    func_sig = line.strip()
                    print(f"- `{func_sig[4 : func_sig.find(':')]}`")

        print()


if __name__ == "__main__":
    analyze_mappers()
