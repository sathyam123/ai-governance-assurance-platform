
import streamlit as st
from src.assurance_database import init_assurance_tables
from src.security_assurance_ui import render_security_assurance
from src.assurance_findings_ui import render_assurance_findings
from src.assurance_execution_ui import render_evaluation_execution
from src.executive_dashboard import render_executive_dashboard
from src.assurance_ui import render_test_case_management
from src.control_database import (
    init_control_tables,
    seed_starter_controls,
)

from src.control_ui import render_control_management

from src.database import (
    init_db,
    init_risk_assessment_table,
    list_ai_systems,
)
from src.ui import (
    render_inventory,
    render_registration,
    render_system_detail,
    render_risk_assessment,
    render_hr_chatbot,
    render_assessment_history,
)

st.set_page_config(
    page_title="Agentic AI Governance & Assurance",
    page_icon="ðŸ›¡ï¸",
    layout="wide",
)

# Initialise database tables
init_db()
init_risk_assessment_table()
init_control_tables()
seed_starter_controls()
init_assurance_tables()

st.title("ðŸ›¡ï¸ Agentic AI Governance & Assurance")
st.caption(
    "Portfolio POC | AI inventory, risk, controls and assurance"
)

with st.sidebar:
    st.header("Governance workspace")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Register AI system",
            "AI inventory",
            "System details",
            "Risk assessment",
            "Assessment history",
	    "HR RAG Chatbot",
            "Control Management",
            "AI Assurance & Evaluation",
            "Evaluation Execution",
"Assurance Findings & Remediation",
"AI Security Assurance",
"Executive AI Governance Dashboard",
        ],
    )

    st.divider()
    st.caption("Prototype status: Functional portfolio POC")
    st.caption("Deterministic risk scoring; human review required.")

if page == "Overview":
    systems = list_ai_systems()

    assessments_pending = sum(
        x["risk_status"] == "Not assessed" for x in systems
    )

    a, b, c = st.columns(3)

    a.metric("Registered AI systems", len(systems))

    b.metric(
        "Systems assessed",
        len(systems) - assessments_pending
    )

    c.metric(
        "Awaiting risk assessment",
        assessments_pending
    )

    st.markdown("### Governance workflow")

    st.markdown(
        """
        1. Register an AI system.
        2. Validate inventory information.
        3. Conduct a six-dimension risk assessment.
        4. Calculate likelihood and impact scores.
        5. Review risk results and suggested mitigations.
        6. Record human review and reviewer notes.
        """
    )

    st.info(
        "Risk scores are illustrative prototype assessments. "
        "They do not constitute regulatory certification, "
        "deployment approval or an autonomous governance decision."
    )

elif page == "Register AI system":
    render_registration()

elif page == "AI inventory":
    render_inventory()

elif page == "System details":
    systems = list_ai_systems()

    if not systems:
        st.warning("No AI systems registered yet.")
    else:
        system_options = {
            f"{x['system_name']} ({x['system_id']})": x
            for x in systems
        }

        selected_label = st.selectbox(
            "Select an AI system",
            list(system_options.keys())
        )

        render_system_detail(system_options[selected_label])

elif page == "Risk assessment":
    render_risk_assessment()

elif page == "Assessment history":
    render_assessment_history()
elif page == "HR RAG Chatbot":
    render_hr_chatbot()
elif page == "Control Management":
    render_control_management()
elif page == "AI Assurance & Evaluation":
    render_test_case_management()
elif page == "Evaluation Execution":
    render_evaluation_execution()
elif page == "Assurance Findings & Remediation":
    render_assurance_findings()
elif page == "AI Security Assurance":
    render_security_assurance()
elif page == "Executive AI Governance Dashboard":
    render_executive_dashboard()
