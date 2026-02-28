"""
ML Model Training Script
===========================
Trains a Logistic Regression model for defect prediction.

Usage:
    python -m ml_models.training.train_model

Process:
    1. Load synthetic training data from datasets/defect_data.csv
    2. Perform feature engineering (optional derived features)
    3. Split into train/test sets (80/20)
    4. Scale features using StandardScaler
    5. Train Logistic Regression with class_weight='balanced'
    6. Evaluate on test set (accuracy, precision, recall, F1, AUC-ROC)
    7. Save model (.pkl) and scaler (.pkl) to ml_models/saved_models/
"""

import os
import sys
import logging

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

# Add project root to path so we can import ml_models.feature_engineering
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ml_models.feature_engineering import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_and_prepare_data,
    scale_features,
)

# ── Configuration ────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

DATASET_PATH = os.path.join(PROJECT_ROOT, "datasets", "defect_data.csv")
SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "ml_models", "saved_models")
MODEL_PATH = os.path.join(SAVED_MODELS_DIR, "defect_model.pkl")
SCALER_PATH = os.path.join(SAVED_MODELS_DIR, "scaler.pkl")

# Ensure output directory exists
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)


def train():
    """Execute the full training pipeline."""
    logger.info("=" * 60)
    logger.info("DEFECT PREDICTION MODEL — TRAINING PIPELINE")
    logger.info("=" * 60)

    # ── Step 1: Load data ────────────────────────────────────
    logger.info("Step 1: Loading dataset from %s", DATASET_PATH)
    X, y = load_and_prepare_data(DATASET_PATH)
    logger.info("Dataset shape: %s, Target distribution:\n%s", X.shape, y.value_counts().to_string())

    # ── Step 2: Train/Test split ─────────────────────────────
    logger.info("Step 2: Splitting data (80%% train / 20%% test)")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )
    logger.info("Train set: %d samples | Test set: %d samples", len(X_train), len(X_test))

    # ── Step 3: Feature scaling ──────────────────────────────
    logger.info("Step 3: Scaling features with StandardScaler")
    X_train_scaled, X_test_scaled, scaler = scale_features(
        X_train.values, X_test.values,
    )

    # ── Step 4: Train model ──────────────────────────────────
    # Using class_weight='balanced' to handle potential class imbalance.
    # Logistic Regression is chosen for interpretability and decent
    # performance on tabular data with limited features.
    logger.info("Step 4: Training Logistic Regression (class_weight='balanced')")
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
        solver="lbfgs",
        C=1.0,  # Regularisation strength (inverse)
    )
    model.fit(X_train_scaled, y_train)
    logger.info("Model coefficients: %s", dict(zip(FEATURE_COLUMNS, model.coef_[0].round(4))))
    logger.info("Model intercept: %.4f", model.intercept_[0])

    # ── Step 5: Evaluate ─────────────────────────────────────
    logger.info("Step 5: Evaluating model on test set")
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc_roc = roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else 0.0

    logger.info("─── EVALUATION RESULTS ───")
    logger.info("Accuracy:  %.4f", accuracy)
    logger.info("Precision: %.4f", precision)
    logger.info("Recall:    %.4f", recall)
    logger.info("F1 Score:  %.4f", f1)
    logger.info("AUC-ROC:   %.4f", auc_roc)
    logger.info("Confusion Matrix:\n%s", confusion_matrix(y_test, y_pred))
    logger.info("Classification Report:\n%s", classification_report(y_test, y_pred, zero_division=0))

    # ── Step 6: Save artefacts ───────────────────────────────
    logger.info("Step 6: Saving model and scaler")
    joblib.dump(model, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    logger.info("Scaler saved to %s", SCALER_PATH)

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE — model ready for inference")
    logger.info("=" * 60)

    return model, scaler


if __name__ == "__main__":
    train()
