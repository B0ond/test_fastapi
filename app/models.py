from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    patients = relationship("Patien", back_populates="doctor")
    appointment_times = relationship("Patien", back_populates="doctor",
                                      primaryjoin="Doctor.id==Patien.doctor_id")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    doctor = relationship("Doctor", back_populates="patients")
    appointment_time = Column(DateTime)


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)

    doctors = relationship("Doctor", back_populates="clinic")
    patients = relationship("Patien", back_populates="clinic")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date = Column(String)

    doctor = relationship("Doctor")
    patient = relationship("Patient")