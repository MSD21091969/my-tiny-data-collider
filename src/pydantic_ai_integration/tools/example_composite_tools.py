"""
Example composite tools demonstrating tool composition patterns.

This module provides sample composite tools that chain multiple tools
together to accomplish higher-level tasks.
"""

from typing import Dict, Any
import logging

from ..tool_decorator import register_composite_tool
from ..dependencies import MDSContext
from ..chains import ChainExecutor, ChainExecutionMode

logger = logging.getLogger(__name__)


# =============================================================================
# Data Enrichment Chain
# =============================================================================

# Register a composite tool that enriches data through multiple steps
DATA_ENRICHMENT_CHAIN = register_composite_tool(
    name="data_enrichment_chain",
    description="Validates input data, fetches metadata, and enriches with context",
    tool_chain=[
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "validation_step"
            }
        },
        {
            "tool_name": "another_example_tool",
            "parameters": {
                "name": "enrichment_step",
                "count": 2
            }
        },
        {
            "tool_name": "advanced_tool",
            "parameters": {
                "input_data": {"source": "composite_chain"},
                "options": {"enrich": True}
            }
        }
    ],
    category="data_processing",
    execution_mode="sequential",
    pass_results=True,
    stop_on_error=True,
    timeout_seconds=180
)


# =============================================================================
# Validation Chain
# =============================================================================

VALIDATION_CHAIN = register_composite_tool(
    name="validation_chain",
    description="Performs multi-level validation of input data",
    tool_chain=[
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "schema_validation"
            }
        },
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "business_rules_validation"
            }
        },
        {
            "tool_name": "another_example_tool",
            "parameters": {
                "name": "final_validation",
                "count": 1
            }
        }
    ],
    category="validation",
    execution_mode="sequential",
    pass_results=True,
    stop_on_error=True,
    timeout_seconds=120
)


# =============================================================================
# Parallel Processing Chain
# =============================================================================

PARALLEL_PROCESSING_CHAIN = register_composite_tool(
    name="parallel_processing_chain",
    description="Executes multiple independent processing tasks concurrently",
    tool_chain=[
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "process_batch_1"
            }
        },
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "process_batch_2"
            }
        },
        {
            "tool_name": "another_example_tool",
            "parameters": {
                "name": "process_batch_3",
                "count": 3
            }
        }
    ],
    category="batch_processing",
    execution_mode="parallel",
    pass_results=False,
    stop_on_error=False,
    timeout_seconds=300
)


# =============================================================================
# Analysis Pipeline
# =============================================================================

ANALYSIS_PIPELINE = register_composite_tool(
    name="analysis_pipeline",
    description="Complete analysis pipeline with data gathering, processing, and reporting",
    tool_chain=[
        {
            "tool_name": "example_tool",
            "parameters": {
                "name": "gather_data"
            }
        },
        {
            "tool_name": "advanced_tool",
            "parameters": {
                "input_data": {"stage": "processing"},
                "options": {"analyze": True}
            }
        },
        {
            "tool_name": "another_example_tool",
            "parameters": {
                "name": "generate_report",
                "count": 1
            }
        }
    ],
    category="analysis",
    execution_mode="sequential",
    pass_results=True,
    stop_on_error=True,
    timeout_seconds=240
)


# =============================================================================
# Helper Functions for Executing Composite Tools
# =============================================================================

async def execute_composite_tool(
    context: MDSContext,
    composite_tool_name: str,
    override_parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute a registered composite tool.
    
    Args:
        context: MDSContext for execution
        composite_tool_name: Name of the composite tool to execute
        override_parameters: Optional parameters to override in the tool chain
        
    Returns:
        Execution results
    """
    from ..tool_decorator import get_composite_tool
    
    # Get the composite tool definition
    composite_tool = get_composite_tool(composite_tool_name)
    if not composite_tool:
        return {
            "error": f"Composite tool '{composite_tool_name}' not found",
            "success": False
        }
    
    # Check if enabled
    if not composite_tool.enabled:
        return {
            "error": f"Composite tool '{composite_tool_name}' is not enabled",
            "success": False
        }
    
    # Apply parameter overrides if provided
    tool_chain = composite_tool.tool_chain
    if override_parameters:
        tool_chain = _apply_parameter_overrides(tool_chain, override_parameters)
    
    # Create executor
    executor = ChainExecutor(context)
    
    # Determine execution mode
    mode = (ChainExecutionMode.PARALLEL 
            if composite_tool.execution_mode == "parallel" 
            else ChainExecutionMode.SEQUENTIAL)
    
    # Execute the chain
    results = await executor.execute_chain(
        tools=tool_chain,
        mode=mode,
        chain_name=composite_tool_name,
        stop_on_error=composite_tool.stop_on_error,
        pass_results=composite_tool.pass_results
    )
    
    return results


def _apply_parameter_overrides(
    tool_chain: list,
    overrides: Dict[str, Any]
) -> list:
    """
    Apply parameter overrides to a tool chain.
    
    Args:
        tool_chain: Original tool chain
        overrides: Parameters to override (key format: "tool_name.param_name")
        
    Returns:
        Modified tool chain with overrides applied
    """
    modified_chain = []
    
    for tool_def in tool_chain:
        modified_tool = tool_def.copy()
        tool_name = tool_def["tool_name"]
        
        # Apply overrides for this tool
        for override_key, override_value in overrides.items():
            if override_key.startswith(f"{tool_name}."):
                param_name = override_key.split(".", 1)[1]
                if "parameters" not in modified_tool:
                    modified_tool["parameters"] = {}
                modified_tool["parameters"][param_name] = override_value
        
        modified_chain.append(modified_tool)
    
    return modified_chain


# =============================================================================
# Logging
# =============================================================================

logger.info(f"Registered {len([DATA_ENRICHMENT_CHAIN, VALIDATION_CHAIN, PARALLEL_PROCESSING_CHAIN, ANALYSIS_PIPELINE])} example composite tools")
