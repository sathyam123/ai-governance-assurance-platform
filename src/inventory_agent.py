import json

REQUIRED_FIELDS = ["system_name","business_purpose","business_owner","technical_owner",
                   "department","system_type","model_provider","data_categories",
                   "user_groups","deployment_status","external_users","human_oversight"]

def validate_and_profile(data):
    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    messages = []
    if missing:
        messages.append("Missing required fields: " + ", ".join(missing))
    if data.get("external_users") == "Yes":
        messages.append("External-user access recorded; assess exposure during risk assessment.")
    if data.get("human_oversight") == "No":
        messages.append("No human oversight declared; this requires review during risk assessment.")
    profile = {k: str(data.get(k, "")).strip() for k in
               ["system_name","business_purpose","business_owner","technical_owner","department",
                "system_type","model_provider","deployment_status","external_users","human_oversight"]}
    profile["data_categories"] = json.dumps(data.get("data_categories", []))
    profile["user_groups"] = json.dumps(data.get("user_groups", []))
    profile["inventory_status"] = "Complete" if not missing else "Incomplete"
    profile["validation_messages"] = json.dumps(messages)
    return {"valid": not missing, "status": profile["inventory_status"],
            "messages": messages, "profile": profile}
