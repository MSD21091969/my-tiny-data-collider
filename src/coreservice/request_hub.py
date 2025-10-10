"""RequestHub orchestrates Request-Action-Response workflows with hook support."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from casefileservice.service import CasefileService
from communicationservice.service import CommunicationService
from pydantic_models.base.envelopes import BaseRequest, BaseResponse
from pydantic_models.base.types import RequestStatus

# Casefile operations
from pydantic_models.operations.casefile_ops import (
    AddSessionToCasefilePayload,
    AddSessionToCasefileRequest,
    AddSessionToCasefileResponse,
    CheckPermissionRequest,
    CheckPermissionResponse,
    CreateCasefilePayload,
    CreateCasefileRequest,
    CreateCasefileResponse,
    DeleteCasefileRequest,
    DeleteCasefileResponse,
    GetCasefileRequest,
    GetCasefileResponse,
    GrantPermissionRequest,
    GrantPermissionResponse,
    ListCasefilesRequest,
    ListCasefilesResponse,
    ListPermissionsRequest,
    ListPermissionsResponse,
    RevokePermissionRequest,
    RevokePermissionResponse,
    StoreDriveFilesRequest,
    StoreDriveFilesResponse,
    StoreGmailMessagesRequest,
    StoreGmailMessagesResponse,
    StoreSheetDataRequest,
    StoreSheetDataResponse,
    UpdateCasefileRequest,
    UpdateCasefileResponse,
)

# Chat session operations
from pydantic_models.operations.chat_session_ops import (
    CloseChatSessionRequest,
    CloseChatSessionResponse,
    CreateChatSessionRequest,
    CreateChatSessionResponse,
    GetChatSessionRequest,
    GetChatSessionResponse,
    ListChatSessionsRequest,
    ListChatSessionsResponse,
)

# RequestHub composite operations
from pydantic_models.operations.request_hub_ops import (
    CasefileWithSessionResultPayload,
    CreateCasefileWithSessionRequest,
    CreateCasefileWithSessionResponse,
    CreateSessionWithCasefileRequest,
    CreateSessionWithCasefileResponse,
    SessionWithCasefileResultPayload,
)

# Tool session operations
from pydantic_models.operations.tool_execution_ops import (
    ChatRequest,
    ChatResponse,
    ToolRequest,
    ToolResponse,
)
from pydantic_models.operations.tool_session_ops import (
    CloseSessionRequest,
    CloseSessionResponse,
    CreateSessionPayload,
    CreateSessionRequest,
    CreateSessionResponse,
    GetSessionRequest,
    GetSessionResponse,
    ListSessionsRequest,
    ListSessionsResponse,
)
from tool_sessionservice.service import ToolSessionService

from .policy_patterns import PolicyPatternLoader

logger = logging.getLogger(__name__)

HookHandler = Callable[
    [str, BaseRequest[Any], dict[str, Any], BaseResponse[Any] | None], Awaitable[None]
]


class RequestHub:
    """Central orchestrator bridging Tool Engineering and R-A-R management."""

    def __init__(
        self,
        casefile_service: CasefileService | None = None,
        tool_session_service: ToolSessionService | None = None,
        communication_service: CommunicationService | None = None,
        policy_loader: PolicyPatternLoader | None = None,
        hook_handlers: dict[str, HookHandler] | None = None,
    ) -> None:
        self.casefile_service = casefile_service or CasefileService()
        self.tool_session_service = tool_session_service or ToolSessionService()
        self.communication_service = communication_service or CommunicationService()
        self.policy_loader = policy_loader or PolicyPatternLoader()
        self.hook_handlers = hook_handlers or {
            "metrics": self._metrics_hook,
            "audit": self._audit_hook,
            "session_lifecycle": self._session_lifecycle_hook,
        }

    async def dispatch(self, request: BaseRequest[Any]) -> BaseResponse[Any]:
        """Dispatch request to the appropriate workflow based on operation name."""

        # Map operation to handler method
        handlers = {
            # Casefile CRUD operations (5)
            "create_casefile": self._execute_casefile_create,
            "workspace.casefile.create_casefile": self._execute_casefile_create,
            "get_casefile": self._execute_casefile_get,
            "update_casefile": self._execute_casefile_update,
            "list_casefiles": self._execute_casefile_list,
            "delete_casefile": self._execute_casefile_delete,
            # Casefile session management (1)
            "add_session_to_casefile": self._execute_casefile_add_session,
            # Casefile ACL operations (4)
            "grant_permission": self._execute_casefile_grant_permission,
            "revoke_permission": self._execute_casefile_revoke_permission,
            "list_permissions": self._execute_casefile_list_permissions,
            "check_permission": self._execute_casefile_check_permission,
            # Casefile workspace sync operations (3)
            "store_gmail_messages": self._execute_casefile_store_gmail,
            "store_drive_files": self._execute_casefile_store_drive,
            "store_sheet_data": self._execute_casefile_store_sheet,
            # Tool session lifecycle (4)
            "create_session": self._execute_session_create,
            "get_session": self._execute_session_get,
            "list_sessions": self._execute_session_list,
            "close_session": self._execute_session_close,
            # Tool execution (1)
            "tool_execution": self._execute_tool_request,
            "process_tool_request": self._execute_tool_request,
            # Chat session lifecycle (4)
            "create_chat_session": self._execute_chat_create,
            "get_chat_session": self._execute_chat_get,
            "list_chat_sessions": self._execute_chat_list,
            "close_chat_session": self._execute_chat_close,
            # Chat message processing (1)
            "chat": self._execute_chat_process,
            "process_chat_request": self._execute_chat_process,
            # Composite workflows (1)
            "workspace.casefile.create_casefile_with_session": self._execute_casefile_with_session,
            "workspace.session.create_session_with_casefile": self._execute_session_with_casefile,
        }

        handler = handlers.get(request.operation)
        if not handler:
            raise ValueError(
                f"RequestHub does not handle operation '{request.operation}'. "
                f"Available operations: {list(handlers.keys())}"
            )

        return await handler(request)

    async def _execute_casefile_create(
        self,
        request: CreateCasefileRequest,
    ) -> CreateCasefileResponse:
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.create_casefile(request)

        context["casefile_id"] = response.payload.casefile_id
        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_get(
        self,
        request: GetCasefileRequest,
    ) -> GetCasefileResponse:
        """Handler for get_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.get_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_update(
        self,
        request: UpdateCasefileRequest,
    ) -> UpdateCasefileResponse:
        """Handler for update_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.update_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_list(
        self,
        request: ListCasefilesRequest,
    ) -> ListCasefilesResponse:
        """Handler for list_casefiles operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.list_casefiles(request)

        context["status"] = response.status.value
        context["count"] = len(response.payload.casefiles)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_delete(
        self,
        request: DeleteCasefileRequest,
    ) -> DeleteCasefileResponse:
        """Handler for delete_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.delete_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_add_session(
        self,
        request: AddSessionToCasefileRequest,
    ) -> AddSessionToCasefileResponse:
        """Handler for add_session_to_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.add_session_to_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_grant_permission(
        self,
        request: GrantPermissionRequest,
    ) -> GrantPermissionResponse:
        """Handler for grant_permission operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.grant_permission(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_revoke_permission(
        self,
        request: RevokePermissionRequest,
    ) -> RevokePermissionResponse:
        """Handler for revoke_permission operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.revoke_permission(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_list_permissions(
        self,
        request: ListPermissionsRequest,
    ) -> ListPermissionsResponse:
        """Handler for list_permissions operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.list_permissions(request)

        context["status"] = response.status.value
        context["permission_count"] = len(response.payload.permissions)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_check_permission(
        self,
        request: CheckPermissionRequest,
    ) -> CheckPermissionResponse:
        """Handler for check_permission operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.check_permission(request)

        context["status"] = response.status.value
        context["has_permission"] = response.payload.has_permission

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_store_gmail(
        self,
        request: StoreGmailMessagesRequest,
    ) -> StoreGmailMessagesResponse:
        """Handler for store_gmail_messages operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.store_gmail_messages(request)

        context["status"] = response.status.value
        context["messages_stored"] = response.payload.messages_stored

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_store_drive(
        self,
        request: StoreDriveFilesRequest,
    ) -> StoreDriveFilesResponse:
        """Handler for store_drive_files operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.store_drive_files(request)

        context["status"] = response.status.value
        context["files_stored"] = response.payload.files_stored

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_store_sheet(
        self,
        request: StoreSheetDataRequest,
    ) -> StoreSheetDataResponse:
        """Handler for store_sheet_data operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.store_sheet_data(request)

        context["status"] = response.status.value
        context["rows_stored"] = response.payload.rows_stored

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_create(
        self,
        request: CreateSessionRequest,
    ) -> CreateSessionResponse:
        """Handler for create_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.create_session(request)

        context["session_id"] = response.payload.session_id
        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_get(
        self,
        request: GetSessionRequest,
    ) -> GetSessionResponse:
        """Handler for get_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.get_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_list(
        self,
        request: ListSessionsRequest,
    ) -> ListSessionsResponse:
        """Handler for list_sessions operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.list_sessions(request)

        context["status"] = response.status.value
        context["count"] = len(response.payload.sessions)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_close(
        self,
        request: CloseSessionRequest,
    ) -> CloseSessionResponse:
        """Handler for close_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.close_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_chat_create(
        self,
        request: CreateChatSessionRequest,
    ) -> CreateChatSessionResponse:
        """Handler for create_chat_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.communication_service.create_session(request)

        context["chat_session_id"] = response.payload.session_id
        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_chat_get(
        self,
        request: GetChatSessionRequest,
    ) -> GetChatSessionResponse:
        """Handler for get_chat_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.communication_service.get_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_chat_list(
        self,
        request: ListChatSessionsRequest,
    ) -> ListChatSessionsResponse:
        """Handler for list_chat_sessions operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.communication_service.list_sessions(request)

        context["status"] = response.status.value
        context["count"] = len(response.payload.sessions)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_chat_close(
        self,
        request: CloseChatSessionRequest,
    ) -> CloseChatSessionResponse:
        """Handler for close_chat_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.communication_service.close_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_tool_request(
        self,
        request: ToolRequest,
    ) -> ToolResponse:
        """Handler for tool_execution and process_tool_request operations."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.process_tool_request(request)

        context["status"] = response.status.value
        if request.session_id:
            context["session_id"] = request.session_id

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_chat_process(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Handler for chat and process_chat_request operations."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.communication_service.process_chat_request(request)

        context["status"] = response.status.value
        context["chat_session_id"] = request.payload.session_id

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_with_session(
        self,
        request: CreateCasefileWithSessionRequest,
    ) -> CreateCasefileWithSessionResponse:
        # Merge hook channels coming from payload into request scope
        if request.payload.hook_channels:
            merged_hooks = list(dict.fromkeys([*request.hooks, *request.payload.hook_channels]))
            request.hooks = merged_hooks  # type: ignore[assignment]

        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        create_payload = CreateCasefilePayload(
            title=request.payload.title,
            description=request.payload.description or "",
            tags=request.payload.tags,
        )
        create_request = CreateCasefileRequest(
            request_id=request.request_id,
            session_id=request.session_id,
            user_id=request.user_id,
            operation="create_casefile",
            payload=create_payload,
            metadata={**request.metadata, "parent_operation": request.operation},
            context_requirements=request.context_requirements,
            hooks=request.hooks,
            policy_hints=request.policy_hints,
            route_directives=request.route_directives,
        )

        casefile_response = await self.casefile_service.create_casefile(create_request)
        casefile_id = casefile_response.payload.casefile_id
        context["casefile_id"] = casefile_id

        session_id: str | None = None
        session_response: CreateSessionResponse | None = None
        if request.payload.auto_start_session:
            session_payload = CreateSessionPayload(
                casefile_id=casefile_id,
                title=request.payload.session_title,
            )
            session_request = CreateSessionRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                payload=session_payload,
                operation="create_session",
                metadata={**request.metadata, "parent_casefile_id": casefile_id},
                context_requirements=request.context_requirements,
                hooks=request.hooks,
                policy_hints=request.policy_hints,
                route_directives=request.route_directives,
            )
            session_response = await self.tool_session_service.create_session(session_request)
            session_id = session_response.payload.session_id
            context["session_id"] = session_id

            add_payload = AddSessionToCasefilePayload(
                casefile_id=casefile_id,
                session_id=session_id,
                session_type="tool",
            )
            add_request = AddSessionToCasefileRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                operation="add_session_to_casefile",
                payload=add_payload,
                metadata={**request.metadata, "parent_casefile_id": casefile_id},
                context_requirements=request.context_requirements,
                hooks=request.hooks,
                policy_hints=request.policy_hints,
                route_directives=request.route_directives,
            )
            await self.casefile_service.add_session_to_casefile(add_request)

        composite_response = CreateCasefileWithSessionResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=CasefileWithSessionResultPayload(
                casefile_id=casefile_id,
                session_id=session_id,
                hooks_executed=context.get("hooks", []),
            ),
            metadata={
                "casefile_request_id": str(casefile_response.request_id),
                "session_request_id": str(session_response.request_id)
                if session_response
                else None,
            },
        )

        await self._run_hooks("post", request, context, composite_response)
        self._attach_hook_metadata(composite_response, context)
        return composite_response

    async def _execute_session_with_casefile(
        self,
        request: CreateSessionWithCasefileRequest,
    ) -> CreateSessionWithCasefileResponse:
        """Handler for create_session_with_casefile composite operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        # Step 1: Create the tool session
        session_payload = CreateSessionPayload(
            casefile_id=request.payload.casefile_id,
            title=request.payload.title,
        )
        session_request = CreateSessionRequest(
            request_id=request.request_id,
            session_id=request.session_id,
            user_id=request.user_id,
            operation="create_session",
            payload=session_payload,
            metadata={**request.metadata, "parent_operation": request.operation},
            context_requirements=request.context_requirements,
            hooks=request.hooks,
            policy_hints=request.policy_hints,
            route_directives=request.route_directives,
        )

        session_response = await self.tool_session_service.create_session(session_request)
        session_id = session_response.payload.session_id
        context["session_id"] = session_id

        # Step 2: Add session to casefile
        add_payload = AddSessionToCasefilePayload(
            casefile_id=request.payload.casefile_id,
            session_id=session_id,
            session_type=request.payload.session_type,
        )
        add_request = AddSessionToCasefileRequest(
            request_id=request.request_id,
            session_id=request.session_id,
            user_id=request.user_id,
            operation="add_session_to_casefile",
            payload=add_payload,
            metadata={**request.metadata, "parent_operation": request.operation},
            context_requirements=request.context_requirements,
            hooks=request.hooks,
            policy_hints=request.policy_hints,
            route_directives=request.route_directives,
        )

        add_response = await self.casefile_service.add_session_to_casefile(add_request)
        context["total_sessions"] = add_response.payload.total_sessions

        # Step 3: Create composite response
        composite_response = CreateSessionWithCasefileResponse(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=SessionWithCasefileResultPayload(
                session_id=session_id,
                casefile_id=request.payload.casefile_id,
                session_type=request.payload.session_type,
                created_at=session_response.payload.created_at,
                total_sessions=add_response.payload.total_sessions,
            ),
            metadata={
                "session_request_id": str(session_response.request_id),
                "add_request_id": str(add_response.request_id),
            },
        )

        await self._run_hooks("post", request, context, composite_response)
        self._attach_hook_metadata(composite_response, context)
        return composite_response

    async def _prepare_context(self, request: BaseRequest[Any]) -> dict[str, Any]:
        policy_defaults = (
            self.policy_loader.load(request.policy_hints.get("pattern"))
            if request.policy_hints
            else self.policy_loader.load(None)
        )

        combined_requirements = list(
            dict.fromkeys(
                [
                    *policy_defaults.get("context_requirements", []),
                    *request.context_requirements,
                ]
            )
        )
        combined_hooks = list(
            dict.fromkeys(
                [
                    *policy_defaults.get("hooks", []),
                    *request.hooks,
                ]
            )
        )

        context: dict[str, Any] = {
            "policy": policy_defaults,
            "requirements": combined_requirements,
            "hooks": combined_hooks,
            "hook_events": [],
        }

        if "session" in combined_requirements and request.session_id:
            session = await self.tool_session_service.repository.get_session(request.session_id)  # type: ignore[attr-defined]
            context["session"] = session.model_dump() if session else None

        if "casefile" in combined_requirements:
            casefile_id = request.metadata.get("casefile_id")
            if not casefile_id and hasattr(request.payload, "casefile_id"):
                casefile_id = request.payload.casefile_id  # type: ignore[attr-defined]
            if casefile_id:
                casefile = await self.casefile_service.repository.get_casefile(casefile_id)  # type: ignore[attr-defined]
                context["casefile"] = casefile.model_dump() if casefile else None

        return context

    async def _run_hooks(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: dict[str, Any],
        response: BaseResponse[Any] | None = None,
    ) -> None:
        for hook_name in context.get("hooks", []):
            handler = self.hook_handlers.get(hook_name)
            if not handler:
                continue
            await handler(stage, request, context, response)

    async def _metrics_hook(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: dict[str, Any],
        response: BaseResponse[Any] | None,
    ) -> None:
        event = {
            "hook": "metrics",
            "stage": stage,
            "operation": request.operation,
            "timestamp": datetime.now().isoformat(),
        }
        if response:
            event["response_status"] = response.status.value
        context.setdefault("hook_events", []).append(event)

    async def _audit_hook(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: dict[str, Any],
        response: BaseResponse[Any] | None,
    ) -> None:
        entry = {
            "hook": "audit",
            "stage": stage,
            "operation": request.operation,
            "user_id": request.user_id,
            "session_id": request.session_id,
        }
        if response:
            entry["status"] = response.status.value

        # Add to audit_log
        context.setdefault("audit_log", []).append(entry)

        # Also add to hook_events for consistency with metrics hook
        context.setdefault("hook_events", []).append(
            {
                "hook": "audit",
                "stage": stage,
                "operation": request.operation,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _session_lifecycle_hook(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: dict[str, Any],
        response: BaseResponse[Any] | None,
    ) -> None:
        """Manage session lifecycle automatically (expiration, activity tracking)."""
        if stage == "pre":
            # Check if session exists and is expired
            session = context.get("session")
            if session and not session.get("active"):
                logger.info(f"Session {session['session_id']} is inactive/expired")
                context["session_inactive"] = True

                # Record hook event
                context.setdefault("hook_events", []).append(
                    {
                        "hook": "session_lifecycle",
                        "stage": stage,
                        "action": "session_inactive_detected",
                        "session_id": session["session_id"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        elif stage == "post":
            # Update session activity timestamp if session is active
            session = context.get("session")
            if session and session.get("active") and request.session_id:
                # Update last_activity in the repository
                try:
                    await self.tool_session_service.repository.update_activity(request.session_id)  # type: ignore[attr-defined]

                    # Record hook event
                    context.setdefault("hook_events", []).append(
                        {
                            "hook": "session_lifecycle",
                            "stage": stage,
                            "action": "activity_updated",
                            "session_id": request.session_id,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to update session activity: {e}")

    def _attach_hook_metadata(self, response: BaseResponse[Any], context: dict[str, Any]) -> None:
        if context.get("hook_events"):
            response.metadata.setdefault("hook_events", context["hook_events"])
        if context.get("audit_log"):
            response.metadata.setdefault("audit_log", context["audit_log"])


async def execute_casefile(request: CreateCasefileRequest) -> CreateCasefileResponse:
    """Module-level helper to execute simple casefile creation via RequestHub."""
    hub = RequestHub()
    response = await hub.dispatch(request)
    if not isinstance(response, CreateCasefileResponse):
        raise TypeError("Unexpected response type from RequestHub for casefile workflow")
    return response


async def execute_casefile_with_session(
    request: CreateCasefileWithSessionRequest,
) -> CreateCasefileWithSessionResponse:
    """Module-level helper to execute the composite workflow via RequestHub."""
    hub = RequestHub()
    response = await hub.dispatch(request)
    if not isinstance(response, CreateCasefileWithSessionResponse):
        raise TypeError("Unexpected response type from RequestHub for composite workflow")
    return response


async def create_session_with_casefile(
    request: CreateSessionWithCasefileRequest,
) -> CreateSessionWithCasefileResponse:
    """Module-level helper to execute the create session with casefile workflow via RequestHub."""
    hub = RequestHub()
    response = await hub.dispatch(request)
    if not isinstance(response, CreateSessionWithCasefileResponse):
        raise TypeError("Unexpected response type from RequestHub for session-casefile workflow")
    return response
