import json
import random
from pathlib import Path
from models import PatientObservation, TriageAction, VitalSigns
from grader import calculate_reward

class HealthTriageEnv:
    def __init__(self, task_id: str = "basic_triage"):
        self.task_id = task_id
        self.step_count = 0
        self.current_case = None
        self.done = False

        # Load cases
        cases_path = Path("data/cases.json")
        with open(cases_path) as f:
            all_cases = json.load(f)
        self.cases = [c for c in all_cases
                      if c["task_id"] == task_id]

    def reset(self) -> PatientObservation:
        """Reset env, return fresh patient observation"""
        self.step_count = 0
        self.done = False
        self.current_case = random.choice(self.cases)
        return self._build_observation()

    def step(self, action: TriageAction):
        """Take action, return (observation, reward, done, info)"""
        if self.done:
            raise ValueError("Episode done. Call reset() first.")

        reward, info = calculate_reward(
            action.action,
            self.current_case["correct_action"],
            self.current_case["severity"]
        )

        self.step_count += 1
        self.done = True

        obs = self._build_observation()
        return obs, reward, self.done, info

    def state(self) -> dict:
        """Return current env state"""
        return {
            "task_id": self.task_id,
            "step_count": self.step_count,
            "done": self.done,
            "current_case_id": self.current_case.get(
                "patient_id") if self.current_case else None
        }

    def _build_observation(self) -> PatientObservation:
        c = self.current_case
        return PatientObservation(
            patient_id=c["patient_id"],
            age=c["age"],
            gender=c["gender"],
            symptoms=c["symptoms"],
            duration_days=c["duration_days"],
            severity_score=c["severity"],
            vitals=VitalSigns(**c["vitals"]),
            location=c["location"],
            previous_conditions=c.get("previous_conditions", []),
            task_id=self.task_id,
            step_count=self.step_count,
            done=self.done
        )