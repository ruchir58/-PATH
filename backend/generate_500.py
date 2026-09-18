import pandas as pd
import numpy as np

def generate_samples():
    np.random.seed(42)
    n = 500

    classes = ['CS101', 'CS102', 'CS201', 'CS301', 'IT101']
    names = [f"Student_{i}" for i in range(1, n+1)]
    ids = [f"STU{1000+i}" for i in range(1, n+1)]
    
    # Generate somewhat realistic data
    attendance = np.random.normal(75, 15, n)
    attendance = np.clip(attendance, 10, 100)
    
    quiz_1 = np.random.normal(70, 15, n) * (attendance / 100)
    quiz_2 = np.random.normal(75, 10, n) * (attendance / 100)
    assignment_1 = np.random.normal(80, 10, n) * (attendance / 100)
    assignment_2 = np.random.normal(85, 10, n) * (attendance / 100)
    lab_score = np.random.normal(70, 20, n) * (attendance / 100)
    prior_gpa = np.random.normal(7.5, 1.5, n)
    
    df = pd.DataFrame({
        'student_id': ids,
        'name': names,
        'class': np.random.choice(classes, n),
        'attendance': attendance,
        'quiz_1': np.clip(quiz_1, 0, 100),
        'quiz_2': np.clip(quiz_2, 0, 100),
        'assignment_1': np.clip(assignment_1, 0, 100),
        'assignment_2': np.clip(assignment_2, 0, 100),
        'lab_score': np.clip(lab_score, 0, 100),
        'prior_gpa': np.clip(prior_gpa, 0, 10),
    })

    # Generate target logic: 
    # At risk if average score < 60 OR attendance < 50
    avg_score = df[['quiz_1', 'quiz_2', 'assignment_1', 'assignment_2', 'lab_score']].mean(axis=1)
    df['support_needed'] = ((avg_score < 60) | (df['attendance'] < 50)).astype(int).map({1: 'Yes', 0: 'No'})

    # Clean dataset
    df.to_csv("student_data_500.csv", index=False)
    
    # Messy dataset
    df_messy = df.copy()
    # Rename columns to test standardization
    df_messy.rename(columns={'student_id': 'Roll No', 'attendance': 'Attendance_Percent', 'support_needed': 'At Risk'}, inplace=True)
    # Add string percentages
    df_messy['Attendance_Percent'] = df_messy['Attendance_Percent'].apply(lambda x: f"{int(x)}%")
    # Add missing values
    df_messy.loc[5:45, 'quiz_1'] = np.nan
    df_messy.loc[100:150, 'class'] = np.nan
    # Add out of bounds
    df_messy.loc[200:210, 'Attendance_Percent'] = "150%"
    df_messy.loc[300:305, 'Attendance_Percent'] = "-10%"
    # Add duplicates
    df_messy = pd.concat([df_messy, df_messy.iloc[0:20]], ignore_index=True)
    
    df_messy.to_csv("student_data_500_messy.csv", index=False)
    print("Generated student_data_500.csv and student_data_500_messy.csv")

if __name__ == "__main__":
    generate_samples()
