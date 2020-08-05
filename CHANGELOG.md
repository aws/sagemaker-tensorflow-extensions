# Changelog

## v1.6.0 (2020-08-05)

### Features

 * support TF 2.3.0

## v1.5.1 (2020-06-18)

### Bug Fixes and Other Changes

 * add Python 3.6 support back

### Testing and Release Infrastructure

 * fix cpplint invocation in release buildspec

## v1.5.0 (2020-05-15)

### Features

 * support TensorFlow 2.2 Python 3.7

## v1.4.0.post0 (2020-05-05)

### Documentation Changes

 * update tf-2 branch README and supporting languages

## v1.4.0 (2020-03-03)

### Features

 * upgrade to TF 2.1

## v0.3.0 (2020-02-12)

### Features

 * add parameter benchmark_records_interval to emit benchmark metrics on a configurable interval

## v0.2.1 (2019-12-13)

### Bug fixes and other changes

 * test v1 compat.
 * TF 2.0 support.

## v0.2.0 (2019-11-23)

### Features

 * upgrade to TF 1.15

### Bug fixes and other changes

 * Upgrade pip so it would find all the latest versions of tensorflow.

## v0.1.5 (2019-09-11)

### Bug fixes and other changes

 * skipping existing files on pypi

## v0.1.4 (2019-09-10)

### Bug fixes and other changes

 * fix a repo in buildspec-deploy

## v0.1.3 (2019-09-09)

### Bug fixes and other changes

 * remove py35 from buildspec-deploy

## v0.1.2 (2019-09-09)

### Bug fixes and other changes

 * remove py35 whl file becasue codebuild does not install py35

## v0.1.1 (2019-09-09)

### Bug fixes and other changes

 * filter cpplint header_guard error in release build

## v0.1.0 (2019-09-04)

### Bug fixes and other changes

 * typo in buildspec-release file
 * add sagemaker-tensorflow-extensions to CodePipeline
 * upgrade to TF 1.14
 * Upgrade to TF 1.13
 * add codebuild ci
 * Add support for multipart recordio records
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * add new line after hyperlink
 * Upgrade to TF 1.12
 * Validate channel name
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * TF 1.11
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Set tox dependency on tensorflow to 1.10
 * Support for TensorFlow 1.10
 * Update readme.
 * Add flake8 dependnecy on tensorflow. Update readme
 * Remove explicit TensorFlow dependency.
 * Update PipeModeDataset to open FIFO immediately on Iterator creation
 * Update README to describe Python 3 support
 * Remove flaky assertion
 * Initial Python3 support
 * Update integ tests to include 'sagemaker' in generated s3 keys
 * Build correct version of package for inclusion in integ test docker image
 * Upgrade Master to TF 1.9
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Update README.rst
 * Add a check to fail fast if invoked in file mode
 * Remove debug statement from RecordReader destructor
 * Add extra logging in benchmark
 * Integrate benchmark tc
 * Add region to benchmark script creation
 * Set region in benchmarking bucket helper
 * Improve style. Add dependency on tensorflow to benchmark package.
 * Add a local benchmark application to benchmarking. Report iterator metrics when benchmarking.
 * Remove from_image build arg. Remove dummy.txt testing file
 * Do a docker pull of base image prior to building integration test docker image
 * Add region to create_integ_test_docker_images
 * Remove erroneous comment from benchmarking Dockerfile
 * Add region name to boto3 clients
 * Add boto3 install_requires to pipemode benchmark
 * Set benchmarking as a separate python package
 * Add documentation to benchmark components
 * Test TC / GH integration
 * Remove setup_requires from setup.py setup function call
 * Add tensorflow as a setup_requires
 * Move cmake to a setup_requires dependency
 * Add cmake as a flake8 dep
 * Exclude benchmark from flake8
 * Add tox dependency on cmake
 * Add Header for TextLineRecordReaderTest
 * Run python tests and flake8 with tox. Refactor RecordReader hierarchy to remove read-ahead buffer from base class.
 * Use old-style super constructor call on CMakeExtension.
 * Add a PipeMode Dataset implementation for TF 1.8
 * Creating initial file from template
 * Creating initial file from template
 * Updating initial README.md from template
 * Creating initial file from template
 * Creating initial file from template
 * Creating initial file from template
 * Initial commit
