FROM ubuntu:latest

# Set variable for branch to be used
ARG BRANCH=main

# Install necessary packages and update system
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10

# Clone the repository
RUN apt-get install -y git && \
    git clone https://mygit.th-deg.de/me04536/style-transfer-webshop.git && \
    cd style-transfer-webshop && \
    git checkout $BRANCH

# navigate into repository
WORKDIR style-transfer-webshop

# Set Python 3.10 as default python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --set python3 /usr/bin/python3.10

# Install venv
RUN apt-get install -y python3.10-venv
    
# Create and activate a virtual environment
ENV VIRTUAL_ENV=/venv
RUN python3.10 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install requirements
RUN pip install -r requirements.txt

# -- Start of running the actual program once it is implemented --
# -- End --

# Cleanup
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*