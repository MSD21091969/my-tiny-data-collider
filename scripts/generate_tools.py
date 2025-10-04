"""Generate tools from YAML configurations.

Usage:
    python generate_tools.py                          # Generate all tools
    python generate_tools.py gmail_send_message       # Generate specific tool
    python generate_tools.py --validate-only          # Validate only
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pydantic_ai_integration.tools.factory import ToolFactory, generate_tools_cli

if __name__ == "__main__":
    generate_tools_cli()
