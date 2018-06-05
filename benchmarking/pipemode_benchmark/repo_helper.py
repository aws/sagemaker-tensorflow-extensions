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
import json
from botocore.errorfactory import ClientError


def repository(region='us-west-2'):
    """Return a repository to store benchmarking docker images in."""
    client = boto3.client('ecr', region_name=region)
    try:
        client.create_repository(repositoryName='tf-pipemode')
    except ClientError as ex:
        if 'RepositoryAlreadyExistsException' in ex.message:
            pass
        else:
            raise ex
    policy = {
        "Version": "2008-10-17",
        "Statement": [
            {
                "Sid": "sagemaker",
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "sagemaker.amazonaws.com"
                    ]
                },
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailabilityecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:ListImages",
                    "ecr:DescribeImages"
                ]
            }
        ]
    }
    client.set_repository_policy(repositoryName='tf-pipemode', policyText=json.dumps(policy))
    account = boto3.client('sts').get_caller_identity()['Account']
    return '{}.dkr.ecr.{}.amazonaws.com/tf-pipemode'.format(account, region)

if __name__ == '__main__':
    print repository()
