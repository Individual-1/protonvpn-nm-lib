FROM ubuntu:latest
RUN apt-get update 
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

# Install a few useful packages

RUN apt-get install -y net-tools \
    apt-utils \
    iproute2 \
    python3 \
    network-manager \
    sudo \
    vim \
    pkg-config \
    iputils-ping \
    openvpn

RUN apt-get install -y \
    python3-pip \
    libcairo2-dev \
    python3-jinja2 \
    libgirepository1.0-dev \
    gir1.2-nm-1.0 

RUN python3 -m pip install cython && \
    python3 -m pip install proton-client && \
    python3 -m pip install keyring && \
    python3 -m pip install xdg

COPY requirements.txt /tmp
RUN python3 -m pip install -r /tmp/requirements.txt && \
    true

RUN useradd -ms /bin/bash user
RUN usermod -a -G sudo user
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY docker_entry.sh /usr/local/bin
ENTRYPOINT ["/usr/local/bin/docker_entry.sh"]