"""
Model Export Verification Tool
Ensures all Pydantic models are being exported correctly.
"""

import ast
from pathlib import Path
from collections import defaultdict


def find_all_models(base_dir):
    """Find all BaseModel classes in the codebase."""
    models_by_file = defaultdict(list)

    for py_file in Path(base_dir).rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    is_model = any(
                        (isinstance(base, ast.Name) and base.id == "BaseModel")
                        for base in node.bases
                    )

                    if is_model:
                        rel_path = py_file.relative_to(base_dir)
                        models_by_file[str(rel_path)].append(node.name)

        except Exception as e:
            print(f"Error parsing {py_file}: {e}")

    return models_by_file


def verify_exports(project_root):
    """Verify all models are exported."""
    print("=" * 70)
    print("MODEL EXPORT VERIFICATION")
    print("=" * 70)

    # Find all models in source
    models_dir = Path(project_root) / "src" / "pydantic_models"
    all_models = find_all_models(models_dir)

    # Count by category
    categories = defaultdict(lambda: {"files": 0, "models": 0})

    for file_path, models in all_models.items():
        parts = Path(file_path).parts
        if len(parts) > 0:
            category = parts[0]
        else:
            category = "root"

        categories[category]["files"] += 1
        categories[category]["models"] += len(models)

    print("\nModels found in source code:")
    print("-" * 70)

    total_files = 0
    total_models = 0

    for category in sorted(categories.keys()):
        info = categories[category]
        print(f"  {category:15} {info['files']:3} files, {info['models']:3} models")
        total_files += info["files"]
        total_models += info["models"]

    print("-" * 70)
    print(f"  {'TOTAL':15} {total_files:3} files, {total_models:3} models")

    # Check exports
    exports_dir = Path(project_root) / "model_exports"
    if exports_dir.exists():
        csv_files = list(exports_dir.rglob("*.csv"))
        # Exclude index files
        model_csvs = [f for f in csv_files if "index" not in f.name.lower()]

        print(f"\nCSV files exported: {len(model_csvs)}")

        if len(model_csvs) != total_models:
            print(f"\nWARNING: Mismatch detected!")
            print(f"  Source models: {total_models}")
            print(f"  Exported CSVs: {len(model_csvs)}")
            print(f"  Difference: {total_models - len(model_csvs)}")
    else:
        print("\nNo exports directory found. Run export script first.")

    # Show details
    print("\n" + "=" * 70)
    print("DETAILED MODEL LIST")
    print("=" * 70)

    for file_path in sorted(all_models.keys()):
        models = all_models[file_path]
        print(f"\n{file_path}")
        for model in models:
            print(f"  - {model}")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

    return total_models, len(model_csvs) if exports_dir.exists() else 0


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    source_count, export_count = verify_exports(project_root)

    if source_count == export_count:
        print("\nStatus: OK - All models exported")
    else:
        print(f"\nStatus: MISMATCH - {source_count} source models, {export_count} exported")
