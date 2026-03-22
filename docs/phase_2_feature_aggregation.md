**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 2: Feature Aggregation Layer

### Objective
Transform the separate customer data and transactional ticket logs into a unified **feature dataset per customer**. 

The goal is to move from event-level data (`tickets.csv`) to customer-level aggregated behaviors, creating the exact input format required by the downstream Rule Engine.

**Inputs:**
- `data/processed/customers.csv`
- `data/processed/tickets.csv`

**Target Output Schema:**
```text
customer_id
contract_type
monthly_charges
tenure
Churn
tickets_last_7_days
tickets_last_30_days
tickets_last_90_days
complaint_ticket
negative_ratio
```

*Note: In the resulting dataset, each row represents exactly **one customer**, rolling up all their historical interactions.*

---

## Step 1: Create the Feature Pipeline Script

We need a script to perform time-windowed aggregations (7, 30, and 90 days), detect the presence of complaint-type tickets, and calculate the ratio of negative sentiment interactions per customer.

```python
# src/feature_pipeline.py

import os
import pandas as pd
from datetime import datetime, timedelta

def build_features(customers_path, tickets_path, output_path):

    # Load datasets
    customers = pd.read_csv(customers_path)
    tickets = pd.read_csv(tickets_path)

    tickets["created_at"] = pd.to_datetime(tickets["created_at"])

    now = datetime.now()
    window_7 = now - timedelta(days=7)
    window_30 = now - timedelta(days=30)
    window_90 = now - timedelta(days=90)

    # -----------------------------
    # 1. Ticket frequency features (Time Windows)
    # -----------------------------
    tickets_7 = tickets[tickets["created_at"] > window_7]
    tickets_30 = tickets[tickets["created_at"] > window_30]
    tickets_90 = tickets[tickets["created_at"] > window_90]

    f7 = tickets_7.groupby("customer_id").size().reset_index(name="tickets_last_7_days")
    f30 = tickets_30.groupby("customer_id").size().reset_index(name="tickets_last_30_days")
    f90 = tickets_90.groupby("customer_id").size().reset_index(name="tickets_last_90_days")

    # -----------------------------
    # 2. Complaint feature flag
    # -----------------------------
    complaints = tickets[tickets["ticket_type"] == "complaint"]
    complaint_feature = complaints.groupby("customer_id").size().reset_index(name="complaint_count")
    complaint_feature["complaint_ticket"] = 1
    complaint_feature = complaint_feature[["customer_id", "complaint_ticket"]]

    # -----------------------------
    # 3. Sentiment feature ratio
    # -----------------------------
    negative = tickets[tickets["sentiment"] == "negative"]
    neg_counts = negative.groupby("customer_id").size().reset_index(name="negative_tickets")
    total_counts = tickets.groupby("customer_id").size().reset_index(name="total_tickets")

    sentiment_feature = total_counts.merge(neg_counts, on="customer_id", how="left")
    sentiment_feature["negative_tickets"] = sentiment_feature["negative_tickets"].fillna(0)
    
    # Calculate ratio: (negative tickets / total tickets)
    sentiment_feature["negative_ratio"] = (
        sentiment_feature["negative_tickets"] / sentiment_feature["total_tickets"]
    )
    sentiment_feature = sentiment_feature[["customer_id", "negative_ratio"]]

    # -----------------------------
    # 4. Merge all features onto base customer data
    # -----------------------------
    features = customers[
        ["customer_id", "contract_type", "monthly_charges", "tenure", "Churn"]
    ]

    features = features.merge(f7, on="customer_id", how="left")
    features = features.merge(f30, on="customer_id", how="left")
    features = features.merge(f90, on="customer_id", how="left")
    features = features.merge(complaint_feature, on="customer_id", how="left")
    features = features.merge(sentiment_feature, on="customer_id", how="left")

    # Replace missing values (e.g., customers with 0 tickets will have NaNs from the left join)
    features = features.fillna(0)

    # Save finalized feature dataset
    features.to_csv(output_path, index=False)

    print("Feature dataset saved to:", output_path)
    print("Shape:", features.shape)

if __name__ == "__main__":
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    build_features(
        customers_path=os.path.join(SCRIPT_DIR, "../data/processed/customers.csv"),
        tickets_path=os.path.join(SCRIPT_DIR, "../data/processed/tickets.csv"),
        output_path=os.path.join(SCRIPT_DIR, "../data/processed/customer_features.csv"),
    )
    print('Feature Dataset created.')
```

---

## Output Execution & Validation

Running the pipeline successfully merges and aggregates the data. 

![Customer Features Output](../images/6_dataset-customer_features.png)

*Created the feature dataset, formatted perfectly to be consumed by the downstream API and logic layers.*

**Conclusion for Phase 2:**
These engineered features (`tickets_last_30_days`, `complaint_ticket`, `negative_ratio`, etc.) serve as the direct inputs for the next phase. The rule-based churn risk engine will evaluate these specific data points to classify customers into **LOW**, **MEDIUM**, or **HIGH** churn risk categories based on deterministic business rules.