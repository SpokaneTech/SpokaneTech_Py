ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

EXPOSE 8000 2222

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

RUN apt-get update && apt-get install -y \
    curl \
    tmux

# Start and enable SSH
COPY sshd_config /etc/ssh/
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd

# Download and install Overmind
RUN curl -SL https://github.com/DarthSim/overmind/releases/download/v2.5.1/overmind-v2.5.1-linux-amd64.gz | gunzip > overmind-v2.5.1-linux-amd64 \
    && curl -SL https://github.com/DarthSim/overmind/releases/download/v2.5.1/overmind-v2.5.1-linux-amd64.gz.sha256sum > overmind-v2.5.1-linux-amd64.gz.sha256sum \
    && chmod +x overmind-v2.5.1-linux-amd64 \
    && mv overmind-v2.5.1-linux-amd64 /usr/bin/overmind

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

EXPOSE 8000

ENTRYPOINT [ "./scripts/entrypoint.sh" ]
CMD ["gunicorn", "--chdir", "./src", "--bind", ":8000", "--workers", "2", "spokanetech.wsgi"]
