from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from auth import get_current_user
import requests
import json
import numpy as np
import schemas

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================
#  Get All Sessions
# ======================
@router.get("/sessions")
def get_all_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sessions = db.query(models.ExamSession).all()

    result = []
    for s in sessions:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()

        result.append({
            "session_id": s.id,
            "candidate_email": user.email if user else None,
            "status": s.status,
            "warnings": s.warning_count,
            "started_at": s.started_at,
            "ended_at": s.ended_at
        })

    return result


# ==========================================
# Get Only Active Sessions
# ==========================================
@router.get("/sessions/active")
def get_active_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sessions = db.query(models.ExamSession).filter(
        models.ExamSession.status == "active"
    ).all()

    result = []
    for s in sessions:
        result.append({
            "session_id": s.id,
            "user_id": s.user_id,
            "exam_id": s.exam_id,
            "started_at": s.started_at
        })

    return result


# ==========================================
# Get Violations for a Session
# ==========================================
@router.get("/sessions/{session_id}/violations")
def get_session_violations(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    violations = db.query(models.Violation).filter(
        models.Violation.session_id == session_id
    ).all()

    result = []
    for v in violations:
        result.append({
            "type": v.type,
            "severity": v.severity,
            "confidence": v.confidence,
            "evidence_url": f"http://localhost:8000/{v.evidence_url}" if v.evidence_url else None,
            "timestamp": v.timestamp
        })

    return result


# ==========================================
# Enroll Candidate Face (Admin Only)
# ==========================================
@router.post("/enroll-candidate-face/{candidate_id}")
async def enroll_candidate_face(
    candidate_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    candidate = db.query(models.User).filter(
        models.User.id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    contents = await file.read()

    # Send image to AI service
    response = requests.post(
        "http://ai-service:8001/generate-embedding",
        files={"file": contents}
    )

    if response.status_code != 200:
        raise HTTPException(400, "Face detection failed")

    embedding = response.json().get("embedding")

    if not embedding:
        raise HTTPException(400, "No face detected")

    # Store embedding
    candidate.face_embedding = json.dumps(embedding)
    candidate.face_enrolled = True

    db.commit()

    return {"message": "Face enrolled successfully"}

# =====================
# Admin Questions
# ============================

@router.post("/exams/{exam_id}/add-question")
def add_question(
    exam_id: int,
    question: schemas.QuestionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    new_question = models.Question(
        exam_id=exam_id,
        subject=question.subject,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_option=question.correct_option
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return {"message": "Question added"}