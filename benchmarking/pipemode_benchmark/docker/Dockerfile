FROM 520713654638.dkr.ecr.us-west-2.amazonaws.com/sagemaker-tensorflow:1.6.0-gpu-py2

MAINTAINER Amazon AI

RUN pip install cmake

ARG tf_version
ARG sagemaker_tensorflow
ARG device=cpu
ARG script

RUN export LD_LIBRARY_PATH=/usr/local/cuda-9.0/targets/x86_64-linux/lib/stubs/:/usr/local/cuda-9.0/targets/x86_64-linux/lib/

RUN if [ "$device"="cpu" ] ; then \
		pip install tensorflow==$tf_version; \
	else \
		pip install "tensorflow-gpu"==$tf_version; \
	fi


WORKDIR /root

COPY $sagemaker_tensorflow .

RUN framework_support_installable_local=$(basename $sagemaker_tensorflow) && \
    \
    pip install $framework_support_installable_local && \
    \
    rm $framework_support_installable_local


COPY $script script.py

# entry.py comes from sagemaker-container-support
ENTRYPOINT ["python", "script.py"]
