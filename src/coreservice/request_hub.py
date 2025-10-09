"""RequestHub orchestrates Request-Action-Response workflows with hook support."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional

from casefileservice.service import CasefileService
from tool_sessionservice.service import ToolSessionService

from pydantic_models.operations.casefile_ops import (
    CreateCasefilePayload,
    CreateCasefileRequest,
    CreateCasefileResponse,
    AddSessionToCasefilePayload,
    AddSessionToCasefileRequest,
    AddSessionToCasefileResponse,
)
from pydantic_models.operations.tool_session_ops import (
    CreateSessionPayload,
    CreateSessionRequest,
    CreateSessionResponse,
)
from pydantic_models.operations.request_hub_ops import (
    CreateCasefileWithSessionRequest,
    CreateCasefileWithSessionResponse,
    CasefileWithSessionResultPayload,
)
from pydantic_models.base.envelopes import BaseRequest, BaseResponse
from pydantic_models.base.types import RequestStatus

from .policy_patterns import PolicyPatternLoader

logger = logging.getLogger(__name__)

HookHandler = Callable[[str, BaseRequest[Any], Dict[str, Any], Optional[BaseResponse[Any]]], Awaitable[None]]


class RequestHub:
    """Central orchestrator bridging Tool Engineering and R-A-R management."""

    def __init__(
        self,
        casefile_service: Optional[CasefileService] = None,
        tool_session_service: Optional[ToolSessionService] = None,
        policy_loader: Optional[PolicyPatternLoader] = None,
        hook_handlers: Optional[Dict[str, HookHandler]] = None,
    ) -> None:
        self.casefile_service = casefile_service or CasefileService()
        self.tool_session_service = tool_session_service or ToolSessionService()
        self.policy_loader = policy_loader or PolicyPatternLoader()
        self.hook_handlers = hook_handlers or {
            "metrics": self._metrics_hook,
            "audit": self._audit_hook,
        }

    async def dispatch(self, request: BaseRequest[Any]) -> BaseResponse[Any]:
        """Dispatch request to the appropriate workflow based on operation name."""
        if request.operation in {"create_casefile", "workspace.casefile.create_casefile"}:
            return await self._execute_casefile_create(request)  # type: ignore[arg-type]
        if request.operation == "workspace.casefile.create_casefile_with_session":
            return await self._execute_casefile_with_session(request)  # type: ignore[arg-type]

        raise ValueError(f"RequestHub does not handle operation '{request.operation}' yet")

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

        session_id: Optional[str] = None
        session_response: Optional[CreateSessionResponse] = None
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
                "session_request_id": str(session_response.request_id) if session_response else None,
            },
        )

        await self._run_hooks("post", request, context, composite_response)
        self._attach_hook_metadata(composite_response, context)
        return composite_response

    async def _prepare_context(self, request: BaseRequest[Any]) -> Dict[str, Any]:
        policy_defaults = self.policy_loader.load(request.policy_hints.get("pattern")) if request.policy_hints else self.policy_loader.load(None)

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

        context: Dict[str, Any] = {
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
                casefile_id = getattr(request.payload, "casefile_id")
            if casefile_id:
                casefile = await self.casefile_service.repository.get_casefile(casefile_id)  # type: ignore[attr-defined]
                context["casefile"] = casefile.model_dump() if casefile else None

        return context

    async def _run_hooks(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: Dict[str, Any],
        response: Optional[BaseResponse[Any]] = None,
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
        context: Dict[str, Any],
        response: Optional[BaseResponse[Any]],
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
        context: Dict[str, Any],
        response: Optional[BaseResponse[Any]],
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
        context.setdefault("hook_events", []).append({
            "hook": "audit",
            "stage": stage,
            "operation": request.operation,
            "timestamp": datetime.now().isoformat(),
        })

    def _attach_hook_metadata(self, response: BaseResponse[Any], context: Dict[str, Any]) -> None:
        if context.get("hook_events"):
            response.metadata.setdefault("hook_events", context["hook_events"])
        if context.get("audit_log"):
            response.metadata.setdefault("audit_log", context["audit_log"])


async def execute_casefile(request: CreateCasefileRequest) -> CreateCasefileResponse:
    """Module-level helper to execute simple casefile creation via RequestHub."""
    hub = RequestHub()
    return await hub.dispatch(request)


async def execute_casefile_with_session(
    request: CreateCasefileWithSessionRequest,
) -> CreateCasefileWithSessionResponse:
    """Module-level helper to execute the composite workflow via RequestHub."""
    hub = RequestHub()
    response = await hub.dispatch(request)
    if not isinstance(response, CreateCasefileWithSessionResponse):
        raise TypeError("Unexpected response type from RequestHub for composite workflow")
    return response