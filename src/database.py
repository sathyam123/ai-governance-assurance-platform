import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from src.config import DB_PATH

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_systems (
          system_id TEXT PRIMARY KEY, system_name TEXT NOT NULL,
          business_purpose TEXT NOT NULL, business_owner TEXT NOT NULL,
          technical_owner TEXT NOT NULL, department TEXT NOT NULL,
          system_type TEXT NOT NULL, model_provider TEXT NOT NULL,
          data_categories TEXT NOT NULL, user_groups TEXT NOT NULL,
          deployment_status TEXT NOT NULL, external_users TEXT NOT NULL,
          human_oversight TEXT NOT NULL, inventory_status TEXT NOT NULL,
          validation_messages TEXT NOT NULL,
          risk_status TEXT NOT NULL DEFAULT 'Not assessed',
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
        conn.commit()

def create_ai_system(profile):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    values = {**profile, "system_id": f"AI-{uuid4().hex[:8].upper()}",
              "risk_status":"Not assessed", "created_at":now, "updated_at":now}
    cols = list(values)
    with _connect() as conn:
        conn.execute(f"INSERT INTO ai_systems ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",
                     [values[c] for c in cols])
        conn.commit()
    return values["system_id"]

def list_ai_systems():
    with _connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM ai_systems ORDER BY created_at DESC").fetchall()]

def get_ai_system(system_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM ai_systems WHERE system_id=?", (system_id,)).fetchone()
    return dict(row) if row else None

def init_risk_assessment_table():
    with _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_assessments (
            assessment_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            overall_score INTEGER NOT NULL,
            overall_risk TEXT NOT NULL,
            assessment_details TEXT NOT NULL,
            review_status TEXT NOT NULL DEFAULT 'Pending review',
            reviewer_notes TEXT DEFAULT '',
            assessed_at TEXT NOT NULL,
            FOREIGN KEY (system_id) REFERENCES ai_systems(system_id)
        )
        """)
        conn.commit()

def save_risk_assessment(system_id, assessment):
    import json

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    assessment_id = f"RA-{uuid4().hex[:8].upper()}"

    details = json.dumps(assessment["dimension_results"])

    with _connect() as conn:
        conn.execute("""
            INSERT INTO risk_assessments (
                assessment_id, system_id, overall_score,
                overall_risk, assessment_details,
                review_status, reviewer_notes, assessed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assessment_id,
            system_id,
            assessment["overall_score"],
            assessment["overall_risk"],
            details,
            "Pending review",
            "",
            now
        ))

        conn.execute("""
            UPDATE ai_systems
            SET risk_status = ?, updated_at = ?
            WHERE system_id = ?
        """, (assessment["overall_risk"], now, system_id))

        conn.commit()

    return assessment_id


def list_risk_assessments(system_id=None):
    with _connect() as conn:
        if system_id:
            rows = conn.execute("""
                SELECT * FROM risk_assessments
                WHERE system_id = ?
                ORDER BY assessed_at DESC
            """, (system_id,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM risk_assessments
                ORDER BY assessed_at DESC
            """).fetchall()

    return [dict(row) for row in rows]


def update_assessment_review(assessment_id, review_status, reviewer_notes):
    with _connect() as conn:
        conn.execute("""
            UPDATE risk_assessments
            SET review_status = ?, reviewer_notes = ?
            WHERE assessment_id = ?
        """, (review_status, reviewer_notes, assessment_id))
        conn.commit()
