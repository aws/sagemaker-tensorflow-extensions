#ifndef SRC_PIPEMODE_OP_RECORDREADER_TEXTLINERECORDREADER_HPP_
#define SRC_PIPEMODE_OP_RECORDREADER_TEXTLINERECORDREADER_HPP_

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
#include "RecordReader.hpp"
#include "tensorflow/core/platform/tstring.h"


namespace sagemaker {
namespace tensorflow {

#define DEFAULT_CAPACITY 1048576

/**
   A RecordReader that reads delimited text records.
 */
class TextLineRecordReader : public RecordReader {
 public:
    using tensorflow::tstring;
    /**
       Constructs a new TextLineRecordReader that reads records from a file.
    
       param [in] file_path: The path and name of the file to open.
       param [in] buffer_capacity: The size of the read ahead buffer, in bytes.
       param [in] read_size: The number of bytes to read from the open file when
                             filling the read-ahead buffer.
       param [in] file_creation_timeout: The number of seconds to wait for the file
                                         being read to exist.
       param [in] delim: The record breaking delimiter, e.g. '\n'.
     */
    TextLineRecordReader(const std::string& file_path, const std::size_t buffer_capacity, const std::size_t read_size,
                 const std::chrono::seconds file_creation_timeout, const char delim);

    /**
       Constructs a new RecordReader that reads records from a file. Uses default values
       for buffer_capacity, read_size, and file_creation_timeout.
       
       param [in] file_path: The path and name of the file to open.
       param [in] delim: The record breaking delimiter, e.g. '\n'.
     */
    TextLineRecordReader(const std::string& file_path, const char delim) : TextLineRecordReader(file_path,
        DEFAULT_CAPACITY, DEFAULT_READ_SIZE, DEFAULT_FILE_CREATION_TIMEOUT, delim) {}

    /**
       Constructs a new RecordReader that reads new-line delimited records from a file. Uses default values
       for buffer_capacity, read_size, file_creation_timeout. delim is defaulted to '\n'.
       
       param [in] file_path: The path and name of the file to open.
     */
    explicit TextLineRecordReader(const std::string& file_path) : TextLineRecordReader(file_path, '\n') {}

    virtual ~TextLineRecordReader();

    bool ReadRecord(tensorflow::tstring* storage) override;

 protected:
    /**
       Attempt to fill the read-ahead buffer. After this method returns, if the buffer
       is not full, then the EOF has been reached.
     */
    void FillBuffer();

 private:
    const char delim_;

    // The read-ahead buffer
    char* buffer_;

    // The maximum number of bytes that can be stored in the read-ahead buffer
    std::size_t capacity_;

    // The current number of bytes stored in the read-ahead buffer
    std::size_t volume_;

    // The location of the next byte to read from the read-ahead buffer
    std::size_t offset_;
};

}  // namespace tensorflow
}  // namespace sagemaker
#endif  // SRC_PIPEMODE_OP_RECORDREADER_TEXTLINERECORDREADER_HPP_
