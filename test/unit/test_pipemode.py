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

import os
import tempfile
import tensorflow as tf
import sys
import pytest
from sagemaker_tensorflow import PipeModeDataset
import struct

_kmagic = 0xced7230a

padding = {}
for amount in range(4):
    if sys.version_info >= (3,):
        padding[amount] = bytes([0x00 for _ in range(amount)])
    else:
        padding[amount] = bytearray([0x00 for _ in range(amount)])


def write_recordio(f, data):
    """Writes a single data point as a RecordIO record to the given file."""
    length = len(data)
    f.write(struct.pack('I', _kmagic))
    f.write(struct.pack('I', length))
    pad = (((length + 3) >> 2) << 2) - length
    f.write(data)
    f.write(padding[pad])


def write_to_channel(channel, records):
    directory = tempfile.mkdtemp()
    filepath = os.path.join(directory, channel + "_0")
    with open(filepath, 'wb') as f:
        for record in records:
            write_recordio(f, record)
    return channel, directory


def test_single_record():
    channel, directory = write_to_channel("A", ["bear"])
    with tf.Session() as sess:
        dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory)
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        assert "bear" == sess.run(next)


def test_multiple_records():
    channel, directory = write_to_channel("B", ["bunny", "caterpillar"])
    with tf.Session() as sess:
        dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory)
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        assert "bunny" == sess.run(next)
        assert "caterpillar" == sess.run(next)


def test_large_record():
    channel, directory = write_to_channel("C", ["a" * 1000000])

    with tf.Session() as sess:
        dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory)
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        assert "a" * 1000000 == sess.run(next)


def test_invalid_data():
    directory = tempfile.mkdtemp()
    filename = "X_0"
    with open(directory + "/" + filename, 'w') as f:
        f.write("adfsafasfd")

    dataset = PipeModeDataset("X", pipe_dir=directory, state_dir=directory)
    with pytest.raises(tf.errors.InternalError):
        with tf.Session() as sess:
            it = dataset.make_one_shot_iterator()
            next = it.get_next()
            sess.run(next)


def test_out_of_range():
    channel, directory = write_to_channel("A", ["bear", "bunny", "truck"])
    with tf.Session() as sess:
        dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory)
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        for i in range(3):
            sess.run(next)
        with pytest.raises(tf.errors.OutOfRangeError):
            sess.run(next)


def test_multiple_iterators():
    channel, directory = write_to_channel("A", ["bear"])

    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory)
    with tf.Session() as sess:
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        assert sess.run(next) == "bear"
        with pytest.raises(tf.errors.OutOfRangeError):
            sess.run(next)

    with open(os.path.join(directory, channel + "_1"), 'wb') as f:
        write_recordio(f, "bunny")
        write_recordio(f, "piano")
        write_recordio(f, "caterpillar")

    with tf.Session() as sess:
        it = dataset.make_one_shot_iterator()
        next = it.get_next()
        assert "bunny" == sess.run(next)
        assert "piano" == sess.run(next)
        assert "caterpillar" == sess.run(next)
        with pytest.raises(tf.errors.OutOfRangeError):
            sess.run(next)
