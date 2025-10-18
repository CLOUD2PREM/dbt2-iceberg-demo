FROM python:3.12-slim

ENV DBT_HOME=/opt/dbt
ENV DBT_PROFILES_DIR=${DBT_HOME}/profiles
ENV DBT_PROJECT_DIR=${DBT_HOME}/project

RUN apt-get update && apt-get install -y \
    git \
    curl \
    libicu-dev \
    less \
    openssh-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN echo "root:3541" | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir ${DBT_HOME} && \
    mkdir -p ${DBT_PROFILES_DIR} && \
    mkdir -p ${DBT_PROJECT_DIR} && \
    mkdir -p ${DBT_PROJECT_DIR}/logs

WORKDIR ${DBT_HOME}

RUN pip install --no-cache-dir \
    dbt-core \
    dbt-trino \
    keyring

COPY init-sh/dbt-starter.sh /usr/local/bin/dbt-starter.sh

RUN chmod +x /usr/local/bin/dbt-starter.sh

CMD [ "dbt-starter.sh" ] 