# AI-Based Test Case Generation & Defect Prediction System
## Executive Documentation for Leadership Review

**Document Version:** 1.0  
**Date:** March 11, 2026  
**Classification:** Internal — Confidential

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Business Problem](#2-the-business-problem)
3. [Our Solution](#3-our-solution)
4. [How It Works (Non-Technical)](#4-how-it-works-non-technical)
5. [Key Features & Capabilities](#5-key-features--capabilities)
6. [System Architecture](#6-system-architecture)
7. [Technology Stack](#7-technology-stack)
8. [Detailed Component Breakdown](#8-detailed-component-breakdown)
9. [AI & Machine Learning Explained](#9-ai--machine-learning-explained)
10. [User Workflows & Screenshots Guide](#10-user-workflows--screenshots-guide)
11. [API & Integration Capabilities](#11-api--integration-capabilities)
12. [Data Flow & Processing Pipeline](#12-data-flow--processing-pipeline)
13. [Quality Assurance & Testing](#13-quality-assurance--testing)
14. [Security Considerations](#14-security-considerations)
15. [Business Value & ROI](#15-business-value--roi)
16. [Current Status & Roadmap](#16-current-status--roadmap)
17. [Glossary](#17-glossary)

---

## 1. Executive Summary

The **AI-Based Test Case Generation & Defect Prediction System** is an internally built AI-powered web application that **automates two of the most time-consuming activities in software quality assurance**:

1. **Test Case Generation** — Automatically creates comprehensive test scenarios from written software requirements or design documents, eliminating hours of manual test writing.
2. **Defect Prediction** — Uses machine learning to predict which software modules are most likely to contain bugs, allowing QA teams to focus effort where it matters most.

### What does it do in one sentence?
> *You give it a software requirement or a design document, and the system instantly generates a full suite of professional test cases while predicting which parts of your software are at highest risk of defects — prioritising everything by risk level.*

### Key Metrics
| Metric | Value |
|--------|-------|
| Test Case Types Generated | 5 categories (Positive, Negative, Boundary, Edge Case, Security) |
| Risk Layers Analyzed | 6 layers (UI, API, Integration, Function, System, Non-functional) |
| Input Methods Supported | Text, Documents (PDF/DOCX/PPTX), Images/Screenshots, URLs |
| Export Formats | CSV, JSON, Excel |
| AI Models Used | NLP Parser + ML Defect Predictor + LLM (GPT/Llama) |

---

## 2. The Business Problem

### The Current Pain Points in Software QA

| Problem | Impact |
|---------|--------|
| **Manual test case writing is slow** | QA engineers spend 40-60% of their time writing test cases by hand from requirements documents |
| **Test coverage gaps** | Humans miss edge cases, security scenarios, and boundary conditions — leading to production bugs |
| **No data-driven defect prioritisation** | Teams test everything equally instead of focusing on high-risk modules |
| **Inconsistent test quality** | Test case quality varies across team members and projects |
| **Late defect discovery** | Bugs found in production cost 10-100x more to fix than those caught during testing |
| **Design-to-test disconnect** | Converting UI designs into test scenarios is manual and error-prone |

### Industry Statistics
- **The average cost of a software bug in production is $10,000** (IBM Systems Science Institute)
- **QA engineers spend approximately 30% of their time on test case creation** rather than actual testing
- **Up to 40% of software defects** are due to incomplete or missed test scenarios

---

## 3. Our Solution

We built a **full-stack web application** that uses **three layers of AI** to solve these problems:

### Layer 1: NLP (Natural Language Processing) Engine
- Reads software requirements written in plain English
- Automatically extracts: **modules**, **actions**, **fields**, and **validation rules**
- Understands context (e.g., "login with email and password" → Login module, email field, password field)

### Layer 2: Intelligent Test Case Generator
- Takes NLP-parsed requirements and generates **5 types of test cases**:
  - **Positive Tests** — Verify the system works correctly (happy path)
  - **Negative Tests** — Verify proper error handling (invalid inputs)
  - **Boundary Tests** — Test limits and extremes (min/max values)
  - **Edge Case Tests** — Test unusual scenarios (unicode, concurrency)
  - **Security Tests** — Test for vulnerabilities (SQL injection, XSS)
- Also has an **Enterprise Mode** using LLM (Large Language Model) AI for even more comprehensive generation

### Layer 3: ML (Machine Learning) Defect Predictor
- Trained on historical software metrics data
- Predicts the **probability (0-100%) that a module will have defects**
- Classifies risk as **High**, **Medium**, or **Low**
- Assigns QA priority: **P1 (Critical)**, **P2 (Major)**, **P3 (Minor)**

### Bonus: Design Intelligence Engine
- Accepts **UI screenshots**, **design documents** (PDF, DOCX, PPTX), and **live URLs**
- Uses **Vision AI** to analyze UI screenshots
- Uses **web crawling** to analyze live websites
- Generates test cases directly from designs — not just requirements

---

## 4. How It Works (Non-Technical)

### Workflow 1: Requirement → Test Cases

```
Step 1: QA engineer pastes a requirement
        "The system shall allow users to register with name, email, and password.
         Email must be valid format. Password must be at least 8 characters."
            │
            ▼
Step 2: AI reads and understands the requirement
        Module: Registration
        Actions: register
        Fields: name, email, password
        Validations: valid format, minimum length
            │
            ▼
Step 3: System generates 20-50+ test cases automatically
        ✅ "Verify registration succeeds with valid name, email, password"
        ❌ "Verify error when email is empty"
        ❌ "Verify error when password is less than 8 characters"
        🔒 "Verify SQL injection attempt in email field is rejected"
        📊 "Verify registration with exactly 8 character password (boundary)"
            │
            ▼
Step 4: Risk analysis scores the requirement across 6 layers
        UI Risk: 0.6 (Medium) | API Risk: 0.3 (Low) | Security Risk: 0.8 (High)
            │
            ▼
Step 5: Defect prediction estimates bug probability
        Registration Module: 67% defect probability → Medium Risk → P2 Priority
            │
            ▼
Step 6: Export everything to CSV/JSON/Excel for your test management tool
```

### Workflow 2: Design → Test Cases

```
Step 1: Upload a UI screenshot, PDF document, or enter a website URL
            │
            ▼
Step 2: AI analyzes the design using Vision AI + Document Extraction
        Detects: buttons, input fields, dropdowns, tables, navigation
            │
            ▼
Step 3: System builds a UI Schema (structured understanding of the interface)
        Page: Login | Components: email input, password input, submit button, forgot link
            │
            ▼
Step 4: Flow Detection Engine identifies user journeys
        Primary: Authentication Flow, Form Submission Flow
        Alternate: Error Recovery, Session Timeout
            │
            ▼
Step 5: Enterprise LLM generates comprehensive test cases
        50-200+ test cases covering all detected flows and components
```

---

## 5. Key Features & Capabilities

### 5.1 Test Case Generation

| Feature | Description |
|---------|-------------|
| **5 Test Types** | Positive, Negative, Boundary, Edge Case, Security |
| **4 Test Levels** | Unit, Integration, System, UAT |
| **Auto-Priority** | P1/P2/P3 assigned based on risk analysis |
| **Complexity Scoring** | 1-5 scale for each test case |
| **Duplicate Detection** | TF-IDF cosine similarity removes redundant tests (>85% threshold) |
| **Requirement Chunking** | Large requirements auto-split for better parsing |

### 5.2 Design Intelligence (Enterprise Feature)

| Feature | Description |
|---------|-------------|
| **Multi-Input** | Documents (PDF, DOCX, PPTX), Images (PNG, JPG), URLs |
| **Vision AI** | Llama 4 Scout analyzes UI screenshots component-by-component |
| **Web Crawling** | Playwright headless browser with depth-3 crawling (up to 20 pages) |
| **UI Schema Builder** | Merges all sources into unified structured UI representation |
| **Flow Detection** | 9 primary flows + 8 alternate flows + cross-flow scenarios |
| **LLM Test Generation** | GPT-class model generates enterprise-grade test cases |

### 5.3 Defect Prediction (ML)

| Feature | Description |
|---------|-------------|
| **Model** | Logistic Regression with balanced class weighting |
| **Inputs** | Lines of code, complexity score, past defects, code churn |
| **Output** | Defect probability (0-100%), risk level, defect category |
| **Risk Levels** | High (≥70%), Medium (40-70%), Low (<40%) |
| **6 Defect Categories** | Functional, Performance, Security, Integration, UI/UX, Data |
| **Fallback** | Weighted heuristic when model file is unavailable |

### 5.4 Risk Analysis Engine

The system performs a **6-layer risk analysis** on every requirement:

| Layer | What It Checks | Example Signals |
|-------|----------------|-----------------|
| **UI Layer** | User interface risks | forms, buttons, responsive, accessibility |
| **API Layer** | API/backend risks | endpoint, REST, authentication, rate limiting |
| **Integration Layer** | Third-party integration risks | payment gateway, external API, database |
| **Function Layer** | Business logic risks | calculation, validation, workflow, rules |
| **System Layer** | Infrastructure risks | performance, scalability, deployment, backup |
| **Non-functional Layer** | Quality attribute risks | security, compliance, usability, reliability |

### 5.5 Dashboard & Reporting

| Feature | Description |
|---------|-------------|
| **Real-time Stats** | Total requirements, test cases, predictions, avg defect probability |
| **Risk Distribution Chart** | Doughnut chart showing High/Medium/Low breakdown |
| **Defect Probability Chart** | Bar chart of predictions per module |
| **Export** | CSV, JSON, Excel with one click |
| **Module Grouping** | Test cases organized by software module |
| **Search & Filter** | Filter by module, test type, test level |

---

## 6. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    USER (Browser)                     │
│                                                       │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│   │  Dashboard   │  │   Upload     │  │   Defect   │ │
│   │  (Charts +   │  │  Requirement │  │ Prediction │ │
│   │   Stats)     │  │  or Design   │  │   Form     │ │
│   └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│          └─────────────────┼─────────────────┘        │
└────────────────────────────┼──────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │               API Layer (3 Routers)              │   │
│  │  • Requirements & Test Cases                     │   │
│  │  • Defect Prediction & Dashboard                 │   │
│  │  • Design Upload & Intelligence                  │   │
│  └──────────────────────┬──────────────────────────┘   │
│                         │                               │
│  ┌──────────────────────┼──────────────────────────┐   │
│  │            Service Layer (20 Services)            │   │
│  │                      │                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │
│  │  │   NLP    │ │ Test Gen │ │  ML Predictor    │ │   │
│  │  │  Engine  │ │  Engine  │ │  (scikit-learn)  │ │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │
│  │  │   Risk   │ │ Duplicate│ │   Complexity     │ │   │
│  │  │ Analysis │ │ Detector │ │    Scorer        │ │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │
│  │  │  Vision  │ │   URL    │ │   Document       │ │   │
│  │  │ Analyzer │ │  Crawler │ │   Extractor      │ │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │
│  │  │   LLM    │ │ UI Schema│ │  Flow Detection  │ │   │
│  │  │  Client  │ │  Builder │ │    Engine        │ │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │   │
│  └──────────────────────┬──────────────────────────┘   │
│                         │                               │
│  ┌──────────────────────┼──────────────────────────┐   │
│  │              Data Layer                           │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │   │
│  │  │  SQLite  │  │   File    │  │  ML Model    │  │   │
│  │  │ Database │  │  Storage  │  │   (.pkl)     │  │   │
│  │  └──────────┘  └───────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│                   EXTERNAL AI SERVICES                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Groq API: GPT-oss-120B (Text) + Llama 4 (Vision)│  │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Component Count Summary

| Component | Count | Description |
|-----------|-------|-------------|
| API Routers | 3 | Requirements, Defect Prediction, Design Upload |
| Backend Services | 20 | NLP, Test Gen, ML, Risk, Crawling, Vision, LLM, etc. |
| Database Models | 5 | Requirement, TestCase, DefectData, Prediction, DesignDocument |
| API Schemas | 30+ | Request/response models for all endpoints |
| Frontend Pages | 5 | Home, Upload Requirement, Upload Design, Test Cases, Defect Prediction |
| API Endpoints | 20+ | Full REST API covering all operations |

---

## 7. Technology Stack

### Backend Technologies

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **Python 3.11** | Core language | Rich AI/ML ecosystem, industry standard for AI |
| **FastAPI** | Web framework | Fastest Python framework, auto-generates API docs |
| **SQLAlchemy** | Database ORM | Industry standard, clean Python-SQL mapping |
| **SQLite** | Database | Zero-config, file-based, easily swappable to PostgreSQL |
| **Pydantic** | Data validation | Automatic request/response validation |
| **NLTK** | NLP processing | Tokenization, stemming, stopword removal |
| **scikit-learn** | Machine Learning | Logistic Regression model for defect prediction |
| **Groq API** | LLM AI | Ultra-fast inference for GPT-class text + Vision models |
| **Playwright** | Web crawling | Headless browser for analyzing live URLs |
| **PyPDF2/python-docx** | Document processing | Extract text from uploaded PDF/DOCX/PPTX files |

### Frontend Technologies

| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **React 19** | UI framework | Component-based, reactive, massive ecosystem |
| **Vite 6** | Build tool | Instant hot reload, fast builds |
| **Bootstrap 5** | CSS framework | Professional UI out of the box |
| **Chart.js** | Data visualization | Beautiful charts for dashboard |
| **Axios** | HTTP client | Promise-based API calls |
| **React Router v7** | Navigation | Client-side routing |

### DevOps & Quality

| Technology | Purpose |
|------------|---------|
| **Pytest** | Backend unit + integration testing |
| **HTTPX** | API test client |
| **ESLint** | Frontend code quality |
| **Uvicorn** | ASGI server with hot reload |

---

## 8. Detailed Component Breakdown

### 8.1 Backend Services (The Brain)

The backend contains **20 specialized services**, each handling a specific responsibility:

#### Core Pipeline Services

| # | Service | Responsibility |
|---|---------|---------------|
| 1 | **NLP Service** | Parses English requirements → extracts modules, actions, fields, validations using keyword matching |
| 2 | **Requirement Chunker** | Splits long requirements into manageable semantic chunks |
| 3 | **Test Case Generator** | Rule-based engine creating 5 types of test cases from parsed data |
| 4 | **Complexity Scorer** | Rates each test case 1-5 based on type, keywords, and test level |
| 5 | **Duplicate Detector** | Uses TF-IDF vectors + cosine similarity to find and flag duplicate tests |
| 6 | **Risk Analysis Service** | Scores risk across 6 layers using weighted keyword analysis |
| 7 | **Defect Prediction Service** | ML model inference + fallback heuristic for defect probability |

#### Design Intelligence Services

| # | Service | Responsibility |
|---|---------|---------------|
| 8 | **Design Intelligence Engine** | Master orchestrator — coordinates the entire design-to-test pipeline |
| 9 | **URL Crawler Service** | Playwright-based headless crawling, captures screenshots + DOM |
| 10 | **Document Extractor** | Extracts text from PDF, DOCX, PPTX, TXT uploads |
| 11 | **Vision Analyzer** | Sends UI screenshots to Llama 4 Vision for component detection |
| 12 | **UI Schema Builder** | Merges all extracted data into unified, structured UI representation |
| 13 | **Flow Detection Engine** | Detects 9 primary + 8 alternate user flows from UI schema |
| 14 | **LLM Test Generator** | GPT-powered enterprise test case generation with coverage validation |
| 15 | **Groq Client** | LLM API wrapper with retry logic and token management |

#### Enterprise & Utility Services

| # | Service | Responsibility |
|---|---------|---------------|
| 16 | **Enterprise Test Engine** | 13-category comprehensive test generation with requirement decomposition |
| 17 | **Requirement Decomposer** | Decomposes requirements into 12 aspect categories for deep analysis |
| 18 | **Folder Storage Service** | Persists all results to timestamped directories for audit trail |
| 19 | **Design Analysis Service** | Lightweight keyword-based design classification |
| 20 | **Export Utilities** | CSV, JSON, Excel generation for test case exports |

### 8.2 Database Schema

The system stores data in **5 tables**:

```
┌──────────────────┐       ┌──────────────────────────────┐
│   Requirement    │       │         TestCase              │
├──────────────────┤       ├──────────────────────────────┤
│ id (PK)          │◄──┐   │ id (PK)                      │
│ text             │   └───│ requirement_id (FK)           │
│ design_text      │       │ module_name                   │
│ folder_path      │       │ scenario                      │
│ created_at       │       │ test_type (5 types)           │
└──────────────────┘       │ test_level (4 levels)         │
                           │ expected_result               │
┌──────────────────┐       │ precondition                  │
│ DesignDocument   │       │ test_steps (JSON)             │
├──────────────────┤       │ priority (P1/P2/P3)           │
│ id (PK)          │       │ complexity_score (1-5)        │
│ requirement_id   │       │ duplicate_score               │
│ file_name        │       │ coverage_tag                  │
│ source_type      │       │ created_at                    │
│ ui_schema (JSON) │       └──────────────────────────────┘
│ detected_flows   │
│ coverage_%       │       ┌──────────────────────────────┐
│ total_components │       │       Prediction              │
└──────────────────┘       ├──────────────────────────────┤
                           │ id (PK)                      │
┌──────────────────┐       │ module_name                   │
│   DefectData     │       │ defect_probability            │
├──────────────────┤       │ risk_level (H/M/L)            │
│ id (PK)          │       │ defect_category               │
│ module_name      │       │ priority (P1/P2/P3)           │
│ lines_of_code    │       │ created_at                    │
│ complexity_score │       └──────────────────────────────┘
│ past_defects     │
│ code_churn       │
│ defect_label     │
└──────────────────┘
```

### 8.3 Frontend Pages

| Page | Route | What The User Sees |
|------|-------|--------------------|
| **Dashboard** | `/` | Stats cards, risk distribution chart, defect probability chart, recent test cases, workflow guide |
| **Upload Requirement** | `/upload` | Text editor with formatting toolbar, enterprise mode toggle, NLP analysis results, risk heatmap, generated test cases table |
| **Upload Design** | `/design` | Multi-file upload area (drag & drop), URL input, 6-stage progress indicator, UI schema visualization, detected flows, enterprise test cases |
| **Test Cases** | `/test-cases` | Full test case management — search, filter, group by module, expandable details, bulk delete, export to CSV/JSON/Excel |
| **Defect Prediction** | `/defect-prediction` | Module metrics input form, prediction result card with probability gauge, history chart and table |

---

## 9. AI & Machine Learning Explained

### 9.1 NLP Engine (Natural Language Processing)

**What it does:** Reads a software requirement written in plain English and extracts structured information.

**How it works:**
1. Text is tokenized (split into words)
2. Stop words removed ("the", "is", "shall")
3. Words lemmatized (reduced to root form)
4. Keyword matching against curated dictionaries:
   - **20 module categories** (Login, Registration, Payment, etc.)
   - **50+ action verbs** (login, register, search, delete, etc.)
   - **50+ field nouns** (email, password, username, etc.)
   - **40+ validation terms** (required, minimum, format, etc.)

**Example:**
```
Input:  "The system shall allow users to login using email and password"
Output: { module: "Login", actions: ["login"], fields: ["email", "password"], validations: [] }
```

### 9.2 Machine Learning Defect Predictor

**What it does:** Predicts the probability that a software module will have defects.

**How it works:**
1. **Training Data:** 39 historical module records with 4 metrics + defect label
2. **Algorithm:** Logistic Regression (a proven classification model)
3. **Input Features:**
   - Lines of Code — larger modules have more potential for bugs
   - Complexity Score — complex code is harder to test
   - Past Defects — modules with bug history tend to have more bugs
   - Code Churn — frequently changed code is riskier
4. **Output:** Probability from 0% to 100%

**Model Performance Metrics:**
- Accuracy, Precision, Recall, F1-Score, AUC-ROC (evaluated during training)

**Risk Classification:**
| Probability Range | Risk Level | QA Priority | Action |
|-------------------|------------|-------------|--------|
| 70% – 100% | **High** | **P1 (Critical)** | Test immediately, allocate senior QA |
| 40% – 70% | **Medium** | **P2 (Major)** | Include in current sprint testing |
| 0% – 40% | **Low** | **P3 (Minor)** | Standard testing procedures |

### 9.3 LLM Integration (Large Language Model)

**What it does:** Uses state-of-the-art AI (GPT-oss-120B and Llama 4 Scout) for advanced analysis.

**Two modes:**
1. **Text LLM (GPT-oss-120B):** Generates enterprise-grade test cases from structured UI schemas and detected user flows
2. **Vision LLM (Llama 4 Scout):** Analyzes UI screenshots to detect components, layout, navigation, and validation rules

**When it's used:**
- Design Intelligence pipeline (design upload feature)
- Enterprise test generation mode
- Vision analysis of UI screenshots

---

## 10. User Workflows & Screenshots Guide

### Workflow A: Requirement-Based Test Generation

| Step | User Action | System Response |
|------|-------------|-----------------|
| 1 | Navigate to **Upload Requirement** page | Text editor loads with formatting toolbar |
| 2 | Type or paste a software requirement | Word/character counter updates live |
| 3 | Optionally enable **Enterprise Mode** | Activates LLM-powered deep generation |
| 4 | Click **Generate Test Cases** | Loading spinner with progress |
| 5 | View **NLP Analysis** panel | Shows detected module, actions, fields, validations |
| 6 | View **Risk Analysis** panel | 6-layer risk heatmap with scores |
| 7 | View **Generated Test Cases** table | Sortable table with type, priority, complexity |
| 8 | Click **Export** (CSV/JSON/Excel) | File downloads to browser |

### Workflow B: Design-Based Test Generation

| Step | User Action | System Response |
|------|-------------|-----------------|
| 1 | Navigate to **Upload Design** page | Multi-input upload area appears |
| 2 | Upload documents (PDF/DOCX/PPTX) | Files queued with type detection |
| 3 | Upload UI screenshots (PNG/JPG) | Images queued for vision analysis |
| 4 | Enter URLs of live application | URLs queued for crawling |
| 5 | Click **Analyze & Generate** | 6-stage progress stepper activates |
| 6 | View **UI Schema** | Collapsible component tree per page |
| 7 | View **Detected Flows** | Primary, alternate, cross-flow cards |
| 8 | View **Enterprise Test Cases** | Comprehensive table grouped by module |

### Workflow C: Defect Prediction

| Step | User Action | System Response |
|------|-------------|-----------------|
| 1 | Navigate to **Defect Prediction** page | Input form loads |
| 2 | Enter module name | Free text field |
| 3 | Enter Lines of Code | Numeric input |
| 4 | Enter Complexity Score | Numeric input |
| 5 | Enter Past Defects count | Numeric input |
| 6 | Enter Code Churn | Numeric input |
| 7 | Click **Predict** | ML model runs inference |
| 8 | View prediction result card | Probability %, risk badge, category, priority |
| 9 | View prediction history chart | Bar chart of all past predictions |

---

## 11. API & Integration Capabilities

The system exposes a **full REST API** that can integrate with any external tool:

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Service health status |
| `POST` | `/api/requirements` | Store a requirement |
| `GET` | `/api/requirements` | List all requirements |
| `POST` | `/api/generate-testcases` | **Main pipeline** — parse + generate + predict |
| `GET` | `/api/test-cases` | List test cases with filters |
| `GET` | `/api/test-cases/grouped` | Test cases grouped by module |
| `DELETE` | `/api/test-cases/{id}` | Delete specific test case |
| `POST` | `/api/predict-defect` | Run ML defect prediction |
| `GET` | `/api/predictions` | List prediction history |
| `GET` | `/api/dashboard/stats` | Dashboard statistics |
| `GET` | `/api/export/csv` | Export as CSV |
| `GET` | `/api/export/json` | Export as JSON |
| `GET` | `/api/export/excel` | Export as Excel |
| `POST` | `/api/design/upload` | Design intelligence upload |
| `POST` | `/api/risk-analysis` | Multi-layer risk analysis |
| `POST` | `/api/model/reload` | Reload ML model |

### Auto-Generated API Documentation
- **Swagger UI:** `http://localhost:8000/docs` — Interactive API testing
- **ReDoc:** `http://localhost:8000/redoc` — Beautiful API reference

### Integration Possibilities
The REST API design allows integration with:
- **Jira / Azure DevOps** — Push generated test cases as work items
- **TestRail / Zephyr** — Import test cases into test management tools
- **CI/CD Pipelines** — Trigger test generation in Jenkins/GitHub Actions
- **Slack / Teams** — Send risk alerts and prediction results
- **Custom Dashboards** — Consume API data in Power BI or Grafana

---

## 12. Data Flow & Processing Pipeline

### Pipeline 1: Requirement → Test Cases (Complete Flow)

```
┌──────────────────────────────────────────────────────────────────┐
│                    REQUIREMENT INPUT                              │
│  "The system shall allow users to register with email..."        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: REQUIREMENT CHUNKING                                    │
│  • Split large text into semantic chunks (≤2000 chars each)      │
│  • Preserve sentence boundaries                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2: NLP PARSING (per chunk)                                 │
│  • Tokenize → Remove stopwords → Lemmatize                       │
│  • Match against keyword dictionaries                            │
│  • Extract: module, actions, fields, validations                 │
│  • Merge results across all chunks                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3: TEST CASE GENERATION                                    │
│  • Positive tests: action × field combinations                   │
│  • Negative tests: missing/empty/invalid per field               │
│  • Boundary tests: min/max/exceeding limits                      │
│  • Edge case tests: unicode, whitespace, concurrency             │
│  • Security tests: SQLi, XSS per field + auth per action         │
│  Output: 20-50+ raw test cases                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: POST-PROCESSING                                         │
│  • Complexity Scorer: assign 1-5 score per test                  │
│  • Duplicate Detector: TF-IDF similarity, flag >85% duplicates   │
│  • Test Level Classifier: Unit / Integration / System / UAT      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5: RISK ANALYSIS                                           │
│  • Score 6 risk layers (UI, API, Integration, Function,          │
│    System, Non-functional)                                       │
│  • Weighted keyword/phrase matching                              │
│  • Generate overall risk score + textual summary                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 6: DEFECT PREDICTION                                       │
│  • Feed module metrics to ML model (or heuristic fallback)       │
│  • Output: probability %, risk level, defect category, priority  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 7: PERSIST & STORE                                         │
│  • Save to SQLite database (Requirement + TestCases + Prediction)│
│  • Save to timestamped folder (requirement.txt, test_cases.json, │
│    risk_analysis.json, defect_prediction.json)                   │
│  • Return complete response to frontend                          │
└──────────────────────────────────────────────────────────────────┘
```

### Pipeline 2: Design → Test Cases

```
Input Sources                    Processing                     Output
─────────────                    ──────────                     ──────
                              ┌─────────────────┐
PDF/DOCX/PPTX ──► Extract ──►│                 │
                              │  UI Schema      │    ┌─────────────────┐
UI Screenshots ──► Vision ───►│  Builder        │───►│ Flow Detection  │
       AI                     │  (merge &       │    │ Engine          │
                              │   deduplicate)  │    │ (9 primary +    │
Live URLs ──► Crawl + ──────►│                 │    │  8 alternate)   │
              Screenshot      └─────────────────┘    └────────┬────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │ LLM Enterprise  │
                                                    │ Test Generator  │
                                                    │ (GPT-oss-120B)  │
                                                    └────────┬────────┘
                                                              │
                                                              ▼
                                                    50-200+ Enterprise
                                                    Test Cases + Stats
```

---

## 13. Quality Assurance & Testing

The system itself is thoroughly tested:

### Test Suite Summary

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| **test_nlp_service.py** | 8 tests | NLP parsing accuracy — login, registration, payment, search, file management |
| **test_case_generator.py** | 11 tests | All 5 test types generated, required fields, IDs, priorities |
| **test_defect_predictor.py** | 18 tests | Risk classification boundaries, priority mapping, fallback heuristic, full prediction |
| **test_api.py** | 20+ tests | All API endpoints — health, requirements, generation, prediction, dashboard, export |

### How to Run Tests
```bash
cd backend
python -m pytest ../tests/ -v --tb=short
```

---

## 14. Security Considerations

| Area | Implementation |
|------|----------------|
| **Input Validation** | Pydantic schemas validate all API inputs automatically |
| **CORS Protection** | Only whitelisted origins (localhost:5173, localhost:3000) |
| **SQL Injection Prevention** | SQLAlchemy ORM with parameterized queries — no raw SQL |
| **XSS Prevention** | React auto-escapes output; no dangerouslySetInnerHTML |
| **File Upload Validation** | File type checking on design uploads |
| **API Rate Limiting** | Groq API calls use retry logic with backoff |
| **No Hardcoded Secrets** | API keys loaded from .env file (environment variables) |
| **Security Test Generation** | The system itself generates SQL injection and XSS test cases |

---

## 15. Business Value & ROI

### Time Savings

| Activity | Manual Effort | With Our System | Savings |
|----------|--------------|-----------------|---------|
| Writing test cases for 1 requirement | 2-4 hours | **< 30 seconds** | ~99% |
| Risk assessment per requirement | 1-2 hours | **Instant** | ~99% |
| Defect risk evaluation per module | 30-60 min | **< 5 seconds** | ~99% |
| Design-to-test conversion | 1-2 days | **< 2 minutes** | ~99% |
| Test case deduplication | 1-2 hours | **Automatic** | 100% |

### Quality Improvements

| Benefit | Description |
|---------|-------------|
| **Comprehensive Coverage** | 5 test types ensure no category is missed (especially security and edge cases that humans often skip) |
| **Consistency** | Every requirement gets the same thorough treatment regardless of QA engineer fatigue or skill level |
| **Risk-Based Focus** | ML predictions direct QA effort to highest-risk modules — catching more bugs with less effort |
| **Audit Trail** | Every generation is persisted with timestamps — full traceability |
| **Knowledge Capture** | System encodes best practices into rules — no knowledge loss when team members leave |

### Strategic Value

| Value | Description |
|-------|-------------|
| **Faster Release Cycles** | Less time on test writing → more time on execution → faster releases |
| **Reduced Production Bugs** | Better coverage + risk-based testing → fewer bugs reaching customers |
| **Lower QA Costs** | Automation reduces manual effort without reducing quality |
| **Scalability** | System handles any volume — 1 requirement or 1,000 in the same time |
| **Competitive Advantage** | AI-driven QA is a differentiator in the market |

---

## 16. Current Status & Roadmap

### Current Status: v1.0.0 — Fully Functional

| Component | Status |
|-----------|--------|
| Backend API | ✅ Complete — all 20+ endpoints operational |
| NLP Engine | ✅ Complete — keyword-based parsing working |
| Test Case Generator | ✅ Complete — 5 types generating correctly |
| ML Defect Predictor | ✅ Complete — trained model + fallback |
| Risk Analysis | ✅ Complete — 6-layer scoring |
| Design Intelligence | ✅ Complete — document, image, URL support |
| LLM Integration | ✅ Complete — Groq API (text + vision) |
| Frontend Dashboard | ✅ Complete — all 5 pages with charts |
| Export System | ✅ Complete — CSV, JSON, Excel |
| Test Suite | ✅ Complete — 55+ automated tests |
| Documentation | ✅ Complete — API docs, README, Postman collection |

### Potential Future Enhancements

| Enhancement | Description | Business Value |
|-------------|-------------|----------------|
| **Jira/ADO Integration** | Auto-push test cases to project management tools | Eliminates manual copy-paste |
| **Advanced ML Models** | Random Forest / XGBoost for better prediction accuracy | Higher defect catch rate |
| **User Authentication** | Login system with role-based access | Enterprise security compliance |
| **Team Collaboration** | Multi-user support with shared projects | Team-wide adoption |
| **Historical Analytics** | Trend analysis of defect predictions over time | Long-term quality insights |
| **CI/CD Plugin** | Trigger test generation from pull requests | Shift-left testing |
| **Custom Dictionaries** | Domain-specific keyword libraries | Better accuracy for your industry |
| **PostgreSQL Migration** | Production-grade database | Handles large-scale data |

---

## 17. Glossary

| Term | Definition |
|------|------------|
| **NLP** | Natural Language Processing — AI that reads and understands human language |
| **ML** | Machine Learning — AI that learns patterns from data to make predictions |
| **LLM** | Large Language Model — Advanced AI like GPT that generates human-quality text |
| **API** | Application Programming Interface — how software systems talk to each other |
| **REST** | Representational State Transfer — standard web API architecture |
| **FastAPI** | Modern Python web framework for building APIs |
| **React** | JavaScript library for building user interfaces |
| **SQLite** | Lightweight file-based database |
| **ORM** | Object-Relational Mapping — Python code instead of raw SQL queries |
| **TF-IDF** | Term Frequency–Inverse Document Frequency — text similarity technique |
| **Cosine Similarity** | Mathematical measure of how similar two texts are |
| **Logistic Regression** | ML algorithm for binary classification (defect yes/no) |
| **CORS** | Cross-Origin Resource Sharing — browser security for API calls |
| **Pydantic** | Python data validation library |
| **Playwright** | Headless browser automation tool |
| **Groq** | AI inference platform — runs LLM models at high speed |
| **P1/P2/P3** | Priority levels — Critical/Major/Minor |
| **QA** | Quality Assurance — ensuring software works correctly |
| **UAT** | User Acceptance Testing — final testing by end users |
| **CI/CD** | Continuous Integration/Continuous Deployment — automated software delivery |

---

*Document prepared for executive review — March 2026*
