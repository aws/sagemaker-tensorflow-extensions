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

#include "RecordReader.hpp"

#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <system_error>

using sagemaker::tensorflow::RecordReader;

bool RecordReader::WaitForFile() {
    auto sleep = std::chrono::seconds(0);
    while (sleep < file_creation_timeout_) {
        struct stat buffer;
        if (stat(file_path_.c_str(), &buffer) == 0) {
            return true;
        }
        sleep = sleep + std::chrono::seconds(1);
        std::this_thread::sleep_for(sleep);
    }
    return false;
}

int UNSET_FILE_DESCRIPTOR = -2;

RecordReader::RecordReader(const std::string& file_path, const std::size_t read_size,
    std::chrono::seconds file_creation_timeout):
    fd_(UNSET_FILE_DESCRIPTOR),
    file_path_(file_path),
    read_size_(read_size),
    file_creation_timeout_(file_creation_timeout)  {
        if (WaitForFile()) {
            fd_ = open(file_path_.c_str(), O_RDONLY);
            if (-1 == fd_) {
                throw std::system_error(errno, std::system_category());
            }
        }
    }

std::size_t RecordReader::Read(void* dest, std::size_t nbytes) {
    if (fd_ == UNSET_FILE_DESCRIPTOR) {
        throw std::runtime_error("File does not exist: " + file_path_);
    }
    std::size_t bytes_read = 0;
    while (nbytes) {
        ssize_t read_amount = read(fd_, dest + bytes_read, std::min(nbytes, read_size_));
        if (-1 == read_amount) {
            throw std::system_error(errno, std::system_category());
        }
        if (!read_amount) {
            break;
        }
        bytes_read += read_amount;
        nbytes -= read_amount;
    }
    return bytes_read;
}
