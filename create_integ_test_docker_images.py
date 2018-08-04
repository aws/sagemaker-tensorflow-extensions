from __future__ import absolute_import

import argparse
import base64
import subprocess
import docker
import boto3
import botocore
import glob
import sys

TF_VERSION = "1.8.0"

REGION = "us-west-2"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('device', nargs='?', default='cpu')
    args = parser.parse_args()

    client = docker.from_env()
    ecr_client = boto3.client('ecr', region_name=REGION)
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']

    subprocess.check_call([sys.executable, 'setup.py', 'sdist'])
    [sdist_path] = glob.glob('dist/sagemaker_tensorflow-{}*'.format(TF_VERSION))
    try:
        ecr_client.create_repository(repositoryName='sagemaker_tensorflow_integ_test')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
            pass
        else:
            raise

    python_version = str(sys.version_info[0])
    tag = '{}/sagemaker_tensorflow_integ_test:{}-{}-{}'.format(registry, TF_VERSION, args.device, python_version)[8:]
    client.images.build(
        path='.',
        dockerfile='test/integ/Dockerfile',
        tag=tag,
        buildargs={'sagemaker_tensorflow': sdist_path,
                   'device': args.device,
                   'python': 'python' if python_version == 2 else 'python3',
                   'tensorflow_version': TF_VERSION,
                   'script': 'test/integ/scripts/estimator_script.py'})

    client.images.push(tag, auth_config={'username': username, 'password': password})
    print(tag)
