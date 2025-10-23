import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, classification_report
from joblib import dump

DATA_CANDIDATES = [
    "student_survey_results.csv",  # produced by the app for multiple submissions
    "student_survey.csv",          # raw CSV as per README
]

FEATURES_PREFERRED = [
    "Stress_Level",
    "Sleep_Hours",
    "Exercise_Hours",
    # Add optional extras if present
    "Academic_Workload",
    "Anxiety_Level",
    "Social_Support",
    "Depression_Level",
    "Financial_Stress",
    "Relationship_Stress",
]


def find_data_path():
    for p in DATA_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No survey data found. Expected one of: " + ", ".join(DATA_CANDIDATES)
    )


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic cleaning: drop completely empty rows
    df = df.dropna(how="all")
    return df


def build_proxy_label(df: pd.DataFrame) -> pd.Series:
    # Proxy rule aligned with README thresholds
    stress = df.get("Stress_Level", pd.Series([0]*len(df)))
    sleep = df.get("Sleep_Hours", pd.Series([10]*len(df)))
    exercise = df.get("Exercise_Hours", pd.Series([10]*len(df)))
    high_risk = ((stress > 7) | (sleep < 6) | (exercise < 1)).astype(int)
    return high_risk


def pick_features(df: pd.DataFrame):
    cols = [c for c in FEATURES_PREFERRED if c in df.columns]
    if len(cols) < 3:
        # Ensure we at least have the core three from README
        core = [c for c in ["Stress_Level", "Sleep_Hours", "Exercise_Hours"] if c in df.columns]
        cols = core
    if not cols:
        raise ValueError("No usable feature columns found in data.")
    return cols


def main():
    data_path = find_data_path()
    df = load_data(data_path)

    # Create or use an existing label
    y = df["high_risk"] if "high_risk" in df.columns else build_proxy_label(df)

    feature_cols = pick_features(df)
    X = df[feature_cols].copy()

    # Check if we have enough data for stratified split
    min_class_count = y.value_counts().min() if len(y) > 0 else 0
    use_stratify = (y.nunique() == 2 and min_class_count >= 2)
    
    # For very small datasets, use smaller test size or no split
    if len(X) < 10:
        print(f"Warning: Only {len(X)} samples available. Using all data for training (no test set).")
        X_train, X_test, y_train, y_test = X, X.iloc[:0], y, y.iloc[:0]
    else:
        test_size = 0.2 if len(X) >= 20 else 0.1
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if use_stratify else None
        )

    # Pipeline: scale numeric features + Logistic Regression
    pipe = Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")),
    ])

    pipe.fit(X_train, y_train)

    # Evaluate
    if len(X_test) > 0 and len(set(y_test)) == 2:
        y_prob = pipe.predict_proba(X_test)[:, 1]
        y_pred = pipe.predict(X_test)
        try:
            roc = roc_auc_score(y_test, y_prob)
        except Exception:
            roc = float('nan')
        f1 = f1_score(y_test, y_pred)
        print(f"ROC-AUC: {roc:.3f}")
        print(f"F1: {f1:.3f}")
        print(classification_report(y_test, y_pred))
    elif len(X_test) == 0:
        print("No test set available (dataset too small). Model trained on all data.")
    else:
        print("Warning: Test set does not contain both classes; skipping metrics.")

    # Persist
    os.makedirs("models", exist_ok=True)
    dump(pipe, os.path.join("models", "risk_model.joblib"))
    with open(os.path.join("models", "feature_list.json"), "w") as f:
        json.dump({"features": feature_cols}, f)

    print("Saved model to models/risk_model.joblib with features:", feature_cols)


if __name__ == "__main__":
    main()
