from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import pandas as pd
import os
import json
from app.database.database import get_db
from app.models.models import Dataset, Student
from app.services.data_cleaner import clean_dataset
from app.services.ml_service import engineer_features, train_and_select_model, predict_risk

router = APIRouter()

RAW_DIR = "data/raw"
CLEANED_DIR = "data/cleaned"

@router.post("/{dataset_id}/clean")
def clean_and_prepare_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    raw_path = os.path.join(RAW_DIR, dataset.filename)
    if not os.path.exists(raw_path):
        raise HTTPException(status_code=404, detail="Raw file missing")
        
    try:
        df = pd.read_csv(raw_path) if raw_path.endswith('.csv') else pd.read_excel(raw_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Clean Data
    df_clean = clean_dataset(df)
    
    # Engineer Features
    df_engineered = engineer_features(df_clean)
    
    # Save Cleaned Data
    cleaned_path = os.path.join(CLEANED_DIR, dataset.filename.replace('.xlsx', '.csv').replace('.xls', '.csv'))
    df_engineered.to_csv(cleaned_path, index=False)
    
    dataset.status = "cleaned"
    db.commit()
    
    return {"message": "Dataset cleaned and features engineered", "cleaned_file": cleaned_path}

@router.post("/{dataset_id}/train")
def train_model_endpoint(dataset_id: int, target_col: str = Body(..., embed=True), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.status == "uploaded":
        raise HTTPException(status_code=400, detail="Dataset must be cleaned first")
        
    # Assume CSV saved from cleaning step
    cleaned_path = os.path.join(CLEANED_DIR, dataset.filename.replace('.xlsx', '.csv').replace('.xls', '.csv'))
    df = pd.read_csv(cleaned_path)
    
    try:
        best_model_name, all_metrics, model_path = train_and_select_model(df, target_col, dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    dataset.model_path = model_path
    dataset.metrics = all_metrics
    dataset.status = "trained"
    db.commit()
    
    return {
        "best_model": best_model_name,
        "metrics": all_metrics
    }

@router.post("/{dataset_id}/predict")
def generate_predictions(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset or not dataset.model_path:
        raise HTTPException(status_code=400, detail="Model not trained for this dataset")
        
    cleaned_path = os.path.join(CLEANED_DIR, dataset.filename.replace('.xlsx', '.csv').replace('.xls', '.csv'))
    df = pd.read_csv(cleaned_path)
    
    # Drop rows that are in db already to avoid duplication, or delete old ones
    db.query(Student).filter(Student.dataset_id == dataset_id).delete()
    
    predictions = predict_risk(df, dataset.model_path)
    
    for i, row in df.iterrows():
        pred = predictions[i]
        
        student_id_val = str(row.get('student_id', f'unknown_{i}'))
        name = str(row.get('name', 'Unknown'))
        class_name = str(row.get('class', 'Unknown'))
        attendance = float(row.get('attendance', 0.0))
        avg_score = float(row.get('average_score', 0.0))
        
        student = Student(
            dataset_id=dataset_id,
            student_record_id=student_id_val,
            name=name,
            class_name=class_name,
            attendance=attendance,
            average_score=avg_score,
            risk_probability=pred['risk_probability'],
            risk_level=pred['risk_level'],
            why_flagged=pred['why_flagged'],
            raw_data=row.to_dict()
        )
        db.add(student)
        
    db.commit()
    
    return {"message": f"Generated predictions for {len(df)} students and saved to database."}
