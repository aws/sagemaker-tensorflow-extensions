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

import boto3
import botocore
import datetime
import os
import pytest
import shutil
import signal
import subprocess
import sys
import time
import uuid

from contextlib import contextmanager

from .. import recordio_utils

DIMENSION = 5
DEFAULT_REGION = 'us-west-2'


class TimeoutError(Exception):
    pass


@contextmanager
def timeout(seconds=0, minutes=0, hours=0):
    """
    Add a signal-based timeout to any block of code.
    If multiple time units are specified, they will be added together to determine time limit.
    Usage:
    with timeout(seconds=5):
        my_slow_function(...)
    Args:
        - seconds: The time limit, in seconds.
        - minutes: The time limit, in minutes.
        - hours: The time limit, in hours.
    """

    limit = seconds + 60 * minutes + 3600 * hours

    def handler(signum, frame):
        raise TimeoutError('timed out after {} seconds'.format(limit))

    try:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(limit)

        yield
    finally:
        signal.alarm(0)


def get_bucket(region='us-west-2'):
    boto_session = boto3.Session()
    s3 = boto_session.resource('s3')
    account = boto_session.client('sts').get_caller_identity()['Account']
    region = boto_session.region_name
    default_bucket = 'pipemode-it-{}-{}'.format(region, account)
    try:
        s3.create_bucket(Bucket=default_bucket, CreateBucketConfiguration={'LocationConstraint': region})
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            pass
        else:
            raise e
    return default_bucket


def make_test_data(directory, name, num_files, num_records, dimension):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(get_bucket())
    if not os.path.exists('test-data'):
        os.makedirs('test-data')
    for i in range(num_files):
        if num_records > 1:
            recordio_utils.build_record_file(os.path.join(directory, name + str(i)),
                                             num_records=num_records, dimension=dimension)
        else:
            recordio_utils.build_single_record_file(os.path.join(directory, name + str(i)), dimension=dimension)

    def upload(file, dataset, test_run, index):
        """Returns a dataset and index if uploading failed"""
        key = 'sagemaker/pipemode/datasets/{}/{}/file_{}.recordio'.format(dataset, test_run, str(index).zfill(6))
        try:
            bucket.put_object(Key=key, Body=open(file, 'rb'))
        except Exception as ex:
            print ('Error uploading:', file, dataset, index)
            print (ex.message)
            raise Exception("Upload Failed: " + file + ", " + dataset + ", " + index)
    test_run = str(uuid.uuid4())
    for index in range(num_files):
        filename = os.path.join(directory, name + str(i))
        upload(filename, name + '-files', test_run, index)
    return 's3://{}/sagemaker/pipemode/datasets/{}/{}/'.format(get_bucket(), name + '-files', test_run)


def delete_s3_url(url):
    without_protocol = url[5:]
    bucket = without_protocol.split('/')[0]
    prefix = without_protocol[len(bucket) + 1:]
    s3 = boto3.resource('s3')
    objects_to_delete = s3.meta.client.list_objects(Bucket=bucket, Prefix=prefix)
    delete_keys = {'Objects': []}
    delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
    s3.meta.client.delete_objects(Bucket=bucket, Delete=delete_keys)


def make_output_path():
    return 's3://{}/sagemaker/pipemode/integ-tests/output/'.format(get_bucket())


def dump_logs(job):
    logs = boto3.client('logs')
    [log_stream] = logs.describe_log_streams(logGroupName="/aws/sagemaker/TrainingJobs",
                                             logStreamNamePrefix=job)['logStreams']
    log_stream_name = log_stream['logStreamName']
    next_token = None
    while True:
        if next_token:
            log_event_response = logs.get_log_events(
                logGroupName="/aws/sagemaker/TrainingJobs",
                logStreamName=log_stream_name,
                nextToken=next_token)
        else:
            log_event_response = logs.get_log_events(
                logGroupName="/aws/sagemaker/TrainingJobs",
                logStreamName=log_stream_name)
        next_token = log_event_response['nextForwardToken']
        events = log_event_response['events']
        if not events:
            break
        for event in events:
            print (event['message'])


def wait_for_job(job, sagemaker_client):
    with timeout(minutes=15):
        while True:
            status = sagemaker_client.describe_training_job(TrainingJobName=job)['TrainingJobStatus']
            if status == 'Failed':
                dump_logs(job)
                pytest.fail('Training job failed: ' + job)
            if status == 'Completed':
                break
            else:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(30)


@pytest.fixture(scope='session', autouse=True)
def docker_image():
    output = subprocess.check_output([sys.executable, 'create_integ_test_docker_images.py'])
    image = output.decode('utf-8').strip().split('\n')[-1]
    return image


@pytest.fixture(scope='session')
def gpu_docker_image():
    output = subprocess.check_output([sys.executable, 'create_integ_test_docker_images.py', 'gpu'])
    image = output.decode('utf-8').strip().split('\n')[-1]
    return image


@pytest.fixture(scope='session')
def multi_records_test_data():
    test_data = 'test-data-' + str(uuid.uuid4())
    os.makedirs(test_data)
    s3_url = make_test_data(
        directory=test_data,
        name='multi',
        num_files=5,
        num_records=1000,
        dimension=DIMENSION)
    yield s3_url
    delete_s3_url(s3_url)
    shutil.rmtree(test_data)


@pytest.fixture(scope='session')
def single_record_test_data():
    test_data = 'test-data-' + str(uuid.uuid4())
    os.makedirs(test_data)
    s3_url = make_test_data(
        directory=test_data,
        name='single',
        num_files=100,
        num_records=1,
        dimension=DIMENSION)
    yield s3_url
    delete_s3_url(s3_url)
    shutil.rmtree(test_data)


@pytest.fixture
def role_arn():
    iam = boto3.client('iam', region_name=DEFAULT_REGION)
    retrieved_all_roles = False
    marker = None
    while not retrieved_all_roles:
        if marker:
            list_roles_response = iam.list_roles(Marker=marker)
        else:
            list_roles_response = iam.list_roles()
        marker = list_roles_response.get('Marker', None)
        retrieved_all_roles = (marker is None)
        for role in list_roles_response['Roles']:
            if "SageMakerRole" in role['Arn']:
                return role['Arn']
    return None


@pytest.fixture
def client():
    return boto3.client('sagemaker', region_name=DEFAULT_REGION)


def run_test(client, role_arn, docker_image, test_data, instance_type, record_wrapper_type=None):
    training_job_name = "-".join([
        "pipemode-it",
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ])
    output_path = make_output_path()
    print ("Using docker image", docker_image)
    print ("Using training data {}".format(test_data))
    print ("Output will be written to {}".format(output_path))
    print ("Role ARN: {}".format(role_arn))
    input_data_config = {
        'ChannelName': 'elizabeth',
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri': test_data,
                'S3DataDistributionType': 'FullyReplicated'
            }
        }
    }
    if record_wrapper_type:
        input_data_config['RecordWrapperType'] = record_wrapper_type
    client.create_training_job(TrainingJobName=training_job_name,
                               RoleArn=role_arn,
                               AlgorithmSpecification={
                                   'TrainingImage': docker_image,
                                   'TrainingInputMode': 'Pipe'
                               },
                               HyperParameters={'dimension': str(DIMENSION)},
                               InputDataConfig=[input_data_config],
                               OutputDataConfig={
                                   'S3OutputPath': output_path
                               },
                               StoppingCondition={
                                   'MaxRuntimeInSeconds': 86400
                               },
                               ResourceConfig={
                                   'InstanceType': instance_type,
                                   'InstanceCount': 1,
                                   'VolumeSizeInGB': 10
                               })
    print ("Submitted training job: {}".format(training_job_name))
    wait_for_job(training_job_name, client)


def test_gpu_with_single_records(client, role_arn, gpu_docker_image, single_record_test_data):
    run_test(client, role_arn, gpu_docker_image, single_record_test_data, 'ml.p3.2xlarge', 'RecordIO')


def test_multi_records(client, role_arn, docker_image, multi_records_test_data):
    run_test(client, role_arn, docker_image, multi_records_test_data, 'ml.m5.large')
