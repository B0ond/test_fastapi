from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependecy = Annotated[Session, Depends(get_db)]

@app.post("/questions/")
async def create_question(question: QuestionBase, db:db_dependecy):
    db_qsession = models.Questions(question_text=question.question_text)
    db.add(db_qsession)
    db.commit()
    db.refresh(db_qsession)
    for choice in question.choices:
        db_choice = models.Choises(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_qsession.id)