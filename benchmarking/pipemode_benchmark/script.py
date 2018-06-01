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

import base64
import boto3
import docker
import os
import repo_helper
import shutil

import region_helper


class BenchmarkScriptException(Exception):
    """An error building a benchmarking docker image."""

    def __init__(self, message):
        """Create a BenchmarkingScriptException."""
        super(BenchmarkScriptException, self).__init__(message)


FROM_IMAGE = "520713654638.dkr.ecr.us-west-2.amazonaws.com/sagemaker-tensorflow:1.6.0-gpu-py2"


class BenchmarkScript(object):
    """A script that performs benchmarking, built into a docker image."""

    def __init__(self, name, repository, script_name, tag, device):
        """Create a benchmarking script.

        Args:
            name (str): The name of the benchmarking script
            repository (str): The ECR repository to store the image in.
            script_name (str): The name of the script file name within ./docker/ to.
                build.
            tag (str): A tag to apply to the image
            device (str): cpu or gpu, indicating whether the script uses a gpu device or not.
        """
        self.name = name
        self.script_name = script_name
        self.tag = tag
        self.repository = repository
        self.device = device

    @property
    def image(self):
        """The URI of the image containing the script."""
        return self.repository + ":" + self.tag

    def build(self, sdist_path):
        """Build the script into a docker image and upload to ECR.

        Args:
              sdist_path (str): The path to a sagemaker_tensorflow sdist .tar.gz that will be benchmarked.
        """
        # Copy in the sdist into a docker build directory
        docker_build_dir = ".docker-build-{}".format(self.name)
        if os.path.exists(docker_build_dir):
            shutil.rmtree(docker_build_dir)

        # Copy everything in the docker package data into the docker build dir
        docker_install_dir = '/' + '/'.join(list(__file__.split('/')[:-1]) + ['docker/'])
        shutil.copytree(docker_install_dir, docker_build_dir)

        # Copy sagemaker_tensorflow sdist
        sdist_name = os.path.basename(sdist_path)
        sdist_dest = "{}/{}".format(docker_build_dir, sdist_name)
        shutil.copyfile(sdist_path, sdist_dest)

        tf_version = sdist_name.split("-")[1][:3]

        client = docker.from_env()
        ecr_client = boto3.client('ecr', region_name=region_helper.region)
        token = ecr_client.get_authorization_token()
        username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')

        client.images.pull(FROM_IMAGE, auth_config={'username': username, 'password': password})
        client.images.build(
            path=docker_build_dir,
            tag="{}:{}".format(self.repository, self.tag),
            buildargs={'sagemaker_tensorflow': sdist_name,
                       'device': self.device,
                       'tf_version': tf_version,
                       'script': self.script_name})

        client.images.push("{}:{}".format(self.repository, self.tag),
                           auth_config={'username': username, 'password': password})
        shutil.rmtree(docker_build_dir)

all_scripts = [
    BenchmarkScript("InputOnly", repo_helper.repository(region=region_helper.region),
                    "input_only_script.py", "input-only", "cpu"),
    BenchmarkScript("GpuLoad", repo_helper.repository(region=region_helper.region),
                    "gpu_pipeline_script.py", "gpu-load", "gpu")
]
