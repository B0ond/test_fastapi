from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base

class Clinic(Base):
    __tablename__ = "clinic"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    doctors = relationship("Doctor", back_populates="clinic")
    Appointment = relationship("Appointment", back_populates="clinic")
    Doctor = relationship("Doctor", back_populates="clinic")


class Doctor(Base):
    __tablename__ = "doctor"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    specialization = Column(String, nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinic.id"))
    clinic = relationship("Clinic", back_populates="doctors")
    Appointment = relationship("Appointment", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patient"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    appointments = relationship("Appointment", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient.id"))
    doctor_id = Column(Integer, ForeignKey("doctor.id"))
    clinic_id = Column(Integer, ForeignKey("clinic.id"))
    datetime = Column(DateTime, nullable=False)
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    clinic = relationship("Clinic", back_populates="appointments")
    