import argparse
import base64
import boto3
import docker
import json
import os
import shutil
import subprocess

import recordio_utils
import region_helper
import repo_helper
from script import BenchmarkScript


def main(args=None):
    """Run local benchmarking."""
    parser = argparse.ArgumentParser(description='Benchmark SageMaker TensorFlow PipeMode')

    parser.add_argument('sdist_path',
                        help='The path of a sagemaker_tensorflow tar.gz source distribution to benchmark')
    args = parser.parse_args()

    recordio_utils.build_record_file("1GB.input", dimension=65536, num_records=2000)

    local_data_dir = '.local_data_dir'
    local_config_dir = '.local_config_dir'

    if os.path.exists(local_data_dir):
        shutil.rmtree(local_data_dir)
    if os.path.exists(local_config_dir):
        shutil.rmtree(local_config_dir)

    os.mkdir(local_data_dir)
    os.mkdir(local_config_dir)

    # Write hyperparameters.json
    with open('{}/hyperparameters.json'.format(local_config_dir), 'w') as f:
        f.write(
            json.dumps({'dimension': '65536', 'batch_size': '400', 'prefetch_size': '40'})
        )

    benchmark_script = BenchmarkScript("InputOnly",
                                       repo_helper.repository(), "input_only_script.py", "input-only", "cpu")
    benchmark_script.build(args.sdist_path)
    client = docker.from_env()
    ecr_client = boto3.client('ecr', region_name=region_helper.region)

    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')

    client.images.pull(benchmark_script.image, auth_config={'username': username, 'password': password})

    subprocess.check_call(['rm', '-f', '{}/elizabeth_0'.format(local_data_dir)])
    subprocess.check_call(['mkfifo', '{}/elizabeth_0'.format(local_data_dir)])
    subprocess.Popen("dd if={} of={} bs=65536".format("1GB.input", "{}/elizabeth_0".format(local_data_dir)), shell=True)

    volumes = {
        '{}/{}'.format(os.getcwd(), local_data_dir): {'bind': '/opt/ml/input/data/', 'mode': 'rw'},
        '{}/{}'.format(os.getcwd(), local_config_dir): {'bind': '/opt/ml/input/config/', 'mode': 'rw'},
    }

    logs = client.containers.run(benchmark_script.image, volumes=volumes, stream=True)
    for log in logs:
        print log.strip()

    shutil.rmtree(local_data_dir)
    shutil.rmtree(local_config_dir)
    os.remove("1GB.input")
