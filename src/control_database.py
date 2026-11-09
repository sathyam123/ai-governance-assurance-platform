
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from src.config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_control_tables():
    """Create governance control tables without changing existing tables."""

    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS governance_controls (
            control_id TEXT PRIMARY KEY,
            control_code TEXT NOT NULL UNIQUE,
            domain TEXT NOT NULL,
            title TEXT NOT NULL,
            objective TEXT NOT NULL,
            guidance TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS control_framework_mappings (
            mapping_id TEXT PRIMARY KEY,
            control_id TEXT NOT NULL,
            framework TEXT NOT NULL,
            reference TEXT NOT NULL,
            mapping_note TEXT DEFAULT '',
            FOREIGN KEY (control_id)
                REFERENCES governance_controls(control_id),
            UNIQUE(control_id, framework, reference)
        );

        CREATE TABLE IF NOT EXISTS system_control_assessments (
            assessment_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            control_id TEXT NOT NULL,
            control_owner TEXT DEFAULT '',
            implementation_status TEXT NOT NULL DEFAULT 'Not assessed',
            effectiveness_status TEXT NOT NULL DEFAULT 'Not evaluated',
            reviewer TEXT DEFAULT '',
            review_notes TEXT DEFAULT '',
            assessed_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (system_id)
                REFERENCES ai_systems(system_id),
            FOREIGN KEY (control_id)
                REFERENCES governance_controls(control_id),
            UNIQUE(system_id, control_id)
        );

        CREATE TABLE IF NOT EXISTS control_evidence (
            evidence_id TEXT PRIMARY KEY,
            assessment_id TEXT NOT NULL,
            evidence_name TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            evidence_location TEXT DEFAULT '',
            description TEXT DEFAULT '',
            review_status TEXT NOT NULL DEFAULT 'Pending review',
            reviewer_notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (assessment_id)
                REFERENCES system_control_assessments(assessment_id)
        );

        CREATE TABLE IF NOT EXISTS control_remediation_actions (
            action_id TEXT PRIMARY KEY,
            assessment_id TEXT NOT NULL,
            action_description TEXT NOT NULL,
            action_owner TEXT NOT NULL,
            due_date TEXT DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Open',
            closure_notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (assessment_id)
                REFERENCES system_control_assessments(assessment_id)
        );
        """)
        conn.commit()


# Starter control library.
# These are practical prototype controls, not a complete framework checklist.
# Framework references are indicative mappings and should be verified
# against the applicable official framework/standard before formal use.

STARTER_CONTROLS = [
    {
        "code": "GOV-001",
        "domain": "Governance and accountability",
        "title": "AI governance policy",
        "objective": "Ensure the organisation has documented expectations for responsible AI use.",
        "guidance": "Check for an approved AI policy, scope, responsibilities, review cycle and communication.",
        "mappings": [
            ("NIST AI RMF", "GOVERN 1.1", "Policies and processes for AI risk management."),
            ("ISO/IEC 42001", "Clause 5", "Leadership and organisational commitment.")
        ]
    },
    {
        "code": "GOV-002",
        "domain": "Governance and accountability",
        "title": "Roles and responsibilities",
        "objective": "Establish accountable business, technical and oversight owners.",
        "guidance": "Verify that system ownership, risk ownership, escalation and approval responsibilities are assigned.",
        "mappings": [
            ("NIST AI RMF", "GOVERN 2.1", "Accountability structures and responsibilities."),
            ("ISO/IEC 42001", "Clause 5", "Leadership, roles and responsibilities.")
        ]
    },
    {
        "code": "INV-001",
        "domain": "AI inventory and lifecycle",
        "title": "AI system inventory",
        "objective": "Maintain visibility of AI systems and their intended purposes.",
        "guidance": "Record system purpose, owners, provider, data categories, users and deployment status.",
        "mappings": [
            ("NIST AI RMF", "MAP 1.1", "Context and intended purpose."),
            ("ISO/IEC 42001", "Clause 4", "Organisational context and scope.")
        ]
    },
    {
        "code": "RSK-001",
        "domain": "Risk management",
        "title": "AI risk assessment",
        "objective": "Identify and assess risks associated with the AI system.",
        "guidance": "Review impact, likelihood, affected stakeholders, risk severity and reassessment triggers.",
        "mappings": [
            ("NIST AI RMF", "MAP; MEASURE", "Map context and measure identified risks."),
            ("ISO/IEC 42001", "Clause 6", "Actions to address risks and opportunities.")
        ]
    },
    {
        "code": "DAT-001",
        "domain": "Data governance and privacy",
        "title": "Data quality and provenance",
        "objective": "Ensure data used by the AI system is appropriate and sufficiently documented.",
        "guidance": "Review data sources, quality, relevance, lineage, permissions and known limitations.",
        "mappings": [
            ("NIST AI RMF", "MAP; MEASURE", "Context and evaluation of data-related risks."),
            ("ISO/IEC 42001", "Annex A", "AI system data management controls; verify applicable control reference.")
        ]
    },
    {
        "code": "DAT-002",
        "domain": "Data governance and privacy",
        "title": "Privacy and data protection",
        "objective": "Protect personal and sensitive information processed by the AI system.",
        "guidance": "Review data minimisation, access, retention, disclosure, privacy assessment and applicable legal obligations.",
        "mappings": [
            ("NIST AI RMF", "GOVERN; MAP; MANAGE", "Privacy governance and risk treatment."),
            ("ISO/IEC 42001", "Annex A", "Data and information management; verify applicable control reference.")
        ]
    },
    {
        "code": "HUM-001",
        "domain": "Human oversight",
        "title": "Human review and escalation",
        "objective": "Ensure appropriate human oversight for consequential AI outputs and decisions.",
        "guidance": "Verify review points, escalation paths, override mechanisms and accountable decision-makers.",
        "mappings": [
            ("NIST AI RMF", "GOVERN; MANAGE", "Accountability and risk response."),
            ("ISO/IEC 42001", "Clause 5; Clause 8", "Roles and operational controls.")
        ]
    },
    {
        "code": "ASS-001",
        "domain": "AI evaluation and assurance",
        "title": "AI system validation and testing",
        "objective": "Evaluate whether the AI system meets defined quality and risk requirements.",
        "guidance": "Review test strategy, datasets, acceptance criteria, results, limitations and defect remediation.",
        "mappings": [
            ("NIST AI RMF", "MEASURE 2", "Evaluate AI system characteristics and risks."),
            ("ISO/IEC 42001", "Clause 8; Clause 9", "Operational planning and performance evaluation.")
        ]
    },
    {
        "code": "SEC-001",
        "domain": "Security",
        "title": "AI security and access control",
        "objective": "Protect the AI system, its data and connected services from unauthorised access and misuse.",
        "guidance": "Review authentication, authorisation, secrets, logging, prompt injection and data leakage testing where relevant.",
        "mappings": [
            ("NIST AI RMF", "MEASURE; MANAGE", "Evaluate and manage security-related risks."),
            ("ISO/IEC 42001", "Annex A", "Security-related AI management controls; verify applicable control reference.")
        ]
    },
    {
        "code": "MON-001",
        "domain": "Monitoring and incident management",
        "title": "AI monitoring and incident response",
        "objective": "Detect, record and respond to AI-related incidents and material system changes.",
        "guidance": "Review monitoring metrics, incident escalation, corrective actions, model changes and reassessment triggers.",
        "mappings": [
            ("NIST AI RMF", "MANAGE", "Prioritise, respond to and manage AI risks."),
            ("ISO/IEC 42001", "Clause 9; Clause 10", "Performance evaluation and continual improvement.")
        ]
    },
    {
        "code": "DOC-001",
        "domain": "Documentation and evidence",
        "title": "AI documentation and traceability",
        "objective": "Maintain records supporting governance, assurance and audit activities.",
        "guidance": "Check system documentation, assessment records, test evidence, decisions, approvals and change history.",
        "mappings": [
            ("NIST AI RMF", "GOVERN; MEASURE; MANAGE", "Documentation and accountability across risk activities."),
            ("ISO/IEC 42001", "Clause 7; Clause 9", "Documented information and performance evaluation.")
        ]
    }
]


def seed_starter_controls():
    """Insert starter controls and mappings without duplicating existing rows."""

    with _connect() as conn:
        for item in STARTER_CONTROLS:
            existing = conn.execute(
                "SELECT control_id FROM governance_controls WHERE control_code = ?",
                (item["code"],)
            ).fetchone()

            if existing:
                control_id = existing["control_id"]
            else:
                control_id = f"GC-{uuid4().hex[:8].upper()}"
                conn.execute("""
                    INSERT INTO governance_controls (
                        control_id, control_code, domain, title,
                        objective, guidance, active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """, (
                    control_id,
                    item["code"],
                    item["domain"],
                    item["title"],
                    item["objective"],
                    item["guidance"],
                    _now()
                ))

            for framework, reference, note in item["mappings"]:
                conn.execute("""
                    INSERT OR IGNORE INTO control_framework_mappings (
                        mapping_id, control_id, framework, reference, mapping_note
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"FM-{uuid4().hex[:8].upper()}",
                    control_id,
                    framework,
                    reference,
                    note
                ))

        conn.commit()


def list_governance_controls(active_only=True):
    query = "SELECT * FROM governance_controls"
    if active_only:
        query += " WHERE active = 1"
    query += " ORDER BY control_code"

    with _connect() as conn:
        return [dict(row) for row in conn.execute(query).fetchall()]


def list_framework_mappings(control_id=None):
    query = """
        SELECT m.*, c.control_code, c.title
        FROM control_framework_mappings m
        JOIN governance_controls c ON c.control_id = m.control_id
    """
    params = []

    if control_id:
        query += " WHERE m.control_id = ?"
        params.append(control_id)

    query += " ORDER BY c.control_code, m.framework"

    with _connect() as conn:
        return [
            dict(row)
            for row in conn.execute(query, params).fetchall()
        ]


def list_system_control_assessments(system_id=None):
    query = """
        SELECT
            a.*,
            c.control_code,
            c.domain,
            c.title,
            c.objective
        FROM system_control_assessments a
        JOIN governance_controls c ON c.control_id = a.control_id
    """
    params = []

    if system_id:
        query += " WHERE a.system_id = ?"
        params.append(system_id)

    query += " ORDER BY c.control_code"

    with _connect() as conn:
        return [
            dict(row)
            for row in conn.execute(query, params).fetchall()
        ]


def save_system_control_assessment(
    system_id,
    control_id,
    control_owner,
    implementation_status,
    effectiveness_status,
    reviewer,
    review_notes
):
    now = _now()

    with _connect() as conn:
        existing = conn.execute("""
            SELECT assessment_id
            FROM system_control_assessments
            WHERE system_id = ? AND control_id = ?
        """, (system_id, control_id)).fetchone()

        if existing:
            assessment_id = existing["assessment_id"]
            conn.execute("""
                UPDATE system_control_assessments
                SET control_owner = ?,
                    implementation_status = ?,
                    effectiveness_status = ?,
                    reviewer = ?,
                    review_notes = ?,
                    assessed_at = ?,
                    updated_at = ?
                WHERE assessment_id = ?
            """, (
                control_owner,
                implementation_status,
                effectiveness_status,
                reviewer,
                review_notes,
                now,
                now,
                assessment_id
            ))
        else:
            assessment_id = f"CA-{uuid4().hex[:8].upper()}"
            conn.execute("""
                INSERT INTO system_control_assessments (
                    assessment_id, system_id, control_id,
                    control_owner, implementation_status,
                    effectiveness_status, reviewer, review_notes,
                    assessed_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id,
                system_id,
                control_id,
                control_owner,
                implementation_status,
                effectiveness_status,
                reviewer,
                review_notes,
                now,
                now
            ))

        conn.commit()

    return assessment_id


def add_control_evidence(
    assessment_id,
    evidence_name,
    evidence_type,
    evidence_location,
    description
):
    evidence_id = f"EV-{uuid4().hex[:8].upper()}"

    with _connect() as conn:
        conn.execute("""
            INSERT INTO control_evidence (
                evidence_id, assessment_id, evidence_name,
                evidence_type, evidence_location, description,
                review_status, reviewer_notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Pending review', '', ?)
        """, (
            evidence_id,
            assessment_id,
            evidence_name,
            evidence_type,
            evidence_location,
            description,
            _now()
        ))
        conn.commit()

    return evidence_id


def list_control_evidence(assessment_id=None):
    query = "SELECT * FROM control_evidence"
    params = []

    if assessment_id:
        query += " WHERE assessment_id = ?"
        params.append(assessment_id)

    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        return [
            dict(row)
            for row in conn.execute(query, params).fetchall()
        ]


def update_evidence_review(evidence_id, review_status, reviewer_notes):
    with _connect() as conn:
        conn.execute("""
            UPDATE control_evidence
            SET review_status = ?, reviewer_notes = ?
            WHERE evidence_id = ?
        """, (review_status, reviewer_notes, evidence_id))
        conn.commit()


def add_remediation_action(
    assessment_id,
    action_description,
    action_owner,
    due_date,
    priority
):
    action_id = f"ACT-{uuid4().hex[:8].upper()}"
    now = _now()

    with _connect() as conn:
        conn.execute("""
            INSERT INTO control_remediation_actions (
                action_id, assessment_id, action_description,
                action_owner, due_date, priority, status,
                closure_notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Open', '', ?, ?)
        """, (
            action_id,
            assessment_id,
            action_description,
            action_owner,
            due_date,
            priority,
            now,
            now
        ))
        conn.commit()

    return action_id


def list_remediation_actions(assessment_id=None):
    query = "SELECT * FROM control_remediation_actions"
    params = []

    if assessment_id:
        query += " WHERE assessment_id = ?"
        params.append(assessment_id)

    query += " ORDER BY due_date"

    with _connect() as conn:
        return [
            dict(row)
            for row in conn.execute(query, params).fetchall()
        ]


def update_remediation_action(action_id, status, closure_notes):
    with _connect() as conn:
        conn.execute("""
            UPDATE control_remediation_actions
            SET status = ?, closure_notes = ?, updated_at = ?
            WHERE action_id = ?
        """, (status, closure_notes, _now(), action_id))
        conn.commit()
