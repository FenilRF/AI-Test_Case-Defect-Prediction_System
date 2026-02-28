# AI-Based Test Case Generation and Defect Prediction System

> An AI-powered web application that automatically generates software test cases from textual requirements using NLP, predicts defect-prone modules using machine learning, and provides a risk-based prioritisation dashboard for QA teams.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikitlearn)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [ML Model Training](#ml-model-training)
- [Testing](#testing)
- [Sample Usage](#sample-usage)

---

## Features

### 1. NLP-Based Requirement Parsing
- Text preprocessing (tokenisation, stopword removal, lemmatisation)
- Automatic extraction of **actions**, **fields**, and **validations**
- Module name detection from requirement context

### 2. Automated Test Case Generation
- **Positive** test cases — happy-path scenarios
- **Negative** test cases — missing/invalid inputs
- **Boundary** test cases — min/max limits
- **Edge** test cases — unicode, concurrency, idempotency
- **Security** test cases — SQL injection, XSS probes

### 3. ML-Based Defect Prediction
- Logistic Regression model trained on module-level metrics
- Predicts defect probability (0–1) with risk classification
- Risk levels: **High** (≥0.7), **Medium** (0.4–0.7), **Low** (<0.4)

### 4. Risk-Based Prioritisation
- High Risk → **P1** (Critical)
- Medium Risk → **P2** (Major)
- Low Risk → **P3** (Minor)

### 5. Dashboard & Visualisation
- Real-time stats (requirements, test cases, predictions)
- Risk distribution doughnut chart
- Defect probability bar chart
- CSV & JSON export for test cases

---

## Architecture

```
┌────────────────┐     HTTP/REST      ┌───────────────────┐
│                │  ◄──────────────►  │                   │
│  React + Vite  │                    │  FastAPI Backend   │
│  (Frontend)    │                    │                   │
│                │                    │  ┌─────────────┐  │
└────────────────┘                    │  │ NLP Engine   │  │
                                      │  │ Test Gen     │  │
                                      │  │ ML Predictor │  │
                                      │  └─────────────┘  │
                                      │         │         │
                                      │    ┌────▼────┐    │
                                      │    │ SQLite  │    │
                                      │    │   DB    │    │
                                      │    └─────────┘    │
                                      └───────────────────┘
```

---

## Tech Stack

| Layer       | Technology                                  |
|-------------|---------------------------------------------|
| Backend     | Python 3.11, FastAPI, SQLAlchemy, Pydantic   |
| Database    | SQLite (swappable via DATABASE_URL)           |
| ML          | scikit-learn, pandas, numpy, joblib           |
| NLP         | NLTK                                         |
| Frontend    | React 18, Vite, Axios, Chart.js, Bootstrap 5 |
| Testing     | Pytest, httpx                                |

---

## Project Structure

```
AI-TestCase-Defect-Prediction-System/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── requirements.py        # Requirement & test case endpoints
│   │   │   └── defect_prediction.py   # Prediction & dashboard endpoints
│   │   ├── models/
│   │   │   ├── database.py            # SQLAlchemy engine & session
│   │   │   └── models.py             # ORM models
│   │   ├── schemas/
│   │   │   └── schemas.py            # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── nlp_service.py         # NLP requirement parser
│   │   │   ├── test_case_generator.py # Test case generation engine
│   │   │   └── defect_prediction_service.py  # ML prediction service
│   │   ├── utils/
│   │   │   ├── text_preprocessing.py  # NLTK text pipeline
│   │   │   └── export.py             # CSV/JSON export helpers
│   │   └── config.py                 # Pydantic settings
│   ├── main.py                       # FastAPI app entry point
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── ml_models/
│   ├── training/
│   │   └── train_model.py            # Model training script
│   ├── saved_models/                 # Trained .pkl files
│   └── feature_engineering.py        # Feature extraction utilities
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx          # Dashboard
│   │   │   ├── UploadRequirement.jsx # Requirement input + generation
│   │   │   ├── GeneratedTestCases.jsx # Test case listing + export
│   │   │   └── DefectPrediction.jsx  # Prediction form + charts
│   │   ├── services/
│   │   │   └── api.js                # Axios API layer
│   │   ├── App.jsx                   # Router + sidebar nav
│   │   ├── App.css                   # Global styles
│   │   └── main.jsx                  # React entry point
│   └── package.json
│
├── datasets/
│   ├── defect_data.csv               # Synthetic training data (50 modules)
│   └── sample_requirements.json      # Sample requirement texts
│
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_nlp_service.py           # NLP unit tests
│   ├── test_case_generator.py        # Generator unit tests
│   ├── test_defect_predictor.py      # Predictor unit tests
│   └── test_api.py                   # API integration tests
│
├── docs/
│   ├── api_documentation.md          # API reference
│   └── postman_collection.json       # Postman import file
│
└── README.md
```

---

## Setup & Installation

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-TestCase-Defect-Prediction-System
```

### 2. Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Train the ML Model (Optional but Recommended)

```bash
cd ..
python -m ml_models.training.train_model
```

This creates `defect_model.pkl` and `scaler.pkl` in `ml_models/saved_models/`.  
If skipped, the system uses a heuristic fallback for predictions.

### 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The UI is now available at **http://localhost:5173**

---

## API Documentation

FastAPI auto-generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| GET    | `/`                          | Health check                         |
| POST   | `/api/requirements`          | Store a requirement                  |
| GET    | `/api/requirements`          | List all requirements                |
| POST   | `/api/generate-testcases`    | Parse requirement + generate cases   |
| GET    | `/api/test-cases`            | List generated test cases            |
| GET    | `/api/test-cases/export/csv` | Export test cases as CSV             |
| GET    | `/api/test-cases/export/json`| Export test cases as JSON            |
| POST   | `/api/predict-defect`        | Predict defect probability           |
| GET    | `/api/predictions`           | List prediction history              |
| GET    | `/api/dashboard/stats`       | Get dashboard statistics             |
| POST   | `/api/model/reload`          | Reload ML model after retraining     |

---

## ML Model Training

The training script (`ml_models/training/train_model.py`) follows this pipeline:

1. **Load Data** — reads `datasets/defect_data.csv`
2. **Split** — 80% train / 20% test (stratified)
3. **Scale** — StandardScaler normalisation
4. **Train** — Logistic Regression with `class_weight='balanced'`
5. **Evaluate** — accuracy, precision, recall, F1, AUC-ROC
6. **Save** — `defect_model.pkl` + `scaler.pkl`

### Features Used

| Feature          | Description                    |
|------------------|--------------------------------|
| lines_of_code    | Total lines in the module      |
| complexity_score | Cyclomatic complexity metric   |
| past_defects     | Historical defect count        |
| code_churn       | Lines changed recently         |

### Risk Classification

| Probability   | Risk Level | QA Priority |
|---------------|------------|-------------|
| 0.7 – 1.0    | High       | P1          |
| 0.4 – 0.7    | Medium     | P2          |
| 0.0 – 0.4    | Low        | P3          |

---

## Testing

Run all tests:

```bash
# From project root
cd backend
python -m pytest ../tests/ -v --tb=short
```

Run specific test files:

```bash
python -m pytest ../tests/test_nlp_service.py -v
python -m pytest ../tests/test_case_generator.py -v
python -m pytest ../tests/test_defect_predictor.py -v
python -m pytest ../tests/test_api.py -v
```

---

## Sample Usage

### Generate Test Cases

```bash
curl -X POST http://localhost:8000/api/generate-testcases \
  -H "Content-Type: application/json" \
  -d '{"requirement_text": "The system shall allow users to login using email and password. Email must be valid format and password is required."}'
```

### Predict Defects

```bash
curl -X POST http://localhost:8000/api/predict-defect \
  -H "Content-Type: application/json" \
  -d '{"module_name": "Payment", "lines_of_code": 4200, "complexity_score": 42.0, "past_defects": 18, "code_churn": 250}'
```

---

## Environment Variables

| Variable        | Default                  | Description              |
|-----------------|--------------------------|--------------------------|
| DATABASE_URL    | sqlite:///./app_database.db | Database connection URL |
| DEBUG           | True                     | Enable debug logging     |
| LOG_LEVEL       | INFO                     | Logging level            |
| CORS_ORIGINS    | ["http://localhost:5173"] | Allowed CORS origins     |

---

## License

This project is built for educational and demonstration purposes.

---

*Built with ❤️ using FastAPI, React, scikit-learn, and NLTK*
