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

add_executable(testPipeStateManager ${sources})
target_compile_options(testPipeStateManager PRIVATE "-D_GLIBCXX_USE_CXX11_ABI=1")
target_compile_options(testPipeStateManager PRIVATE "-g")

target_link_libraries(testPipeStateManager PipeStateManager libgtest libgmock)

add_test(NAME testPipeStateManager COMMAND testPipeStateManager)
