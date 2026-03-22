from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

from prometheus_client import Counter, Histogram, generate_latest

from src.rule_engine import compute_risk


# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("churn-risk-service")


# -----------------------------
# Prometheus metrics
# -----------------------------
REQUEST_COUNT = Counter(
    "api_request_count",
    "Total API request count",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency in seconds"
)

PREDICTION_COUNT = Counter(
    "prediction_count",
    "Total number of churn predictions made"
)


# -----------------------------
# FastAPI app initialization
# -----------------------------
app = FastAPI(
    title="Churn Risk Prediction Service",
    description="Rule-based churn risk prediction API using customer and ticket data",
    version="1.0"
)


# -----------------------------
# Load datasets on startup
# -----------------------------
logger.info("Loading datasets...")

customers = pd.read_csv("data/processed/customers.csv")
tickets = pd.read_csv("data/processed/tickets.csv")

tickets["created_at"] = pd.to_datetime(tickets["created_at"])

logger.info(
    f"Datasets loaded successfully | customers={len(customers)} | tickets={len(tickets)}"
)


# -----------------------------
# Request schema
# -----------------------------
class CustomerRequest(BaseModel):
    customer_id: str


# -----------------------------
# Health check endpoint
# -----------------------------
@app.get(
    "/",
    summary="Health Check",
    description="Returns service status to verify that the churn risk service is running.",
    response_description="Service status message",
)
def health_check():

    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()

    logger.info("Health check endpoint accessed")

    return {"status": "service running"}


# -----------------------------
# Metrics endpoint
# -----------------------------
@app.get("/metrics")
def metrics():

    logger.info("Metrics endpoint accessed")

    return Response(generate_latest(), media_type="text/plain")


# -----------------------------
# Feature computation
# -----------------------------
def compute_features(customer_id):

    logger.info(f"Computing features for customer {customer_id}")

    # Fetch customer row
    customer_row = customers[customers["customer_id"] == customer_id]

    if customer_row.empty:
        logger.error(f"Customer not found: {customer_id}")
        raise HTTPException(status_code=404, detail="Customer not found")

    contract_type = customer_row.iloc[0]["contract_type"]

    # Fetch ticket history
    customer_tickets = tickets[tickets["customer_id"] == customer_id]

    now = datetime.now()
    window_30 = now - timedelta(days=30)

    # tickets_last_30_days
    tickets_30 = customer_tickets[customer_tickets["created_at"] > window_30]
    tickets_last_30_days = len(tickets_30)

    # complaint_ticket
    complaint_ticket = int((customer_tickets["ticket_type"] == "complaint").any())

    # negative_ratio
    if len(customer_tickets) > 0:
        negative_ratio = (
            (customer_tickets["sentiment"] == "negative").sum()
            / len(customer_tickets)
        )
    else:
        negative_ratio = 0

    logger.info(
        f"Features computed | customer={customer_id} | "
        f"tickets_30={tickets_last_30_days} | "
        f"complaint={complaint_ticket} | "
        f"negative_ratio={round(negative_ratio,3)}"
    )

    return {
        "contract_type": contract_type,
        "tickets_last_30_days": tickets_last_30_days,
        "complaint_ticket": complaint_ticket,
        "negative_ratio": negative_ratio
    }


# -----------------------------
# Prediction endpoint
# -----------------------------
@app.post(
    "/predict-risk",
    summary="Predict Churn Risk",
    description="Computes churn risk category for a customer using contract type and support ticket history.",
    response_description="Predicted churn risk category",
    responses={
        200: {"description": "Prediction successful"},
        404: {"description": "Customer not found"},
        422: {"description": "Invalid request payload"},
    },
)
def predict_risk(request: CustomerRequest):

    start_time = time.time()

    REQUEST_COUNT.labels(method="POST", endpoint="/predict-risk").inc()

    customer_id = request.customer_id

    logger.info(f"Prediction request received for customer {customer_id}")

    features = compute_features(customer_id)

    risk = compute_risk(features)

    PREDICTION_COUNT.inc()

    REQUEST_LATENCY.observe(time.time() - start_time)

    logger.info(
        f"Prediction completed | customer={customer_id} | risk={risk}"
    )

    return {
        "customer_id": customer_id,
        "risk_category": risk
    }