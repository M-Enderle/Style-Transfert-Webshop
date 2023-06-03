FROM nvidia/cuda:12.0.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages and update system
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8

# install pip3
RUN apt-get install -y python3-pip

# install torch and torchvision
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# copy code
COPY . ./style-transfer-webshop
WORKDIR style-transfer-webshop

# print version for debug
# ENTRYPOINT ["python3", "-m", "sts", "--version"]