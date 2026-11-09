# Architecture and Module Guide

## Application entry point

`app.py` configures the Streamlit application, initialises the SQLite-backed modules, presents the navigation menu, and routes the selected page to the relevant UI function.

## Module map

| Capability | Primary modules |
|---|---|
| AI inventory and risk assessment | `src/database.py`, `src/ui.py` |
| Application configuration | `src/config.py` |
| RAG demonstration | `src/rag_engine.py` |
| Governance control library, mappings, assessments, evidence, and actions | `src/control_database.py`, `src/control_ui.py` |
| Assurance test cases and evaluation data | `src/assurance_database.py`, `src/assurance_ui.py` |
| Evaluation execution | `src/assurance_execution_ui.py` |
| Assurance findings and remediation | `src/assurance_findings_ui.py` |
| Security assurance scenarios | `src/security_assurance_ui.py` |
| Executive dashboard | `src/executive_dashboard.py` |

The project uses SQLite persistence and modular Streamlit UI functions. The dashboard consolidates metrics by reading records from the existing application tables.

## Governance lifecycle represented

1. Register an AI system and capture its context and owners.
2. Record a structured risk assessment.
3. Capture human review and reviewer notes.
4. Assess governance controls and their effectiveness.
5. Record evidence references and evidence-review status.
6. Define and track control remediation actions.
7. Define assurance test cases and evaluation runs.
8. Record test outcomes, observations, and linked findings.
9. Track finding severity, root cause, recommendations, ownership, and status.
10. Review consolidated governance indicators in the executive dashboard.

## Data and decision boundaries

- The SQLite database is local application storage.
- Risk scoring and severity categorisation are prototype conventions.
- Framework mappings are indicative references; they require verification against the applicable official publications and organisational context.
- The dashboard is a reporting view of persisted records, not an independent audit or compliance determination.
- Human reviewers retain responsibility for interpreting results and approving risk treatment.
