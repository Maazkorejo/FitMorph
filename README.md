---
title: FitMorph Adaptive Fitness Intelligence
emoji: 🏋️
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# FitMorph — Adaptive Fitness Intelligence & Physique Progression Engine

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-003B57.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-25%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **FitMorph** is an adaptive, scientifically periodized fitness web engine. It dynamically personalizes training routines, prescribes goal-oriented cardio protocols, protects users from joint harm through an intelligent **Injury Prevention Shield**, tracks tonnage volume loads to schedule deload weeks via **Background Workers**, diagnoses muscular imbalances using **AI Vision Physique Scans**, and compiles executive **Printable 4-Week Coaching Dossiers (PDF)**.

---

## Capstone Core Concepts Implemented

| # | Concept | Implementation in FitMorph |
|---|---------|-----------------------------|
| 1 | **API Endpoints** | High-performance FastAPI routers across Authentication, Biometrics, Workouts, Logs, Plateau, AI Vision, and PDF reporting. |
| 2 | **Database** | Relational SQLite database modeled with SQLAlchemy ORM (Users, Profiles, Exercises, Plans, Days, Logged Sets, Cardio Logs, and Scans). |
| 3 | **Authentication** | Secure bcrypt password hashing with passlib and stateful JWT Bearer tokens with python-jose. |
| 4 | **Background Jobs** | APScheduler background worker continuously evaluating rolling 14-day training volume, detecting strength plateaus, and triggering deload weeks. |
| 5 | **Reporting — PDF** | Dynamic ReportLab PDF compilation generating printable 4-week workout blueprints and muscular symmetry scorecards. |
| 6 | **LLM / Vision AI** | Computer vision integration with Google Gemini Flash Vision analyzing user physique check-ins for posture and muscular symmetry. |

---

## Biomechanical Features & Intelligence

### 1. Goal & Equipment Specialization
- **3 Dynamic Fitness Goals**: Fat Loss, Muscle Building (Hypertrophy), Strength & Power.
- **3 Equipment Tiers**:
  - **Full Gym**: Heavy barbells, cable stations, machines, and dumbbells.
  - **Dumbbells Only**: Minimal home setup focusing on dumbbell compound movements.
  - **No Equipment (Zero-Equipment Calisthenics)**: 100% bodyweight movements (Push-ups, doorframe rows, wall sits, glute bridges).

### 2. Gender-Specific Physiological Adaptations
- **Female Athletes**:
  - Capitalizes on Type I muscle fiber fatigue resistance and faster intra-set ATP recovery.
  - Higher repetition brackets (10–15 reps) and shorter rest periods (45–60 seconds).
  - Posterior chain / glute volume bias (+30%).
- **Male Athletes**:
  - High-intensity neural recruitment (5–8 reps) with longer recovery intervals (90–180 seconds) to dissipate central nervous system fatigue.
  - Upper chest, lateral deltoid, and lat width bias (+25%).

### 3. Injury Prevention Shield
The system filters out contraindicated exercises based on active user injuries:
- **Lower Back**: Bans heavy axial spinal compression lifts (Barbell Back Squats, Barbell Deadlifts); auto-substitutes Dumbbell Goblet Squats, Leg Presses, or Romanian Deadlifts.
- **Shoulders / Rotator Cuff**: Bans flat barbell bench presses and overhead military presses; auto-substitutes Dumbbell Floor Presses and Scapular Plane Cable Lateral Raises.
- **Knees / Patellar Tendonitis**: Bans high-impact plyometrics and deep heavy squats; auto-substitutes Isometric Wall Sits, Glute Bridges, and Low-Impact Incline Walking.
- **1-Click Safe Swapping**: Users can instantly swap any exercise with a single click while preserving biomechanical safety.

---

## Project Structure

```
FitMorph/
├── app/
│   ├── api/                      # FastAPI Endpoint Routers
│   │   ├── auth.py               # User Signup, Login & Me
│   │   ├── profile.py            # Biometrics, Height/Weight, BMI
│   │   ├── exercises.py          # Anatomical Exercise Search
│   │   ├── workouts.py           # Workout Plan Generation & Swaps
│   │   ├── logs.py               # Strength & Cardio Logging
│   │   ├── plateau.py            # Plateau Status & Manual Audits
│   │   ├── physique.py           # Photo Upload & Vision Analysis
│   │   ├── reports.py            # Printable PDF Generation
│   │   ├── coach.py              # AI Coach Form & Recovery Tips
│   │   └── deps.py               # DB and JWT Dependency Injection
│   ├── core/
│   │   ├── config.py             # App Configuration & Settings
│   │   └── security.py           # Bcrypt & JWT Utilities
│   ├── data/                     # Biomechanical Knowledge Base
│   │   ├── exercises_gym.py      # Full-Gym Exercise Catalog
│   │   ├── exercises_dumbbells.py# Dumbbells-Only Catalog
│   │   └── exercises_bodyweight.py# Zero-Equipment Calisthenics
│   ├── db/
│   │   └── session.py            # SQLAlchemy Engine & Session Factory
│   ├── models/                   # SQLAlchemy Database Models
│   │   ├── user.py               # User Model
│   │   ├── profile.py            # Physical Profile Model
│   │   ├── exercise.py           # Biomechanical Exercise Model
│   │   ├── workout.py            # WorkoutPlan & WorkoutDay Models
│   │   ├── log.py                # LoggedSet & CardioLog Models
│   │   └── physique.py           # PhysiqueScan Model
│   ├── schemas/                  # Pydantic v2 Request/Response Schemas
│   ├── services/                 # Core Algorithmic Engines
│   │   ├── injury_shield.py      # Biomechanical Contraindication Engine
│   │   ├── gender_tuning.py      # Gender Physiological Tuning
│   │   ├── cardio_engine.py      # LISS & HIIT Protocol Engine
│   │   ├── workout_generator.py  # 4-Day Periodized Split Builder
│   │   ├── volume_calculator.py  # Tonnage Load & Fatigue Index
│   │   ├── ai_vision.py          # Gemini Flash Vision Analyzer
│   │   ├── ai_coach.py           # Contextual AI Coach
│   │   └── pdf_generator.py      # ReportLab PDF Dossier Builder
│   └── workers/
│       └── plateau_worker.py     # APScheduler Deload Worker
├── tests/                        # Automated Pytest Suite (25 Tests)
│   ├── test_auth.py
│   ├── test_profile.py
│   ├── test_injury_shield.py
│   ├── test_workout_generator.py
│   ├── test_volume_and_plateau.py
│   ├── test_physique_and_pdf.py
│   └── test_coach_api.py
├── uploads/                      # Uploaded Physique Check-in Photos
├── reports/                      # Generated PDF Coaching Dossiers
├── seed_data.py                  # Database Seeder (32 exercises + demo user)
├── run.py                        # Application Startup Script
├── requirements.txt              # Project Python Dependencies
└── README.md                     # Documentation
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.11+ installed.
- Git installed.

### 2. Setup & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Maazkorejo/FitMorph.git
cd FitMorph

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python seed_data.py
```
> Pre-seeds 32 biomechanically tagged exercises and creates a test athlete account:
> - **Email**: `demo@fitmorph.com`
> - **Password**: `demo1234`

### 4. Run the Application
```bash
python run.py
```
- Interactive Swagger API Documentation: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Health Check Status: **[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)**

---

## Running Automated Tests

FitMorph comes with a comprehensive automated test suite verifying all 6 capstone concepts:

```bash
pytest -v
```

**Results:**
```
tests/test_auth.py ......................... [PASSED]
tests/test_profile.py ...................... [PASSED]
tests/test_injury_shield.py ................ [PASSED]
tests/test_workout_generator.py ............ [PASSED]
tests/test_volume_and_plateau.py ........... [PASSED]
tests/test_physique_and_pdf.py ............. [PASSED]
tests/test_coach_api.py .................... [PASSED]

======================= 25 passed in 18.2s =======================
```

---

## Author & Academic Integrity
- **Author**: Muhammad Maaz
- **GitHub**: [Maazkorejo/FitMorph](https://github.com/Maazkorejo/FitMorph)
- **License**: MIT
