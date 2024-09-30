from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'cagri',
    'start_date': datetime(2024, 9, 20), 
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'dbt_airflow_dag',
    default_args=default_args,
    description='dbt test',
    schedule_interval='*/10 * * * *',  
    catchup=False
) as dag:

    airflow_start = BashOperator(
        task_id='airflow_tasks_starting',  
        bash_command="echo 'airflow tasks are starting'"
    )

    dbt_debug = BashOperator(
        task_id='dbt_debug_task',
        bash_command='cd /home/cagri/project/test-dbt2-demo/jaffle_shop && dbt debug',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_task',
        bash_command='cd /home/cagri/project/test-dbt2-demo/jaffle_shop && dbt run',
    )

    dbt_test = BashOperator(
        task_id='dbt_test_task',
        bash_command='cd /home/cagri/project/test-dbt2-demo/jaffle_shop && dbt test',
    )

    airflow_end = BashOperator(
        task_id='airflow_tasks_ended',  
        bash_command="echo 'airflow tasks have ended'"
    )

    airflow_start >> dbt_debug >> dbt_run >> dbt_test >> airflow_end
