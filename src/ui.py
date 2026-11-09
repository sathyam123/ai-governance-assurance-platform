
import json
import streamlit as st

from src.database import (
    create_ai_system,
    list_ai_systems,
    list_risk_assessments,
    save_risk_assessment,
    update_assessment_review,
)
from src.inventory_agent import validate_and_profile
from src.risk_agent import RISK_DIMENSIONS, assess_dimensions


def render_registration():
    st.subheader("Register an AI system")
    st.write("Enter system information. The inventory agent validates required fields before saving.")

    with st.form("register_ai_system"):
        name = st.text_input("AI system name", "HR RAG Chatbot")
        purpose = st.text_area(
            "Business purpose",
            "Answers employee questions about approved HR policies, leave, benefits and workplace procedures."
        )

        c1, c2 = st.columns(2)

        with c1:
            owner = st.text_input("Business owner", "HR Operations")
            tech = st.text_input("Technical owner", "Enterprise AI Team")
            dept = st.selectbox(
                "Department",
                ["Human Resources", "IT", "Finance", "Legal", "Operations", "Other"]
            )
            kind = st.selectbox(
                "System type",
                ["Generative AI / RAG", "Predictive ML", "Classification", "AI agent", "Other"]
            )
            provider = st.selectbox(
                "Model provider",
                ["OpenAI", "Azure OpenAI", "Anthropic", "Open-source model", "Other / not decided"]
            )

        with c2:
            data = st.multiselect(
                "Data categories",
                [
                    "Public HR policies",
                    "Employee personal data",
                    "Compensation data",
                    "Performance data",
                    "Health-related data",
                    "Other confidential data"
                ],
                default=["Public HR policies"]
            )
            users = st.multiselect(
                "Intended user groups",
                ["Employees", "HR staff", "Managers", "External applicants", "External vendors"],
                default=["Employees", "HR staff"]
            )
            deployment = st.selectbox(
                "Deployment status",
                ["Concept", "Development", "Pilot", "Production", "Retired"]
            )
            external = st.radio(
                "Can external users access it?",
                ["No", "Yes"],
                horizontal=True
            )
            oversight = st.radio(
                "Is human oversight available?",
                ["Yes", "No", "Under design"],
                horizontal=True
            )

        submitted = st.form_submit_button("Validate and register", type="primary")

    if submitted:
        result = validate_and_profile({
            "system_name": name,
            "business_purpose": purpose,
            "business_owner": owner,
            "technical_owner": tech,
            "department": dept,
            "system_type": kind,
            "model_provider": provider,
            "data_categories": data,
            "user_groups": users,
            "deployment_status": deployment,
            "external_users": external,
            "human_oversight": oversight
        })

        if result["valid"]:
            sid = create_ai_system(result["profile"])
            st.success(f"Registered successfully. Inventory ID: {sid}")
        else:
            st.error("Inventory record incomplete; it was not saved.")

        for msg in result["messages"]:
            st.warning(msg)


def render_inventory():
    st.subheader("AI system inventory")
    systems = list_ai_systems()

    if not systems:
        st.info("No systems registered yet.")
        return

    for system in systems:
        with st.container(border=True):
            st.subheader(system["system_name"])
            st.write(f"Inventory ID: {system['system_id']}")
            st.write(f"Department: {system['department']}")
            st.write(f"Business owner: {system['business_owner']}")
            st.write(f"System type: {system['system_type']}")
            st.write(f"Deployment: {system['deployment_status']}")
            st.write(f"Inventory validation: {system['inventory_status']}")
            st.write(f"Risk assessment: {system['risk_status']}")


def render_system_detail(system):
    if not system:
        st.warning("System not found.")
        return

    st.subheader(system["system_name"])
    st.caption(f"Inventory ID: {system['system_id']}")

    a, b, c = st.columns(3)
    a.metric("Inventory status", system["inventory_status"])
    b.metric("Risk assessment", system["risk_status"])
    c.metric("Deployment", system["deployment_status"])

    st.markdown("### System profile")

    for label, key in [
        ("Business purpose", "business_purpose"),
        ("Business owner", "business_owner"),
        ("Technical owner", "technical_owner"),
        ("Department", "department"),
        ("System type", "system_type"),
        ("Model provider", "model_provider"),
        ("External users", "external_users"),
        ("Human oversight", "human_oversight")
    ]:
        st.write(f"**{label}:** {system[key]}")

    st.write("**Data categories:**", ", ".join(json.loads(system["data_categories"])))
    st.write("**User groups:**", ", ".join(json.loads(system["user_groups"])))
    st.write("**Created (UTC):**", system["created_at"])

    for msg in json.loads(system["validation_messages"]):
        st.warning(msg)


def render_risk_assessment():
    st.subheader("AI system risk assessment")
    systems = list_ai_systems()

    if not systems:
        st.warning("Register an AI system before starting a risk assessment.")
        return

    options = {
        f"{s['system_name']} ({s['system_id']})": s
        for s in systems
    }

    selected_label = st.selectbox("Select AI system", list(options.keys()))
    selected_system = options[selected_label]

    st.info(
        "Assess each dimension using likelihood and impact. "
        "Scores are illustrative prototype ratings and require human review."
    )

    responses = {}

    with st.form("risk_assessment_form"):
        for dimension, details in RISK_DIMENSIONS.items():
            st.markdown(f"### {dimension}")
            st.caption(details["description"])

            col1, col2 = st.columns(2)

            with col1:
                likelihood = st.slider(
                    f"{dimension} — Likelihood",
                    min_value=1,
                    max_value=5,
                    value=2,
                    key=f"likelihood_{dimension}"
                )

            with col2:
                impact = st.slider(
                    f"{dimension} — Impact",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"impact_{dimension}"
                )

            responses[dimension] = {
                "likelihood": likelihood,
                "impact": impact
            }

            st.caption(f"Suggested mitigation: {details['mitigation']}")
            st.divider()

        submitted = st.form_submit_button("Calculate and save assessment", type="primary")

    if submitted:
        result = assess_dimensions(responses)
        assessment_id = save_risk_assessment(selected_system["system_id"], result)

        st.success(f"Assessment saved. Assessment ID: {assessment_id}")
        st.metric("Overall risk score", result["overall_score"])
        st.metric("Overall risk classification", result["overall_risk"])

        st.markdown("### Dimension results")

        for item in result["dimension_results"]:
            st.write(
                f"**{item['dimension']}:** "
                f"{item['score']} — {item['risk_level']}"
            )


def render_assessment_history():
    st.subheader("Risk assessment history")

    systems = list_ai_systems()

    if not systems:
        st.info("No registered AI systems found.")
        return

    options = {
        f"{s['system_name']} ({s['system_id']})": s["system_id"]
        for s in systems
    }

    selected_label = st.selectbox(
        "Filter by AI system",
        ["All systems"] + list(options.keys())
    )

    if selected_label == "All systems":
        assessments = list_risk_assessments()
    else:
        assessments = list_risk_assessments(options[selected_label])

    if not assessments:
        st.info("No risk assessments found.")
        return

    system_names = {s["system_id"]: s["system_name"] for s in systems}

    for assessment in assessments:
        with st.container(border=True):
            st.markdown(f"### {system_names.get(assessment['system_id'], 'Unknown system')}")
            st.write(f"Assessment ID: {assessment['assessment_id']}")
            st.write(f"Assessment date: {assessment['assessed_at']}")
            st.write(f"Overall score: {assessment['overall_score']}")
            st.write(f"Risk classification: {assessment['overall_risk']}")

            st.write(f"Review status: {assessment['review_status']}")

            details = json.loads(assessment["assessment_details"])

            with st.expander("View dimension results"):
                for item in details:
                    st.write(
                        f"**{item['dimension']}:** "
                        f"{item['score']} — {item['risk_level']}"
                    )
                    st.caption(f"Mitigation: {item['mitigation']}")

            st.write(f"Reviewer notes: {assessment['reviewer_notes'] or 'None'}")

            with st.form(f"review_{assessment['assessment_id']}"):
                review_status = st.selectbox(
                    "Update review status",
                    ["Pending review", "In review", "Reviewed — action required", "Reviewed — no further action"],
                    key=f"status_{assessment['assessment_id']}"
                )

                reviewer_notes = st.text_area(
                    "Reviewer notes",
                    value=assessment["reviewer_notes"] or "",
                    key=f"notes_{assessment['assessment_id']}"
                )

                review_submitted = st.form_submit_button("Save human review")

            if review_submitted:
                update_assessment_review(
                    assessment["assessment_id"],
                    review_status,
                    reviewer_notes
                )
                st.success("Human review updated. Refresh the page to see the saved status.")

def render_hr_chatbot():
    import streamlit as st
    from src.rag_engine import answer_question

    st.header("HR RAG Chatbot")
    st.caption("Ask questions using the available sample HR policy documents.")

    st.info(
        "Prototype: This chatbot uses keyword-based document retrieval "
        "and mock responses. It does not use an LLM. "
        "Always verify HR information against the source policy."
    )

    if "hr_chat_history" not in st.session_state:
        st.session_state.hr_chat_history = []

    # Display previous conversation
    for message in st.session_state.hr_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("Retrieved source documents"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**{source['source']}** "
                            f"(Chunk: {source['chunk_id']}, "
                            f"Score: {source['score']})"
                        )
                        st.write(source["text"])

    # Accept a new question
    question = st.chat_input("Ask an HR policy question...")

    if question:
        st.session_state.hr_chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        result = answer_question(question)

        answer = result["answer"]

        st.session_state.hr_chat_history.append({
            "role": "assistant",
            "content": answer,
            "sources": result["sources"]
        })

        with st.chat_message("assistant"):
            st.markdown(answer)

            if result["sources"]:
                with st.expander("Retrieved source documents"):
                    for source in result["sources"]:
                        st.markdown(
                            f"**{source['source']}** "
                            f"(Chunk: {source['chunk_id']}, "
                            f"Score: {source['score']})"
                        )
                        st.write(source["text"])

    if st.button("Clear chat history"):
        st.session_state.hr_chat_history = []
        st.rerun()

