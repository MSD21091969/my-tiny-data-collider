"""
Test script to create a session directly via service layer.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tool_sessionservice import ToolSessionService
from src.casefileservice import CasefileService
from src.pydantic_models.casefile import CasefileModel, CasefileMetadata


async def create_session_example():
    """Example of creating a session directly via service."""
    
    print("=" * 60)
    print("Creating Session via Service Layer")
    print("=" * 60)
    
    # 1. Create casefile service and session service
    casefile_service = CasefileService()
    session_service = ToolSessionService()
    
    # 2. Create a casefile first (sessions require casefile)
    print("\n1. Creating casefile...")
    metadata = CasefileMetadata(
        title="Test Casefile for Session",
        description="Created via script",
        tags=["test", "script"],
        created_by="user123"
    )
    
    casefile = CasefileModel(metadata=metadata)
    casefile_id = await casefile_service.create_casefile(casefile)
    print(f"   ✅ Casefile created: {casefile_id}")
    
    # 3. Create a session linked to the casefile
    print("\n2. Creating session...")
    result = await session_service.create_session(
        user_id="user123",
        casefile_id=casefile_id
    )
    session_id = result["session_id"]
    print(f"   ✅ Session created: {session_id}")
    
    # 4. Get the session to verify
    print("\n3. Retrieving session...")
    session_data = await session_service.get_session(session_id)
    print(f"   ✅ Session retrieved:")
    print(f"      - Session ID: {session_data['session_id']}")
    print(f"      - User ID: {session_data['user_id']}")
    print(f"      - Casefile ID: {session_data['casefile_id']}")
    print(f"      - Active: {session_data['active']}")
    print(f"      - Request IDs: {session_data['request_ids']}")
    
    # 5. Verify casefile has session linked
    print("\n4. Verifying casefile linkage...")
    casefile_data = await casefile_service.get_casefile(casefile_id)
    print(f"   ✅ Casefile has {len(casefile_data['session_ids'])} session(s)")
    print(f"      - Session IDs: {casefile_data['session_ids']}")
    
    print("\n" + "=" * 60)
    print("✅ Complete! Session created successfully")
    print("=" * 60)
    
    return session_id


async def create_and_execute_tool():
    """Example showing full workflow: create session + execute tool."""
    
    print("\n" + "=" * 60)
    print("Full Workflow: Create Session + Execute Tool")
    print("=" * 60)
    
    from src.pydantic_models.tool_session import ToolRequest, ToolRequestPayload
    
    # 1. Setup services
    casefile_service = CasefileService()
    session_service = ToolSessionService()
    
    # 2. Create casefile
    print("\n1. Creating casefile...")
    metadata = CasefileMetadata(
        title="Full Workflow Test",
        created_by="user123"
    )
    casefile = CasefileModel(metadata=metadata)
    casefile_id = await casefile_service.create_casefile(casefile)
    print(f"   ✅ Casefile: {casefile_id}")
    
    # 3. Create session
    print("\n2. Creating session...")
    result = await session_service.create_session(
        user_id="user123",
        casefile_id=casefile_id
    )
    session_id = result["session_id"]
    print(f"   ✅ Session: {session_id}")
    
    # 4. Execute a tool
    print("\n3. Executing tool...")
    payload = ToolRequestPayload(
        tool_name="example_tool",
        parameters={"value": 42}
    )
    
    request = ToolRequest(
        user_id="user123",
        session_id=session_id,
        payload=payload
    )
    
    response = await session_service.process_tool_request(request)
    print(f"   ✅ Tool executed:")
    print(f"      - Status: {response.status}")
    print(f"      - Result: {response.payload.result}")
    
    # 5. Check session for events
    print("\n4. Checking session events...")
    session_data = await session_service.get_session(session_id)
    print(f"   ✅ Session now has {len(session_data['request_ids'])} request(s)")
    
    # 6. Get request details
    if session_data['request_ids']:
        request_id = session_data['request_ids'][0]
        print(f"\n5. Checking request details...")
        request_data = await session_service.repository.get_request(session_id, request_id)
        if request_data:
            print(f"   ✅ Request has {len(request_data.get('event_ids', []))} event(s)")
            
            # Get events for this request
            events = await session_service.repository.get_request_events(session_id, request_id)
            print(f"\n6. Events for this request:")
            for i, event in enumerate(events, 1):
                print(f"      {i}. {event.event_type} - {event.status or 'N/A'}")
    
    print("\n" + "=" * 60)
    print("✅ Complete! Full workflow successful")
    print("=" * 60)


if __name__ == "__main__":
    print("\nChoose an example:")
    print("1. Simple session creation")
    print("2. Full workflow (session + tool execution)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(create_session_example())
    elif choice == "2":
        asyncio.run(create_and_execute_tool())
    else:
        print("Invalid choice!")
