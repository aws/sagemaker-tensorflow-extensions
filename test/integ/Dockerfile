FROM 520713654638.dkr.ecr.us-west-2.amazonaws.com/sagemaker-tensorflow:1.6.0-gpu-py2

RUN pip install cmake

ARG device=cpu
ARG tensorflow_version=1.4.0
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

# entry.py comes from sagemaker-container-support
ENTRYPOINT ["python", "script.py"]
