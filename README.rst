===============================
SageMaker TensorFlow 
===============================

.. role:: python(code)
   :language: python

SageMaker specific extensions to TensorFlow. This package includes the :python:`PipeModeDataset` class, that allows SageMaker Pipe Mode channels to be read using TensorFlow DataSets.

Pre-Install
~~~~~~~~~~~
SageMaker TensorFlow build requires :code:`cmake` to be installed. Please :code:`pip install cmake` before building SageMaker TensorFlow.

Install
~~~~~~~
SageMaker TensorFlow extensions is installed as a python package :code:`sagemaker_tensorflow`. 

To install this package, run:

::

    pip install .

in this directory. 

To install in a SageMaker docker image, you can use the following RUN command in your Dockerfile, assuming you have Python 2.7 and pip already installed in your image:

::

    RUN git clone https://github.com/aws/sagemaker-tensorflow-extensions.git && \
        cd sagemaker-tensorflow-extensions && \
        pip install . && \
        cd .. && \
        rm -rf sagemaker-tensorflow-extensions

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
SageMaker TensorFlow extensions builds on Python 2.7 in Linux, with either TensorFlow 1.4, 1.7, and 1.8. Please make sure to checkout the branch of sagemaker-tensorflow-extensions that matches your TensorFlow version installed.

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

License
-------

SageMaker TensorFlow is licensed under the Apache 2.0 License. It is copyright 2018
Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at:
http://aws.amazon.com/apache2.0/
