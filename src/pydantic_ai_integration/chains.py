"""
Chain execution engine for tool composition workflows.

This module provides the ChainExecutor class for orchestrating multi-tool
workflows with support for sequential and parallel execution patterns.
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from enum import Enum
from uuid import uuid4
from datetime import datetime
import asyncio
import logging

from .dependencies import MDSContext
from .tool_decorator import get_tool_definition

logger = logging.getLogger(__name__)


class ChainExecutionMode(str, Enum):
    """Execution modes for tool chains."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class ChainStatus(str, Enum):
    """Status of a chain execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class ChainExecutionError(Exception):
    """Exception raised when chain execution fails."""
    pass


class ChainExecutor:
    """
    Executor for tool chains with support for sequential and parallel execution.
    
    The ChainExecutor manages the lifecycle of tool chain execution including:
    - Chain validation
    - Sequential execution (one tool after another)
    - Parallel execution (multiple tools concurrently)
    - Error handling and rollback
    - Result aggregation
    - State management
    
    Example:
        >>> executor = ChainExecutor(context)
        >>> chain = [
        ...     {"tool_name": "tool1", "parameters": {"input": "test"}},
        ...     {"tool_name": "tool2", "parameters": {"data": "value"}}
        ... ]
        >>> results = await executor.execute_chain(chain, mode="sequential")
    """
    
    def __init__(self, context: MDSContext):
        """
        Initialize the chain executor.
        
        Args:
            context: The MDSContext for execution
        """
        self.context = context
        self.current_chain_id: Optional[str] = None
        self.current_status: ChainStatus = ChainStatus.PENDING
        
    async def execute_chain(
        self,
        tools: List[Dict[str, Any]],
        mode: ChainExecutionMode = ChainExecutionMode.SEQUENTIAL,
        chain_name: Optional[str] = None,
        stop_on_error: bool = True,
        pass_results: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a chain of tools.
        
        Args:
            tools: List of tool definitions with tool_name and parameters
            mode: Execution mode (sequential or parallel)
            chain_name: Optional name for the chain
            stop_on_error: Whether to stop chain execution on first error
            pass_results: Whether to pass results from one tool to the next
            
        Returns:
            Execution results including status, results, and any errors
        """
        # Validate the chain
        validation = self.context.validate_chain(tools)
        if not validation["valid"]:
            return {
                "status": ChainStatus.FAILED,
                "error": "Chain validation failed",
                "validation_errors": validation["errors"]
            }
        
        # Create chain ID
        chain_id = str(uuid4())
        self.current_chain_id = chain_id
        self.current_status = ChainStatus.RUNNING
        
        # Initialize chain tracking
        if chain_name:
            self.context.active_chains[chain_name] = {
                "chain_id": chain_id,
                "started_at": datetime.now().isoformat(),
                "mode": mode,
                "tool_count": len(tools),
                "tools": []
            }
        
        start_time = datetime.now()
        
        try:
            # Execute based on mode
            if mode == ChainExecutionMode.SEQUENTIAL:
                results = await self._execute_sequential(
                    tools, chain_id, chain_name, stop_on_error, pass_results
                )
            elif mode == ChainExecutionMode.PARALLEL:
                results = await self._execute_parallel(
                    tools, chain_id, chain_name, stop_on_error
                )
            else:
                raise ChainExecutionError(f"Unsupported execution mode: {mode}")
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Determine final status
            failed_count = sum(1 for r in results if r.get("error"))
            if failed_count == 0:
                final_status = ChainStatus.COMPLETED
            elif failed_count == len(results):
                final_status = ChainStatus.FAILED
            else:
                final_status = ChainStatus.PARTIALLY_COMPLETED
            
            self.current_status = final_status
            
            # Complete the chain
            summary = {
                "total_tools": len(tools),
                "successful": len(results) - failed_count,
                "failed": failed_count,
                "duration_ms": duration_ms,
                "mode": mode
            }
            
            self.context.complete_chain(
                chain_id=chain_id,
                chain_name=chain_name,
                success=(final_status == ChainStatus.COMPLETED),
                summary=summary
            )
            
            return {
                "status": final_status,
                "chain_id": chain_id,
                "results": results,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Chain execution failed: {e}", exc_info=True)
            self.current_status = ChainStatus.FAILED
            
            # Mark chain as failed
            self.context.complete_chain(
                chain_id=chain_id,
                chain_name=chain_name,
                success=False,
                summary={"error": str(e)}
            )
            
            return {
                "status": ChainStatus.FAILED,
                "chain_id": chain_id,
                "error": str(e),
                "results": []
            }
    
    async def _execute_sequential(
        self,
        tools: List[Dict[str, Any]],
        chain_id: str,
        chain_name: Optional[str],
        stop_on_error: bool,
        pass_results: bool
    ) -> List[Dict[str, Any]]:
        """
        Execute tools sequentially in order.
        
        Args:
            tools: List of tool definitions
            chain_id: Chain identifier
            chain_name: Optional chain name
            stop_on_error: Whether to stop on first error
            pass_results: Whether to pass results between tools
            
        Returns:
            List of execution results
        """
        results = []
        previous_result = None
        
        for position, tool_def in enumerate(tools, start=1):
            tool_name = tool_def["tool_name"]
            parameters = tool_def.get("parameters", {})
            
            # Pass previous result if enabled
            if pass_results and previous_result and not previous_result.get("error"):
                # Merge previous result into parameters
                parameters = {
                    **parameters,
                    "_previous_result": previous_result
                }
            
            # Execute the tool
            result = await self._execute_single_tool(
                tool_name=tool_name,
                parameters=parameters,
                chain_id=chain_id,
                chain_name=chain_name,
                position=position
            )
            
            results.append(result)
            previous_result = result
            
            # Stop on error if configured
            if stop_on_error and result.get("error"):
                logger.warning(f"Stopping chain execution at position {position} due to error")
                break
        
        return results
    
    async def _execute_parallel(
        self,
        tools: List[Dict[str, Any]],
        chain_id: str,
        chain_name: Optional[str],
        stop_on_error: bool
    ) -> List[Dict[str, Any]]:
        """
        Execute tools in parallel.
        
        Args:
            tools: List of tool definitions
            chain_id: Chain identifier
            chain_name: Optional chain name
            stop_on_error: Whether to stop on first error (cancels remaining tasks)
            
        Returns:
            List of execution results in original order
        """
        # Create tasks for all tools
        tasks = []
        for position, tool_def in enumerate(tools, start=1):
            task = self._execute_single_tool(
                tool_name=tool_def["tool_name"],
                parameters=tool_def.get("parameters", {}),
                chain_id=chain_id,
                chain_name=chain_name,
                position=position
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        if stop_on_error:
            # Use gather with return_exceptions to get all results even if some fail
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "tool_name": tools[i]["tool_name"],
                        "position": i + 1,
                        "error": str(result),
                        "error_type": type(result).__name__
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            # Execute all regardless of errors
            return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def _execute_single_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        chain_id: str,
        chain_name: Optional[str],
        position: int
    ) -> Dict[str, Any]:
        """
        Execute a single tool within a chain.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            chain_id: Chain identifier
            chain_name: Optional chain name
            position: Position in the chain
            
        Returns:
            Execution result
        """
        start_time = datetime.now()
        
        try:
            # Get tool definition
            tool_def = get_tool_definition(tool_name)
            if not tool_def:
                raise ChainExecutionError(f"Tool '{tool_name}' not found")
            
            # Check if tool is enabled
            if not tool_def.business_rules.enabled:
                raise ChainExecutionError(f"Tool '{tool_name}' is not enabled")
            
            # Execute the tool implementation
            result = await tool_def.implementation(self.context, **parameters)
            
            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Register the event
            chain_context = {
                "chain_id": chain_id,
                "chain_name": chain_name,
                "position": position,
                "purpose": f"Chain execution at position {position}"
            }
            
            event_id = self.context.register_event(
                tool_name=tool_name,
                parameters=parameters,
                result_summary=result,
                duration_ms=duration_ms,
                chain_context=chain_context
            )
            
            return {
                "tool_name": tool_name,
                "position": position,
                "event_id": event_id,
                "result": result,
                "duration_ms": duration_ms,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {e}", exc_info=True)
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Still register the event as failed
            chain_context = {
                "chain_id": chain_id,
                "chain_name": chain_name,
                "position": position,
                "purpose": f"Chain execution at position {position} (failed)"
            }
            
            event_id = self.context.register_event(
                tool_name=tool_name,
                parameters=parameters,
                result_summary={"error": str(e)},
                duration_ms=duration_ms,
                chain_context=chain_context,
                event_type="tool_execution_failed"
            )
            
            return {
                "tool_name": tool_name,
                "position": position,
                "event_id": event_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": duration_ms,
                "success": False
            }
    
    def get_status(self) -> ChainStatus:
        """Get the current status of the executor."""
        return self.current_status
    
    def get_current_chain_id(self) -> Optional[str]:
        """Get the ID of the currently executing chain."""
        return self.current_chain_id
