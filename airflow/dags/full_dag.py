from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

default_args = {
    'owner': 'cagri',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 18),
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ETL_Full',
    default_args=default_args,
    description='DBT pipeline with Trino',
    schedule_interval=timedelta(days=1),
)

create_schema_iceberg = SQLExecuteQueryOperator(
    task_id='Create_iceberg_schema',
    conn_id='trino_conn',
    sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc 
            WITH (location = 's3a://lakehouse/jaffle_shop_sc')
        """,
    autocommit=True,
    dag=dag
)

create_schema_postgres = SQLExecuteQueryOperator(
    task_id='Create_postgres_schema',
    conn_id='trino_conn',
    sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc
    """,
    dag=dag
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
    dag=dag
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
    dag=dag
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
    dag=dag
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
    dag=dag
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
    dag=dag
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
    dag=dag
)

dbt_insert_raw_data_to_postgres_table = SSHOperator(
    task_id='dbt_seed_raw_to_postgres',
    command='cd /dbt && dbt seed --profiles-dir /dbt/profiles --project-dir /dbt/project --profile jaffle_shop_postgres',
    ssh_conn_id='dbt_ssh',
    dag=dag
)

dbt_insert_raw_data_to_iceberg_table = SSHOperator(
    task_id='dbt_seed_raw_to_iceberg',
    command='cd /dbt && dbt seed --profiles-dir /dbt/profiles --project-dir /dbt/project --profile jaffle_shop_iceberg',
    ssh_conn_id='dbt_ssh',
    dag=dag
)

postgres_to_iceberg_customers = SQLExecuteQueryOperator(
    task_id='postgres_to_iceberg_customers',
    conn_id='trino_conn',
    sql="""            
        INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_customers 
        SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_customers
    """,
    dag=dag
)

postgres_to_iceberg_orders = SQLExecuteQueryOperator(
    task_id='postgres_to_iceberg_orders',
    conn_id='trino_conn',
    sql="""            
        INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_orders 
        SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_orders
    """,
    dag=dag
)

postgres_to_iceberg_payments = SQLExecuteQueryOperator(
    task_id='postgres_to_iceberg_payments',
    conn_id='trino_conn',
    sql="""            
        INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_payments 
        SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_payments
    """,
    dag=dag
)

iceberg_to_postgres_customers = SQLExecuteQueryOperator(
    task_id='iceberg_to_postgres_customers',
    conn_id='trino_conn',
    sql="""
        INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_customers 
        SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_customers
    """,
    dag=dag
)

iceberg_to_postgres_orders = SQLExecuteQueryOperator(
    task_id='iceberg_to_postgres_orders',
    conn_id='trino_conn',
    sql="""
        INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_orders 
        SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_orders
    """,
    dag=dag
)

iceberg_to_postgres_payments = SQLExecuteQueryOperator(
    task_id='iceberg_to_postgres_payments',
    conn_id='trino_conn',
    sql="""
        INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_payments 
        SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_payments
    """,
    dag=dag
)

connect_node_1 = DummyOperator(task_id='connect_empty_node_1', dag=dag)
connect_node_2 = DummyOperator(task_id='connect_empty_node_2', dag=dag)
connect_node_3 = DummyOperator(task_id='connect_empty_node_5', dag=dag)

[create_schema_iceberg, create_schema_postgres] >> connect_node_1

connect_node_1 >> [create_clean_postgres_customers, create_clean_postgres_orders, create_clean_postgres_payments] >> connect_node_2

connect_node_2 >> [create_clean_iceberg_customers, create_clean_iceberg_orders, create_clean_iceberg_payments] >> \
    dbt_insert_raw_data_to_postgres_table >> dbt_insert_raw_data_to_iceberg_table >> \
    [iceberg_to_postgres_customers, iceberg_to_postgres_orders, iceberg_to_postgres_payments] >> connect_node_3

connect_node_3 >> [postgres_to_iceberg_customers, postgres_to_iceberg_orders, postgres_to_iceberg_payments]
