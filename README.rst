SageMaker TensorFlow
====================

.. role:: python(code)
   :language: python

This package contains SageMaker-specific extensions to TensorFlow, including the :python:`PipeModeDataset` class, that allows SageMaker Pipe Mode channels to be read using TensorFlow Datasets.

This package supports Python 3.7-3.10 and TensorFlow versions 1.7 and higher, including 2.0-2.11.0.
For TensorFlow 1.x support, see the `master branch <https://github.com/aws/sagemaker-tensorflow-extensions>`_.
``sagemaker-tensorflow`` releases for all supported versions are available on `PyPI <https://pypi.org/project/sagemaker-tensorflow/#history>`_.

Install
-------
You can build SageMaker TensorFlow into a docker image with the following command:

::

   pip install sagemaker-tensorflow


You can also install sagemaker-tensorflow for a specific version of TensorFlow. The following command will install sagemaker-tensorflow for TensorFlow 1.7:

::

   pip install "sagemaker-tensorflow>=2.0,<2.1"

Build and install from source
-----------------------------
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
------------------------------------------
Release branching is used to track different versions of TensorFlow. To build for a specific release of TensorFlow, checkout the release branch prior to running a pip install. For example, to build for TensorFlow 1.7, you can run the following command in your Dockerfile:

::

    RUN git clone https://github.com/aws/sagemaker-tensorflow-extensions.git && \
	cd sagemaker-tensorflow-extensions && \
        git checkout 1.7 && \
        pip install . && \
        cd .. && \
        rm -rf sagemaker-tensorflow-extensions

Requirements
------------
SageMaker TensorFlow extensions builds on Python 3.4-3.10 in Linux with a TensorFlow version >= 1.7. Older versions of TensorFlow are not supported. Please make sure to checkout the branch of sagemaker-tensorflow-extensions that matches your TensorFlow version.

Please refer to below table for release support information:

.. list-table:: Sagemaker TensorFlow Extensions Release Information
   :widths: 25 25 25 25
   :header-rows: 1

   * - Sagemaker TensorFlow Extensions PyPI Version
     - Sagemaker TensorFlow Extensions Release Version
     - TensorFlow Release Version
     - Sagemaker TensorFlow Extentions Supported Python Versions
   * - 2.11.0.1.17.x
     - v1.17.x
     - 2.11.0
     - 3.7, 3.8, 3.9, 3.10
   * - 2.10.0.1.16.x
     - v1.16.x
     - 2.10.0
     - 3.7, 3.8, 3.9
   * - 2.9.1.1.15.x
     - v1.15.x
     - 2.9.1
     - 3.7, 3.8, 3.9
   * - 2.8.0.1.14.x
     - v1.14.x
     - 2.8.0
     - 3.7, 3.8, 3.9
   * - 2.8.0.1.13.x
     - v1.13.x
     - 2.8.0
     - 3.7, 3.8
   * - 2.7.1.1.12.x
     - v1.12.x
     - 2.7.1
     - 3.7, 3.8
   * - 2.6.0.1.11.0
     - v1.11.x
     - 2.6.0
     - 3.6, 3.7, 3.8
   * - 2.5.0.1.9.0
     - v1.9.x
     - 2.5.0
     - 3.6, 3.7
   * - 2.4.1.1.8.0
     - v1.8.x
     - 2.4.1
     - 3.6, 3.7
   * - 2.3.0.1.6.1
     - v1.6.x
     - 2.3.0
     - 3.6, 3.7
   * - 2.2.0.1.0.0
     - v1.5.0
     - 2.2
     - 2.7, 3.6, 3.7
   * - 2.1.0.1.0.0
     - v1.4.0
     - 2.1
     - 2.7, 3.6
   * - 2.0.0.1.0.0
     - v1.2.1
     - 2.0
     - 2.7, 3.6
   * - 1.15.0.1.0.0
     - v0.2.0
     - 1.15
     - 2.7, 3.6
   * - 1.14.0.1.0.0
     - v0.1.0
     - 1.14, 1.13
     - 2.7, 3.6

SageMaker Pipe Mode
-------------------
SageMaker Pipe Mode is a mechanism for providing S3 data to a training job via Linux fifos. Training programs can read from the fifo and get high-throughput data transfer from S3, without managing the S3 access in the program itself.

SageMaker Pipe Mode is enabled when a SageMaker training job is created. Multiple S3 datasets can be mapped to individual fifos, configured in the training request. Pipe Mode is covered in more detail in the SageMaker documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html#your-algorithms-training-algo-running-container-inputdataconfig

Using the PipeModeDataset
-------------------------
The :code:`PipeModeDataset` is a TensorFlow :code:`Dataset` for reading SageMaker Pipe Mode channels. After installing this package, the :code:`PipeModeDataset` can be imported from a moduled named :code:`sagemaker_tensorflow`.

To construct a :code:`PipeModeDataset` that reads TFRecord encoded records from a "training" channel, do the following:

.. code:: python

  from sagemaker_tensorflow import PipeModeDataset

  ds = PipeModeDataset(channel='training', record_format='TFRecord')

A :python:`PipeModeDataset` should be created for a SageMaker Pipe Mode channel. Each channel corresponds to a single S3 dataset, configured when the training job is created. You can create multiple :python:`PipeModeDataset` instances over different channels to read from multiple S3 datasets in the same training job.

A :python:`PipeModeDataset` can read TFRecord, RecordIO, or text line records, by using the :code:`record_format` constructor argument.  The :code:`record_format` keyword argument can be set to either :code:`RecordIO`, :code:`TFRecord`, or :code:`TextLine` to differentiate between the three encodings. :code:`RecordIO` is the default.

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

Using the PipeModeDataset with the SageMaker Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :code:`sagemaker_tensorflow` module is available for TensorFlow scripts to import when launched on SageMaker via the SageMaker Python SDK. If you are using the SageMaker Python SDK :code:`TensorFlow` Estimator to launch TensorFlow training on SageMaker, note that the default channel name is :code:`training` when just a single S3 URI is passed to :code:`fit`.

Using the PipeModeDataset with SageMaker Augmented Manifest Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SageMaker Augmented Manifest Files provide a mechanism to associate metdata (such as labels) with binary data (like images) for training. An Augmented Manifest File is a single json-lines file, stored as an object in S3. During training, SageMaker reads the data from an Augmented Manifest File and passes the data to the running training job, through a SageMaker Pipe Mode channel.

To learn more about preparing and using an Augmented Manifest File, please consult the SageMaker documentation on Augmented Manifest Files `here`__.

.. _SMAMF: https://docs.aws.amazon.com/sagemaker/latest/dg/augmented-manifest.html

__ SMAMF_

You can use the PipeModeDataset to read data from a Pipe Mode channel that is backed by an Augmented Manifest, by following these guidelines:

First, use a Dataset :code:`batch` operation to combine successive records into a single tuple. Each attribute in an Augmented Manifest File record is queued into the Pipe Mode's fifo as a separate record. By batching, you can combine these successive per-attribute records into a single per-record tuple. In general, if your Augmented Manifest File contains n attributes, then you should issue a call to :code:`batch(n)` on your PipeModeDataset and then use a simple combining function applied with a :code:`map` to combine each per-attribute record in the batch into a single tuple. For example, assume your Augmented Manifest File contains 3 attributes, the following code sample will read Augmented Manifest records into a 3-tuple of string Tensors when applied to a PipeModeDataset.

.. code:: python

        ds = PipeModeDataset("my_channel")

	def combine(records):
	    return (records[0], records[1], records[2])

	ds = ds.batch(3)     # Batch series of three attributes together.
	ds = ds.map(combine) # Convert each batch of three records into a single tuple with three Tensors.

	# Perform other operations on the Dataset - e.g. subsequent batching, decoding
	...

Second, pass :code:`"RecordIO"` as the value for :code:`RecordWrapperType` when you launch the SageMaker training job with an Augmented Manifest File. Doing this will cause SageMaker to wrap each per-attribute record in a RecordIO wrapper, enabling the PipeModeDataset to separate these records.

Third, ensure your PipeModeDataset splits records using RecordIO decoding in your training script. You can do this by simply constructing the PipeModeDataset with no :code:`record_format` argument, as RecordIO is the default record wrapping type for the PipeModeDataset.

If you follow these steps then the PipeModeDataset will produce tuples of string Tensors that you can then decode or process further (for example, by doing a jpeg decode if your data are images).

Release SageMaker TensorFlow Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To release the package, please follow the below steps:

1. Make your changes and run the test in CodeBuild docker container.

2. If you are bumping TensorFlow version, please make sure you bump the versions in ``create_integ_test_docker_images.py``, ``tox.ini`` and ``buildspec-release.yml``. Please drop the Python versions that the new TensorFlow version no longer supports.

3. If you are adding new Python version, please make sure the new Python version is installed in the CodeBuild docker container. Add the new Python version to tox environment and update the tox commands in ``buildspec.yml`` and ``buildspec-release.yml``.

4. If any Python versions are dropped or added, please make sure you update the ``classifiers`` in ``setup.py``.

5. Before starting the release process, you will need to manually bump the package version in ``setup.py``.

Support
-------
We're here to help. Have a question? Please open a `GitHub issue`__, we'd love to hear from you.

.. _X: https://github.com/aws/sagemaker-tensorflow-extensions/issues/new

__ X_

License
-------

SageMaker TensorFlow is licensed under the Apache 2.0 License. It is copyright 2018
Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at:
http://aws.amazon.com/apache2.0/
