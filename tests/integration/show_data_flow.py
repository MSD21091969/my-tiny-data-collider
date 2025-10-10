"""
Demonstrate enhanced data flow logging.
Shows all data being handled at each step of tool execution.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Configure logging to show all INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from pydantic_ai_integration.tool_decorator import register_tools_from_yaml, get_tool_definition
from pydantic_ai_integration.dependencies import MDSContext
from tool_sessionservice.service import ToolSessionService


async def main():
    """Run a single tool with enhanced data logging."""
    
    print("=" * 80)
    print("ENHANCED DATA FLOW DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Load tools
    print("Loading tools from YAML...")
    register_tools_from_yaml()
    print()
    
    # Get a tool
    tool_name = "create_casefile_tool"
    tool_def = get_tool_definition(tool_name)
    
    if not tool_def:
        print(f"Tool '{tool_name}' not found!")
        return
    
    print(f"Found tool: {tool_name}")
    print(f"Description: {tool_def.description}")
    print()
    
    # Create context
    print("Creating execution context...")
    session_service = ToolSessionService()
    user_id = "user_test_123"
    casefile_id = "cf_test_456"
    session_id = session_service.new_tool_session_id(user_id=user_id, casefile_id=casefile_id)
    
    ctx = MDSContext(
        user_id=user_id,
        session_id=session_id,
        casefile_id=casefile_id
    )
    print(f"Context created: {ctx}")
    print()
    
    # Execute tool with parameters
    print("=" * 80)
    print("EXECUTING TOOL WITH ENHANCED LOGGING")
    print("=" * 80)
    print()
    
    result = await tool_def.implementation(
        ctx,
        title="Demo Casefile - Data Flow Test",
        description="This demonstrates all data being logged at each step",
        tags=["demo", "data-flow", "logging"],
        timeout_seconds=30,
        dry_run=False  # Set to True to see dry run mode
    )
    
    print()
    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print()
    
    import json
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
