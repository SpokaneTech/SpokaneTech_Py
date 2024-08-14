ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

RUN apt-get update && apt-get install -y \
    curl \
    tmux

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

# CMD ["gunicorn", "--chdir", "./src", "--bind", ":8000", "--workers", "2", "spokanetech.wsgi"]
CMD ["overmind", "start"]
