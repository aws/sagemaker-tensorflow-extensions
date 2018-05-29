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


class BenchmarkScriptException(Exception):
    """An error building a benchmarking docker image."""

    def __init__(self, message):
        """Create a BenchmarkingScriptException."""
        super(BenchmarkScriptException, self).__init__(message)


class _BenchmarkScript(object):

    def __init__(self, name, repository, script_name, tag, device):
        self.name = name
        self.script_name = script_name
        self.tag = tag
        self.repository = repository
        self.device = device

    @property
    def image(self):
        return self.repository + ":" + self.tag

    def build(self):
        sdist_name = None
        for file in os.listdir("../dist/"):
            if file.startswith("sagemaker_tensorflow") and file.endswith(".tar.gz"):
                sdist_name = file
                break

        sdist_source = "../dist/{}".format(sdist_name)
        sdist_dest = "docker/{}".format(sdist_name)

        if not os.path.exists(sdist_source):
            raise BenchmarkScriptException("No sdist file found. Please run setup.py sdist prior to benchmarking.")
        shutil.copyfile(sdist_source, sdist_dest)

        tf_version = sdist_name.split("-")[1][:3]

        subprocess.check_call(['docker', 'build',
                               '-t', self.tag,
                               '-t', "{}:{}".format(self.repository, self.tag),
                               '--build-arg', 'script={}'.format(self.script_name),
                               '--build-arg', 'device={}'.format(self.device),
                               '--build-arg', 'sagemaker_tensorflow={}'.format(sdist_name),
                               '--build-arg', 'tf_version={}'.format(tf_version),
                               'docker'])
        subprocess.check_call("aws ecr get-login | bash", shell=True)
        subprocess.check_call(['docker', 'push', '{}:{}'.format(self.repository, self.tag)])

all_scripts = [
    _BenchmarkScript("InputOnly", repo_helper.repository(), "input_only_script.py", "input-only", "cpu"),
    _BenchmarkScript("GpuLoad", repo_helper.repository(), "gpu_pipeline_script.py", "gpu-load", "gpu")
]
