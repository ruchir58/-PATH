# प्रगति-PATH: Student Academic Risk Early Warning System

A complete, polished, full-stack web application designed to help faculty identify students who may benefit from academic support. 

This is a decision-support tool focused on providing insights through machine learning (Logistic Regression, Decision Trees, Random Forests), utilizing data points such as attendance, assignment scores, quiz marks, and prior performance.

## Technology Stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Backend:** Python FastAPI, SQLite (SQLAlchemy)
- **Machine Learning:** Pandas, NumPy, scikit-learn, Joblib
- **Exporting:** ReportLab (PDF), Pandas (CSV)

## Project Structure

- `/frontend` - Next.js React application
- `/backend` - FastAPI Python application, containing ML services and data processors

## Quick Start Guide

### 1. Backend Setup

The backend handles the APIs, Data Cleaning, and Model Training pipelines.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# (or just: pip install fastapi uvicorn sqlalchemy pandas numpy scikit-learn joblib reportlab pydantic python-multipart)

# Generate Sample Datasets
python generate_sample.py

# Run the FastAPI server
uvicorn app.main:app --reload
```
The API documentation will be available at: http://localhost:8000/docs

### 2. Frontend Setup

The frontend provides the sleek and calming UI for the faculty.

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The application will be available at: http://localhost:3000

## How to Test

1. Open http://localhost:3000 and it will redirect to the Dashboard.
2. Go to **Upload Data** in the sidebar.
3. Upload the `backend/sample_students_messy.csv` file.
4. Review the Data Quality Report (Notice the missing values, duplicates, and invalid attendance).
5. Select `At Risk` as the Target Column and click **Clean & Train Model**.
6. The backend will clean the messy data (handle outliers, impute missing values), dynamically engineer features, evaluate 3 models, and select the best one.
7. Go to **Students** to view the directory. Filter and sort students by Risk Level.
8. Click **View Profile** to open a student's profile, check why they were flagged, and run a **What-If Analysis** by simulating higher attendance or scores.
9. Export data via CSV or PDF from the Students page.
10. Check **Class Analytics** to compare risk across subjects or class groups.

## Design Philosophy

The application uses a soft, calm, and trustworthy academic theme:
- **Primary:** Coffee brown
- **Secondary:** Terracotta brown
- **Background:** Beige
- **Accent:** Light oak wood
- **Risk Colors:** Accessible muted tones (Soft green, amber, terracotta)

No harsh labels or deterministic "failing" language is used. Predictions are strictly framed as recommendations for faculty review.
