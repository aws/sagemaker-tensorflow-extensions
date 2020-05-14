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
#include "tensorflow/core/platform/tstring.h"
#include <algorithm>
#include <iostream>
#include <string>

using namespace tensorflow;
using sagemaker::tensorflow::RecordReader;
using sagemaker::tensorflow::TextLineRecordReader;

TextLineRecordReader::TextLineRecordReader(const std::string& file_path, const std::size_t buffer_capacity,
    const std::size_t read_size, const std::chrono::seconds file_creation_timeout, const char delim):
    RecordReader(file_path, read_size, file_creation_timeout),
    capacity_(buffer_capacity),
    volume_(0),
    offset_(0),
    delim_(delim) {
        buffer_ = new char[capacity_];
    }

TextLineRecordReader::~TextLineRecordReader() {
     delete [] buffer_;
}

void TextLineRecordReader::FillBuffer() {
    while (volume_ < capacity_) {
        size_t read_amount = Read(buffer_ + volume_, capacity_ - volume_);
        if (!read_amount) {
            break;
        }
        volume_ += read_amount;
    }
    offset_ = 0;
}

bool TextLineRecordReader::ReadRecord(::tensorflow::tstring* data) {
    data->resize(0);
    static const std::size_t STEP_SIZE = 1024;
    while (true) {
        if (!volume_) {
            FillBuffer();
        }
        if (!volume_) {
            if (data->size() == 0) {
                return false;
            } else {
                return true;
            }
        }
        while (volume_) {
            data->reserve(data->size() + STEP_SIZE);
            for (int i = 0; i < STEP_SIZE && volume_; ++i) {
                const char next_char = buffer_[offset_++];
                --volume_;
                if (next_char == delim_) {
                    return true;
                } else {
                    data->push_back(next_char);
                }
            }
        }
    }
}
