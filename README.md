# MLOps Assignment 2: Rule-Based Churn Risk Prediction System

**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

## Project Overview
This repository contains a complete DevOps lifecycle implementation for a deterministic backend service that computes customer churn risk based on fixed business rules utilizing customer and ticket history. This forms Phase 1 of the overarching MLOps pipeline assignment.

## System Features
- **Data Preparation:** Synthetic generation of realistic ticket logs conditionally correlated with customer churn.
- **Feature Aggregation:** Time-windowed feature computation (7, 30, 90 days) and natural language sentiment tracking.
- **Rule Engine:** A deterministic scoring logic classifying churn risk as `HIGH`, `MEDIUM`, or `LOW`.
- **REST API:** FastAPI-based service providing endpoints for health checks, predictions, and metrics.
- **Testing Layer:** Unit tests and API integration tests verified through `pytest`.
- **Monitoring:** Prometheus integration for tracking request counts, latencies, and prediction volumes, visualized via Grafana.
- **Dockerized Environment:** Containerized application for consistent execution across environments.
- **CI/CD Pipeline:** GitHub Actions workflow for automated testing and continuous deployment of the Docker Image to DockerHub.

## Documentation
Comprehensive phase-by-phase documentation of the system's development can be found in the `docs/` directory:
- [Roadmap & Architecture](docs/roadmap.md)
- [Phases Summary](docs/phases.md)
- [Phase 1: Data Preparation](docs/phase_1_data_prep.md)
- [Phase 2: Feature Aggregation](docs/phase_2_feature_aggregation.md)
- [Phase 3: Rule Engine Implementation](docs/phase_3_rule_engine.md)
- [Phase 4: API Service](docs/phase_4_api_service.md)
- [Phase 5: Testing](docs/phase_5_testing.md)
- [Phase 6: Containerization](docs/phase_6_containerization.md)
- [Phase 7: CI/CD](docs/phase_7_ci_cd.md)
- [Phase 8: Monitoring](docs/phase_8_monitoring.md)
- [Phase 9: API Documentation](docs/api_documentation.md)

## How to Run

### 1. Local Execution
```bash
pip install -r requirements.txt
uvicorn src.app:app --reload
```
Access the API locally at: `http://localhost:8000/docs`

### 2. Docker Execution
```bash
docker build -t churn-risk-service .
docker run -p 8000:8000 churn-risk-service
```

### 3. Monitoring Stack (Prometheus + Grafana)
*Ensure the API is already running.*
```bash
cd monitoring
docker compose -f docker-compose.monitoring.yml up -d
```
- Prometheus Dashboard: `http://localhost:9090`
- Grafana Dashboard: `http://localhost:3000` (admin / admin)
