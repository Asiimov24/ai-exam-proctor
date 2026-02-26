from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from auth import get_current_user
from datetime import datetime
from fastapi import Query 


router = APIRouter(prefix="/sessions", tags=["Sessions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# START EXAM (WITH FACE VERIFICATION CHECK)
# =====================================================
@router.post("/start/{exam_id}")
def start_exam(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can start exams")

    user = db.query(models.User).filter(
        models.User.email == current_user["email"]
    ).first()

    # Check latest verification
    verification = db.query(models.IdentityVerificationLog).filter(
        models.IdentityVerificationLog.user_id == user.id,
        models.IdentityVerificationLog.exam_id == exam_id
    ).order_by(models.IdentityVerificationLog.timestamp.desc()).first()

    if not verification or verification.success is not True:
        raise HTTPException(
            status_code=403,
            detail="Face verification required before starting exam"
        )

    # Create session
    new_session = models.ExamSession(
        user_id=user.id,
        exam_id=exam_id,
        status="active"
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "session_id": new_session.id,
        "status": "exam started"
    }

# =====================================================
# TERMINATE EXAM
# =====================================================
@router.post("/terminate/{session_id}")
def terminate_exam(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(models.ExamSession).filter(
        models.ExamSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "terminated"
    session.ended_at = datetime.utcnow()

    db.commit()

    return {"message": "Exam terminated"}


# =====================================================
# REPORT VIOLATION (WITH HARD STOP)
# =====================================================
@router.post("/violation/{session_id}")
def report_violation(
    session_id: int,
    violation_type: str = Query(...),
    severity: str = Query(...),
    confidence: float = Query(...),
    evidence_url: str = Query(None),
    db: Session = Depends(get_db)
):
    session = db.query(models.ExamSession).filter(
        models.ExamSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # HARD STOP — if already terminated, do nothing
    if session.status == "terminated":
        return {
            "warnings": session.warning_count,
            "status": "terminated"
        }

    # Save violation
    violation = models.Violation(
        session_id=session_id,
        type=violation_type,
        severity=severity,
        confidence=confidence,   
        evidence_url=evidence_url,
        timestamp=datetime.utcnow()
    )

    db.add(violation)

    # Warning logic
    if severity in ["LOW", "MEDIUM"]:
        session.warning_count += 1

    termination_reason = None
    # Termination logic
    if severity == "HIGH" or session.warning_count >= 3:
        session.status = "terminated"
        session.ended_at = datetime.utcnow()
        termination_reason = violation_type

    db.commit()
    db.refresh(session)

    return {
        "warnings": session.warning_count,
        "status": session.status,
        "reason": violation_type if session.status == "terminated" else None
    }

@router.get("/validate/{session_id}")
def validate_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Candidate access only")

    user = db.query(models.User).filter(
        models.User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = db.query(models.ExamSession).filter(
        models.ExamSession.id == session_id,
        models.ExamSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=403, detail="Session not active")

    verification = db.query(models.IdentityVerificationLog).filter(
        models.IdentityVerificationLog.user_id == user.id,
        models.IdentityVerificationLog.exam_id == session.exam_id
    ).order_by(models.IdentityVerificationLog.timestamp.desc()).first()

    if not verification or verification.success is not True:
        raise HTTPException(status_code=403, detail="Face verification not completed")

    return {"valid": True}

@router.get("/questions/{exam_id}")
def get_questions(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    questions = db.query(models.Question).filter(
        models.Question.exam_id == exam_id
    ).all()

    return questions 
