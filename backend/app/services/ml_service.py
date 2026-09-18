import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import os
import json

MODELS_DIR = "models"

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Dynamic feature engineering"""
    df_feat = df.copy()
    numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
    
    # Identify marks columns (quiz, assignment, lab, score)
    marks_cols = [c for c in numeric_cols if any(kw in c for kw in ['quiz', 'assignment', 'lab', 'score', 'mark', 'prior', 'cgpa', 'gpa'])]
    
    if marks_cols:
        df_feat['average_score'] = df_feat[marks_cols].mean(axis=1)
        df_feat['performance_consistency'] = df_feat[marks_cols].std(axis=1).fillna(0)
    
    # Calculate missed submissions (if missing was 0, but since we median imputed, we can't easily tell unless we track before imputation. 
    # For now, just a dummy if needed, or based on threshold)
    df_feat['low_performance_indicator'] = 0
    if 'average_score' in df_feat.columns:
        threshold = df_feat['average_score'].median()
        df_feat['low_performance_indicator'] = (df_feat['average_score'] < threshold).astype(int)
        
    return df_feat

def train_and_select_model(df: pd.DataFrame, target_col: str, dataset_id: int):
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in the dataset.")
        
    # Drop IDs and target for features
    features = [c for c in df.columns if c != target_col and c not in ['student_id', 'name', 'class', 'class_name']]
    
    X = df[features]
    
    # Check if target is categorical or numeric. If numeric and many unique, it's regression (not supported)
    # We want binary classification (at-risk or not) or multi-class
    y = df[target_col]
    if y.dtype == object or len(y.unique()) <= 10:
        y = y.astype(str)
    else:
        # Binarize if it's a score
        y = (y < y.median()).astype(int).astype(str)
        
    # Ensure X is only numeric (dummy encode object cols if any)
    X = pd.get_dummies(X, drop_first=True)
    feature_names = X.columns.tolist()
    
    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42)
    }
    
    best_model_name = ""
    best_accuracy = -1
    best_f1 = -1
    best_pipeline = None
    all_metrics = {}
    
    for name, model in models.items():
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', model)
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        metrics = {
            "accuracy": acc,
            "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
            "f1_score": f1,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        all_metrics[name] = metrics
        
        if acc > best_accuracy or (acc == best_accuracy and f1 > best_f1):
            best_accuracy = acc
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipeline
            
    # Save best model
    model_path = os.path.join(MODELS_DIR, f"model_dataset_{dataset_id}.joblib")
    joblib.dump({
        'pipeline': best_pipeline,
        'features': feature_names,
        'target_col': target_col,
        'classes': best_pipeline.classes_.tolist()
    }, model_path)
    
    return best_model_name, all_metrics, model_path

def predict_risk(df: pd.DataFrame, model_path: str):
    data = joblib.load(model_path)
    pipeline = data['pipeline']
    features = data['features']
    classes = data['classes']
    
    # Ensure all features exist
    X = pd.get_dummies(df) # Do NOT use drop_first=True for inference to prevent dropping the only category in a single row
    for f in features:
        if f not in X.columns:
            X[f] = 0
    X = X[features]
    
    probs = pipeline.predict_proba(X)
    
    # Determine which class represents 'risk'
    # Default to 1 if binary, otherwise 0
    risk_class_idx = 1 if len(classes) > 1 else 0
    for idx, c in enumerate(classes):
        c_lower = str(c).lower()
        if any(bad in c_lower for bad in ['risk', 'fail', 'support', '1', 'true', 'drop', 'poor']):
            risk_class_idx = idx
            break
            
    risk_probs = probs[:, risk_class_idx]
    
    results = []
    classifier = pipeline.named_steps['classifier']
    
    for idx, prob in enumerate(risk_probs):
        if prob < 0.33:
            level = "low"
        elif prob < 0.66:
            level = "medium"
        else:
            level = "high"
            
        # Explanations using Logistic Regression coefficients or Tree importance
        reason = "Multiple factors"
        if isinstance(classifier, LogisticRegression):
            coef = classifier.coef_[0]
            top_feature_idx = np.argsort(np.abs(coef))[-1]
            reason = f"Main indicator: {features[top_feature_idx]}"
        elif hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            top_feature_idx = np.argsort(importances)[-1]
            reason = f"Main indicator: {features[top_feature_idx]}"
            
        results.append({
            "risk_probability": round(prob, 2),
            "risk_level": level,
            "why_flagged": reason if level in ['medium', 'high'] else "Normal performance"
        })
        
    return results
