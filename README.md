# FitMorph — Adaptive Fitness Intelligence & Physique Progression Engine

A production-grade, AI-powered fitness web application and adaptive workout recommendation engine that tailors training protocols for **Fat Loss, Hypertrophy, and Strength**, customizes volume for **Male vs. Female physiology**, enforces an **Injury Prevention Shield** with joint-safe substitutions, supports **Gym, Dumbbells, and Zero-Equipment** workouts, scans physique photos for **muscular symmetry**, and outputs printable **4-Week Coaching Dossier PDFs**.

---

## 🏛 The 10x Claim

> *"Designing a fully personalized 4-week periodized workout plan with joint-safe exercise substitutions, gender-tailored recovery, and visual physique symmetry analysis used to require hours of manual research or a $200/month personal trainer; now FitMorph dynamically generates an adaptive, injury-vetted training routine, audits weekly plateaus, and delivers a printable Coaching Dossier PDF in under 10 seconds."*

---

## 🛠 Core Features

1. **User Authentication & Private Profiles:**
   - Secure signup & login with bcrypt password hashing and JWT Bearer tokens.
   - Individual progress, workout history, and photo scans are private and persistent.
2. **Dynamic Biomechanical Workout Generator:**
   - Adapts to goals: **Fat Loss**, **Hypertrophy (Muscle Building)**, or **Strength**.
   - Tuned for **Male vs. Female** metabolic recovery and physiological volume limits.
   - Dynamic equipment support: **Full Gym**, **Dumbbells Only**, or **Zero Equipment / Bodyweight**.
3. **Injury Prevention Shield & Safe Substitutions:**
   - Trainees can flag pains (lower back, shoulders, knees, wrists).
   - System automatically bans contraindicated movements and substitutes joint-safe alternatives.
4. **Cardio & Metabolic Conditioning Protocols:**
   - Prescribes Zone 2 Low-Intensity Steady State (LISS) or High-Intensity Interval Training (HIIT) based on goals and bodyweight.
5. **AI Vision Physique & Symmetry Scanner:**
   - Powered by Gemini Flash Vision. Upload physique check-ins to detect muscle imbalances, posture flags, and lagging muscle groups.
   - Injects targeted accessory volume to correct identified weak points.
6. **Monthly Progress Comparison:**
   - Compares Month 1 vs. Month 2 physique scans with visual progression notes.
7. **Automated Weekly Plateau Detection:**
   - Background worker audits weekly volume load ($Sets \times Reps \times Weight$). Automatically flags plateaus and schedules deload weeks.
8. **Printable 4-Week Coaching Blueprint (PDF):**
   - 1-click export of an executive training dossier with routine tables and progression targets.

---

## 📋 The 6 Program Concepts Implemented

| # | Concept | Where It Lives |
|---|---|---|
| 1 | **API Endpoints** | `app/api/` (FastAPI routes for auth, profile, workouts, physique, reports) |
| 2 | **Database** | `app/db/` (SQLAlchemy models for Users, Profiles, Exercises, Plans, Scans) |
| 3 | **Authentication** | `app/core/auth.py` (JWT Bearer tokens & password encryption) |
| 4 | **Background Jobs / Cron** | `app/workers/plateau_worker.py` (APScheduler volume & fatigue audit) |
| 5 | **Reporting — PDF** | `app/services/pdf_generator.py` (ReportLab printable 4-week blueprint) |
| 6 | **LLM / Vision AI** | `app/services/ai_vision.py` & `ai_coach.py` (Gemini Flash Vision) |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Free Gemini API Key (from [Google AI Studio](https://aistudio.google.com/) — $0, no credit card required)

### 2. Setup Environment
```bash
# Clone and navigate
cd FitMorph

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
```bash
cp .env.example .env
```
Edit `.env` and set your `SECRET_KEY` and `GEMINI_API_KEY`.

### 4. Seed Database & Run App
```bash
python seed_data.py
uvicorn main:app --reload --port 8000
```
Open `http://localhost:8000` to launch the FitMorph Web App!
