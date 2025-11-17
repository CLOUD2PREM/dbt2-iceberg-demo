from airflow.sdk import DAG, TaskGroup
from datetime import datetime, timedelta
from airflow.providers.ssh.operators.ssh import SSHOperator

default_args = {
    'owner': 'cagri',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='ETL_Lakehouse_Pattern',
    default_args=default_args,
    description='Modern lakehouse ETL with DBT Iceberg',
    schedule=None,
    catchup=False,
    max_active_runs=1
)

with TaskGroup("dbt_seed_group", dag=dag) as dbt_seed_group:
    dbt_seed = SSHOperator(
        task_id='dbt_sample_data',
        command="""
            cd /opt/dbt && \
            dbt seed --profiles-dir /opt/dbt/profiles \
                     --project-dir /opt/dbt/project \
                     --profile jaffle_shop_iceberg \
                     --target dev
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

with TaskGroup("dbt_pipeline", dag=dag) as dbt_pipeline:
    dbt_staging = SSHOperator(
        task_id='dbt_staging',
        command="""
            cd /opt/dbt && \
            dbt run --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev \
                    --select models/staging
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

    dbt_intermediate = SSHOperator(
        task_id='dbt_intermediate',
        command="""
            cd /opt/dbt && \
            dbt run --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev \
                    --select models/intermediate
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

    dbt_marts = SSHOperator(
        task_id='dbt_marts',
        command="""
            cd /opt/dbt && \
            dbt run --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev \
                    --select models/marts
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

    dbt_staging >> dbt_intermediate >> dbt_marts

with TaskGroup("quality_checks", dag=dag) as quality_checks:
    dbt_quality = SSHOperator(
        task_id='dbt_quality',
        command="""
            cd /opt/dbt && \
            dbt run --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev \
                    --select models/quality
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

    dbt_test = SSHOperator(
        task_id='dbt_test',
        command="""
            cd /opt/dbt && \
            dbt test --profiles-dir /opt/dbt/profiles \
                     --project-dir /opt/dbt/project \
                     --profile jaffle_shop_iceberg \
                     --target dev
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

    dbt_quality >> dbt_test

with TaskGroup("dbt_docs", dag=dag) as dbt_docs:
    dbt_docs_task = SSHOperator(
        task_id='dbt_docs_generate',
        command="""
            cd /opt/dbt && \
            dbt docs generate --profiles-dir /opt/dbt/profiles \
                              --project-dir /opt/dbt/project \
                              --profile jaffle_shop_iceberg \
                              --target dev
        """,
        ssh_conn_id='dbt_ssh',
        dag=dag
    )

dbt_seed_group >> dbt_pipeline >> quality_checks >> dbt_docs