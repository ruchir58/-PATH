import pandas as pd
import numpy as np

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Trim whitespace from string columns and standardize headers
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Standardize common names if they differ slightly
    col_mapping = {}
    for col in df.columns:
        if any(kw in col for kw in ['student_id', 'id', 'roll_no', 'enrollment_no']):
            col_mapping[col] = 'student_id'
        elif any(kw in col for kw in ['attendance', 'attendance_percent', 'attendance_rate']):
            col_mapping[col] = 'attendance'
    df = df.rename(columns=col_mapping)
    
    # 2. Convert percentage strings to numeric values (e.g. "85%" -> 85.0)
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].astype(str).str.contains('%').any():
                df[col] = df[col].astype(str).str.replace('%', '').astype(float)
    
    # 3. Handle invalid numeric values and detect out-of-range
    if 'attendance' in df.columns:
        df['attendance'] = pd.to_numeric(df['attendance'], errors='coerce')
        # Cap at 100, floor at 0
        df['attendance'] = np.where(df['attendance'] > 100, 100, df['attendance'])
        df['attendance'] = np.where(df['attendance'] < 0, 0, df['attendance'])
        
    # Handle missing numeric values with median imputation
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    # Handle missing categorical values with mode imputation
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna("Unknown")
                
    # 4. Remove duplicate rows completely identical
    df = df.drop_duplicates()
    
    # Drop rows where student_id is completely missing
    if 'student_id' in df.columns:
        df = df.dropna(subset=['student_id'])
        # Ensure student ID is string
        df['student_id'] = df['student_id'].astype(str)
        # Keep first instance if duplicate student IDs remain
        df = df.drop_duplicates(subset=['student_id'], keep='first')
        
    return df
