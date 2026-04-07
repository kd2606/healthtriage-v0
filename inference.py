"""
Inference script for HealthTriage-v0
"""
import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "")
BASE_URL = os.getenv("ENV_URL", "http://localhost:8000")

TASKS = ["basic_triage", "severity_assessment", "multi_condition_triage"]

def simple_agent(obs: dict) -> str:
    severity = obs.get("severity_score", 0)
    spo2 = obs.get("vitals", {}).get("spo2_percent", 99)
    pulse = obs.get("vitals", {}).get("pulse_rate", 80)
    bp = obs.get("vitals", {}).get("blood_pressure_systolic", 120)
    age = obs.get("age", 30)

    if severity >= 8.5: return "emergency"
    if spo2 < 92: return "emergency"
    if bp > 170: return "emergency"
    if pulse > 120: return "emergency"
    if severity >= 5.5 and age > 50: return "specialist"
    if severity >= 6.0: return "specialist"
    if severity >= 4.0: return "clinic_visit"
    return "home_care"

def run_task(task_id: str, episodes: int = 10) -> float:
    scores = []
    for i in range(episodes):
        try:
            obs = requests.post(
                f"{BASE_URL}/reset",
                params={"task_id": task_id},
                timeout=10
            ).json()

            action_str = simple_agent(obs)

            requests.post(
                f"{BASE_URL}/step",
                json={"action": action_str},
                params={"task_id": task_id},
                timeout=10
            )

            score = requests.post(
                f"{BASE_URL}/grader",
                params={"task_id": task_id},
                timeout=10
            ).json().get("score", 0.0)

            print(f"[STEP] step={i+1} reward={score:.4f}", flush=True)
            scores.append(score)

        except Exception as e:
            print(f"[STEP] step={i+1} reward=0.0 error={e}", flush=True)
            scores.append(0.0)

    return sum(scores) / len(scores) if scores else 0.0

if __name__ == "__main__":
    for task in TASKS:
        print(f"[START] task={task}", flush=True)
        score = run_task(task, episodes=10)
        print(f"[END] task={task} score={score:.4f} steps=10", flush=True)