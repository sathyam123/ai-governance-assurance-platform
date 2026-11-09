from datetime import date, datetime
from html import escape

import streamlit as st

from src.database import list_ai_systems, list_risk_assessments
from src.control_database import (
    list_system_control_assessments,
    list_control_evidence,
    list_remediation_actions,
)
from src.assurance_database import (
    list_evaluation_runs,
    list_evaluation_results,
    list_assurance_findings,
)


def _is_open(status):
    return str(status or "").strip().lower() not in {
        "closed", "resolved", "complete", "completed"
    }


def _is_overdue(item):
    due = str(item.get("due_date") or "").strip()
    if not due or not _is_open(item.get("status")):
        return False
    try:
        return date.fromisoformat(due[:10]) < date.today()
    except ValueError:
        return False


def _bar_section(title, counts):
    st.markdown(f"#### {escape(title)}")
    total = sum(counts.values())

    if total == 0:
        st.caption("No records available.")
        return

    for label, count in counts.items():
        percentage = (count / total) * 100
        st.markdown(
            f"""
            <div style="margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;
                          font-size:14px;margin-bottom:3px">
                <span>{escape(str(label))}</span>
                <strong>{count}</strong>
              </div>
              <div style="background:#e6e6e6;border-radius:5px;
                          height:10px;overflow:hidden">
                <div style="background:#3976a8;width:{percentage:.1f}%;
                            height:10px;border-radius:5px"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_executive_dashboard():
    st.title("Executive AI Governance Dashboard")
    st.caption(
        "Leadership overview of AI inventory, risk, controls, assurance "
        "and remediation. Metrics are read from the existing prototype database."
    )

    # Read existing records
    systems = list_ai_systems()
    risk_assessments = list_risk_assessments()
    control_assessments = list_system_control_assessments()
    evidence_records = list_control_evidence()
    control_actions = list_remediation_actions()
    evaluation_runs = list_evaluation_runs()
    findings = [
    dict(item) for item in list_assurance_findings()
]

       # Gather evaluation results from existing runs
    evaluation_results = []

    for run in evaluation_runs:
        run_id = run["run_id"]

        if run_id:
            results = list_evaluation_results(run_id)
            evaluation_results.extend(
                [dict(result) for result in results]
            )

    # Inventory and risk metrics
    high_critical_risks = sum(
        str(item.get("overall_risk", "")).strip().lower()
        in {"high", "critical"}
        for item in risk_assessments
    )

    pending_risk_reviews = sum(
        str(item.get("review_status", "")).strip().lower()
        in {"pending review", "pending"}
        for item in risk_assessments
    )

    # Control metrics
    assessed_controls = sum(
        str(item.get("implementation_status", "")).strip().lower()
        != "not assessed"
        for item in control_assessments
    )

    pending_evidence = sum(
        str(item.get("review_status", "")).strip().lower()
        in {"pending review", "pending"}
        for item in evidence_records
    )

    open_control_actions = [
        item for item in control_actions
        if _is_open(item.get("status"))
    ]
    overdue_control_actions = sum(
        _is_overdue(item) for item in control_actions
    )

    # Assurance and finding metrics
    open_findings = [
        item for item in findings
        if _is_open(item.get("finding_status"))
    ]

    outstanding_high_critical = sum(
        str(item.get("severity", "")).strip().lower()
        in {"high", "critical"}
        for item in open_findings
    )

    result_counts = {
        "Pass": 0,
        "Fail": 0,
        "Needs Review": 0,
        "Other / Unclassified": 0,
    }

    for result in evaluation_results:
        status = str(result.get("result_status", "")).strip().lower()
        if status == "pass":
            result_counts["Pass"] += 1
        elif status == "fail":
            result_counts["Fail"] += 1
        elif status in {"needs review", "needs_review"}:
            result_counts["Needs Review"] += 1
        else:
            result_counts["Other / Unclassified"] += 1

    # Executive KPI row
    st.markdown("### Governance position")

    columns = st.columns(4)
    columns[0].metric("Registered AI systems", len(systems))
    columns[1].metric("High / Critical risk assessments", high_critical_risks)
    columns[2].metric("Open findings", len(open_findings))
    columns[3].metric("Controls assessed", assessed_controls)

    columns = st.columns(4)
    columns[0].metric("Pending risk reviews", pending_risk_reviews)
    columns[1].metric("Evidence awaiting review", pending_evidence)
    columns[2].metric("Open control actions", len(open_control_actions))
    columns[3].metric("Overdue control actions", overdue_control_actions)

    st.divider()
    st.markdown("### Risk and assurance overview")

    left, right = st.columns(2)

    with left:
        risk_counts = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
        for item in risk_assessments:
            label = str(item.get("overall_risk", "")).strip().title()
            if label in risk_counts:
                risk_counts[label] += 1
        _bar_section("Risk assessment distribution", risk_counts)

    with right:
        _bar_section("Assurance evaluation outcomes", result_counts)

    st.divider()
    st.markdown("### Governance control coverage")

    implementation_counts = {}
    effectiveness_counts = {}

    for item in control_assessments:
        implementation = str(
            item.get("implementation_status") or "Not recorded"
        )
        effectiveness = str(
            item.get("effectiveness_status") or "Not recorded"
        )
        implementation_counts[implementation] = (
            implementation_counts.get(implementation, 0) + 1
        )
        effectiveness_counts[effectiveness] = (
            effectiveness_counts.get(effectiveness, 0) + 1
        )

    left, right = st.columns(2)

    with left:
        _bar_section("Implementation status", implementation_counts)

    with right:
        _bar_section("Effectiveness status", effectiveness_counts)

    st.divider()
    st.markdown("### Findings and remediation")

    finding_severity = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }
    finding_status = {}

    for item in findings:
        severity = str(item.get("severity") or "").title()
        if severity in finding_severity:
            finding_severity[severity] += 1

        status = str(item.get("finding_status") or "Not recorded")
        finding_status[status] = finding_status.get(status, 0) + 1

    left, right = st.columns(2)

    with left:
        _bar_section("Findings by severity", finding_severity)

    with right:
        _bar_section("Findings by remediation status", finding_status)

    st.divider()
    st.markdown("### Systems requiring attention")

    attention_items = []

    for item in risk_assessments:
        if str(item.get("review_status", "")).strip().lower() in {
            "pending review", "pending"
        }:
            attention_items.append(
                f"Risk assessment awaiting review — System ID: "
                f"{item.get('system_id', 'Not available')}"
            )

    for item in open_findings:
        if str(item.get("severity", "")).strip().lower() in {
            "high", "critical"
        }:
            attention_items.append(
                f"{item.get('severity')} finding — "
                f"{item.get('finding_category', 'Uncategorised')}"
            )

    for item in control_actions:
        if _is_overdue(item):
            attention_items.append(
                f"Overdue control action — "
                f"{item.get('action_description', 'Description unavailable')} "
                f"(Owner: {item.get('action_owner', 'Unassigned')})"
            )

    if attention_items:
        for item in attention_items:
            st.warning(item)
    else:
        st.success("No items currently match these attention rules.")

    st.divider()
    st.markdown("### Dashboard interpretation")
    st.caption(
        "These indicators reflect records currently stored in this prototype. "
        "They are operational summaries, not evidence of regulatory compliance, "
        "certification, or independent assurance. A control marked assessed "
        "does not automatically mean it is effective."
    )
