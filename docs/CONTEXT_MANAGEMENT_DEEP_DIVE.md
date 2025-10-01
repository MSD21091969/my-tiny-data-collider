# Context Management Deep Dive: MDSContext vs PydanticAI vs Google ADK

## Your Question Decoded

You're wrestling with **3 layers of context**:

1. **Your Rich Audit Trail** - `casefile → session → session_request_id → toolevents` with BaseRequest/BaseResponse "nuggets"
2. **PydanticAI's `RunContext`** - Simple deps injection for tools
3. **Google ADK's Session Management** - Framework-level session/context handling

**The Core Tension:** You want YOUR context (rich audit trail) to BE the agent's context, not fight with framework abstractions.

---

## 1. Your Context Architecture (MDSContext)

### What You Built:
```python
class MDSContext(BaseModel):
    # YOUR RICH IDENTIFIERS
    user_id: str
    session_id: str  # ts_YYMMDD_USER_CASE_RANDOM
    casefile_id: Optional[str]  # Links to case
    session_request_id: Optional[str]  # Current request
    tool_events: List[ToolEvent]  # Your audit trail!
    
    # YOUR STATE MANAGEMENT
    transaction_context: Dict  # Request-level state
    persistent_state: Dict  # Cross-session state
    conversation_history: List  # Chat messages
    
    # YOUR TOOL CHAIN TRACKING
    previous_tools: List  # Chain history
    next_planned_tools: List  # Chain planning
    active_chains: Dict  # Named chains
```

### What It Does Well:
✅ **Hierarchical IDs** - Clear lineage: `casefile → session → request → events`  
✅ **Audit Trail** - Every tool execution = ToolEvent with rich metadata  
✅ **State Management** - Both transient (request) and persistent (cross-session)  
✅ **Tool Chains** - Track sequences, reasoning, dependencies  
✅ **Serializable** - Can persist to Firestore, restore later  

### The "Nuggets":
Your BaseRequest/BaseResponse models carry:
- `request_id` (UUID) - Links to Firestore `/sessions/{sid}/requests/{rid}`
- `user_id`, `operation`, `payload`, `timestamp`, `metadata`
- Status tracking (PENDING → PROCESSING → COMPLETED/FAILED)

These ARE your audit trail! Each request generates multiple ToolEvents:
1. `tool_request_received` - Request arrived
2. `tool_execution_started` - Tool beginning
3. `tool_execution_completed` - Tool finished (success)
4. `tool_execution_failed` - Tool failed (error)
5. `tool_response_sent` - Response returned

**This is YOUR session management layer. It's complete and rich.**

---

## 2. PydanticAI's Context (`RunContext`)

### What PydanticAI Does:

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4',
    deps_type=MDSContext  # ← YOUR context becomes deps!
)

@agent.tool
async def example_tool(ctx: RunContext[MDSContext], value: int) -> dict:
    # ctx.deps = YOUR MDSContext instance
    # ctx.retry = Retry attempt number
    # ctx.tool_name = Name of this tool
    
    # Access YOUR context
    user_id = ctx.deps.user_id
    session_id = ctx.deps.session_id
    
    # Register in YOUR audit trail
    ctx.deps.register_event(
        tool_name="example_tool",
        parameters={"value": value},
        result_summary={"result": value * 2}
    )
    
    return {"result": value * 2}
```

### PydanticAI's `RunContext`:
```python
class RunContext[AgentDeps]:
    deps: AgentDeps  # ← YOUR MDSContext goes here!
    retry: int  # Retry attempt (0 for first try)
    tool_name: str | None  # Current tool name
    # ... other framework metadata
```

### What PydanticAI Does NOT Do:
❌ **No session management** - Doesn't track sessions across requests  
❌ **No persistence** - Context lives only during `agent.run()` call  
❌ **No audit trail** - Doesn't track tool execution history  
❌ **No state continuity** - Each `run()` is isolated  

### What PydanticAI DOES Do:
✅ **Dependency injection** - Passes YOUR context to tools  
✅ **Tool registration** - Discovers `@agent.tool` functions  
✅ **LLM orchestration** - Calls LLM, parses tool calls, executes tools  
✅ **Retry logic** - Handles tool failures with retries  

---

## 3. Google ADK (Agent Development Kit)

### What ADK Provides:

```python
from vertexai.preview import agents

# ADK's AgentRunner
runner = agents.AgentRunner(
    agent=my_agent,
    config=RunnerConfig(
        session_id="user123_session",  # ADK's session tracking
        context=initial_context  # ADK's context
    )
)

# ADK manages:
# - Session persistence (saves/restores state)
# - Context propagation (passes context to tools)
# - Tool execution tracking
# - Conversation history
```

### ADK's Context Model:
```python
# ADK provides:
class ExecutionContext:
    session_id: str  # ADK's session ID
    user_id: str
    conversation: List[Message]  # ADK's message history
    state: Dict  # ADK's state storage
    # ... ADK-specific fields
```

### The Problem You Hit:

**ADK wants to own the session:**
- ADK's `session_id` ≠ Your `session_id` (ts_YYMMDD_...)
- ADK's `state` ≠ Your rich audit trail
- ADK's persistence ≠ Your Firestore structure

**You can't easily "slide your toolcontext into ADK session"** because:
1. ADK expects its own session schema
2. ADK's ExecutionContext has different fields than MDSContext
3. ADK's persistence layer doesn't know about your Firestore structure

---

## 4. The Solution: Force YOUR Context on the Agent

### YES, You Can Bypass ADK! Here's How:

### Option A: Use PydanticAI with YOUR MDSContext (Recommended)

```python
from pydantic_ai import Agent

# Define agent with YOUR context type
agent = Agent(
    'openai:gpt-4',
    deps_type=MDSContext  # ← Use YOUR context
)

@agent.tool
async def my_tool(ctx: RunContext[MDSContext], param: str) -> dict:
    """Tool has access to YOUR full context."""
    
    # Access YOUR identifiers
    session_id = ctx.deps.session_id  # ts_YYMMDD_...
    casefile_id = ctx.deps.casefile_id
    user_id = ctx.deps.user_id
    
    # Register in YOUR audit trail
    ctx.deps.register_event(
        tool_name="my_tool",
        parameters={"param": param},
        result_summary={"status": "success"}
    )
    
    # Access YOUR state
    previous_value = ctx.deps.transaction_context.get("key")
    
    # Update YOUR state
    ctx.deps.transaction_context["key"] = "new_value"
    
    # YOUR persistence (if configured)
    if ctx.deps._auto_persist:
        ctx.deps.persist()  # Saves to YOUR Firestore structure
    
    return {"result": "done"}


# In your service layer:
async def execute_tool_with_your_context():
    """Execute tool with YOUR context."""
    
    # 1. Create YOUR context (from session)
    context = MDSContext(
        user_id="user123",
        session_id="ts_251001_user123_case_abc",
        casefile_id="251001_abc"
    )
    
    # 2. Optionally restore persisted state
    # persisted = await load_from_firestore(session_id)
    # context.from_persisted_state(persisted)
    
    # 3. Set up persistence handler
    async def save_to_firestore(data):
        # Save to YOUR Firestore structure
        await firestore.collection("sessions").document(
            context.session_id
        ).collection("context").document("state").set(data)
    
    context.set_persistence_handler(save_to_firestore, auto_persist=True)
    
    # 4. Run agent with YOUR context
    result = await agent.run(
        "Execute my_tool with param='test'",
        deps=context  # ← YOUR context passed to tools!
    )
    
    # 5. YOUR context is now updated with audit trail
    print(f"Tool events: {len(context.tool_events)}")
    print(f"Transaction state: {context.transaction_context}")
    
    # 6. Persist final state
    context.persist()
    
    return result
```

### Option B: Wrap ADK with YOUR Context Translation Layer

```python
class ADKContextAdapter:
    """Translates between YOUR context and ADK's context."""
    
    def __init__(self, mds_context: MDSContext):
        self.mds = mds_context
        self.adk_context = self._to_adk_context(mds_context)
    
    def _to_adk_context(self, mds: MDSContext) -> dict:
        """Convert YOUR context to ADK format."""
        return {
            "session_id": mds.session_id,  # Use YOUR session ID
            "user_id": mds.user_id,
            "state": {
                # Embed YOUR rich state
                "casefile_id": mds.casefile_id,
                "transaction_context": mds.transaction_context,
                "tool_events": [e.model_dump() for e in mds.tool_events],
                # ... all your fields
            }
        }
    
    def _from_adk_context(self, adk_ctx: dict) -> MDSContext:
        """Convert ADK context back to YOUR context."""
        state = adk_ctx.get("state", {})
        return MDSContext(
            session_id=adk_ctx["session_id"],
            user_id=adk_ctx["user_id"],
            casefile_id=state.get("casefile_id"),
            transaction_context=state.get("transaction_context", {}),
            # ... restore all fields
        )
    
    async def run_with_adk(self, agent, prompt):
        """Run ADK agent with YOUR context."""
        # Convert to ADK format
        adk_ctx = self._to_adk_context(self.mds)
        
        # Run ADK agent
        runner = agents.AgentRunner(agent, config=RunnerConfig(
            session_id=self.mds.session_id,
            context=adk_ctx
        ))
        result = await runner.run(prompt)
        
        # Convert back to YOUR context
        self.mds = self._from_adk_context(result.context)
        
        return result
```

### Option C: Don't Use ADK or PydanticAI - Direct Tool Execution

```python
# Your current approach in ToolSessionService
async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
    """YOU manage context, YOU call tools directly."""
    
    # 1. Get session (YOUR session structure)
    session = await self.repository.get_session(request.session_id)
    
    # 2. Create YOUR context
    context = MDSContext(
        user_id=session.user_id,
        session_id=session.session_id,
        casefile_id=session.casefile_id
    )
    
    # 3. Create session request ID (YOUR tracking)
    request_id = str(request.request_id)
    session.request_ids.append(request_id)
    
    # 4. Create ToolEvent: tool_request_received
    event = ToolEvent(
        event_type="tool_request_received",
        tool_name=request.payload.tool_name,
        parameters=request.payload.parameters
    )
    await self.repository.add_event_to_request(session_id, request_id, event)
    
    # 5. Execute tool DIRECTLY (no framework)
    if request.payload.tool_name == "example_tool":
        from ..tools.enhanced_example_tools import example_tool
        result_data = await example_tool(context, request.payload.parameters["value"])
    
    # 6. Create ToolEvent: tool_execution_completed
    event = ToolEvent(
        event_type="tool_execution_completed",
        tool_name=request.payload.tool_name,
        result_summary=result_data,
        status="success"
    )
    await self.repository.add_event_to_request(session_id, request_id, event)
    
    # 7. Return response (YOUR structure)
    return ToolResponse(...)
```

---

## 5. How ADK Retrieves Tool Context (The Elaborate Answer)

### ADK's Context Flow:

```
1. SESSION START
   ↓
   AgentRunner.run(session_id="abc123")
   ↓
   ADK checks persistence layer:
   - Vertex AI Session Store
   - Or custom SessionManager
   ↓
   Loads: ExecutionContext(session_id, state, history)

2. TOOL EXECUTION
   ↓
   LLM decides to call tool: "search_documents"
   ↓
   ADK looks up tool registration
   ↓
   ADK calls tool function:
   tool_func(context=ExecutionContext, **params)
   ↓
   Tool has access to:
   - context.session_id
   - context.state (dict)
   - context.conversation (messages)

3. TOOL UPDATES CONTEXT
   ↓
   Tool modifies context.state["key"] = "value"
   ↓
   ADK tracks context mutations

4. SESSION END
   ↓
   AgentRunner persists updated context
   ↓
   Saves to Vertex AI Session Store
   ↓
   Next run with same session_id restores state
```

### ADK's Context Retrieval Mechanism:

```python
# ADK's internal flow (simplified):

class AgentRunner:
    def __init__(self, agent, config: RunnerConfig):
        self.agent = agent
        self.session_id = config.session_id
        self.session_manager = config.session_manager or DefaultSessionManager()
    
    async def run(self, prompt: str):
        # 1. RETRIEVE context from persistence
        context = await self.session_manager.get_context(self.session_id)
        
        if not context:
            # First time - create new context
            context = ExecutionContext(
                session_id=self.session_id,
                state=config.initial_state or {},
                conversation=[]
            )
        
        # 2. ADD user message to conversation
        context.conversation.append(Message(role="user", content=prompt))
        
        # 3. RUN agent loop
        while not done:
            # Get LLM response
            llm_response = await self.agent.llm.generate(context.conversation)
            
            # Parse tool calls
            if llm_response.has_tool_calls():
                for tool_call in llm_response.tool_calls:
                    # 4. EXECUTE tool with context
                    tool_result = await self._execute_tool(
                        tool_call.name,
                        tool_call.parameters,
                        context  # ← Context passed here!
                    )
                    
                    # Add tool result to conversation
                    context.conversation.append(
                        Message(role="tool", content=tool_result)
                    )
            else:
                done = True
        
        # 5. PERSIST updated context
        await self.session_manager.save_context(self.session_id, context)
        
        return AgentResponse(content=llm_response.content, context=context)
    
    async def _execute_tool(self, tool_name: str, params: dict, context: ExecutionContext):
        """Execute tool with context."""
        # Find registered tool
        tool_func = self.agent.tools[tool_name]
        
        # Call with context as first argument
        result = await tool_func(context, **params)
        
        # Context may have been mutated by tool
        return result
```

### ADK's Session Manager:

```python
class DefaultSessionManager:
    """ADK's default persistence for sessions."""
    
    def __init__(self):
        # Uses Vertex AI's built-in session store
        self.client = aiplatform.SessionClient()
    
    async def get_context(self, session_id: str) -> ExecutionContext:
        """Retrieve context from Vertex AI."""
        # Query Vertex AI session store
        session_data = await self.client.get_session(session_id)
        
        if not session_data:
            return None
        
        # Deserialize to ExecutionContext
        return ExecutionContext(
            session_id=session_id,
            state=session_data.get("state", {}),
            conversation=session_data.get("conversation", [])
        )
    
    async def save_context(self, session_id: str, context: ExecutionContext):
        """Persist context to Vertex AI."""
        # Serialize context
        session_data = {
            "state": context.state,
            "conversation": context.conversation,
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to Vertex AI session store
        await self.client.update_session(session_id, session_data)
```

### The Problem:

**ADK's session store ≠ Your Firestore structure**

ADK saves:
```
Vertex AI Session Store:
  /sessions/{adk_session_id}
    - state: {}
    - conversation: []
```

You want:
```
Your Firestore:
  /sessions/{ts_YYMMDD_USER_CASE_RANDOM}
    - request_ids: []
    /requests/{request_id}
      /events/{event_id}
```

**These are incompatible structures!**

---

## 6. The Recommended Architecture

### Use PydanticAI + YOUR Context + YOUR Persistence

```python
# 1. YOUR CONTEXT (Already built!)
class MDSContext(BaseModel):
    user_id: str
    session_id: str  # ts_YYMMDD_...
    casefile_id: Optional[str]
    tool_events: List[ToolEvent]
    transaction_context: Dict
    # ... all your fields

# 2. PYDANTIC AI AGENT (with YOUR context)
from pydantic_ai import Agent

agent = Agent('openai:gpt-4', deps_type=MDSContext)

@agent.tool
async def search_documents(ctx: RunContext[MDSContext], query: str) -> dict:
    """Tool with full access to YOUR context."""
    # Access YOUR session
    session_id = ctx.deps.session_id
    casefile_id = ctx.deps.casefile_id
    
    # Do work...
    results = await do_search(query, casefile_id)
    
    # Register in YOUR audit trail
    ctx.deps.register_event(
        tool_name="search_documents",
        parameters={"query": query},
        result_summary={"count": len(results)}
    )
    
    return {"results": results}

# 3. YOUR SERVICE LAYER (orchestrates everything)
class ToolSessionService:
    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        # Get YOUR session
        session = await self.repository.get_session(request.session_id)
        
        # Create YOUR context
        context = MDSContext(
            user_id=session.user_id,
            session_id=session.session_id,
            casefile_id=session.casefile_id
        )
        
        # Set up YOUR persistence
        async def save_to_your_firestore(data):
            await self.repository.save_context(session.session_id, data)
        context.set_persistence_handler(save_to_your_firestore, auto_persist=True)
        
        # Track in YOUR audit trail
        request_id = str(request.request_id)
        session.request_ids.append(request_id)
        await self.repository.add_request_to_session(session.session_id, request)
        
        # Create ToolEvent: request received
        event = ToolEvent(
            event_type="tool_request_received",
            tool_name=request.payload.tool_name,
            parameters=request.payload.parameters
        )
        await self.repository.add_event_to_request(session.session_id, request_id, event)
        
        # RUN AGENT with YOUR context
        result = await agent.run(
            f"Execute {request.payload.tool_name} with parameters: {request.payload.parameters}",
            deps=context  # ← YOUR context!
        )
        
        # YOUR context now has updated audit trail
        # Save all events from context to YOUR Firestore
        for event in context.tool_events:
            await self.repository.add_event_to_request(session.session_id, request_id, event)
        
        # Create ToolEvent: response sent
        event = ToolEvent(
            event_type="tool_response_sent",
            tool_name=request.payload.tool_name,
            status="success"
        )
        await self.repository.add_event_to_request(session.session_id, request_id, event)
        
        # Return YOUR response structure
        return ToolResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=ToolResponsePayload(result=result.output)
        )
```

---

## 7. Summary: Your Questions Answered

### Q: "Can I force my execution context upon the agent, bypassing ADK framework?"

**A: YES!** Use PydanticAI with YOUR MDSContext as `deps_type`. PydanticAI doesn't impose its own session management - it just passes YOUR context to tools. You retain full control.

### Q: "Am I missing ADK's finesses?"

**A: NO.** ADK's "finesses" are:
- Session persistence (you have better with Firestore subcollections)
- Context propagation (PydanticAI does this via deps)
- Tool execution tracking (you have richer audit trail)

ADK is designed for Vertex AI ecosystem. Your Firestore-based architecture is more flexible.

### Q: "How does ADK retrieve tool context?"

**A:** ADK uses:
1. `AgentRunner` wraps agent with session management
2. `SessionManager` loads/saves `ExecutionContext` from Vertex AI Session Store
3. Each tool call receives `ExecutionContext` as first parameter
4. Tools mutate `context.state` directly
5. After run completes, context is persisted back to Vertex AI

**But:** This is opinionated for Vertex AI. Your Firestore structure is more detailed and flexible.

---

## 8. The Win: You Already Have Everything

Your architecture is **better** than ADK for your use case:

✅ **Hierarchical IDs** - casefile → session → request → events  
✅ **Rich Audit Trail** - Every action tracked as ToolEvent  
✅ **Flexible Persistence** - Firestore subcollections, no document size limits  
✅ **State Management** - Transaction + persistent state  
✅ **Tool Chains** - Track sequences and reasoning  
✅ **Type Safety** - All Pydantic models, full validation  

**Use PydanticAI for LLM orchestration, but YOUR context for everything else.**

The refactored architecture we just built is production-ready! 🎉
