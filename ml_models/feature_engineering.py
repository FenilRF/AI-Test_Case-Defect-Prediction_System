"""
Feature Engineering for Defect Prediction
--------------------------------------------
Provides feature extraction and transformation utilities
used by both the training script and the prediction service.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple


# Feature columns used by the model
FEATURE_COLUMNS = ["lines_of_code", "complexity_score", "past_defects", "code_churn"]
TARGET_COLUMN = "defect_label"


def load_and_prepare_data(csv_path: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load training CSV and split into features (X) and target (y).

    Parameters
    ----------
    csv_path : str
        Path to the CSV file with columns matching FEATURE_COLUMNS + TARGET_COLUMN.

    Returns
    -------
    tuple[DataFrame, Series]
        (X, y) where X is the feature matrix and y is the binary target.
    """
    df = pd.read_csv(csv_path)

    # Validate required columns
    missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    return X, y


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer additional features from raw metrics.

    New features:
      • defect_density    = past_defects / lines_of_code
      • churn_complexity  = code_churn × complexity_score
      • risk_index        = (past_defects × complexity_score) / max(lines_of_code, 1)
    """
    out = df.copy()
    out["defect_density"] = out["past_defects"] / out["lines_of_code"].clip(lower=1)
    out["churn_complexity"] = out["code_churn"] * out["complexity_score"]
    out["risk_index"] = (out["past_defects"] * out["complexity_score"]) / out["lines_of_code"].clip(lower=1)
    return out


def scale_features(X_train: np.ndarray, X_test: np.ndarray = None) -> Tuple:
    """
    Fit a StandardScaler on training data and optionally transform test data.

    Returns
    -------
    tuple
        (X_train_scaled, X_test_scaled | None, scaler)
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test) if X_test is not None else None
    return X_train_scaled, X_test_scaled, scaler
