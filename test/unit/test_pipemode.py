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
import os
import tempfile
import tensorflow as tf
import sys
import pytest
from sagemaker_tensorflow import PipeModeDataset, PipeModeDatasetException
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
    write_config(directory, channel)
    filepath = os.path.join(directory, channel + "_0")
    with open(filepath, 'wb') as f:
        for record in records:
            write_recordio(f, record)
    return channel, directory

def write_config(directory, channel):
    configpath = os.path.join(directory, 'inputdataconfig.json')
    input_data_config = {
        channel: {
            "TrainingInputMode": "Pipe"
        }
    }
    with open(configpath, 'w') as f:
        f.write(json.dumps(input_data_config))

def test_single_record():
    channel, directory = write_to_channel("A", [b"bear"])
    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory,
                              config_dir=directory)
    assert b"bear" == iter(dataset).get_next()


def test_multiple_records():
    channel, directory = write_to_channel("B", [b"bunny", b"caterpillar"])
    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory,
                              config_dir=directory)
    it = iter(dataset)
    assert b"bunny" == it.get_next()
    assert b"caterpillar" == it.get_next()


def test_large_record():
    channel, directory = write_to_channel("C", [b"a" * 1000000])
    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory,
                              config_dir=directory)
    assert b"a" * 1000000 == iter(dataset).get_next()


def test_invalid_data():
    directory = tempfile.mkdtemp()
    filename = "X_0"
    with open(directory + "/" + filename, 'wb') as f:
        f.write(b"adfsafasfd")
    write_config(directory, 'X')
    dataset = PipeModeDataset("X", pipe_dir=directory, state_dir=directory, config_dir=directory)
    with pytest.raises(tf.errors.InternalError):
        iter(dataset).get_next()


def test_out_of_range():
    channel, directory = write_to_channel("A", [b"bear", b"bunny", b"truck"])
    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory, config_dir=directory)
    it = iter(dataset)
    for i in range(3):
        it.get_next()
    with pytest.raises(tf.errors.OutOfRangeError):
        it.get_next()


def test_missing_channel():
    channel, directory = write_to_channel("A", [b"bear", b"bunny", b"truck"])
    with pytest.raises(PipeModeDatasetException):
        PipeModeDataset("Not A Channel", pipe_dir=directory, state_dir=directory, config_dir=directory)


def test_multiple_iterators():
    channel, directory = write_to_channel("A", [b"bear"])

    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory, config_dir=directory)
    it = iter(dataset)
    assert it.get_next() == b"bear"
    with pytest.raises(tf.errors.OutOfRangeError):
        it.get_next()

    with open(os.path.join(directory, channel + "_1"), 'wb') as f:
        write_recordio(f, b"bunny")
        write_recordio(f, b"piano")
        write_recordio(f, b"caterpillar")

    it = iter(dataset)
    assert b"bunny" == it.get_next()
    assert b"piano" == it.get_next()
    assert b"caterpillar" == it.get_next()
    with pytest.raises(tf.errors.OutOfRangeError):
        it.get_next()

def test_benchmark_records_interval_enabled(capfd):
    channel, directory = write_to_channel("A", [b"bear"])

    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory, config_dir=directory, benchmark_records_interval=1)
    it = iter(dataset)
    assert it.get_next() == b"bear"
    out, err = capfd.readouterr()
    assert 'Iterator records' in out

def test_benchmark_records_interval_disabled(capfd):
    channel, directory = write_to_channel("A", [b"bear"])

    dataset = PipeModeDataset(channel, pipe_dir=directory, state_dir=directory, config_dir=directory, benchmark_records_interval=0)
    it = iter(dataset)
    assert it.get_next() == b"bear"
    out, err = capfd.readouterr()
    assert 'Iterator records' not in out
