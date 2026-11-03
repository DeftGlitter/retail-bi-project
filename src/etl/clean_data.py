
from pathlib import Path
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

print("========== ETL PROCESS STARTED ==========")

# 1. EXTRACT
sales = pd.read_csv(RAW / "sales.csv")
products = pd.read_csv(RAW / "products.csv")
customers = pd.read_csv(RAW / "customers.csv")
stores = pd.read_csv(RAW / "stores.csv")

original_rows = len(sales)

print(f"Extracted {original_rows} sales records")

# 2. DETECT EXACT DUPLICATES
duplicates = sales[
    sales.duplicated(keep="first")
].copy()

duplicates.to_csv(
    PROCESSED / "duplicate_records.csv",
    index=False
)

sales = sales.drop_duplicates(keep="first").copy()

print(f"Exact duplicates detected: {len(duplicates)}")

# 3. DATA VALIDATION

# Convert dates
sales["order_date"] = pd.to_datetime(
    sales["order_date"],
    errors="coerce"
)

# Create validation rules
invalid_date = sales["order_date"].isna()

invalid_quantity = sales["quantity"] <= 0

invalid_discount = (
    (sales["discount_pct"] < 0) |
    (sales["discount_pct"] > 1)
)

unknown_customer = ~sales["customer_id"].isin(
    customers["customer_id"]
)

unknown_product = ~sales["product_id"].isin(
    products["product_id"]
)

unknown_store = ~sales["store_id"].isin(
    stores["store_id"]
)

invalid_sales = sales["sales_amount"] < 0
invalid_cost = sales["cost_amount"] < 0

# 4. ASSIGN REJECTION REASONS

reasons = pd.Series(
    "",
    index=sales.index,
    dtype="object"
)

rules = {
    "missing_or_invalid_date": invalid_date,
    "invalid_quantity": invalid_quantity,
    "invalid_discount": invalid_discount,
    "unknown_customer": unknown_customer,
    "unknown_product": unknown_product,
    "unknown_store": unknown_store,
    "negative_sales": invalid_sales,
    "negative_cost": invalid_cost
}

for reason, condition in rules.items():
    reasons.loc[condition] = (
        reasons.loc[condition] +
        reason + ";"
    )

# 5. SEPARATE VALID AND INVALID RECORDS

sales["rejection_reason"] = reasons

quarantine = sales[
    sales["rejection_reason"] != ""
].copy()

clean_sales = sales[
    sales["rejection_reason"] == ""
].copy()

clean_sales = clean_sales.drop(
    columns=["rejection_reason"]
)

# 6. TRANSFORM

# Save dates in standard format
clean_sales["order_date"] = (
    clean_sales["order_date"].dt.strftime("%Y-%m-%d")
)

# 7. LOAD

clean_sales.to_csv(
    PROCESSED / "sales_clean.csv",
    index=False
)

quarantine.to_csv(
    PROCESSED / "sales_quarantine.csv",
    index=False
)

# Copy dimension tables after basic validation
products.to_csv(
    PROCESSED / "products_clean.csv",
    index=False
)

customers.to_csv(
    PROCESSED / "customers_clean.csv",
    index=False
)

stores.to_csv(
    PROCESSED / "stores_clean.csv",
    index=False
)

# 8. ETL SUMMARY

print("\n========== ETL SUMMARY ==========")

print(f"Original records: {original_rows}")
print(f"Exact duplicates removed: {len(duplicates)}")
print(f"Records after deduplication: {len(sales)}")
print(f"Quarantined records: {len(quarantine)}")
print(f"Clean records: {len(clean_sales)}")

print("\nQuarantine reasons:")

for reason, condition in rules.items():
    print(f"{reason}: {condition.sum()}")

print("\n========== ETL COMPLETED ==========")
