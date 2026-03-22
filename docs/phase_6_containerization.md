**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 6: Containerization

## Objective

Package the service and its dependencies into a deployable container unit to guarantee consistent execution across all environments (development, testing, staging, and production).

**Outputs:**
- `Dockerfile`
- `.dockerignore`
- Built Docker Image (`churn-risk-service`)

---

## Step 01: Create the Dockerfile

We define the exact environment the application requires to run using a `Dockerfile` placed in the project root. We use a lightweight Python 3.12 slim image to minimize the final image size.

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose API port
EXPOSE 8000

# Start FastAPI server via Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"] 
```

---

## Step 02: Configure .dockerignore

To prevent unnecessary files (like local testing artifacts or virtual environments) from bloating the Docker image, we configure a `.dockerignore` file.

```text
# .dockerignore

# Python cache
__pycache__/
*.pyc
*.pyo

# virtual environment
.venv/

# pytest artifacts
.pytest_cache/

# git
.git
.gitignore

# notebooks
notebooks/

# development scripts
scripts/

# tests (not needed in runtime container)
tests/

# editor configs
.vscode/

# OS files
.DS_Store
```

---

## Step 03: Build the Docker Image

Execute the docker build command in the terminal from the project root directory.

```bash
docker build -t churn-risk-service .
```

![Docker Build Command Output](../images/12_docker-build.png)

*The image builds successfully, leveraging cache where appropriate.*

---

## Step 04: Run the Container

Run the newly built image, mapping the container's internal port 8000 to the host machine's port 8000.

```bash
docker run -p 8000:8000 churn-risk-service
```

![Docker Run Command Output](../images/13_docker-run.png)

The container spins up and the Uvicorn server starts.

**Accessing the Service:**
The API is now accessible locally via the container. You can view the automatically generated Swagger UI documentation at:
`http://localhost:8000/docs#/`

![Swagger UI from Container](../images/14_docker-run-website.png)

---

## Step 05: Verify API Functionality Inside the Container

We perform integration tests against the containerized API via the Swagger UI to ensure the routing, logic, and error handling remain intact after containerization.

### Test A: Health Check
Testing the root `GET /` endpoint.

![Health Check](../images/15_test-get-end-point.png)

**Result:** `200 OK`, returning `{"status": "service running"}`.

### Test B: Valid Prediction Request
Testing `POST /predict-risk` with a valid customer payload: `{"customer_id": "7590-VHVEG"}`

![Valid Prediction Request](../images/16_test_post-end-point-valid.png)

**Result:** `200 OK`, successfully predicting Risk: `LOW`.

### Test C: Invalid Customer (Not Found)
Testing `POST /predict-risk` with an unknown customer code.

![Invalid Customer Not Found](../images/17_test_post-end-point-invalid.png)

**Result:** `404 Not Found`, returning error details `"Customer not found"`.

### Test D: Invalid Payload Type
Testing `POST /predict-risk` with an improper input data type (sending an integer instead of a string).

![Invalid Input Data Type](../images/18_test_post-end-point-invalid-input.png)

**Result:** `422 Unprocessable Entity`, triggering Pydantic validation error indicating a valid string is expected.

---
**Status:** We have successfully verified via Docker that our application behaves deterministically and handles errors properly, completely independent of the host system's configuration.