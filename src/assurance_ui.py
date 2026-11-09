
import streamlit as st

from src.database import list_ai_systems
from src.assurance_database import (
    create_test_case,
    list_test_cases,
    update_test_case_status,
)


CATEGORIES = [
    "Accuracy",
    "Retrieval relevance",
    "Groundedness",
    "Completeness",
    "Hallucination",
    "Unsupported-question handling",
    "Bias and fairness",
    "Safety and privacy",
]

SEVERITIES = [
    "Low",
    "Medium",
    "High",
    "Critical",
]


def render_test_case_management():
    st.title("AI Assurance & Evaluation")
    st.caption(
        "Create and manage reusable evaluation scenarios for registered AI systems."
    )

    systems = list_ai_systems()

    if not systems:
        st.warning(
            "No AI systems are registered. Register an AI system before "
            "creating assurance test cases."
        )
        return

    system_lookup = {
        system["system_id"]: system["system_name"]
        for system in systems
    }

    selected_system_id = st.selectbox(
        "Select AI system under evaluation",
        options=list(system_lookup.keys()),
        format_func=lambda system_id: (
            f"{system_lookup[system_id]} ({system_id})"
        ),
        key="assurance_selected_system",
    )

    test_cases = list_test_cases(selected_system_id)

    total_cases = len(test_cases)
    active_cases = sum(
        1 for case in test_cases if case["active"] == 1
    )
    inactive_cases = total_cases - active_cases

    st.divider()
    st.subheader("Test case summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total test cases", total_cases)
    col2.metric("Active test cases", active_cases)
    col3.metric("Inactive test cases", inactive_cases)

    st.divider()

    tab_create, tab_library = st.tabs(
        ["Create test case", "Test case library"]
    )

    # -----------------------------------------------------
    # CREATE TEST CASE
    # -----------------------------------------------------
    with tab_create:
        st.subheader("Create an evaluation test case")

        st.write(
            "Define what the AI system should do and what result "
            "the evaluator should expect."
        )

        with st.form("create_assurance_test_case"):
            category = st.selectbox(
                "Evaluation category",
                CATEGORIES,
            )

            test_name = st.text_input(
                "Test case name",
                placeholder="Example: Verify annual leave answer",
            )

            user_query = st.text_area(
                "Test input / user question",
                placeholder=(
                    "Example: How many days of annual leave "
                    "are employees entitled to?"
                ),
            )

            expected_behavior = st.text_area(
                "Expected behaviour",
                placeholder=(
                    "Describe the correct answer or behaviour "
                    "that the chatbot should demonstrate."
                ),
            )

            expected_source = st.text_input(
                "Expected source document",
                placeholder=(
                    "Example: employee_leave_policy.txt"
                ),
            )

            severity = st.selectbox(
                "Risk severity if the test fails",
                SEVERITIES,
                index=1,
            )

            submitted = st.form_submit_button(
                "Save test case",
                type="primary",
            )

        if submitted:
            if not test_name.strip():
                st.error("Please provide a test case name.")
            elif not user_query.strip():
                st.error("Please provide a test input.")
            elif not expected_behavior.strip():
                st.error("Please describe the expected behaviour.")
            else:
                create_test_case(
                    system_id=selected_system_id,
                    category=category,
                    test_name=test_name.strip(),
                    user_query=user_query.strip(),
                    expected_behavior=expected_behavior.strip(),
                    expected_source=expected_source.strip(),
                    severity=severity,
                )

                st.success("Evaluation test case created successfully.")
                st.rerun()

    # -----------------------------------------------------
    # TEST CASE LIBRARY
    # -----------------------------------------------------
    with tab_library:
        st.subheader("Evaluation test case library")

        if not test_cases:
            st.info(
                "No test cases have been created for this AI system yet."
            )
        else:
            category_filter = st.selectbox(
                "Filter by category",
                ["All categories"] + CATEGORIES,
                key="assurance_category_filter",
            )

            for case in test_cases:
                case_category = case["category"]

                if (
                    category_filter != "All categories"
                    and category_filter != case_category
                ):
                    continue

                case_id = case["test_case_id"]
                status = (
                    "Active"
                    if case["active"] == 1
                    else "Inactive"
                )

                with st.expander(
                    f"{case['test_name']} | {case_category} | {status}"
                ):
                    st.write(
                        f"**Test input:** {case['user_query']}"
                    )

                    st.write(
                        f"**Expected behaviour:** "
                        f"{case['expected_behavior']}"
                    )

                    st.write(
                        f"**Expected source:** "
                        f"{case['expected_source'] or 'Not specified'}"
                    )

                    st.write(
                        f"**Failure severity:** {case['severity']}"
                    )

                    st.caption(
                        f"Test case ID: {case_id}"
                    )

                    with st.form(f"test_case_status_{case_id}"):
                        active = st.checkbox(
                            "Active test case",
                            value=bool(case["active"]),
                        )

                        status_submitted = st.form_submit_button(
                            "Update test case status"
                        )

                    if status_submitted:
                        update_test_case_status(
                            test_case_id=case_id,
                            active=active,
                        )
                        st.success("Test case status updated.")
                        st.rerun()

    st.divider()

    st.info(
        "Test case management is the first stage of AI assurance. "
        "A saved test case is not yet an executed test or a passing result. "
        "Evaluation execution and evidence recording will be implemented "
        "in the next stage."
    )
