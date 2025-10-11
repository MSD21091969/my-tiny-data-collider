"""Import all generated tool modules for registration."""

from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# Ensure project root is on sys.path so ``src`` imports resolve
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def import_all_generated_modules() -> Tuple[int, List[Tuple[str, str, str]]]:
    """Import every module in ``tools.generated``.

    Returns the number of successfully imported modules and a list of
    ``(module_name, exception_class, message)`` tuples for failures.
    """

    try:
        import src.pydantic_ai_integration.tools.generated as generated
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to import generated package: {exc}") from exc

    errors: List[Tuple[str, str, str]] = []
    count = 0
    for _finder, name, _ispkg in pkgutil.walk_packages(
        generated.__path__, generated.__name__ + "."
    ):
        try:
            importlib.import_module(name)
            count += 1
        except Exception as exc:  # pragma: no cover
            errors.append((name, exc.__class__.__name__, str(exc)))

    return count, errors


def _format_report(count: int, errors: Iterable[Tuple[str, str, str]]) -> str:
    lines = [f"Imported {count} generated modules"]
    errs = list(errors)
    if errs:
        lines.append("Errors while importing:")
        for name, exc_cls, message in errs:
            lines.append(f"  - {name}: {exc_cls}: {message}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    report = _format_report(*import_all_generated_modules())
    print(report)
