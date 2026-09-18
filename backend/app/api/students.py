from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import copy
import pandas as pd
from app.database.database import get_db
from app.models.models import Student, Dataset, Note, Intervention
from app.schemas import schemas
from app.services.ml_service import predict_risk
import os

router = APIRouter()
CLEANED_DIR = "data/cleaned"

@router.get("/", response_model=dict)
def get_students(
    dataset_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "risk_probability",
    sort_desc: bool = True,
    search: str = None,
    risk_level: str = None,
    class_name: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Student).filter(Student.dataset_id == dataset_id)
    
    if search:
        query = query.filter(Student.name.ilike(f"%{search}%") | Student.student_record_id.ilike(f"%{search}%"))
    if risk_level:
        query = query.filter(Student.risk_level == risk_level)
    if class_name:
        query = query.filter(Student.class_name == class_name)
        
    total = query.count()
    
    sort_column = getattr(Student, sort_by, Student.risk_probability)
    if sort_desc:
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
        
    students = query.offset(skip).limit(limit).all()
    
    # We will return the dict to match a pagination structure or list
    return {
        "total": total,
        "items": [schemas.Student.from_orm(s) for s in students]
    }

@router.get("/{student_id}", response_model=schemas.Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/{student_id}/review")
def mark_reviewed(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.review_status = "reviewed"
    db.commit()
    return {"message": "Status updated to reviewed"}

@router.post("/{student_id}/notes", response_model=schemas.Note)
def add_note(student_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = Note(student_id=student_id, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.post("/{student_id}/interventions", response_model=schemas.Intervention)
def add_intervention(student_id: int, intervention: schemas.InterventionCreate, db: Session = Depends(get_db)):
    db_int = Intervention(student_id=student_id, intervention_type=intervention.intervention_type, status=intervention.status)
    db.add(db_int)
    db.commit()
    db.refresh(db_int)
    return db_int

@router.post("/{student_id}/what-if")
def what_if_analysis(student_id: int, overrides: dict = Body(...), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    dataset = db.query(Dataset).filter(Dataset.id == student.dataset_id).first()
    if not dataset or not dataset.model_path:
        raise HTTPException(status_code=400, detail="Model not found")
        
    # Apply feature engineering first
    from app.services.ml_service import engineer_features
    df_raw = pd.DataFrame([student.raw_data])
    
    # If average_score is overridden, we must also apply this to the underlying raw mark columns
    # because tree models often split on raw columns (like quiz_1) instead of the engineered average_score!
    if 'average_score' in overrides:
        val = float(overrides['average_score'])
        numeric_cols = df_raw.select_dtypes(include=['number']).columns
        marks_cols = [c for c in numeric_cols if any(kw in c for kw in ['quiz', 'assignment', 'lab', 'score', 'mark', 'prior', 'cgpa', 'gpa']) and c != 'average_score']
        for c in marks_cols:
            df_raw[c] = val
            
    df_engineered = engineer_features(df_raw)
    
    # Then apply overrides directly to engineered features
    for k, v in overrides.items():
        val = float(v) if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit() else v
        df_engineered[k] = val
        
    
    predictions = predict_risk(df_engineered, dataset.model_path)
    if not predictions:
        raise HTTPException(status_code=500, detail="Failed to predict")
        
    return {
        "original_risk_probability": student.risk_probability,
        "original_risk_level": student.risk_level,
        "new_risk_probability": predictions[0]["risk_probability"],
        "new_risk_level": predictions[0]["risk_level"],
        "simulated_features": overrides
    }
