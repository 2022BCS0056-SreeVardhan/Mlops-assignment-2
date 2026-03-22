**Name:** Sree Vardhan Reddy Gujjala  
**Roll No:** 2022BCS0056  

# Phase 3: Rule Engine Implementation

## Objective

Use the aggregated features to compute a churn risk category by defining the Rule Engine.

**Input:**
```
data/processed/customer_features.csv
```

**Output:**
```
risk_category
```

**Possible values:**
```
LOW
MEDIUM
HIGH
```

---

## Business Rules

Rules given in the assignment translated into logical conditions:

**Rule 1**
```
tickets_last_30_days > 5 → HIGH
```

**Rule 2**
```
contract_type = Month-to-Month AND complaint_ticket = 1 → HIGH
```

**Rule 3**
```
monthly charge increase + multiple tickets → MEDIUM
```

*Note: Since the dataset does not track historical monthly charge changes yet, we approximate this rule with multiple recent tickets.*

Example proxy rule for Rule 3:
```
tickets_last_30_days >= 3 → MEDIUM
```

**Fallback Rule**
Everything else:
```
LOW
```

---

## Step 01: Rule Engine Implementation

```python
# src/rule_engine.py

import os
import pandas as pd

def compute_risk(row):

    tickets_30 = row["tickets_last_30_days"]
    contract = row["contract_type"]
    complaint = row["complaint_ticket"]

    # Rule 1
    if tickets_30 > 5:
        return "HIGH"

    # Rule 2
    if contract == "Month-to-month" and complaint == 1:
        return "HIGH"

    # Rule 3
    if tickets_30 >= 3:
        return "MEDIUM"

    return "LOW"

def apply_rules(input_path, output_path):

    df = pd.read_csv(input_path)

    df["risk_category"] = df.apply(compute_risk, axis=1)

    df.to_csv(output_path, index=False)

    print("Risk predictions generated")
    print(df["risk_category"].value_counts())

if __name__ == "__main__":
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    apply_rules(
        os.path.join(SCRIPT_DIR, "../data/processed/customer_features.csv"),
        os.path.join(SCRIPT_DIR, "../data/processed/customer_risk_predictions.csv")
    )
```

Example row of `customer_risk_predictions.csv`:

| **customer_id** | **contract_type** | **monthly_charges** | **tenure** | **Churn** | **tickets_last_7_days** | **tickets_last_30_days** | **tickets_last_90_days** | **complaint_ticket** | **negative_ratio** | **risk_category** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7590-VHVEG | Month-to-month | 29.85 | 1 | No | 0.0 | 1.0 | 3.0 | 0.0 | 0.0 | LOW |

---

## Why the CSV was generated

Saving the output as a CSV serves three distinct development purposes before moving to the API layer.

### A. Rule verification

We needed to check whether the rules behave logically across the whole dataset.

Example validation output:
```text
LOW       5017
HIGH      1917
MEDIUM      98
```

This tells us:
- The rules are not broken.
- The rules produce realistic distributions.
- The rules align with the churn signal.

Without this step, we would not know if the logic is flawed prior to serving it via an API.

---

### B. System debugging

We can inspect rows to manually verify the logic:

```text
customer_id
tickets_last_30_days
complaint_ticket
contract_type
risk_category
```

This helps verify that specific conditions, such as:
```
tickets_last_30_days > 5 → HIGH
```
are actually triggering correctly on real data rows.