FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages and update system
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8

# COPY files
COPY ./src/style_ai ./style-transfer-webshop/src/style_ai
COPY ./pyproject.toml ./style-transfer-webshop/pyproject.toml
COPY ./poetry.lock ./style-transfer-webshop/poetry.lock

WORKDIR style-transfer-webshop

# Set Python 3.10 as default python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --set python3 /usr/bin/python3.8

# Install pip
RUN apt-get update && apt-get install -y python3-pip

RUN pip install poetry

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-interaction --no-ansi -vvv --without dev \
    && poetry run pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 --index-url https://download.pytorch.org/whl/cu118

# print version for debug
ENTRYPOINT ["/style-transfer-webshop/.venv/bin/python3", "src/style_ai/runpod_entry.py"]