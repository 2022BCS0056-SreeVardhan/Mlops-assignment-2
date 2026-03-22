**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 9: API Documentation

## Churn Risk Prediction API

Rule-based churn risk prediction microservice built using FastAPI.  
The service evaluates customer churn risk using contract type and ticket history.

---

## Base URL

http://localhost:8000

**Swagger UI (interactive API documentation):**  
http://localhost:8000/docs

**OpenAPI specification:**  
http://localhost:8000/openapi.json

---

## 1. Health Check

### Endpoint

```http
GET /
```

### Description

Verifies that the service is running and accessible.

### Response

**200 OK**

```json
{
  "status": "service running"
}
```

---

## 2. Predict Churn Risk

### Endpoint

```http
POST /predict-risk
```

### Description

Computes churn risk category for a given customer using:

* Contract type
* Ticket frequency (last 30 days)
* Complaint presence
* Negative sentiment ratio

### Request Body

```json
{
  "customer_id": "7590-VHVEG"
}
```

### Successful Response

**200 OK**

```json
{
  "customer_id": "7590-VHVEG",
  "risk_category": "LOW"
}
```

### Risk Categories

* `LOW`
* `MEDIUM`
* `HIGH`

---

## 3. Error Responses

### 404 — Customer Not Found

Returned when the provided `customer_id` does not exist in the processed dataset.

```json
{
  "detail": "Customer not found"
}
```

---

### 422 — Invalid Request Payload

Returned when the request body:

* Is missing required fields
* Has incorrect field names
* Has incorrect data types

Example invalid request:

```json
{}
```

---

## 4. Metrics Endpoint

### Endpoint

```http
GET /metrics
```

### Description

Exposes application metrics in Prometheus format for monitoring and observability.  
This endpoint is intended for scraping by Prometheus and should not be used directly by clients.

### Example Metrics

* `prediction_count_total`
* `api_request_count_total`
* `api_request_latency_seconds`
* `process_cpu_seconds_total`
* `process_resident_memory_bytes`

---

## 5. Observability Architecture

The service integrates with a monitoring stack:

```text
FastAPI Service
      ↓
/metrics endpoint
      ↓
Prometheus (metrics collection)
      ↓
Grafana (dashboard visualization)
```

Monitoring provides:

* Total prediction count
* Request rate
* API latency
* System resource usage

---

## 6. Deployment

The service is:

* Containerized using Docker
* Built and pushed automatically via CI/CD
* Published to DockerHub
* Deployable using Docker or Docker Compose

To run locally:

```bash
docker build -t churn-risk-service .
docker run -p 8000:8000 churn-risk-service
```

---

## 7. Version

Current API Version:

```text
1.0
```