from fastapi import FastAPI, HTTPException
from models import TriageAction, PatientObservation
from environment import HealthTriageEnv
from tasks import TASKS
from grader import grade_episode
import subprocess

app = FastAPI(title="HealthTriage-v0")

# One env per task
envs = {
    task_id: HealthTriageEnv(task_id)
    for task_id in TASKS
}
episode_logs = {t: [] for t in TASKS}

@app.get("/health")
def health():
    return {"status": "ok", "env": "healthtriage-v0"}

@app.get("/tasks")
def get_tasks():
    return {"tasks": list(TASKS.values())}

@app.post("/reset")
def reset(task_id: str = "basic_triage"):
    if task_id not in envs:
        raise HTTPException(404, f"Unknown task: {task_id}")
    episode_logs[task_id] = []
    obs = envs[task_id].reset()
    return obs.dict()

@app.post("/step")
def step(action: TriageAction, task_id: str = "basic_triage"):
    if task_id not in envs:
        raise HTTPException(404, f"Unknown task: {task_id}")
    obs, reward, done, info = envs[task_id].step(action)
    episode_logs[task_id].append({"reward": reward, **info})
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state(task_id: str = "basic_triage"):
    if task_id not in envs:
        raise HTTPException(404, f"Unknown task: {task_id}")
    return envs[task_id].state()

@app.post("/grader")
def grader(task_id: str = "basic_triage"):
    score = grade_episode(episode_logs.get(task_id, []))
    return {"task_id": task_id, "score": score}

@app.post("/baseline")
def baseline():
    result = subprocess.run(
        ["python", "baseline.py"],
        capture_output=True, text=True
    )
    return {"output": result.stdout, "error": result.stderr}