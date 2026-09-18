from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from app.database.database import get_db
from app.models.models import Student, Dataset

router = APIRouter()
REPORTS_DIR = "reports"

@router.get("/{dataset_id}/export/csv")
def export_csv(dataset_id: int, risk_level: str = None, class_name: str = None, db: Session = Depends(get_db)):
    query = db.query(Student).filter(Student.dataset_id == dataset_id)
    if risk_level:
        query = query.filter(Student.risk_level == risk_level)
    if class_name:
        query = query.filter(Student.class_name == class_name)
        
    students = query.all()
    if not students:
        raise HTTPException(status_code=404, detail="No students found for export")
        
    data = []
    for s in students:
        row = {
            "Student ID": s.student_record_id,
            "Name": s.name,
            "Class": s.class_name,
            "Attendance": s.attendance,
            "Average Score": s.average_score,
            "Risk Probability": s.risk_probability,
            "Risk Level": s.risk_level,
            "Why Flagged": s.why_flagged,
            "Review Status": s.review_status
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    filepath = os.path.join(REPORTS_DIR, f"export_dataset_{dataset_id}.csv")
    df.to_csv(filepath, index=False)
    
    return FileResponse(path=filepath, filename=f"students_risk_report.csv", media_type='text/csv')

@router.get("/{dataset_id}/export/pdf")
def export_pdf(dataset_id: int, risk_level: str = None, class_name: str = None, db: Session = Depends(get_db)):
    query = db.query(Student).filter(Student.dataset_id == dataset_id)
    if risk_level:
        query = query.filter(Student.risk_level == risk_level)
    if class_name:
        query = query.filter(Student.class_name == class_name)
        
    students = query.all()
    if not students:
        raise HTTPException(status_code=404, detail="No students found for export")
        
    filepath = os.path.join(REPORTS_DIR, f"export_dataset_{dataset_id}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph("Student Academic Risk Report", styles['Title'])
    elements.append(title)
    
    data = [["ID", "Name", "Class", "Att %", "Avg Score", "Risk", "Flagged Reason"]]
    for s in students:
        data.append([
            s.student_record_id or "-",
            s.name or "-",
            s.class_name or "-",
            f"{s.attendance:.1f}" if s.attendance else "-",
            f"{s.average_score:.1f}" if s.average_score else "-",
            s.risk_level.upper() if s.risk_level else "-",
            s.why_flagged or "-"
        ])
        
    table = Table(data, colWidths=[60, 100, 60, 50, 60, 50, 140])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A3B32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return FileResponse(path=filepath, filename=f"students_risk_report.pdf", media_type='application/pdf')
