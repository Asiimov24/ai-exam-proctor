from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class ExamCreate(BaseModel):
    title: str
    duration_minutes: int


class ExamOut(BaseModel):
    id: int
    title: str
    duration_minutes: int

    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    subject: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str