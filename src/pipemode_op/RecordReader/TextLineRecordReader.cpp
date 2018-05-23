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

#include "TextLineRecordReader.hpp"
#include <string>

using sagemaker::tensorflow::RecordReader;
using sagemaker::tensorflow::TextLineRecordReader;

TextLineRecordReader::TextLineRecordReader(const std::string& file_path, const std::size_t buffer_capacity,
    const std::size_t read_size, const std::chrono::seconds file_creation_timeout, const char delim):
    RecordReader(file_path, buffer_capacity, read_size, file_creation_timeout), delim_(delim) {}

bool TextLineRecordReader::ReadRecord(std::string* storage) {
    return ReadLine(storage, delim_);
}
