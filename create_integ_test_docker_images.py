import argparse
import base64
import subprocess
import docker
import boto3
import botocore
import os

TF_VERSION = "1.4.0"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('device', nargs='?', default='cpu')
    args = parser.parse_args()

    client = docker.from_env()
    ecr_client = boto3.client('ecr')
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']

    sdist_path = 'dist/sagemaker_tensorflow-{}.1.0.0.tar.gz'.format(TF_VERSION)
    if not os.path.exists(sdist_path):
        subprocess.check_call(['python', 'setup.py', 'sdist'])
    try:
        ecr_client.create_repository(repositoryName='sagemaker_tensorflow_integ_test')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
            pass
        else:
            raise

    tag = '{}/sagemaker_tensorflow_integ_test:{}-{}'.format(registry, TF_VERSION, args.device)[8:]

    client.images.build(
        path='.',
        dockerfile='test/integ/Dockerfile',
        tag=tag,
        buildargs={'sagemaker_tensorflow': sdist_path,
                   'device': args.device,
                   'tensorflow_version': TF_VERSION,
                   'script': 'test/integ/scripts/estimator_script.py'})

    client.images.push(tag, auth_config={'username': username, 'password': password})
    print(tag)
