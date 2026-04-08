"""
Inference script for HealthTriage-v0
"""
import os
import requests
import json
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.environ.get("API_KEY", os.environ.get("HF_TOKEN", "dummy"))
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
BASE_URL = os.environ.get("ENV_URL", "http://localhost:8000")

TASKS = ["basic_triage", "severity_assessment", "multi_condition_triage"]

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def llm_agent(obs: dict) -> str:
    prompt = f"""You are a medical triage agent for rural India.
Patient info:
- Age: {obs.get('age')}
- Gender: {obs.get('gender')}
- Symptoms: {obs.get('symptoms')}
- Severity score: {obs.get('severity_score')}/10
- Vitals: {obs.get('vitals')}
- Location: {obs.get('location')}
- Previous conditions: {obs.get('previous_conditions')}

Choose exactly ONE action from: home_care, clinic_visit, emergency, specialist

Reply with ONLY a JSON object like: {{"action": "emergency"}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        action = json.loads(text).get("action", "clinic_visit")
        if action not in ["home_care", "clinic_visit", "emergency", "specialist"]:
            action = "clinic_visit"
        return action
    except Exception as e:
        # Fallback to rule-based
        severity = obs.get("severity_score", 0)
        spo2 = obs.get("vitals", {}).get("spo2_percent", 99)
        bp = obs.get("vitals", {}).get("blood_pressure_systolic", 120)
        pulse = obs.get("vitals", {}).get("pulse_rate", 80)
        age = obs.get("age", 30)
        if severity >= 8.5 or spo2 < 92 or bp > 170 or pulse > 120:
            return "emergency"
        if severity >= 5.5 and age > 50: return "specialist"
        if severity >= 6.0: return "specialist"
        if severity >= 4.0: return "clinic_visit"
        return "home_care"

def run_task(task_id: str, episodes: int = 5) -> float:
    scores = []
    for i in range(episodes):
        try:
            obs = requests.post(
                f"{BASE_URL}/reset",
                params={"task_id": task_id},
                timeout=15
            ).json()

            action_str = llm_agent(obs)

            requests.post(
                f"{BASE_URL}/step",
                json={"action": action_str},
                params={"task_id": task_id},
                timeout=15
            )

            score = requests.post(
                f"{BASE_URL}/grader",
                params={"task_id": task_id},
                timeout=15
            ).json().get("score", 0.0)

            print(f"[STEP] step={i+1} reward={score:.4f}", flush=True)
            scores.append(score)

        except Exception as e:
            print(f"[STEP] step={i+1} reward=0.0 error={str(e)}", flush=True)
            scores.append(0.0)

    return sum(scores) / len(scores) if scores else 0.0

if __name__ == "__main__":
    for task in TASKS:
        print(f"[START] task={task}", flush=True)
        score = run_task(task, episodes=5)
        print(f"[END] task={task} score={score:.4f} steps=5", flush=True)