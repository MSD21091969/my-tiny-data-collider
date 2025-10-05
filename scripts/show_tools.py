"""Display registered Managed Tools and their metadata."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Tuple

# Ensure script directory and project root are importable
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
for path in (script_dir, project_root):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

try:  # Local import to avoid circular dependency when used as module
    from import_generated_tools import import_all_generated_modules
except ImportError:  # pragma: no cover
    import_all_generated_modules = None

from src.pydantic_ai_integration.tool_decorator import MANAGED_TOOLS


def _format_errors(errors: Iterable[Tuple[str, str, str]]) -> str:
    lines = []
    for module_name, exc_cls, message in errors:
        lines.append(f"  - {module_name}: {exc_cls}: {message}")
    return "\n".join(lines)


def main() -> None:
    if import_all_generated_modules is not None:
        imported, errors = import_all_generated_modules()
        print(f"Imported {imported} generated modules")
        if errors:
            print("Errors while importing:")
            print(_format_errors(errors))
            print("\nRegistry snapshot may be incomplete.\n")
    else:  # pragma: no cover
        print("Warning: import_generated_tools module unavailable; displaying current registry only.\n")

    print("=" * 70)
    print(f"REGISTERED TOOLS: {len(MANAGED_TOOLS)}")
    print("=" * 70)

    for index, (name, tool_def) in enumerate(sorted(MANAGED_TOOLS.items()), start=1):
        metadata = tool_def.metadata
        params_model = tool_def.params_model
        print(f"\n{index}. {name}")
        print(f"   Display Name: {metadata.display_name}")
        print(f"   Domain: {metadata.category}")
        print(f"   Description: {metadata.description}")
        print(f"   Permissions: {tool_def.business_rules.required_permissions}")
        print(f"   Requires Auth: {tool_def.business_rules.requires_auth}")
        print(f"   Timeout: {tool_def.business_rules.timeout_seconds}s")

        print("   Parameters:")
        for param_name, field_info in params_model.model_fields.items():
            required = "required" if field_info.is_required() else "optional"
            annotation = field_info.annotation
            type_name = getattr(annotation, "__name__", str(annotation))
            print(f"      - {param_name}: {type_name} ({required})")

        if tool_def.session_policies:
            print(f"   Session Required: {tool_def.session_policies.requires_active_session}")
        if tool_def.casefile_policies:
            print(f"   Requires Casefile: {tool_def.casefile_policies.requires_casefile}")

    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)


if __name__ == "__main__":  # pragma: no cover
    main()
