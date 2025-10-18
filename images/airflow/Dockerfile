FROM python:3.12-slim

ARG AIRFLOW_VERSION=${AIRFLOW_VERSION}

ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_USER=${AIRFLOW_USER}
ENV AIRFLOW_PASSWORD=${AIRFLOW_PASSWORD}

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    netcat-traditional \
    supervisor \
    openssh-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir ${AIRFLOW_HOME} && \
    mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/logs/dag_processor ${AIRFLOW_HOME}/plugins ${AIRFLOW_HOME}/auth

RUN chmod 750 -R ${AIRFLOW_HOME} && \
    chmod 777 ${AIRFLOW_HOME}/logs

WORKDIR ${AIRFLOW_HOME}

RUN pip install apache-airflow==$AIRFLOW_VERSION

COPY conf/requirement.txt /tmp/requirement.txt
RUN pip install -r /tmp/requirement.txt

COPY init-sh/airflow-starter.sh /usr/bin/airflow-starter.sh
RUN chmod +x /usr/bin/airflow-starter.sh

CMD [ "airflow-starter.sh" ]