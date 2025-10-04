"""Lightweight firebase_admin stub for test environment.

Provides minimal surface area to satisfy ToolSessionRepository dependencies
without requiring real Firebase credentials or network access.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import uuid


class _Document:
    def __init__(self, store: Dict[str, Any], doc_id: str | None = None):
        self._store = store
        self.id = doc_id or str(uuid.uuid4())

    # Firestore document API
    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        if merge and self.id in self._store:
            self._store[self.id].update(data)
        else:
            self._store[self.id] = dict(data)

    def get(self) -> "_Snapshot":
        exists = self.id in self._store
        data = self._store.get(self.id, {})
        return _Snapshot(exists=exists, data=data)

    def delete(self) -> None:
        self._store.pop(self.id, None)

    def collection(self, name: str) -> "_Collection":
        collections = self._store.setdefault("__collections__", {})
        collection_store = collections.setdefault(name, {})
        return _Collection(collection_store)


class _Collection:
    def __init__(self, store: Dict[str, Any]):
        self._store = store

    def document(self, doc_id: str | None = None) -> _Document:
        return _Document(self._store, doc_id)

    def set(self, data: Dict[str, Any]) -> None:
        self._store.update(data)

    def where(self, *_, **__) -> "_Collection":
        return self

    def order_by(self, *_args, **_kwargs) -> "_Collection":
        return self

    def stream(self) -> List[_Snapshot]:
        snapshots = []
        for doc_id, value in list(self._store.items()):
            if doc_id == "__collections__":
                continue
            snapshots.append(_Snapshot(True, value, doc_id))
        return snapshots


@dataclass
class _Snapshot:
    exists: bool
    data: Dict[str, Any]
    id: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)


@dataclass
class _FirestoreClient:
    database_id: str
    _root: Dict[str, Any] = field(default_factory=dict)

    def collection(self, name: str) -> _Collection:
        store = self._root.setdefault(name, {})
        return _Collection(store)


class firestore:  # mimic firebase_admin.firestore module
    @staticmethod
    def client(database_id: str | None = None) -> _FirestoreClient:
        return _FirestoreClient(database_id or "stub-db")

    class ArrayUnion(list):
        def __init__(self, values: List[Any]):
            super().__init__(values)


_app_instance: object | None = None


def initialize_app(*_args, **_kwargs) -> object:
    global _app_instance
    if _app_instance is None:
        _app_instance = object()
    return _app_instance


def get_app() -> object:
    if _app_instance is None:
        raise ValueError("App not initialized")
    return _app_instance
