from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Doctor(Base):
    __tablename__ = "doctor"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    specialization = Column(String, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinic.id"))
    clinic = relationship("Clinic", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")