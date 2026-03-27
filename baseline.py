"""
Baseline inference script for HealthTriage-v0
Run: python baseline.py
"""
import os
import requests
import json
import random

BASE_URL = os.getenv("ENV_URL", "http://localhost:8000")

TASKS = ["basic_triage", "severity_assessment", "multi_condition_triage"]

def simple_agent(obs: dict) -> str:
    """
    Rule-based baseline agent.
    No LLM needed — uses severity score + vitals.
    """
    severity = obs.get("severity_score", 0)
    spo2 = obs.get("vitals", {}).get("spo2_percent", 99)
    pulse = obs.get("vitals", {}).get("pulse_rate", 80)
    bp = obs.get("vitals", {}).get("blood_pressure_systolic", 120)
    age = obs.get("age", 30)

    # Emergency conditions
    if severity >= 8.5:
        return "emergency"
    if spo2 < 92:
        return "emergency"
    if bp > 170:
        return "emergency"
    if pulse > 120:
        return "emergency"

    # Specialist conditions
    if severity >= 5.5 and age > 50:
        return "specialist"
    if severity >= 6.0:
        return "specialist"

    # Clinic visit
    if severity >= 4.0:
        return "clinic_visit"

    # Home care
    return "home_care"


def run_episode(task_id: str, episodes: int = 10) -> float:
    scores = []

    for i in range(episodes):
        try:
            # Reset environment
            reset_resp = requests.post(
                f"{BASE_URL}/reset",
                params={"task_id": task_id},
                timeout=10
            )
            obs = reset_resp.json()

            # Agent decides action
            action_str = simple_agent(obs)
            action = {"action": action_str}

            # Step
            step_resp = requests.post(
                f"{BASE_URL}/step",
                json=action,
                params={"task_id": task_id},
                timeout=10
            )

            # Grade
            grade_resp = requests.post(
                f"{BASE_URL}/grader",
                params={"task_id": task_id},
                timeout=10
            )
            score = grade_resp.json().get("score", 0.0)
            scores.append(score)

        except Exception as e:
            print(f"  Episode {i+1} error: {e}")
            scores.append(0.0)

    return sum(scores) / len(scores) if scores else 0.0


if __name__ == "__main__":
    print("=" * 45)
    print("  HealthTriage-v0 Baseline Scores")
    print("=" * 45)

    all_scores = {}
    for task in TASKS:
        print(f"\nRunning task: {task}...")
        score = run_episode(task, episodes=10)
        all_scores[task] = score
        print(f"  Score: {score:.3f}")

    avg = sum(all_scores.values()) / len(all_scores)
    print("\n" + "=" * 45)
    print(f"  Average Score: {avg:.3f}")
    print("=" * 45)