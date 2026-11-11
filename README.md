# AI Governance & Assurance Management Platform

A Python and Streamlit portfolio proof of concept demonstrating an end-to-end workflow for AI system inventory, risk assessment, governance controls, assurance evaluation, security-oriented testing, findings management, remediation tracking, and executive reporting.

**Project status:** Functional portfolio prototype  
**Maintainer:** [@sathyam123](https://github.com/sathyam123)  
**Repository:** https://github.com/sathyam123/ai-governance-assurance-platform

## Overview

The platform brings together practical governance activities that are often managed across separate spreadsheets and tools. It provides a single prototype workspace for recording AI systems, assessing risks, mapping governance controls to selected frameworks, evaluating AI-enabled use cases, tracking findings, and viewing an executive summary.

## Portfolio highlights

This project demonstrates how AI governance activities can be connected in a practical, reviewable workflow using Python, Streamlit, and SQLite.

The implementation highlights:

- Modular Streamlit pages and SQLite-backed records for governance workflows.
- Structured risk scoring, control assessments, evaluation runs, evidence references, and remediation tracking.
- Indicative NIST AI RMF and ISO/IEC 42001 control references, with explicit disclaimers against treating them as certification.
- A fictional HR policy retrieval demo and security-oriented test scenarios designed for portfolio walkthroughs.

## Capabilities

- **AI inventory:** Register AI systems and maintain core ownership, purpose, data, user, provider, and deployment information.
- **Risk assessment:** Record structured risk assessments across six dimensions: privacy and data protection, security and access control, accuracy and reliability, bias and fairness, transparency and user understanding, and human oversight and accountability.
- **Human review:** Record review status and reviewer notes for risk assessments.
- **Governance controls:** Maintain a starter control library and assess implementation and effectiveness for AI systems.
- **Framework reference mapping:** Indicative mappings to NIST AI Risk Management Framework (AI RMF) and ISO/IEC 42001.
- **Evidence and remediation:** Record evidence references, evidence review status, control remediation actions, owners, priorities, and due dates.
- **AI assurance and evaluation:** Maintain test cases, execute evaluation runs, record results and observations, and create linked findings.
- **Security-oriented assurance:** Run prototype scenarios covering unsupported information requests, information disclosure, broad document extraction, retrieval relevance, and access-control considerations.
- **Findings management:** Track severity, root cause, recommendations, owners, due dates, and remediation status.
- **Executive dashboard:** Consolidate inventory, risk, control, evidence, assurance, findings, and remediation indicators from the local database.

## Technology

- Python
- Streamlit
- SQLite
- Keyword-based document retrieval demo
- SQL-based persistence

## Architecture at a glance

```text
Streamlit user interface
        |
        +-- AI inventory and risk assessment
        |
        +-- Governance control management
        |
        +-- AI assurance and evaluation
        |
        +-- Security assurance scenarios
        |
        +-- Findings and remediation
        |
        +-- Executive governance dashboard
        |
        v
     SQLite database
```

The application is modularised under `src/`, with separate UI and database modules for the main governance capabilities.

## Local setup

The exact dependency versions should be taken from the repository's `requirements.txt`.

1. Install Python 3.10 or later.
2. Clone the repository:

   ```powershell
   git clone https://github.com/sathyam123/ai-governance-assurance-platform.git
   cd ai-governance-assurance-platform
   ```

3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the application:

   ```powershell
   python -m streamlit run app.py
   ```

The local database is initialised by the application modules. Use synthetic demonstration records when evaluating or presenting the prototype.

The local HR policy retrieval demo looks for `.txt` policy files under `data/hr_documents/`. Those documents are intentionally not included in this public repository. To exercise retrieval locally, create that folder and add fictional, non-sensitive sample policies. Without local policy files, the chatbot returns its documented no-supporting-information response.

## Framework and assessment disclaimer

NIST AI RMF and ISO/IEC 42001 references in this project are indicative learning and design mappings. They are not a complete control checklist, formal interpretation, conformity assessment, audit opinion, or certification. Risk categories, scoring bands, test outcomes, and dashboard metrics are prototype conventions and should not be represented as official regulatory ratings.

## Prototype limitations

This is a **portfolio proof of concept**, not a production governance platform. In particular:

- Production identity management, authentication, role-based access control, and document-level authorisation are not implemented.
- The HR policy demo uses local document chunking and keyword-based retrieval with mock responses; it is not a production semantic retrieval system and does not call an LLM.
- Security scenarios are prototype evaluation cases, not proof of resistance to real-world attacks or LLM prompt injection.
- Evidence references are recorded as metadata; this does not by itself verify the authenticity or sufficiency of evidence.
- Dashboard indicators summarise records in the local database and depend on the quality and completeness of those records.
- Human review remains necessary. The application does not make autonomous compliance, deployment, or risk-acceptance decisions.

## Safe publication guidance

Do not commit local SQLite databases, HR source documents, credentials, API keys, environment files, virtual environments, or personal information. Keep demonstration data synthetic and non-sensitive.

## Intended use

This repository demonstrates applied thinking across AI governance, quality engineering, risk-based assurance, control tracking, and executive reporting. It is intended for learning, portfolio review, and technical discussion—not for making real-world employment, financial, healthcare, or other consequential decisions.
