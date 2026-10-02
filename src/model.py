from pathlib import Path

from pandas import DataFrame

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def load_dataset(csv_path: str | Path) -> DataFrame:
    df = DataFrame
    return __import__("pandas").read_csv(csv_path)


def derive_farm_features(
    soil_ph: float,
    rainfall_reliability: float,
    temperature: float,
    risk_preference: str,
    input_access: str,
    past_yield: float,
    farm_size: float,
) -> dict:
    access_factor = {"Low": 0.85, "Medium": 1.0, "High": 1.2}
    risk_factor = {"Low": 0.95, "Medium": 1.0, "High": 1.08}

    rainfall = rainfall_reliability * 2.0
    humidity = 65 + (past_yield * 2.5) + (farm_size * 0.35)

    n = 62 + (access_factor.get(input_access, 1.0) * 28) + (past_yield * 7)
    p = 38 + (access_factor.get(input_access, 1.0) * 20) + (past_yield * 6)
    k = 34 + (access_factor.get(input_access, 1.0) * 18) + (past_yield * 5)

    n *= risk_factor.get(risk_preference, 1.0)
    p *= risk_factor.get(risk_preference, 1.0)
    k *= risk_factor.get(risk_preference, 1.0)

    return {
        "N": round(min(max(n, 0), 150), 2),
        "P": round(min(max(p, 0), 150), 2),
        "K": round(min(max(k, 0), 150), 2),
        "temperature": round(temperature, 2),
        "humidity": round(min(max(humidity, 30), 100), 2),
        "ph": round(soil_ph, 2),
        "rainfall": round(min(max(rainfall, 30), 300), 2),
    }


def build_model(df):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    X = df.drop(columns=["label"], errors="ignore")
    y = df["label"]

    X = X[FEATURE_COLUMNS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")),
        ]
    )

    pipeline.fit(X_train, y_train)

    # Quick validation for feedback in terminal
    test_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, test_pred)
    report = classification_report(y_test, test_pred, zero_division=0)

    print(f"Crop model validation accuracy: {acc:.3f}")
    print(report)

    return pipeline


def recommend_crops(model, row_dict):
    import numpy as np
    import pandas as pd

    feature_row = pd.DataFrame([row_dict], columns=FEATURE_COLUMNS)
    probabilities = model.predict_proba(feature_row)[0]
    labels = model.classes_

    ranked = sorted(zip(labels, probabilities), key=lambda item: item[1], reverse=True)[:3]
    return [{"crop": crop, "score": float(score)} for crop, score in ranked]
