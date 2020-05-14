#ifndef SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_
#define SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_

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
#include <stdexcept>
#include <exception>
#include <thread>
#include <chrono>

#include "tensorflow/core/platform/tstring.h"

namespace sagemaker {
namespace tensorflow {

#define DEFAULT_READ_SIZE 65536
#define DEFAULT_FILE_CREATION_TIMEOUT std::chrono::seconds(120)

/**
   An abstract record reader. Records are byte sequences read from a file. 

   Instances of this class are not thread-safe.
  */
class RecordReader {
 public:
    /**
       Constructs a new RecordReader that reads records from a file.
    
       param [in] file_path: The path and name of the file to open.
       param [in] read_size: The preferred number of bytes to read from the open file 
                             during invocation of Read.
       param [in] file_creation_timeout: The number of seconds to wait for the file
                                         being read to exist.
     */
    RecordReader(const std::string& file_path, const std::size_t read_size,
                 const std::chrono::seconds file_creation_timeout);

    /**
       Constructs a new RecordReader that reads records from a file. Uses default a value
       for read_size.
       
       param [in] file_path: The path and name of the file to open.
     */
    explicit RecordReader(const std::string& file_path) : RecordReader(file_path, DEFAULT_READ_SIZE,
        DEFAULT_FILE_CREATION_TIMEOUT) {}

    RecordReader(const RecordReader&) = delete;
    RecordReader& operator=(const RecordReader&) = delete;
    RecordReader(RecordReader&&) = delete;
    RecordReader& operator=(RecordReader&&) = delete;

    /**
       Closes the file opened by this RecordReader.
     */
    virtual ~RecordReader();

    /**
       Reads a record from the underlying file and stores the record data in the 
       specified string pointer. The specified string is resized to accomodate the record.

       param [out] storage The string where the record is written to.
       return true if a record could be read, false otherwise.
     */
    virtual bool ReadRecord(tensorflow::tstring* storage) = 0;

 protected:
    /**
       Read bytes from the file into a byte array. 

       param [out] data The byte array to write into.
       param [in] nbytes The number of bytes to read.

       return the number of bytes read
     */
    std::size_t Read(void* data, std::size_t nbytes);

    /**
       Wait for the file this RecordReader is reading to be created. Will 
       time-out after file_creation_timeout_ seconds. Returns true if the file
       was found before time-out, false otherwise.
     */
    bool WaitForFile();

 private:
    // The file descriptor of the file being read
    int fd_;

    // The path of the file being read
    const std::string file_path_;

    // The number of bytes to read from the open file when filling the read-ahead
    // buffer
    std::size_t read_size_;

    // The number of seconds to wait for the file being read to exist. Measured from
    // the first invocation of Read. Defaults to 120 seconds.
    std::chrono::seconds file_creation_timeout_;
};
}  // namespace tensorflow
}  // namespace sagemaker

#endif  // SRC_PIPEMODE_OP_RECORDREADER_RECORDREADER_HPP_
