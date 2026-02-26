from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine
from models import Base
from routers import user
from routers import exam
from routers import session
from routers import admin

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/evidence", StaticFiles(directory="evidence"), name="evidence")

app.include_router(user.router)
app.include_router(exam.router)
app.include_router(session.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "AI Remote Proctoring Backend Running"}
