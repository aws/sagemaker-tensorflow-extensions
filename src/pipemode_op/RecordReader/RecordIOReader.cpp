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

#include <chrono>
#include <cstring>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include "RecordIOReader.hpp"
#include "tensorflow/core/platform/tstring.h"

using namespace tensorflow
using sagemaker::tensorflow::RecordIOReader;

std::uint32_t RECORD_IO_MAGIC = 0xced7230a;
std::uint32_t RECORD_IO_START_MULTIPART_RECORD_FLAG = 1;
std::uint32_t RECORD_IO_CONTINUE_MULTIPART_RECORD_FLAG = 2;

struct RecordIOHeader {
    std::uint32_t magic_number;
    std::uint32_t size_and_flag;
};

inline void ValidateMagicNumber(const RecordIOHeader& header) {
    if (header.magic_number != RECORD_IO_MAGIC) {
        throw std::runtime_error("Invalid magic number: " + std::to_string(header.magic_number));
    }
}

inline std::uint32_t GetRecordSize(const RecordIOHeader& header) {
    return header.size_and_flag & ((1u << 29u) - 1u);
}

inline std::uint32_t GetRecordFlag(const RecordIOHeader& header) {
    return (header.size_and_flag >> 29u) & 7u;
}

inline std::uint32_t GetPaddedSize(std::uint32_t size) {
    return size + (4 - size % 4) % 4;
}

inline bool HasFollowingMultipartRecords(const RecordIOHeader& header) {
    return GetRecordFlag(header) == RECORD_IO_START_MULTIPART_RECORD_FLAG ||
        GetRecordFlag(header) == RECORD_IO_CONTINUE_MULTIPART_RECORD_FLAG;
}

bool RecordIOReader::ReadRecord(::tensorflow::tstring* storage) {
    std::size_t total_record_size = 0;
    RecordIOHeader header;
    do {
        if (!Read(&header, sizeof(header))) {
            return false;
        }
        ValidateMagicNumber(header);
        std::size_t expected_size = GetRecordSize(header);
        std::size_t padded_expected_size = GetPaddedSize(expected_size);
        total_record_size += expected_size;
        storage->resize_uninitialized(total_record_size);
        Read(&(storage.begin()) + (total_record_size - expected_size), expected_size);
        static char ignore[4] = {0, 0, 0, 0};
        std::size_t pad_amount = padded_expected_size - expected_size;
        if (pad_amount) {
            Read(&ignore, pad_amount);
        }
    } while (HasFollowingMultipartRecords(header));
    return true;
}
