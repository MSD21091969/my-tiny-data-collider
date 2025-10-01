"""
Core dependency types for the MDS Objects framework.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Optional, Callable
from uuid import uuid4
from datetime import datetime
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

from ..coreservice.id_service import get_id_service
from ..pydantic_models.tool_session.models import ToolEvent

def with_persistence(method):
    """Decorator to automatically persist context after method execution."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        # Persist after method call if persistence is enabled
        if getattr(self, '_auto_persist', False) and hasattr(self, 'persist'):
            try:
                self.persist()
            except Exception as e:
                logger.warning(f"Auto-persistence failed after {method.__name__}: {e}")
        return result
    return wrapper

class MDSContext(BaseModel):
    """Unified context for MDS operations across tools and sessions."""
    
    # Core identifiers for linking
    user_id: str = Field(..., description="The ID of the current user")
    session_id: str = Field(..., description="Current tool session identifier (ts_ prefix)")
    casefile_id: Optional[str] = Field(None, description="Current casefile being worked on (string format: cf_yymmdd_code)")
    
    # Session tracking
    session_request_id: Optional[str] = Field(None, description="Current request within the session")
    tool_events: List[ToolEvent] = Field(default_factory=list, description="Event tracking for the current session")
    
    # State management
    transaction_context: Dict[str, Any] = Field(default_factory=dict, description="Shared state across tool calls")
    persistent_state: Dict[str, Any] = Field(default_factory=dict, description="State that persists across sessions")
    
    # Tool chain tracking
    previous_tools: List[Dict[str, Any]] = Field(default_factory=list, description="Previous tools executed in this chain")
    next_planned_tools: List[Dict[str, Any]] = Field(default_factory=list, description="Tools planned for execution after this one")
    active_chains: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Currently active tool chains")
    
    # Memory and history
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of conversation messages")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences and settings")
    
    # Knowledge integration
    related_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Documents relevant to current context")
    knowledge_graph: Dict[str, Any] = Field(default_factory=dict, description="Structured knowledge for the session")
    
    # Environment configuration
    environment: str = Field("development", description="Current deployment environment")
    
    # Persistence configuration
    _auto_persist: bool = False
    _persistence_handler: Optional[Callable] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="When this context was created")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="When this context was last updated")
    version: str = Field(default="1.0.0", description="Schema version for backward compatibility")
    
    @model_validator(mode='after')
    def ensure_serializable(self) -> 'MDSContext':
        """Ensure all fields are serializable for storage."""
        self.transaction_context = self._ensure_serializable_dict(self.transaction_context)
        self.persistent_state = self._ensure_serializable_dict(self.persistent_state)
        self.user_preferences = self._ensure_serializable_dict(self.user_preferences)
        self.knowledge_graph = self._ensure_serializable_dict(self.knowledge_graph)
        
        # Ensure conversation history is serializable
        self.conversation_history = [
            self._ensure_serializable_dict(msg) if isinstance(msg, dict) else msg.model_dump() 
            for msg in self.conversation_history
        ]
        
        # Ensure tool chain entries are serializable
        self.previous_tools = [
            self._ensure_serializable_dict(tool) if isinstance(tool, dict) else tool.model_dump() 
            for tool in self.previous_tools
        ]
        self.next_planned_tools = [
            self._ensure_serializable_dict(tool) if isinstance(tool, dict) else tool.model_dump() 
            for tool in self.next_planned_tools
        ]
        
        # Ensure related documents are serializable
        self.related_documents = [
            self._ensure_serializable_dict(doc) if isinstance(doc, dict) else doc.model_dump() 
            for doc in self.related_documents
        ]
        
        return self
    
    def _ensure_serializable_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively ensure dictionary is JSON serializable."""
        if not isinstance(data, dict):
            return data
            
        result = {}
        for k, v in data.items():
            if isinstance(v, dict):
                result[k] = self._ensure_serializable_dict(v)
            elif isinstance(v, list):
                result[k] = [self._ensure_serializable_dict(item) if isinstance(item, dict) else item for item in v]
            elif hasattr(v, 'model_dump'):
                # Handle Pydantic models
                result[k] = v.model_dump()
            elif isinstance(v, (str, int, float, bool, type(None))):
                # Basic types are fine
                result[k] = v
            else:
                # Convert anything else to string
                try:
                    result[k] = str(v)
                except:
                    result[k] = f"<non-serializable-{type(v).__name__}>"
        
        return result
    
    def set_persistence_handler(self, handler: Callable, auto_persist: bool = False) -> None:
        """Set a function to handle persistence of the context.
        
        Args:
            handler: Function that takes a serialized context and persists it
            auto_persist: Whether to automatically persist after state-changing operations
        """
        self._persistence_handler = handler
        self._auto_persist = auto_persist
        logger.info(f"Persistence handler set with auto_persist={auto_persist}")
    
    def persist(self) -> bool:
        """Persist the current state of the context.
        
        Returns:
            Whether persistence was successful
        """
        if not self._persistence_handler:
            logger.warning("No persistence handler set, cannot persist context")
            return False
            
        try:
            # Update timestamp
            self.updated_at = datetime.now().isoformat()
            
            # Serialize context ensuring all data is JSON compatible
            serialized = self.model_dump(mode='json')
            
            # Call persistence handler
            self._persistence_handler(serialized)
            logger.debug(f"Context persisted for session {self.session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to persist context: {e}")
            return False
    
    def from_persisted_state(self, state: Dict[str, Any]) -> 'MDSContext':
        """Update this context from a persisted state.
        
        Args:
            state: The persisted state to restore from
            
        Returns:
            Self for chaining
        """
        # We use model_validate to ensure proper type conversion
        updated = self.__class__.model_validate(state)
        
        # Update all fields from the persisted state
        for field_name, field_value in updated.model_dump().items():
            if field_name not in ('_persistence_handler', '_auto_persist'):
                setattr(self, field_name, field_value)
        
        logger.info(f"Context restored for session {self.session_id} with {len(self.tool_events)} events")
        return self
    
    @with_persistence
    def register_event(self, tool_name: str, parameters: Dict[str, Any], 
                      result_summary: Optional[Dict[str, Any]] = None,
                      duration_ms: Optional[int] = None,
                      chain_context: Optional[Dict[str, Any]] = None,
                      event_type: str = "tool_execution_completed") -> str:
        """Register a tool event in the audit trail and return its ID.
        
        Args:
            tool_name: Name of the tool being executed
            parameters: Tool parameters
            result_summary: Summary of tool results
            duration_ms: Execution duration in milliseconds
            chain_context: Context for tool chaining
            event_type: Type of event (default: "tool_execution_completed")
        
        Returns:
            Event ID
        """
        # Create chain ID if this is part of a chain
        chain_id = None
        if chain_context:
            # Use existing chain ID if provided
            chain_id = chain_context.get("chain_id")
            
            # Create new chain ID if starting a new chain
            if not chain_id and chain_context.get("start_new_chain", False):
                chain_id = str(uuid4())
                chain_context["chain_id"] = chain_id
            
            # Look up from active chains if we have a chain name
            chain_name = chain_context.get("chain_name")
            if chain_name and not chain_id:
                if chain_name in self.active_chains:
                    chain_id = self.active_chains[chain_name].get("chain_id")
                else:
                    # Create new chain and track it by name
                    chain_id = str(uuid4())
                    self.active_chains[chain_name] = {
                        "chain_id": chain_id,
                        "started_at": datetime.now().isoformat(),
                        "tools": []
                    }
        
        # Determine chain position if applicable
        chain_position = None
        if chain_id:
            # Find existing chain
            chain_events = [event for event in self.tool_events 
                           if event.chain_id == chain_id]
            chain_position = len(chain_events) + 1
        
        # Create the event
        event = ToolEvent(
            event_type=event_type,
            tool_name=tool_name,
            parameters=parameters,
            result_summary=result_summary,
            duration_ms=duration_ms,
            chain_id=chain_id,
            chain_position=chain_position,
            reasoning=chain_context.get("reasoning") if chain_context else None
        )
        self.tool_events.append(event)
        
        # If this is part of a tool chain, track it
        if chain_context:
            prev_tool = None
            if self.tool_events and len(self.tool_events) > 1:
                prev_tool = {
                    "tool_name": self.tool_events[-2].tool_name,
                    "event_id": self.tool_events[-2].event_id,
                    "chain_id": self.tool_events[-2].chain_id
                }
            
            # Record this tool in the chain
            tool_chain_entry = {
                "tool_name": tool_name,
                "event_id": event.event_id,
                "chain_id": chain_id,
                "sequence": len(self.previous_tools) + 1,
                "previous_tool": prev_tool,
                "reasoning": chain_context.get("reasoning"),
                "purpose": chain_context.get("purpose"),
                "timestamp": event.timestamp
            }
            
            self.previous_tools.append(tool_chain_entry)
            
            # Update active chain if tracking by name
            chain_name = chain_context.get("chain_name")
            if chain_name and chain_name in self.active_chains:
                self.active_chains[chain_name]["tools"].append({
                    "tool_name": tool_name,
                    "event_id": event.event_id,
                    "position": chain_position
                })
        
        return event.event_id
    
    @with_persistence
    def create_session_request(self, client_request_id: Optional[str] = None) -> str:
        """Create a new session request ID.
        
        Args:
            client_request_id: Optional client-provided request ID for tracking
            
        Returns:
            The generated request ID
        """
        self.session_request_id = get_id_service().new_session_request_id()
        # Store the client request ID for cross-referencing
        if client_request_id:
            self.transaction_context["client_request_id"] = client_request_id
        
        # Record creation time
        self.transaction_context["request_created_at"] = datetime.now().isoformat()
        return self.session_request_id
    
    @with_persistence    
    def plan_tool_chain(self, tools: List[Dict[str, Any]], reasoning: str = None, chain_name: str = None) -> str:
        """Plan a sequence of tools to be executed.
        
        Args:
            tools: List of tools to execute, each with name and parameters
            reasoning: Optional explanation of why this chain is planned
            chain_name: Optional name for this chain for later reference
            
        Returns:
            The ID for this planned chain
        """
        # Generate a chain ID
        chain_id = str(uuid4())
        
        # Store tools with chain ID
        self.next_planned_tools = [{
            **tool,
            "chain_id": chain_id,
            "planned_at": datetime.now().isoformat()
        } for tool in tools]
        
        # Record chain metadata
        chain_metadata = {
            "chain_id": chain_id,
            "reasoning": reasoning,
            "planned_at": datetime.now().isoformat(),
            "tool_count": len(tools)
        }
        
        # Store in transaction context
        self.transaction_context["planned_chain"] = chain_metadata
        
        # If named, store in active chains
        if chain_name:
            self.active_chains[chain_name] = {
                "chain_id": chain_id,
                "planned_at": datetime.now().isoformat(),
                "started_at": None,
                "tools": [],
                "planned_tools": [tool["tool_name"] for tool in tools]
            }
        
        return chain_id
    
    @with_persistence
    def add_conversation_message(self, message: Dict[str, Any]) -> str:
        """Add a message to the conversation history.
        
        Args:
            message: The message to add with role, content, and timestamp
            
        Returns:
            The ID assigned to this message
        """
        # Ensure required fields
        if not message.get("timestamp"):
            message["timestamp"] = datetime.now().isoformat()
            
        if not message.get("message_id"):
            message["message_id"] = str(uuid4())
        
        # Add metadata for correlation
        if self.session_request_id:
            message["session_request_id"] = self.session_request_id
            
        self.conversation_history.append(message)
        return message["message_id"]
    
    def get_relevant_history(self, tool_name: str = None, limit: int = 5,
                           chain_id: str = None, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """Get relevant history for the current context or specific tool.
        
        Args:
            tool_name: Optional tool name to filter history for
            limit: Maximum number of history items to return
            chain_id: Optional chain ID to filter by
            include_metadata: Whether to include full metadata or just content
            
        Returns:
            List of relevant history items
        """
        # For conversation history
        if not tool_name and not chain_id:
            history = self.conversation_history[-limit:] if self.conversation_history else []
            
            # Filter out metadata if requested
            if not include_metadata:
                history = [{
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "message_id": msg.get("message_id")
                } for msg in history]
                
            return history
        
        # For tool events    
        if tool_name or chain_id:
            # Start with all events
            filtered_events = self.tool_events
            
            # Filter by tool name if provided
            if tool_name:
                filtered_events = [event for event in filtered_events 
                                 if event.tool_name == tool_name]
                
            # Filter by chain ID if provided
            if chain_id:
                filtered_events = [event for event in filtered_events 
                                 if event.chain_id == chain_id]
            
            # Limit and convert to dict
            events = filtered_events[-limit:]
            if include_metadata:
                return [event.model_dump() for event in events]
            else:
                return [{"event_id": event.event_id, 
                         "tool_name": event.tool_name, 
                         "parameters": event.parameters,
                         "timestamp": event.timestamp} for event in events]
        
        return []
    
    @with_persistence    
    def link_related_document(self, document: Dict[str, Any]) -> str:
        """Link a document to the current context.
        
        Args:
            document: Document metadata including ID, type, and relevance
            
        Returns:
            The document ID
        """
        # Ensure required fields
        if not document.get("linked_at"):
            document["linked_at"] = datetime.now().isoformat()
            
        if not document.get("id"):
            document["id"] = str(uuid4())
            
        # Add session correlation
        if self.session_request_id:
            document["session_request_id"] = self.session_request_id
            
        self.related_documents.append(document)
        return document["id"]
    
    @with_persistence
    def store_persistent_state(self, key: str, value: Any) -> None:
        """Store a value in persistent state that survives across sessions.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        self.persistent_state[key] = value
        self.persistent_state["_last_updated"] = datetime.now().isoformat()
    
    def get_persistent_state(self, key: str, default: Any = None) -> Any:
        """Get a value from persistent state.
        
        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The stored value or default
        """
        return self.persistent_state.get(key, default)
    
    @with_persistence
    def add_to_knowledge_graph(self, entity_type: str, entity_id: str, data: Dict[str, Any]) -> None:
        """Add or update entity in the knowledge graph.
        
        Args:
            entity_type: Type of entity (person, document, concept, etc.)
            entity_id: Unique identifier for this entity
            data: Entity data and properties
        """
        # Initialize type if not exist
        if entity_type not in self.knowledge_graph:
            self.knowledge_graph[entity_type] = {}
            
        # Add timestamp
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        
        # Store entity
        self.knowledge_graph[entity_type][entity_id] = data
    
    @with_persistence    
    def complete_chain(self, chain_id: str = None, chain_name: str = None,
                     success: bool = True, summary: Dict[str, Any] = None) -> None:
        """Mark a chain as completed.
        
        Args:
            chain_id: The ID of the chain to complete
            chain_name: The name of the chain to complete (alternative to ID)
            success: Whether the chain completed successfully
            summary: Optional summary information about the chain results
        """
        # Find chain ID from name if provided
        if chain_name and not chain_id:
            if chain_name in self.active_chains:
                chain_id = self.active_chains[chain_name].get("chain_id")
        
        if not chain_id:
            logger.warning("Cannot complete chain: no chain ID or valid chain name provided")
            return
            
        # Update transaction context
        self.transaction_context["chain_completed"] = {
            "chain_id": chain_id,
            "completed_at": datetime.now().isoformat(),
            "success": success,
            "summary": summary or {}
        }
        
        # Update active chains
        for name, chain in list(self.active_chains.items()):
            if chain.get("chain_id") == chain_id:
                chain["completed_at"] = datetime.now().isoformat()
                chain["success"] = success
                if summary:
                    chain["summary"] = summary
                
                # Optionally remove from active chains
                if success:
                    self.active_chains.pop(name, None)
    
    def get_chain_status(self, chain_id: str = None, chain_name: str = None) -> Dict[str, Any]:
        """Get the status of a chain.
        
        Args:
            chain_id: The ID of the chain to check
            chain_name: The name of the chain to check (alternative to ID)
            
        Returns:
            Status information about the chain
        """
        # Check named chains first
        if chain_name and chain_name in self.active_chains:
            return self.active_chains[chain_name]
            
        # Look up by ID
        if chain_id:
            # Check active chains
            for name, chain in self.active_chains.items():
                if chain.get("chain_id") == chain_id:
                    return chain
                    
            # Look through tool events
            chain_events = [event for event in self.tool_events 
                           if event.chain_id == chain_id]
                           
            if chain_events:
                return {
                    "chain_id": chain_id,
                    "started_at": chain_events[0].timestamp,
                    "last_update": chain_events[-1].timestamp,
                    "tool_count": len(chain_events),
                    "tools": [{"tool_name": event.tool_name, 
                               "event_id": event.event_id,
                               "position": event.chain_position} 
                              for event in chain_events]
                }
        
        return {"error": "Chain not found"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage or transmission.
        
        Returns:
            Dictionary representation of the context
        """
        # Convert context to dict with special handling
        data = self.model_dump(mode='json')
        
        # Convert tool events to dicts
        data["tool_events"] = [
            event.to_storage_format() if hasattr(event, 'to_storage_format') 
            else event
            for event in self.tool_events
        ]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MDSContext':
        """Create context from dictionary.
        
        Args:
            data: Dictionary representation of context
            
        Returns:
            New MDSContext instance
        """
        return cls.model_validate(data)
    
    def export_to_json(self, file_path: str) -> bool:
        """Export context to JSON file.
        
        Args:
            file_path: Path to save the JSON file
            
        Returns:
            Whether the export was successful
        """
        try:
            data = self.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export context to JSON: {e}")
            return False
    
    @classmethod
    def import_from_json(cls, file_path: str) -> 'MDSContext':
        """Import context from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            New MDSContext instance
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to import context from JSON: {e}")
            raise