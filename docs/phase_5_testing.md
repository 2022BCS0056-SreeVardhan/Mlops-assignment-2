**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 5: Testing Layer

## Objective

Verify that the underlying system logic, API routing, and error handling mechanisms work correctly and reliably. 

**Tasks:**
- Develop unit tests for the Rule Engine logic.
- Develop integration tests for the FastAPI service.
- Validate input handling, specifically edge cases and invalid data.

**Tools utilized:**
- `pytest`
- `httpx` (for FastAPI `TestClient`)

**Testing Scenarios:**
- HIGH risk classification logic
- MEDIUM risk classification logic
- LOW risk classification logic
- API health checks
- Invalid request handling (e.g., 404 Not Found)

---

## Step 01: Install Test Dependencies

To execute the test suite, we need to add `pytest` and `httpx` to our dependencies.

Update `requirements.txt`:
```text
fastapi
uvicorn
pandas
pydantic
pytest
httpx
```

Run installation:
```bash
pip install -r requirements.txt
```

---

## Step 02: Define the Testing Directory Structure

A standardized `tests/` directory is created at the root level alongside `src/` and `data/`.

![Project File Structure](../images/10_file-structure.png)

*Directory layout containing test scripts and configurations.*

---

## Step 03: Unit Testing the Rule Engine

We write targeted unit tests to validate the deterministic rules applied to various customer profiles.

```python
# tests/test_rule_engine.py

from src.rule_engine import compute_risk

def test_high_risk_many_tickets():
    """
    Tests rule: tickets_last_30_days > 5 → HIGH risk
    """
    row = {
        "contract_type": "Month-to-month",
        "tickets_last_30_days": 7,
        "complaint_ticket": 0
    }
    assert compute_risk(row) == "HIGH"

def test_high_risk_complaint_monthly_contract():
    """
    Tests rule: month-to-month contract + complaint ticket → HIGH risk
    """
    row = {
        "contract_type": "Month-to-month",
        "tickets_last_30_days": 2,
        "complaint_ticket": 1
    }
    assert compute_risk(row) == "HIGH"

def test_medium_risk():
    """
    Tests rule: tickets_last_30_days >= 3 → MEDIUM risk
    """
    row = {
        "contract_type": "Two year",
        "tickets_last_30_days": 3,
        "complaint_ticket": 0
    }
    assert compute_risk(row) == "MEDIUM"

def test_low_risk():
    """
    Tests rule fallback: otherwise → LOW risk
    """
    row = {
        "contract_type": "Two year",
        "tickets_last_30_days": 1,
        "complaint_ticket": 0
    }
    assert compute_risk(row) == "LOW"

def test_high_rule_boundary():
    """
    Boundary condition: exactly 5 tickets does NOT trigger HIGH risk.
    Should fall back to MEDIUM (>= 3).
    """
    row = {
        "contract_type": "Two year",
        "tickets_last_30_days": 5,
        "complaint_ticket": 0
    }
    assert compute_risk(row) == "MEDIUM"

def test_rule_precedence():
    """
    Verifies that HIGH risk conditions supersede MEDIUM risk conditions.
    """
    row = {
        "contract_type": "Month-to-month",
        "tickets_last_30_days": 3,
        "complaint_ticket": 1
    }
    assert compute_risk(row) == "HIGH"

def test_complaint_not_monthly():
    """
    Verifies that a complaint alone does NOT trigger HIGH risk if 
    contract type is not month-to-month.
    """
    row = {
        "contract_type": "Two year",
        "tickets_last_30_days": 2,
        "complaint_ticket": 1
    }
    assert compute_risk(row) == "LOW"
```

---

## Step 04: Integration Testing the API

We utilize FastAPI's `TestClient` to mock HTTP requests against our endpoints without starting a live server.

```python
# tests/test_api.py

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health_check():
    """Validates the health endpoint is active."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "service running"

def test_predict_risk_valid_customer():
    """Validates the API successfully computes risk for a known customer."""
    response = client.post(
        "/predict-risk",
        json={"customer_id": "7590-VHVEG"}
    )
    assert response.status_code == 200
    assert "risk_category" in response.json()

def test_predict_risk_invalid_customer():
    """Validates proper error handling (404) for unknown customers."""
    response = client.post(
        "/predict-risk",
        json={"customer_id": "INVALID-ID"}
    )
    assert response.status_code == 404
```

### Configuration (`pytest.ini`)
To ensure Pytest resolves the `src` module paths correctly from the project root:

```ini
# pytest.ini
[pytest]
pythonpath = .
```

---

## Step 05: Execution and Results

Execute the complete test suite from the project root directory:

```bash
pytest
```

![Test Passing Output](../images/11_tests-pass.png)

**Results:**
All 10 tests (7 Rule Engine + 3 API tests) passed successfully. The system behaves exactly as designed under normal, boundary, and erroneous conditions.