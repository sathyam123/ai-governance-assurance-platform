
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from src.config import DB_PATH


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _now():
    return datetime.now(timezone.utc).isoformat()


def init_assurance_tables():
    """Create assurance tables without modifying existing tables."""

    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS assurance_test_cases (
            test_case_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            category TEXT NOT NULL,
            test_name TEXT NOT NULL,
            user_query TEXT NOT NULL,
            expected_behavior TEXT NOT NULL,
            expected_source TEXT DEFAULT '',
            severity TEXT NOT NULL DEFAULT 'Medium',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (system_id)
                REFERENCES ai_systems(system_id)
        );

        CREATE TABLE IF NOT EXISTS assurance_evaluation_runs (
            run_id TEXT PRIMARY KEY,
            system_id TEXT NOT NULL,
            run_name TEXT NOT NULL,
            evaluator TEXT NOT NULL,
            environment TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            run_status TEXT NOT NULL DEFAULT 'In progress',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (system_id)
                REFERENCES ai_systems(system_id)
        );

        CREATE TABLE IF NOT EXISTS assurance_evaluation_results (
            result_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            test_case_id TEXT NOT NULL,
            actual_response TEXT DEFAULT '',
            retrieved_sources TEXT DEFAULT '',
            result_status TEXT NOT NULL DEFAULT 'Not evaluated',
            accuracy_score INTEGER,
            retrieval_score INTEGER,
            groundedness_score INTEGER,
            completeness_score INTEGER,
            evaluator_notes TEXT DEFAULT '',
            evaluated_by TEXT DEFAULT '',
            evaluated_at TEXT NOT NULL,
            FOREIGN KEY (run_id)
                REFERENCES assurance_evaluation_runs(run_id),
            FOREIGN KEY (test_case_id)
                REFERENCES assurance_test_cases(test_case_id),
            UNIQUE(run_id, test_case_id)
        );

        CREATE TABLE IF NOT EXISTS assurance_findings (
            finding_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            result_id TEXT,
            finding_category TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'Medium',
            finding_description TEXT NOT NULL,
            root_cause TEXT DEFAULT '',
            recommendation TEXT DEFAULT '',
            action_owner TEXT DEFAULT '',
            due_date TEXT DEFAULT '',
            finding_status TEXT NOT NULL DEFAULT 'Open',
            closure_notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (run_id)
                REFERENCES assurance_evaluation_runs(run_id),
            FOREIGN KEY (result_id)
                REFERENCES assurance_evaluation_results(result_id)
        );

        CREATE INDEX IF NOT EXISTS idx_assurance_cases_system
            ON assurance_test_cases(system_id);

        CREATE INDEX IF NOT EXISTS idx_assurance_runs_system
            ON assurance_evaluation_runs(system_id);

        CREATE INDEX IF NOT EXISTS idx_assurance_results_run
            ON assurance_evaluation_results(run_id);

        CREATE INDEX IF NOT EXISTS idx_assurance_findings_run
            ON assurance_findings(run_id);
        """)


def create_test_case(
    system_id,
    category,
    test_name,
    user_query,
    expected_behavior,
    expected_source="",
    severity="Medium",
):
    test_case_id = str(uuid4())

    with _connect() as conn:
        conn.execute("""
            INSERT INTO assurance_test_cases (
                test_case_id, system_id, category, test_name,
                user_query, expected_behavior, expected_source,
                severity, active, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            test_case_id,
            system_id,
            category,
            test_name,
            user_query,
            expected_behavior,
            expected_source,
            severity,
            _now(),
        ))

    return test_case_id


def list_test_cases(system_id=None, active_only=True):
    query = "SELECT * FROM assurance_test_cases WHERE 1=1"
    params = []

    if system_id:
        query += " AND system_id = ?"
        params.append(system_id)

    if active_only:
        query += " AND active = 1"

    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        return conn.execute(query, params).fetchall()


def update_test_case_status(test_case_id, active):
    with _connect() as conn:
        conn.execute("""
            UPDATE assurance_test_cases
            SET active = ?
            WHERE test_case_id = ?
        """, (1 if active else 0, test_case_id))


def create_evaluation_run(
    system_id,
    run_name,
    evaluator,
    environment="",
    notes="",
):
    run_id = str(uuid4())

    with _connect() as conn:
        conn.execute("""
            INSERT INTO assurance_evaluation_runs (
                run_id, system_id, run_name, evaluator,
                environment, notes, run_status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'In progress', ?)
        """, (
            run_id,
            system_id,
            run_name,
            evaluator,
            environment,
            notes,
            _now(),
        ))

    return run_id


def list_evaluation_runs(system_id=None):
    query = "SELECT * FROM assurance_evaluation_runs WHERE 1=1"
    params = []

    if system_id:
        query += " AND system_id = ?"
        params.append(system_id)

    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        return conn.execute(query, params).fetchall()


def get_evaluation_run(run_id):
    with _connect() as conn:
        return conn.execute("""
            SELECT * FROM assurance_evaluation_runs
            WHERE run_id = ?
        """, (run_id,)).fetchone()


def complete_evaluation_run(run_id):
    with _connect() as conn:
        conn.execute("""
            UPDATE assurance_evaluation_runs
            SET run_status = 'Completed',
                completed_at = ?
            WHERE run_id = ?
        """, (_now(), run_id))


def save_evaluation_result(
    run_id,
    test_case_id,
    actual_response,
    retrieved_sources="",
    result_status="Not evaluated",
    accuracy_score=None,
    retrieval_score=None,
    groundedness_score=None,
    completeness_score=None,
    evaluator_notes="",
    evaluated_by="",
):
    result_id = str(uuid4())

    with _connect() as conn:
        existing = conn.execute("""
            SELECT result_id
            FROM assurance_evaluation_results
            WHERE run_id = ? AND test_case_id = ?
        """, (run_id, test_case_id)).fetchone()

        if existing:
            result_id = existing["result_id"]

            conn.execute("""
                UPDATE assurance_evaluation_results
                SET actual_response = ?,
                    retrieved_sources = ?,
                    result_status = ?,
                    accuracy_score = ?,
                    retrieval_score = ?,
                    groundedness_score = ?,
                    completeness_score = ?,
                    evaluator_notes = ?,
                    evaluated_by = ?,
                    evaluated_at = ?
                WHERE result_id = ?
            """, (
                actual_response,
                retrieved_sources,
                result_status,
                accuracy_score,
                retrieval_score,
                groundedness_score,
                completeness_score,
                evaluator_notes,
                evaluated_by,
                _now(),
                result_id,
            ))
        else:
            conn.execute("""
                INSERT INTO assurance_evaluation_results (
                    result_id, run_id, test_case_id,
                    actual_response, retrieved_sources,
                    result_status, accuracy_score, retrieval_score,
                    groundedness_score, completeness_score,
                    evaluator_notes, evaluated_by, evaluated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id,
                run_id,
                test_case_id,
                actual_response,
                retrieved_sources,
                result_status,
                accuracy_score,
                retrieval_score,
                groundedness_score,
                completeness_score,
                evaluator_notes,
                evaluated_by,
                _now(),
            ))

    return result_id


def list_evaluation_results(run_id):
    with _connect() as conn:
        return conn.execute("""
            SELECT
                r.*,
                t.test_name,
                t.category,
                t.user_query,
                t.expected_behavior,
                t.expected_source,
                t.severity
            FROM assurance_evaluation_results r
            JOIN assurance_test_cases t
                ON r.test_case_id = t.test_case_id
            WHERE r.run_id = ?
            ORDER BY t.category, t.test_name
        """, (run_id,)).fetchall()


def create_assurance_finding(
    run_id,
    finding_category,
    severity,
    finding_description,
    result_id=None,
    root_cause="",
    recommendation="",
    action_owner="",
    due_date="",
):
    finding_id = str(uuid4())

    with _connect() as conn:
        conn.execute("""
            INSERT INTO assurance_findings (
                finding_id, run_id, result_id,
                finding_category, severity,
                finding_description, root_cause,
                recommendation, action_owner,
                due_date, finding_status,
                closure_notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', '', ?, ?)
        """, (
            finding_id,
            run_id,
            result_id,
            finding_category,
            severity,
            finding_description,
            root_cause,
            recommendation,
            action_owner,
            due_date,
            _now(),
            _now(),
        ))

    return finding_id


def list_assurance_findings(run_id=None):
    query = "SELECT * FROM assurance_findings WHERE 1=1"
    params = []

    if run_id:
        query += " AND run_id = ?"
        params.append(run_id)

    query += " ORDER BY created_at DESC"

    with _connect() as conn:
        return conn.execute(query, params).fetchall()


def update_assurance_finding(
    finding_id,
    finding_status,
    closure_notes="",
):
    with _connect() as conn:
        conn.execute("""
            UPDATE assurance_findings
            SET finding_status = ?,
                closure_notes = ?,
                updated_at = ?
            WHERE finding_id = ?
        """, (
            finding_status,
            closure_notes,
            _now(),
            finding_id,
        ))
