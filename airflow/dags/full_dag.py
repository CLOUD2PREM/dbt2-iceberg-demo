from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
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
    dag_id='iceberg_postgres_dags',
    default_args=default_args,
    description='A simple Trino DAG for PostgreSQL and Iceberg',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['example']
) as dag:

    create_schema_iceberg = SQLExecuteQueryOperator(
        task_id='Create_iceberg_schema',
        conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc 
        WITH (location = 's3a://lakehouse/jaffle_shop_sc')
        """,
        autocommit=True
    )

    create_schema_postgres = SQLExecuteQueryOperator(
        task_id='Create_postgres_schema',
        conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc
        """,
    )

    create_clean_postgres_customers = SQLExecuteQueryOperator(
        task_id='create_postgres_customers_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            )
        """,
    )

    create_clean_postgres_orders = SQLExecuteQueryOperator(
        task_id='create_postgres_orders_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            )
        """,
    )

    create_clean_postgres_payments = SQLExecuteQueryOperator(
        task_id='create_postgres_payments_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            )
        """,
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
        task_id='dbt_seed_raw_to_postgres',
        bash_command='cd /opt/dbt/dbt_project && dbt seed --profile jaffle_shop_postgres',
    )

    dbt_insert_raw_data_to_iceberg_table = BashOperator(
        task_id='dbt_seed_raw_to_iceberg',
        bash_command='cd /opt/dbt/dbt_project && dbt seed --profile jaffle_shop_iceberg',
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

    iceberg_to_postgres_customers = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_customers',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_customers 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_customers
        """,
    )

    iceberg_to_postgres_orders = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_orders',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_orders 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_orders
        """,
    )

    iceberg_to_postgres_payments = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_payments',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_payments 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_payments
        """,
    )

    connect_node_1 = DummyOperator(task_id='connect_empty_node_1')
    connect_node_2 = DummyOperator(task_id='connect_empty_node_2')
    connect_node_3 = DummyOperator(task_id='connect_empty_node_3')
    connect_node_4 = DummyOperator(task_id='connect_empty_node_4')
    connect_node_5 = DummyOperator(task_id='connect_empty_node_5')

    [create_schema_iceberg, create_schema_postgres] >> connect_node_1
    connect_node_1 >> [create_clean_postgres_customers, create_clean_postgres_orders, create_clean_postgres_payments] >> connect_node_2
    connect_node_2 >> [create_clean_iceberg_customers, create_clean_iceberg_orders, create_clean_iceberg_payments] >> connect_node_3
    connect_node_3 >> [dbt_insert_raw_data_to_postgres_table, dbt_insert_raw_data_to_iceberg_table] >> connect_node_4
    connect_node_4 >> [iceberg_to_postgres_customers, iceberg_to_postgres_orders, iceberg_to_postgres_payments] >> connect_node_5
    connect_node_5 >> [postgres_to_iceberg_customers, postgres_to_iceberg_orders, postgres_to_iceberg_payments]
