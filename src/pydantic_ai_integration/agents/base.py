"""
Base agent factory and agent definitions.
"""

from typing import Dict, Any
import logging
import inspect

# This is a placeholder for the actual Pydantic AI Agent class
# In a real implementation, you would import this from the Pydantic AI package
class Agent:
    """Placeholder for Pydantic AI Agent class."""
    
    def __init__(self, name: str, instructions: str = None):
        self.name = name
        self.instructions = instructions
        self.tools = {}
        
    async def run(self, prompt: str, deps=None):
        """Run the agent with a prompt."""
        # This would call the actual LLM in a real implementation
        
        # For the example implementation, try to match a tool name in the prompt
        # and execute it directly
        tool_name = None
        for name in self.tools:
            if name.lower() in prompt.lower():
                tool_name = name
                break
                
        if tool_name and tool_name in self.tools:
            try:
                # For demonstration, extract simple parameters
                # In a real agent, this would be done by the LLM
                import re
                import json
                
                # Try to find JSON-like parameters in the prompt
                json_match = re.search(r'{.*}', prompt)
                if json_match:
                    try:
                        params = json.loads(json_match.group(0))
                        logging.info(f"Extracted parameters from prompt: {params}")
                    except Exception as e:
                        logging.warning(f"Failed to parse JSON parameters: {e}")
                        params = {}
                else:
                    params = {}
                
                # Execute the tool
                tool_func = self.tools[tool_name]
                sig = inspect.signature(tool_func)
                
                # Log what we're about to execute for debugging
                logging.info(f"Executing tool {tool_name} with params: {params}")
                logging.info(f"Tool signature: {sig}")
                
                # Only use parameters that exist in the tool's signature
                valid_params = {}
                for param_name, param in sig.parameters.items():
                    if param_name == 'ctx' or param_name == 'context':
                        continue  # Skip context parameter
                    
                    if param_name in params:
                        valid_params[param_name] = params[param_name]
                
                # Special case handling for our example tools
                if tool_name == "example_tool" and "value" not in valid_params:
                    # Add the required parameter with a default value
                    valid_params["value"] = 42
                
                if tool_name == "another_example_tool":
                    if "name" not in valid_params:
                        valid_params["name"] = "Default User"
                    if "count" not in valid_params:
                        valid_params["count"] = 1
                        
                logging.info(f"Using valid parameters for {tool_name}: {valid_params}")
                
                if 'ctx' in sig.parameters or 'context' in sig.parameters:
                    # Tool expects context as first parameter
                    result = await tool_func(deps, **valid_params)
                else:
                    # Tool doesn't expect context
                    result = await tool_func(**valid_params)
                    
                return AgentResult(result)
            except Exception as e:
                logging.exception(f"Error executing tool {tool_name}")
                return AgentResult({"error": str(e)})
        
        # If no matching tool, return a generic response
        tools_str = ", ".join(self.tools.keys())
        return AgentResult({
            "message": f"Agent {self.name} processed: {prompt}",
            "available_tools": tools_str
        })
        
    def tool(self, func):
        """Register a function as a tool."""
        self.tools[func.__name__] = func
        return func
        
    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())

class AgentResult:
    """Result from an agent run."""
    
    def __init__(self, output: Dict[str, Any]):
        self.output = output

# Registry of agents by toolset
_AGENTS = {}

def register_agent(toolset_name: str, agent: Agent):
    """Register an agent for a toolset."""
    _AGENTS[toolset_name] = agent
    return agent

def get_agent_for_toolset(toolset_name: str) -> Agent:
    """Get the appropriate agent for a toolset."""
    # First check if we have a direct match
    if toolset_name in _AGENTS:
        return _AGENTS[toolset_name]
        
    # Then check for a partial match
    for name in _AGENTS:
        if name.lower() in toolset_name.lower() or toolset_name.lower() in name.lower():
            return _AGENTS[name]
            
    # Fall back to default
    logging.warning(f"No agent registered for toolset '{toolset_name}', using default")
    return _AGENTS.get("default", Agent("default", "Default agent instructions"))

# Create and register the default agent
default_agent = register_agent("default", Agent(
    name="default",
    instructions="""
    You are an assistant that helps users execute tools and analyze data.
    Follow these guidelines:
    1. Execute tools as requested
    2. Provide clear explanations of results
    3. Ask for clarification when parameters are missing
    """
))

def import_tools():
    """
    Import all tool modules to register their tools.
    
    This function uses lazy imports to avoid circular dependencies.
    Tools import default_agent from this module, so we only import
    tools AFTER default_agent is defined.
    """
    try:
        # Try to import example tools
        try:
            from ..tools import example_tools  # noqa: F401
            logging.info("Imported example_tools successfully")
        except ImportError as e:
            logging.warning(f"Could not import example_tools: {e}")
        
        # Try to import unified example tools
        try:
            from ..tools import unified_example_tools  # noqa: F401
            logging.info("Imported unified_example_tools successfully")
        except ImportError as e:
            logging.warning(f"Could not import unified_example_tools: {e}")
            
        # Try to import agent-aware tools
        try:
            from ..tools import agent_aware_tools  # noqa: F401
            logging.info("Imported agent_aware_tools successfully")
        except ImportError as e:
            logging.warning(f"Could not import agent_aware_tools: {e}")
            
    except Exception as e:
        logging.exception(f"Error importing tools: {e}")

# Register specific tool names to use the default agent
register_agent("example_tool", default_agent)
register_agent("another_example_tool", default_agent)
register_agent("advanced_tool", default_agent)
register_agent("hello_world", default_agent)
register_agent("echo_data", default_agent)
register_agent("chain_aware_tool", default_agent)
register_agent("context_enrichment_tool", default_agent)

# Import tools AFTER default_agent is defined to avoid circular imports
import_tools()