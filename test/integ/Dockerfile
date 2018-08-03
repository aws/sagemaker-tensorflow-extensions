FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libcurl3-dev \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python-dev \
        python3 \
        python-pip \
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

ARG tensorflow_version=1.8.0
ARG device=cpu
ARG script
ARG python

RUN $python -m pip install cmake wheel setuptools


RUN if [ "$device"="cpu" ] ; then \
		$python -m pip install tensorflow==$tensorflow_version; \
	else \
		$python -m pip install "tensorflow-gpu"==$tensorflow_version; \
	fi

ARG sagemaker_tensorflow=sagemaker_tensorflow-$tensorflow_version.1.0.0.tar.gz

WORKDIR /root

COPY $sagemaker_tensorflow .

RUN sagemaker_tensorflow_local=$(basename $sagemaker_tensorflow) && \
    \
    $python -m pip install $sagemaker_tensorflow_local && \
    \
    rm $sagemaker_tensorflow_local

COPY $script script.py
ENV python_command=$python
ENTRYPOINT ["sh", "-c", "$python_command script.py"]
