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

#include <sys/file.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <fstream>
#include <iostream>
#include <ios>
#include <string>
#include <system_error>
#include "PipeStateManager.hpp"

using sagemaker::tensorflow::PipeStateManager;
using sagemaker::tensorflow::Lock;

PipeStateManager::PipeStateManager(const std::string& state_directory, const std::string& channel):
    lock_file_(state_directory + "/." + channel + "-pipe_mode-lock"),
    state_file_(state_directory + "/." + channel + "-pipe_mode-state") {
    Lock lock(lock_file_);
    struct stat buffer;
    if (stat(state_file_.c_str(), &buffer) == -1) {
        std::fstream state_file_ostream(state_file_, std::ios_base::out);
        state_file_ostream << 0;
    }
}

int PipeStateManager::GetPipeIndex() const {
    std::fstream state_file_istream(state_file_, std::ios_base::in);
    int pipe_index;
    state_file_istream >> pipe_index;
    return pipe_index;
}

void PipeStateManager::IncrementPipeIndex() const {
    Lock lock(lock_file_);
    std::fstream state_file_istream(state_file_, std::ios_base::in);
    int pipe_index;
    state_file_istream >> pipe_index;
    state_file_istream.close();

    ++pipe_index;

    std::fstream state_file_ostream(state_file_, std::ios_base::out);
    state_file_ostream << pipe_index;
    state_file_ostream.close();
}

int check(int x) {
    if (x == -1) {
        throw std::system_error(errno, std::system_category());
    }
    return x;
}

Lock::Lock(const std::string& lock_file) {
    fd_ = check(open(lock_file.c_str(), O_WRONLY | O_CREAT, 0666));
    check(flock(fd_, LOCK_EX));
}

Lock::~Lock() {
    check(flock(fd_, LOCK_UN));
    close(fd_);
}
