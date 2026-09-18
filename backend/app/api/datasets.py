from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
import pandas as pd
from datetime import datetime
from app.database.database import get_db
from app.models.models import Dataset
from app.schemas import schemas
from typing import Dict, Any

router = APIRouter()

RAW_DIR = "data/raw"

@router.post("/upload", response_model=schemas.Dataset)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".csv", ".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail=f"Only CSV and Excel files are supported. Received: {file.filename}")

    # Save raw file
    file_path = os.path.join(RAW_DIR, file.filename)
    # Ensure unique filename to prevent overwrite
    base, ext = os.path.splitext(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{base}_{timestamp}{ext}"
    unique_file_path = os.path.join(RAW_DIR, unique_filename)

    with open(unique_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create dataset record
    db_dataset = Dataset(filename=unique_filename, status="uploaded")
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)

    return db_dataset

@router.get("/latest", response_model=schemas.Dataset)
def get_latest_dataset(db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.status == "trained").order_by(Dataset.id.desc()).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="No trained datasets found")
    return dataset

@router.get("/{dataset_id}/inspect", response_model=schemas.DataQualityReport)
def inspect_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = os.path.join(RAW_DIR, dataset.filename)
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    total_rows = len(df)
    columns_detected = df.columns.tolist()
    missing_values = df.isnull().sum().to_dict()
    duplicate_rows = int(df.duplicated().sum())
    
    # Simple heuristic to find student ID column
    student_id_col = None
    for col in columns_detected:
        if any(kw in col.lower() for kw in ['student_id', 'id', 'roll_no', 'enrollment_no']):
            student_id_col = col
            break
            
    duplicate_student_ids = 0
    if student_id_col:
        duplicate_student_ids = int(df.duplicated(subset=[student_id_col]).sum())
        
    # Heuristics for invalid attendance (assuming percentage > 100 or < 0)
    invalid_attendance = 0
    for col in columns_detected:
        if 'attendance' in col.lower():
            try:
                # Convert to numeric first, coerce errors to NaN
                att = pd.to_numeric(df[col], errors='coerce')
                invalid_attendance = int(((att > 100) | (att < 0)).sum())
            except:
                pass

    return {
        "total_rows": total_rows,
        "columns_detected": columns_detected,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "duplicate_student_ids": duplicate_student_ids,
        "invalid_attendance_count": invalid_attendance,
        "invalid_marks_count": 0 # To be implemented deeper during cleaning
    }
