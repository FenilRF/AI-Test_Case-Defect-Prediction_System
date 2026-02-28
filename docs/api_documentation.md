# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required (open API for development).

---

## Endpoints

### Health Check

#### `GET /`
Returns application status.

**Response:**
```json
{
  "status": "healthy",
  "app": "AI Test Case & Defect Prediction System",
  "version": "1.0.0"
}
```

---

### Requirements

#### `POST /api/requirements`
Store a new requirement.

**Request Body:**
```json
{
  "text": "The system shall allow users to login..."
}
```

**Response (201):**
```json
{
  "id": 1,
  "text": "The system shall allow users to login...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `GET /api/requirements`
List all requirements.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 500)

#### `GET /api/requirements/{req_id}`
Get a single requirement by ID.

---

### Test Case Generation

#### `POST /api/generate-testcases`
Parse requirement and generate test cases.

**Request Body:**
```json
{
  "requirement_text": "The system shall allow users to login using email and password. Email must be valid format and password is required."
}
```

**Response (200):**
```json
{
  "requirement_id": 1,
  "parsed": {
    "module": "Login",
    "actions": ["login"],
    "fields": ["email", "password"],
    "validations": ["required", "format"]
  },
  "test_cases": [
    {
      "test_id": 1,
      "module_name": "Login",
      "scenario": "Verify that login succeeds with valid email",
      "test_type": "positive",
      "expected_result": "Login operation completes successfully",
      "priority": "P2"
    }
  ]
}
```

#### `GET /api/test-cases`
List all stored test cases.

**Query Parameters:**
- `requirement_id` (int, optional) — filter by requirement
- `test_type` (string, optional) — filter by type (positive/negative/boundary/edge/security)
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)

#### `GET /api/test-cases/export/csv`
Download test cases as CSV file.

#### `GET /api/test-cases/export/json`
Download test cases as JSON file.

---

### Defect Prediction

#### `POST /api/predict-defect`
Predict defect probability for a module.

**Request Body:**
```json
{
  "module_name": "Payment",
  "lines_of_code": 4200,
  "complexity_score": 42.0,
  "past_defects": 18,
  "code_churn": 250
}
```

**Response (200):**
```json
{
  "module_name": "Payment",
  "defect_probability": 0.82,
  "risk_level": "High"
}
```

#### `GET /api/predictions`
List all prediction history.

---

### Dashboard

#### `GET /api/dashboard/stats`
Get aggregated statistics.

**Response:**
```json
{
  "total_requirements": 5,
  "total_test_cases": 120,
  "total_predictions": 8,
  "high_risk_modules": 3,
  "medium_risk_modules": 2,
  "low_risk_modules": 3
}
```

---

### Model Management

#### `POST /api/model/reload`
Force-reload the ML model from disk.

**Response:**
```json
{
  "message": "Model reloaded successfully"
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400` — Bad Request (validation error)
- `404` — Not Found
- `422` — Unprocessable Entity (schema validation)
- `500` — Internal Server Error
