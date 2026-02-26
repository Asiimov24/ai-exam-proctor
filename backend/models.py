from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # admin or candidate

    face_embedding = Column(JSON, nullable=True)
    face_enrolled = Column(Boolean, default=False)


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    duration_minutes = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id"))

class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    status = Column(String, default="active")  # active, terminated, completed
    warning_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    submitted_at = Column(DateTime, nullable=True)

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    type = Column(String)
    severity = Column(String)  # LOW, MEDIUM, HIGH
    evidence_url = Column(String, nullable=True)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class FaceTemplate(Base):
    __tablename__ = "face_templates"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    embedding = Column(String)  # store JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class IdentityVerificationLog(Base):
    __tablename__ = "identity_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer)
    similarity_score = Column(Float)
    success = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    subject = Column(String)
    question_text = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_option = Column(String)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_option = Column(String)