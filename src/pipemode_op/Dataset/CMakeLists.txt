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

cmake_minimum_required(VERSION 3.10)
set (CMAKE_CXX_STANDARD 11)
set (CMAKE_VERBOSE_MAKEFILE on )

file(GLOB_RECURSE sources ./src/*.cpp ./src/*.hpp)

add_library(PipeModeOp SHARED ${sources})

if(NOT DEFINED ENV{PYTHON_EXECUTABLE})
    set(ENV{PYTHON_EXECUTABLE} "python")
endif(NOT DEFINED ENV{PYTHON_EXECUTABLE})

message("python executable $ENV{PYTHON_EXECUTABLE}")

execute_process(COMMAND "$ENV{PYTHON_EXECUTABLE}" "-c"
	"import tensorflow as tf; import sys; sys.stdout.write(tf.sysconfig.get_lib() + '/')"
	OUTPUT_VARIABLE TF_LIB_DIR)
execute_process(COMMAND "$ENV{PYTHON_EXECUTABLE}" "-c"
	"import tensorflow as tf; import sys; sys.stdout.write(tf.sysconfig.get_include() + '/')"
	OUTPUT_VARIABLE TF_INCLUDE_DIR)

find_library(TF_LIB 
	NAMES tensorflow_framework
	PATHS "${TF_LIB_DIR}"
	NO_DEFAULT_PATH)

target_compile_options(PipeModeOp PRIVATE "-D_GLIBCXX_USE_CXX11_ABI=0")

target_link_libraries(PipeModeOp ${TF_LIB})

target_link_libraries(PipeModeOp RecordReader)
target_link_libraries(PipeModeOp PipeStateManager)

target_include_directories(PipeModeOp PRIVATE "${TF_INCLUDE_DIR}")
target_include_directories(PipeModeOp PRIVATE "../include")
