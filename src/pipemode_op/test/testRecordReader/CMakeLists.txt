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

file(GLOB_RECURSE sources ./*.cpp ./*.hpp)

execute_process(COMMAND "python" "-c"
	"import tensorflow as tf; import sys; sys.stdout.write(tf.sysconfig.get_lib() + '/')"
	OUTPUT_VARIABLE TF_LIB_DIR)

find_library(TF_LIB 
	NAMES tensorflow_framework
	PATHS "${TF_LIB_DIR}"
	NO_DEFAULT_PATH)

add_executable(testRecordReader ${sources})
target_compile_options(testRecordReader PRIVATE "-D_GLIBCXX_USE_CXX11_ABI=0")
target_compile_options(testRecordReader PRIVATE "-g")
target_include_directories(testRecordReader PRIVATE "../../include")

target_link_libraries(testRecordReader RecordReader libgtest libgmock ${TF_LIB})

add_test(NAME testRecordReader COMMAND testRecordReader)
