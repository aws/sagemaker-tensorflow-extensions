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
import logging
import os
import pytest
import shutil
import subprocess
import sys
import tempfile
import tensorflow as tf
from .. import recordio_utils
from sagemaker_tensorflow import PipeModeDataset

dimension = 100

tf.logging.set_verbosity(logging.INFO)


@pytest.fixture(autouse=True, scope='session')
def recordio_file():
    recordio_utils.build_record_file('test.recordio', num_records=100, dimension=dimension)
    recordio_utils.validate_record_file('test.recordio', dimension=dimension)
    yield
    os.remove('test.recordio')


@pytest.fixture(autouse=True, scope='session')
def tfrecords_file():
    writer = tf.python_io.TFRecordWriter("test.tfrecords")
    for i in range(100):
        writer.write("hello world")
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


def create_fifos(epochs, channel_dir, channel_name, input_file='test.recordio'):
    for epoch in range(epochs):
        fifo = '{}/{}_{}'.format(channel_dir, channel_name, epoch)
        subprocess.check_call(['mkfifo', fifo])
        devnull = open(os.devnull, 'w')
        subprocess.Popen(['dd', 'if={}'.format(input_file), 'of={}'.format(fifo), 'bs=65536'],
                         stdout=devnull, stderr=devnull)


features = {
    'data': tf.FixedLenFeature([], tf.string),
    'labels': tf.FixedLenFeature([], tf.int64),
}


def parse(record):
    parsed = tf.parse_single_example(record, features)
    return ({
        'data': tf.decode_raw(parsed['data'], tf.float64)
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

    def input_fn():
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir)
        ds = ds.map(parse, num_parallel_calls=12)
        ds = ds.repeat(count=2)
        ds = ds.prefetch(3)
        ds = ds.batch(3)
        it = ds.make_one_shot_iterator()
        return it.get_next()

    estimator = make_estimator(model_dir=model_dir)
    estimator.train(input_fn=input_fn)
    print estimator.model_dir
    print os.path.exists(estimator.model_dir)
    print os.listdir(estimator.model_dir)
    assert os.path.exists(os.path.join(estimator.model_dir, 'model.ckpt-0.index'))


def test_multi_channels():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 3
    create_fifos(epochs, channel_dir, "channel_a")
    create_fifos(epochs, channel_dir, "channel_b")

    def make_dataset(channel_name):
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir)
        ds = ds.map(parse, num_parallel_calls=12)
        ds = ds.repeat(count=2)
        ds = ds.prefetch(3)
        ds = ds.batch(10)
        return ds

    ds_a = make_dataset("channel_a")
    ds_b = make_dataset("channel_b")
    dataset = tf.data.Dataset.zip((ds_a, ds_b))

    with tf.Session() as sess:
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        for i in range(20):
            a, b = sess.run(next)
            assert a[0]['data'].shape == (10, 100)
            assert len(a[1]) == 10
            assert b[0]['data'].shape == (10, 100)
            assert len(b[1]) == 10
        with pytest.raises(tf.errors.OutOfRangeError):
            sess.run(next)


def test_tf_record():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 1
    channel_name = 'testchannel'
    create_fifos(epochs, channel_dir, channel_name, input_file='test.tfrecords')
    ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, record_format='TFRecord')

    with tf.Session() as sess:
        it = ds.make_one_shot_iterator()
        next = it.get_next()
        for i in range(100):
            assert sess.run(next) == 'hello world'


FIELD_DEFAULTS = [[0] for i in range(100)]
COLUMNS = [str(i) for i in range(100)]


def test_csv():
    channel_dir = tempfile.mkdtemp()
    state_dir = tempfile.mkdtemp()
    epochs = 1
    channel_name = 'testchannel'
    create_fifos(epochs, channel_dir, channel_name, input_file='test.csv')

    def parse(line):
        fields = tf.decode_csv(line, FIELD_DEFAULTS)
        features = dict(zip(COLUMNS, fields))
        return features

    with tf.Session() as sess:
        ds = PipeModeDataset(channel_name, pipe_dir=channel_dir, state_dir=state_dir, record_format='TextLine')
        ds = ds.map(parse)

        it = ds.make_one_shot_iterator()
        next = it.get_next()
        for i in range(100):
            d = sess.run(next)
            sys.stdout.flush()
            assert d == {str(i): i for i in range(100)}
