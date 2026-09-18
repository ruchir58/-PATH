from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import datetime
from app.database.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="uploaded") # uploaded, cleaned, trained
    model_path = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True) # To store model metrics
    feature_mapping = Column(JSON, nullable=True) # To store detected column mappings

    students = relationship("Student", back_populates="dataset", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    student_record_id = Column(String, index=True) # Original ID from CSV
    name = Column(String, nullable=True)
    class_name = Column(String, nullable=True)
    attendance = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    
    risk_probability = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True) # low, medium, high
    why_flagged = Column(Text, nullable=True) # Reason string
    
    review_status = Column(String, default="pending") # pending, reviewed
    
    raw_data = Column(JSON, nullable=True) # Store all original columns dynamically

    dataset = relationship("Dataset", back_populates="students")
    notes = relationship("Note", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="notes")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    intervention_type = Column(String)
    status = Column(String, default="active") # active, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="interventions")
