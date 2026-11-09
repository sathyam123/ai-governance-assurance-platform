
RISK_DIMENSIONS = {
    "Privacy and data protection": {
        "description": "Personal data, sensitive information, data minimisation and retention.",
        "mitigation": "Apply data minimisation, access restrictions, retention limits and privacy review."
    },
    "Security and access control": {
        "description": "Unauthorised access, prompt injection, data leakage and system vulnerabilities.",
        "mitigation": "Implement RBAC, authentication, input validation, security testing and audit logging."
    },
    "Accuracy and reliability": {
        "description": "Incorrect, unsupported, inconsistent or misleading AI outputs.",
        "mitigation": "Use representative evaluation datasets, accuracy tests, RAG grounding checks and monitoring."
    },
    "Bias and fairness": {
        "description": "Unequal outcomes or potentially discriminatory responses across user groups.",
        "mitigation": "Evaluate outputs across relevant groups and introduce fairness testing and escalation."
    },
    "Transparency and user understanding": {
        "description": "Users may not understand that they are interacting with AI or its limitations.",
        "mitigation": "Disclose AI usage, explain limitations and provide appropriate user guidance."
    },
    "Human oversight and accountability": {
        "description": "Insufficient human review, escalation, ownership or accountability.",
        "mitigation": "Define accountable owners, human review points, escalation routes and approval records."
    }
}


def calculate_risk(likelihood, impact):
    """Calculate an illustrative risk score from likelihood and impact."""
    likelihood = int(likelihood)
    impact = int(impact)

    if not 1 <= likelihood <= 5:
        raise ValueError("Likelihood must be between 1 and 5.")

    if not 1 <= impact <= 5:
        raise ValueError("Impact must be between 1 and 5.")

    return likelihood * impact


def classify_risk(score):
    """Return an illustrative prototype risk band."""
    score = int(score)

    if not 1 <= score <= 25:
        raise ValueError("Risk score must be between 1 and 25.")

    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Moderate"
    elif score <= 16:
        return "High"
    return "Critical"


def assess_dimensions(responses):
    """
    Calculate scores for all six dimensions.

    responses format:
    {
        "Privacy and data protection": {
            "likelihood": 3,
            "impact": 4
        },
        ...
    }
    """
    results = []

    for dimension, details in RISK_DIMENSIONS.items():
        if dimension not in responses:
            raise ValueError(f"Missing assessment: {dimension}")

        likelihood = int(responses[dimension]["likelihood"])
        impact = int(responses[dimension]["impact"])

        score = calculate_risk(likelihood, impact)

        results.append({
            "dimension": dimension,
            "description": details["description"],
            "likelihood": likelihood,
            "impact": impact,
            "score": score,
            "risk_level": classify_risk(score),
            "mitigation": details["mitigation"]
        })

    average_score = sum(item["score"] for item in results) / len(results)
    overall_score = int(average_score + 0.5)

    return {
        "overall_score": overall_score,
        "overall_risk": classify_risk(overall_score),
        "dimension_results": results
    }
