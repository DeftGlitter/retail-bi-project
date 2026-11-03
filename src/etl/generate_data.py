"""Generate synthetic retail data for the Retail BI portfolio project."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

# Dimension tables
n_products, n_customers, n_stores = 120, 1500, 20
categories = ["Electronics", "Home", "Small Appliances", "Accessories"]
product_rows = []
for i in range(1, n_products + 1):
    category = categories[(i - 1) % len(categories)]
    price = round(float(rng.uniform(15, 900)), 2)
    cost = round(price * float(rng.uniform(0.45, 0.82)), 2)
    product_rows.append({
        "product_id": f"P{i:04d}",
        "product_name": f"{category[:-1] if category.endswith('s') else category} Product {i:03d}",
        "category": category,
        "brand": f"Brand {(i % 12) + 1:02d}",
        "unit_price": price,
        "unit_cost": cost,
    })
products = pd.DataFrame(product_rows)

regions = ["North", "South", "East", "West", "Central"]
cities = ["Valencia", "Madrid", "Barcelona", "Seville", "Bilbao", "Zaragoza", "Malaga", "Alicante", "Murcia", "Valladolid"]
stores = pd.DataFrame([
    {
        "store_id": f"S{i:03d}",
        "store_name": f"Store {i:02d}",
        "city": cities[(i - 1) % len(cities)],
        "region": regions[(i - 1) % len(regions)],
        "store_type": "Urban" if i % 3 else "Shopping Centre",
    }
    for i in range(1, n_stores + 1)
])

segments = ["Consumer", "Small Business", "Corporate"]
customers = pd.DataFrame({
    "customer_id": [f"C{i:05d}" for i in range(1, n_customers + 1)],
    "customer_segment": rng.choice(segments, n_customers, p=[0.72, 0.20, 0.08]),
    "customer_city": rng.choice(cities, n_customers),
    "signup_date": pd.to_datetime(rng.integers(pd.Timestamp("2021-01-01").value // 10**9,
                                                pd.Timestamp("2026-01-01").value // 10**9,
                                                n_customers), unit="s").date,
})

# Fact table: three years of transactions
n_sales = 25000
dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
sale_dates = rng.choice(dates, n_sales)
product_idx = rng.integers(0, n_products, n_sales)
store_idx = rng.integers(0, n_stores, n_sales)
customer_idx = rng.integers(0, n_customers, n_sales)
units = rng.choice([1, 2, 3, 4, 5], n_sales, p=[0.62, 0.22, 0.09, 0.05, 0.02])
discounts = rng.choice([0.0, 0.05, 0.10, 0.15, 0.20], n_sales, p=[0.55, 0.15, 0.16, 0.09, 0.05])

sales = pd.DataFrame({
    "order_id": [f"O{i:07d}" for i in range(1, n_sales + 1)],
    "order_date": pd.to_datetime(sale_dates),
    "product_id": products.iloc[product_idx]["product_id"].to_numpy(),
    "customer_id": customers.iloc[customer_idx]["customer_id"].to_numpy(),
    "store_id": stores.iloc[store_idx]["store_id"].to_numpy(),
    "quantity": units,
    "discount_pct": discounts,
})
sales = sales.merge(products[["product_id", "unit_price", "unit_cost"]], on="product_id", how="left")
sales["sales_amount"] = (sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"])).round(2)
sales["cost_amount"] = (sales["quantity"] * sales["unit_cost"]).round(2)
sales["profit"] = (sales["sales_amount"] - sales["cost_amount"]).round(2)
sales = sales[["order_id", "order_date", "product_id", "customer_id", "store_id", "quantity",
               "discount_pct", "sales_amount", "cost_amount", "profit"]]

# Introduce a small number of realistic data-quality issues for ETL practice.
if len(sales) > 10:
    sales.loc[5, "customer_id"] = "C99999"  # invalid foreign key
    sales.loc[8, "discount_pct"] = 1.25      # invalid discount
    sales.loc[12, "quantity"] = 0            # invalid quantity
    sales.loc[20, "order_date"] = pd.NaT     # missing date
    sales = pd.concat([sales, sales.iloc[[2]]], ignore_index=True)  # duplicate order

products.to_csv(RAW / "products.csv", index=False)
customers.to_csv(RAW / "customers.csv", index=False)
stores.to_csv(RAW / "stores.csv", index=False)
sales.to_csv(RAW / "sales.csv", index=False)

print(f"Generated files in: {RAW}")
for name, df in [("sales", sales), ("products", products), ("customers", customers), ("stores", stores)]:
    print(f"{name}: {len(df):,} rows")
