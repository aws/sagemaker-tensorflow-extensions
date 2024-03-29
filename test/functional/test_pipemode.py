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
import logging
import os
import pytest
import shutil
import subprocess
import sys
import tempfile
import tensorflow as tf
from .. import recordio_utils
from sagemaker_tensorflow import PipeModeDataset, PipeModeDatasetException

dimension = 100

logger = tf.get_logger()
logger.setLevel(logging.INFO)


@pytest.fixture(autouse=True, scope='session')
def recordio_file():
    recordio_utils.build_record_file('test.recordio', num_records=100, dimension=dimension)
    recordio_utils.validate_record_file('test.recordio', dimension=dimension)
    yield
    os.remove('test.recordio')


@pytest.fixture(autouse=True, scope='session')
def multipart_recordio_file():
    recordio_utils.build_record_file('test.mp.recordio', num_records=100, dimension=dimension, multipart=True)
    yield
    os.remove('test.mp.recordio')


@pytest.fixture(autouse=True, scope='session')
def tfrecords_file():
    writer = tf.io.TFRecordWriter("test.tfrecords")
    for i in range(100):
        writer.write(b"hello world")
    writer.close()
    yield
    os.remove('test.tfrecords')


@pytest.fixture(autouse=True, scope='session')
def csv_file():
    with open('test.csv', 'w') as csv_file:
        for i in range(100):
            for j in range(100):
                csv_file.write(str(j))
                if j < 99:
                    csv_file.write(',')
                else:
                    csv_file.write('\n')
    yield
    os.remove('test.csv')


@pytest.fixture
def model_dir():
    model_dir = tempfile.mkdtemp()
    yield model_dir
    shutil.rmtree(model_dir)


def write_config(directory, *channels):
    configpath = os.path.join(directory, 'inputdataconfig.json')
    input_data_config = {
        channel: {
            "TrainingInputMode": "Pipe"
        } for channel in channels
    }
    with open(configpath, 'w') as f:
        f.write(json.dumps(input_data_config))


def create_fifos(epochs, channel_dir, channel_name, input_file='test.recordio'):
    for epoch in range(epochs):
        fifo = '{}/{}_{}'.format(channel_dir, channel_name, epoch)
        subprocess.check_call(['mkfifo', fifo])
        devnull = open(os.devnull, 'w')
        subprocess.Popen(['dd', 'if={}'.format(input_file), 'of={}'.format(fifo), 'bs=65536'],
                         stdout=devnull, stderr=devnull)


features = {
    'data': tf.io.FixedLenFeature([], tf.string),
    'labels': tf.io.FixedLenFeature([], tf.int64),
}


def parse(record):
    parsed = tf.io.parse_single_example(record, features)
    return ({
        'data': tf.io.decode_raw(parsed['data'], tf.float64)
    }, parsed['labels'])


def make_estimator(model_dir):
    column = tf.feature_column.numeric_column('data', shape=(dimension, ))
    return tf.estimator.LinearClassifier(feature_columns=[column], model_dir=model_dir)


def test_multi_epoch_pipeline(model_dir):
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 3
    channel_name = 'testchannel'
    create_fifos(epochs, channel_dir, channel_name)
    write_config(channel_dir, 'testchannel')

    def input_fn():
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, config_dir=channel_dir)
        ds = ds.map(parse, num_parallel_calls=12)
        ds = ds.repeat(count=2)
        ds = ds.prefetch(3)
        ds = ds.batch(3)
        return ds

    estimator = make_estimator(model_dir=model_dir)
    estimator.train(input_fn=input_fn)


def test_multi_channels():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 3
    create_fifos(epochs, channel_dir, "channel_a")
    create_fifos(epochs, channel_dir, "channel_b")
    write_config(channel_dir, 'channel_a', 'channel_b')

    def make_dataset(channel_name):
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, config_dir=channel_dir)
        ds = ds.map(parse, num_parallel_calls=12)
        ds = ds.repeat(count=2)
        ds = ds.prefetch(3)
        ds = ds.batch(10)
        return ds

    ds_a = make_dataset("channel_a")
    ds_b = make_dataset("channel_b")
    dataset = tf.data.Dataset.zip((ds_a, ds_b))

    it = iter(dataset)
    for i in range(20):
        a, b = it.get_next()
        assert a[0]['data'].shape == (10, 100)
        assert len(a[1]) == 10
        assert b[0]['data'].shape == (10, 100)
        assert len(b[1]) == 10
    with pytest.raises(tf.errors.OutOfRangeError):
        it.get_next()



def test_multipart_recordio(model_dir):
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    channel_name = 'testchannel'
    create_fifos(1, channel_dir, channel_name, input_file='test.mp.recordio')
    write_config(channel_dir, 'testchannel')

    def input_fn():
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, config_dir=channel_dir)
        ds = ds.map(parse, num_parallel_calls=12)
        ds = ds.prefetch(3)
        ds = ds.batch(3)
        return ds

    estimator = make_estimator(model_dir=model_dir)
    estimator.train(input_fn=input_fn)


def test_tf_record():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 1
    channel_name = 'testchannel'
    create_fifos(epochs, channel_dir, channel_name, input_file='test.tfrecords')
    write_config(channel_dir, 'testchannel')

    ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, config_dir=channel_dir,
                         record_format='TFRecord')

    it = iter(ds)
    for i in range(100):
        assert it.get_next() == b'hello world'


FIELD_DEFAULTS = [[0] for i in range(100)]
COLUMNS = [str(i) for i in range(100)]


def test_csv():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 1
    channel_name = 'testchannel'
    write_config(channel_dir, 'testchannel')

    create_fifos(epochs, channel_dir, channel_name, input_file='test.csv')

    def parse(line):
        fields = tf.io.decode_csv(line, FIELD_DEFAULTS)
        features = dict(zip(COLUMNS, fields))
        return features

    ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir,
                         config_dir=channel_dir,
                         record_format='TextLine')
    ds = ds.map(parse)

    it = iter(ds)
    for i in range(100):
        d = it.get_next()
        sys.stdout.flush()
        assert d == {str(i): i for i in range(100)}


def test_input_config_validation_failure():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    write_config(channel_dir, 'testchannel')
    with pytest.raises(PipeModeDatasetException):
        PipeModeDataset("Not a Channel", pipe_dir=channel_dir, state_dir=state_dir, config_dir=channel_dir)
