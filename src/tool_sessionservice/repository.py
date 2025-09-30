"""Repository for tool session data persistence."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import logging

from ..pydantic_models.tool_session import ToolSession, ToolRequest, ToolResponse

logger = logging.getLogger(__name__)


class ToolSessionRepository:
    """Repository for tool session data persistence."""

    _UNASSIGNED_KEY = "_unassigned"

    def __init__(self, use_mocks: bool = False):
        self.use_mocks = use_mocks
        if use_mocks:
            self._init_mock_storage()
        else:
            self._init_firestore()

    @staticmethod
    def _casefile_key(casefile_id: Optional[str]) -> str:
        return casefile_id or ToolSessionRepository._UNASSIGNED_KEY

    # ------------------------------------------------------------------
    # Mock storage implementation
    # ------------------------------------------------------------------
    def _init_mock_storage(self) -> None:
        self.sessions_by_casefile: Dict[str, Dict[str, ToolSession]] = {}
        self.session_index: Dict[str, str] = {}

    async def _mock_create_or_update(self, session: ToolSession) -> None:
        key = self._casefile_key(session.casefile_id)
        self.sessions_by_casefile.setdefault(key, {})[session.session_id] = session
        self.session_index[session.session_id] = key

    async def _mock_get(self, session_id: str) -> Optional[ToolSession]:
        key = self.session_index.get(session_id)
        if key is None:
            return None
        return self.sessions_by_casefile.get(key, {}).get(session_id)

    async def _mock_delete(self, session_id: str) -> None:
        key = self.session_index.pop(session_id, None)
        if key and key in self.sessions_by_casefile:
            self.sessions_by_casefile[key].pop(session_id, None)

    async def _mock_list(self, user_id: Optional[str], casefile_id: Optional[str]) -> List[ToolSession]:
        sessions: List[ToolSession] = []
        if casefile_id:
            key = self._casefile_key(casefile_id)
            sessions = list(self.sessions_by_casefile.get(key, {}).values())
        else:
            for bucket in self.sessions_by_casefile.values():
                sessions.extend(bucket.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        return sessions

    # ------------------------------------------------------------------
    # Firestore implementation
    # ------------------------------------------------------------------
    def _init_firestore(self) -> None:
        try:
            import firebase_admin
            from firebase_admin import firestore

            logger.info("Initializing Firestore for ToolSessionRepository")

            try:
                self.app = firebase_admin.get_app()
                logger.info("Using existing Firebase app")
            except ValueError:
                cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path:
                    logger.info(f"Initializing Firebase app with credentials from {cred_path}")
                else:
                    logger.warning("No GOOGLE_APPLICATION_CREDENTIALS found, using default credentials")
                self.app = firebase_admin.initialize_app()

            database_id = os.environ.get("FIRESTORE_DATABASE", "mds-objects")
            logger.info(f"Using Firestore database: {database_id}")

            self.db = firestore.client(database_id=database_id)
            self.casefiles_collection = self.db.collection("casefiles")
            self.session_index_collection = self.db.collection("tool_sessions_index")

            logger.info("Firestore initialized successfully")

        except ImportError as exc:
            print(f"Warning: firebase-admin package not found ({exc}), falling back to mock storage")
            self.use_mocks = True
            self._init_mock_storage()
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"Error initializing Firestore: {exc}")
            import traceback
            traceback.print_exc()
            self.use_mocks = True
            self._init_mock_storage()

    def _session_collection(self, casefile_id: Optional[str]):
        key = self._casefile_key(casefile_id)
        return self.casefiles_collection.document(key).collection("tool_sessions")

    def _session_doc(self, casefile_id: Optional[str], session_id: str):
        return self._session_collection(casefile_id).document(session_id)

    def _replace_subcollection(self, parent_ref, name: str, payloads: Dict[str, Dict[str, Any]]) -> None:
        collection_ref = parent_ref.collection(name)
        existing_docs = list(collection_ref.stream())
        for doc in existing_docs:
            doc.reference.delete()
        for doc_id, data in payloads.items():
            collection_ref.document(doc_id).set(data)

    def _load_subcollection(self, parent_ref, name: str) -> Dict[str, Dict[str, Any]]:
        collection_ref = parent_ref.collection(name)
        return {doc.id: doc.to_dict() for doc in collection_ref.stream()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def create_session(self, session: ToolSession) -> None:
        if self.use_mocks:
            await self._mock_create_or_update(session)
            return

        session_doc = self._session_doc(session.casefile_id, session.session_id)
        metadata = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "casefile_id": session.casefile_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "request_index": session.request_index,
            "active": session.active,
        }
        session_doc.set(metadata)

        requests_payload = {rid: req.model_dump(mode="json") for rid, req in session.requests.items()}
        responses_payload = {rid: resp.model_dump(mode="json") for rid, resp in session.responses.items()}
        events_payload = {}
        for idx, event in enumerate(session.events):
            event_id = event.get("event_id") or f"event_{idx:04d}"
            events_payload[event_id] = event

        self._replace_subcollection(session_doc, "requests", requests_payload)
        self._replace_subcollection(session_doc, "responses", responses_payload)
        self._replace_subcollection(session_doc, "events", events_payload)

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
        if self.use_mocks:
            return await self._mock_get(session_id)

        index_snapshot = self.session_index_collection.document(session_id).get()
        if not index_snapshot.exists:
            return None
        index_data = index_snapshot.to_dict()
        casefile_id = index_data.get("casefile_id")

        session_snapshot = self._session_doc(casefile_id, session_id).get()
        if not session_snapshot.exists:
            return None

        session_data = session_snapshot.to_dict()
        session_doc_ref = session_snapshot.reference

        request_docs = self._load_subcollection(session_doc_ref, "requests")
        response_docs = self._load_subcollection(session_doc_ref, "responses")
        event_docs = self._load_subcollection(session_doc_ref, "events")

        requests = {rid: ToolRequest.model_validate(data) for rid, data in request_docs.items()}
        responses = {rid: ToolResponse.model_validate(data) for rid, data in response_docs.items()}
        events = sorted(event_docs.values(), key=lambda evt: evt.get("timestamp", ""))

        return ToolSession(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            casefile_id=session_data.get("casefile_id"),
            created_at=session_data.get("created_at", datetime.now().isoformat()),
            updated_at=session_data.get("updated_at", datetime.now().isoformat()),
            requests=requests,
            responses=responses,
            request_index=session_data.get("request_index", {}),
            events=events,
            active=session_data.get("active", True)
        )

    async def update_session(self, session: ToolSession) -> None:
        if self.use_mocks:
            await self._mock_create_or_update(session)
            return

        await self.create_session(session)

    async def list_sessions(self, user_id: Optional[str] = None, casefile_id: Optional[str] = None) -> List[ToolSession]:
        if self.use_mocks:
            return await self._mock_list(user_id, casefile_id)

        sessions: List[ToolSession] = []

        if casefile_id:
            collection = self._session_collection(casefile_id)
            for snapshot in collection.stream():
                session = await self.get_session(snapshot.id)
                if session:
                    sessions.append(session)
            return sessions

        query = self.session_index_collection
        if user_id:
            query = query.where("user_id", "==", user_id)

        for index_snapshot in query.stream():
            session = await self.get_session(index_snapshot.id)
            if session:
                sessions.append(session)

        return sessions

    async def delete_session(self, session_id: str) -> None:
        if self.use_mocks:
            await self._mock_delete(session_id)
            return

        index_snapshot = self.session_index_collection.document(session_id).get()
        if not index_snapshot.exists:
            return

        index_data = index_snapshot.to_dict()
        casefile_id = index_data.get("casefile_id")
        session_doc = self._session_doc(casefile_id, session_id)

        # Clean up subcollections
        for name in ("requests", "responses", "events"):
            collection_ref = session_doc.collection(name)
            for doc in collection_ref.stream():
                doc.reference.delete()

        session_doc.delete()
        self.session_index_collection.document(session_id).delete()