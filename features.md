# AI Exam Proctoring System – Features Overview

This document describes the complete feature set of the system.

---

# Authentication & Roles

- JWT-based authentication
- Role-based access control
- Admin and Candidate roles
- Secure token validation
- Swagger authorization support

---

# Admin Features

- Register admin
- Login and authorize
- Enroll candidate face
- Create exams
- Set exam duration
- Add subject-wise questions
- Define correct answers
- View exam sessions
- View violation records
- View candidate scores
- Publish results (future enhancement)

---

# Candidate Features

- Secure login
- Face verification before exam
- Session validation
- Countdown timer based on exam duration
- Subject-wise navigation
- Question tracking (color-coded)
- Review later option
- Answer persistence
- Automatic submission on timeout
- Secure Electron desktop environment

---

# AI Monitoring Features

## Face Detection (MediaPipe)

- Detects presence of face
- Logs "no_face" violation
- Saves evidence image

## Face Verification (InsightFace)

- Embedding generation
- Cosine similarity comparison
- Identity verification logging

## Mobile Phone Detection (YOLOv8)

- Real-time object detection
- Detects "cell phone"
- High severity violation
- Immediate termination

---

# Violation System

- Low severity → warning count increment
- Medium severity → warning increment
- High severity → immediate termination
- 3 warnings → automatic termination
- Evidence image saved
- Violation stored in database
- Termination reason returned to frontend

---

# Smart Exam UI

- 75% / 25% layout split
- Left side:
  - Timer
  - Subject heading
  - Question
  - MCQ options (A, B, C, D)
- Right side:
  - Live camera feed
  - Question legend
  - Question navigation block
  - Next button
  - Submit button

---

# Question Legend

Color coding:

- Green → Answered
- Blue → Marked for review
- Red → Seen but not answered
- No color → Not visited

---

# Backend Data Tracking

- Exam sessions
- Warning count
- Termination reason
- Candidate answers
- Score (hidden from candidate)
- Submission timestamp
- Identity verification history
- Violation evidence paths

---

# Dockerized Microservices

- Backend container
- AI container
- PostgreSQL container
- Networked via Docker
- Environment isolated

---

# Electron Security

- Desktop-only environment
- Disabled right-click
- Disabled developer tools
- Controlled navigation
- Secure token storage

---

# Scalability Ready

- Microservice architecture
- REST-based API design
- AI service separated
- Database-driven exam logic
- Extensible violation engine

---

# Future Enhancements (Planned)

- Tab-switch detection
- Audio monitoring
- Multi-face detection
- Result publishing panel
- Admin dashboard UI
- Cloud deployment
- Real-time WebSocket streaming
- Advanced analytics

---

This system demonstrates a full-stack AI-powered secure remote examination platform.