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
#include <iostream>
#include <string>
#include <cstdio>
#include "tensorflow/core/lib/hash/crc32c.h"
#include "TFRecordReader.hpp"

using sagemaker::tensorflow::TFRecordReader;

inline void ValidateLength(const std::uint64_t& length, const std::uint32_t masked_crc32_of_length) {
    if (tensorflow::crc32c::Unmask(masked_crc32_of_length)
        != tensorflow::crc32c::Value(reinterpret_cast<const char*>(&(length)), sizeof(length))) {
        throw std::runtime_error("CRC check on header failed.");
    }
}

inline void ValidateData(const std::string* storage, const std::uint64_t& length,
                         const std::uint32_t masked_crc32_of_data) {
    auto unmasked_crc = tensorflow::crc32c::Unmask(masked_crc32_of_data);
    auto data_crc = tensorflow::crc32c::Value(storage->data(), length);
    if (unmasked_crc != data_crc) {
        throw std::runtime_error("CRC check on data failed.");
    }
}

bool TFRecordReader::ReadRecord(std::string* storage) {
    std::uint64_t length;
    std::uint32_t masked_crc32_of_length;
    if (!Read(&length, sizeof(length))) {
        return false;
    }
    Read(&masked_crc32_of_length, sizeof(masked_crc32_of_length));
    ValidateLength(length, masked_crc32_of_length);
    storage->resize(length);
    Read(&(storage->at(0)), length);
    std::uint32_t footer;
    Read(&footer, sizeof(footer));
    ValidateData(storage, length, footer);
    return true;
}
