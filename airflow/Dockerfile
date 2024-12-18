FROM python:3.12-slim

# Redeclare the ARG after FROM
ARG AIRFLOW_VERSION
ARG AIRFLOW_USER
ARG AIRFLOW_PASSWORD

ENV dags_folder=/root/airflow/dags
ENV logs_folder=/root/airflow/logs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    netcat-traditional \
    supervisor \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Create airflow directory
RUN mkdir -p /root/airflow

WORKDIR /root/airflow

# Install Apache Airflow using the ARG
RUN pip install apache-airflow==$AIRFLOW_VERSION
RUN pip install apache-airflow-providers-ssh
RUN pip install psycopg2-binary

# Copy config files and starter script
COPY ./config/airflow.cfg /root/airflow/airflow.cfg 
COPY ./config/webserver_config.py /root/airflow/webserver_config.py
COPY ./scripts/airflow-starter.sh /root/airflow/airflow-starter.sh

# Make the script executable
RUN chmod +x /root/airflow/airflow-starter.sh

CMD ["/root/airflow/airflow-starter.sh"]