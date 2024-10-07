from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'cagri',
    'retries': 1,
    'retry_delay': timedelta(seconds=15)
}

with DAG(
    dag_id='Load_Data_from_Postgres_into_Iceberg',
    default_args=default_args,
    description='Trino DAG for Postgres Table to Iceberg',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['example']
) as dag:

    create_schema_postgres = SQLExecuteQueryOperator(
        task_id='Create_postgres_schema',
        conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc
        """,
    )

    create_raw_postgres_customers = SQLExecuteQueryOperator(
        task_id='create_postgres_customers_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            )
        """,
    )

    create_raw_postgress_orders = SQLExecuteQueryOperator(
        task_id='create_postgress_orders_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            )
        """,
    )

    create_raw_postgres_payments = SQLExecuteQueryOperator(
        task_id='create_postgres_payments_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            )
        """,
    )

    create_schema_iceberg = SQLExecuteQueryOperator(
        task_id='Create_iceberg_schema',
        conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc 
        WITH (location = 's3a://lakehouse/jaffle_shop_sc')
        """,
        autocommit=True
    )

    create_clean_iceberg_customers = SQLExecuteQueryOperator(
        task_id='create_iceberg_customers_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/customers'
            )
        """,
    )

    create_clean_iceberg_orders = SQLExecuteQueryOperator(
        task_id='create_iceberg_orders_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/orders'
            )
        """,
    )

    create_clean_iceberg_payments = SQLExecuteQueryOperator(
        task_id='create_iceberg_payments_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/payments'
            )
        """,
    )

    dbt_insert_raw_data_to_postgres_table = BashOperator(
        task_id='dbt_seed_raw',
        bash_command='cd /opt/dbt/dbt_project && dbt seed --profile jaffle_shop_postgres',
    )

    postgres_to_iceberg_customers = SQLExecuteQueryOperator(
        task_id='postgres_to_iceberg_customers',
        conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_customers 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_customers
        """,
    )

    postgres_to_iceberg_orders = SQLExecuteQueryOperator(
        task_id='postgres_to_iceberg_orders',
        conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_orders 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_orders
        """,
    )

    postgres_to_iceberg_payments = SQLExecuteQueryOperator(
        task_id='postgres_to_iceberg_payments',
        conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_payments 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_payments
        """
    )

    create_schema_postgres >> [create_raw_postgres_customers, create_raw_postgress_orders, create_raw_postgres_payments] >> create_schema_iceberg
    create_schema_iceberg >> [create_clean_iceberg_customers, create_clean_iceberg_orders, create_clean_iceberg_payments] >> dbt_insert_raw_data_to_postgres_table
    dbt_insert_raw_data_to_postgres_table >> [postgres_to_iceberg_customers, postgres_to_iceberg_orders, postgres_to_iceberg_payments]