"""CLI entry point for Tool Factory.

This script provides a command-line interface to the Tool Factory in
src/pydantic_ai_integration/tools/factory/

Usage:
    python scripts/generate_tools.py [tool_name] [--validate-only] [--verbose]
    
Examples:
    python scripts/generate_tools.py              # Generate all tools
    python scripts/generate_tools.py echo_tool    # Generate specific tool
    python scripts/generate_tools.py --validate-only  # Validate only
"""
import sys
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pydantic_ai_integration.tools.factory import generate_tools_cli

if __name__ == "__main__":
    generate_tools_cli()
