#ifndef SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_COMMON_HPP_
#define SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_COMMON_HPP_

// Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"). You
// may not use this file except in compliance with the License. A copy of
// the License is located at
//
//     http://aws.amazon.com/apache2.0/
//
// or in the "license" file accompanying this file. This file is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
// ANY KIND, either express or implied. See the License for the specific
// language governing permissions and limitations under the License.

#include <string>
#include <fstream>

std::string CreateTemporaryDirectory();

std::string CreateChannel(const std::string& channel_directory, const std::string& channel_name,
    const std::string data, unsigned int index);
#endif  // SRC_PIPEMODE_OP_TEST_TESTRECORDREADER_COMMON_HPP_
