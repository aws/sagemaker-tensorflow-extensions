import boto3
import datetime
import os
import pytest
import shutil
import subprocess
import uuid

import integ_test_resources

DIMENSION = 5


@pytest.fixture(scope='session', autouse=True)
def docker_image():
    image = subprocess.check_output(['python', 'create_integ_test_docker_images.py']).strip().split('\n')[-1]
    return image


@pytest.fixture(scope='session')
def gpu_docker_image():
    image = subprocess.check_output(['python', 'create_integ_test_docker_images.py', 'gpu']).strip().split('\n')[-1]
    return image


@pytest.fixture(scope='session')
def multi_records_test_data():
    test_data = 'test-data-' + str(uuid.uuid4())
    os.makedirs(test_data)
    s3_url = integ_test_resources.make_test_data(
        directory=test_data,
        name='multi',
        num_files=5,
        num_records=1000,
        dimension=DIMENSION)
    yield s3_url
    integ_test_resources.delete_s3_url(s3_url)
    shutil.rmtree(test_data)


@pytest.fixture(scope='session')
def single_record_test_data():
    test_data = 'test-data-' + str(uuid.uuid4())
    os.makedirs(test_data)
    s3_url = integ_test_resources.make_test_data(
        directory=test_data,
        name='single',
        num_files=100,
        num_records=1,
        dimension=DIMENSION)
    yield s3_url
    integ_test_resources.delete_s3_url(s3_url)
    shutil.rmtree(test_data)


@pytest.fixture
def role_arn():
    iam = boto3.client('iam')
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


def run_test(role_arn, docker_image, test_data, instance_type, record_wrapper_type=None):
    training_job_name = "-".join([
        "pipemode-it",
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ])
    output_path = integ_test_resources.make_output_path()
    client = boto3.client('sagemaker')
    print "Using docker image", docker_image
    print "Using training data {}".format(test_data)
    print "Output will be written to {}".format(output_path)
    print "Role ARN: {}".format(role_arn)
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
    print "Submitted training job: {}".format(training_job_name)
    integ_test_resources.wait_for_job(training_job_name, client)


def test_gpu_with_single_records(role_arn, gpu_docker_image, single_record_test_data):
    run_test(role_arn, gpu_docker_image, single_record_test_data, 'ml.p3.2xlarge', 'RecordIO')


def test_multi_records(role_arn, docker_image, multi_records_test_data):
    run_test(role_arn, docker_image, multi_records_test_data, 'ml.m5.large')
