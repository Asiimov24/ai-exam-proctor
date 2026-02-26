from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas
import auth
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import numpy as np
import json
import requests

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}



@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({
        "sub": db_user.email,
        "role": db_user.role
    })

    return {"access_token": token, "token_type": "bearer"}


@router.post("/verify-face/{exam_id}")
async def verify_face(
    exam_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates allowed")

    user = db.query(models.User).filter(
        models.User.email == current_user["email"]
    ).first()

    if not user.face_enrolled or not user.face_embedding:
        raise HTTPException(status_code=400, detail="No enrolled face found")

    contents = await file.read()

    response = requests.post(
        "http://ai-service:8001/generate-embedding",
        files={"file": ("image.jpg", contents, "image/jpeg")}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI service error")

    live_embedding = response.json().get("embedding")

    if not live_embedding:
        raise HTTPException(status_code=400, detail="No face detected")

    stored_embedding = np.array(json.loads(user.face_embedding))
    live_embedding = np.array(live_embedding)

    similarity = np.dot(stored_embedding, live_embedding) / (
        np.linalg.norm(stored_embedding) * np.linalg.norm(live_embedding)
    )

    success = similarity >= 0.6

    log = models.IdentityVerificationLog(
        user_id=user.id,
        exam_id=exam_id,
        similarity_score=float(similarity),
        success=success
    )

    db.add(log)
    db.commit()

    if not success:
        raise HTTPException(status_code=403, detail="Face verification failed")

    return {
        "message": "Face verified",
        "similarity": float(similarity)
    }
