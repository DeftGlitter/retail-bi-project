from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

# Cargar fuentes
sales = pd.read_csv(RAW / "sales.csv")
products = pd.read_csv(RAW / "products.csv")
customers = pd.read_csv(RAW / "customers.csv")
stores = pd.read_csv(RAW / "stores.csv")

print("\n========== DATA PROFILING ==========\n")

# 1. Resumen general
tables = {
    "Sales": sales,
    "Products": products,
    "Customers": customers,
    "Stores": stores
}

for name, df in tables.items():
    print(f"\n--- {name} ---")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)

# 2. Duplicados
print("\n========== DUPLICATES ==========")

print("Duplicated orders:", sales["order_id"].duplicated().sum())
print("Duplicated products:", products["product_id"].duplicated().sum())
print("Duplicated customers:", customers["customer_id"].duplicated().sum())
print("Duplicated stores:", stores["store_id"].duplicated().sum())

# 3. Validaciones de negocio
print("\n========== BUSINESS RULES ==========")

print("Invalid quantities:", (sales["quantity"] <= 0).sum())

print(
    "Invalid discounts:",
    ((sales["discount_pct"] < 0) |
     (sales["discount_pct"] > 1)).sum()
)

print("Negative sales:", (sales["sales_amount"] < 0).sum())
print("Negative costs:", (sales["cost_amount"] < 0).sum())

# 4. Integridad referencial
print("\n========== REFERENTIAL INTEGRITY ==========")

print(
    "Unknown products:",
    (~sales["product_id"].isin(products["product_id"])).sum()
)

print(
    "Unknown customers:",
    (~sales["customer_id"].isin(customers["customer_id"])).sum()
)

print(
    "Unknown stores:",
    (~sales["store_id"].isin(stores["store_id"])).sum()
)

# 5. Estadísticas de ventas
print("\n========== SALES STATISTICS ==========")

print(sales[[
    "quantity",
    "discount_pct",
    "sales_amount",
    "cost_amount",
    "profit"
]].describe().round(2))

print("\n========== END OF AUDIT ==========")

print("\n========== ISSUE INVESTIGATION ==========")

# 1. Pedidos duplicados
duplicates = sales[
    sales["order_id"].duplicated(keep=False)
]

print("\nDuplicated orders:")
print(duplicates.to_string(index=False))

# 2. Fechas nulas
print("\nMissing dates:")
print(sales[sales["order_date"].isna()])

# 3. Cantidades inválidas
print("\nInvalid quantities:")
print(sales[sales["quantity"] <= 0])

# 4. Descuentos inválidos
print("\nInvalid discounts:")
print(sales[
    (sales["discount_pct"] < 0) |
    (sales["discount_pct"] > 1)
])

# 5. Clientes inexistentes
print("\nUnknown customers:")
print(sales[
    ~sales["customer_id"].isin(customers["customer_id"])
])

# 6. Comprobar cálculo del beneficio
sales["calculated_profit"] = (
    sales["sales_amount"] - sales["cost_amount"]
)

sales["profit_difference"] = (
    sales["profit"] - sales["calculated_profit"]
)

print("\nProfit calculation inconsistencies:")
print(
    sales[
        sales["profit_difference"].abs() > 0.01
    ][[
        "order_id",
        "sales_amount",
        "cost_amount",
        "profit",
        "calculated_profit"
    ]]
)

# 7. Fechas no interpretables
parsed_dates = pd.to_datetime(
    sales["order_date"],
    errors="coerce"
)

print("\nInvalid dates:", parsed_dates.isna().sum())