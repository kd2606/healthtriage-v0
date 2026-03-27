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
---

# HealthTriage-v0

RL environment for medical triage in rural India using OpenEnv framework.

## Endpoints
- `POST /reset` - Start new episode
- `POST /step` - Take triage action
- `GET /state` - Current env state
- `GET /tasks` - List all tasks
- `POST /grader` - Get episode score
- `POST /baseline` - Run baseline agent

## Actions
- `home_care` - Treat at home
- `clinic_visit` - Visit nearby clinic
- `emergency` - Emergency hospital
- `specialist` - Specialist referral