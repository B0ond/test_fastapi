from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"))
    clinic = relationship("Clinic", back_populates="doctors", lazy="selectin")
    patients = relationship("Patient", back_populates="doctor", lazy="selectin", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor", lazy="selectin", cascade="all, delete-orphan")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)
    doctor = relationship("Doctor", back_populates="patients", lazy="selectin")
    clinic = relationship("Clinic", back_populates="patients", lazy="selectin")
    appointments = relationship("Appointment", back_populates="patient", lazy="selectin", cascade="all, delete-orphan")
    appointment_time = Column(DateTime)

class Clinic(Base):
    __tablename__ = "clinics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    doctors = relationship("Doctor", back_populates="clinic", lazy="selectin", cascade="all, delete-orphan")
    patients = relationship("Patient", back_populates="clinic", lazy="selectin", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date = Column(DateTime)
    doctor = relationship("Doctor", back_populates="appointments", lazy="selectin")
    patient = relationship("Patient", back_populates="appointments", lazy="selectin")