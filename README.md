# AI-Based Test Case Generation and Defect Prediction System

AI-powered QA platform that converts requirements and design inputs into structured test cases, runs risk analysis, and predicts defect risk using ML.

## What This Project Does

- Generates functional test cases from requirement text using NLP and rule-based logic.
- Supports enterprise test generation and design-based generation from files, text, and URLs.
- Runs multi-layer risk analysis on requirement and design context.
- Predicts defect probability and risk class for modules.
- Stores generated artifacts in timestamped folders and exports test cases to CSV, JSON, and Excel.

## Current Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, NLTK, scikit-learn
- Design Intelligence: Groq API, Playwright, Pillow, BeautifulSoup, PyPDF2, python-docx, python-pptx
- Frontend: React 19, Vite 7, Axios, Bootstrap 5, Chart.js
- Database: SQLite by default (configurable via DATABASE_URL)
- Testing: Pytest, HTTPX

## Architecture Design

### High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                             Frontend (React)                        │
│  Pages: Dashboard, Upload Requirement, Upload Design, Test Cases,   │
│         Defect Prediction                                            │
└───────────────────────────────┬──────────────────────────────────────┘
                      │ HTTP/JSON
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend                            │
│                                                                      │
│  API Layer                                                           │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ /api/requirements, /api/test-cases, /api/predict-defect,      │  │
│  │ /api/design/upload, /api/dashboard/stats, exports             │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  Service Layer                                                       │
│  ┌───────────────────────────┬────────────────────────────────────┐  │
│  │ Requirement Pipeline      │ Design Intelligence Pipeline       │  │
│  │ - chunker + NLP parser    │ - file/url ingestion              │  │
│  │ - test generator          │ - crawl / vision / extraction     │  │
│  │ - complexity + dedupe     │ - UI schema + flow detection      │  │
│  │ - risk analysis           │ - enterprise LLM test generation  │  │
│  │ - defect prediction       │ - coverage validation             │  │
│  └───────────────────────────┴────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  Persistence + Artifacts                                              │
│  - SQLite tables: requirements, test_cases, predictions, designs      │
│  - Folder storage: backend/test_cases/<timestamped folders>           │
│  - Exports: CSV / JSON / Excel                                        │
└───────────────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        External Services                             │
│  Groq (LLM text + vision), Playwright crawling, file parsers         │
└──────────────────────────────────────────────────────────────────────┘
```

### Core Data Flows

1. Requirement Flow
  User submits requirement text -> NLP parsing -> test generation -> scoring and deduplication -> risk analysis + defect prediction -> DB save + folder artifacts -> response to UI.

2. Design Flow
  User uploads file/image/URL/text -> extraction/crawling/vision analysis -> UI schema + flow detection -> enterprise test generation -> DB save + design folder artifacts -> response to UI.

3. Reporting and Management Flow
  UI requests grouped test cases, dashboard stats, and exports -> API queries DB -> response as JSON/CSV/Excel.

### Architecture Notes

- The backend is modular by layer: api, services, models, schemas, utils.
- Storage is dual-mode: relational records in SQLite and audit artifacts in filesystem folders.
- The design pipeline is fault-tolerant: if intelligence analysis fails, upload metadata is still persisted with graceful fallback.

## Project Structure

  AI-TestCase-Defect-Prediction-System/
  |- AI-Test-Generator.md
  |- README.md
  |- backend/
  |  |- main.py
  |  |- requirements.txt
  |  |- app/
  |  |  |- api/
  |  |  |  |- requirements.py
  |  |  |  |- defect_prediction.py
  |  |  |  |- design_upload.py
  |  |  |- models/
  |  |  |- schemas/
  |  |  |- services/
  |  |  |- utils/
  |  |- test_cases/
  |- frontend/
  |  |- src/
  |  |- package.json
  |- ml_models/
  |  |- training/
  |  |- saved_models/
  |- datasets/
  |  |- defect_data.csv
  |  |- sample_requirements.json
  |- docs/
  |  |- api_documentation.md
  |  |- postman_collection.json
  |  |- CEO_Project_Documentation.md
  |- tests/

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1) Backend setup

  cd backend
  python -m venv venv

Windows:

  venv\Scripts\activate

macOS/Linux:

  source venv/bin/activate

Install dependencies:

  pip install -r requirements.txt

Optional but recommended for design crawling and screenshots:

  python -m playwright install

### 2) Frontend setup

  cd frontend
  npm install

## Run the Application

### Terminal 1: Backend

  cd backend
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

### Terminal 2: Frontend

  cd frontend
  npm run dev

App URLs:

- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Frontend: http://localhost:5173

## Main API Endpoints

### Health

- GET / 
- GET /health

### Requirements and Test Cases

- POST /api/requirements
- GET /api/requirements
- GET /api/requirements/{req_id}
- POST /api/generate-testcases
- POST /api/generate-enterprise
- GET /api/test-cases
- GET /api/test-cases/grouped
- DELETE /api/test-cases/{test_id}
- POST /api/test-cases/delete-selected
- DELETE /api/test-cases/clear/{req_id}
- DELETE /api/test-cases/clear-all
- DELETE /api/test-cases/clear-module/{module_name}
- GET /api/test-cases/export/csv
- GET /api/test-cases/export/json
- POST /api/test-cases/export/excel
- POST /api/test-cases/save-excel/{req_id}
- POST /api/risk-analysis

### Defect Prediction

- POST /api/predict-defect
- GET /api/predictions
- POST /api/defect-data
- GET /api/defect-data
- GET /api/dashboard/stats
- POST /api/model/reload

### Design Upload and Intelligence

- POST /api/design/upload
- GET /api/design/{design_id}
- GET /api/design/by-requirement/{req_id}

## ML Model Training

From project root:

  python -m ml_models.training.train_model

Expected output files:

- ml_models/saved_models/defect_model.pkl
- ml_models/saved_models/scaler.pkl

If model files are missing, defect prediction falls back to heuristic scoring.

## Running Tests

From backend folder:

  python -m pytest ../tests/ -v --tb=short

Run specific suites:

  python -m pytest ../tests/test_nlp_service.py -v
  python -m pytest ../tests/test_case_generator.py -v
  python -m pytest ../tests/test_defect_predictor.py -v
  python -m pytest ../tests/test_api.py -v

## Environment Variables

Set these in backend/.env if needed:

- DATABASE_URL (default: sqlite:///./app_database.db)
- DEBUG (default: True)
- LOG_LEVEL (default: INFO)
- CORS_ORIGINS (default includes localhost:5173 and localhost:3000)
- GROQ_API_KEY
- GROQ_TEXT_MODEL
- GROQ_VISION_MODEL

## Notes

- Generated requirement and design artifacts are stored under backend/test_cases.
- datasets folder is intentionally kept for model training and sample data.
- frontend/node_modules is environment-specific and can be reinstalled with npm install.

## License

Internal project for development, demonstration, and evaluation.
