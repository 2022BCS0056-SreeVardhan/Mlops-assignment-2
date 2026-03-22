**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 1: Data Preparation Layer

**Objective:** Create a realistic telecom backend data environment.

**Tasks:**
* Download **Telco Customer Churn dataset**
* Clean dataset
* Extract required fields
* Generate **synthetic ticket logs**
* Store both datasets

**Outputs:**
```text
data/
   customers.csv
   tickets.csv
```

**Key fields from this phase:**
* `customer_id`
* `contract_type`
* `monthly_charges`
* `tenure`
* `tickets_last_30_days`
* `complaint_ticket`

**Purpose:**
The rule engine will consume **aggregated features**, not raw tickets.

---

# Phase 2: Feature Aggregation Layer

**Objective:** Convert raw ticket logs into usable behavioral features.

**Tasks:**
* Aggregate ticket history per customer
* Compute time-based metrics

**Features:**
* `tickets_last_7_days`
* `tickets_last_30_days`
* `tickets_last_90_days`
* `complaint_ticket`
* `negative_ratio`

**Output:**
```text
data/processed/customer_features.csv
```

**Example:**

| **customer_id** | **contract_type** | **monthly_charges** | **tenure** | **Churn** | **tickets_last_7_days** | **tickets_last_30_days** | **tickets_last_90_days** | **complaint_ticket** | **negative_ratio** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 7590-VHVEG | Month-to-month | 29.85 | 1 | No | 0.0 | 1.0 | 3.0 | 0.0 | 0.0 |

**Purpose:**
The Rule Engine should consume structured features for deterministic decision making.

---

# Phase 3: Rule Engine Implementation

**Objective:** Build the churn risk scoring logic.

**Tasks:**
* Implement rule-based scoring
* Define risk categories

**Rules:**
* `tickets_last_30_days > 5` → **HIGH**
* `contract == "Month-to-month" AND complaint == 1` → **HIGH**
* `tickets_last_30_days >= 3` → **MEDIUM**
* `else` → **LOW**

**Output:**
* `risk_category` (HIGH, MEDIUM, LOW)

**Purpose:**
This replaces ML inference in Stage 1, providing a transparent and explainable baseline.

---

# Phase 4: API Service Layer

**Objective:** Expose the rule engine through a microservice.

**Tasks:**
* Build REST API using FastAPI
* Define request schema (Pydantic)
* Return prediction response

**Endpoint:**
`POST /predict-risk`

**Input:**
```json
{
  "customer_id": "7590-VHVEG"
}
```

**Output:**
```jsonjson
{
  "customer_id": "7590-VHVEG",
  "risk_category": "LOW"
}
```

**Technology:**
* **FastAPI**
* Generates automatic **Swagger documentation** at `/docs`.

---

# Phase 5: Testing Layer

**Objective:** Verify the system works correctly.

**Tasks:**
* Unit tests for rule engine logic
* API integration tests
* Input validation tests

**Tools:**
* `pytest`

**Tests validate:**
* HIGH/MEDIUM/LOW risk logic accuracy
* Handling of non-existent customers (404)
* API health and latency

---

# Phase 6: Containerization

**Objective:** Package the service into a deployable unit.

**Tasks:**
* Create `Dockerfile`
* Install dependencies from `requirements.txt`
* Expose port 8000
* Run FastAPI server using Uvicorn

**Outputs:**
* **Docker Image**

**Example Run:**
```bash
docker build -t churn-risk-service .
docker run -p 8000:8000 churn-risk-service
```

**Purpose:**
Ensure consistent execution across development, testing, and production environments.

---

# Phase 7: CI/CD Pipeline

**Objective:** Automate build and testing workflows.

**Tasks:**
1. Clone repository
2. Install dependencies
3. Run `pytest`
4. Build Docker image
5. (Optional) Push to Registry

**Technology:**
* **GitHub Actions**

**Trigger:**
* `on: [push]` to main branch

**Output:**
* Automated build verification and deployment readiness.

---

# Phase 8: Logging and Monitoring

**Objective:** Observe system behavior in production.

**Logging:**
* Request/Response logs
* Prediction audit logs
* Error/Exception tracking

**Monitoring Metrics:**
* `api_request_count`
* `prediction_count`
* `api_request_latency_seconds`

**Tools:**
* **Prometheus** (Metrics collection)
* **Grafana** (Visualization dashboards)

---

# Phase 9: Documentation

**Objective:** Define the API lifecycle and project structure.

**Include:**
* Installation guides
* API Reference
* Architecture diagrams
* Performance benchmarks
