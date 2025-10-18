FROM openjdk:17-slim-bullseye

ARG HADOOP_VERSION=${HADOOP_VERSION}

ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN apt-get update && \
    apt-get install -y wget openssh-server openssh-client procps && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN mkdir ${HADOOP_HOME}

RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
   tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
   mv hadoop-${HADOOP_VERSION}/* ${HADOOP_HOME} && \
   rm -rf hadoop-${HADOOP_VERSION}.tar.gz hadoop-${HADOOP_VERSION}

RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

COPY init-sh/hdfs-starter.sh /usr/bin/hdfs-starter.sh
RUN chmod +x /usr/bin/hdfs-starter.sh

CMD [ "hdfs-starter.sh" ]