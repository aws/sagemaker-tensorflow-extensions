===============================
SageMaker TensorFlow 
===============================

.. role:: python(code)
   :language: python

SageMaker specific extensions to TensorFlow, for Python 2.7, 3.4-3.6 and TensorFlow versions 1.7-1.11. This package includes the :python:`PipeModeDataset` class, that allows SageMaker Pipe Mode channels to be read using TensorFlow Datasets.

Install
~~~~~~~
You can build SageMaker TensorFlow into a docker image with the following command:

::

   pip install sagemaker-tensorflow


You can also install sagemaker-tensorflow for a specific version of TensorFlow. The following command will install sagemaker-tensorflow for TensorFlow 1.7:

::

   pip install "sagemaker-tensorflow>=1.7,<1.8"

Build and install from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The SageMaker TensorFlow build depends on the following: 

* cmake
* tensorflow
* curl-dev

To install these run:

::

   pip install cmake tensorflow

On Amazon Linux, curl-dev can be installed with:

::

   yum install curl-dev

On Ubuntu, curl-dev can be installed with:

::

   apt-get install libcurl4-openssl-dev


To build and install this package, run:

::

    pip install .

in this directory. 

To build in a SageMaker docker image, you can use the following RUN command in your Dockerfile:

::

    RUN git clone https://github.com/aws/sagemaker-tensorflow-extensions.git && \
	cd sagemaker-tensorflow-extensions && \
        pip install . && \
        cd .. && \
        rm -rf sagemaker-tensorflow-extensions

Building for a specific TensorFlow version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Release branching is used to track different versions of TensorFlow. To build for a specific release of TensorFlow, checkout the release branch prior to running a pip install. For example, to build for TensorFlow 1.7, you can run the following command in your Dockerfile:

::

    RUN git clone https://github.com/aws/sagemaker-tensorflow-extensions.git && \
	cd sagemaker-tensorflow-extensions && \
        git checkout 1.7 && \
        pip install . && \
        cd .. && \
        rm -rf sagemaker-tensorflow-extensions

Requirements
~~~~~~~~~~~~
SageMaker TensorFlow extensions builds on Python 2.7, 3.4-3.6 in Linux with a TensorFlow version >= 1.7. Older versions of TensorFlow are not supported. Please make sure to checkout the branch of sagemaker-tensorflow-extensions that matches your TensorFlow version.

SageMaker Pipe Mode
~~~~~~~~~~~~~~~~~~~
SageMaker Pipe Mode is a mechanism for providing S3 data to a training job via Linux fifos. Training programs can read from the fifo and get high-throughput data transfer from S3, without managing the S3 access in the program itself. 

SageMaker Pipe Mode is enabled when a SageMaker Training Job is created. Multiple S3 datasets can be mapped to individual fifos, configured in the training request. Pipe Mode is covered in more detail in the SageMaker documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html#your-algorithms-training-algo-running-container-inputdataconfig

Using the PipeModeDataset
~~~~~~~~~~~~~~~~~~~~~~~~~
The :code:`PipeModeDataset` is a TensorFlow :code:`Dataset` for reading SageMaker Pipe Mode channels. After installing the sagemaker tensorflow extensions package, the :code:`PipeModeDataset` can be imported from a moduled named :code:`sagemaker_tensorflow`.

To construct a :code:`PipeModeDataset` that reads TFRecord encoded records from a "training" channel, do the following:

.. code:: python

  from sagemaker_tensorflow import PipeModeDataset
  
  ds = PipeModeDataset(channel='training', record_format='TFRecord')

A :python:`PipeModeDataset` should be created for a SageMaker PipeMode channel. Each channel corresponds to a single S3 dataset, configured when the training job is created. You can create multiple :python:`PipeModeDataset` instances over different channels to read from multiple S3 datasets in the same training program.

A :python:`PipeModeDataset` can read TFRecord, RecordIO, or text line records, by using the :code:`record_format` constructor argument.  The :code:`record_format` kwarg can be set to either :code:`RecordIO`, :code:`TFRecord`, or :code:`TextLine` to differentiate between the three encodings. :code:`RecordIO` is the default.

A :python:`PipeModeDataset` is a regular TensorFlow :python:`Dataset` and as such can be used in TensorFlow input processing pipelines, and in TensorFlow Estimator :code:`input_fn` definitions. All :python:`Dataset` operations are supported on :python:`PipeModeDataset`. The following code snippet shows how to create a batching and parsing :python:`Dataset` that reads data from a SageMaker Pipe Mode channel:

.. code:: python

	features = {
	    'data': tf.FixedLenFeature([], tf.string),
	    'labels': tf.FixedLenFeature([], tf.int64),
	}

	def parse(record):
	    parsed = tf.parse_single_example(record, features)
	    return ({
	        'data': tf.decode_raw(parsed['data'], tf.float64)
	    }, parsed['labels'])

	ds = PipeModeDataset(channel='training', record_format='TFRecord')
	num_epochs = 20
	ds = ds.repeat(num_epochs)
	ds = ds.prefetch(10)
	ds = ds.map(parse, num_parallel_calls=10)
	ds = ds.batch(64)


If you are using the SageMaker Python SDK :code:`TensorFlow` Estimator to launch TensorFlow training on SageMaker, note that the default channel name is :code:`training` when just a single s3 URI is passed to :code:`fit`.

Support
~~~~~~~
We're here to help. Have a question? Please open a `GitHub issue`__, we'd love to hear from you.

.. _X: https://github.com/aws/sagemaker-tensorflow-extensions/issues/new

__ X_

License
~~~~~~~

SageMaker TensorFlow is licensed under the Apache 2.0 License. It is copyright 2018
Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at:
http://aws.amazon.com/apache2.0/
