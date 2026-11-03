CREATE SCHEMA IF NOT EXISTS retail;

-- Dimension: Products
CREATE TABLE retail.dim_product (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150),
    category VARCHAR(100),
    brand VARCHAR(100),
    unit_price NUMERIC(12,2),
    unit_cost NUMERIC(12,2)
);

-- Dimension: Customers
CREATE TABLE retail.dim_customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_segment VARCHAR(50),
    customer_city VARCHAR(100),
    signup_date DATE
);

-- Dimension: Stores
CREATE TABLE retail.dim_store (
    store_id VARCHAR(20) PRIMARY KEY,
    store_name VARCHAR(150),
    city VARCHAR(100),
    region VARCHAR(100),
    store_type VARCHAR(50)
);

-- Dimension: Dates
CREATE TABLE retail.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    day INTEGER,
    weekday INTEGER
);

-- Fact: Sales
CREATE TABLE retail.fact_sales (
    sales_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    order_date DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    discount_pct NUMERIC(5,4),
    sales_amount NUMERIC(12,2),
    cost_amount NUMERIC(12,2),
    profit NUMERIC(12,2),

    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES retail.dim_product(product_id),

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES retail.dim_customer(customer_id),

    CONSTRAINT fk_store
        FOREIGN KEY (store_id)
        REFERENCES retail.dim_store(store_id),

    CONSTRAINT fk_date
        FOREIGN KEY (order_date)
        REFERENCES retail.dim_date(full_date)
);