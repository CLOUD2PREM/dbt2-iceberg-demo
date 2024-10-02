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
    dag_id='Load_Data_from_Postgres_into_Iceberg',
    default_args=default_args,
    description='A simple Trino DAG for PostgreSQL and Iceberg',
    schedule_interval='*/5 * * * *',
    start_date=days_ago(1),
    tags=['example']
) as dag:

    create_schema_postgres = TrinoOperator(
        task_id='Create_postgres_schema',
        trino_conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc
        """,
    )

    create_raw_postgres_customers = TrinoOperator(
        task_id='create_postgres_customers_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            )
        """,
    )

    create_raw_postgress_orders = TrinoOperator(
        task_id='create_postgress_orders_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            )
        """,
    )

    create_raw_postgres_payments = TrinoOperator(
        task_id='create_postgres_payments_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            )
        """,
    )

    dbt_insert_raw_data_to_postgres_table = BashOperator(
        task_id='dbt_seed_raw',
        bash_command='cd /home/cagri/project/dbt2-iceberg-demo/jaffle_shop && dbt seed --profile jaffle_shop_postgres',
    )

    postgres_to_iceberg_customers = TrinoOperator(
        task_id='postgres_to_iceberg_customers',
        trino_conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_customers 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_customers
        """,
    )

    postgres_to_iceberg_orders = TrinoOperator(
        task_id='postgres_to_iceberg_orders',
        trino_conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_orders 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_orders
        """,
    )

    postgres_to_iceberg_payments = TrinoOperator(
        task_id='postgres_to_iceberg_payments',
        trino_conn_id='trino_conn',
        sql="""            
            INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_payments 
            SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_payments
        """
    )

    create_schema_postgres >> [create_raw_postgres_customers, create_raw_postgress_orders, create_raw_postgres_payments] >> dbt_insert_raw_data_to_postgres_table
    dbt_insert_raw_data_to_postgres_table >> [postgres_to_iceberg_customers, postgres_to_iceberg_orders, postgres_to_iceberg_payments]