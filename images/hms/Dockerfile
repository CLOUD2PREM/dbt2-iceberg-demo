FROM openjdk:17.0.2-jdk-slim

ARG HADOOP_VERSION=${HADOOP_VERSION}
ARG METASTORE_VERSION=${METASTORE_VERSION}

ENV HADOOP_HOME=/opt/hadoop
ENV HIVE_HOME=/opt/hive-metastore
ENV HADOOP_OPTS="-Dmetastore.log.dir=${HIVE_HOME}/logs"
ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HIVE_HOME/bin
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

RUN apt-get update && \
    apt-get install -y wget netcat-openbsd procps gettext && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN mkdir -p ${HIVE_HOME} && \
    mkdir -p ${HADOOP_HOME} && \
    mkdir -p ${HIVE_HOME}/logs && \
    chmod -R 777 ${HIVE_HOME}
    
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
   tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
   mv hadoop-${HADOOP_VERSION}/* ${HADOOP_HOME} && \
   rm -rf hadoop-${HADOOP_VERSION}.tar.gz hadoop-${HADOOP_VERSION}

RUN wget https://dlcdn.apache.org/hive/hive-standalone-metastore-${METASTORE_VERSION}/hive-standalone-metastore-${METASTORE_VERSION}-bin.tar.gz && \
    tar -xzf hive-standalone-metastore-${METASTORE_VERSION}-bin.tar.gz && \
    mv apache-hive-metastore-${METASTORE_VERSION}-bin/* ${HIVE_HOME} && \
    rm -rf hive-standalone-metastore-${METASTORE_VERSION}-bin.tar.gz apache-hive-metastore-${METASTORE_VERSION}-bin
 
RUN wget https://jdbc.postgresql.org/download/postgresql-42.7.6.jar -P ${HIVE_HOME}/lib/ 

COPY init-sh/hms-starter.sh /usr/bin/hms-starter.sh
RUN chmod +x /usr/bin/hms-starter.sh

CMD [ "hms-starter.sh" ]