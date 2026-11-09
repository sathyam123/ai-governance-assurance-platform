import streamlit as st

from src.database import list_ai_systems

from src.assurance_database import (
    create_evaluation_run,
    list_evaluation_runs,
    get_evaluation_run,
    complete_evaluation_run,
    list_test_cases,
    save_evaluation_result,
    list_evaluation_results,
)


RESULT_STATUSES = [
    "Pass",
    "Fail",
    "Needs Review",
]

SCORE_GUIDANCE = """
**Scoring guide (0–5)**

- 0 – Completely inadequate
- 1 – Very poor
- 2 – Partially meets expectations
- 3 – Acceptable, with gaps
- 4 – Good, minor gaps
- 5 – Fully meets expectations

Scores support the evaluator's judgement. They do not automatically
determine the Pass/Fail result.
"""


def _system_label(system):
    return (
        f'{system["system_name"]} '
        f'({system["system_id"]})'
    )

def _run_label(run):
    return (
        f'{run["run_name"]} | {run["run_status"]} | '
        f'{run["created_at"][:10]}'
    )


def _test_case_label(test_case):
    return (
        f'{test_case["test_name"]} | '
        f'{test_case["category"]} | '
        f'{test_case["severity"]}'
    )


def render_evaluation_execution():

    st.title("AI Assurance – Evaluation Execution")

    st.caption(
        "Create evaluation runs, assess AI responses, "
        "record evidence and review outcomes."
    )

    systems = list_ai_systems()

    if not systems:
        st.warning(
            "No AI systems are registered. Register an AI system "
            "before creating an evaluation run."
        )
        return

    system = st.selectbox(
        "Select AI system",
        systems,
        format_func=_system_label,
        key="assurance_execution_system",
    )

    system_id = system["system_id"]

    st.divider()

    create_tab, execution_tab, history_tab = st.tabs(
        [
            "Create evaluation run",
            "Execute test cases",
            "Evaluation history",
        ]
    )

    # --------------------------------------------------
    # TAB 1: CREATE EVALUATION RUN
    # --------------------------------------------------

    with create_tab:

        st.subheader("Create a new evaluation run")

        with st.form("create_evaluation_run_form"):

            run_name = st.text_input(
                "Evaluation run name",
                placeholder="Example: HR Chatbot – Initial Evaluation",
            )

            evaluator = st.text_input(
                "Evaluator name",
                placeholder="Example: AI Assurance Lead",
            )

            environment = st.selectbox(
                "Evaluation environment",
                [
                    "Local prototype",
                    "Development",
                    "Test",
                    "Staging",
                    "Production",
                    "Other",
                ],
            )

            run_notes = st.text_area(
                "Evaluation scope and notes",
                placeholder=(
                    "Describe the purpose, scope, version or "
                    "conditions of this evaluation."
                ),
            )

            submitted = st.form_submit_button(
                "Create evaluation run",
                type="primary",
            )

            if submitted:

                if not run_name.strip():
                    st.error("Enter an evaluation run name.")

                elif not evaluator.strip():
                    st.error("Enter the evaluator name.")

                else:

                    run_id = create_evaluation_run(
                        system_id=system_id,
                        run_name=run_name.strip(),
                        evaluator=evaluator.strip(),
                        environment=environment,
                        notes=run_notes.strip(),
                    )

                    st.session_state[
                        "selected_assurance_run"
                    ] = run_id

                    st.success(
                        f"Evaluation run created successfully. "
                        f"Run ID: {run_id}"
                    )

                    st.rerun()

    # --------------------------------------------------
    # TAB 2: EXECUTE TEST CASES
    # --------------------------------------------------

    with execution_tab:

        st.subheader("Execute registered test cases")

        runs = [
    dict(run)
    for run in list_evaluation_runs(system_id)
]

        if not runs:

            st.info(
                "Create an evaluation run before executing test cases."
            )

        else:

            selected_run_id = st.selectbox(
                "Select evaluation run",
                runs,
                format_func=_run_label,
                key="assurance_execution_run",
                index=next(
                    (
                        i for i, run in enumerate(runs)
                        if run["run_id"] == st.session_state.get(
                            "selected_assurance_run"
                        )
                    ),
                    0,
                ),
            )["run_id"]

            selected_run = get_evaluation_run(selected_run_id)

            results = list_evaluation_results(selected_run_id)

            test_cases = [
    dict(case)
    for case in list_test_cases(
        system_id=system_id,
        active_only=True,
    )
]

            completed_case_ids = {
                result["test_case_id"]
                for result in results
            }

            total_cases = len(test_cases)
            evaluated_cases = len(completed_case_ids)
            pending_cases = max(
                total_cases - evaluated_cases,
                0,
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Active test cases", total_cases)
            col2.metric("Evaluated", evaluated_cases)
            col3.metric("Pending", pending_cases)

            st.write(
                f'**Run status:** {selected_run["run_status"]}'
            )

            if selected_run["run_status"] == "Completed":

                st.success(
                    "This evaluation run is completed. "
                    "Create another run for additional testing."
                )

            elif not test_cases:

                st.warning(
                    "There are no active test cases for this AI system."
                )

            else:

                st.markdown("### Select a test case")

                selected_case = st.selectbox(
                    "Test case",
                    test_cases,
                    format_func=_test_case_label,
                    key="assurance_execution_case",
                )

                st.markdown("#### Test case details")

                st.write(
                    f'**Category:** {selected_case["category"]}'
                )

                st.write(
                    f'**Failure severity:** '
                    f'{selected_case["severity"]}'
                )

                st.write("**User query**")
                st.info(selected_case["user_query"])

                st.write("**Expected behaviour**")
                st.write(selected_case["expected_behavior"])

                st.write(
                    f'**Expected source:** '
                    f'{selected_case["expected_source"] or "Not specified"}'
                )

                st.divider()

                st.markdown("### Record actual chatbot behaviour")

                st.caption(
                    "Run the query in your HR RAG Chatbot, then "
                    "record its response and the sources it retrieved."
                )

                with st.form(
                    f"evaluation_result_{selected_run_id}_"
                    f'{selected_case["test_case_id"]}'
                ):

                    actual_response = st.text_area(
                        "Actual chatbot response",
                        height=180,
                        placeholder=(
                            "Paste the chatbot's actual response here."
                        ),
                    )

                    retrieved_sources = st.text_area(
                        "Retrieved sources",
                        height=90,
                        placeholder=(
                            "Example: employee_leave_policy.txt"
                        ),
                    )

                    st.markdown("#### Evaluation outcome")

                    result_status = st.radio(
                        "Result",
                        RESULT_STATUSES,
                        horizontal=True,
                    )

                    st.markdown("#### Quality scores")

                    st.caption(
                        "Rate each dimension from 0 (poor) to 5 (excellent)."
                    )

                    accuracy_score = st.slider(
                        "Accuracy",
                        min_value=0,
                        max_value=5,
                        value=3,
                    )

                    retrieval_score = st.slider(
                        "Retrieval relevance",
                        min_value=0,
                        max_value=5,
                        value=3,
                    )

                    groundedness_score = st.slider(
                        "Groundedness",
                        min_value=0,
                        max_value=5,
                        value=3,
                    )

                    completeness_score = st.slider(
                        "Completeness",
                        min_value=0,
                        max_value=5,
                        value=3,
                    )

                    evaluator_notes = st.text_area(
                        "Evaluator observations",
                        placeholder=(
                            "Explain why the result passed, failed "
                            "or requires further review."
                        ),
                    )

                    evaluated_by = st.text_input(
                        "Evaluated by",
                        value=selected_run["evaluator"],
                    )

                    save_result = st.form_submit_button(
                        "Save evaluation result",
                        type="primary",
                    )

                    if save_result:

                        if not actual_response.strip():
                            st.error(
                                "Enter the actual chatbot response."
                            )

                        elif not evaluated_by.strip():
                            st.error(
                                "Enter the evaluator name."
                            )

                        elif (
                            result_status != "Pass"
                            and not evaluator_notes.strip()
                        ):
                            st.error(
                                "Add evaluator observations for "
                                "Fail or Needs Review results."
                            )

                        else:

                            save_evaluation_result(
                                run_id=selected_run_id,
                                test_case_id=selected_case[
                                    "test_case_id"
                                ],
                                actual_response=actual_response.strip(),
                                retrieved_sources=retrieved_sources.strip(),
                                result_status=result_status,
                                accuracy_score=accuracy_score,
                                retrieval_score=retrieval_score,
                                groundedness_score=groundedness_score,
                                completeness_score=completeness_score,
                                evaluator_notes=evaluator_notes.strip(),
                                evaluated_by=evaluated_by.strip(),
                            )

                            st.success(
                                "Evaluation result saved successfully."
                            )

                            st.rerun()

                with st.expander("Scoring guidance"):
                    st.markdown(SCORE_GUIDANCE)

            st.divider()

            st.markdown("### Evaluation run results")

            results = list_evaluation_results(selected_run_id)

            if not results:

                st.info("No evaluation results have been recorded yet.")

            else:

                for result in results:

                    with st.expander(
                        f'{result["test_name"]} | '
                        f'{result["result_status"]}'
                    ):

                        st.write(
                            f'**Category:** {result["category"]}'
                        )

                        st.write(
                            f'**Actual response:** '
                            f'{result["actual_response"]}'
                        )

                        st.write(
                            f'**Retrieved sources:** '
                            f'{result["retrieved_sources"] or "Not recorded"}'
                        )

                        st.write(
                            f'**Accuracy:** {result["accuracy_score"]}/5'
                        )

                        st.write(
                            f'**Retrieval relevance:** '
                            f'{result["retrieval_score"]}/5'
                        )

                        st.write(
                            f'**Groundedness:** '
                            f'{result["groundedness_score"]}/5'
                        )

                        st.write(
                            f'**Completeness:** '
                            f'{result["completeness_score"]}/5'
                        )

                        st.write(
                            f'**Evaluator notes:** '
                            f'{result["evaluator_notes"] or "None"}'
                        )

            if (
                selected_run["run_status"] != "Completed"
                and total_cases > 0
            ):

                if evaluated_cases == total_cases:

                    st.success(
                        "All currently active test cases have results."
                    )

                    if st.button(
                        "Complete evaluation run",
                        type="primary",
                        key=f"complete_{selected_run_id}",
                    ):

                        complete_evaluation_run(selected_run_id)

                        st.success(
                            "Evaluation run marked as completed."
                        )

                        st.rerun()

                else:

                    st.info(
                        "Complete all active test cases before "
                        "closing this evaluation run."
                    )

    # --------------------------------------------------
    # TAB 3: EVALUATION HISTORY
    # --------------------------------------------------

    with history_tab:

        st.subheader("Evaluation history")

        runs = [
    dict(run)
    for run in list_evaluation_runs(system_id)
]

        if not runs:

            st.info("No evaluation runs found.")

        else:

            for run in runs:

                run_results = list_evaluation_results(
                    run["run_id"]
                )

                pass_count = sum(
                    1 for item in run_results
                    if item["result_status"] == "Pass"
                )

                fail_count = sum(
                    1 for item in run_results
                    if item["result_status"] == "Fail"
                )

                review_count = sum(
                    1 for item in run_results
                    if item["result_status"] == "Needs Review"
                )

                with st.expander(
                    f'{run["run_name"]} | {run["run_status"]}'
                ):

                    st.write(
                        f'**Evaluator:** {run["evaluator"]}'
                    )

                    st.write(
                        f'**Environment:** {run["environment"]}'
                    )

                    st.write(
                        f'**Created:** {run["created_at"]}'
                    )

                    st.write(
                        f'**Completed:** '
                        f'{run["completed_at"] or "Not completed"}'
                    )

                    st.write(
                        f'**Pass:** {pass_count} | '
                        f'**Fail:** {fail_count} | '
                        f'**Needs Review:** {review_count}'
                    )

                    st.write(
                        f'**Notes:** {run["notes"] or "None"}'
                    )

                    st.caption(
                        f'Run ID: {run["run_id"]}'
                    )