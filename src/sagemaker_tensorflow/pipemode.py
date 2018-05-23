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
import errno
import os
import tensorflow as tf

from tensorflow.python.data.ops import dataset_ops
from tensorflow.python.framework import ops
from tensorflow.python.framework import tensor_shape
from tensorflow.python.framework import dtypes


def load_plugin():
    tf_plugin_path = '/' + '/'.join(list(__file__.split('/'))[:-1] + ["libPipeModeOp.so"])
    return tf.load_op_library(tf_plugin_path)


class PipeModeDataset(dataset_ops.Dataset):

    _tf_plugin = load_plugin()

    def __init__(self, channel, record_format='RecordIO',
                 state_dir='/opt/ml/pipe_state', pipe_dir='/opt/ml/input/data'):
        """A Dataset for reading from a SageMaker PipeMode channel. Supports records encoded using
        either RecordIO, TFRecord, or new line text encoding.

        Args:
            record_format: The record format to use. One of 'RecordIO', 'TFRecord', or 'TextLine'
            channel: The name of the SageMaker channel.
            pipe_dir: The directory to read SageMaker Channels from.
            state_dir: The directory where pipe index state is persisted.
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

    def _as_variant_tensor(self):
        return self._tf_plugin.pipe_mode_dataset(self.record_format, self.state_dir, self.channel, self.pipe_dir)

    @property
    def output_classes(self):
        return ops.Tensor

    @property
    def output_shapes(self):
        return tensor_shape.scalar()

    @property
    def output_types(self):
        return dtypes.string
