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

import json
import multiprocessing
import time
import tensorflow as tf
from sagemaker_tensorflow import PipeModeDataset
from tensorflow.contrib.data import map_and_batch


class _BenchmarkConfig(object):

    def __init__(self):
        self.hp = json.load(open('/opt/ml/input/config/hyperparameters.json'))

    @property
    def batch_size(self):
        return int(self.hp.get('batch_size', 50))

    @property
    def prefetch_size(self):
        return int(self.hp.get('prefetch_size', 1000))

    @property
    def channel(self):
        return self.hp.get('channel', 'elizabeth')

    @property
    def dimension(self):
        return int(self.hp['dimension'])

    @property
    def epochs(self):
        return int(self.hp.get('epochs', 1))

    @property
    def parallel_transform_calls(self):
        return int(self.hp.get('parallel_transform_calls', max(1, multiprocessing.cpu_count() - 2)))

    def __repr__(self):
        """Return all properties."""
        return str(vars(self))

config = _BenchmarkConfig()


def _input_fn():
    features = {
        'data': tf.FixedLenFeature([], tf.string),
        'labels': tf.FixedLenFeature([], tf.int64),
    }

    def parse(record):
        parsed = tf.parse_single_example(record, features)
        return ({
            'data': tf.decode_raw(parsed['data'], tf.float64)
        }, parsed['labels'])

    ds = PipeModeDataset(config.channel, benchmark=True)
    if config.epochs > 1:
        ds = ds.repeat(config.epochs)
    if config.prefetch_size > 0:
        ds = ds.prefetch(config.prefetch_size)
    ds = ds.apply(map_and_batch(parse, batch_size=config.batch_size,
                                num_parallel_batches=config.parallel_transform_calls))

    return ds


with tf.Session() as sess:
    next = _input_fn().make_one_shot_iterator().get_next()
    it_start = time.time()
    while True:
        try:
            sess.run(next)
        except tf.errors.OutOfRangeError:
            break
print "iteration time:", time.time() - it_start
