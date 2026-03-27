def calculate_reward(
    action: str,
    correct: str,
    severity: float
) -> tuple:
    """
    Returns reward (0.0-1.0) and info dict.
    Clinically weighted: missing emergency = max penalty.
    """

    if action == correct:
        reward = 1.0
        explanation = "Correct triage decision"

    # Dangerous under-triage
    elif correct == "emergency" and action == "home_care":
        reward = 0.0
        explanation = "CRITICAL: Emergency patient sent home"

    elif correct == "emergency" and action == "clinic_visit":
        reward = 0.1
        explanation = "Emergency patient under-triaged to clinic"

    elif correct == "emergency" and action == "specialist":
        reward = 0.2
        explanation = "Emergency redirected — delay risk"

    # Over-triage
    elif correct == "home_care" and action == "emergency":
        reward = 0.3
        explanation = "Over-triage: wastes emergency resources"

    elif correct == "home_care" and action == "clinic_visit":
        reward = 0.7
        explanation = "Slight over-triage, not harmful"

    # Specialist misjudgment
    elif correct == "specialist" and action == "clinic_visit":
        reward = 0.5
        explanation = "Reasonable but specialist needed"

    elif correct == "specialist" and action == "emergency":
        reward = 0.4
        explanation = "Over-escalated to emergency"

    else:
        reward = 0.3
        explanation = f"Mismatch: expected {correct}, got {action}"

    info = {
        "correct_action": correct,
        "agent_action": action,
        "explanation": explanation,
        "severity": severity,
        "partial_credit": reward
    }

    return reward, info


def grade_episode(actions_log: list) -> float:
    """Score full episode 0.0-1.0"""
    if not actions_log:
        return 0.0
    return sum(a["reward"] for a in actions_log) / len(actions_log)