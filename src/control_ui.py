
import streamlit as st

from src.database import list_ai_systems
from src.control_database import (
    list_governance_controls,
    list_framework_mappings,
    list_system_control_assessments,
    save_system_control_assessment,
    add_control_evidence,
    list_control_evidence,
    update_evidence_review,
    add_remediation_action,
    list_remediation_actions,
    update_remediation_action,
)


IMPLEMENTATION_STATUSES = [
    "Not assessed",
    "Not implemented",
    "Partially implemented",
    "Implemented",
    "Not applicable",
]

EFFECTIVENESS_STATUSES = [
    "Not evaluated",
    "Effective",
    "Partially effective",
    "Ineffective",
    "Not verified",
]

EVIDENCE_REVIEW_STATUSES = [
    "Pending review",
    "Accepted",
    "Rejected",
    "Needs clarification",
]

REMEDIATION_STATUSES = [
    "Open",
    "In progress",
    "Blocked",
    "Closed",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]


def value(row, field, default=""):
    """Safely read a field from a SQLite Row or dictionary."""
    try:
        result = row[field]
        return default if result is None else result
    except (KeyError, IndexError, TypeError):
        return default


def render_control_management():
    st.title("Governance Control Management")
    st.caption(
        "Manage governance controls, framework mappings, system assessments, "
        "evidence reviews and remediation actions."
    )

    systems = list_ai_systems()
    controls = list_governance_controls()
    mappings = list_framework_mappings()
    assessments = list_system_control_assessments()

    if not systems:
        st.warning(
            "No AI systems are registered yet. Register an AI system first "
            "before assessing governance controls."
        )
        return

    if not controls:
        st.warning(
            "The governance control library is empty. Check the database "
            "initialisation and starter-control seeding."
        )
        return

    system_lookup = {
        value(system, "system_id"): value(system, "system_name", "Unnamed system")
        for system in systems
    }

    control_lookup = {
        value(control, "control_id"): control
        for control in controls
    }

    st.subheader("Select AI system")

    selected_system_id = st.selectbox(
        "AI system",
        options=list(system_lookup.keys()),
        format_func=lambda system_id: (
            f"{system_lookup[system_id]} ({system_id})"
        ),
        key="governance_selected_system",
    )

    system_assessments = [
        assessment
        for assessment in assessments
        if value(assessment, "system_id") == selected_system_id
    ]

    assessment_lookup = {
        value(assessment, "control_id"): assessment
        for assessment in system_assessments
    }

    implemented_count = sum(
        1
        for assessment in system_assessments
        if value(assessment, "implementation_status") == "Implemented"
    )

    partial_count = sum(
        1
        for assessment in system_assessments
        if value(assessment, "implementation_status") == "Partially implemented"
    )

    not_implemented_count = sum(
        1
        for assessment in system_assessments
        if value(assessment, "implementation_status") == "Not implemented"
    )

    pending_evidence_count = 0
    open_remediation_count = 0

    for assessment in system_assessments:
        assessment_id = value(assessment, "assessment_id")

        evidence_items = list_control_evidence(assessment_id)
        pending_evidence_count += sum(
            1
            for item in evidence_items
            if value(item, "review_status") == "Pending review"
        )

        remediation_items = list_remediation_actions(assessment_id)
        open_remediation_count += sum(
            1
            for item in remediation_items
            if value(item, "status") != "Closed"
        )

    st.divider()
    st.subheader("Control assessment summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control library", len(controls))
    col2.metric("Assessed controls", len(system_assessments))
    col3.metric("Implemented", implemented_count)
    col4.metric("Partially implemented", partial_count)

    col5, col6, col7 = st.columns(3)
    col5.metric("Not implemented", not_implemented_count)
    col6.metric("Evidence pending review", pending_evidence_count)
    col7.metric("Open remediation actions", open_remediation_count)

    st.divider()

    tab_library, tab_assess, tab_evidence, tab_remediation = st.tabs(
        [
            "Control Library",
            "System Assessment",
            "Evidence Management",
            "Remediation",
        ]
    )

    # ---------------------------------------------------------
    # TAB 1: CONTROL LIBRARY
    # ---------------------------------------------------------
    with tab_library:
        st.subheader("Governance control library")
        st.write(
            "The starter library contains prototype governance controls "
            "with indicative mappings to NIST AI RMF and ISO/IEC 42001."
        )

        domains = sorted(
            {
                value(control, "domain", "Unclassified")
                for control in controls
            }
        )

        selected_domain = st.selectbox(
            "Filter by control domain",
            options=["All domains"] + domains,
            key="control_domain_filter",
        )

        framework_filter = st.selectbox(
            "Filter by framework",
            options=[
                "All frameworks",
                "NIST AI RMF",
                "ISO/IEC 42001",
            ],
            key="control_framework_filter",
        )

        for control in controls:
            control_id = value(control, "control_id")
            control_domain = value(control, "domain", "Unclassified")

            if (
                selected_domain != "All domains"
                and control_domain != selected_domain
            ):
                continue

            control_mappings = [
                mapping
                for mapping in mappings
                if value(mapping, "control_id") == control_id
            ]

            if framework_filter != "All frameworks":
                control_mappings = [
                    mapping
                    for mapping in control_mappings
                    if value(mapping, "framework") == framework_filter
                ]

                if not control_mappings:
                    continue

            title = value(control, "title", "Untitled control")
            code = value(control, "control_code", control_id)

            with st.expander(f"{code} — {title}"):
                st.markdown(f"**Domain:** {control_domain}")
                st.markdown(
                    f"**Objective:** {value(control, 'objective', 'Not specified')}"
                )
                st.markdown(
                    f"**Guidance:** {value(control, 'guidance', 'Not specified')}"
                )

                st.markdown("**Framework mappings**")

                if control_mappings:
                    for mapping in control_mappings:
                        st.write(
                            f"- {value(mapping, 'framework')}: "
                            f"{value(mapping, 'reference')}"
                        )
                        note = value(mapping, "mapping_note")
                        if note:
                            st.caption(note)
                else:
                    st.info("No mappings are available for this filter.")

        st.info(
            "Framework mappings are indicative starter mappings. They are "
            "not a complete control catalogue, formal compliance assessment "
            "or certification of conformity."
        )

    # ---------------------------------------------------------
    # TAB 2: SYSTEM CONTROL ASSESSMENT
    # ---------------------------------------------------------
    with tab_assess:
        st.subheader("Assess governance controls for this AI system")

        control_ids = list(control_lookup.keys())

        selected_control_id = st.selectbox(
            "Select a governance control",
            options=control_ids,
            format_func=lambda control_id: (
                f"{value(control_lookup[control_id], 'control_code')} — "
                f"{value(control_lookup[control_id], 'title')}"
            ),
            key="assessment_control_selector",
        )

        selected_control = control_lookup[selected_control_id]
        existing_assessment = assessment_lookup.get(selected_control_id)

        st.markdown(
            f"**Control objective:** "
            f"{value(selected_control, 'objective', 'Not specified')}"
        )
        st.caption(
            value(selected_control, "guidance", "No additional guidance available.")
        )

        with st.form("system_control_assessment_form"):
            control_owner = st.text_input(
                "Control owner",
                value=(
                    value(existing_assessment, "control_owner")
                    if existing_assessment
                    else ""
                ),
                placeholder="Enter the accountable control owner",
            )

            implementation_status = st.selectbox(
                "Implementation status",
                options=IMPLEMENTATION_STATUSES,
                index=(
                    IMPLEMENTATION_STATUSES.index(
                        value(existing_assessment, "implementation_status")
                    )
                    if existing_assessment
                    and value(existing_assessment, "implementation_status")
                    in IMPLEMENTATION_STATUSES
                    else 0
                ),
            )

            effectiveness_status = st.selectbox(
                "Effectiveness status",
                options=EFFECTIVENESS_STATUSES,
                index=(
                    EFFECTIVENESS_STATUSES.index(
                        value(existing_assessment, "effectiveness_status")
                    )
                    if existing_assessment
                    and value(existing_assessment, "effectiveness_status")
                    in EFFECTIVENESS_STATUSES
                    else 0
                ),
            )

            reviewer = st.text_input(
                "Reviewer",
                value=(
                    value(existing_assessment, "reviewer")
                    if existing_assessment
                    else ""
                ),
                placeholder="Enter reviewer name or role",
            )

            review_notes = st.text_area(
                "Assessment notes",
                value=(
                    value(existing_assessment, "review_notes")
                    if existing_assessment
                    else ""
                ),
                placeholder="Describe implementation, gaps, test results and observations.",
            )

            assessment_submitted = st.form_submit_button(
                "Save control assessment",
                type="primary",
            )

        if assessment_submitted:
            if not control_owner.strip():
                st.error("Please enter a control owner.")
            else:
                save_system_control_assessment(
                    system_id=selected_system_id,
                    control_id=selected_control_id,
                    control_owner=control_owner.strip(),
                    implementation_status=implementation_status,
                    effectiveness_status=effectiveness_status,
                    reviewer=reviewer.strip(),
                    review_notes=review_notes.strip(),
                )
                st.success("Control assessment saved.")
                st.rerun()

        if existing_assessment:
            st.caption(
                "This control already has an assessment for the selected "
                "AI system. Saving updates that system-control assessment."
            )
        else:
            st.info(
                "This control has not yet been assessed for the selected system."
            )

        st.markdown("#### Assessment status across this system")

        for control in controls:
            control_id = value(control, "control_id")
            assessment = assessment_lookup.get(control_id)

            status = (
                value(assessment, "implementation_status")
                if assessment
                else "Not assessed"
            )

            st.write(
                f"**{value(control, 'control_code')}** — "
                f"{value(control, 'title')}  \n"
                f"Implementation: `{status}`"
            )

    # ---------------------------------------------------------
    # TAB 3: EVIDENCE MANAGEMENT
    # ---------------------------------------------------------
    with tab_evidence:
        st.subheader("Control evidence management")

        if not system_assessments:
            st.info(
                "Assess at least one control before adding evidence."
            )
        else:
            assessment_options = {
                value(assessment, "assessment_id"): (
                    f"{value(control_lookup.get(value(assessment, 'control_id'), {}), 'control_code')} — "
                    f"{value(control_lookup.get(value(assessment, 'control_id'), {}), 'title')}"
                )
                for assessment in system_assessments
            }

            selected_assessment_id = st.selectbox(
                "Select assessed control",
                options=list(assessment_options.keys()),
                format_func=lambda assessment_id: assessment_options[
                    assessment_id
                ],
                key="evidence_assessment_selector",
            )

            with st.form("add_control_evidence_form"):
                evidence_name = st.text_input(
                    "Evidence name",
                    placeholder="e.g. AI risk assessment report",
                )

                evidence_type = st.selectbox(
                    "Evidence type",
                    [
                        "Policy",
                        "Procedure",
                        "Risk assessment",
                        "Test report",
                        "Approval record",
                        "Monitoring report",
                        "Meeting record",
                        "Other",
                    ],
                )

                evidence_location = st.text_input(
                    "Evidence location or reference",
                    placeholder="File name, repository path or URL",
                )

                evidence_description = st.text_area(
                    "Evidence description",
                    placeholder="Explain what this evidence demonstrates.",
                )

                evidence_submitted = st.form_submit_button(
                    "Add evidence",
                    type="primary",
                )

            if evidence_submitted:
                if not evidence_name.strip():
                    st.error("Please enter an evidence name.")
                else:
                    add_control_evidence(
                        assessment_id=selected_assessment_id,
                        evidence_name=evidence_name.strip(),
                        evidence_type=evidence_type,
                        evidence_location=evidence_location.strip(),
                        description=evidence_description.strip(),
                    )
                    st.success("Evidence reference added.")
                    st.rerun()

            st.markdown("#### Evidence records")

            evidence_items = list_control_evidence(
                selected_assessment_id
            )

            if not evidence_items:
                st.info("No evidence records have been added for this control.")
            else:
                for evidence in evidence_items:
                    evidence_id = value(evidence, "evidence_id")

                    with st.expander(
                        value(evidence, "evidence_name", "Evidence record")
                    ):
                        st.write(
                            f"**Type:** {value(evidence, 'evidence_type')}"
                        )
                        st.write(
                            f"**Location/reference:** "
                            f"{value(evidence, 'evidence_location')}"
                        )
                        st.write(
                            f"**Description:** "
                            f"{value(evidence, 'description')}"
                        )
                        st.write(
                            f"**Review status:** "
                            f"{value(evidence, 'review_status')}"
                        )

                        with st.form(f"review_evidence_{evidence_id}"):
                            current_status = value(
                                evidence,
                                "review_status",
                                "Pending review",
                            )

                            review_index = (
                                EVIDENCE_REVIEW_STATUSES.index(current_status)
                                if current_status in EVIDENCE_REVIEW_STATUSES
                                else 0
                            )

                            new_review_status = st.selectbox(
                                "Evidence review decision",
                                EVIDENCE_REVIEW_STATUSES,
                                index=review_index,
                            )

                            evidence_reviewer_notes = st.text_area(
                                "Reviewer notes",
                                value=value(evidence, "reviewer_notes"),
                            )

                            evidence_review_submitted = st.form_submit_button(
                                "Update evidence review"
                            )

                        if evidence_review_submitted:
                            update_evidence_review(
                                evidence_id=evidence_id,
                                review_status=new_review_status,
                                reviewer_notes=evidence_reviewer_notes.strip(),
                            )
                            st.success("Evidence review updated.")
                            st.rerun()

            st.caption(
                "Evidence location is currently stored as a reference only. "
                "This version does not upload or store the actual evidence file."
            )

    # ---------------------------------------------------------
    # TAB 4: REMEDIATION MANAGEMENT
    # ---------------------------------------------------------
    with tab_remediation:
        st.subheader("Control remediation actions")

        if not system_assessments:
            st.info(
                "Assess at least one control before creating remediation actions."
            )
        else:
            remediation_assessment_options = {
                value(assessment, "assessment_id"): (
                    f"{value(control_lookup.get(value(assessment, 'control_id'), {}), 'control_code')} — "
                    f"{value(control_lookup.get(value(assessment, 'control_id'), {}), 'title')}"
                )
                for assessment in system_assessments
            }

            selected_remediation_assessment_id = st.selectbox(
                "Select assessed control",
                options=list(remediation_assessment_options.keys()),
                format_func=lambda assessment_id: (
                    remediation_assessment_options[assessment_id]
                ),
                key="remediation_assessment_selector",
            )

            with st.form("add_remediation_action_form"):
                action_description = st.text_area(
                    "Remediation action",
                    placeholder="Describe the corrective or improvement action.",
                )

                action_owner = st.text_input(
                    "Action owner",
                    placeholder="Person or team responsible",
                )

                due_date = st.date_input("Target due date")

                priority = st.selectbox(
                    "Priority",
                    PRIORITIES,
                    index=1,
                )

                remediation_submitted = st.form_submit_button(
                    "Create remediation action",
                    type="primary",
                )

            if remediation_submitted:
                if not action_description.strip():
                    st.error("Please enter a remediation action.")
                elif not action_owner.strip():
                    st.error("Please enter an action owner.")
                else:
                    add_remediation_action(
                        assessment_id=selected_remediation_assessment_id,
                        action_description=action_description.strip(),
                        action_owner=action_owner.strip(),
                        due_date=due_date.isoformat(),
                        priority=priority,
                    )
                    st.success("Remediation action created.")
                    st.rerun()

            st.markdown("#### Remediation action records")

            remediation_items = list_remediation_actions(
                selected_remediation_assessment_id
            )

            if not remediation_items:
                st.info("No remediation actions have been created.")
            else:
                for action in remediation_items:
                    action_id = value(action, "action_id")

                    with st.expander(
                        value(action, "action_description", "Remediation action")
                    ):
                        st.write(
                            f"**Owner:** {value(action, 'action_owner')}"
                        )
                        st.write(
                            f"**Due date:** {value(action, 'due_date')}"
                        )
                        st.write(
                            f"**Priority:** {value(action, 'priority')}"
                        )
                        st.write(
                            f"**Current status:** {value(action, 'status')}"
                        )

                        with st.form(f"update_remediation_{action_id}"):
                            current_action_status = value(
                                action,
                                "status",
                                "Open",
                            )

                            action_status_index = (
                                REMEDIATION_STATUSES.index(
                                    current_action_status
                                )
                                if current_action_status in REMEDIATION_STATUSES
                                else 0
                            )

                            new_action_status = st.selectbox(
                                "Action status",
                                REMEDIATION_STATUSES,
                                index=action_status_index,
                            )

                            closure_notes = st.text_area(
                                "Progress or closure notes",
                                value=value(action, "closure_notes"),
                                placeholder=(
                                    "Record progress, blockers or closure evidence."
                                ),
                            )

                            action_update_submitted = st.form_submit_button(
                                "Update remediation action"
                            )

                        if action_update_submitted:
                            if (
                                new_action_status == "Closed"
                                and not closure_notes.strip()
                            ):
                                st.error(
                                    "Please provide closure notes before "
                                    "marking the action as closed."
                                )
                            else:
                                update_remediation_action(
                                    action_id=action_id,
                                    status=new_action_status,
                                    closure_notes=closure_notes.strip(),
                                )
                                st.success("Remediation action updated.")
                                st.rerun()

    st.divider()
    st.caption(
        "Prototype governance workspace. Control status, evidence acceptance "
        "and remediation closure require human review. Framework mappings "
        "should be validated against the applicable official framework "
        "documents before operational or compliance use."
    )
