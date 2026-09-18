from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Note Schemas
class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Intervention Schemas
class InterventionBase(BaseModel):
    intervention_type: str
    status: Optional[str] = "active"

class InterventionCreate(InterventionBase):
    pass

class Intervention(InterventionBase):
    id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Student Schemas
class StudentBase(BaseModel):
    student_record_id: Optional[str]
    name: Optional[str]
    class_name: Optional[str]
    attendance: Optional[float]
    average_score: Optional[float]
    risk_probability: Optional[float]
    risk_level: Optional[str]
    why_flagged: Optional[str]
    review_status: Optional[str]
    raw_data: Optional[Dict[str, Any]]

class Student(StudentBase):
    id: int
    dataset_id: int
    notes: List[Note] = []
    interventions: List[Intervention] = []

    class Config:
        from_attributes = True

# Dataset Schemas
class DatasetBase(BaseModel):
    filename: str

class Dataset(DatasetBase):
    id: int
    uploaded_at: datetime
    status: str
    metrics: Optional[Dict[str, Any]]
    feature_mapping: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

# Data Quality Report
class DataQualityReport(BaseModel):
    total_rows: int
    columns_detected: List[str]
    missing_values: Dict[str, int]
    duplicate_rows: int
    duplicate_student_ids: int
    invalid_attendance_count: int
    invalid_marks_count: int
