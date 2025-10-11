"""
Export Pydantic Models to Excel Spreadsheets
Creates tangible, analyzable files from your model definitions
"""

import ast
import csv
from pathlib import Path
from datetime import datetime


def parse_model_file(file_path):
    """Extract model information from a Python file."""
    models = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            is_model = any(
                (isinstance(base, ast.Name) and base.id == "BaseModel") for base in node.bases
            )

            if is_model:
                model_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "No description",
                    "fields": [],
                }

                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_name = item.target.id
                        field_type = ast.unparse(item.annotation) if item.annotation else "Any"

                        required = True
                        description = ""
                        default_value = ""

                        if item.value:
                            value_str = ast.unparse(item.value)

                            # Check if Field() is used
                            if "Field(" in value_str:
                                # Extract description
                                if 'description="' in value_str:
                                    desc_start = value_str.find('description="') + 13
                                    desc_end = value_str.find('"', desc_start)
                                    if desc_end > desc_start:
                                        description = value_str[desc_start:desc_end]

                                # Check if required
                                if "default=" in value_str or "default_factory" in value_str:
                                    required = False
                                    if (
                                        "default=" in value_str
                                        and "default_factory" not in value_str
                                    ):
                                        def_start = value_str.find("default=") + 8
                                        def_part = value_str[def_start : def_start + 50]
                                        default_value = def_part.split(",")[0].split(")")[0]

                                if "..." not in value_str:
                                    required = False
                            else:
                                required = False
                                default_value = value_str[:50]

                        model_info["fields"].append(
                            {
                                "name": field_name,
                                "type": field_type,
                                "required": required,
                                "description": description,
                                "default": default_value,
                            }
                        )

                models.append(model_info)

    return models


def export_to_csv(models, output_dir, category):
    """Export models to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a master index CSV
    index_path = output_dir / f"{category}_index.csv"
    with open(index_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Model Name", "Description", "Field Count", "Required Fields", "Optional Fields"]
        )

        for model in models:
            required_count = sum(1 for f in model["fields"] if f["required"])
            optional_count = len(model["fields"]) - required_count
            writer.writerow(
                [
                    model["name"],
                    model["docstring"][:100],
                    len(model["fields"]),
                    required_count,
                    optional_count,
                ]
            )

    print(f"Created: {index_path}")

    # Create detailed CSV for each model
    for model in models:
        model_path = output_dir / f"{category}_{model['name']}.csv"
        with open(model_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Field Name", "Type", "Required", "Description", "Default Value"])

            for field in model["fields"]:
                writer.writerow(
                    [
                        field["name"],
                        field["type"],
                        "YES" if field["required"] else "NO",
                        field["description"],
                        field["default"],
                    ]
                )

        print(f"Created: {model_path}")


def main():
    """Main export function."""
    print("=" * 70)
    print("EXPORTING MODELS TO SPREADSHEETS")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent.parent
    model_dir = project_root / "src" / "pydantic_models"
    output_dir = project_root / "model_exports"

    # Auto-discover all subdirectories with Python files (systematic approach)
    categories = {}
    for subdir in sorted(model_dir.iterdir()):
        if subdir.is_dir() and subdir.name != "__pycache__":
            # Check if directory has any .py files (excluding __init__.py)
            py_files = [f for f in subdir.glob("*.py") if f.name != "__init__.py"]
            if py_files:
                categories[subdir.name] = f"Models from {subdir.name}/"

    print(f"Auto-discovered {len(categories)} categories")
    print()

    total_models = 0
    total_files = 0

    for category in sorted(categories.keys()):
        cat_dir = model_dir / category
        description = categories[category]

        print(f"\n[{category.upper()}] - {description}")
        print("-" * 70)

        all_models = []
        files = list(cat_dir.glob("*.py"))

        for file_path in sorted(files):
            if file_path.name == "__init__.py":
                continue

            print(f"  Processing: {file_path.name}")
            models = parse_model_file(file_path)

            if models:
                all_models.extend(models)
                total_files += 1

        if all_models:
            export_to_csv(all_models, output_dir / category, category)
            total_models += len(all_models)
            print(f"  Exported {len(all_models)} models")

    print("\n" + "=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)
    print(f"\nTotal: {total_models} models from {total_files} files")
    print(f"Output directory: {output_dir}")
    print("\nYou can now open these CSV files in Excel, Google Sheets, or any")
    print("spreadsheet application for analysis!")
    print("\nFiles created:")
    print("  - *_index.csv - Overview of all models in each category")
    print("  - *_ModelName.csv - Detailed field information for each model")


if __name__ == "__main__":
    main()
