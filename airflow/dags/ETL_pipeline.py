from airflow import DAG
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
    dag_id='dbt_datapipeline',
    default_args=default_args,
    description='A simple Trino DAG for PostgreSQL and Iceberg',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['example']
) as dag:

    dbt_debug_iceberg = BashOperator(
        task_id='dbt_etl_debug_iceberg',
        bash_command='cd /opt/dbt/jaffle_shop && dbt debug --profile jaffle_shop_iceberg',
    )

    dbt_status_count = BashOperator(
        task_id='status_count',
        bash_command='cd /opt/dbt/jaffle_shop && dbt run --models status_count --profile jaffle_shop_iceberg'
    )

    dbt_debug_iceberg >> dbt_status_count