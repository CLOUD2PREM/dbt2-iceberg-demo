FROM openjdk:25-ea-25-slim-bullseye

ARG TRINO_VERSION=${TRINO_VERSION}

ENV TRINO_HOME=/opt/trino
ENV PATH="/opt/trino/bin:$PATH"
ENV HADOOP_CONF_DIR=/opt/trino/confs

RUN mkdir ${TRINO_HOME} && \
    mkdir -p ${TRINO_HOME}/logs && \
    mkdir -p ${TRINO_HOME}/confs && \
    mkdir -p ${TRINO_HOME}/init-sql

WORKDIR ${TRINO_HOME}

RUN apt-get update && apt-get install -y \
    wget \
    apache2-utils \
    jq \
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN wget https://repo1.maven.org/maven2/io/trino/trino-server/${TRINO_VERSION}/trino-server-${TRINO_VERSION}.tar.gz \
    -O trino-server-${TRINO_VERSION}.tar.gz && \
    tar -xzf trino-server-${TRINO_VERSION}.tar.gz && \
    mv trino-server-${TRINO_VERSION}/* ${TRINO_HOME} && \
    rm -rf trino-server-${TRINO_VERSION}.tar.gz trino-server-${TRINO_VERSION}

RUN wget https://repo1.maven.org/maven2/io/trino/trino-cli/${TRINO_VERSION}/trino-cli-${TRINO_VERSION}-executable.jar \
    -O /opt/trino-cli-${TRINO_VERSION}-executable.jar && \
    mv /opt/trino-cli-${TRINO_VERSION}-executable.jar /usr/bin/trino && \
    chmod +x /usr/bin/trino

COPY init-sh/trino-starter.sh /usr/bin/trino-starter.sh
COPY init-sh/post-init.sh /usr/bin/post-init.sh

RUN chmod +x /usr/bin/trino-starter.sh && \
    chmod +x /usr/bin/post-init.sh

CMD [ "trino-starter.sh" ]