# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import

import errno
import json
import os
import tensorflow as tf

from tensorflow.python.data.ops import dataset_ops
from tensorflow.python.framework import ops
from tensorflow.python.framework import tensor_shape
from tensorflow.python.framework import tensor_spec
from tensorflow.python.framework import dtypes


def _load_plugin():
    tf_plugin_path = '/' + '/'.join(list(__file__.split('/'))[:-1] + ["libPipeModeOp.so"])
    return tf.load_op_library(tf_plugin_path)


class PipeModeDatasetException(Exception):
    """An error using a PipeModeDataset."""

    pass


class PipeModeDataset(dataset_ops.Dataset):
    """A SageMaker Pipe Mode TensorFlow Dataset."""

    _tf_plugin = _load_plugin()

    def __init__(self, channel, record_format='RecordIO',
                 state_dir='/opt/ml/pipe_state', pipe_dir='/opt/ml/input/data',
                 config_dir='/opt/ml/input/config', benchmark=False, benchmark_records_interval=0):
        """Create a Dataset for reading from a SageMaker PipeMode channel.

        Supports records encoded using either RecordIO, TFRecord, or new line text encoding.

        Args:
            record_format: The record format to use. One of 'RecordIO', 'TFRecord', or 'TextLine'
            channel: The name of the SageMaker channel.
            pipe_dir: The directory to read SageMaker Channels from.
            state_dir: The directory where pipe index state is persisted.
            config_dir: The path for SageMaker input data config.
            benchmark: Controls whether to emit timing and throughput metrics after closing an Iterator created from
                     this Dataset. If True, timing and throughput metrics will be emitted to stdout after an Iterator
                     created from this Dataset is destroyed.
            benchmark_records_interval: Controls whether to emit timing and throughput metrics while records are being
                    read from this Dataset. Defines the number of records per interval to emit timing and throughput
                    metrics. If zero, no metrics will be emitted while records are being read from this Dataset.
                    Metrics are emitted to stdout.
        """
        try:
            os.makedirs(state_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.record_format = record_format
        self.channel = channel
        self.pipe_dir = pipe_dir
        self.state_dir = state_dir
        self.benchmark = benchmark
        self.benchmark_records_interval = benchmark_records_interval
        with open(os.path.join(config_dir, 'inputdataconfig.json')) as f:
            self.input_data_config = json.load(f)
        self._validate_input_data_config()
        super(PipeModeDataset, self).__init__(variant_tensor=self._as_variant_tensor())

    def _as_variant_tensor(self):
        return self._tf_plugin.pipe_mode_dataset(self.benchmark, self.record_format, self.state_dir, self.channel,
                                                 self.pipe_dir, self.benchmark_records_interval)

    def _inputs(self):
        return []

    def _validate_input_data_config(self):
        if self.channel not in self.input_data_config:
            raise PipeModeDatasetException("Channel {} not found in Training Job InputDataConfig".format(self.channel))
        if self.input_data_config[self.channel].get('TrainingInputMode', "").lower() != "pipe":
            raise PipeModeDatasetException("Channel {} is not a PipeMode channel".format(self.channel))

    @property
    def output_classes(self):
        """The return type of this Dataset."""
        return ops.Tensor

    @property
    def output_shapes(self):
        """The shape of the output Tensor."""
        return tensor_shape.TensorShape([])

    @property
    def output_types(self):
        """The type of data stored in the output Tensor."""
        return dtypes.string

    @property
    def element_spec(self):
        return tensor_spec.TensorSpec(
            shape=self.output_shapes,
            dtype=self.output_types,
            name=self.channel,
        )
