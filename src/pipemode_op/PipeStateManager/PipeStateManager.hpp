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

#ifndef SRC_PIPEMODE_OP_PIPESTATEMANAGER_PIPESTATEMANAGER_HPP_
#define SRC_PIPEMODE_OP_PIPESTATEMANAGER_PIPESTATEMANAGER_HPP_

#include <fcntl.h>
#include <string>

namespace sagemaker {
namespace tensorflow {

/**
 * Manages the current pipe index for a SageMaker Pipe Mode channel.
 *
 * The current pipe index can be retrieved with GetPipeIndex(). The
 * pipe index may be incremented with IncrementPipeIndex().
 *
 * The current pipe index is maintained in a persistent file system store
 * and can be recovered if a PipeStateManager object is destroyed. 
 */
class PipeStateManager {
 public:
    /**
      * Constructs a new PipeStateManager.
      *
      * The pipe index is stored in a file within state_directory. Manages
      * the pipe index for channel.
      */
    PipeStateManager(const std::string& state_directory, const std::string& channel);

    /**
      * Retrieve the current pipe index.
      */
    int GetPipeIndex() const;

    /**
      * Increment the current pipe index.
      */
    void IncrementPipeIndex() const;

 private:
    const std::string lock_file_;
    const std::string state_file_;
};

/** 
  * A simple RAII multi-thread and multi-process exclusive lock based on filesystem
  * locking.
  */
class Lock {
 public:
    explicit Lock(const std::string& lock_file);
    ~Lock();

    Lock(const Lock&) = delete;
    Lock& operator=(const Lock&) = delete;

 private:
    int fd_;
};
}  // namespace tensorflow
}  // namespace sagemaker

#endif  // SRC_PIPEMODE_OP_PIPESTATEMANAGER_PIPESTATEMANAGER_HPP_
