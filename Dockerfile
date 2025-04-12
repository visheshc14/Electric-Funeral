FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    mininet \
    net-tools \
    iputils-ping \
    python3 \
    python3-pip \
    python3-dev \
    git \
    openvswitch-switch \
    iproute2 \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python
WORKDIR /app

# Install POX properly
RUN mkdir -p /usr/local/lib/python3/dist-packages && \
    git clone https://github.com/noxrepo/pox.git /tmp/pox && \
    cp -r /tmp/pox/pox /usr/local/lib/python3/dist-packages/ && \
    rm -rf /tmp/pox

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app/
RUN git submodule update --init --recursive

ENV PYTHONPATH=/app:/usr/local/lib/python3/dist-packages

RUN chmod +x network_controller.py create_network
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Initialize OpenVSwitch
RUN mkdir -p /etc/openvswitch && \
    ovsdb-tool create /etc/openvswitch/conf.db

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/bin/bash"]
