from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/exams", tags=["Exams"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.ExamOut)
def create_exam(
    exam: schemas.ExamCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create exams")

    new_exam = models.Exam(
        title=exam.title,
        duration_minutes=exam.duration_minutes,
        created_by=1  # temporarily hardcoded
    )

    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    return new_exam


@router.get("/", response_model=list[schemas.ExamOut])
def list_exams(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exams = db.query(models.Exam).all()
    return exams


# Get all questions for exam
@router.get("/{exam_id}/questions")
def get_questions(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    exam = db.query(models.Exam).filter(
        models.Exam.id == exam_id
    ).first()

    questions = db.query(models.Question).filter(
        models.Question.exam_id == exam_id
    ).all()

    return {
        "duration": exam.duration_minutes,
        "questions": questions
    }


# Submit answers
@router.post("/{session_id}/submit")
def submit_exam(
    session_id: int,
    answers: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.query(models.ExamSession).filter(
        models.ExamSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(404, "Session not found")

    questions = db.query(models.Question).filter(
        models.Question.exam_id == session.exam_id
    ).all()

    score = 0
    total = len(questions)

    for q in questions:
        if str(q.id) in answers:
            if answers[str(q.id)] == q.correct_option:
                score += 1

    session.status = "completed"
    session.score = score
    session.total_questions = total
    session.submitted_at = datetime.utcnow()

    db.commit()

    return {"message": "Submission successful"}