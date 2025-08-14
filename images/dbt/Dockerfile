FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    libicu-dev \
    less \
    openssh-server \
    && mkdir -p /var/log \
    && touch /var/log/auth.log \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN echo "root:3541" | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

ENV DBT_PROFILES_DIR=/dbt/profiles

WORKDIR /dbt

# Install dbt-core and required adapters
RUN pip install --no-cache-dir \
    dbt-core \
    dbt-trino \
    dbt-postgres

COPY init-sh/starter-dbt.sh /usr/local/bin/starter-dbt.sh
RUN chmod +x /usr/local/bin/starter-dbt.sh

ENTRYPOINT ["/usr/local/bin/starter-dbt.sh"]