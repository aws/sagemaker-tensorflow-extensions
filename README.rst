===============================
SageMaker TensorFlow 
===============================

Building
~~~~~~~~
This is a standard Python package with a Python C extension module, built using CMake. 

To build run :code:`pip install .` in this directory.

Use
~~~
This module builds a TensorFlow :code:`Dataset` subclass, :code:`PipeModeDataset`, stored in a module named :code:`sagemaker_tensorflow`. 

A :code:`PipeModeDataset` is instantiated with a required SageMaker channel name, for example "training". It takes a keyword argument
:code:`record_format`. This can either be :code:`"RecordIO"` or :code:`"TFRecord"`, and is used to indicate how records are split 
in the stream.

To construct a :code:`PipeModeDataset` that reads TFRecord encoded records from a "training" channel, do the following:


.. code-block:: python
  ds = PipeModeDataset(config.channel, record_format='TFRecord')

License
-------

SageMaker TensorFlow is licensed under the Apache 2.0 License. It is copyright 2018
Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at:
http://aws.amazon.com/apache2.0/
