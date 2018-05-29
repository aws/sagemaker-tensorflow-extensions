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
from __future__ import absolute_import

import os
import multiprocessing
import sys
import subprocess

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


def read(fname):
    """Return the contents of fname."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_files(dir, extensions=(".cpp", ".cc", ".h", ".hpp", ".txt")):
    """Find files matching extensions."""
    for root, directories, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith(extensions):
                yield os.path.join(root, filename)


class CMakeExtension(Extension):
    """A setuptools Extension for buildling CMake projects."""

    def __init__(self, name, sourcedir=''):
        """A CMake Build Extension, for invoking CMake building of TensorFlow C++ plugins.

        Requires CMake to be installed.
        """
        Extension.__init__(self, name, sources=list(find_files(sourcedir)))
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """A CMake build_ext."""

    def run(self):
        """Build a CMake project."""
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        """Build a specific CMakeExtension."""
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + os.path.join(extdir, 'sagemaker_tensorflow'),
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        build_args += ['--', '-j{}'.format(multiprocessing.cpu_count())]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)
        subprocess.check_call(['ctest'], cwd=self.build_temp)
        print()


setup(
    name='sagemaker_tensorflow',
    version='1.8.0.1.0.0',
    description='Amazon Sagemaker specific TensorFlow extensions.',

    packages=find_packages(where='src', exclude=('test',)),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    ext_modules=[CMakeExtension(name='pipemode_op', sourcedir='src/pipemode_op')],
    cmdclass=dict(build_ext=CMakeBuild),
    long_description=read('README.rst'),
    url='https://github.com/aws/sagemaker-tensorflow',
    license='Apache License 2.0',
    author='Amazon Web Services',
    maintainer='Amazon Web Services',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['cmake', 'tensorflow==1.8'],
    extras_require={
        'test': ['tox', 'flake8', 'pytest', 'pytest-cov', 'pytest-xdist', 'mock',
                 'sagemaker', 'docker']
    },
)
