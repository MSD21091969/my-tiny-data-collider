"""
Quick Model Viewer - View Pydantic models without importing
"""

import ast
import sys
from pathlib import Path


def view_model_file(file_path):
    """Parse and display models from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        models_found = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a model (inherits from BaseModel)
                is_model = any(
                    (isinstance(base, ast.Name) and base.id == "BaseModel") for base in node.bases
                )

                if is_model:
                    models_found.append(node.name)
                    print(f"\n{'=' * 70}")
                    print(f"[MODEL] {node.name}")
                    print(f"{'=' * 70}")

                    # Get docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        print(f"\n{docstring}\n")

                    # Find fields
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id

                            # Get field type
                            if item.annotation:
                                field_type = ast.unparse(item.annotation)
                            else:
                                field_type = "Any"

                            # Check if Field is used
                            description = ""
                            required = True

                            if item.value:
                                value_str = ast.unparse(item.value)
                                if "Field(" in value_str:
                                    # Try to extract description
                                    if "description=" in value_str:
                                        desc_start = value_str.find('description="') + 13
                                        desc_end = value_str.find('"', desc_start)
                                        if desc_end > desc_start:
                                            description = value_str[desc_start:desc_end]

                                    if "default=" in value_str or "default_factory" in value_str:
                                        required = False
                                    if "..." not in value_str:
                                        required = False
                                else:
                                    required = False

                            fields.append((field_name, field_type, required, description))

                    # Display fields
                    print(f"Fields ({len(fields)}):")
                    for field_name, field_type, required, description in fields:
                        req_marker = "[REQ]" if required else "[OPT]"
                        print(f"  {req_marker} {field_name}: {field_type}")
                        if description:
                            print(f"       -> {description}")

                    print()

        return models_found

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def main():
    print("\n" + "=" * 70)
    print("QUICK MODEL VIEWER")
    print("=" * 70)

    if len(sys.argv) > 1:
        # View specific file
        file_path = Path(sys.argv[1])
        if file_path.exists():
            models = view_model_file(file_path)
            print(f"\n{'=' * 70}")
            print(f"Found {len(models)} model(s): {', '.join(models)}")
        else:
            print(f"File not found: {file_path}")
    else:
        # Show available model files
        print("\nAvailable model files:\n")

        project_root = Path(__file__).parent
        model_dir = project_root / "src" / "pydantic_models"

        if model_dir.exists():
            categories = {
                "canonical": "Core domain models",
                "payloads": "API request/response models",
                "operations": "Operation-specific models",
                "workspace": "Google Workspace models",
                "views": "Summary/view models",
            }

            for category, desc in categories.items():
                cat_dir = model_dir / category
                if cat_dir.exists():
                    files = list(cat_dir.glob("*.py"))
                    if files:
                        print(f"\n  [{category.upper()}] - {desc}")
                        for f in sorted(files):
                            if f.name != "__init__.py":
                                print(f"    - {f.name}")

            print("\n" + "=" * 70)
            print("Usage:")
            print(f"  python {Path(__file__).name} <file_path>")
            print("\nExample:")
            print(f"  python {Path(__file__).name} src/pydantic_models/canonical/casefile.py")
        else:
            print("Model directory not found!")


if __name__ == "__main__":
    main()
