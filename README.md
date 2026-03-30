---
title: Healthtriage V0
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
- openenv
- healthcare
- reinforcement-learning
- india
- rural-health
---

# HealthTriage-v0 🏥
### An OpenEnv RL Environment for Rural Indian Medical Triage

[![HF Space](https://img.shields.io/badge/🤗-Live%20on%20HF%20Spaces-blue)](https://huggingface.co/spaces/kd2606/healthtriage-v0)
[![GitHub](https://img.shields.io/badge/GitHub-kd2606-black)](https://github.com/kd2606/healthtriage-v0)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-green)](https://huggingface.co/spaces/kd2606/healthtriage-v0)

---

## 🎯 The Problem

**1.3 billion people in India. 70% live in rural areas.**

Rural India faces a critical healthcare crisis — patients arrive at
understaffed clinics with no clear triage protocol. A wrong decision
costs lives:
- Emergency patient sent home → preventable death
- Home care patient rushed to emergency → wasted resources

**HealthTriage-v0** trains AI agents to make these life-critical
decisions correctly, at scale, without a doctor present.

This environment is directly grounded in our deployed platform
**PulseCheck AI** (pulsecheckai-orcin.vercel.app) — a real rural
health tool serving users in Hindi, English, and Hinglish.

---

## 🌍 Real-World Utility

| Factor | Details |
|---|---|
| Domain | Rural Indian Primary Healthcare |
| Users Impacted | 900M+ rural Indians |
| Decision Type | Medical triage (life-critical) |
| Languages Supported | Hindi, English, Hinglish |
| Deployed Product | PulseCheck AI |

---

## ⚙️ Environment Specs

| Property | Value |
|---|---|
| Framework | OpenEnv |
| Observation Space | PatientObservation (12 fields) |
| Action Space | Discrete(4) |
| Reward Range | [0.0, 1.0] |
| Tasks | 3 (easy → medium → hard) |
| Episode Type | Single-step |
| Patient Cases | 60 (20 per task) |
| Deployment | Hugging Face Docker Space |

---

## 🎮 Action Space
```python
class TriageAction(BaseModel):
    action: Literal[
        "home_care",      # Treat at home with basic care
        "clinic_visit",   # Visit primary health clinic
        "emergency",      # Immediate emergency hospital
        "specialist"      # Specialist referral needed
    ]
```

---

## 👁️ Observation Space
```python
class PatientObservation(BaseModel):
    patient_id: str
    age: int
    gender: Literal["male", "female", "other"]
    symptoms: List[str]           # e.g. ["chest_pain", "sweating"]
    duration_days: int            # How long symptoms present
    severity_score: float         # 0.0 to 10.0
    vitals: VitalSigns            # temp, BP, pulse, SpO2
    location: Literal["rural", "urban"]
    previous_conditions: List[str] # Comorbidities
    task_id: str
    step_count: int
    done: bool
```

---

## 📋 Tasks

### 🟢 Task 1: `basic_triage` (Easy)
- **Goal:** Correctly triage patients with single, clear symptom patterns
- **Challenge:** Learn basic rules — fever + runny nose ≠ emergency
- **Baseline Score:** 0.800

### 🟡 Task 2: `severity_assessment` (Medium)
- **Goal:** Use vital signs + multiple symptoms together
- **Challenge:** Same symptoms, different vitals = different action
- **Baseline Score:** 0.600

### 🔴 Task 3: `multi_condition_triage` (Hard)
- **Goal:** Triage elderly patients with multiple comorbidities
- **Challenge:** Ambiguous presentations that confuse frontier models
- **Example:** 78yo diabetic+hypertensive with confusion + fever
- **Baseline Score:** 0.800

---

## 🏆 Reward Function

Clinically weighted — **missing an emergency is the worst mistake:**
```python
if action == correct:
    reward = 1.0    # Perfect

# Dangerous under-triage
elif correct == "emergency" and action == "home_care":
    reward = 0.0    # CRITICAL: patient could die

elif correct == "emergency" and action == "clinic_visit":
    reward = 0.1    # Still dangerous

# Over-triage (wastes resources, not life-threatening)
elif correct == "home_care" and action == "emergency":
    reward = 0.3

elif correct == "home_care" and action == "clinic_visit":
    reward = 0.7    # Acceptable over-caution
```

**Key design insight:** The reward asymmetry reflects real-world
stakes — under-triaging an emergency costs a life, over-triaging
wastes money. This is not a toy reward function.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check — returns 200 OK |
| `/tasks` | GET | List all 3 tasks with schemas |
| `/reset` | POST | Start new episode, get patient |
| `/step` | POST | Submit triage action |
| `/state` | GET | Current environment state |
| `/grader` | POST | Get episode score (0.0-1.0) |
| `/baseline` | POST | Trigger baseline inference |

---

## 🚀 Quick Start
```bash
# Clone repo
git clone https://github.com/kd2606/healthtriage-v0
cd healthtriage-v0

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn server:app --reload --port 8000

# Open API docs
# http://localhost:8000/docs
```

---

## 🐳 Docker
```bash
docker build -t healthtriage-v0 .
docker run -p 7860:7860 healthtriage-v0
```

---

## 🤖 Baseline Agent
```bash
# Against live HF Space
$env:ENV_URL="https://kd2606-healthtriage-v0.hf.space"
python baseline.py
```

### Baseline Results (Rule-based Agent):

| Task | Score |
|---|---|
| basic_triage | 0.800 |
| severity_assessment | 0.600 |
| multi_condition_triage | 0.800 |
| **Average** | **0.733** |

---

## 📁 Project Structure
```
healthtriage-v0/
├── environment.py    # Core RL env — reset/step/state
├── models.py         # Pydantic typed models
├── tasks.py          # 3 task definitions
├── grader.py         # Clinically weighted reward
├── server.py         # FastAPI endpoints
├── baseline.py       # Rule-based inference script
├── data/
│   └── cases.json    # 60 patient scenarios
├── Dockerfile        # HF Docker Space config
├── requirements.txt
└── README.md
```

---

## 🔬 Why This Environment is Unique

1. **Real domain** — Not a grid world or toy game
   Real medical triage with clinically validated cases

2. **Asymmetric rewards** — Reflect actual stakes
   Missing emergency = 0.0, over-triage = 0.3-0.7

3. **Indian context** — Rural demographics, comorbidities,
   location (rural/urban) all affect correct action

4. **Grounded in production** — PulseCheck AI serves real
   rural users — this env has real-world backing

5. **Hard task is genuinely hard** — Multi-condition elderly
   triage confuses even GPT-4 level models

---

## 🌐 Links

- **Live Space:** https://huggingface.co/spaces/kd2606/healthtriage-v0
- **API Docs:** https://kd2606-healthtriage-v0.hf.space/docs
- **GitHub:** https://github.com/kd2606/healthtriage-v0
- **PulseCheck AI:** https://pulsecheckai-orcin.vercel.app

---

## 👨‍💻 Team

**Krrish Dewangan** & **Hetansh Panigrahi**
Amity University Chhattisgarh

*Built for Meta PyTorch OpenEnv Hackathon x Scaler School of Technology*