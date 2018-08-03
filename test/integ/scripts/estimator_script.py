import json
import multiprocessing
import os
import tempfile

import tensorflow as tf
from sagemaker_tensorflow import PipeModeDataset


class BenchmarkConfig(object):

    def __init__(self):
        self.hp = json.load(open('/opt/ml/input/config/hyperparameters.json'))

    @property
    def batch_size(self):
        return int(self.hp.get('batch_size', 5))

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
        return int(self.hp.get('epochs', 3))

    @property
    def parallel_transform_calls(self):
        return int(self.hp.get('parallel_transform_calls', max(1, multiprocessing.cpu_count() - 2)))

    def __repr__(self):
        """Return all properties"""
        return str(vars(self))


config = BenchmarkConfig()


def input_fn():
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
    ds = ds.map(parse, num_parallel_calls=config.parallel_transform_calls)
    ds = ds.batch(config.batch_size)
    print (ds)
    return ds


# Perform Estimator training
column = tf.feature_column.numeric_column('data', shape=(config.dimension, ))
estimator = tf.estimator.LinearClassifier(feature_columns=[column])
estimator.train(input_fn=input_fn)

# Confirm that we have read the correct number of pipes
assert os.path.exists('/opt/ml/input/data/{}_{}'.format(config.channel, config.epochs))

print (os.listdir('/opt/ml/input/data/'))
print ("Trained")
