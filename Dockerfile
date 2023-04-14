# use the latest ubuntu image
FROM ubuntu:latest

# Install necessary packages and update system
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10

# navigate into repository
COPY . ./style-transfer-webshop
WORKDIR style-transfer-webshop

# Set Python 3.10 as default python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --set python3 /usr/bin/python3.10

# Install pip
RUN apt-get install -y python3-pip

# Install poetry
RUN pip install poetry
    
# Create and activate a virtual environment
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-interaction --no-ansi -vvv
ENV PATH="/style-transfer-webshop/.venv"

# -- Start of running the actual program once it is implemented --

# -- End --