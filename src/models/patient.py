from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base

class Patient(Base):
    __tablename__ = "patient"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    appointments = relationship("Appointment", back_populates="patient")