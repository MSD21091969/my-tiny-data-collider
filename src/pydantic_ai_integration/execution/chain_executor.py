"""Chain Executor for Composite Tools

Executes sequences of tools with conditional branching, error recovery,
and state management for tool composition workflows.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from ..dependencies import MDSContext
from ..tool_decorator import MANAGED_TOOLS


class ChainExecutionError(Exception):
    """Raised when chain execution fails."""
    def __init__(self, message: str, step_index: int, step_name: str, original_error: Exception = None):
        self.message = message
        self.step_index = step_index
        self.step_name = step_name
        self.original_error = original_error
        super().__init__(self.message)


class ChainExecutor:
    """Executes chains of tools with conditional logic and error handling.
    
    Supports:
    - Sequential tool execution
    - Conditional branching (on_success, on_failure)
    - State passing between steps
    - Error recovery strategies
    - Audit trail integration
    """
    
    def __init__(self, ctx: MDSContext):
        """Initialize chain executor.
        
        Args:
            ctx: MDSContext carrying user_id, session_id, casefile_id
        """
        self.ctx = ctx
        self.execution_history: List[Dict[str, Any]] = []
        
    async def execute_chain(
        self,
        steps: List[Dict[str, Any]],
        initial_state: Optional[Dict[str, Any]] = None,
        chain_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a chain of tool steps.
        
        Args:
            steps: List of step definitions with tool, inputs, on_success, on_failure
            initial_state: Initial state dict available to all steps
            chain_name: Optional name for this chain execution
            
        Returns:
            Dict with chain execution results
            
        Example step structure:
            {
                "tool": "gmail_search_messages",
                "inputs": {
                    "query": "{{ state.search_query }}",
                    "max_results": 10
                },
                "on_success": {
                    "next": "drive_upload_file",
                    "map_outputs": {
                        "messages": "search_results"
                    }
                },
                "on_failure": {
                    "action": "continue",  # or "stop", "retry"
                    "next": "notify_failure"
                }
            }
        """
        chain_id = self.ctx.plan_tool_chain(
            tools=[{"tool_name": step.get("tool"), "parameters": step.get("inputs", {})} for step in steps],
            reasoning=f"Executing composite tool chain: {chain_name or 'unnamed'}",
            chain_name=chain_name
        )
        
        # Initialize chain state
        state = initial_state or {}
        state["chain_id"] = chain_id
        state["chain_name"] = chain_name
        state["started_at"] = datetime.now().isoformat()
        
        results = []
        current_step_index = 0
        
        while current_step_index < len(steps):
            step = steps[current_step_index]
            step_name = step.get("tool", f"step_{current_step_index}")
            
            try:
                # Execute step
                step_result = await self._execute_step(step, state)
                
                # Record success
                self.execution_history.append({
                    "step_index": current_step_index,
                    "step_name": step_name,
                    "status": "success",
                    "result": step_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                results.append({
                    "step": step_name,
                    "status": "success",
                    "result": step_result
                })
                
                # Update state with outputs
                if step.get("on_success", {}).get("map_outputs"):
                    for source_key, dest_key in step["on_success"]["map_outputs"].items():
                        if source_key in step_result.get("data", {}):
                            state[dest_key] = step_result["data"][source_key]
                
                # Determine next step
                on_success = step.get("on_success", {})
                if on_success.get("next"):
                    # Find named step
                    next_step_name = on_success["next"]
                    next_index = self._find_step_by_name(steps, next_step_name)
                    if next_index is not None:
                        current_step_index = next_index
                    else:
                        # Step not found, continue to next
                        current_step_index += 1
                else:
                    # No explicit next, continue sequentially
                    current_step_index += 1
                    
            except Exception as e:
                # Record failure
                self.execution_history.append({
                    "step_index": current_step_index,
                    "step_name": step_name,
                    "status": "failure",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                results.append({
                    "step": step_name,
                    "status": "failure",
                    "error": str(e)
                })
                
                # Handle failure according to on_failure policy
                on_failure = step.get("on_failure", {})
                action = on_failure.get("action", "stop")
                
                if action == "stop":
                    # Stop chain execution
                    raise ChainExecutionError(
                        f"Chain execution stopped at step {current_step_index}: {step_name}",
                        current_step_index,
                        step_name,
                        e
                    )
                elif action == "retry":
                    # Retry the same step (with max retries check)
                    max_retries = on_failure.get("max_retries", 3)
                    retry_count = state.get(f"{step_name}_retry_count", 0)
                    
                    if retry_count < max_retries:
                        state[f"{step_name}_retry_count"] = retry_count + 1
                        # Stay on same step
                        continue
                    else:
                        # Max retries exceeded, stop
                        raise ChainExecutionError(
                            f"Max retries ({max_retries}) exceeded for step {step_name}",
                            current_step_index,
                            step_name,
                            e
                        )
                elif action == "continue":
                    # Continue to next step despite failure
                    if on_failure.get("next"):
                        next_step_name = on_failure["next"]
                        next_index = self._find_step_by_name(steps, next_step_name)
                        if next_index is not None:
                            current_step_index = next_index
                        else:
                            current_step_index += 1
                    else:
                        current_step_index += 1
                else:
                    # Unknown action, stop
                    raise ChainExecutionError(
                        f"Unknown failure action: {action}",
                        current_step_index,
                        step_name,
                        e
                    )
        
        # Build final result
        return {
            "success": True,
            "chain_id": chain_id,
            "chain_name": chain_name,
            "steps_executed": len(results),
            "steps_succeeded": sum(1 for r in results if r["status"] == "success"),
            "steps_failed": sum(1 for r in results if r["status"] == "failure"),
            "results": results,
            "execution_history": self.execution_history,
            "final_state": state,
            "completed_at": datetime.now().isoformat()
        }
    
    async def _execute_step(self, step: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in the chain.
        
        Args:
            step: Step definition with tool name and inputs
            state: Current chain state
            
        Returns:
            Step execution result
        """
        tool_name = step.get("tool")
        if not tool_name:
            raise ValueError("Step must have 'tool' field")
        
        # Get tool function from registry
        tool_info = MANAGED_TOOLS.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool not found in registry: {tool_name}")
        
        tool_func = tool_info["func"]
        
        # Resolve inputs from state
        inputs = self._resolve_inputs(step.get("inputs", {}), state)
        
        # Execute tool
        result = await tool_func(self.ctx, **inputs)
        
        return result
    
    def _resolve_inputs(self, inputs: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input parameters using template substitution from state.
        
        Args:
            inputs: Input specification with possible {{ state.variable }} templates
            state: Current state dict
            
        Returns:
            Resolved inputs dict
        """
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("{{ state.") and value.endswith(" }}"):
                # Template substitution: {{ state.variable }}
                var_name = value[10:-3].strip()  # Extract variable name
                resolved[key] = state.get(var_name, value)
            elif isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Generic template: {{ expression }}
                # For now, just look up in state
                var_name = value[2:-2].strip()
                resolved[key] = state.get(var_name, value)
            else:
                # Literal value
                resolved[key] = value
        
        return resolved
    
    def _find_step_by_name(self, steps: List[Dict[str, Any]], name: str) -> Optional[int]:
        """Find step index by tool name.
        
        Args:
            steps: List of step definitions
            name: Tool name to find
            
        Returns:
            Step index or None if not found
        """
        for i, step in enumerate(steps):
            if step.get("tool") == name:
                return i
        return None
