from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.models import Student, Dataset

router = APIRouter()

@router.get("/{dataset_id}/dashboard-summary")
def get_dashboard_summary(dataset_id: int, db: Session = Depends(get_db)):
    # Verify dataset exists
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    total_students = db.query(Student).filter(Student.dataset_id == dataset_id).count()
    if total_students == 0:
        return {"total_students": 0}

    low_risk = db.query(Student).filter(Student.dataset_id == dataset_id, Student.risk_level == "low").count()
    medium_risk = db.query(Student).filter(Student.dataset_id == dataset_id, Student.risk_level == "medium").count()
    high_risk = db.query(Student).filter(Student.dataset_id == dataset_id, Student.risk_level == "high").count()

    avg_attendance = db.query(func.avg(Student.attendance)).filter(Student.dataset_id == dataset_id).scalar() or 0
    avg_performance = db.query(func.avg(Student.average_score)).filter(Student.dataset_id == dataset_id).scalar() or 0

    return {
        "total_students": total_students,
        "risk_distribution": {
            "low": low_risk,
            "medium": medium_risk,
            "high": high_risk
        },
        "average_attendance": round(avg_attendance, 2),
        "average_performance": round(avg_performance, 2),
        "model_used": dataset.model_path.split("/")[-1] if dataset.model_path else "None",
        "top_metrics": dataset.metrics.get(dataset.model_path.split("/")[-1].split("_")[0], {}) if dataset.metrics else {}
    }

@router.get("/{dataset_id}/class-analytics")
def get_class_analytics(dataset_id: int, db: Session = Depends(get_db)):
    # Group by class_name
    classes = db.query(Student.class_name, 
                       func.count(Student.id).label("count"),
                       func.avg(Student.attendance).label("avg_attendance"),
                       func.avg(Student.average_score).label("avg_score")
                       ).filter(Student.dataset_id == dataset_id).group_by(Student.class_name).all()

    class_stats = []
    for c in classes:
        # Get risk distribution per class
        low = db.query(Student).filter(Student.dataset_id == dataset_id, Student.class_name == c.class_name, Student.risk_level == "low").count()
        med = db.query(Student).filter(Student.dataset_id == dataset_id, Student.class_name == c.class_name, Student.risk_level == "medium").count()
        high = db.query(Student).filter(Student.dataset_id == dataset_id, Student.class_name == c.class_name, Student.risk_level == "high").count()

        class_stats.append({
            "class_name": c.class_name,
            "student_count": c.count,
            "average_attendance": round(c.avg_attendance or 0, 2),
            "average_score": round(c.avg_score or 0, 2),
            "risk_distribution": {"low": low, "medium": med, "high": high}
        })

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    return {
        "class_statistics": class_stats,
        "feature_importance": dataset.feature_mapping if dataset else {} # Dummy mapping placeholder, can be enhanced
    }
