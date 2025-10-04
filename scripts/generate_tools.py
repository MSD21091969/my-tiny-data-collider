"""Generate tools from YAML configurations.

Usage:
    python generate_tools.py                          # Generate all tools
    python generate_tools.py gmail_send_message       # Generate specific tool
    python generate_tools.py --validate-only          # Validate only
"""
import sys
from pathlib import Path

# Add project root to sys.path so src/ imports resolve when invoked from anywhere
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
# Ensure project root is first so local src/ takes precedence over any installed package
sys.path.insert(0, str(project_root))

from src.pydantic_ai_integration.tools.factory import ToolFactory, generate_tools_cli

if __name__ == "__main__":
    generate_tools_cli()
