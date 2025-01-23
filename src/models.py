from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from database import Base

class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)

class Choises(Base):
    __tablename__ = 'choises'

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String, index=True)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey('questions.id'))