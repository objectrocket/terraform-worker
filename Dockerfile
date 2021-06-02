FROM python:3.9-slim-buster

COPY . /usr/src/tfworker
WORKDIR /usr/src/tfworker

# apt is run with 2>/dev/null to squelch apt CLI warnings and make builds look cleaner, remove to debug
RUN apt update 2>/dev/null && \
    apt install -y --no-install-recommends \
        wget \
        unzip && 2>/dev/null \
    wget --quiet --output-document terraform.zip https://releases.hashicorp.com/terraform/0.12.29/terraform_0.12.29_linux_amd64.zip && \
    unzip terraform.zip && \
    rm terraform.zip && \
    mv terraform /usr/local/bin && \
    chmod 755 /usr/local/bin/terraform && \
    pip install . && \
    apt remove -y wget unzip 2>/dev/null && \
    rm -rf /var/lib/apt/lists/*

ENV USER=orwork
RUN addgroup --gid 1000 ${USER} && \
    adduser --uid 1000 --gecos "${USER} user" --gid 1000 --disabled-password ${USER} && \
    chown -R ${USER}:${USER} /home/orwork

USER ${USER}:${USER}

WORKDIR /home/${USER}
ENTRYPOINT [ "/bin/bash" ]
