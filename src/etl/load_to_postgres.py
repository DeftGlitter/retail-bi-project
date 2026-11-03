
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text, URL

# =====================================
# CONFIGURATION
# =====================================

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"

# Database credentials from environment
password = os.environ["PGPASSWORD"]

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("PGUSER", "postgres"),
    password=password,
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5432")),
    database=os.getenv("PGDATABASE", "retail_bi")
)

engine = create_engine(connection_url)

# =====================================
# LOAD CSV FILES
# =====================================

tables = {
    "dim_product": "products_clean.csv",
    "dim_customer": "customers_clean.csv",
    "dim_store": "stores_clean.csv",
    "fact_sales": "sales_clean.csv"
}

print("========== DATA LOAD STARTED ==========")

try:
    with engine.begin() as connection:

        for table_name, filename in tables.items():

            print(f"\nLoading {table_name}...")

            file_path = PROCESSED / filename

            df = pd.read_csv(file_path)

            # Convert date columns
            if table_name == "dim_customer":
                df["signup_date"] = pd.to_datetime(
                    df["signup_date"],
                    errors="coerce"
                ).dt.date

            if table_name == "fact_sales":
                df["order_date"] = pd.to_datetime(
                    df["order_date"],
                    errors="raise"
                ).dt.date

            # Load data into PostgreSQL
            df.to_sql(
                name=table_name,
                con=connection,
                schema="retail",
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000
            )

            print(f"Inserted {len(df)} records")

        # =================================
        # VALIDATE LOADED DATA
        # =================================

        print("\n========== DATABASE VALIDATION ==========")

        for table_name in tables:

            result = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM retail.{table_name}"
                )
            )

            print(f"{table_name}: {result.scalar()} records")

    print("\n========== DATA LOAD COMPLETED ==========")

except Exception as error:
    print("\nDATA LOAD FAILED")
    print(f"Error: {error}")
    raise

finally:
    engine.dispose()
