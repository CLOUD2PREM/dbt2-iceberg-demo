from airflow import DAG
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'cagri',
    'retries': 1,
    'retry_delay': timedelta(seconds=15)
}

with DAG(
    dag_id='Load_Data_from_Iceberg_into_Postgres',
    default_args=default_args,
    description='Trino DAG for Iceberg Table to Postgres',
    schedule_interval='*/5 * * * *',
    start_date=days_ago(1),
    tags=['example']
) as dag:

    create_schema_iceberg = TrinoOperator(
        task_id='Create_iceberg_schema',
        trino_conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc WITH (location = 's3://warehouse')
        """,
    )

    create_raw_iceberg_customers = TrinoOperator(
        task_id='create_iceberg_customers_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.raw_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3://warehouse/raw_data/customers'
            )
        """,
    )

    create_raw_iceberg_orders = TrinoOperator(
        task_id='create_iceberg_orders_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.raw_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3://warehouse/raw_data/orders'
            )
        """,
    )

    create_raw_iceberg_payments = TrinoOperator(
        task_id='create_iceberg_payments_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.raw_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            ) WITH (
                format = 'PARQUET',
                location = 's3://warehouse/raw_data/payments'
            )
        """,
    )

    dbt_insert_raw_data_to_iceberg_table = BashOperator(
        task_id='dbt_seed_raw',
        bash_command='cd /home/cagri/project/dbt2-iceberg-demo/jaffle_shop && dbt seed --profile jaffle_shop_iceberg',
    )

    iceberg_to_postgres_customers = TrinoOperator(
        task_id='iceberg_to_postgres_customers',
        trino_conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_customers 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_customers
        """,
    )

    iceberg_to_postgres_orders = TrinoOperator(
        task_id='iceberg_to_postgres_orders',
        trino_conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_orders 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_orders
        """,
    )

    iceberg_to_postgres_payments = TrinoOperator(
        task_id='iceberg_to_postgres_payments',
        trino_conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_payments 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_payments
        """,
    )

    create_schema_iceberg >> [create_raw_iceberg_customers, create_raw_iceberg_orders, create_raw_iceberg_payments] >> dbt_insert_raw_data_to_iceberg_table
    dbt_insert_raw_data_to_iceberg_table >> [iceberg_to_postgres_customers, iceberg_to_postgres_orders, iceberg_to_postgres_payments]
