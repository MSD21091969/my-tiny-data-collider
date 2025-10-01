"""Repository for tool session data persistence."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import logging

# Firestore imports (required – no mock fallback retained)
try:  # Import eagerly; failure is a hard error for this repository now.
    import firebase_admin  # type: ignore
    from firebase_admin import firestore  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "firebase_admin is required for ToolSessionRepository after mock removal."
    ) from exc

from ..pydantic_models.tool_session import ToolSession, ToolRequest, ToolResponse, ToolEvent

logger = logging.getLogger(__name__)


class ToolSessionRepository:
    """Firestore-backed repository for tool session data persistence (no mock mode)."""

    def __init__(self, *_, **__):  # ignore legacy params
        self._init_firestore()

    # ------------------------------------------------------------------
    # Firestore implementation
    # ------------------------------------------------------------------
    def _init_firestore(self) -> None:
        logger.info("Initializing Firestore for ToolSessionRepository (mock removed)")
        try:
            try:
                self.app = firebase_admin.get_app()  # type: ignore[attr-defined]
                logger.info("Using existing Firebase app")
            except ValueError:
                cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path:
                    logger.info(f"Initializing Firebase app with credentials from {cred_path}")
                else:
                    logger.info("Initializing Firebase app with default credentials")
                self.app = firebase_admin.initialize_app()  # type: ignore[attr-defined]

            database_id = os.environ.get("FIRESTORE_DATABASE", "mds-objects")
            self.db = firestore.client(database_id=database_id)  # type: ignore
            self.session_index_collection = self.db.collection("tool_sessions_index")
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to initialize Firestore: {exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def create_session(self, session: ToolSession) -> None:
        """Create a new session in Firestore."""
        # Store session metadata only (no requests/events here)
        metadata = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "casefile_id": session.casefile_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "request_ids": session.request_ids,
            "active": session.active,
        }
        
        # Store in /sessions/{session_id}
        session_doc = self.db.collection("sessions").document(session.session_id)
        session_doc.set(metadata)
        
        # Index for quick lookups
        index_doc = {
            "session_id": session.session_id,
            "casefile_id": session.casefile_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "active": session.active,
        }
        self.session_index_collection.document(session.session_id).set(index_doc)

    async def get_session(self, session_id: str) -> Optional[ToolSession]:
        """Get session by ID - returns metadata only, requests/events loaded separately."""
        session_doc = self.db.collection("sessions").document(session_id).get()
        if not session_doc.exists:
            return None

        session_data = session_doc.to_dict()
        return ToolSession(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            casefile_id=session_data.get("casefile_id"),
            created_at=session_data.get("created_at", datetime.now().isoformat()),
            updated_at=session_data.get("updated_at", datetime.now().isoformat()),
            request_ids=session_data.get("request_ids", []),
            active=session_data.get("active", True)
        )

    async def update_session(self, session: ToolSession) -> None:
        """Update session metadata."""
        metadata = {
            "updated_at": session.updated_at,
            "request_ids": session.request_ids,
            "active": session.active,
        }
        session_doc = self.db.collection("sessions").document(session.session_id)
        session_doc.set(metadata, merge=True)
        
        # Update index
        self.session_index_collection.document(session.session_id).set({
            "updated_at": session.updated_at,
            "active": session.active,
        }, merge=True)
    
    async def add_request_to_session(self, session_id: str, request: ToolRequest, response: Optional[ToolResponse] = None) -> None:
        """Add a request (and optional response) to a session."""
        request_id = str(request.request_id)
        
        # Store in /sessions/{session_id}/requests/{request_id}
        request_doc = self.db.collection("sessions").document(session_id).collection("requests").document(request_id)
        request_data = {
            "request": request.model_dump(mode="json"),
            "response": response.model_dump(mode="json") if response else None,
            "event_ids": request.event_ids,
            "created_at": request.timestamp,
            "updated_at": datetime.now().isoformat()
        }
        request_doc.set(request_data)
    
    async def update_request_response(self, session_id: str, request_id: str, response: ToolResponse) -> None:
        """Update the response for a request."""
        request_doc = self.db.collection("sessions").document(session_id).collection("requests").document(request_id)
        request_doc.set({
            "response": response.model_dump(mode="json"),
            "updated_at": datetime.now().isoformat()
        }, merge=True)
    
    async def add_event_to_request(self, session_id: str, request_id: str, event: ToolEvent) -> None:
        """Add a ToolEvent to a request's events subcollection."""
        # Store in /sessions/{session_id}/requests/{request_id}/events/{event_id}
        event_doc = (self.db.collection("sessions")
                     .document(session_id)
                     .collection("requests")
                     .document(request_id)
                     .collection("events")
                     .document(event.event_id))
        event_doc.set(event.model_dump(mode="json"))
        
        # Update request's event_ids list
        request_doc = self.db.collection("sessions").document(session_id).collection("requests").document(request_id)
        request_doc.set({
            "event_ids": firestore.ArrayUnion([event.event_id])
        }, merge=True)
    
    async def get_request(self, session_id: str, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a request with its response."""
        request_doc = (self.db.collection("sessions")
                       .document(session_id)
                       .collection("requests")
                       .document(request_id)
                       .get())
        if not request_doc.exists:
            return None
        return request_doc.to_dict()
    
    async def get_request_events(self, session_id: str, request_id: str) -> List[ToolEvent]:
        """Get all events for a request."""
        events_collection = (self.db.collection("sessions")
                             .document(session_id)
                             .collection("requests")
                             .document(request_id)
                             .collection("events"))
        
        events = []
        for event_doc in events_collection.order_by("timestamp").stream():
            event_data = event_doc.to_dict()
            events.append(ToolEvent(**event_data))
        return events

    async def list_sessions(self, user_id: Optional[str] = None, casefile_id: Optional[str] = None) -> List[ToolSession]:
        """List sessions with optional filtering."""
        sessions: List[ToolSession] = []

        query = self.session_index_collection
        if user_id:
            query = query.where("user_id", "==", user_id)
        if casefile_id:
            query = query.where("casefile_id", "==", casefile_id)

        for index_snapshot in query.stream():
            session = await self.get_session(index_snapshot.id)
            if session:
                sessions.append(session)

        return sessions

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all its subcollections."""
        session_doc = self.db.collection("sessions").document(session_id)

        # Delete all requests and their events
        requests_collection = session_doc.collection("requests")
        for request_doc in requests_collection.stream():
            # Delete events subcollection
            events_collection = request_doc.reference.collection("events")
            for event_doc in events_collection.stream():
                event_doc.reference.delete()
            # Delete request
            request_doc.reference.delete()

        # Delete session
        session_doc.delete()
        
        # Delete index
        self.session_index_collection.document(session_id).delete()