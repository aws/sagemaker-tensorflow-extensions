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


def get_role_arn():
    """Return the arn for the role SageMakerRole."""
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

if __name__ == '__main__':
    role = get_role_arn()
    parallelism = 8  # how many training jobs to run in parallel

    role_arn = get_role_arn()
    bucket = bucket_helper.bucket()

    output_path = "s3://{}/pipemode/output/".format(bucket)
    dataset_path = "s3://{}/pipemode/datasets".format(bucket)

    executor = concurrent.futures.ProcessPoolExecutor(max_workers=parallelism)
    futures = []
    for benchmark_script in script.all_scripts:
        benchmark_script.build()
        for benchmark_dataset in dataset.all_datasets:
            benchmark_dataset.generate()
            future = executor.submit(benchmark,
                                     role_arn,
                                     benchmark_dataset,
                                     output_path,
                                     'ml.p3.16xlarge',
                                     benchmark_script)
            futures.append(future)
            time.sleep(2)

    cwclient = boto3.client('cloudwatch')
    for future in concurrent.futures.as_completed(futures):
        (training_job_name, dataset, instance_type, script, iteration_time) = future.result()
        print training_job_name, dataset, instance_type, script, iteration_time
        cwclient.put_metric_data(
            Namespace='tf-pipemode-benchmark',
            MetricData=[{
                'MetricName': 'IterationTime.{}.{}'.format(dataset.name, script.name),
                'Dimensions': [
                    {
                        'Dataset': dataset.name
                    }
                ],
                'Timestamp': datetime.datetime.now(),
                'Value': iteration_time,
                'Unit': 'Seconds'
            }]
        )
