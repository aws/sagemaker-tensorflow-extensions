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
from botocore.errorfactory import ClientError


def repository():
    """Return a repository to store benchmarking docker images in."""
    try:
        boto3.client('ecr').create_repository(repositoryName='tf-pipemode')
    except ClientError as ex:
        if 'RepositoryAlreadyExistsException' in ex.message:
            pass
        else:
            raise ex
    account = boto3.client('sts').get_caller_identity()['Account']
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    return '{}.dkr.ecr.{}.amazonaws.com/tf-pipemode'.format(account, my_region)

if __name__ == '__main__':
    print repository()
