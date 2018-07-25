import os
import pytest
import sys
import time
import boto3
import botocore
from .. import recordio_utils
import uuid
from timeout import timeout


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
            print 'Error uploading:', file, dataset, index
            print ex.message
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
            print event['message']


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
