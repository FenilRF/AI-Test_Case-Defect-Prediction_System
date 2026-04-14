**AI-Based Test Case Generation & Defect Prediction System:**

This document outlines the **AI-Based Test Case Generation & Defect Prediction System**, an internally developed AI-powered web application designed to **automate and optimize software quality assurance (QA)**.

The system addresses critical bottlenecks in the QA process by focusing on two primary functions:

1. **Automated Test Case Generation:** Instantly creates comprehensive test scenarios from requirements or designs, eliminating up to 60% of manual test writing time.  
2. **AI Defect Prediction:** Uses Machine Learning to predict modules most likely to contain defects, enabling QA teams to prioritize effort and catch critical bugs earlier.

**Value Proposition (in one sentence):** You provide a software requirement or design, and the system immediately generates a professional, risk-prioritized test suite while highlighting the parts of your code at the highest risk of failure.

| Metric | Value |
| ----- | ----- |
| **Automation Focus** | Test Case Generation & Defect Prediction |
| **Risk Layers Analyzed** | 6 (UI, API, Integration, Function, System, Non-functional) |
| **Test Case Types** | 5 (Positive, Negative, Boundary, Edge Case, Security) |
| **Core AI Models** | NLP Parser, ML Defect Predictor, LLM (GPT/Llama) |

**The Business Problem & Impact**

Current software QA is plagued by manual effort and inconsistent quality, leading to high-cost production bugs.

| Problem | Impact on Business |
| ----- | ----- |
| **Manual Test Case Writing** | QA engineers spend **40-60% of their time** writing tests, diverting resources from actual testing. |
| **Test Coverage Gaps** | Human oversight misses edge cases and security scenarios, resulting in **up to 40% of software defects**. |
| **Lack of Prioritization** | Teams test all modules equally, wasting time on low-risk areas. |
| **Late Defect Discovery** | Bugs found in production cost **10-100x more** to fix than those caught during testing. |

**Our AI-Driven Solution**

The system is built on a full-stack web application utilizing three distinct layers of Artificial Intelligence to solve the problems identified above:

| AI Layer | Function | Core Responsibility |
| ----- | ----- | ----- |
| **Layer 1: NLP Engine** | **Natural Language Processing** | Reads requirements (plain English) and automatically extracts structured data: modules, actions, fields, and validation rules. |
| **Layer 2: Intelligent Test Case Generator** | **Rule-Based & LLM Generation** | Generates 5 types of test cases (Positive, Negative, Boundary, Edge Case, Security) from the structured data. |
| **Layer 3: ML Defect Predictor** | **Machine Learning** | Trained on historical data to predict the **probability (0-100%)** of a module having defects, classifying risk as High/Medium/Low and assigning QA Priority (P1-P3). |
| **Bonus: Design Intelligence** | **Vision AI & Web Crawling** | Accepts UI screenshots, documents (PDF/DOCX), and live URLs. Uses **Llama 4 Scout Vision AI** to analyze designs and generate test cases directly from the interface elements. |

**Key Workflows (Non-Technical)**

**Workflow 1: Requirement → Test Cases**

1. **Input:** QA Engineer pastes a requirement (e.g., "The system shall allow users to register with name, email, and password.").  
2. **AI Analysis:** NLP Engine parses the text, identifying the **Registration Module**, **fields** (name, email, password), and **validations** (valid email format, min password length).  
3. **Generation:** System automatically creates **20-50+ test cases** (e.g., Happy Path, Empty Field Error, Boundary Test).  
4. **Risk & Prediction:** Risk Analysis scores the requirement across 6 layers (e.g., **Security Risk: 0.8 (High)**). Defect Predictor estimates probability (e.g., **67% defect probability** → **P2 Priority**).  
5. **Output:** Export the prioritized test cases to CSV, JSON, or Excel.

**Workflow 2: Design → Test Cases**

1. **Input:** Upload UI screenshot, PDF design document, or live website URL.  
2. **Vision AI Analysis:** Llama 4 Scout analyzes the image/DOM to detect components (buttons, inputs, tables).  
3. **Schema & Flow Detection:** The system builds a structured UI Schema and identifies **user journeys** (e.g., Authentication Flow, Form Submission Flow).  
4. **Generation:** Enterprise LLM (GPT-oss-120B) generates a comprehensive suite of **50-200+ enterprise-grade test cases** covering all detected flows and components.

**Technology & Integration SummaryCore Technology Stack**

| Technology | Purpose |
| ----- | ----- |
| **Backend** | **Python 3.11** (Core Language), **FastAPI** (Web Framework), **scikit-learn** (ML Model: Logistic Regression), **Groq API** (LLM AI Client), **Playwright** (Web Crawling) |
| **Frontend** | **React 19** (UI Framework), **Chart.js** (Data Visualization) |
| **Database** | **SQLite** (Initial database, easily swappable), **SQLAlchemy** (ORM) |

