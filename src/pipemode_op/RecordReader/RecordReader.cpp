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

void RecordReader::WaitForFile() {
    auto sleep = std::chrono::seconds(0);
    while (sleep < file_creation_timeout_) {
        struct stat buffer;
        if (stat(file_path_.c_str(), &buffer) == 0) {
            return;
        }
        sleep = sleep + std::chrono::seconds(1);
        std::this_thread::sleep_for(sleep);
    }
    throw std::runtime_error("File does not exist: " + file_path_);
}

int UNSET_FILE_DESCRIPTOR = -2;

RecordReader::RecordReader(const std::string& file_path, const std::size_t buffer_capacity,
    const std::size_t read_size, std::chrono::seconds file_creation_timeout):
    fd_(UNSET_FILE_DESCRIPTOR),
    file_path_(file_path),
    capacity_(buffer_capacity),
    read_size_(read_size),
    volume_(0),
    offset_(0),
    file_creation_timeout_(file_creation_timeout)  {
    buffer_ = new char[capacity_];
}

RecordReader::~RecordReader() {
    if (fd_ >= 0) {
        close(fd_);
    }
    delete [] buffer_;
}

void RecordReader::FillBuffer() {
    while (volume_ < capacity_) {
        std::size_t size = std::min(read_size_, capacity_ - volume_);
        ssize_t read_amount = read(fd_, buffer_ + volume_, size);
        if (read_amount < 0) {
           throw std::system_error(errno, std::system_category());
        }
        if (!read_amount) {
            break;
        }
        volume_ += read_amount;
    }
    offset_ = 0;
}

std::size_t RecordReader::Read(void* dest, std::size_t nbytes) {
    if (fd_ == UNSET_FILE_DESCRIPTOR) {
        WaitForFile();
        fd_ = open(file_path_.c_str(), O_RDONLY);
        if (-1 == fd_) {
            throw std::system_error(errno, std::system_category());
        }
    }
    std::size_t bytes_read = 0;
    while (nbytes) {
        if (!volume_) {
            FillBuffer();
        }
        if (!volume_) {
            return bytes_read;
        }
        std::size_t copy_nbytes = std::min(volume_, nbytes);
        std::memcpy(static_cast<char*>(dest) + bytes_read, buffer_ + offset_, copy_nbytes);
        nbytes -= copy_nbytes;
        volume_ -= copy_nbytes;
        offset_ += copy_nbytes;
        bytes_read += copy_nbytes;
    }
    return bytes_read;
}

bool RecordReader::ReadLine(std::string* data, const char delim) {
    if (fd_ == UNSET_FILE_DESCRIPTOR) {
        WaitForFile();
        fd_ = open(file_path_.c_str(), O_RDONLY);
        if (-1 == fd_) {
            throw std::system_error(errno, std::system_category());
        }
    }
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
                data->shrink_to_fit();
                return true;
            }
        }
        while (volume_) {
            data->reserve(data->size() + STEP_SIZE);
            for (int i = 0; i < STEP_SIZE && volume_; ++i) {
                const char next_char = buffer_[offset_++];
                --volume_;
                if (next_char == delim) {
                    data->shrink_to_fit();
                    return true;
                } else {
                    data->push_back(next_char);
                }
            }
        }
    }
}
