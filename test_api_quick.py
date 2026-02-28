"""Quick API smoke test."""
import httpx

BASE = "http://localhost:8000"

# 1. Test case generation
print("=== Test Case Generation ===")
r = httpx.post(f"{BASE}/api/generate-testcases", json={
    "requirement_text": "The system shall allow users to login using their email and password. The email must be in a valid format and the password is required."
})
data = r.json()
print(f"Module: {data['parsed']['module']}")
print(f"Actions: {data['parsed']['actions']}")
print(f"Fields: {data['parsed']['fields']}")
print(f"Validations: {data['parsed']['validations']}")
print(f"Total test cases: {len(data['test_cases'])}")
print()

# 2. Defect prediction
print("=== Defect Prediction ===")
r = httpx.post(f"{BASE}/api/predict-defect", json={
    "module_name": "Payment",
    "lines_of_code": 4200,
    "complexity_score": 42.0,
    "past_defects": 18,
    "code_churn": 250,
})
pred = r.json()
print(f"Module: {pred['module_name']}")
print(f"Probability: {pred['defect_probability']}")
print(f"Risk Level: {pred['risk_level']}")
print()

# 3. Dashboard stats
print("=== Dashboard Stats ===")
r = httpx.get(f"{BASE}/api/dashboard/stats")
stats = r.json()
print(f"Total Requirements: {stats['total_requirements']}")
print(f"Total Test Cases: {stats['total_test_cases']}")
print(f"Total Predictions: {stats['total_predictions']}")
print()

print("All API tests passed!")
