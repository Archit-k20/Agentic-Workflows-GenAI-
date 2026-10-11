"""Session-owned storage interface and local SQLite/filesystem implementation."""

import hashlib
import json
import secrets
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Protocol
from fastapi import HTTPException

TTL = (
    24 * 60 * 60 - 60
)  # leave one housekeeping interval inside the maximum 24h retention


class Storage(Protocol):
    def create_session(self) -> dict: ...
    def session(self, token: str) -> str: ...
    def put(
        self, session: str, kind: str, name: str, metadata: dict | None = None
    ) -> tuple[str, Path]: ...
    def get(self, session: str, item: str, kind: str | None = None) -> dict: ...
    def clear(self, session: str) -> None: ...


class LocalStorage:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.root.chmod(0o700)
        self.db = self.root / "metadata.sqlite3"
        with self.connect() as db:
            db.executescript(
                "CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, token_hash TEXT UNIQUE, expires REAL); CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, session TEXT, kind TEXT, name TEXT, metadata TEXT);"
            )
        self.cleanup()

    def connect(self):
        return sqlite3.connect(self.db, timeout=30)

    def create_session(self):
        self.cleanup()
        sid = secrets.token_hex(16)
        token = secrets.token_urlsafe(32)
        expires = time.time() + TTL
        with self.connect() as db:
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?)",
                (sid, hashlib.sha256(token.encode()).hexdigest(), expires),
            )
        (self.root / sid).mkdir(mode=0o700)
        return {"token": token, "expires_at": expires}

    def session(self, token):
        self.cleanup()
        with self.connect() as db:
            row = db.execute(
                "SELECT id,expires FROM sessions WHERE token_hash=?",
                (hashlib.sha256(token.encode()).hexdigest(),),
            ).fetchone()
        if not row or row[1] <= time.time():
            raise HTTPException(
                401,
                "Session expired or cleared. Create a session and reprocess your files or URLs.",
            )
        return row[0]

    def put(self, session, kind, name, metadata=None):
        item = secrets.token_hex(16)
        folder = self.root / session / item
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT expires FROM sessions WHERE id=?", (session,)).fetchone()
            if not row or row[0] <= time.time():
                raise HTTPException(401, "Session expired or cleared. Create a session and reprocess your files or URLs.")
            folder.mkdir(parents=True, mode=0o700)
            db.execute("INSERT INTO items VALUES (?,?,?,?,?)", (item, session, kind, name, json.dumps(metadata or {})))
        return item, folder

    def get(self, session, item, kind=None):
        with self.connect() as db:
            row = db.execute(
                "SELECT session,kind,name,metadata FROM items WHERE id=?", (item,)
            ).fetchone()
        if not row or row[0] != session or (kind and row[1] != kind):
            raise HTTPException(
                404,
                "File, artifact or context not found in this session. Reprocess expired inputs.",
            )
        return {
            "id": item,
            "kind": row[1],
            "name": row[2],
            "metadata": json.loads(row[3]),
            "folder": self.root / session / item,
        }

    def clear(self, session):
        with self.connect() as db:
            db.execute("DELETE FROM items WHERE session=?", (session,))
            db.execute("DELETE FROM sessions WHERE id=?", (session,))
        shutil.rmtree(self.root / session, ignore_errors=True)

    def cleanup(self):
        with self.connect() as db:
            expired = [
                r[0]
                for r in db.execute(
                    "SELECT id FROM sessions WHERE expires<=?", (time.time(),)
                )
            ]
        for sid in expired:
            self.clear(sid)
