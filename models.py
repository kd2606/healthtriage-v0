from pydantic import BaseModel
from typing import Literal, List, Dict, Optional

class TriageAction(BaseModel):
    action: Literal[
        "home_care",
        "clinic_visit",
        "emergency",
        "specialist"
    ]

class VitalSigns(BaseModel):
    temperature_celsius: float
    blood_pressure_systolic: int
    pulse_rate: int
    spo2_percent: int

class PatientObservation(BaseModel):
    patient_id: str
    age: int
    gender: Literal["male", "female", "other"]
    symptoms: List[str]
    duration_days: int
    severity_score: float
    vitals: VitalSigns
    location: Literal["rural", "urban"]
    previous_conditions: List[str]
    task_id: str
    step_count: int
    done: bool
    info: Optional[Dict] = {}