# Retail BI Project

End-to-end retail analytics portfolio project: synthetic data generation, data quality checks, Python ETL, SQL dimensional model, and Power BI reporting.

## Business objective
Help a fictional retail chain understand sales, profitability, product performance, customer segments, and store performance.

## Planned architecture
1. Synthetic source data (CSV)
2. Python / pandas ETL and data-quality validation
3. SQL dimensional model (star schema)
4. Power BI semantic model, DAX measures, and report pages
5. Business recommendations and client-style presentation

## Generate source data
```bash
python src/etl/generate_data.py
```

The generator creates data in `data/raw/` and intentionally includes a few data-quality issues for the ETL phase.
