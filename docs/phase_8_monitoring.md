**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 8: Logging and Monitoring

## Objective

Implement a robust observability layer to monitor system behavior in production. This ensures we can track system health, debug issues, and analyze usage patterns over time.

**Logging:**
- Request logs
- Prediction audit logs
- Error logs

**Monitoring Metrics:**
- `request_count` (API usage)
- `prediction_count` (Business usage)
- `latency` (Performance)

**Technology Stack:**
- **Python `logging`** (Structured logs)
- **Prometheus** (Metrics aggregation & Time-Series DB)
- **Grafana** (Visualization Dashboard)

---

## Step 01: Implement Structured Logging in the API

We update `src/app.py` to use Python's built-in `logging` module to track the application lifecycle, dataset loading, and incoming requests.

*(Code for logging implementation is integrated within `src/app.py`)*

Start the application locally and observe the terminal output.

![Proper logging output](../images/33_proper-logging.png)

*The terminal displays structured logs for dataset loading, health checks, and prediction requests.*

---

## Step 02: Implement Prometheus Metrics

We install the `prometheus-client` to instrument our FastAPI application with custom metrics.

```bash
pip install prometheus-client
```

*(Ensure `prometheus-client` is added to `requirements.txt`)*

We update `src/app.py` to track `Counter` and `Histogram` metrics and expose them via a new `/metrics` endpoint.

---

## Step 03: Verify Metrics Locally

Start the server and check the `/metrics` endpoint before making any predictions.

![Metrics Status Before Predictions](../images/34_status-before.png)

*Initial state showing baseline metric structure.*

Make a successful prediction request:
![Post Request Call](../images/35_post-request-call.png)

Observe the updated metrics at `/metrics`:
![API Request Count Increased](../images/36_api-request-count-increased.png)
![Proper Logging of Metric Updates](../images/37_proper-logging.png)

*The `api_request_count` and `prediction_count` have incremented, and request latency has been recorded in the histogram buckets.*

**CI/CD Verification:**
Push the logging and monitoring code to GitHub to ensure it passes the CI/CD pipeline.
![CI Success](../images/38_github-actions-ci.png)
![CD Success](../images/39_dockerhub-cd.png)

---

## Step 04: Build the Monitoring Stack (Prometheus & Grafana)

Instead of manually reading raw text metrics, we deploy Prometheus to scrape the data periodically and Grafana to visualize it.

Create a `monitoring/` directory and add `prometheus.yml`:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "churn-risk-service"
    metrics_path: /metrics
    static_configs:
      - targets: ["host.docker.internal:8000"] # Use host.docker.internal to reach local app from container
```
![Add Prometheus Config](../images/40_add-prometheus-monitoring.png)

Create `docker-compose.monitoring.yml` to orchestrate the monitoring containers:

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```
![Add Docker Compose](../images/41_add-docker-compose-monitoring.png)

---

## Step 05: Start the Monitoring Stack

Ensure the FastAPI app is running on host `0.0.0.0`.
![Metrics Endpoint Added](../images/42_added-metrics-endpoint.png)

From the `monitoring` directory, start the stack:
```bash
docker compose -f docker-compose.monitoring.yml up -d
```
![Run Monitoring Stack](../images/43_run-monitoring.png)
![Successful Monitoring Run](../images/44_successfuly-ran-monitoring.png)

---

## Step 06: Verify Prometheus Data Collection

Access Prometheus at `http://localhost:9090`.

![Check Prometheus UI](../images/45_check-prometheus.png)

Execute a query (e.g., `prediction_count_total`) to confirm Prometheus is successfully scraping the FastAPI metrics endpoint.
![Query in Prometheus](../images/46_query-in-prometheus.png)

---

## Step 07: Configure Grafana Dashboard

Access Grafana at `http://localhost:3000` (Default login: admin/admin).
![Grafana Login](../images/47_grafna-login-page.png)
![Grafana Home](../images/48_grafna-after_login.png)

**Connect Prometheus Data Source:**
1. Navigate to Connections → Data Sources.
   ![Grafana Data Sources](../images/49_grafna-data-sources.png)
2. Add Prometheus and set the connection URL to `http://prometheus:9090`.
   ![Data Source Prometheus Config](../images/50_data-source-prometheus.png)
3. Save & Test to verify the connection.
   ![Saving Data Source](../images/51_saving-data-source.png)

**Create Dashboards:**
1. Create a new visualization panel for `prediction_count_total`.
   ![No Data Initially](../images/52_no-data-inbeginning.png)
2. Generate API traffic and refresh. The visualization will update with live data.
   ![Data Retrieved](../images/53_data-retrieved.png)
3. Add complex queries, such as the rate of predictions over time: `rate(prediction_count_total[1m])`.
   ![Add Other Queries](../images/54_add-other-queries.png)
4. Enable auto-refresh to see real-time system monitoring.
   ![Auto Refresh Enabled](../images/55_auto-refresh.png)

![Logging received correctly](../images/56_logging-received.png)

**Conclusion:** 
We successfully implemented a complete observability pipeline. Prometheus acts as the time-series database scraping our API, while Grafana provides real-time visual insights into our system's operational health.