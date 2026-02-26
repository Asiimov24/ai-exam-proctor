# 🚀 AI Exam Proctoring System – Complete Execution Guide

This document explains how to run the full system from scratch.

The system consists of:

- FastAPI Backend
- AI Service (Face + Mobile Detection)
- PostgreSQL Database
- Electron Desktop Exam Client
- Docker-based architecture

---

# STEP 1 — Start All Services (Backend + AI + Database)

Open Terminal 1.

Navigate to the project root:
Run:
cd ai-exam-proctor
Run:
docker compose up --build


Wait until:

- PostgreSQL is ready
- Backend is running on port 8000
- AI service is running on port 8001

Do NOT close this terminal.

System URLs:

- Backend Swagger: http://localhost:8000/docs#/
- AI Service: http://localhost:8001

---

# STEP 2 — Setup Exam (Admin Configuration)

Open browser:
http://localhost:8000/docs#/

---
## 2.1 Register Users

Register:

- One Admin
- One Candidate

Use:
POST/users/register

---
## 2.2 Login as Admin

Click 🔒 Authorize (top-right in Swagger)
Type down mail and password and login

---
## 2.3 Find Candidate ID

Open Terminal 2.

Run:
docker exec -it arp_postgres psql -U arp_user -d arp_db
Run:
SELECT id, name, email FROM users;

Note the candidate ID.

Run (Exit):
\q

---
## 2.4 Enroll Candidate Face

In Swagger:
POST /admin/enroll-candidate-face/{candidate_id}

Upload candidate face image.

You should receive:
Face enrolled successfully

---
## 2.5 Create Exam

Use:
POST /exams/

Provide:

- title
- duration_minutes

Note the returned exam_id.

---
## 2.6 Add Questions (Subject-wise)

Use:
POST /admin/exams/{exam_id}/add-question

Add questions

# STEP 3 — Start Electron Exam Client

Open Terminal 3.

Navigate to:

Run:
cd electron_app
Run:
npm start


Electron exam client will open.

---

# Candidate Exam Flow

1. Login as Candidate
2. Enter Exam ID
3. Perform Face Verification
4. Exam Session starts automatically
5. Countdown timer begins
6. Questions load subject-wise
7. Live camera monitoring starts
8. Violations auto-detected
9. Exam auto-terminates if:
   - 3 warnings
   - High severity violation (mobile phone)
   - Time expires
10. Submission stored in backend database

---

# Violation Logic

LOW or MEDIUM severity:
- Increments warning count

HIGH severity:
- Immediate termination

Maximum allowed warnings:
- 3

After termination:
- Monitoring stops
- Popup shows reason
- Submission recorded

---

# Data Stored in Database

- Exam Sessions
- Violations
- Identity Verification Logs
- Candidate Answers
- Score (hidden from candidate)

---

# Important Notes

- Keep Docker running
- Do not close Terminal 1
- Allow camera permissions
- Ensure ports 8000 and 8001 are free
- If models are downloading, wait

---

# System Architecture Ports

| Service       | Port |
|--------------|------|
| Backend       | 8000 |
| AI Service    | 8001 |
| PostgreSQL    | 5432 |

---

System is now fully operational.