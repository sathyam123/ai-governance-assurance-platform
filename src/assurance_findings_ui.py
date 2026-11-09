import streamlit as st
from datetime import date

from src.database import list_ai_systems

from src.assurance_database import (
    list_evaluation_runs,
    list_evaluation_results,
    create_assurance_finding,
    list_assurance_findings,
    update_assurance_finding,
)


FINDING_CATEGORIES = [
    "Accuracy",
    "Retrieval relevance",
    "Groundedness",
    "Completeness",
    "Hallucination",
    "Unsupported-question handling",
    "Bias and fairness",
    "Safety and privacy",
    "Security",
    "Governance and documentation",
    "Other",
]

SEVERITIES = ["Low", "Medium", "High", "Critical"]

FINDING_STATUSES = [
    "Open",
    "In Progress",
    "Resolved",
    "Closed",
]


def _system_label(system):
    return f'{system["system_name"]} ({system["system_id"]})'


def _run_label(run):
    return (
        f'{run["run_name"]} | {run["run_status"]} | '
        f'{run["created_at"][:10]}'
    )


def _result_label(result):
    return (
        f'{result["test_name"]} | '
        f'{result["result_status"]}'
    )


def render_assurance_findings():

    st.title("AI Assurance – Findings & Remediation")

    st.caption(
        "Identify assurance gaps, investigate root causes, "
        "assign remediation actions and track closure."
    )

    systems = [
        dict(system)
        for system in list_ai_systems()
    ]

    if not systems:
        st.warning("Register an AI system first.")
        return

    selected_system = st.selectbox(
        "Select AI system",
        systems,
        format_func=_system_label,
        key="findings_system",
    )

    system_id = selected_system["system_id"]

    runs = [
        dict(run)
        for run in list_evaluation_runs(system_id)
    ]

    findings = [
        dict(finding)
        for finding in list_assurance_findings()
    ]

    system_findings = []

    system_run_ids = {
        run["run_id"] for run in runs
    }

    for finding in findings:
        if finding["run_id"] in system_run_ids:
            system_findings.append(finding)

    st.divider()

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    st.subheader("Findings summary")

    open_count = sum(
        1 for f in system_findings
        if f["finding_status"] == "Open"
    )

    progress_count = sum(
        1 for f in system_findings
        if f["finding_status"] == "In Progress"
    )

    resolved_count = sum(
        1 for f in system_findings
        if f["finding_status"] in ["Resolved", "Closed"]
    )

    critical_high_count = sum(
        1 for f in system_findings
        if f["severity"] in ["Critical", "High"]
        and f["finding_status"] not in ["Resolved", "Closed"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total findings", len(system_findings))
    col2.metric("Open", open_count)
    col3.metric("In progress", progress_count)
    col4.metric("Resolved / Closed", resolved_count)

    st.metric(
        "Outstanding High / Critical findings",
        critical_high_count,
    )

    st.divider()

    create_tab, tracking_tab = st.tabs(
        [
            "Create finding",
            "Finding & remediation register",
        ]
    )

    # --------------------------------------------------
    # TAB 1: CREATE FINDING
    # --------------------------------------------------

    with create_tab:

        st.subheader("Register an assurance finding")

        if not runs:

            st.info(
                "Create an evaluation run before registering "
                "an evaluation-linked finding."
            )

        else:

            selected_run = st.selectbox(
                "Linked evaluation run",
                runs,
                format_func=_run_label,
                key="finding_run",
            )

            results = [
                dict(result)
                for result in list_evaluation_results(
                    selected_run["run_id"]
                )
            ]

            result_options = [None] + results

            selected_result = st.selectbox(
                "Linked evaluation result",
                result_options,
                format_func=lambda result: (
                    "General finding – not linked to one result"
                    if result is None
                    else _result_label(result)
                ),
                key="finding_result",
            )

            if selected_result is not None:
                st.caption(
                    "This finding will be linked to the selected "
                    "evaluation result."
                )

            with st.form("create_assurance_finding_form"):

                finding_category = st.selectbox(
                    "Finding category",
                    FINDING_CATEGORIES,
                )

                severity = st.selectbox(
                    "Severity",
                    SEVERITIES,
                    index=1,
                )

                finding_description = st.text_area(
                    "Finding description",
                    height=120,
                    placeholder=(
                        "Describe the observed issue and its "
                        "potential impact."
                    ),
                )

                root_cause = st.text_area(
                    "Root cause analysis",
                    height=100,
                    placeholder=(
                        "Explain the likely cause. If not yet "
                        "confirmed, state that investigation is pending."
                    ),
                )

                recommendation = st.text_area(
                    "Recommended remediation action",
                    height=120,
                    placeholder=(
                        "Describe the corrective or preventive action."
                    ),
                )

                col1, col2 = st.columns(2)

                with col1:
                    action_owner = st.text_input(
                        "Remediation owner",
                        placeholder="Example: RAG Engineering Lead",
                    )

                with col2:
                    due_date = st.date_input(
                        "Target completion date",
                        value=date.today(),
                    )

                submitted = st.form_submit_button(
                    "Create assurance finding",
                    type="primary",
                )

                if submitted:

                    if not finding_description.strip():
                        st.error(
                            "Enter a finding description."
                        )

                    elif not recommendation.strip():
                        st.error(
                            "Enter a remediation recommendation."
                        )

                    elif not action_owner.strip():
                        st.error(
                            "Enter a remediation owner."
                        )

                    elif due_date < date.today():
                        st.error(
                            "Choose a target date that is today "
                            "or in the future."
                        )

                    else:

                        finding_id = create_assurance_finding(
                            run_id=selected_run["run_id"],
                            finding_category=finding_category,
                            severity=severity,
                            finding_description=(
                                finding_description.strip()
                            ),
                            result_id=(
                                selected_result["result_id"]
                                if selected_result is not None
                                else None
                            ),
                            root_cause=root_cause.strip(),
                            recommendation=recommendation.strip(),
                            action_owner=action_owner.strip(),
                            due_date=due_date.isoformat(),
                        )

                        st.success(
                            "Assurance finding created successfully. "
                            f"Finding ID: {finding_id}"
                        )

                        st.rerun()

    # --------------------------------------------------
    # TAB 2: FINDING REGISTER
    # --------------------------------------------------

    with tracking_tab:

        st.subheader("Finding & remediation register")

        if not system_findings:

            st.info(
                "No assurance findings have been recorded "
                "for this AI system yet."
            )

        else:

            status_filter = st.selectbox(
                "Filter by status",
                [
                    "All statuses",
                    "Open",
                    "In Progress",
                    "Resolved",
                    "Closed",
                ],
            )

            severity_filter = st.selectbox(
                "Filter by severity",
                [
                    "All severities",
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                ],
            )

            filtered_findings = system_findings

            if status_filter != "All statuses":
                filtered_findings = [
                    f for f in filtered_findings
                    if f["finding_status"] == status_filter
                ]

            if severity_filter != "All severities":
                filtered_findings = [
                    f for f in filtered_findings
                    if f["severity"] == severity_filter
                ]

            if not filtered_findings:
                st.info("No findings match the selected filters.")

            for finding in filtered_findings:

                with st.expander(
                    f'{finding["finding_category"]} | '
                    f'{finding["severity"]} | '
                    f'{finding["finding_status"]}'
                ):

                    st.write("**Finding description**")
                    st.write(finding["finding_description"])

                    st.write("**Root cause analysis**")
                    st.write(
                        finding["root_cause"]
                        or "Not yet documented"
                    )

                    st.write("**Recommended remediation**")
                    st.write(
                        finding["recommendation"]
                        or "Not documented"
                    )

                    st.write(
                        f'**Owner:** '
                        f'{finding["action_owner"] or "Unassigned"}'
                    )

                    st.write(
                        f'**Target date:** '
                        f'{finding["due_date"] or "Not specified"}'
                    )

                    st.caption(
                        f'Finding ID: {finding["finding_id"]}'
                    )

                    st.divider()

                    st.markdown("### Update remediation status")

                    with st.form(
                        f'update_finding_{finding["finding_id"]}'
                    ):

                        new_status = st.selectbox(
                            "Finding status",
                            FINDING_STATUSES,
                            index=FINDING_STATUSES.index(
                                finding["finding_status"]
                            )
                            if finding["finding_status"]
                            in FINDING_STATUSES
                            else 0,
                        )

                        closure_notes = st.text_area(
                            "Reviewer / closure notes",
                            value=finding["closure_notes"] or "",
                            placeholder=(
                                "Record remediation evidence, "
                                "verification performed and review "
                                "decision. Required for closure."
                            ),
                        )

                        update_button = st.form_submit_button(
                            "Update finding",
                            type="primary",
                        )

                        if update_button:

                            if (
                                new_status in ["Resolved", "Closed"]
                                and not closure_notes.strip()
                            ):
                                st.error(
                                    "Provide verification or closure "
                                    "notes before resolving or closing "
                                    "a finding."
                                )

                            else:

                                update_assurance_finding(
                                    finding_id=finding["finding_id"],
                                    finding_status=new_status,
                                    closure_notes=closure_notes.strip(),
                                )

                                st.success(
                                    "Finding status updated successfully."
                                )

                                st.rerun()