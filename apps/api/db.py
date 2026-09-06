"""
EdgeShield Mesh - In-Memory and SQLite Database Layer
Supports instant zero-dependency local startup with persistent SQLite backing,
and optional PostgreSQL connection if configured.
"""
import os
import json
import sqlite3
import aiosqlite
from typing import Optional

DB_PATH = os.getenv("EDGESHIELD_DB_PATH", "edgeshield_local.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")


async def init_db():
    """Initialize SQLite database tables if not present."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            device_type TEXT NOT NULL,
            zone TEXT NOT NULL,
            owner TEXT,
            status TEXT NOT NULL,
            firmware_version TEXT NOT NULL,
            hardware_rev TEXT,
            ip_address TEXT,
            mac_address TEXT,
            last_seen TEXT NOT NULL,
            created_at TEXT NOT NULL,
            telemetry_interval_sec INTEGER,
            expected_topics TEXT,
            allowed_actuators TEXT,
            is_virtual INTEGER,
            metadata TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            event_id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            device_type TEXT NOT NULL,
            zone TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            seq INTEGER,
            nonce TEXT,
            payload_hash TEXT,
            battery_level REAL,
            signal_rssi INTEGER,
            measurements TEXT,
            is_valid INTEGER,
            validation_errors TEXT,
            received_at TEXT NOT NULL,
            raw_id TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            device_id TEXT NOT NULL,
            detector_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence REAL,
            observed_facts TEXT,
            derived_findings TEXT,
            recommendations TEXT,
            evidence_items TEXT,
            citations TEXT,
            risk_assessment TEXT,
            recommended_action TEXT,
            limitations TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            target_device_id TEXT NOT NULL,
            scope TEXT NOT NULL,
            reason TEXT NOT NULL,
            impact_summary TEXT,
            rollback_procedure TEXT,
            requires_approval INTEGER,
            parameters TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT NOT NULL,
            idempotency_key TEXT UNIQUE,
            executed_at TEXT,
            execution_result TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            status TEXT NOT NULL,
            actor_username TEXT NOT NULL,
            actor_role TEXT NOT NULL,
            reason TEXT NOT NULL,
            idempotency_key TEXT UNIQUE,
            action_taken_at TEXT NOT NULL,
            signature_or_token_hash TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            actor TEXT NOT NULL,
            actor_role TEXT NOT NULL,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            details TEXT,
            status TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            entry_hash TEXT NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active INTEGER,
            created_at TEXT NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS detection_rules (
            rule_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            detector_id TEXT NOT NULL,
            enabled INTEGER,
            severity TEXT NOT NULL,
            parameters TEXT,
            description TEXT
        )
        """)

        await db.commit()
