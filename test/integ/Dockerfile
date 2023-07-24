FROM public.ecr.aws/lts/ubuntu:20.04

ARG device=cpu
ARG tensorflow_version=2.13.0
ARG script
ARG python

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcurl4-openssl-dev \
        g++-9 \
        build-essential \
        curl \
        git \
        libcurl3-dev \
        libfreetype6-dev \
        libzmq3-dev \
        pkg-config \
        python3 \
        python3-pip \
        rsync \
        software-properties-common \
        unzip \
        zip \
        zlib1g-dev \
        openjdk-8-jdk \
        openjdk-8-jre-headless \
        wget \
        vim \
        iputils-ping \
        nginx \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install cmake setuptools


RUN if [ "$device"="cpu" ] ; then \
		pip3 install tensorflow==$tensorflow_version; \
	else \
		pip3 install "tensorflow-gpu"==$tensorflow_version; \
	fi

ARG sagemaker_tensorflow=sagemaker_tensorflow-$tensorflow_version.1.0.0.tar.gz

WORKDIR /root

COPY $sagemaker_tensorflow .

RUN sagemaker_tensorflow_local=$(basename $sagemaker_tensorflow) && \
    \
    pip3 install $sagemaker_tensorflow_local && \
    \
    rm $sagemaker_tensorflow_local

COPY $script script.py

ENV python_command=$python
ENTRYPOINT ["sh", "-c", "$python_command script.py"]
