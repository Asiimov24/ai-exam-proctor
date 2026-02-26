from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import mediapipe as mp
import requests
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from insightface.app import FaceAnalysis
import json
from ultralytics import YOLO

os.makedirs("evidence", exist_ok=True)

phone_model= YOLO("yolov8n.pt")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0)

BACKEND_URL = "http://backend:8000"


@app.post("/analyze/{session_id}")
async def analyze_frame(session_id: int, file: UploadFile = File(...)):
    contents = await file.read()

    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"evidence/session_{session_id}_{timestamp}.jpg"

    # ---------------
    #  Face Detection
    # -----------------
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_frame)

    if not results.detections:
        cv2.imwrite(filename, frame)

        response = requests.post(
            f"{BACKEND_URL}/sessions/violation/{session_id}",
            params={
                "violation_type": "no_face",
                "severity": "LOW",
                "confidence": 0.9,
                "evidence_url": filename
            }
        )

        return {
            "violation": True,
            "backend": response.json()
        }

    # --------------
    #  Mobile Phone Detection
    # -------------------------
    phone_results = phone_model(frame)

    for r in phone_results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            label = phone_model.names[class_id]

            if label == "cell phone":
                cv2.imwrite(filename, frame)

                response = requests.post(
                    f"{BACKEND_URL}/sessions/violation/{session_id}",
                    params={
                        "violation_type": "mobile_phone_detected",
                        "severity": "HIGH",
                        "confidence": 0.95,
                        "evidence_url": filename
                    }
                )

                return {
                    "violation": True,
                    "backend": response.json()
                }

    # -------------------------
    # 3️⃣ No Violation
    # -------------------------
    return {"violation": False}

@app.post("/generate-embedding")
async def generate_embedding(file: UploadFile = File(...)):
    contents = await file.read()

    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    faces = face_app.get(img)

    if not faces:
        return {"error": "No face detected"}

    embedding = faces[0].embedding.tolist()

    return {"embedding": embedding}