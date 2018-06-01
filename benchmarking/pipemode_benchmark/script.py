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

import os
import repo_helper
import shutil
import subprocess

import region_helper


class BenchmarkScriptException(Exception):
    """An error building a benchmarking docker image."""

    def __init__(self, message):
        """Create a BenchmarkingScriptException."""
        super(BenchmarkScriptException, self).__init__(message)


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

        subprocess.check_call("aws --region {} ecr get-login --no-include-email | bash".format(region_helper.region),
                              shell=True)
        subprocess.check_call(['docker', 'build',
                               '-t', self.tag,
                               '-t', "{}:{}".format(self.repository, self.tag),
                               '--build-arg', 'script={}'.format(self.script_name),
                               '--build-arg', 'device={}'.format(self.device),
                               '--build-arg', 'sagemaker_tensorflow={}'.format(sdist_name),
                               '--build-arg', 'tf_version={}'.format(tf_version),
                               docker_build_dir])
        subprocess.check_call(['docker', 'push', '{}:{}'.format(self.repository, self.tag)])

        shutil.rmtree(docker_build_dir)

all_scripts = [
    BenchmarkScript("InputOnly", repo_helper.repository(region=region_helper.region),
                    "input_only_script.py", "input-only", "cpu"),
    BenchmarkScript("GpuLoad", repo_helper.repository(region=region_helper.region),
                    "gpu_pipeline_script.py", "gpu-load", "gpu")
]
