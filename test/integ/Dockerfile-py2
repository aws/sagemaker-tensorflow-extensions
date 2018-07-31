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

RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

RUN pip install cmake

ARG device=cpu
ARG tensorflow_version=1.9.0
ARG script

RUN if [ "$device"="cpu" ] ; then \
		pip install tensorflow==$tensorflow_version; \
	else \
		pip install "tensorflow-gpu"==$tensorflow_version; \
	fi

ARG sagemaker_tensorflow=sagemaker_tensorflow-$tensorflow_version.1.0.0.tar.gz

WORKDIR /root

COPY $sagemaker_tensorflow .

RUN sagemaker_tensorflow_local=$(basename $sagemaker_tensorflow) && \
    \
    pip install $sagemaker_tensorflow_local && \
    \
    rm $sagemaker_tensorflow_local

COPY $script script.py

ENTRYPOINT ["python", "script.py"]
