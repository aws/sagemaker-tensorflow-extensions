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

import boto3
import concurrent.futures as cf
import os
import shutil
import sys
import tempfile

import bucket_helper
import recordio_utils


class BenchmarkDataset(object):
    """A collection of synthetic multi-class vector training data stored in record io files.

    Each dataset contains multiple records of labeled floating point vectors. Each vector
    is sampled from a Gaussian distribution with a class specific mean. This means it should
    be possible to build a classifier that performs better than random guessing using
    datasets built wtih this class.

    Datasets are generated locally and uploaded to s3 in a specific bucket with specific
    prefix.
    """

    def __init__(self, name, bucket, prefix, dimension, num_records, num_files, num_copies, num_classes):
        """Create a BenchmarkDataset.

        Args:
            name (str): The name of the dataset
            bucket (str): An S3 bucket to store the dataset in
            prefix (str): An S3 prefix directory to store dataset objects in, within the bucket
            dimension (int): The number of features in the dataset.
            num_records (int): How many records to write in each dataset file.
            num_files (int): How many distinct files of unique labeled records to create.
            num_copies (int): How many times to duplicate each file when being uploaded to s3.
            num_classes (int): How many classes to generate.
        """
        self.name = name
        self.bucket_name = bucket
        self.prefix = prefix
        self.dimension = dimension
        self.num_records = num_records
        self.num_files = num_files
        self.num_copies = num_copies
        self.num_classes = num_classes

    def build(self, overwrite=False):
        """Build the dataset and upload to s3.

        Args:
            overwrite (bool): If true will overwrite the dataset if it exists already.
        """
        if self._exists() and not overwrite:
            return
        self.root_dir = tempfile.mkdtemp()
        self._make_benchmark_files()
        self._upload_to_s3()
        self._cleanup()

    @property
    def s3_uri(self):
        """Return the S3 prefix of this dataset."""
        return "s3://{}/{}/{}".format(self.bucket_name, self.prefix.rstrip('/'), self.name)

    def _exists(self):
        boto_session = boto3.Session()
        s3 = boto_session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)

        return len(list(bucket.objects.filter(MaxKeys=1, Prefix=self.prefix + "/" + self.name)))

    def _cleanup(self):
        shutil.rmtree(self.root_dir)

    def _make_benchmark_files(self):
        for file_index in range(self.num_files):
            recordio_utils.build_record_file(
                os.path.join(self.root_dir, '{}-{}.recordio'.format(self.name, str(file_index))),
                num_records=self.num_records, dimension=self.dimension)

    def _upload_to_s3(self):
        print "Creating Dataset:", self

        def upload(local_file, copy_index):
            boto_session = boto3.Session()
            s3 = boto_session.resource('s3')
            bucket = s3.Bucket(self.bucket_name)

            """Returns a dataset and index if uploading failed"""
            key = '{}/{}/file_{}.recordio'.format(self.prefix, self.name, str(copy_index).zfill(6))
            try:
                bucket.put_object(Key=key, Body=open(local_file, 'rb'))
                if copy_index % 50 == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()
            except Exception as ex:
                print 'Error uploading:', local_file
                print ex.message
                raise Exception("Upload Failed: " + local_file)

        executor = cf.ProcessPoolExecutor()
        futures = []
        uploaded_file_index = 0
        for file_index in range(self.num_files):
            for copy_index in range(self.num_copies):
                local_file = os.path.join(self.root_dir, '{}-{}.recordio'.format(self.name, str(file_index)))
                futures.append(executor.submit(upload(local_file, uploaded_file_index)))
                uploaded_file_index += 1

    def __str__(self):
        """Return the name of this dataset."""
        return self.name

PREFIX = "sagemaker-tf-benchmarking/async-pipe-test"

all_datasets = [
    BenchmarkDataset("1GB.100MBFiles",
                     bucket=bucket_helper.bucket(),
                     prefix=PREFIX,
                     dimension=65536,
                     num_records=200,
                     num_files=1,
                     num_copies=10,
                     num_classes=2),
    BenchmarkDataset("1GB.1MBFiles",
                     bucket=bucket_helper.bucket(),
                     prefix=PREFIX,
                     dimension=65536,
                     num_records=2,
                     num_files=50,
                     num_copies=20,
                     num_classes=2),
    BenchmarkDataset("50GB.1MBFiles",
                     bucket=bucket_helper.bucket(),
                     prefix=PREFIX,
                     dimension=65536,
                     num_records=2,
                     num_files=50,
                     num_copies=1000,
                     num_classes=2),
    BenchmarkDataset("50GB.100MBFiles",
                     bucket=bucket_helper.bucket(),
                     prefix=PREFIX,
                     dimension=65536,
                     num_records=200,
                     num_files=1,
                     num_copies=500,
                     num_classes=2)]
