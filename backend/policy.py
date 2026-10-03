"""Persistent anonymous fair-use and conservative hosted-compute reservations."""

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timezone
from fastapi import HTTPException

LIMITS = {"text": 20, "image": 2, "audio": 5, "context": 3}


class Policy:
    def __init__(self, storage):
        self.storage = storage
        with storage.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS policy_secret (id INTEGER PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS usage (day TEXT, actor TEXT, category TEXT, amount INTEGER,
              PRIMARY KEY(day,actor,category));
            CREATE TABLE IF NOT EXISTS active_runs (actor TEXT PRIMARY KEY, lease TEXT, expires REAL);
            CREATE TABLE IF NOT EXISTS starts (actor TEXT, at REAL);
            CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, day TEXT, category TEXT, amount REAL);
            """)
            db.execute(
                "INSERT OR IGNORE INTO policy_secret VALUES (1,?)",
                (secrets.token_hex(32),),
            )
            self.secret = (
                os.environ.get("TRACE_IP_HASH_SECRET")
                or db.execute("SELECT value FROM policy_secret WHERE id=1").fetchone()[
                    0
                ]
            )

    def actor(self, ip):
        return (
            "ip:"
            + hmac.new(self.secret.encode(), ip.encode(), hashlib.sha256).hexdigest()
        )

    @staticmethod
    def day():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def reset():
        return (int(time.time()) // 86400 + 1) * 86400

    def usage(self, sid, actor):
        day = self.day()
        with self.storage.connect() as db:
            used = {
                c: max(
                    [
                        db.execute(
                            "SELECT amount FROM usage WHERE day=? AND actor=? AND category=?",
                            (day, a, c),
                        ).fetchone()
                        or (0,)
                        for a in (sid, actor)
                    ]
                )[0]
                for c in LIMITS
            }
        return {
            "remaining": {c: max(0, LIMITS[c] - used[c]) for c in LIMITS},
            "limits": LIMITS,
            "reset_at": self.reset(),
            "shared_network": True,
        }

    def begin(self, sid, actor, categories):
        lease, now, day = secrets.token_hex(16), time.time(), self.day()
        with self.storage.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM active_runs WHERE expires<=?", (now,))
            db.execute("DELETE FROM starts WHERE at<?", (now - 60,))
            db.execute("DELETE FROM usage WHERE day<?", (day,))
            db.execute("DELETE FROM reservations WHERE day<?", (day,))
            if db.execute(
                "SELECT 1 FROM active_runs WHERE actor IN (?,?)", (sid, actor)
            ).fetchone():
                raise HTTPException(
                    429,
                    "One workflow is already running for this visitor/network. Retry explicitly after it finishes.",
                )
            if (
                db.execute(
                    "SELECT COUNT(*) FROM starts WHERE actor=?", (actor,)
                ).fetchone()[0]
                >= 5
            ):
                raise HTTPException(
                    429, "Please wait a minute before starting another workflow."
                )
            for a in (sid, actor):
                for c in categories:
                    used = db.execute(
                        "SELECT amount FROM usage WHERE day=? AND actor=? AND category=?",
                        (day, a, c),
                    ).fetchone()
                    if used and used[0] >= LIMITS[c]:
                        raise HTTPException(
                            429,
                            f"Daily {c} allowance reached. It resets at 00:00 UTC; people sharing a network may share a limit.",
                        )
                    db.execute(
                        "INSERT INTO usage VALUES (?,?,?,1) ON CONFLICT(day,actor,category) DO UPDATE SET amount=amount+1",
                        (day, a, c),
                    )
                db.execute(
                    "INSERT INTO active_runs VALUES (?,?,?)", (a, lease, now + 900)
                )
            db.execute("INSERT INTO starts VALUES (?,?)", (actor, now))
        return {
            "lease": lease,
            "day": day,
            "actors": (sid, actor),
            "categories": categories,
        }

    def finish(self, record, refund=()):
        with self.storage.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM active_runs WHERE lease=?", (record["lease"],))
            for actor in record["actors"]:
                for category in refund:
                    db.execute(
                        "UPDATE usage SET amount=MAX(0,amount-1) WHERE day=? AND actor=? AND category=?",
                        (record["day"], actor, category),
                    )

    def reserve(self, category, amount):
        day, rid = self.day(), secrets.token_hex(16)
        with self.storage.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            total = db.execute(
                "SELECT COALESCE(SUM(amount),0) FROM reservations WHERE day=?", (day,)
            ).fetchone()[0]
            text = db.execute(
                "SELECT COALESCE(SUM(amount),0) FROM reservations WHERE day=? AND category='text'",
                (day,),
            ).fetchone()[0]
            if total + amount > 8000 or (category == "text" and text + amount > 7000):
                raise Capacity(
                    "The shared hosted allowance is unavailable until 00:00 UTC."
                )
            db.execute(
                "INSERT INTO reservations VALUES (?,?,?,?)",
                (rid, day, category, amount),
            )
        return rid

    def reconcile(self, rid, amount):
        if amount is not None:
            with self.storage.connect() as db:
                db.execute(
                    "UPDATE reservations SET amount=? WHERE id=?", (max(0, amount), rid)
                )


class Capacity(RuntimeError):
    pass
