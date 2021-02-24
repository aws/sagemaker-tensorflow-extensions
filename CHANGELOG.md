# Changelog

## v0.4.1 (2021-02-24)

### Bug Fixes and Other Changes

 * update package minor version

## v0.4.0 (2021-02-23)

### Features

 * allow skipping corrupt TFRecords

## v0.3.4 (2021-02-08)

### Bug Fixes and Other Changes

 * throw an exception if call to read in RecordReader::Read returns an error

## v0.3.3 (2020-12-22)

### Bug Fixes and Other Changes

 * use public aws ecr repo

## v0.3.2 (2020-12-21)

### Bug Fixes and Other Changes

 * add crc check on TFRecord data
 * close lock file on Lock destructor execution

## v0.3.1.post6 (2020-09-17)

### Documentation Changes

 * updated broken Homepage link

## v0.3.1.post5 (2020-08-06)

### Documentation Changes

 * fix the release section format

## v0.3.1.post4 (2020-08-03)

### Testing and Release Infrastructure

 * pin sagemaker<2 in test dependencies

## v0.3.1.post3 (2020-07-20)

### Documentation Changes

 * improving docs to stress that you must install for the specific TF version

## v0.3.1.post2 (2020-06-25)

### Testing and Release Infrastructure

 * add issue templates

## v0.3.1.post1 (2020-06-17)

### Documentation Changes

 * update wording to reflect current state of version support
 * clarify support for TF2 in README

## v0.3.1.post0 (2020-05-01)

### Documentation Changes

 * add steps for releasing the package

## v0.3.1 (2020-04-30)

### Bug Fixes and Other Changes

 * Py37
 * manually bump package version and tensorflow version

## v0.3.0 (2020-04-29)

### Features

 * python3.7 support

## v0.2.1 (2020-02-13)

### Bug Fixes and Other Changes

 * Revert "infra: set --min-version for release process (#67)"
 * bump library version to unblock release pipeline
 * Add configurable metrics interval

### Testing and Release Infrastructure

 * set --min-version for release process

## v0.2.1 (2020-02-13)

### Bug Fixes and Other Changes

 * bump library version to unblock release pipeline
 * Add configurable metrics interval

### Testing and Release Infrastructure

 * set --min-version for release process

## v0.2.1 (2020-02-13)

### Bug Fixes and Other Changes

 * bump library version to unblock release pipeline
 * Add configurable metrics interval

## v0.2.1 (2020-02-12)

### Bug Fixes and Other Changes

 * bump library version to unblock release pipeline
 * Add configurable metrics interval

## v0.2.1 (2020-02-11)

### Bug Fixes and Other Changes

 * Add configurable metrics interval

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
