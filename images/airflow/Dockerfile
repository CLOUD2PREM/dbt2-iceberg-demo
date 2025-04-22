FROM python:3.12-slim

ARG AIRFLOW_VERSION

ENV dags_folder=/root/airflow/dags
ENV logs_folder=/root/airflow/logs

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    netcat-traditional \
    supervisor \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/airflow

WORKDIR /root/airflow

RUN pip install apache-airflow==$AIRFLOW_VERSION
RUN pip install apache-airflow-providers-ssh
RUN pip install apache-airflow-providers-trino
RUN pip install psycopg2-binary asyncpg flask-appbuilder

COPY ./init-sh/starter-airflow.sh /root/airflow/starter-airflow.sh

RUN chmod +x /root/airflow/starter-airflow.sh

CMD ["/root/airflow/starter-airflow.sh"]