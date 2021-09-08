FROM openjdk:11.0.9.1-jre

ARG CONFLUENT_MAJOR_VERSION=6.1
ARG CONFLUENT_COMMUNITY_VERSION=6.1.1

ENV TZ=UTC
ENV PATH ${PATH}:/opt/confluent-${CONFLUENT_COMMUNITY_VERSION}/bin

# Generic Tools
RUN apt-get update
RUN apt-get install -y apt-utils telnet netcat git jq nano

WORKDIR /

# Confluent CLI
RUN curl -L --http1.1 https://cnfl.io/cli | sh -s -b -- latest /bin
RUN curl -L --http1.1 https://cnfl.io/ccloud-cli | sh -s -b -- latest /bin

WORKDIR /app

# Confluent Platform
#RUN apt-get update && apt-get install -y kubectl kafkacat confluent-platform-oss-2.11
RUN wget http://packages.confluent.io/archive/${CONFLUENT_MAJOR_VERSION}/confluent-community-${CONFLUENT_COMMUNITY_VERSION}.tar.gz -P /tmp && tar -xzvf /tmp/confluent-community-${CONFLUENT_COMMUNITY_VERSION}.tar.gz -C /opt && rm /tmp/* -r

# Python
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN echo "alias python=python3" >> /root/.bashrc
RUN echo "alias pip=pip3" >> /root/.bashrc
COPY ./python/requirements.txt /app
RUN pip3 install -r /app/requirements.txt

# Kafka tools
#RUN apt-get install -y kafkacat

RUN apt-get install -y git librdkafka-dev

# Install kcat
RUN mkdir -p git && cd git && git clone https://github.com/edenhill/kafkacat.git && cd kafkacat && ./configure && make && make install

# Customizing
RUN echo "alias ls='ls -lh --color=auto'" >> /root/.bashrc
RUN echo "export PS1=\"[ \[\e[0;34m\]Kafka Client $(date +'%d/%m/%Y %H:%M:%S')\[\e[m\] \[\e[1;37m\]\w\[\e[m\] ] \"" >> /root/.bashrc

# Configurar ambiente
RUN echo ". ./shell/environment_set.sh"  >> /root/.bashrc


