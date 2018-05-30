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

import argparse
import concurrent.futures
import datetime
import time
import boto3

import bucket_helper
import dataset
import script

"""
A script for benchmarking running time of SageMaker PipeMode in TensorFlow, using the
SageMaker TensorFlow PipeModeDataset.

Benchmarking is by way of several TensorFlow scripts that are built into Docker images.
The scripts and Dockerfile are stored in the folder 'docker/'.

Benchmarking results are published to CloudWatch in the tf-pipemode-benchmark namespace.

Requires a SageMakerRole IAM role to exist in the account the script is run in.
"""


class BenchmarkingException(Exception):
    """An error running benchmarking."""

    def __init__(self, message):
        """Create a BenchmarkingException."""
        super(BenchmarkingException, self).__init__(message)


def benchmark(role_arn, dataset, output_path, instance_type, script):
    """Run a single benchmark task.

    Returns a description of the benchmark task, together with the time TensorFlow spent
    iterating over data via the PipeModeDataset.

    Args:
        role_arn: The ARN of a role to run the training task with.
        dataset: A BenchmarkDataset
        output_path: A place to dump models (not needed, but required by the API)
        instance_type: The EC2 instance to benchmark on
        image: A BenchmarkScript
    """
    training_job_name = "-".join([
        "pmb",
        "-".join(dataset.name.split(".")),
        script.name,
        datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ])

    client = boto3.client('sagemaker')
    client.create_training_job(TrainingJobName=training_job_name,
                               RoleArn=role_arn,
                               AlgorithmSpecification={
                                   'TrainingImage': script.image,
                                   'TrainingInputMode': 'Pipe'
                               },
                               HyperParameters={'dimension': str(dataset.dimension)},
                               InputDataConfig=[{
                                   'ChannelName': 'elizabeth',
                                   'DataSource': {
                                       'S3DataSource': {
                                           'S3DataType': 'S3Prefix',
                                           'S3Uri': dataset.s3_uri,
                                           'S3DataDistributionType': 'FullyReplicated'
                                       }
                                   }
                               }],
                               OutputDataConfig={
                                   'S3OutputPath': output_path
                               },
                               StoppingCondition={
                                   'MaxRuntimeInSeconds': 86400
                               },
                               ResourceConfig={
                                   'InstanceType': instance_type,
                                   'InstanceCount': 1,
                                   'VolumeSizeInGB': 100
                               })
    # Wait for training job to complete. return if fail.
    while True:
        status = client.describe_training_job(TrainingJobName=training_job_name)['TrainingJobStatus']
        if status == 'Failed':
            raise BenchmarkingException("Failed job: " + training_job_name)
        if status == 'Completed':
            break
        else:
            time.sleep(30)

    # Extract the iteration time from the logs and return this.
    logs = boto3.client('logs')
    [log_stream] = logs.describe_log_streams(logGroupName="/aws/sagemaker/TrainingJobs",
                                             logStreamNamePrefix=training_job_name)['logStreams']
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
            message = event['message']
            if 'iteration time' in message:
                return (training_job_name, dataset, instance_type, script, float(message[15:].strip()))
    return None


def get_role_arn(role_name):
    """Return the arn for the role role_name."""
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
            if role_name in role['Arn']:
                return role['Arn']
    return None


def main(args=None):
    """Run benchmarking."""
    parser = argparse.ArgumentParser(description='Benchmark SageMaker TensorFlow PipeMode')
    parser.add_argument('--parallelism', type=int, default=8, help='How many training jobs to run concurrently')
    parser.add_argument('sdist_path',
                        help='The path of a sagemaker_tensorflow tar.gz source distribution to benchmark')
    parser.add_argument('--role_name', default='SageMakerRole',
                        help='The name of an IAM role to pass to SageMaker for running benchmarking training jobs')
    parser.add_argument('--instance_type', default='ml.p3.16xlarge')
    args = parser.parse_args()

    role_arn = get_role_arn(role_name=args.role_name)
    bucket = bucket_helper.bucket()

    output_path = "s3://{}/pipemode/output/".format(bucket)

    executor = concurrent.futures.ProcessPoolExecutor(max_workers=args.parallelism)
    futures = []
    for benchmark_script in script.all_scripts:
        benchmark_script.build(sdist_path=args.sdist_path)
        for benchmark_dataset in dataset.all_datasets:
            benchmark_dataset.build()
            future = executor.submit(benchmark,
                                     role_arn,
                                     benchmark_dataset,
                                     output_path,
                                     args.instance_type,
                                     benchmark_script)
            futures.append(future)
            time.sleep(2)

    cwclient = boto3.client('cloudwatch')
    for future in concurrent.futures.as_completed(futures):
        (training_job_name, benchmark_dataset, instance_type, benchmark_script, iteration_time) = future.result()
        print training_job_name, benchmark_dataset, instance_type, benchmark_script, iteration_time
        cwclient.put_metric_data(
            Namespace='tf-pipemode-benchmark',
            MetricData=[{
                'MetricName': 'IterationTime.{}.{}'.format(benchmark_dataset.name, benchmark_script.name),
                'Dimensions': [
                    {
                        'Dataset': benchmark_dataset.name
                    }
                ],
                'Timestamp': datetime.datetime.now(),
                'Value': iteration_time,
                'Unit': 'Seconds'
            }]
        )
