TASKS = {
    "basic_triage": {
        "id": "basic_triage",
        "difficulty": "easy",
        "description": "Triage patient with single, clear symptom pattern",
        "max_steps": 1,
        "action_schema": {
            "action": "one of: home_care, clinic_visit, emergency, specialist"
        }
    },
    "severity_assessment": {
        "id": "severity_assessment",
        "difficulty": "medium",
        "description": "Triage based on vital signs and multiple symptoms",
        "max_steps": 1,
        "action_schema": {
            "action": "one of: home_care, clinic_visit, emergency, specialist"
        }
    },
    "multi_condition_triage": {
        "id": "multi_condition_triage",
        "difficulty": "hard",
        "description": "Triage elderly patient with comorbidities and ambiguous vitals",
        "max_steps": 1,
        "action_schema": {
            "action": "one of: home_care, clinic_visit, emergency, specialist"
        }
    }
}