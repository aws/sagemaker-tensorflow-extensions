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

from botocore.exceptions import ClientError

import boto3


def bucket(region='us-west-2'):
    """Return a bucket for storing SageMaker pipe mode benchmarking data."""
    boto_session = boto3.Session()
    s3 = boto_session.resource('s3')
    account = boto_session.client('sts').get_caller_identity()['Account']
    default_bucket = 'pipemode-benchmark-{}-{}'.format(region, account)
    try:
        s3.create_bucket(Bucket=default_bucket, CreateBucketConfiguration={'LocationConstraint': region})
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            pass
        else:
            raise e
    return default_bucket
